"""Additional current-source regions at unchanged narration cues."""
import math
from polish_common import *

def track(e,sid,name,keys,meaning):
 src=e.O/f'clips/{sid}.mp4'
 def ellipse(x,y,rx,ry):
  return [[(x+rx*math.cos(a))*1.25,(y+ry*math.sin(a))*1.25] for a in [math.radians(25+310*i/32) for i in range(33)]]
 p=e.H/'cue-tracks'/f'{sid}-{name}.json'
 save(p,{'sourceFile':rel(src),'sourceSha256':sha(src),'coordinatePixels':[800,450],
  'keyframes':[{'t':t,'object':name,'red':ellipse(x,y,rx,ry)} for t,x,y,rx,ry in keys],
  'maxInterpolationGapSeconds':.51,'manualHideIntervals':[],'closed':False,'allowInsetLowerSurface':True,
  'seedDefinition':{'id':name,'meaning':meaning},
  'sourceEvidence':rel(B/'remaining-guide-cues.json'),'sourceEvidenceSha256':sha(B/'remaining-guide-cues.json'),
  'coordinateFrame':'editorial screen region; no measured plane, world coordinates or inferred engine data',
  'tracking':'Manual current-source half-second observations; hide outside observed interval. An open regional guide is not a traced mesh boundary.',
  'movingPixelApproval':False})
 return rel(p)

e=Episode('M11');e.authorized()
paths=[track(e,'02','sand-reference',[[4,245,261,100,35],[4.5,252,270,90,32],[5,265,290,75,30]],'Selected visible sandy ground, not a measured fixed point'),
 track(e,'02','bridge-top',[[5.5,157,273,120,25],[6,177,296,115,23],[6.5,128,270,105,25],[7,79,276,67,23]],'Visible wooden top surface; hide before it leaves the frame'),
 track(e,'02','ground-recap',[[37.5,311,298,79,32],[38,311,298,79,32],[38.5,319,316,64,20],[39,313,310,65,26],[39.5,316,315,61,24],[40,318,310,58,26]],'Visible ground below the combat; clear of weapons and effects')]
save(e.H/'cue-guide-additions.json',{'scenes':{'02':{'landmarkSources':paths,'redLabel':'빨강: 관찰할 바닥·윗면 영역','mathNote':'표면까지의 거리 ≠ 발판 안쪽 여부'}},'status':'await-current-composited-review','replacesSuppressedOriginalTracks':True})
e=Episode('M12');e.authorized()
paths=[track(e,'21','roof-and-wall',[[2.5,196,104,39,44],[3,218,94,39,46],[3.5,194,111,40,46],[4,194,106,39,43]],'The same left watchtower roof and wall; avoid the earlier bright projectile occlusion'),
 track(e,'21','same-roof',[[39.5,242,96,31,32],[40,226,119,33,33],[40.5,229,102,34,33],[41,206,88,36,35],[41.5,209,101,37,36]],'Left watchtower roof and upper wall under observed camera movement; hide before damage overlay')]
save(e.H/'cue-guide-additions.json',{'scenes':{'21':{'landmarkSources':paths,'redLabel':'빨강: 같은 망루의 지붕·벽','mathNote':'표면 위치 → 그 위치의 속성'}},'status':'await-current-composited-review','replacesSuppressedOriginalTracks':True})
print('M11 floor and M12 tower cue tracks prepared, not approved')
