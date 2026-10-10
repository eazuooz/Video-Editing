"""Bind existing observed anchors to the native frames they actually came from.

Preserve pre-correction drafts; exact single-frame GA01 authoring is untouched.
"""
from pathlib import Path
import json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;archive=B/'baselines/landmark-drafts-before-native-time-fix';archive.mkdir(parents=True,exist_ok=True)
audit=json.loads((ROOT/'shared/output/game-math-part2-teaching-revision/landmark-sample-timestamp-audit.json').read_text())
assert all(r['meanAbsolutePixelError']==0 for r in audit)
half={'gb05','gb06','ga02','ga08','gb07','ga06','ga04','ga09','gb02','ga10','ga05old'}
one={'ga03','gb01','ga07','o02','o05','o08','o11ski','o11wing','o14','o17board','o17bike','o20','o23','gb03','gb03late','gb04'}
record=[]
for stem in sorted(half|one|{'ga05new'}):
 file=B/(stem+'-landmarks.json');old=file.read_bytes();d=json.loads(old)
 if d.get('nativeFrameTimestampCorrection'):continue
 shutil.copy2(file,archive/file.name)
 changes=[]
 for k in d['keyframes']:
  prior=k['t'];step=.5 if stem in half or (stem=='ga05new' and prior<380.5) else 1
  offset=(round(60*step/2)-1)/60
  k['authoringLabelTime']=prior;k['t']=round(prior+offset,9);changes.append({'label':prior,'native':k['t'],'offset':offset})
 # Preserve all pre-existing concealment and add a conservative edge around
 # ambiguous fast rotation/occlusion; never extend coordinates into it.
 d['hideIntervals']=[[max(0,a-.5),b+.5] for a,b in d.get('hideIntervals',[])]
 d['nativeFrameTimestampCorrection']={'rule':'fps-bin last input frame: .233333s for2fps, .483333s for1fps; direct native-frame pixel comparison confirms zero error','evidence':'shared/output/game-math-part2-teaching-revision/landmark-sample-timestamp-audit.json','originalDraftSha256':hashlib.sha256(old).hexdigest(),'exactSingleFrameGA01Preserved':True}
 d['movingPixelApproval']=False;file.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');record.append({'file':file.relative_to(ROOT).as_posix(),'points':len(changes),'changes':changes})
(B/'quaternion-native-timestamp-correction.json').write_text(json.dumps({'correctedTracks':record,'movingPixelApproval':False,'nativeScenePixelsNeedRerender':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# The equipment retake was based on an incorrect low-resolution reading.
# Preserve its generated WAVs, but explicitly reject its use.
(B/'quaternion-v7-rejected-equipment-reading.json').write_text(json.dumps({'project':'game-math-quaternion-teaching-additions-v7','appliedToLecture':False,'reason':'Exact native enlarged175.25 and170.25 frames show two skis and two poles. Original new-script phrase 스키 was correct; board retake is semantically rejected.','actualEquipment':'two skis','originalV4GA05VoiceRetained':True,'gpuHandoffToken':'268bd1a2-d83e-40b1-b233-df751d7a1f11','researchResumedOwner':72544,'actualPostResumeCompletedJobs':703,'noTrainingTerminated':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Corrected {len(record)} observed tracks to their real native frame times. GA01 unchanged. V7 equipment retake rejected and preserved.')
