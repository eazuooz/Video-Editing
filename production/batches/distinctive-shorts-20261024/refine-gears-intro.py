"""Match the first spoken run-to-stop example to a viewed native gameplay interval."""
from pathlib import Path
import json,time,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'projects/shorts-gears-inertialization';deadline=time.monotonic()+1800
while not (p/'production/delivery.json').exists() or '.v3.captioned.mp4' not in read(p/'production/delivery.json')['files']['captioned']['path']:
 assert time.monotonic()<deadline;time.sleep(10)
control=read(R/'shared/publishing/video-production-control.json')['shortsBatchAuthorization'];assert control['status']=='active' and p.name in control['slugs']
timing=read(p/'production/visual-timing.json');section=timing['sections'][0]
section.update(sourceStart=40.2,sourceEnd=40.2+section['end']-section['start'])
timing['gameFramesDirectory']='game-frames-v2';timing['sources']['gameplay']['originalOffsetSeconds']=1200
for f in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',p/'production/local/audio-v1/visual-timing.json']:save(f,timing)
out=p/'production/local/game-frames-v2/game';out.mkdir(parents=True,exist_ok=False)
subprocess.run(['ffmpeg','-v','error','-n','-ss','40.2','-i',str(p/'production/local/gameplay.mp4'),'-frames:v',str(section['endFrame']),'-vf','fps=60','-q:v','3','-threads','2','-start_number','0',str(out/'%05d.jpg')],check=True)
f=R/'motion-canvas/src/projects/distinctive-shorts-20261024/composite.tsx';s=f.read_text(encoding='utf8');old="ROOT+'game-frames/'";assert old in s;s=s.replace(old,"ROOT+(timing.gameFramesDirectory??'game-frames')+'/'");f.write_text(s,encoding='utf8')
source=read(p/'sources/selected-footage.json');source.update(plannedIntroStart=40.2,inspectionSeconds=[35,60],observation='Viewed 35–60s in a 1fps sequence and 39–43s at 5fps. Selected 40.2–45.4167s shows low movement transitioning into a stationary aiming pose, matching the opening run-to-stop example; this is game context, not a measurement of its internal animation algorithm.');save(p/'sources/selected-footage.json',source)
plan=read(p/'planning/production-plan.json');plan['introFootageRevision']={'reason':'Earlier 34s start held in cover before starting to run; move to the observed low-run-to-aim transition for the spoken opening.','sourceLocalIn':40.2,'sourceLocalOut':section['sourceEnd'],'originalIn':1240.2,'normalSpeed':True,'evidence':['production/local/intro-candidate-35-60.jpg','production/local/intro-candidate-39-43.jpg'],'unchanged':'All speech, captions, Unity frames and timing; previous masters retained.'};save(p/'planning/production-plan.json',plan)
project=read(p/'project.json');project.update(currentFinalDirectory='production/local/final-reviewed-v4',deliveryFilenameSuffix='.v4');save(p/'project.json',project)
mode='distinctive-v4-full'
with (p/f'production/local/render-{mode}.log').open('w',encoding='utf8') as log:subprocess.run(['node',str(p/'production/render-visual.cjs'),mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
file=R/f'shared/output/motion-canvas/{p.name}-{mode}.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(file)]))['streams'][0]
assert (probe['width'],probe['height'],probe['r_frame_rate'],int(probe['nb_frames']))==(1080,1920,'60/1',timing['frames']);save(p/f'production/local/render-{mode}-verified.json',probe)
subprocess.run([sys.executable,'-X','utf8',str(B/'finish-encoding.py'),p.name+':'+mode],cwd=R,check=True)
