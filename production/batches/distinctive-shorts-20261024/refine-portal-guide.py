"""Anchor the introductory guide to inspected inner-portal frames."""
from pathlib import Path
import json,time,subprocess,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(f):return json.loads(f.read_text(encoding='utf8'))
def save(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ready=R/'projects/shorts-gears-inertialization/production/delivery.json';deadline=time.monotonic()+3600
while True:
 if ready.exists() and '.v2.captioned.mp4' in read(ready)['files']['captioned']['path']:break
 assert time.monotonic()<deadline;time.sleep(10)
p=R/'projects/shorts-portal-recursion';control=read(R/'shared/publishing/video-production-control.json')['shortsBatchAuthorization'];assert control['status']=='active' and p.name in control['slugs']
f=R/'motion-canvas/src/projects/distinctive-shorts-20261024/composite.tsx';s=f.read_text(encoding='utf8')
old="if(topic==='portal')gameBox.add(<Circle position={[15,65]} size={230} stroke={C.green} lineWidth={6} opacity={()=>e()<1.2?clamp(e()/.15):0}/>);"
new="""if(topic==='portal'){
  // Editorial arrow follows the exposed inner opening at source frames 0,30,60.
  const guide=()=>{const u=clamp(e());return new Vector2(u<.5?100-10*u:95+70*(u-.5),u<.5?-10-110*u:-65-10*(u-.5));};
  gameBox.add(<Line points={()=>[new Vector2(-230,90),guide()]} stroke={C.green} lineWidth={7} endArrow arrowSize={22} opacity={()=>e()<1.05?clamp(e()/.15):0}/>);
  gameBox.add(<Txt text="안쪽 포털" position={[-255,135]} fill={C.white} fontFamily={FONT} fontSize={34} fontWeight={700} opacity={()=>e()<1.05?clamp(e()/.15):0}/>);
 }"""
assert old in s;s=s.replace(old,new);f.write_text(s,encoding='utf8')
d=read(p/'project.json');d.update(currentFinalDirectory='production/local/final-reviewed-v2',deliveryFilenameSuffix='.v2');save(p/'project.json',d)
d=read(p/'planning/production-plan.json');d['finalVisualCorrection']={'reason':'Introductory circle sat on the outer wall. Replace it with a labeled arrow ending on the exposed inner portal at inspected source frames 0,30,60; clear at 1.05s before view changes further.','sourceFrames':[0,30,60],'screenCoordinatesInGameBox':[[100,-10],[95,-65],[130,-70]],'guideMeaning':'Inner portal opening, editorial guide rather than detector output.','previousMaster':'production/local/final-reviewed','newMaster':'production/local/final-reviewed-v2'};save(p/'planning/production-plan.json',d)
mode='distinctive-v2-full'
with (p/f'production/local/render-{mode}.log').open('w',encoding='utf8') as log:subprocess.run(['node',str(p/'production/render-visual.cjs'),mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
file=R/f'shared/output/motion-canvas/{p.name}-{mode}.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(file)]))['streams'][0]
assert (probe['width'],probe['height'],probe['r_frame_rate'],int(probe['nb_frames']))==(1080,1920,'60/1',read(p/'production/visual-timing.json')['frames'])
save(p/f'production/local/render-{mode}-verified.json',probe)
subprocess.run([sys.executable,'-X','utf8',str(B/'finish-encoding.py'),p.name+':'+mode],cwd=R,check=True)
