"""Remove two redundant secondary labels inside the fixed caption region."""
from pathlib import Path
import json, subprocess, sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug,version in [('shorts-superliminal-perspective',2),('shorts-gears-inertialization',3)]:
 control=read(R/'shared/publishing/video-production-control.json')['shortsBatchAuthorization']
 assert control['status']=='active' and slug in control['slugs']
 p=R/'projects'/slug;project=read(p/'project.json')
 previous=project.get('currentFinalDirectory','production/local/final-reviewed')
 project.update(currentFinalDirectory=f'production/local/final-reviewed-v{version}',deliveryFilenameSuffix=f'.v{version}')
 save(p/'project.json',project)
 plan=read(p/'planning/production-plan.json')
 plan['captionClearanceRevision']={'reason':'Remove a redundant secondary label entering the fixed two-line caption area; narration, captions, native footage, numeric comparison and all timing preserved.','removedLabel':'같은 카메라 · 같은 물체' if version==2 else '움직이던 방향과 속도도 반영','previousMaster':previous,'newMaster':project['currentFinalDirectory']}
 save(p/'planning/production-plan.json',plan)
 mode=f'distinctive-v{version}-full'
 if not (p/f'production/local/render-{mode}-verified.json').exists():
  with (p/f'production/local/render-{mode}.log').open('w',encoding='utf8') as log:
   subprocess.run(['node',str(p/'production/render-visual.cjs'),mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 file=R/f'shared/output/motion-canvas/{slug}-{mode}.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(file)]))['streams'][0]
 assert (probe['width'],probe['height'],probe['r_frame_rate'],int(probe['nb_frames']))==(1080,1920,'60/1',read(p/'production/visual-timing.json')['frames'])
 save(p/f'production/local/render-{mode}-verified.json',probe)
 subprocess.run([sys.executable,'-X','utf8',str(B/'finish-encoding.py'),slug+':'+mode],cwd=R,check=True)
