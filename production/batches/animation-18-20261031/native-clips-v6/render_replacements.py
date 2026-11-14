"""Render only the audited, affected explanation ranges on the original final clock."""
import argparse
from functools import lru_cache
import hashlib
import subprocess
import sys

from prepare import BATCH, HERE, ROOT, WORK, read, save
from finish_episode import sha
from native_visuals import REPAIR, draw

sys.path.insert(0,str(BATCH/'contrast-v5/review-notes-20261110'))
import paint_replacements as old

ENC=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-bf','0','-g','120',
     '-sc_threshold','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000',
     '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']


@lru_cache(1024)
def pixels(ep,key,n,mode,counter):
    return draw(ep,key,n,mode,counter).tobytes()


def state(ep,row,offset):
    if row['mode']=='retimed':
        ref=row['template']
        return state(ep,ref,min(ref['frames']-1,round(offset*(ref['frames']-1)/max(1,row['frames']-1))))
    f=offset+row.get('cutOffset',0)
    if row['mode']=='native':
        return min(179,max(0,row.get('sourceStartFrame',0)+f)),'native',row.get('passIndex')
    total=row['originalCutFrames'];lead=row.get('nativeLeadFrames',0)
    if f<lead:return min(179,f),'native',None
    end=round(total*.70) if row.get('phaseModeAtTail') else total
    if row.get('phaseModeAtTail') and f>=end:return 179,'stages',None
    u=max(0,min(1,(f-lead)/max(1,end-lead-1)))
    n=round(14+51*u) if ep=='A11' else round(179*u)
    return n,'compare',None


def main(ep):
    control=read(ROOT/'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
    assert ep in control['episodes'] and ep in REPAIR and control['renderAuthorized']
    old.EPISODES={ep:REPAIR[ep]}
    edl=read(BATCH/'contrast-v5/local/explanation-assembly'/ep/'edl.json')
    spans=old.classify(ep,edl)
    assert spans and all(a['end']<=b['start'] for a,b in zip(spans,spans[1:]))
    folder=WORK/ep/'new-pictures';folder.mkdir(parents=True,exist_ok=True)
    code=hashlib.sha256(b''.join((HERE/name).read_bytes() for name in
                ('native_visuals.py','native_specials.py','render_replacements.py'))).hexdigest()
    source_inputs={}
    for key in ('AS_ComboHands','am_Ready_Fight_01_Knockdown_A','anim_GrabValve_R','anim_OpeningValve_R','A_Guard_idle'):
        p=WORK/(key+'-capture.json')
        if p.exists(): source_inputs[key]=sha(p)
    source_inputs['gameBanks']=sha(WORK/'game-banks/manifest.json')
    for i,span in enumerate(spans):
        path=folder/f'{i:03}-{span["start"]:06}-{span["end"]:06}.mp4'
        sidecar=path.with_suffix('.json')
        signature={'span':span,'code':code,'sourceInputs':source_inputs}
        cache=read(sidecar) if sidecar.exists() else {}
        if not path.exists() or cache.get('signature')!=signature or cache.get('sha256')!=sha(path):
            with path.with_suffix('.log').open('wb') as log:
                proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
                    '-s','1920x1080','-r','60','-i','pipe:0','-an',*ENC,str(path)],
                    stdin=subprocess.PIPE,stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
                try:
                    for f in range(span['end']-span['start']):
                        n,mode,counter=state(ep,span['reference'],span['offset']+(0 if span.get('hold') else f))
                        proc.stdin.write(pixels(ep,span['reference']['key'],n,mode,counter))
                finally:
                    proc.stdin.close()
                    assert proc.wait()==0,path
            save(sidecar,{'signature':signature,'sha256':sha(path)})
        span.update(file=str(path),sha256=sha(path))
        print(ep,i+1,len(spans),'native explanation range ready',flush=True)
    save(folder/'manifest.json',{'episode':ep,'priorFrameCount':edl['frames'],'spans':spans,
                               'code':code,'sourceInputs':source_inputs,'humanReviewed':False})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode')
    main(parser.parse_args().episode)
