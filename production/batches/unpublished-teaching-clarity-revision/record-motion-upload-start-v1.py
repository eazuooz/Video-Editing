from pathlib import Path
from datetime import datetime,timezone
import json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
pub=read(R/'publishing/youtube-upload-v1.json')
assert pub['actualVideoId']=='mBDd9VzSTkA' and pub['fileSelectedOnce'] and not pub['privateSaveVerified']
assert read(R/'collection-private-preflight-v2.json')['sourceAndOutputAllFourHashesEqual']
now=datetime.now(timezone.utc).isoformat();stage='current-v2-reviewed-collected; single-mBDd9VzSTkA-upload-and-settings-in-progress'
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage=stage,ownedJob=None,actualNewVideoId=pub['actualVideoId'],outputsCollected=True,uploaded=False,privateSettingsVerified=False,gitDelivered=False,scheduled=False,
 finalMediaAdoption=(R/'final-media-adoption-v2.json').relative_to(ROOT).as_posix(),collectionEvidence=(R/'collection-private-preflight-v2.json').relative_to(ROOT).as_posix(),privateUploadReceipt=(R/'publishing/youtube-upload-v1.json').relative_to(ROOT).as_posix(),next='Continue existing upload tab54; no new file selection. Complete private settings/checks/CC-off pixels and selective Git before replacing baseline Oct12 reservation.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_text('utf-8-sig');q=json.loads(before)
q['updatedAt']=now;q['execution'].update(stage=stage,next=cp['next'],actualNewVideoId=pub['actualVideoId'],actualReplacementVideoId=pub['actualVideoId'],ownedJob=None,finalMediaAdoption=cp['finalMediaAdoption'],collectionEvidence=cp['collectionEvidence'],privateUploadReceipt=cp['privateUploadReceipt'])
item=next(v for v in q['items'] if v['slug']=='motion-sickness-games');item.update(status=stage,actualReplacementVideoId=pub['actualVideoId'],collectionEvidence=cp['collectionEvidence'],privateUploadReceipt=cp['privateUploadReceipt'])
item['review'].update(fullScriptAndClaimsRead=True,openingOverviewPassed=True,causalFlowPassed=True,referenceFlowCompared=True,firstTimeGameplayCompared=True,onFootageAnnotationMotionPassed=True,currentMixedAudioPassed=True,allFinalPixelsPassed=True,technicalQaPassed=True,outputsCollected=True)
item['reviewScopeNote']='Current14 whole plus66 independent complete mixed ASR texts directly compared; all1180 current decoded samples either directly read or byte-identical to prior direct observations, with all60 changed samples directly reviewed. Normal1x whole reached end; selected moving targets/transition directly observed. Human full hearing/pronunciation/public rights remain pending. Actual private/settings/Git/schedule are pending.'
assert qp.read_text('utf-8-sig')==before;save(qp,q)
print(json.dumps(dict(actualNewVideoId=pub['actualVideoId'],localQaAndFourFiles=True,privateSettingsPending=True,baselineScheduleChanged=False)))
