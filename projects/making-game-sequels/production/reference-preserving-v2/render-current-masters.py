"""Run the selected measured production serially; stop before final QA."""
from pathlib import Path
import json,subprocess,sys,datetime,os
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def selected():
 c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
selected();plan=read(V/'edit-plan.json');ledger=read(P/'production/review-ledger.json')
assert plan['timing']=='measured-and-asr-aligned';assert ledger['audioQA']['wholeNarrationAsr']=='complete-full-text-reviewed';assert ledger['preparedEdit']['actualCaptionPreflight']=='passed-direct-layout-review'
stages=[('diagrams',['node',str(V/'render-diagrams.cjs'),'game-sequels-production-v2','0',str(plan['mcFrames']),'/src/projects/making-game-sequels/revision-v2/production-project.ts']),('footage',[sys.executable,'-X','utf8',str(V/'render-footage.py')]),('mix',[sys.executable,'-X','utf8',str(V/'build-audio.py')]),('slices',[sys.executable,'-X','utf8',str(V/'compose-video.py'),'slices']),('pair',[sys.executable,'-X','utf8',str(V/'compose-video.py'),'pair'])]
state={'pid':os.getpid(),'status':'running','completedStages':[],'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};out=L/'master-render-execution.json'
def save():out.write_text(json.dumps(state,indent=2)+'\n')
for name,cmd in stages:
 selected();state.update(stage=name,command=cmd);save();print('START '+name,flush=True)
 with (L/('stage-'+name+'.log')).open('w',encoding='utf8') as log:
  process=subprocess.Popen(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT);state['childPid']=process.pid;save();code=process.wait()
 if code:state.update(status='failed',returncode=code);save();raise SystemExit(code)
 state['completedStages'].append(name);save();print('DONE '+name,flush=True)
state.update(status='masters-ready-for-current-output-QA',finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
