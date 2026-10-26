"""Resume this selected local rendering pipeline, without ASR or platform work."""
from pathlib import Path
import json, subprocess, sys
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
ROOT=HERE.parents[3]
plan=HERE/'edit-plan.json'
data=json.loads(plan.read_text('utf-8-sig'))
local=PROJECT/'production/local/batch-v1/edit'
master=local/(data['outputStem']+'-captioned.mp4')
# Renderer source identity and body grid are checked by the individual stages.
commands=[
 [sys.executable,str(HERE/'audio_pipeline.py'),'mix','--plan',str(plan)],
 [sys.executable,str(HERE/'video_pipeline.py'),'cuts','--plan',str(plan)],
 [sys.executable,str(HERE/'video_pipeline.py'),'pair','--plan',str(plan)],
 [sys.executable,str(HERE/'video_pipeline.py'),'verify','--plan',str(plan)],
 [sys.executable,str(HERE/'review_audio.py'),'--plan',str(plan),'--encoded',str(master)],
 [sys.executable,str(HERE/'extract-final-review.py')],
 ['node',str(ROOT/'scripts/collect-video-output.cjs'),PROJECT.name],
]
if __name__=='__main__':
 for number,cmd in enumerate(commands,1):
  print(f'[{PROJECT.name}] stage{number}/{len(commands)} '+Path(cmd[1]).name+' '+(' '.join(cmd[2:4])),flush=True)
  if Path(cmd[1]).name=='collect-video-output.cjs':
   verification=json.loads((local/'structural-verification.json').read_text('utf-8'))
   assert verification['status']=='pass'
   manifest_file=PROJECT/'project.json';manifest=json.loads(manifest_file.read_text('utf-8'))
   manifest['membershipOutro']['appliedToFinal']=True
   manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
  subprocess.run(cmd,cwd=ROOT,check=True)
 print('Four local outputs collected. Root final encoded ASR, direct final pixels and human/user review are separate pending checks.',flush=True)
