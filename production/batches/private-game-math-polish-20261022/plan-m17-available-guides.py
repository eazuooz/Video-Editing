"""Two observed Townscaper regions; unverified occlusion timing stays pending."""
from polish_common import *
e=Episode('M17');e.authorized()
def guide(sid,label,keys,pos):
 return {'scene':sid,'label':label,'role':'focus','shape':'ring','labelPosition':pos,
  'keyframes':[[k[0],*[v*4 for v in k[1:]]] for k in keys],
  'meaning':label,'coordinateFrame':'observed-screen-projection',
  'tracking':'Hand-observed 480x270 source states at half-second intervals; open region is editorial attention guidance, not a measured mesh or matrix.',
  'occlusion':'Hide outside the observed span and before the roof is rebuilt. Never infer an occluded point.'}
guides=[
 guide('05','기존 지붕',[[0,185,62,68,24],[.5,185,62,68,24],[1,185,62,68,24],[1.5,185,62,68,24],[2,185,62,68,24],[2.5,185,62,68,24],[3,185,62,68,24],[3.8,185,62,68,24]],[270,390]),
 guide('08','같은 건물의 지붕',[[3,226,84,66,37],[3.5,257,86,89,31],[4,268,79,92,24],[4.5,270,92,95,42],[5,270,92,95,42]],[1570,390]),
]
save(e.H/'observed-guides.json',{'version':1,'episode':e.id,'partial':True,'selectedScenes':['05','08'],'guides':guides,
 'captionClearanceScenes':['05','08','14'],'renderMapping':{'full':[1,0,0],'inset':[5/6,160,0]},
 'sourceEvidence':rel(e.H/'available-guide-targets.json'),'sourceEvidenceSha256':sha(e.H/'available-guide-targets.json'),
 'status':'draft-anchors-await-current-pixel-preflight','fullMasterApproval':False,
 'axisConvention':'No world axes, camera matrices or measured rotation inferred from gameplay.',
 'remaining':['14: the retained13.5–17s pixels show rebuilding from a fixed view; do not place a camera-orbit/hidden-tower guide here. Find a visually corresponding preserved-action window before full assembly.','Portal2 native FHD inputs remain unresolved.']})
print('M17 two available-scene guides prepared; remaining source/cue review pending')
