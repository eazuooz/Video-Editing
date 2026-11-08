"""Frame-accurate integration of approved game edits and real UE overlays.

All coordinates are the immutable relations-v4 master unless stated otherwise.
Replacements may change length. Overlays never change length. No production
job runs on import, and old masters are never written. The renderer and source
teams produce inputs; this module enforces preservation during final assembly.
"""
from pathlib import Path
import re,hashlib
import numpy as np
import soundfile as sf

FPS=60
RATE=48000
SPF=RATE//FPS

def sha(path):
    return hashlib.file_digest(Path(path).open('rb'),'sha256').hexdigest()

def validate(replacements,total):
    last=0
    for r in sorted(replacements,key=lambda x:x['startFrame']):
        a,b,n=r['startFrame'],r['endFrame'],r['newFrames']
        assert all(isinstance(i,int) for i in (a,b,n))
        assert last<=a<b<=total and n>0,('overlapping/out-of-bounds replacement',r)
        assert r.get('sourceVerified') is True,('Actual source review required',r.get('id'))
        last=b

def map_frame(frame,replacements):
    shift=0
    for r in sorted(replacements,key=lambda x:x['startFrame']):
        a,b=r['startFrame'],r['endFrame']
        if frame<=a: break
        if frame<b: raise ValueError(f'Frame {frame} is inside replacement {r["id"]}')
        shift+=r['newFrames']-(b-a)
    return frame+shift

def picture_edl(total,baseline,overlays,replacements):
    validate(replacements,total)
    replacements=sorted(replacements,key=lambda x:x['startFrame'])
    overlays=sorted(overlays,key=lambda x:x['startFrame'])
    assert all(x['endFrame']<=y['startFrame'] for x,y in zip(overlays,overlays[1:])), 'UE overlay overlap'
    assert all(0<=o['startFrame']<o['endFrame']<=total for o in overlays)
    edges={0,total}
    for row in overlays+replacements: edges.update((row['startFrame'],row['endFrame']))
    edges=sorted(edges);out=[];cursor=0
    for a,b in zip(edges,edges[1:]):
        replacement=next((r for r in replacements if r['startFrame']<=a<r['endFrame']),None)
        if replacement:
            if a!=replacement['startFrame']: continue
            frames=replacement['newFrames'];src=replacement['picture'];start=0;kind='new-game-passage';key=replacement['id']
        else:
            overlay=next((o for o in overlays if o['startFrame']<=a<o['endFrame']),None)
            frames=b-a
            if overlay:
                src=overlay['picture'];start=a-overlay['startFrame'];kind='verified-UE-overlay';key=overlay['id']
            else: src=baseline;start=a;kind='preserved-baseline';key='baseline'
        out.append(dict(kind=kind,id=key,source=src,sourceStartFrame=start,frames=frames,
                        oldStartFrame=a,oldEndFrame=(replacement['endFrame'] if replacement else b),
                        outputStartFrame=cursor,outputEndFrame=cursor+frames))
        cursor+=frames
    assert cursor==total+sum(r['newFrames']-(r['endFrame']-r['startFrame']) for r in replacements)
    assert all(a['outputEndFrame']==b['outputStartFrame'] for a,b in zip(out,out[1:]))
    return out

def audio_splices(total,replacements):
    """Audio and pictures share one frame clock; one frame is exactly800samples."""
    validate(replacements,total);rows=[];at=0;dest=0
    for r in sorted(replacements,key=lambda x:x['startFrame']):
        a,b=r['startFrame']*SPF,r['endFrame']*SPF
        if a>at:
            rows.append(dict(kind='preserve',sourceStartSample=at,samples=a-at,outputStartSample=dest));dest+=a-at
        n=r['newFrames']*SPF
        rows.append(dict(kind='replace',id=r['id'],source=r['audio'],samples=n,outputStartSample=dest));dest+=n;at=b
    if at<total*SPF:
        rows.append(dict(kind='preserve',sourceStartSample=at,samples=total*SPF-at,outputStartSample=dest))
        dest+=total*SPF-at
    return rows,dest

