from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
obs=read(R/'final-board-observations-v1.json'); ix=read(ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v1/index.json')
assert obs['all197BoardsActuallyDirectlyRead'] and obs['all1180SelectedSamplesActuallyDirectlyRead']
assert [n for v in obs['directReadingRanges'] for n in range(v['first'],v['last']+1)]==list(range(1,198))
assert len(ix['samples'])==1180 and len(ix['boards'])==197
for v in ix['samples']+ix['boards']:assert sha(ROOT/v['path'])==v['sha256'],v['path']
assert all(v['pts']==v['frame']*1500 for v in ix['samples'])
unresolved=[{'scene':'02','frames':[6573,6747,6922],'cue':31,'finding':'Spoken right is additional shake but right still shows stationary body, with additional arrow on left. Replace late comparison with camera-turning left and extra camera effect right, retaining early visual/body comparison.'},
 {'scene':'06b','frames':[20400,20524],'finding':obs['fullSizeFollowup']['finding']}]
record=dict(schemaVersion=1,recordedAt=now(),status='held-after-complete-direct-review',source=ix['source'],sourceSha256=ix['sourceSha256'],
 index='shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v1/index.json',indexSha256=sha(ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v1/index.json'),
 allListedSamplesDirectlyRead=True,all197BoardsDirectlyRead=True,all1180SamplesDirectlyRead=True,allExactAbsolutePtsVerified=True,
 allFinalCueCutPixelsApproved=False,unresolvedFindings=unresolved,observations='final-board-observations-v1.json',allIntermediateFramesViewed=False,
 originalIntroMemberPreserved=True,allFinalPixelsApproved=False,humanListeningApproved=False,publicRightsApproved=False,newGitImages=0)
p=R/'final-pixel-direct-review-v1.json';assert not p.exists();save(p,record)
flow=read(R/'final-flow-ended-observation-v1.json');assert flow['status']['ended'] and flow['status']['playbackRate']==1 and flow['status']['muted']
assert [x['event'] for x in flow['events']]==['play','seeked','pause','ended']
assert flow['events'][1]['currentTime']<.02 and flow['events'][2]['currentTime']==669.883333
p=R/'final-whole-flow-direct-review-v1.json';assert not p.exists()
save(p,dict(schemaVersion=1,recordedAt=now(),status='held-visual-findings',sourceSha256=ix['sourceSha256'],wholeNormalSpeedPlaybackEnded=True,
 sampledFlowApproved=False,unresolvedFindings=unresolved,observation='final-flow-ended-observation-v1.json',muted=True,humanListeningApproved=False,
 allIntermediateFramesViewed=False,continuousDecodedPlaybackTrue=True,newGitImages=0))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='final-pair-v1-held-two-targeted-visual-findings',ownedJob=None,
 currentMixedAudioApproved=False,currentMixedContentReviewPassed=True,allFinalPixelsApproved=False,qaApproved=False,outputCollected=False,
 finalPixelReview='final-pixel-direct-review-v1.json',wholeFlowReview='final-whole-flow-direct-review-v1.json',
 next='Fix only scene02 late reference and scene06b caption clearance; preserve all current PCM/AAC/SRT/timing and held v1. Render/review two targets, then verified v2 pair/current pixels before adoption or upload.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw);q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=None,next=cp['next'])
item=next(x for x in q['items'] if x['slug']=='motion-sickness-games');item.update(status=cp['stage'],currentExecution=None)
item['review']['allFinalPixelsPassed']=False;item['review']['causalFlowPassed']=False;q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw;save(qp,q)
print(json.dumps({'held':True,'boardsDirectlyRead':197,'samplesDirectlyRead':1180,'unresolved':2,'ttsAsrRepeated':0}))
