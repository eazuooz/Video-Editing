"""Prepare only nine changed M21 captures; preserve the other 69 originals."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1];S=P/'production/unity-staging'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
 assert control['productionAllowedNow'] and P.name in control['projectSlugs']
 q=read(P/'production/local/render-v2/queue.json');preview=S/'local-preflight-v14'
 assert read(preview/'progress.json')['status']=='images-ready-for-internal-visual-QA'
 review=read(preview/'visual-review.json');assert review['status']=='targeted-images-pass' and not review['finalVideoQa']
 latest=read(preview/'queue.json');sandbox=Path(latest['sandbox']);fp=latest['fingerprint']
 assert read(sandbox/'M21_SANDBOX.json')['fingerprint']==fp
 out=P/'production/local/render-v3';assert not out.exists(),'Preserve existing revision';out.mkdir()
 selected={'007','013','015','063','065','066','067','068','078'};jobs=[];reused=[];changes=[]
 for jp in q['jobs']:
  job=read(Path(jp));sid=job['sceneId']
  if sid not in selected:
   receipt=read(Path(job['output'])/'capture-success.json')
   assert receipt['completed']==job['frames'] and receipt['compiledFingerprint']==job['expectedFingerprint']
   jobs.append(jp);reused.append(sid);continue
  prior=copy.deepcopy(job)
  source=S/('local-preflight-v11' if sid in {'007','015'} else 'local-preflight-v14')/(sid+'.cue.json')
  cue=read(source);cue['id']=job['id'];cue['duration']=job['frames']/60
  job.update(expectedFingerprint=fp,output=str(out/'unity'/sid),cueFile=str(out/'cues'/(sid+'.json')))
  for key in ('comparisonFrames',):job.pop(key,None)
  save(Path(job['cueFile']),cue);path=out/'jobs'/(sid+'.json');save(path,job);jobs.append(str(path))
  for cut in q['cuts']:
   if cut['scene']==sid and cut['kind']=='explanation':cut['file']=str(Path(job['output'])/'unity.mp4')
  changes.append(dict(scene=sid,priorJob=jp,priorFingerprint=prior['expectedFingerprint'],newJob=str(path),inspectedCue=str(source),inspectedCueSha256=sha(source)))
 assert len(reused)==69 and len(changes)==9
 q.update(sandbox=str(sandbox),fingerprint=fp,jobs=jobs,repair=dict(createdAt=datetime.now(timezone.utc).isoformat(),reusedScenes=reused,changedScenes=changes,narrationChanged=False,timingChanged=False,sourceQueue='production/local/render-v2/queue.json'),finalReviewReady=False)
 save(out/'queue.json',q);print('Prepared 9 repaired captures and69 verified capture reuses; audio and timing unchanged.')
if __name__=='__main__':main()
