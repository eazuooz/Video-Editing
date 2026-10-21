"""Source-keyed game guides and secondary axis legends; no media rendering.

--plan-only validates guide provenance, source visibility keys and safe layout.
--build consumes edit-plan.json and writes76 paragraph-relative ASS files.
The root owns headers, definition cards/chips, underlying models and boards.
"""
from pathlib import Path
import argparse,bisect,importlib.util,json,math
from PIL import ImageFont
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v8_annotations_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
O=c.O/'annotations'
RECT=(40,250,1000,562)
PALETTE=dict(focus='#66c49a',axisX='#ef5a63',axisY='#6cce8e',axisZ='#66b9ed',reference='#b8b8b8',body='#f5f5f5',heading='#e8cf83')
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legend,Malgun Gothic,28,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Focus,Malgun Gothic,48,&H0083CFE8,&H0083CFE8,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Stroke,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def evidence(p):return dict(file=c.rel(p),sha256=c.sha(p))
def stamp(frame):
 # Floor exact60fps bounds to centiseconds: F is active at F/60, while
 # F-1 is not. Prevent the previous kind-label boundary rounding lag.
 cs=int(frame)*100//60;hours,cs=divmod(cs,360000);minutes,cs=divmod(cs,6000);sec,cs=divmod(cs,100)
 return f'{hours}:{minutes:02}:{sec:02}.{cs:02}'
def color(value):
 value=value.lstrip('#');return '&H'+value[4:6]+value[2:4]+value[:2]+'&'
def escape(text):return text.replace('\\','\\\\').replace('{','(').replace('}',')').replace('\n',r'\N')
def event(a,b,style,text,layer):
 assert 0<=a<b
 return f'Dialogue: {layer},{stamp(a)},{stamp(b)},{style},,0,0,0,,{text}\n'
def legend(scene):
 # A reference to axis *marks*, not a recoloring of scene parts or statuses.
 text='축: X Y Z 물체 기준 · 회색 바깥 기준'
 markup=r'{\an7\pos(1080,136)}축: '
 for axis in 'XYZ':markup+=r'{\1c'+color(PALETTE['axis'+axis])+r'}'+axis+' '
 markup+=r'{\1c'+color(PALETTE['body'])+r'}물체 기준 · {\1c'+color(PALETTE['reference'])+r'}회색 바깥 기준'
 if scene in ('m04','m08','m13'):
  text+=' · 행=입력축'
  markup+=r'{\1c'+color(PALETTE['body'])+r'} · 행=입력축'
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',28)
 assert font.getlength(text)<=800,(scene,'Legend must remain within right header',text,font.getlength(text))
 return text,markup
def validated_inputs():
 c.authorized();data=c.read(H/'game-cut-plan.json');keys=data['annotations']['keys'];script=c.read(c.S/'narration.ko.json')
 assert data['scriptSha256']==c.sha(c.S/'narration.ko.json')
 assert len(script['scenes'])==13 and sum(len(s['paragraphs']) for s in script['scenes'])==76
 assert [k['sourceFrame'] for k in keys]==sorted(set(k['sourceFrame'] for k in keys))
 assert keys[0]['sourceFrame']==59925 and keys[-1]['sourceFrame']==60390
 for key in keys:
  if not key['visible']:assert not key['guides'];continue
  assert key.get('evidence') and (c.R/key['evidence']['file']).is_file()
  assert c.sha(c.R/key['evidence']['file'])==key['evidence']['sha256'],'Changed source anchor evidence needs renewed inspection'
  for g in key['guides']:assert len(g['point'])==2 and all(0<=v<=1 for v in g['point'])
 for s in script['scenes']:legend(s['id'])
 return data,keys,script
