"""Record current content/Studio comparison and an explicit review-flag transition."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
planp=O/'cross-game-causal-and-source-plan-v1.json'
plan=read(planp);prior=dict(plan);prior.pop('pairedDirectReview');prior['wholePairedTextReviewed']=False
encoded=(json.dumps(prior,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode('utf-8')
review=read(O/'cross-game-paired-script-direct-review-v1.json')
oldsha=next(x['sha256'] for x in review['evidence'] if x['path']==rel(planp))
assert hashlib.sha256(encoded).hexdigest()==oldsha
before=O/'cross-game-causal-and-source-plan-pre-review-v1.json'
assert not before.exists();before.write_bytes(encoded)
save(O/'cross-game-plan-review-flag-transition-v1.json',dict(recordedAt=now,beforePath=rel(before),beforeSha256=oldsha,afterPath=rel(planp),afterSha256=sha(planp),changedFields=['wholePairedTextReviewed','pairedDirectReview'],wordingAndSourcePlanUnchanged=True,reason='Review sealer captured the directly read plan before setting its reviewed flag; current voice request binds the resulting plan.'))
invp=ROOT/'production/preflight/game-math-orientation-matrices.json';inv=read(invp)
prevp=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json';prev=read(prevp)
previous={x['path']:x['sha256'] for x in prev['inputFiles']}
changed=[x for x in inv['inputFiles'] if previous.get(x['path'])!=x['sha256']]
assert len(inv['existingProjects'])==88 and len(inv['inputFiles'])==509 and not inv['exactMatches']
assert len(changed)==10 and all(x['path'].startswith('projects/motion-sickness-games/') for x in changed),'New foreign evidence needs whole content and current Studio review.'
for x in inv['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
save(O/'duplicate-inventory-before-decision-v1.json',inv)
combined=read(R/'combined-script-preservation-v1.json')
proofpaths=[O/'duplicate-candidate-v1.json',R/'combined-script-preservation-v1.json',R/'current17-mixed-complete-direct-review-v2.json',R/'current17-main-promotion-v1.json',R/'publishing/private-settings-direct-review-v1.json',R/'publishing/schedule-direct-review-v1.json',R/'duplicate-content-and-studio-direct-review-v10.json',prevp,O/'current-studio-full-description-v1.ax.txt',O/'current-studio-schedule-v1.ax.txt',O/'current-studio-future-list-v1.ax.txt']
save(O/'duplicate-content-and-studio-direct-review-v1.json',dict(schemaVersion=1,reviewedAt=now,candidate=inv['candidate'],inventoryDigest=inv['inputsDigest'],inventoryProjectCount=88,inventoryInputCount=509,changedInputs=changed,unchangedForeignInputCount=499,unchangedForeignWholeReviewsReused=rel(R/'duplicate-content-and-studio-direct-review-v10.json'),allCurrentChangesCompared=True,
 findings=['This is an authorized additive replacement of the existing orientation lesson 6-kP65hrZcI, rather than another copy of that upload. Original24 scenes/140 paired paragraphs and six measured additions are preserved.',
 'Orientation constructs a column rotation matrix from object basis directions in one reference frame, verifies orthogonality/handedness and distinguishes local-to-world from its transpose. Euler order/gimbal/axis-angle, quaternion half-angle/inverse/composition, SLERP paths, representation conversions and camera clipping/projection answer different central questions; exact unchanged scripts remain bound to prior whole-content reviews.',
 'The only ten inputs newly included relative to the latest motion inventory belong to the completed owned motion revision. Its full17 scenes/81 paragraphs were directly compared during current mixed review, original14 plus new3 retained by the preservation proof. Camera/aim/locomotion comfort options differ from orientation matrix construction. Its active receipt/main promotion/private settings and actual Oct12 replacement were verified; no foreign files/settings changed.',
 'CUA105 full title/description, SD/HD and disabled Save directly read. Its actual schedule dialog shows October13 2026,09:00,GMT+0900; no schedule edit or Save. CUA102 current28 future titles/dates directly read, including orientationOct13 and latest owned motionOct12. The list is not a whole-description review of every foreign upload.',
 'Shared game recording segments in quaternion examples are explicitly declared transfer comparisons with different narration, not proof of unique recording rights. Public rights and human listening remain pending.'],
 studioReads=dict(orientationVideoId='6-kP65hrZcI',orientationTab=105,futureTab=102,wholeOrientationDescriptionRead=True,actualDate='2026-10-13',actualTime='09:00',actualTimezoneLabel='GMT+0900',sdHdComplete=True,saveDisabled=True,futureRowsRead=28,settingsChanges=0),verdict='distinct-authorized-revision',currentCheckPassed=False,foreignQualityOrRightsApproved=False,
 evidence=[dict(path=rel(p),sha256=sha(p)) for p in proofpaths]))
print(json.dumps(dict(planTransitionVerified=True,existingProjects=88,inputs=509,changedOwnedMotion=10,unchangedForeign=499,readyForStrictDecision=True)))
