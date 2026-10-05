"""Adopt reviewed source crops/clean action88; preserve every current PCM sample."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();dest=BASE/'measured-edit-v6';assert not dest.exists()
old=BASE/'measured-edit-v5/plan.json';plan=copy.deepcopy(read(old));review=read(BASE/'targeted-framing-adoption-review.json')
for s in plan['scenes']:
 assert sha(ROOT/s['audio'])==s['audioSha256']
 for c in s['segments']:
  if c['id'] in review['adoptedCropFilters']:
   c.update(sourceCropFilter=review['adoptedCropFilters'][c['id']],sourceFramingReview=rel(BASE/'targeted-framing-adoption-review.json'),sampledFocusClear=True,finalCaptionFramingApproved=False)
s13=next(s for s in plan['scenes'] if s['id']=='13');c=next(c for c in s13['segments'] if c['bankCutId']=='action-88')
assert c['sourceStartFrame']==4838 and c['frames']==190
c.update(id='13-p1-action-88-4850-5035',sourceStartFrame=4850,sourceEndFrameExclusive=5035,
 inSeconds=4850/c['nativeFps'],outSeconds=5035/c['nativeFps'],nativeSeconds=185/c['nativeFps'],frames=185,seconds=185/60,
 nativeToOutputQuantizationFrames=185-185/c['nativeFps']*60,nativeEdgeReview=rel(BASE/'targeted-framing-adoption-review.json'),mediaCompiled=False)
s13['frames']-=5;s13['seconds']=s13['frames']/60
# Preserve the complete p1/p2 source run. The small removed visual duration falls
# in existing quiet reading tails, not in a spoken syllable or a good explanation.
s13['pcmPlacement']=[dict(kind='preserved-current-PCM',fromSample=0,toSample=505728,outputFromSample=0,outputToSample=505728),
 dict(kind='inserted-silence',samples=44672,outputFromSample=505728,outputToSample=550400,reason='Observe the named key directions at normal speed before the preserved writing explanation.'),
 dict(kind='preserved-current-PCM',fromSample=505728,toSample=685440,outputFromSample=550400,outputToSample=730112),
 dict(kind='inserted-silence',samples=288,outputFromSample=730112,outputToSample=730400,reason='Retain the complete third paragraph and end on the explanation.')]
s12=next(s for s in plan['scenes'] if s['id']=='12');diagram=next(c for c in s12['segments'] if c['id']=='12-2-white-comparison')
assert diagram['frames']==263;diagram.update(frames=260,seconds=260/60)
for p in s12['pcmPlacement']:
 if p['kind']=='inserted-silence' and p['outputFromSample']==715416:
  assert p['samples']==6584;p.update(samples=5384,outputToSample=720800,reason='Read the new unapproved cost comparison at4.333333s; all4.109s of its current PCM remain.')
 elif p['outputFromSample']>=722000:
  p['outputFromSample']-=1200;p['outputToSample']-=1200
s12['frames']-=3;s12['seconds']=s12['frames']/60
cursor=120
for s in plan['scenes']:
 s['startFrame']=cursor;local=0
 for c in s['segments']:
  c.update(localFromFrame=local,startFrame=cursor+local);local+=c['frames'];c['endFrameExclusive']=cursor+local
 assert local==s['frames'];cursor+=s['frames']
 pieces=s['pcmPlacement'];assert pieces[0]['outputFromSample']==0 and pieces[-1]['outputToSample']==s['frames']*400
 assert all(a['outputToSample']==b['outputFromSample'] for a,b in zip(pieces,pieces[1:]))
 kept=[p for p in pieces if p['kind']=='preserved-current-PCM']
 assert kept[0]['fromSample']==0 and kept[-1]['toSample']==s['samples']
 assert all(a['toSample']==b['fromSample'] for a,b in zip(kept,kept[1:]))
 assert sum(p['toSample']-p['fromSample'] for p in kept)==s['samples']
cuts=[c for s in plan['scenes'] for c in s['segments'] if c['classification']=='actual-existing-game']
diagrams=[c for s in plan['scenes'] for c in s['segments'] if c['classification']=='explanation']
actual=sum(c['frames'] for c in cuts);explanation=sum(c['frames'] for c in diagrams)
assert actual==18828 and explanation==12552 and abs(actual-.6*(actual+explanation))<1e-8
assert sum(c['frames'] for c in diagrams if 'original-white' in c['id'])==9800
for source in {c['sourceVideoId'] for c in cuts}:
 rows=sorted((c for c in cuts if c['sourceVideoId']==source),key=lambda c:c['sourceStartFrame'])
 assert all(a['sourceEndFrameExclusive']<=b['sourceStartFrame'] for a,b in zip(rows,rows[1:]))
plan.update(createdAt=now,status='current15-clean-native-source-framing-candidate-edited-join-ASR-pending',previousCandidate=dict(path=rel(old),sha256=sha(old)),
 actualFrames=actual,explanationFrames=explanation,bodyFrames=actual+explanation,finalFrames=actual+explanation+720,body60_40ErrorFrames=0,
 targetedFramingReview=rel(BASE/'targeted-framing-adoption-review.json'),sourceBank='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/source-action-bank-v8.json',
 finalTimingApproved=False,bodyRatioApproved=False,allCaptionPixelsReviewed=False,finalMixBuilt=False,finalMixAsrApproved=False)
plan['flaggedNativeCorrections']['action88']=dict(startInclusive=4850,endExclusive=5035,oldStartInclusive=4838,oldEndExclusive=5028,reason='Exclude different-map editorial dissolve; add only seven directly reviewed adjacent active native frames, stop before action89.')
plan['flaggedNativeCorrections']['ratioRebalance']='Only three frames of the new unapproved12p2 diagram reading tail are removed. All current PCM and the original9800 explanation frames are preserved. Candidate60:40 is exact; final pixel/mix verification remains pending.'
plan['wordAlignmentReviewNotes'].append('13p1/p2 are the same uninterrupted source PCM across related book/key footage; source visual transition precedes paragraph2 by0.052s without truncation. Cup KO/EN cue must start at the actual23.333333s PCM/visual boundary, not its earlier ASR estimate.')
dest.mkdir();write(dest/'plan.json',plan)
bank_path=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/source-action-bank-v7.json';bank=read(bank_path)
b=next(x for x in bank['clips'] if x['id']=='action-88');b.update(startFrame=4850,endFrameExclusive=5035,inSeconds=4850/b['nativeFps'],outSeconds=5035/b['nativeFps'],seconds=185/b['nativeFps'],directReview=rel(BASE/'targeted-framing-adoption-review.json'))
bank.update(createdAt=now,previousBank=dict(path=rel(bank_path),sha256=sha(bank_path)),uniqueSourceSeconds=sum(x['seconds'] for x in bank['clips']),bodyRatioApproved=False,finalCutAndCaptionApproval=False)
bank['bySourceSeconds']={source:sum(x['seconds'] for x in bank['clips'] if x['sourceVideoId']==source) for source in {x['sourceVideoId'] for x in bank['clips']}}
write(bank_path.with_name('source-action-bank-v8.json'),bank)
evidence=dict(reviewedAt=now,plan=rel(dest/'plan.json'),planSha256=sha(dest/'plan.json'),actualFrames=actual,explanationFrames=explanation,bodyFrames=actual+explanation,finalFrames=actual+explanation+720,candidateSeconds=(actual+explanation+720)/60,ratioErrorFrames=0,
 all15PcmHashesPreserved=True,all60ParagraphsPreserved=True,originalSixExplanationFrames=9800,newSourceImagesLocalOnly=True,newGitImages=0,
 finalTimingApproved=False,allFinalPixelsApproved=False,editedJoinAsrApproved=False,finalMixBuilt=False,
 corrections=['Four reviewed source-only crop candidates adopted; fixed caption position unchanged.','Action88 different-map dissolve trimmed independently; adjacent active native samples added without overlap.','13p1/p2 source PCM kept continuous; no synthesis.','Three frames removed only from the new unapproved12p2 reading tail; every narration sample and original good explanation preserved.'])
write(BASE/'framing-candidate-v6-preservation-review.json',evidence)
print(json.dumps(evidence,ensure_ascii=False))
