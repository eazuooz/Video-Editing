"""Bind reviewed pieces to the measured timeline; prepare, never render or approve."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
out=R/'current17-assembly-inputs-v2.json';assert not out.exists()
plan=read(R/'measured-current17-plan-v2.json')
normal=read(R/'remaining-action-normal-playback-observation-v4.json')
assert normal['allEightNormalSpeedStartEndsObserved']
roles={v['id']:v for v in read(R/'remaining-action-normal-playback-plan-v4.json')['items']}
extra=read(R/'extra-annotation-normal-playback-observation-v1.json');assert extra['normalSpeedStartEndObserved']
portal='shared/output/cross-game-example-coverage/motion/extra-annotation-pieces-v2/portal-held-putdown-portal-beam/silent-role-annotation.mp4'
power='shared/output/cross-game-example-coverage/motion/extra-annotation-pieces-v4/powerwash-independent-nozzle-aim/silent-role-annotation.mp4'
pieces=[];newscenes={v['id']:v for v in plan['scenes'] if not v['retainedBaseline']}
def append_new(sid):
 for part in newscenes[sid]['parts']:
  ident=part['id'];mask=False;offset=0
  if ident in roles:
   row=roles[ident];path=row['path'];digest=row['sha256'];assert row['frames']==part['frames']
  elif 'reuseVideo' in part:path=part['reuseVideo'];digest=part['videoSha256']
  else:
   assert ident in ['07b-cube-room-prefix','07b-cube-room-observe','08b-tool-and-common-question']
   path=power if ident.startswith('08b') else portal;digest=sha(ROOT/path);mask=True;offset=part.get('sourceOutputStartFrame',0)
   review=read(R/('extra-annotation-pieces-sampled-direct-review-v4.json' if ident.startswith('08b') else 'extra-annotation-pieces-sampled-direct-review-v2.json'))
   assert review['sha256RecheckedFiles'][path]==digest
  assert sha(ROOT/path)==digest
  pieces.append(dict(id=ident,scene=sid,path=path,sha256=digest,frames=part['frames'],startFrame=part['startFrame'],endFrame=part['endFrame'],sourceOutputStartFrame=offset,clearBakedPreviewCaption=mask,classification=part['classification'],reencodeRequired=mask,alreadyEncodedAndReviewed=not mask,finalNarrationTimedPixelsApproved=False))
cursor=0
for i,v in enumerate(plan['retainedTwentySilentPieces']):
 assert sha(ROOT/v['path'])==v['sha256']
 pieces.append(dict(id=f'retained-{i:02d}',path=v['path'],sha256=v['sha256'],frames=v['frames'],startFrame=cursor,endFrame=cursor+v['frames'],retainedByteIdentical=True,reencodeRequired=False))
 cursor+=v['frames']
 if i in [13,14,17]:
  sid={13:'07b',14:'08b',17:'11b'}[i];assert cursor==newscenes[sid]['startFrame'];append_new(sid);cursor+=newscenes[sid]['frames']
assert len(pieces)==37 and cursor==plan['totalFrames']==51186
assert all(a['endFrame']==b['startFrame'] for a,b in zip(pieces,pieces[1:]))
assert sum(v['frames'] for v in pieces if v.get('retainedByteIdentical'))==40193
value=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),planSha256=sha(R/'measured-current17-plan-v2.json'),pieces=pieces,retainedPieceCount=20,newPieceCount=17,maskSplitPieceCount=3,frames=cursor,seconds=cursor/60,maskMethod='Retain upper900 annotated pixels; bottom180 uses blurred same-frame upper image, excluding baked preview caption pixels entirely. No slowdown or looping.',allInputHashesVerified=True,renderStarted=False,finalAudioApproved=False,finalPixelsApproved=False,finalRatioApproved=False,newGitMedia=0)
out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedPieces=37,byteIdenticalBaselinePieces=20,requiredMaskSplitPieces=3,frames=cursor,renderStarted=False)))
