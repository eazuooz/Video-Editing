"""Current-screen glyph region and grapple endpoint; no inferred game values."""
import math
from polish_common import *
e=Episode('M11');e.authorized();src=e.O/'clips/08.mp4';e.verify(src,3240)
evidence=e.H/'uncle-guide-source.json';observations=read(evidence)
assert observations['sourceSha256']==sha(src)
def oval(x,y,rx,ry):
 return [[1.25*(x+rx*math.cos(a)),1.25*(y+ry*math.sin(a))] for a in [math.radians(25+310*i/32) for i in range(33)]]
def make(name,keys):
 p=e.H/'cue-tracks'/('08-'+name+'.json')
 save(p,{'sourceFile':rel(src),'sourceSha256':sha(src),'coordinatePixels':[800,450],
  'keyframes':keys,'maxInterpolationGapSeconds':.26,'manualHideIntervals':[],'closed':False,
  'seedDefinition':{'id':name},'sourceEvidence':rel(evidence),'sourceEvidenceSha256':sha(evidence),
  'coordinateFrame':'screen-space editorial region around the visible glyph/endpoint; not a mesh triangle, world coordinate or actual barycentric value',
  'tracking':'Manually observed quarter-second keyframes; hide outside observed intervals, at the source cut and when the glyph leaves the frame.',
  'movingPixelApproval':False})
 return rel(p)
keys=[]
for t,x,y,rx,ry in [(13.25,330,95,30,44),(13.5,324,106,29,43),(13.75,309,115,29,40),(14,301,117,29,40),(14.25,301,116,29,40),(14.5,299,124,29,40),(14.75,301,125,29,40)]:
 keys.append({'t':t,'object':'glyph-observation','red':oval(x,y,rx,ry)})
p1=make('glyph-observation',keys);keys=[]
for t,x,y,rx,ry,bx,by in [(38,255,82,34,44,350,73),(38.25,255,90,34,44,322,67),(38.5,270,123,28,44,297,76),(38.75,294,125,30,40,284,89),(39,336,106,40,40,305,105),(39.25,354,74,45,43,314,110)]:
 keys.append({'t':t,'object':'glyph-and-endpoint','red':oval(x,y,rx,ry),'blue':oval(bx,by,12,12)})
p2=make('glyph-and-endpoint',keys)
p=e.H/'cue-guide-additions.json';d=read(p)
d['scenes']['08']={'landmarkSources':[p1,p2],'useReviewedLocalClip':True,
 'redLabel':'빨강: 표식 · 메시 아님','blueLabel':'파랑: 보이는 연결점','hideMathNote':True,
 'mathNote':'표식 관찰 ≠ 실제 메시 좌표','mathNotePosition':[390,155],
 'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'redKeyword':'표식','blueKeyword':'표식','mathNoteAtLine':0}
d['status']='additional-source-guide-await-composited-review';save(p,d)
print('M11 08 new source guide prepared; composited review required',flush=True)
