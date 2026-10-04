"""CPU source discovery only. No synthesis, action approval or final render."""
import json, math, os, re, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BATCH=ROOT/'production/batches/sakurai-planning-game-design'
ACQ=json.loads((HERE/(sys.argv[1] if len(sys.argv)>1 else 'acquisition.json')).read_text(encoding='utf-8'))
if ACQ['status']!='acquired-decoded-awaiting-direct-action-review': raise RuntimeError('Complete source acquisition first')
STATE=HERE/(sys.argv[2] if len(sys.argv)>2 else 'discovery.json')
if STATE.exists(): raise RuntimeError('Discovery already exists; inspect its real state instead of rerunning')
stamp=lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
state={'pid':os.getpid(),'startedAt':stamp(),'status':'initializing','sources':[],'gpuJobs':0,'actualCutApproval':False,'sourceAudioUsed':False}
def write(p,v):
    tmp=Path(str(p)+'.'+str(os.getpid())+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
def save():
    state['updatedAt']=stamp();write(STATE,state)
    q=json.loads((BATCH/'queue.json').read_text(encoding='utf-8'));item=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
    item['stage']='source-direct-discovery-review';item['execution'].update({'phase':'CPU-official-source-discovery','pid':os.getpid(),'status':state['status'],'state':str(STATE.relative_to(ROOT)).replace('\\','/'),'updatedAt':stamp(),'activeTasks':[s for s in state['sources'] if s.get('status')=='extracting'],'gpuSynthesisJobs':0,'renderJobs':0,'uploads':0,'newNarrationCreated':False,'newSceneCreated':False})
    item['nextAction']='Directly read discovery frames, inspect native action/boundary frames and approve unique source intervals before narration.';q['updatedAt']=stamp();write(BATCH/'queue.json',q)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
out=HERE.parent/'research-local'/(sys.argv[3] if len(sys.argv)>3 else 'game-discovery');out.mkdir(parents=True,exist_ok=True)
try:
    for src in ACQ['results']:
        vid=src['videoId'];folder=out/vid;folder.mkdir(exist_ok=True)
        video=next(s for s in src['streams'] if s['codec_type']=='video');fps=round(float(video['r_frame_rate'].split('/')[0])/float(video['r_frame_rate'].split('/')[1]));log=folder/'ffmpeg-extraction.log'
        rec={'videoId':vid,'status':'extracting','nativeFps':fps,'source':src['localMediaPath'],'nominalSampleSeconds':1,'log':str(log.relative_to(ROOT)).replace('\\','/'),'sheets':[]};state['sources'].append(rec);state['status']='extracting';save()
        args=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-threads','2','-filter_threads','1','-i',str(ROOT/src['localMediaPath']),'-an','-vf',f'select=not(mod(n\\,{fps})),showinfo,scale=960:540','-vsync','0','-q:v','3',str(folder/'frame-%04d.jpg')]
        with log.open('ab') as fh:
            child=subprocess.Popen(args,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW);rec['childPid']=child.pid;save();code=child.wait()
        if code: raise RuntimeError(f'Frame extraction {vid} exited{code}')
        raw=log.read_text(encoding='utf-8',errors='replace');times=[float(x) for x in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)',raw)]
        frames=sorted(folder.glob('frame-*.jpg'))
        if len(times)!=len(frames): raise RuntimeError(f'Frame/PTS mismatch {vid}: {len(times)} / {len(frames)}')
        rec['frames']=len(frames);rec['actualPtsSeconds']=times;rec['status']='extracted'
        for start in range(0,len(frames),16):
            group=frames[start:start+16];sheet=Image.new('RGB',(2560,1552),(238,238,238));draw=ImageDraw.Draw(sheet)
            for j,file in enumerate(group):
                im=Image.open(file).resize((640,360));x=(j%4)*640;y=(j//4)*388;sheet.paste(im,(x,y+28));draw.text((x+6,y+2),f'{vid}  {times[start+j]:.3f}s  frame{start+j+1}',font=font,fill=(0,0,0))
            target=folder/f'sheet-{start//16+1:02d}.jpg';sheet.save(target,quality=92);rec['sheets'].append(str(target.relative_to(ROOT)).replace('\\','/'))
        rec['endedAt']=stamp();save()
    state['status']='discovery-extracted-awaiting-direct-review';state['endedAt']=stamp();save();print(json.dumps({'status':state['status'],'pid':state['pid'],'frames':sum(s['frames'] for s in state['sources']),'sheets':sum(len(s['sheets']) for s in state['sources'])}))
except Exception as exc:
    state['status']='failed';state['error']=repr(exc);save();raise
