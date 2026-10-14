"""Audit the next additive draft without touching its baselines or starting TTS."""
from pathlib import Path
import datetime, hashlib, json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
I=Path(__file__).parent/'cross-game-review-20261011/interpolation-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
base=read(I/'baseline.json');draft=read(I/'additions-draft.json')
assert not draft['ttsStarted'] and not draft['movingPixelApproval']
assert draft['actualShare']==.4 and draft['explanationShare']==.6 and not draft['bgm']
assert len(set(draft['gamesPerEpisode']))==4
preserved=[];insertions=[]
for ep in base['episodes']:
 for f in ep['files']:
  assert sha(ROOT/f['path'])==f['sha256'],f['path']
  preserved.append(f['path'])
 rows=[s for s in draft['scenes'] if s['episode']==ep['newSlug']]
 assert len(rows)==4 and sum(s['classification']=='actual' for s in rows)==1
 order=list(ep['sceneIds'])
 for row in rows:
  assert row['after'] in order and len(row['ko'])==len(row['en'])
  order.insert(order.index(row['after'])+1,row['id'])
 assert [s for s in order if s in ep['sceneIds']]==ep['sceneIds']
 if ep['newSlug'].endswith('conversions-v3'):
  assert order.index('IP05')<order.index('RCF12')<order.index('21')
 insertions.append(dict(episode=ep['newSlug'],retainedSceneIds=ep['sceneIds'],proposedSceneOrder=order,
  originalOrderPreserved=True,maximumAddedActualSeconds=35))
def mul(a,b):
 w,x,y,z=a;v,u,t,s=b
 return np.array([w*v-x*u-y*t-z*s,w*u+x*v+y*s-z*t,w*t-x*s+y*v+z*u,w*s+x*t-y*u+z*v])
def qz(angle):return np.array([math.cos(angle/2),0,0,math.sin(angle/2)])
def rotate(q,v):return mul(mul(q,np.r_[0,v]),q*np.array([1,-1,-1,-1]))[1:]
checks=[]
for parameter,degrees in [(.5,45),(.25,22.5)]:
 q=qz(parameter*math.pi/2);axes=np.array([rotate(q,v) for v in np.eye(3)])
 assert np.allclose(axes@axes.T,np.eye(3))
 assert np.allclose(axes[0],[math.cos(math.radians(degrees)),math.sin(math.radians(degrees)),0])
 checks.append(dict(parameter=parameter,actualDegrees=degrees,storedHalfAngleDegrees=degrees/2,
  rotatedBody=axes[0].tolist(),rotatedWing=axes[1].tolist(),lengthAndPerpendicularityPreserved=True))
matrix=np.array([[0,-1,0],[1,0,0],[0,0,1]])
by_quaternion=np.column_stack([rotate(qz(math.pi/2),v) for v in np.eye(3)])
assert np.allclose(matrix,by_quaternion)
reflection=np.diag([-1,1,1]);halfturn=np.diag([-1,-1,1])
assert np.allclose(reflection.T@reflection,np.eye(3)) and math.isclose(np.linalg.det(reflection),-1)
assert np.allclose(halfturn.T@halfturn,np.eye(3)) and math.isclose(np.linalg.det(halfturn),1)
source=read(I/'candidate-comparison.json')
assert sha(ROOT/source['sourceFile'])==source['sourceSha256']
assert all(p['completed'] and p['rate']==1 for p in source['nativeProofs'])
result=dict(schemaVersion=1,auditedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 draftSha256=sha(I/'additions-draft.json'),baselineMetadataAndNarrationUnchanged=True,
 retainedScenes=sum(len(e['sceneIds']) for e in base['episodes']),verifiedOriginalFiles=preserved,
 proposedInsertionMaps=insertions,modelCalculations=checks,quaternionMatrix90DegreesAgree=True,
 reflectionDeterminant=-1,halfTurnDeterminant=1,diagonalProductRuleScopedToDiagonalExamples=True,
 conventions=draft['conventions'],sourceHashAndNormalSpeedComparisonVerified=True,
 screenDirectionsNotMeasuredWorldCoordinates=True,hiddenGameInterpolationNotClaimed=True,
 teachingChain='retained sports action -> aircraft action -> explicitly chosen fixed model -> result -> retained next question',
 ratioPlanning='New actual frames must be 2/3 of new explanation frames, with total divisible by 5. Preserve all original frames and PCM. Acquire an additional clear source interval if 35 seconds is insufficient.',
 prerequisites=['time parameter versus progress along a fixed path','half angle before quaternion use',
 'three transformed basis vectors before matrix columns','orthonormality and reflection before determinant validation'],
 preTtsDraftAuditPassed=True,newTtsStarted=False,currentMovingPixelsApproved=False,
 humanListeningComplete=False,rightsHumanReviewComplete=False)
(I/'numeric-and-preservation-draft-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(retainedScenes=result['retainedScenes'],proposedAdditions=8,draftAuditPassed=True,newTtsStarted=False)))
