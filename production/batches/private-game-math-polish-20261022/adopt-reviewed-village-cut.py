"""Adopt only the inspected FHD village cut and manually observed wood guides."""
import datetime,shutil
from polish_common import *
e=Episode('M10');e.authorized();candidate=e.H/'village-cue-review.json';d=read(candidate)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
permission=read(B/'fhd-candidate-catalog.json')['oU__wsOyeiY']
assert sha(R/d['sourceFile'])==d['sourceSha256']
assert sha(R/d['rawClip'])==d['rawClipSha256'] and sha(R/d['preview'])==d['previewSha256']
assert sha(R/permission['permissionMetadata'])==permission['permissionMetadataSha256']
slot=next(s for s in e.T['scenes'] if s['id']=='19')
assert d['frames']==slot['frames']==sum(s['frames'] for s in d['segments'])==3781
e.verify(R/d['rawClip'],3781)
review={'status':'passed-source-cut-inspection','reviewedAt':now,'candidateSha256':sha(candidate),
 'previewSha256':d['previewSha256'],'rawClipSha256':d['rawClipSha256'],
 'directCaptionedStates':63,'directSheets':d['sheets'],
 'directDenseTargetStates':56,'targetReports':[rel(e.H/'new-uncle-guide-targets.json'),rel(e.H/'village-stable-targets.json')],
 'observed':'Native village traversal: rails, posts and cloth stalls viewed from multiple directions; original caption cues and frame count preserved. No world-space dimensions or inferred collision boxes.',
 'cueMapping':[
  {'seconds':[0,8],'evidence':'Wooden floor, rail and hut approach; varying projected extents.'},
  {'seconds':[8,15],'evidence':'Camera moves around cloth stall and its poles; different faces revealed.'},
  {'seconds':[15,33],'evidence':'Bridge and stationary wood posts; fixed-world-axis explanation does not claim that the objects move.'},
  {'seconds':[33,48],'evidence':'Village woodwork from another view; object-rotation sentence explicitly recalls the preceding square experiment, not a rotating village building.'},
  {'seconds':[48,63.016667],'evidence':'Village post/bridge traversal closes the distinction and leads to the original affine diagram.'}],
 'playbackObserved':'Browser source preview start, selected middle at approximately33s, and restart at8s observed. Not continuous full-clip listening.',
 'sourceAudioUsed':False,'fullMasterApproval':False,'humanReview':'pending'}
save(e.H/'village-source-cut-review.json',review)
cut={'status':'approved-source-cut','sourceId':'oU__wsOyeiY','game':permission['game'],
 'sourceFile':d['sourceFile'],'sourceSha256':d['sourceSha256'],'sourceUrl':permission['url'],
 'sourceSpeed':1,'frames':3781,'segments':d['segments'],'sourceAudioUsed':False,
 'permissionMetadata':permission['permissionMetadata'],'permissionMetadataSha256':permission['permissionMetadataSha256'],
 'permissionEvidence':permission['permissionEvidence'],'requiredDescriptionCredit':permission['requiredCredit'],
 'reviewedInternalExcerptChanges':True,'sourceReview':rel(e.H/'village-source-cut-review.json'),
 'sourceReviewSha256':sha(e.H/'village-source-cut-review.json'),'originalSceneOrderAndDurationPreserved':True,
 'difference':'Different independent recording of the same wooden village; new screen-space tracks replace old source landmarks. Existing narration, slot order and frame count retained.'}
