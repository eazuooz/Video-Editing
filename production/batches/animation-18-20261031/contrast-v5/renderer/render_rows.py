"""CPU-only silent cut rendering. Parent owns final audio/gameplay assembly.

Only selected --episodes run, never A03. Resume requires exact visual-code,
source-sequence and row signatures; dimensions alone are not sufficient.
"""
from sources import *
from compose import frame,contract
import argparse,os,time
ENC=['-threads','4','-c:v','libx264','-preset','veryfast','-crf','18','-bf','0','-g','120','-sc_threshold','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']
def state(ep,row,i):
    f=i+row.get('cutOffset',0);key=row['key'];d=source(ep,key)['definition'];full=d['frames']
    if row['mode']=='native':
        if ep=='A02':return min(full-1,12+f),'screen-size'if row.get('screenSize')else'native'
        return min(full-1,row.get('sourceStartFrame',0)+f),'native'
    if ep=='A02':
        if row['baselineCut']=='A02-E004':return min(full-1,f+12),'native'
        if f<324:return min(144,12+f),'screen-size'
        if f<516:return 12,'compare'
        if f<684:return min(full-1,12+f-516),'native'
        if f>1000:return 81,'stages'
        return min(112,32+(f-684)//5),'compare'
    a,b=d.get('observationFrames',[12,min(88,full-1)])
    if ep=='A01':a,b=16,100
    if ep=='A04'and key=='anticipation':a,b=12,24
    if ep=='A11'and key=='kick':a,b=12,20
    lead=row.get('nativeLeadFrames',0)
    if row.get('phaseModeAtTail')and f>=max(lead,round(row['originalCutFrames']*.70)):return int(b),'stages'
    # Keep a real 1x pass where the original body supplied the third observation.
    if f<lead:return min(full-1,f),'native'
    analysis_end=round(row['originalCutFrames']*.70) if row.get('phaseModeAtTail')else row['originalCutFrames']
    progress=max(0,f-lead)/max(1,analysis_end-lead-1)
    return min(full-1,round(a+(b-a)*np.clip(progress,0,1))),'compare'

def render(ep,row,signature):
    dest=R/row['output'];dest.parent.mkdir(parents=True,exist_ok=True);receipt=dest.with_suffix('.json')
    if receipt.exists()and dest.exists():
        old=read(receipt)
        if old.get('signature')==signature and old.get('sha256')==sha(dest):return 'reused'
    tmp=dest.with_name(dest.stem+'.partial.mp4');log=dest.with_suffix('.log');start=time.time();previous=None;pixels=None;used={}
    with log.open('wb')as output:
        proc=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-an',*ENC,str(tmp)],stdin=subprocess.PIPE,stderr=output,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for i in range(row['frames']):
                n,mode=state(ep,row,i);ident=(n,mode)
                if ident!=previous:
                    im=frame(ep,row['key'],n,mode,pass_index=row.get('passIndex')if row['mode']=='native'else None,legend=bool(row.get('showLegend')))
                    pixels=im.tobytes();previous=ident
                used[mode]=used.get(mode,0)+1;proc.stdin.write(pixels)
        finally:proc.stdin.close()
        assert proc.wait()==0,dest
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(tmp)]))['streams'];v=meta[0]
    assert len(meta)==1 and(v['width'],v['height'],int(v['nb_frames']),v['avg_frame_rate'])==(1920,1080,row['frames'],'60/1')
    os.replace(tmp,dest)
    receipt.write_text(json.dumps({'episode':ep,'rowId':row['id'],'signature':signature,'sha256':sha(dest),'frames':row['frames'],'audio':False,'modes':used,
       'renderSeconds':round(time.time()-start,2),'resolution':[1920,1080],'fps':60,'scope':'Only this authored explanation replacement. Full final decode/captions review belongs to parent assembly.','humanReviewed':False},ensure_ascii=False,indent=2),'utf8')
    return 'rendered'

def main(episodes,limit=0,only_row=None):
    ctrl=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ctrl['renderAuthorized'] and ctrl['fullLocalProductionAuthorized']
    assert 'A03' not in episodes and set(episodes)<=set(ctrl['episodes'])
    p=read(H/'replacement-plan.json');code=hashlib.sha256(b''.join((H/n).read_bytes()for n in ('compose.py','sources.py','config.py','render_rows.py'))).hexdigest();done=0
    for ep in p['episodes']:
        if ep['id']not in episodes:continue
        assert not ep['pending'],(ep['id'],'capture pending')
        live={key:input_receipt(ep['id'],key)for key in ep['sourceInputs']}
        for row in ep['rows']:
            if only_row and row['id']!=only_row:continue
            assert row['readyForRender']
            sig=hashlib.sha256(json.dumps({'code':code,'row':row,'source':live[row['key']]},sort_keys=True).encode()).hexdigest()
            result=render(ep['id'],row,sig);done+=1;print(ep['id'],row['id'],result,flush=True)
            if limit and done>=limit:return
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episodes',nargs='+',required=True);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--row');a=ap.parse_args();main(a.episodes,a.limit,a.row)