def at(keys,frame):
 positions=[k['sourceFrame'] for k in keys];n=bisect.bisect_left(positions,frame)
 if n<len(keys) and positions[n]==frame:return keys[n]['guides'] if keys[n]['visible'] else []
 if n==0 or n==len(keys):return []
 a,b=keys[n-1],keys[n]
 if not a['visible'] or not b['visible'] or b['sourceFrame']-a['sourceFrame']>246:return []
 if [(g['label'],g['colorRole']) for g in a['guides']]!=[(g['label'],g['colorRole']) for g in b['guides']]:return []
 frac=(frame-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame'])
 return [dict(x,point=[u+(v-u)*frac for u,v in zip(x['point'],y['point'])]) for x,y in zip(a['guides'],b['guides'])]
def line_path(points):return 'm '+' l '.join(f'{x:.3f} {y:.3f}' for x,y in points)
def strokes(points,width=6):
 result=[]
 for a,b in zip(points,points[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  if length<.001:continue
  nx,ny=-dy/length*width/2,dx/length*width/2
  q=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
  result.append(line_path(q+[q[0]]))
 return result
def bracket(point):
 x=RECT[0]+point[0]*RECT[2];y=RECT[1]+point[1]*RECT[3]
 if not RECT[0]+20<x<RECT[0]+RECT[2]-20 or not RECT[1]+20<y<RECT[1]+RECT[3]-20:return []
 r=18;wing=10
 corners=[[(x-r,y-r+wing),(x-r,y-r),(x-r+wing,y-r)],[(x+r-wing,y-r),(x+r,y-r),(x+r,y-r+wing)],
  [(x+r,y+r-wing),(x+r,y+r),(x+r-wing,y+r)],[(x-r+wing,y+r),(x-r,y+r),(x-r,y+r-wing)]]
 return [path for corner in corners for path in strokes(corner)]
def windows(segment,keys):
 n=segment['endFrameExclusive']-segment['startFrame']
 if segment['kind']=='still':return [(0,n)]
 first=segment['sourceStartFrame'];bounds={0,n,*range(0,n,6)}
 bounds.update(k['sourceFrame']-first for k in keys if first<k['sourceFrame']<first+n)
 bounds=sorted(bounds);return list(zip(bounds,bounds[1:]))
def move(start,count,p0,p1):
 if count<=1:return r'\pos(0,0)'
 dx=(p1[0]-p0[0])*RECT[2];dy=(p1[1]-p0[1])*RECT[3]
 t0=round((start/60-(start*100//60)/100)*1000);t1=t0+round((count-1)*1000/60)
 return f'\\move(0,0,{dx:.4f},{dy:.4f},{t0},{t1})'
def label(segment):
 if segment['kind']=='video':
  return '물체 이동 · 아직 누운 돛' if segment['sourceStartFrame']<60195 else '회전 조작 · 돛 세우기'
 source=segment['sourceFrameForGuide']
 return '선택할 물체 · 누운 돛' if source==59925 else ('옮긴 뒤 · 아직 누운 돛' if source==60195 else '세운 돛 · 놓인 자세')
def paragraph(p,keys):
 duration=p['frames'];text=HEADER;windows_report=[];events=0;hidden=0
 if p['layout']=='model-math':
  assert isinstance(p.get('axisLegend',False),bool),'axisLegend must describe whether this Unity shot actually shows axis guides'
  plain=None
  if p.get('axisLegend',False):
   plain,markup=legend(p['sceneId']);text+=event(0,duration,'Legend',markup,2)
  return text,dict(legend=plain,gameGuideEvents=0,hiddenGuideWindows=0,sourceWindows=[])
 assert p['layout']=='game-model' and p['id']=='m01.L02','New gameplay requires its own inspected target keys'
 focusfont=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
 for row in p['left']:
  a=row['startFrame']-p['startFrame'];b=row['endFrameExclusive']-p['startFrame'];focus=label(row)
  assert focusfont.getlength(focus)<=1000
  text+=event(a,b,'Focus',r'{\an5\pos(540,850)}'+escape(focus),4)
  moving=row['kind']=='video';source=row['sourceStartFrame'] if moving else row['sourceFrameForGuide']
  report=dict(globalStartFrame=row['startFrame'],globalEndFrameExclusive=row['endFrameExclusive'],sourceFirstFrame=source,
      sourceLastFrame=source+(b-a-1 if moving else 0),classification=row['classification'],guideSpace='source-screen editorial guide',
      sourceCutClear=True,liveNativeSpeed=1 if moving else None,pointIsNot3DCenter=True,label=focus)
  windows_report.append(report)
  for start,end in windows(row,keys):
   f0=source+(start if moving else 0);f1=source+(end-1 if moving else 0)
   ga,gb=at(keys,f0),at(keys,f1)
   if not ga or [(g['label'],g['colorRole']) for g in ga]!=[(g['label'],g['colorRole']) for g in gb]:hidden+=1;continue
   for x,y in zip(ga,gb):
    motion=move(a+start,end-start,x['point'],y['point']) if moving else r'\pos(0,0)'
    for path in bracket(x['point']):
     tags=r'{\an7'+motion+r'\p1\bord0\shad0\1a&H00&\1c'+color(PALETTE['focus'])+r'\clip(40,250,1040,812)}'
     text+=event(a+start,a+end,'Stroke',tags+path+r'{\p0}',3);events+=1
 return text,dict(legend=None,gameGuideEvents=events,hiddenGuideWindows=hidden,sourceWindows=windows_report)
def plan_only(data,keys,script):
 ids=[s['id']+f'.L{i:02}' for s in script['scenes'] for i in range(1,len(s['paragraphs'])+1)]
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',status='guide-and-legend-design-ready-awaiting-edit-plan',
  inputs=dict(gameCutPlan=evidence(H/'game-cut-plan.json'),implementation=evidence(Path(__file__))),paragraphCount=len(ids),
  paragraphASS={},intendedFiles={pid:c.rel(O/'paragraphs'/(pid.replace('.','-')+'.ass')) for pid in ids},
  gameGuideParagraphs=['m01.L02'],sourceSpace=RECT,sourceKeyCount=len(keys),palette=PALETTE,
  leftHeaderModified=False,canonicalDefinitionCards='owned by root compositor; not drawn here',
  axisLegendPolicy='Only model-math paragraphs with explicit axisLegend=true; absent defaults false. Root derives this flag from the actual Unity shot axes setting.',
  legendSafeRegion=[1080,136,800,36],gameFocusSafeRegion=[40,824,1000,52],fixedCaptionsProtected=True,
  sourceCopyOrSourceCreatorText=False,actualGameAxesClaimed=False,
  guideInterpolation='Linear source-screen manual anchors only; no extrapolation or bridging a hidden endpoint. Continuous libass move within≤6frame event windows.',
  current1080And375MovingReview='pending actual output',outputsCreated=False)
 c.save(O/'plan-validation.json',result)
 if not (H/'annotations-manifest.json').exists():c.save(H/'annotations-manifest.json',result)
 print(json.dumps(dict(status=result['status'],paragraphs=76,keys=len(keys),mediaCreated=False),ensure_ascii=False))
def build(data,keys,script):
 assert (H/'edit-plan.json').exists(),'Run --plan-only until root edit-plan.json is ready'
 edit=c.read(H/'edit-plan.json');assert len(edit['paragraphs'])==76
 expected={s['id']+f'.L{i:02}' for s in script['scenes'] for i in range(1,len(s['paragraphs'])+1)}
 assert {p['id'] for p in edit['paragraphs']}==expected
 rows={}
 for p in edit['paragraphs']:
  assert p['frames']==p['endFrame']-p['startFrame']>0
  text,details=paragraph(p,keys);path=O/'paragraphs'/(p['id'].replace('.','-')+'.ass');path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(text,encoding='utf-8-sig')
  rows[p['id']]=dict(evidence(path),startFrame=p['startFrame'],endFrame=p['endFrame'],frames=p['frames'],timeBase='paragraph-relative60fps, centisecondfloor',**details)
 result=dict(schemaVersion=1,revision='orientation-matrix-v8',status='source-keyed-guides-and-legends-built;current-moving-review-pending',
  inputs=dict(editPlan=evidence(H/'edit-plan.json'),gameCutPlan=evidence(H/'game-cut-plan.json'),implementation=evidence(Path(__file__))),
  paragraphCount=76,paragraphASS=rows,gameGuideParagraphs=[pid for pid,x in rows.items() if x['sourceWindows']],
  sourceGameRect=RECT,sourceRaster=[1920,1080],palette=PALETTE,
  guideInterpolation='Existing linear source-screen points, libass move sampled at60fps in≤6frame windows, split at every manual/hide key and source cut; no new path reconstruction.',
  hides='Hide if either bracketing source anchor is hidden, unlinked, beyond246frames, or target differs. Cloth out of frame is never replaced by a pointer to the cyan tether.',
  sourceCopyOrSourceCreatorText=False,actualGameAxesClaimed=False,leftHeaderModified=False,
  canonicalDefinitionCards='Root compositor owns header/card/chip. No duplicate definition card is overlaid.',
  axisLegendPolicy='Only model-math paragraphs with explicit axisLegend=true; absent defaults false. Root derives this flag from the actual Unity shot axes setting.',
  fixedCaptionCenter=[960,970],gameFocusCenter=[540,850],legendSafeRegion=[1080,136,800,36],
  nativePixelReview='pending actual paired encoded output',mobileMovingReview='pending actual375px output',
  sourceAudioChanged=False,narrationChanged=False,sourceTimingChanged=False)
 c.save(H/'annotations-manifest.json',result);c.save(O/'build-review.json',result)
 print(json.dumps(dict(paragraphs=76,gameGuideParagraphs=result['gameGuideParagraphs'],gameGuideEvents=sum(x['gameGuideEvents'] for x in rows.values()),manifest=c.rel(H/'annotations-manifest.json')),ensure_ascii=False))
def main():
 ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--plan-only',action='store_true');g.add_argument('--build',action='store_true');a=ap.parse_args()
 data,keys,script=validated_inputs()
 if a.plan_only:plan_only(data,keys,script)
 else:build(data,keys,script)
if __name__=='__main__':main()
