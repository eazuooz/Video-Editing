"""Persist the actual21board/125still direct review, retaining moving/final gates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
path=PROOF/'targeted-input-recheck-v3.json';e=read(path)
assert e['boardCount']==21 and e['sampleCount']==125
for row in e['tiles']+e['boards']:assert sha(ROOT/row['path'])==row['sha256']
notes={
 (1,3):'Market Q1110–1285: grounded/airborne player body and umbrella visible after the targeted crop; some feet approach the box boundary. Upper wire scene retained. Still review only; whole transition and action timing pending.',
 (4,6):'Q1287/1288: upper umbrella/wire retained. Boss B1470–1619: player, umbrella and high barrel visible; source upper beams remain. Direction of high-aim words and full action timing pending.',
 (7,8):'C300–319: ladder, player and shot clearer above the fixed box. Z1726/1727: low enemies already approach/cross native lower frame edge, upper player remains clear. Z1756–1786: grounded main body/tool and surrounding attackers visible after crop.',
 (9,11):'Z1793–1829: main ground firing and turret context visible, caption below platform. B2130–2332: fall, landing, umbrella jump and nearby saw/targets retained. Lower opponents partly enter/leave source edge; upper player remains visible.',
 (12,14):'B2339–2549: main umbrella/jump/ground action visible; some peripheral lower targets remain partly hidden. Boss3480: main body and barrel retained, right upper arm extends beyond crop.',
 (15,16):'Boss3481–3569: main umbrella/player and barrel remain visible, but upper projectile row is clipped at3510. This is a real framing tradeoff; do not approve complete source context without native moving comparison.',
 (17,18):'Pedro5580–5811: native upper rooms/targets preserved. Narrow cues221–225 leave lower orange/purple feet visible beside the box. Bright muzzle flash briefly masks the player in source pixels, not a subtitle failure.',
 (19,21):'Pedro5820–6010: new narrower cues reveal lower bodies/feet; upper active aiming, trajectories and room exits preserved. Closing 확인해 보세요. is one0.74second cue. New exact split-edge pixels, readable timing and full motion remain pending.',
}
dest=PROOF/'targeted-input-direct-review-v3.json';assert not dest.exists()
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now,evidence=rel(path),evidenceSha256=sha(path),
 sourceCandidate=e['sourceCandidate'],sourceCandidateSha256=e['sourceCandidateSha256'],captionCandidate=e['captionCandidate'],
 captionCandidateSha256=e['captionCandidateSha256'],all21BoardsDirectlyRead=True,all125TilesDirectlyRead=True,
 boards=[dict(index=b['index'],path=b['path'],sha256=b['sha256'],tileIndices=b['tileIndices'],directlyRead=True,
             notes=next(v for (a,z),v in notes.items() if a<=b['index']<=z)) for b in e['boards']],
 exactNewCueEdgePixelsReviewed=False,allSourceMotionReviewed=False,allFinalCaptionPixelsReviewed=False,
 finalTimingApproved=False,finalTimelineAdopted=False,humanListeningPronunciation='pending',newGitImages=0,
 noPcmOrSourceIntervalsChanged=True,noEnglishSrtChanged=True,
 unresolved=['Boss06-part3-cut07 upper projectile row clipped in bottom120 trial; compare native moving composition before adoption.',
             'Lift06-part1-cut03: lower figures partly lie beyond the raw source lower edge. Upper main player firing is clear in re-read1686; full moving focus/context still pending.',
             'New semantic split-edge pixels and narration/action timing pending; current stills are preserved original sampling positions.'])
dest.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
next_action='Review complete moving candidate source/word alignment, compare boss07 native versus targeted crop, and check exact new Pedro cue edges. Then adopt measured timing and render independent white6+2. All70paragraphs/PCM373.680083333s/23570candidateframes and118EN preserved; final mix/ASR/pair/encodedQA/collection/private false. Closed input extraction57728/session39466 must not rerun.'
patch=dict(stage='targeted-crop-and-narrow-cue-input-review-motion-pending',nextAction=next_action,
 wordCaptionCandidate='projects/familiar-game-rules/production/word-caption-candidate-v3/captions.json',
 wordActionSourceCandidate='projects/familiar-game-rules/production/word-action-source-candidate-v2.json',
 inputWordCueDirectReview='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/word-cue-input-direct-progress-v1.json',
 targetedFramingDirectReview='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/targeted-framing-direct-review-v2.json',
 targetedInputDirectReview=rel(dest),allInput225BoardsDirectlyRead=True,allModified21BoardsDirectlyRead=True,
 finalTimingApproved=False,allSourceMotionReviewed=False,allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,
 render=False,qa=False,collected=False,uploaded=False,updatedAt=now)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
 j=read(p);j.update(patch)
 if isinstance(j.get('execution'),dict):j['execution']['status']='closed-native-literal-worker-all225boards-read-targeted125stills-reviewed-motion-pending'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
queue=ROOT/'production/batches/sakurai-planning-game-design/queue.json';j=read(queue)
item=next(r for r in j['items'] if r['slug']=='familiar-game-rules');item.update(patch)
item['execution']['status']='closed-native-literal-worker-all225boards-read-targeted125stills-reviewed-motion-pending'
j['updatedAt']=now;j['lastProgressAt']=now
queue.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(reviewedBoards=21,reviewedSamples=125,updatedCheckpoints=3,sourceMotionApproved=False,render=False)))
