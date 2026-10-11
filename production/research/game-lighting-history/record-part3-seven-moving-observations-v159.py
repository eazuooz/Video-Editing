"""Save actual CUA normal-speed observations before repairing two final defects."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=m.ROOT/'projects/game-lighting-history-04/production'
pair=m.read(P/'part3-reviewed-pair-build-v149.json')
assert pair['captioned']['sha256']=='cdb87bbc334f2bd165daf66f3a41b6b66bd7a592f0be6896df7d530c8ea5db7a'
request=m.read(P/'part3-final-moving-review-request-v158.json')
assert request['sourceSha256']==pair['captioned']['sha256']
observations=[
 ('hogwarts-terrace-reference',271.655,'Near rail/distant landscape marks follow the observed camera motion and hide across reacquisition; fixed captions remain readable.',None),
 ('hogwarts-courtyard-ui',328.259,'Actual player clothing and later Talk prompt were watched across the entire approach. External white note overlaps Nellie Oggspire name around local13 seconds.','Move external note to left background; preserve actual Talk and all fixed narration captions.'),
 ('grade-shared-reference',673.761,'Full color-grading camera/setting comparison watched. Red lowest-face mark is detached during local8–10 seconds; pre7.25 and post13 face anchors inspected at full resolution.','Hide red during fast camera motion7.25–13 and show camera reacquisition note.'),
 ('resource-viewer-context',1267.007,'Whole editor resource type/size/flags/owner inspection visible; presenter and conference backdrop excluded; fixed bottom captions read.',None),
 ('resource-name-limits',1289.002,'Whole resource-name inspection watched. Visible name does not by itself prove frame cost; narration/diagram preserve this distinction.',None),
 ('resource-upload-control',1385.386,'Whole actual UE resource-upload console/settings demonstration watched; upload control is not labelled frame generation.',None),
 ('resource-budget-to-measure',1407.643,'Whole resource budget/settings inspection followed by black measurement diagram watched; visual settings are distinguished from measured timing.',None),
]
records=[]
for key,observed_end,note,issue in observations:
 row=next(r for r in request['rows'] if r['id']==key)
 records.append(dict(id=key,rangeSeconds=row['ranges'][0],playbackRate=1,fullSelectedIntervalActuallyPlayed=True,
  observedPausedTimeSeconds=observed_end,actualObservation=note,issue=issue,finalIssueFree=issue is None,
  tool='CUA tab56 selected range play control; video read-only DOM and actual screenshots',
  sourceSha256=pair['captioned']['sha256']))
m.save(P/'part3-seven-final-moving-observations-v159.json',dict(recordedAt=m.stamp(),
 historicalSource=pair['captioned'],requestSha256=m.sha(P/'part3-final-moving-review-request-v158.json'),
 records=records,completedNormalRateIntervals=7,issuesRequiringRepair=2,
 allMovingPixelsReviewed=False,allFinalPixelsReviewed=False,qaApproved=False,
 humanWholeListening='pending',humanPronunciation='pending',newGitImages=0))
print('Saved seven actual normal-speed intervals; two observed defects remain unapproved.')
