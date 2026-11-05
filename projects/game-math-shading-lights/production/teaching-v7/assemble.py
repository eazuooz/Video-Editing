"""Re-use the exact V6 cut for unchanged material and recompose only edited explanations."""
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor
import math,os,shutil,subprocess,time
from common import *
from narration import LESSONS
from plates import generate,BOARDS,EXTRA
from samples import DEMOS
from unity_guides import NATIVE,render as native_overlay
from sequence import construct
EDIT=WORK/'edit';EDIT.mkdir(exist_ok=True)
CHANGED=set(BOARDS)|set(EXTRA)|{15}
def remap(old, timeline):
    pos=old*60;i=max(0,bisect_right([r['oldStart'] for r in timeline],pos)-1);r=timeline[i]
    if pos<120:return old
    return (r['start']+(pos-r['oldStart'])*r['frames']/r['oldFrames'])/60
def captions(timeline):
    bylang={}
    for lang in ('ko','en'):
        rows=[]
        prev=v6.original.CAP.read_srt(V6/(PROJECT.name+'.'+lang+'.srt'))
        meta=v6.original.AL[lang];assert len(prev)==len(meta)
        for old,tag in zip(prev,meta):
            if int(tag['scene']) in LESSONS:continue
            rows.append(dict(start=remap(old['start'],timeline),end=remap(old['end'],timeline),text=old['text']))
        for r in timeline:
            if not r['newSpeech']:continue
            al=read(VOICE/f'{r["sid"]:03}-alignment.json')
            for cue in al[lang]:
                rows.append(dict(start=r['start']/60+.06+cue['start'],end=r['start']/60+.06+cue['end'],text=cue['text']))
        rows.sort(key=lambda c:c['start'])
        for i,c in enumerate(rows):
            c['id']=i+1
            if i and rows[i-1]['end']>c['start']:rows[i-1]['end']=c['start']
            if c['end']<=c['start']+.05:raise RuntimeError(('short cue',lang,c))
        v6.original.CAP.write_srt(OUT/(PROJECT.name+'.'+lang+'.srt'),rows,0);bylang[lang]=rows
    return bylang
def ff(args):subprocess.run(['ffmpeg','-nostdin','-hide_banner','-v','error','-y',*map(str,args)],cwd=EDIT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def layerfile(r,states):
    name=f'{r["i"]:03}-{r["sid"]:03}';lst=EDIT/(name+'.layers');lines=['ffconcat version 1.0']
    for i,(k,f) in enumerate(states):
        end=states[i+1][0] if i+1<len(states) else r['frames']
        lines+=["file '"+f.as_posix()+"'",'option framerate 60','duration %.6f'%((round(end*1e6/60)-round(k*1e6/60))/1e6)]
    lines+=["file '"+states[-1][1].as_posix()+"'",'option framerate 60'];lst.write_text('\n'.join(lines)+'\n','utf-8');return lst
def paths(r):
    name=f'{r["i"]:03}-{r["sid"]:03}';local=r['kind']=='explanation' and r['sid'] in CHANGED
    base=EDIT if local else V6WORK/'edit'
    return base/(name+'.mp4'),base/(name+'-cap.mp4')
def render(r,ko):
    s=r['sid'];name=f'{r["i"]:03}-{s:03}';raw=V6WORK/'edit'/(name+'.mp4')
    if r['kind']!='explanation' or s not in CHANGED:return
    clean,cap=paths(r);n=r['frames'];start=r['start']/60;end=start+n/60
    notes=[dict(a,start=max(0,a['start']-start),end=min(n/60,a['end']-start)) for a in ko if a['end']>start+.0005 and a['start']<end-.0005]
    ass=EDIT/(name+'.ass');receipt=v6.original.CAP.caption_ass(ass,notes,0,{});assert all(len(r['lines'])<=2 for r in receipt)
    states=generate(r);layers=layerfile(r,states);demo=WORK/'demos'/f'{s:03}-guided.mp4'
    inputs=[sha(raw),sha(ass),[(k,sha(path)) for k,path in states],n]
    if s in DEMOS:
        deadline=time.monotonic()+900
        while not demo.with_suffix('.json').is_file() or read(demo.with_suffix('.json'))['stamp'][0]!=sha(BASE/'surface.hlsl') or read(demo.with_suffix('.json'))['stamp'][-1]!=sha(BASE/'guides.py'):
            if time.monotonic()>deadline:raise RuntimeError(('shader not ready',s))
            time.sleep(1)
        assert read(demo.with_suffix('.json'))['frames']==n;inputs.append(sha(demo))
    if s in NATIVE:
        native_overlay(s)
        native=WORK/'native-guides'/f'{s:03}.mov';inputs.append(sha(native))
    proof=EDIT/(name+'.json')
    stamp=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    if proof.is_file() and read(proof)['stamp']==stamp and clean.exists() and cap.exists():return
    args=['-threads','2','-i',raw,'-threads','1','-f','concat','-safe','0','-i',layers]
    if s in DEMOS:args+=['-threads','1','-i',demo]
    if s in NATIVE:args+=['-threads','1','-i',native]
    graph=f'[0:v]setpts=PTS*{n}/{r["oldFrames"]},fps=60,tpad=stop_mode=clone:stop_duration=0.15[clock];[clock][1:v]overlay=eof_action=repeat'
    if s in DEMOS:graph+='[board];[board][2:v]overlay=78:290:eof_action=repeat'
    elif s in NATIVE:graph+='[board];[board][2:v]overlay=0:174:eof_action=repeat'
    graph+=f',split=2[clean][sub];[sub]ass={name}.ass[cap]'
    ff([*args,'-filter_complex_threads','2','-filter_complex',graph,'-map','[clean]','-an','-frames:v',n,*v6.options(),clean,'-map','[cap]','-an','-frames:v',n,*v6.options(),cap])
    assert v6.original.frames(clean)==n==v6.original.frames(cap)
    write(proof,dict(stamp=stamp,frames=n,states=[k for k,p in states],scene=s,clean=sha(clean),captioned=sha(cap)));print('Composed',name,flush=True)
def mux(timeline):
    for i,kind in enumerate(('clean','captioned')):
        files=[(v6.original.D/'brand.mp4',120)]+[(paths(r)[i],r['frames']) for r in timeline]+[(v6.original.D/'member.mp4',600)]
        frames=0;lines=['ffconcat version 1.0']
        for path,n in files:
            lines+=["file '"+path.as_posix()+"'",'duration %.6f'%((round((frames+n)*1e6/60)-round(frames*1e6/60))/1e6)];frames+=n
        listing=EDIT/(kind+'.join');listing.write_text('\n'.join(lines)+'\n','utf-8');dest=OUT/(PROJECT.name+'.'+kind+'.mp4');tmp=dest.with_suffix('.pending.mp4')
        ff(['-f','concat','-safe','0','-i',listing,'-i',VOICE/'pair.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',tmp]);assert v6.original.frames(tmp)==frames;os.replace(tmp,dest)
def run():
    timeline=construct();cap=captions(timeline)['ko']
    # Send the reported section through the same renderer first so its layout can be inspected early.
    rows=sorted(timeline,key=lambda r:(r['sid'] not in [42,44,12,39],r['i']))
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda r:render(r,cap),rows))
    mux(timeline)
if __name__=='__main__':run()
