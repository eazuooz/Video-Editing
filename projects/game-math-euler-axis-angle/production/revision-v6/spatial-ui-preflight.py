"""Compose bounded current-UI/caption stills at frozen real timeline frames.

No clip render, Unity, audio or ASR; two selected source frames are decoded once.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];H=Path(__file__).parent
O=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v6'
Q=O/'edit/spatial-ui-preflight'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def load(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def seconds(s):
    a,b,c=s.split(':');return int(a)*3600+int(b)*60+float(c)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if not a.run:ap.print_help();return
    ctl=read(ROOT/'shared/publishing/video-production-control.json');assert ctl['selectedVideo']=='game-math-euler-axis-angle'
    plan=read(O/'edit/scene-plan.json');assert plan['timelineSha256']==sha(H/'timeline.json') and plan['screenPlanSha256']==sha(H/'screen-plan.json')
    Q.mkdir(exist_ok=True);comp=load('spatial_preflight_compositor',H/'composite.py');comp.E=Q
    nums=load('spatial_preflight_numbers',H/'spatial-readouts.py')
    scenes={s['id']:s for s in plan['scenes']};screens={s['id']:s for s in read(H/'screen-plan.json')['scenes']}
    shots={s['id']:s for s in read(nums.CATALOG)['shots']}
    ui={sid:comp.ui_ass(scenes[sid],screens[sid]) for sid in ['v6-07','v6-13']}
    captions=O/'captions.ko.ass';caption_text=captions.read_text(encoding='utf8')
    signatures={'compositorSha256':sha(H/'composite.py'),'timelineSha256':sha(H/'timeline.json'),'editPlanSha256':sha(O/'edit/scene-plan.json'),
        'screenPlanSha256':sha(H/'screen-plan.json'),'captionsSha256':sha(captions),'readoutImplementationSha256':sha(H/'spatial-readouts.py')}
    samples=[]
    cases=[('07-definition','v6-07','v6-07.B01',0,scenes['v6-07']['startFrame']+120),
           ('07-bank-y-tip','v6-07','v6-07.B01',0,None),('07-camera-y-tip','v6-07','v6-07.B02',148,None),
           ('13-definition','v6-13','v6-13.B01',0,scenes['v6-13']['startFrame']+120),('13-top-x-tip','v6-13','v6-13.B02',417,None)]
    for name,sid,key,frame,global_frame in cases:
        motion=next(p for p in scenes[sid]['phases'] if p['kind']=='motion' and p.get('beatId')==key)
        if global_frame is None:global_frame=motion['startFrame']+frame
        clip=ROOT/motion['file'];source=Q/(name+'.source.png')
        states=[json.loads(s) for s in clip.with_suffix('.anchors.ndjson').read_text().splitlines()];state=states[frame]
        if frame==0:source=clip.with_suffix('.first.png')
        else:
            marker=source.with_suffix('.json');sig={'clipSha256':sha(clip),'sourceFrame':frame}
            if not(source.exists() and marker.exists() and read(marker).get('inputs')==sig and read(marker).get('sha256')==sha(source)):
                subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(clip),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-threads','1','-y',str(source)],check=True)
                save(marker,{'inputs':sig,'sha256':sha(source)})
        display=Q/(name+'.display.png');nums.still(source,display,nums.layout(shots[key],nums.evaluated(shots[key],state['normalizedTime'],state)))
        output=Q/(name+'.png');filters=f'settb=1/60,setpts=N+{global_frame},ass={rel(ui[sid])},ass={rel(captions)}'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-loop','1','-framerate','60','-i',str(display),'-vf',filters,'-frames:v','1','-threads','1','-y',str(output)],check=True,cwd=ROOT)
        mobile=Q/(name+'.375.png')
        with Image.open(output) as im:assert im.size==(1920,1080);im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        active=[]
        for line in caption_text.splitlines():
            if not line.startswith('Dialogue: 12,'):continue
            parts=line.split(',',9)
            if seconds(parts[1])<=global_frame/60<seconds(parts[2]):active.append(parts[9])
        tips=[{'name':v['name'],'x':v['pixelTopLeft']['x'],'y':v['pixelTopLeft']['y']} for v in state['anchors'] if any(s in v['name'] for s in ['bodyX','bodyY','bodyZ','uprightX','uprightY','uprightZ'])]
        samples.append({'name':name,'sceneId':sid,'shotId':key,'sourceFrame':frame,'globalFrame':global_frame,'globalSeconds':global_frame/60,
            'sourceClipSha256':sha(clip),'sourceImageSha256':sha(source),'uiASS':rel(ui[sid]),'uiASSsha256':sha(ui[sid]),'activeActualCaptionRows':active,
            'axisTips':tips,'minimumTipY':min(v['y'] for v in tips),'headerBottomPx':112,'tipCenterDistanceFromHeaderBottom':min(v['y'] for v in tips)-112,
            'native':{'file':rel(output),'sha256':sha(output)},'mobile375':{'file':rel(mobile),'sha256':sha(mobile)},'directImageReview':'pending actual viewing'})
    assert signatures['compositorSha256']==sha(H/'composite.py') and signatures['timelineSha256']==sha(H/'timeline.json') and signatures['captionsSha256']==sha(captions)
    out={'schemaVersion':1,'inputs':signatures,'scope':'Actual frozen source frames/real global frame times with current compositor UI and actual caption cues. No synthetic caption timing; silent motion samples may correctly have no active cue.',
        'samples':samples,'clipsRerendered':False,'sourcePCMChanged':False,'GPUUnityASRStarted':False,'pending':['Direct native375 inspection','Full final encoded moving/caption/joins review']}
    save(H/'spatial-ui-preflight-review.json',out);print(json.dumps({'samples':len(samples),'output':str(H/'spatial-ui-preflight-review.json')}),flush=True)
if __name__=='__main__':main()
