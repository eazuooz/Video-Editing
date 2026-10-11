"""Record an observed final-pair/pixel outer exit without implying visual approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['pair','pixels'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--outer-exit',type=int,required=True);ap.add_argument('--completion',required=True);a=ap.parse_args()
name='current17-final-pair-execution-v2' if a.mode=='pair' else 'current17-final-pixel-execution-v1'
sp=R/(name+'.json');ss=R/(name+'.session.json');s=read(sp);v=read(ss)
assert s['sessionId']==v['sessionId']==a.session and v['actualOuterExitCode'] is None and s['exitCode']==a.outer_exit
assert s['pid']==v['pid'] and abs(s['createTime']-v['createTime'])<.01
try:assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01,'Worker is still live.'
except psutil.NoSuchProcess:pass
mix=read(R/'current-mix-execution-v2.json')
for row in mix['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
if a.outer_exit==0:
 if a.mode=='pair':
  assert s['frames']==51186 and s['retainedByteIdenticalPieceCount']==20 and s['all71ProtectedInputsUnchanged']
  for row in s['pair']:
   assert sha(ROOT/row['path'])==row['sha256'] and row['wholeDecodeExitCode']==0 and row['allPts1500Verified'] and row['identicalReviewedWholeAacPackets']
 else:
  assert s['allExactAbsolutePtsVerified'] and sha(ROOT/s['index'])==s['indexSha256']
  index=read(ROOT/s['index']);assert index['all220CuesAnd37PieceCutBoundariesIncluded']
  for row in index['samples']+index['boards']:assert sha(ROOT/row['path'])==row['sha256']
v.update(actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,workerCurrentlyAlive=False,verifiedAt=datetime.now(timezone.utc).isoformat(),all71ProtectedInputsUnchanged=True,visualApproval=False)
t=ss.with_name(ss.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,ss)
print(json.dumps(dict(mode=a.mode,session=a.session,actualExit=a.outer_exit,workerAlive=False,all71Protected=True,pixelApproval=False)))
