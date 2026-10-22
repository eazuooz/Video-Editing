"""Append directly observed Portal screen guides; preserve reviewed Townscaper."""
from polish_common import *
e=Episode('M17');e.authorized();path=e.H/'observed-guides.json';p=read(path)
src=R/'shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4'
for sid in ['02','11']:assert approved_original_resolution(e,sid,src)
evidence=e.H/'portal-anchor-source.json';assert read(evidence)['sourceSha256']==sha(src)
def guide(sid,label,role,pos,keys):
 return {'scene':sid,'label':label,'role':role,'shape':'ring',
  'labelPosition':[v*4 for v in pos],
  'keyframes':[[k[0],*[v*4 for v in k[1:]]] for k in keys],
  'meaning':label,'coordinateFrame':'observed-screen-projection',
  'tracking':'Manually observed exact quarter-second480x270 frames; open attention rings, not segmentation, world coordinates or engine measurements.',
  'occlusion':'Hide at the last directly observed clear frame; no offscreen extrapolation.',
  'sourceEvidence':rel(evidence),'sourceEvidenceSha256':sha(evidence)}
p['guides']=[g for g in p['guides'] if g['scene'] not in ['02','11']]+[
 guide('02','고정된 기둥','focus',[330,215],[
  [2.25,95,145,78,86],[2.5,142,153,65,73],[2.75,145,155,65,74],
  [3,145,155,65,74],[3.25,146,156,65,74],[3.5,214,156,56,65],
  [3.75,289,142,61,70],[4,336,137,71,75]]),
 guide('02','시점이 바뀐 같은 기둥','focus',[150,210],[
  [10,266,95,42,49],[10.25,286,97,44,50],[10.5,322,92,51,51],
  [10.75,345,91,56,53],[11,353,94,56,53],[11.25,353,94,56,53]]),
 guide('11','큐브 앞면','board',[390,120],[
  [5,240,195,51,47],[5.25,240,214,51,45],[5.5,240,225,51,44]]),
 guide('11','큐브 앞면','board',[390,120],[
  [13,240,213,52,46],[13.25,240,213,52,46],[13.5,240,213,52,46],
  [13.75,240,213,52,46],[14,240,213,52,46],[14.25,240,213,52,46]]),
 guide('11','켜진 표시','focus',[200,38],[
  [41.5,195,92,46,11],[41.75,195,92,46,11],[42,175,85,47,11],
  [42.25,166,86,49,11],[42.5,161,101,53,11]])]
p['selectedScenes']=sorted(set(p['selectedScenes']+['02','11']))
p['captionClearanceScenes']=sorted(set(p['captionClearanceScenes']+['02','11']))
p['remaining']=[];p['partial']=False;p['status']='await-current-portal-guide-preflight'
p['originalResolutionException']={'evidence':rel(B/'portal-original-resolution-exception.json'),'scenes':['02','11'],'sourceSha256':sha(src),'decodedResolution':[video(src)['width'],video(src)['height']]}
p['sourceObservation']={'coarse':rel(e.H/'portal-source-observation.json'),'coarseFrames':84,'exact':rel(evidence),'exactFrames':43,
 'finding':'Viewpoint changes with stationary pillars; front face changes screen position; activated path indicators are directly visible. Rings mark observed regions only.'}
save(path,p);print('M17 Portal guides appended; composite inspection pending')