mp=e.H/'fhd-replacement-cuts.json';mapping=read(mp) if mp.exists() else {'episode':'M10','scenes':{}}
mapping.update(status='approved-source-cuts',originalTimelineSha256=sha(e.P/'production/timeline.json'),originalNarrationAudioAndTimingPreserved=True)
mapping['scenes']['19']=cut;save(mp,mapping)
save(e.H/'fhd-cut-review.json',{'status':'passed-source-cut-inspection','cutMapSha256':sha(mp),'sceneReviews':{k:v['sourceReview'] for k,v in mapping['scenes'].items()},'fullMasterApproval':False,'humanReview':'pending'})
dst=e.O/'clips/19.mp4';assert not dst.exists() or sha(dst)==d['rawClipSha256']
if not dst.exists():shutil.copy2(R/d['rawClip'],dst)
record=read(e.H/'gameplay-restoration.json')
record['scenes']['19']={'path':rel(dst),'sha256':sha(dst),'frames':3781,'speed':1,
 'sources':[{'sourceSha256':d['sourceSha256'],'source':d['sourceFile'],'sourceIn':s['in'],'frames':s['frames'],'vf':'fps=60; native1920x1080'} for s in d['segments']],
 'originalCutOrderAndDuration':False,'originalSceneOrderAndDuration':True,'internalExcerptChangesReviewed':True,
 'sourceKind':'reviewed-same-game-FHD-replacement','sourceReview':cut['sourceReview'],
 'currentMovingPixelReview':'Limited source playback observations; full annotated master pending','annotationPolish':'pending',
 'sourceAudio':'Original approved narration-only baseline retained; replacement audio unused'}
record['replacementCutMap']={'path':rel(mp),'sha256':sha(mp)};save(e.H/'gameplay-restoration.json',record)
actual={s['id'] for s in e.T['scenes'] if s['classification']=='actual'}
statuses=read(B/'gameplay-restoration-status.json');statuses['M10']={'status':'partial-gameplay-restored','restoredScenes':sorted(record['scenes']),'missingScenes':sorted(actual-record['scenes'].keys()),'annotationPolish':'pending','fullMasterReady':False};save(B/'gameplay-restoration-status.json',statuses)
# Coordinates are hand observed in actual 800x450 source frames, not an engine
# measurement. Stop before the hand/effect occludes the selected wooden area.
keys=[]
def key(t,obj,points):
 xs=[p[0] for p in points];ys=[p[1] for p in points];a,b,c,z=min(xs)-5,min(ys)-5,max(xs)+5,max(ys)+5
 keys.append({'t':t,'object':obj,'red':points,'blue':[[a,b],[c,b],[c,z],[a,z]]})
for n in range(97,109):
 key(n/4,'visible-upper-post-portion',[[682,50],[714,50],[677,242],[642,242]])
for t,points in [
 (45.25,[[359,62],[516,27],[519,40],[359,80]]),
 (45.5,[[328,102],[476,80],[479,94],[328,117]]),
 (45.75,[[328,128],[472,117],[476,132],[328,143]]),
 (46,[[328,148],[472,134],[476,147],[328,163]]),
 (46.25,[[328,151],[472,137],[476,151],[328,167]]),
 (46.5,[[328,151],[472,137],[476,151],[328,167]])]:key(t,'visible-upper-plank',points)
track=e.H/'cue-track-19-village-wood.json'
save(track,{'sourceFile':rel(dst),'sourceSha256':sha(dst),'coordinatePixels':[800,450],
 'keyframes':keys,'maxInterpolationGapSeconds':.26,'manualHideIntervals':[],'closed':True,
 'meaning':'Red observed visible wood portion; blue screen-aligned extent of that selected portion only. Not the whole object, world bounds, collision data or an engine measurement.',
 'coordinateFrame':'screen pixels; no world/local axes inferred','tracking':'Manually inspected quarter-second anchors; only stable unoccluded visible portions retained.',
 'occlusion':'Post ends above hand. Upper plank stops before the grapple effect at46.75s. No interpolation between different objects or cuts.',
 'evidence':[rel(e.H/'new-uncle-guide-targets.json'),rel(e.H/'village-stable-targets.json')]})
save(e.H/'cue-guide-additions.json',{'episode':'M10','scenes':{'19':{'useReviewedLocalClip':True,'landmarkSources':[rel(track)],
 'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'tealAtLine':0,'hideMathNote':True,
 'redLabel':'빨강: 보이는 목재 일부','blueLabel':'파랑: 화면 범위 · 월드 경계 아님'}}})
for name in ['new-uncle-guide-targets.json','village-stable-targets.json']:
 q=e.H/name;r=read(q);r.update(status='direct-target-stills-inspected',reviewedAt=now,fullMasterApproval=False);save(q,r)
print('M10 scene19 adopted; manual guides need current composited preflight',flush=True)
