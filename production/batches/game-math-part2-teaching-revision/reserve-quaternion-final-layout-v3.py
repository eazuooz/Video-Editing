"""Keep prior render generations and reserve the verified QC11 layout master."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
Q=Path(__file__).parent/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows=read(O/'narrated-scene-review/index.json');native=read(O/'native-narrated-scenes-v3.json')
for sid,row in rows.items():
 assert any(x['scene']==sid and x['sha256']==row['sha256'] and x['rate']==1 and x['ended'] for x in native),sid
checked={'schemaVersion':1,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewMethod':'Direct current 3fps moving contact pages for all six action additions; spoken reveal/frame alignment; current native 1x end proof for all14 additions. Direct explanation line/mid/end frames. Original80 layers kept unchanged.','sceneFiles':rows,'nativePlaybackEvidence':(O/'native-narrated-scenes-v3.json').relative_to(ROOT).as_posix(),'nativePlaybackSha256':sha(O/'native-narrated-scenes-v3.json'),'editableTracks':{n:sha(Q/n) for n in ['trail-screen-track.json','gear-v3-screen-track.json','besiege-screen-track.json']},'visualFixes':['Hide Trailmakers guides9.5–10s during camera orbit; resume on confirmed front/wing anchors.','Raise QC11 result group and center the two lines; distinct left/right numeric results and fixed captions remain clear.'],'gameplayAnnotationsPassed':True,'addedSceneMovingPixelsPassed':True,'fullMasterReviewComplete':False,'humanListeningComplete':False,'rightsHumanReviewComplete':False,'gameWorldValuesMeasured':False}
write(Q/'current-narrated-additions-review.json',checked)
p=ROOT/'projects/game-math-quaternion-calculations-v3/project.json';m=read(p)
clean='shared/output/motion-canvas/game-math-quaternion-calculations-v3-refined-v3.mp4'
captioned='shared/output/motion-canvas/game-math-quaternion-calculations-v3-subtitled-refined-v3.mp4'
if m['paths']['videoClean']!=clean:
 old={k:{'path':m['paths'][k],'sha256':sha(ROOT/m['paths'][k])} for k in ['videoClean','videoBurnedCaptions']}
 m['finalRender']['previousCaptionClearanceMaster']=old
 m['paths']['videoClean']=clean;m['paths']['videoBurnedCaptions']=captioned
 m['finalRender']['currentLayoutCorrection']={'scene':'QC11','reason':'Center the noncommutative product line to separate it from the two coordinate results after raising the group.','sceneReview':(Q/'current-narrated-additions-review.json').relative_to(ROOT).as_posix(),'sceneSha256':rows['QC11']['sha256'],'fullMasterReviewComplete':False}
 write(p,m)
print('All14 current addition files have normal-speed native proof; reserved calculations final layout master without replacing prior generations.')