def reconstruct_audio(baseline,total,replacements,target):
    old,rate=sf.read(baseline,dtype='float32',always_2d=True)
    assert rate==RATE and len(old)>=total*SPF
    rows,n=audio_splices(total,replacements);out=np.zeros((n,old.shape[1]),np.float32);evidence=[]
    for row in rows:
        start=row['outputStartSample'];samples=row['samples']
        if row['kind']=='preserve':
            source=old[row['sourceStartSample']:row['sourceStartSample']+samples]
        else:
            source,sr=sf.read(row['source'],dtype='float32',always_2d=True)
            assert sr==rate and source.shape==(samples,old.shape[1]),(row['id'],'replacement PCM dimensions')
        out[start:start+samples]=source
    assert np.isfinite(out).all() and np.max(np.abs(out))<1, 'Invalid/clipping PCM'
    sf.write(target,out,rate,subtype='FLOAT')
    stored,sr=sf.read(target,dtype='float32',always_2d=True)
    for row in rows:
        if row['kind']=='preserve':
            a=row['sourceStartSample'];b=row['outputStartSample'];n=row['samples']
            exact=np.array_equal(old[a:a+n],stored[b:b+n]);assert exact
            evidence.append(dict(oldStartSample=a,newStartSample=b,samples=n,exactSerializedEquality=exact))
    return dict(baselineSha256=sha(baseline),outputSha256=sha(target),sampleRate=rate,
                untouchedPcmPreservedExactly=True,segments=evidence,replacements=[r for r in rows if r['kind']=='replace'])

def map_seconds(sec,replacements):
    # Keep sub-frame caption timestamps; the displacement is an exact frame count.
    f=sec*FPS;shift=0
    for r in sorted(replacements,key=lambda x:x['startFrame']):
        if f<=r['startFrame']+1e-6: break
        if f<r['endFrame']-1e-6: raise ValueError('Caption endpoint intersects changed speech')
        shift+=r['newFrames']-(r['endFrame']-r['startFrame'])
    return sec+shift/FPS

def retime_cues(cues,replacements,new_cues):
    kept=[];removed=[]
    for c in cues:
        overlap=[r for r in replacements if c['start']<r['endFrame']/FPS-1e-6 and c['end']>r['startFrame']/FPS+1e-6]
        if overlap:
            assert len(overlap)==1
            r=overlap[0]
            assert c['start']>=r['startFrame']/FPS-.002 and c['end']<=r['endFrame']/FPS+.002,('Splice bisects subtitle',c,r['id'])
            removed.append(c)
        else:
            kept.append(dict(c,start=map_seconds(c['start'],replacements),end=map_seconds(c['end'],replacements)))
    out=sorted(kept+new_cues,key=lambda c:c['start'])
    assert all(c['start']<c['end'] for c in out)
    assert all(a['end']<=b['start']+.002 for a,b in zip(out,out[1:])), 'Caption overlap'
    return out,removed

def _sec(t):
    h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s)
def _stamp(t):
    q=round(t*100);s,q=divmod(q,100);h,s=divmod(s,3600);m,s=divmod(s,60)
    return f'{h}:{m:02d}:{s:02d}.{q:02d}'

def retime_ass(text,replacements):
    out=[]
    for line in text.splitlines():
        if not line.startswith('Dialogue: '):out.append(line);continue
        fields=line.split(',',9);a,b=_sec(fields[1]),_sec(fields[2])
        overlaps=[r for r in replacements if a<r['endFrame']/FPS-.012 and b>r['startFrame']/FPS+.012]
        if overlaps:
            assert len(overlaps)==1
            r=overlaps[0]
            assert a>=r['startFrame']/FPS-.012 and b<=r['endFrame']/FPS+.012, 'ASS clipping'
            continue
        fields[1]=_stamp(map_seconds(a,replacements));fields[2]=_stamp(map_seconds(b,replacements));out.append(','.join(fields))
    return '\n'.join(out)+'\n'

def selfcheck():
    # Covers real risks: length changes, split overlays, cue clipping and sample offsets.
    rs=[dict(id='r',startFrame=30,endFrame=50,newFrames=40,sourceVerified=True,picture='new.mp4',audio='new.wav')]
    os=[dict(id='o',startFrame=20,endFrame=70,picture='overlay.mp4')]
    edl=picture_edl(100,'base.mp4',os,rs)
    assert [(x['kind'],x['frames'],x['sourceStartFrame']) for x in edl]==[
        ('preserved-baseline',20,0),('verified-UE-overlay',10,0),('new-game-passage',40,0),('verified-UE-overlay',20,30),('preserved-baseline',30,70)]
    assert map_frame(50,rs)==70 and map_frame(100,rs)==120
    rows,n=audio_splices(100,rs);assert n==96000 and rows[-1]['sourceStartSample']==40000 and rows[-1]['outputStartSample']==56000
    cs=[dict(start=.1,end=.3,text='keep'),dict(start=.55,end=.8,text='change'),dict(start=1,end=1.2,text='keep2')]
    out,removed=retime_cues(cs,rs,[]);assert len(removed)==1 and out[1]['start']==1+20/60
    try:retime_cues([dict(start=.4,end=.6,text='cut')],rs,[])
    except AssertionError:pass
    else:raise AssertionError('Cut through spoken subtitle was not rejected')
    print('EDL/sample/caption boundary checks passed')

if __name__=='__main__':selfcheck()
