"""Bind current draft evidence while keeping final narration/pixel QA pending."""
from pathlib import Path
import hashlib,json
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proof=read(O/'native-silent-draft-review-current.json')
assert {(x['scene'],x['duration']) for x in proof}=={('trail annotations',35),('gear-v3 annotations',9.6),('QC11',18)}
assert all(x['rate']==1 and x['endedAt']==x['duration'] for x in proof)
tracks={};review=[]
for stem in ['trail','gear-v3','besiege']:
 p=R/f'{stem}-screen-track.json';d=read(p)
 assert sha(ROOT/d['video'])==d['videoSha256']
 tracks[stem]=(p.relative_to(ROOT).as_posix(),sha(p))
 review.append(dict(stem=stem,trackSha256=sha(p),sourceDraftSha256=d['videoSha256'],annotatedDraftSha256=sha(O/f'action-drafts/{stem}-annotated-draft.mp4'),observedFrames=len(d['frames']),visibleFrames=sum(bool(f and f['visible']) for f in d['frames']),manualProposals=sum(bool(f and f.get('manualInterpolationCandidate')) for f in d['frames']),denseDraftPixelsReviewed=True,currentNative1xCompleted=stem!='besiege',finalNarratedAndCaptionedPixelsReviewed=False))
for p in [R/'additions.json',ROOT/'projects/game-math-quaternion-foundations-v3/production/lesson.json',ROOT/'projects/game-math-quaternion-calculations-v3/production/lesson.json']:
 d=read(p)
 for s in d['scenes']:
  if s['id'] not in {'QF10','QF20','QF30','QC10','QC20','QC30'}:continue
  stem={'QF10':'trail','QC10':'trail','QF20':'gear-v3','QC20':'gear-v3','QF30':'besiege','QC30':'besiege'}[s['id']]
  s['annotation'].update(tracksPrepared=True,trackFile=tracks[stem][0],trackSha256=tracks[stem][1],movingPixelApproval=False)
 write(p,d)
write(R/'current-draft-review.json',dict(recordedAt=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),nativeProof=(O/'native-silent-draft-review-current.json').relative_to(ROOT).as_posix(),nativeProofSha256=sha(O/'native-silent-draft-review-current.json'),tracks=review,QC11CurrentPreviewSha256=sha(O/'explanation-preview/videos/quaternion_four_game_v3/540p30/QC11.mp4'),meaning='Current silent draft operation/alignment check; final voice, captions, full source selection and listening remain pending'))
q=read(B/'queue.json');q['execution'].update(stage='quaternion-four-game-v3-three-critical-line-retakes-and-current-draft-review; final timing/render/publishing pending',fullTaskComplete=False,currentQuaternionDraftReview=(R/'current-draft-review.json').relative_to(ROOT).as_posix(),lastProgressAt=datetime.now(ZoneInfo('Asia/Seoul')).isoformat());write(B/'queue.json',q)
print('Bound current source/track hashes; final moving narrated/captioned approval remains false.')
