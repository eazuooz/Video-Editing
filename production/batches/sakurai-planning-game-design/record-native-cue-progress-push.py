"""Record an already observed normal progress push, never a future SHA."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;P=B/'proof-avoid-game-comparisons';PROJECT=ROOT/'projects/avoid-game-comparisons'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True,encoding='utf-8').strip()
now=datetime.now(timezone.utc).isoformat();r=read(P/'native-cue-progress-git-verification.json')
assert r['pushExitCode']==0 and r['remoteMatches'] and r['foreignIndexBefore']==r['foreignIndexAfter']
assert git('rev-parse','HEAD')==r['localSha']==git('ls-remote','origin','refs/heads/main').split()[0]
assert len(r['commitPaths'])==69 and not r['completedVideoDelivery'] and r['newRasterCommitted']==0
qpath=B/'queue.json';q=read(qpath);task=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
task['nativeCueProgressGit']=dict(status='selected-current15-native-cue-progress-normally-pushed',progressCommit=r['nativeCueProgressCommit'],verifiedAt=r['verifiedAt'],proof='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/native-cue-progress-git-verification.json',paths=69,newImages=0,media=0,foreignStagingPreserved=True,completedVideoDelivery=False,localSha=r['localSha'],remoteSha=r['remoteSha'],remoteMatches=True)
task['execution'].update(observedAt=now,status='closed-current15-native-cue-progress-pushed',alive=False,cpuProductionJobs=0,primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,activeTasks=[],foreignTrainingObservation=dict(observedAt=now,pids=[12940,54920],command='train_v2.py --target shape_id --scope vi --out_root lora_experiment/output_v2sw_vi',untouched=True),previewServer=dict(pid=57756,port=9220,alive=True,command='vite.avoid-game-comparisons.config.ts',observationOnly=True))
task['updatedAt']=now;q.update(updatedAt=now,lastProgressAt=now);save(qpath,q)
for p in [PROJECT/'production/latest-checkpoint.json',P/'latest-checkpoint.json']:
 d=read(p)
 for k in ['stage','updatedAt','nextAction','execution','nativeCueProgressGit','nativeCuePlanning']:d[k]=task[k]
 d['progressGitDelivery']=task['nativeCueProgressGit'];d['completedVideoDelivery']=False;save(p,d)
print(json.dumps(dict(actualProgressCommit=r['nativeCueProgressCommit'],normalPush=True,remoteMatches=True,completedVideoDelivery=False)))
