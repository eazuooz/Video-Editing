"""Move the reaction after the comparison has settled; preserve earlier master."""
from pathlib import Path
import json,time,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
lock=B/'local/motion-export.lock'
deadline=time.monotonic()+3600
while lock.exists():
 assert time.monotonic()<deadline;time.sleep(10)
p=R/'projects/shorts-gears-inertialization'
def read(f):return json.loads(f.read_text(encoding='utf8'))
def save(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
control=read(R/'shared/publishing/video-production-control.json')['shortsBatchAuthorization']
assert control['status']=='active' and p.name in control['slugs']
for f in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',p/'production/local/audio-v1/visual-timing.json']:
 d=read(f);d['reactions'][0].update(start=9.3,end=10.9);save(f,d)
d=read(p/'project.json');d.update(currentFinalDirectory='production/local/final-reviewed-v2',deliveryFilenameSuffix='.v2');save(p/'project.json',d)
d=read(p/'planning/production-plan.json');d['finalVisualCorrection']={'reason':'Initial cat overlapped the right mannequin during the first decaying-offset comparison. Move reaction after the motion settles; preserve full-sized branded cat, native frames and approved PCM.','reactionSeconds':[9.3,10.9],'previousMaster':'production/local/final-reviewed','newMaster':'production/local/final-reviewed-v2'};save(p/'planning/production-plan.json',d)
mode='distinctive-v2-full'
with (p/f'production/local/render-{mode}.log').open('w',encoding='utf8') as log:
 subprocess.run(['node',str(p/'production/render-visual.cjs'),mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
file=R/f'shared/output/motion-canvas/{p.name}-{mode}.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(file)]))['streams'][0]
assert (probe['width'],probe['height'],probe['r_frame_rate'],int(probe['nb_frames']))==(1080,1920,'60/1',read(p/'production/visual-timing.json')['frames'])
save(p/f'production/local/render-{mode}-verified.json',probe)
subprocess.run([sys.executable,'-X','utf8',str(B/'finish-encoding.py'),p.name+':'+mode],cwd=R,check=True)
