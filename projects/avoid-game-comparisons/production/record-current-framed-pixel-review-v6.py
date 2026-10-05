"""Record directly read encoded gameplay and adopt only the two new corrections."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
old=read(WORK/'current-framed-cue-local/execution.json');new=read(WORK/'two-lower-crops-local/execution.json')
assert len(old['images'])==543 and len(old['sheets'])==91 and len(new['images'])==24 and len(new['sheets'])==4
for state in [old,new]:
 assert state['exitCode']==0
 for row in state['images']+state['sheets']:assert sha(ROOT/row['path'])==row['sha256']
newIds=[x['id'] for x in new['cuts']]
profile=read(WORK/'source-framing-profile.json');media=read(WORK/'framed-media-index.json')
# Preserve the complete first pixel-review index instead of overwriting its source hash.
baseline=WORK/'framed-media-before-two-corrections.json';assert not baseline.exists()
baseline.write_bytes((WORK/'framed-media-index.json').read_bytes())
for cut in new['cuts']:
 for key in ['cuts']:
  n=next(i for i,r in enumerate(media[key]) if r['id']==cut['id'])
  prior=media[key][n];media[key][n]={**prior,**cut,'reusedByteIdentical':False,'previousCandidateSha256':prior['sha256'],'finalPixelsApproved':True,'pixelReview':rel(BASE/'current-framed-pixel-direct-review-v6.json')}
 for r in profile['profiles']:
  if r['id']==cut['id']:r.update(cropFilter=cut['cropFilter'],filter=cut['filter'])
for cut in media['cuts']:
 assert sha(ROOT/cut['video'])==cut['sha256']
 cut.update(finalPixelsApproved=True,pixelReview=rel(BASE/'current-framed-pixel-direct-review-v6.json'))
for r in profile['profiles']:r['finalPixelsApproved']=True
profile.update(updatedAt=now,allFinalPixelsApproved=True,evidence=profile['evidence']+[rel(BASE/'current-framed-pixel-direct-review-v6.json')])
(WORK/'source-framing-profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
media.update(updatedAt=now,profileSha256=sha(WORK/'source-framing-profile.json'),allFinalPixelsApproved=True)
(WORK/'framed-media-index.json').write_text(json.dumps(media,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
observations=[
 'Directly read all91 pages/543 current encoded frame/caption samples, then four pages/24 new targeted lower-avatar samples. All111 current cuts and189 actual Korean cue intersections are covered; final full-composite verification is still required.',
 'Adopted two lower crops1440x810 at240,270. Printed night/day words, book avatar feet, bubble launcher, colored ball field and left character panel remain readable above the fixed caption. Earlier full-frame feet overlap is preserved as historical rejected framing.',
 'Four prior targeted crops retain late feet/body, upper drill/falling red enemy, descending avatar and water vehicle/drill.02p4 has a small noncentral red-tail edge at87/89 under the box; its upper falling body and the narrated drill/attack remain visible.06p2 briefly clips feet at the bottom source crop near53, while landing/walking at63–89 is fully visible. Neither limitation conceals the narrated action or a required interface.',
 'The exact source88 starts on clean4850 after the editorial different-map dissolve, and ends before5035 next source action. Mine94 is a separately reviewed in-game book/desk transition. Cue06cup starts at177.0s at the exact first cup shot.',
 '13 book entry, tilting, left/right yellow-key motion and14 red chest card remain visible above the fixed narration band. The card claim is attached to the independently observed165.03s card interval, not preceding combat.',
 '10 water clips remain separate actions; no continuous chase is inferred.10 accessibility combat retains its invincibility/one-hit-killON context label. KWD development context is visible; some unrelated source bottom typography is cropped at the edge and is not presented as complete source text.',
 'All game content fills1920x1080; source audio, agent games, loops and arbitrary slowdown are zero. Every narration box stays at960,970/48px/max2lines. Current encoded sample approval does not establish whole-video listening, final mix, final composite or upload completion.'
]
review=dict(reviewedAt=now,planSha256=sha(WORK/'plan.json'),priorMediaIndex=rel(baseline),priorMediaIndexSha256=sha(baseline),
 finalFramedMediaIndex=rel(WORK/'framed-media-index.json'),finalFramedMediaIndexSha256=sha(WORK/'framed-media-index.json'),
 all111EncodedCutsDirectlyRead=True,actualCueIntersections=189,fixedCenter=[960,970],allCurrentGameplayCueSamplesApproved=True,
 originalSampleState=rel(WORK/'current-framed-cue-local/execution.json'),originalStateSha256=sha(WORK/'current-framed-cue-local/execution.json'),
 correctiveSampleState=rel(WORK/'two-lower-crops-local/execution.json'),correctiveStateSha256=sha(WORK/'two-lower-crops-local/execution.json'),
 newCorrectedCuts=newIds,imagesDirectlyRead=567,sheetsDirectlyRead=95,imageEvidence=[dict(path=r['path'],sha256=r['sha256'],directlyRead=True) for r in old['images']+new['images']],
 sheetEvidence=[dict(path=r['path'],sha256=r['sha256'],directlyRead=True) for r in old['sheets']+new['sheets']],findings=observations,
 finalCompositePixelsReviewed=False,finalMixReviewed=False,humanWholeListening='pending',newGitImages=0)
(BASE/'current-framed-pixel-direct-review-v6.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(cuts=111,images=567,actualCueSamplesApproved=True,finalCompositeApproved=False,newGitImages=0)))
