"""Reuse original lines/planes tracks on restored, explicitly authorized slots.

Original PCM and ASR caches are unavailable. Narration gates therefore use the
saved sentence cues and original pause map, never a newly generated voice.
Source byte hashes may change on restoration; every replacement is recorded and
must pass direct composited source/track inspection before full production.
"""
import copy,datetime,importlib.util,re,sys
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M09','M10','M11','M12'];e.authorized()
oldbase=R/'production/batches/game-math-part2-teaching-revision'
kind='lines' if e.id in ['M09','M10'] else 'planes'
original=oldbase/f'create-{kind}-overlay.py';registry=read(oldbase/f'{kind}-annotation-tracks.json')
additions=e.H/'cue-guide-additions.json'
if additions.exists():
 for sid,changes in read(additions)['scenes'].items():registry['scenes'][sid].update(changes)
if e.id=='M09':
 # Current restored Portal pixels: the old top-right summary covers the
 # receiver/exit indicators. Narration and the short beam label already
 # explain the relation; keep that actual result visible.
 registry['scenes']['LG01']['hideMathNote']=True
if e.id=='M10':
 registry['scenes']['LG04'].update(redLabel='빨강: 머리 윤곽',tealLabel='청록: 둥근 비교 · 판정 구 아님',mathNote='중심·반지름은 다음 그림에서 정의')
 registry['scenes']['LG05']['hideMathNote']=True
if e.id=='M12':
 # The original triangle is an editorial comparison over the terrain, not a
 # traced terrain boundary or an observed engine mesh.
 registry['scenes']['17'].update(redLabel='빨강: 설명용 삼각형 · 메시 아님')
if e.id=='M11':
 registry['scenes']['PG01'].update(redLabel='빨강: 보이는 바닥·벽 경계선',blueLabel='파랑: 경계의 관찰 기준점')
for sid in {'M11':['PG01','PG02','PG03'],'M12':['PG04','PG06','PG07']}.get(e.id,[]):
 # Redundant upper cards obscure gel emitters, panels or the path result.
 # Retain the narrated lesson, meaningful short labels and actual guides.
 registry['scenes'][sid]['hideMathNote']=True
out=e.O/'available-game-overlays';out.mkdir(exist_ok=True)
insets={'M09':[],'M10':['10','LG04','13','16','LG06','LG07','21'],'M11':['02','05'],'M12':['11','17','19','21']}[e.id]
exception_path=B/'portal-original-resolution-exception.json'
if exception_path.exists():
 for sid in read(exception_path).get('episodes',{}).get(e.id,{}).get('scenes',{}):
  slot=next(s for s in e.T['scenes'] if s['id']==sid)
  for segment in slot['cut']['segments']:
   source=R/segment.get('sourceFile',slot['cut']['sourceFile'])
   assert approved_original_resolution(e,sid,source)
  assert (e.O/f'clips/{sid}.mp4').exists(),f'{sid}: restore the approved cut first'
  if sid not in insets:insets.append(sid)
if additions.exists():
 for sid,changes in read(additions)['scenes'].items():
  if changes.get('useReviewedLocalClip') and sid not in insets:insets.append(sid)
if sys.argv[2:]:
 assert set(sys.argv[2:])<=set(insets)
 insets=[sid for sid in insets if sid in sys.argv[2:]]
selection=set(insets)
timeline=copy.deepcopy(e.T);track_records=[];mapped={};baseline={}
for slot in timeline['scenes']:
 if slot['classification']!='actual' or slot['id'] not in selection:continue
 if registry['scenes'][slot['id']].get('useReviewedLocalClip'):
  slot['preservedOriginal']=True;slot['baselineClip']=rel(e.O/f'clips/{slot["id"]}.mp4')
 if slot.get('preservedOriginal'):
  baseline[slot['baselineClip']]=rel(e.O/f'clips/{slot["id"]}.mp4');slot['baselineClip']=baseline[slot['baselineClip']]
 for name in registry['scenes'][slot['id']]['landmarkSources']:
  track=read(R/name);current=copy.deepcopy(track);current['sourceFile']=baseline.get(track['sourceFile'],track['sourceFile'])
  if e.id=='M10' and slot['id']=='LG04':
   # Direct current-frame review found a stale head track following a flame.
   # Replace the observed approach, hide the ambiguous shot/edge intervals.
   current['keyframes']=[k for k in current['keyframes'] if not 640<=k['t']<=643.3 and not 649<=k['t']<=650]
  if e.id=='M10' and slot['id']=='LG06' and Path(name).stem=='LG06-blue':
   # Current source reveals that later blue components select the weapon or
   # unrelated distant pixels. Retain only the directly observed blue torso.
   current['keyframes']=[k for k in current['keyframes'] if 731<=k['t']<=732.14]
  if e.id=='M10' and slot['id']=='LG05':
   # Source82.5s is the last clear cube face; later legacy extents also
   # include the portal below it. End the guide before that ambiguity.
   current['keyframes']=[k for k in current['keyframes'] if k['t']<=82.5]
  current['sourceSha256']=sha(R/current['sourceFile']);mapped[(R/name).resolve()]=current
  track_records.append({'scene':slot['id'],'track':name,'trackSha256':sha(R/name),'originalSource':track['sourceFile'],'originalSourceSha256':track['sourceSha256'],'restoredSource':current['sourceFile'],'restoredSourceSha256':current['sourceSha256'],'sameBytes':track['sourceSha256']==current['sourceSha256'],'reason':'Original cuts/frame count/framing restored; observed track retained. Changed source hashes require current pixel equivalence review.'})
  local_track=e.H/'available-tracks'/Path(name).name
  save(local_track,current)
  track_records[-1].update(effectiveTrack=rel(local_track),effectiveTrackSha256=sha(local_track),originalPointsUnchanged=current['keyframes']==track['keyframes'])
if e.id=='M10' and 'LG04' in selection:
 import math
 source_file='shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4'
 observed=[[8,127,103,9,8],[8.1,110,103,9,8],[8.2,104,106,9,8],[8.3,95,105,10,9],
  [8.4,84,104,11,9],[8.5,115,111,11,10],[8.6,128,115,12,11],[8.7,120,115,13,11],
  [8.8,110,119,14,12],[8.9,96,119,16,14],[9,77,120,19,16],[9.1,51,125,23,20]]
 keys=[]
 for t,x,y,rx,ry in observed:
  ellipse=lambda ax,ay:[[2*(x+ax*math.cos(i*math.pi/16)),2*(y+ay*math.sin(i*math.pi/16))] for i in range(32)]
  keys.append({'t':632+t,'object':'LG04-manually-observed-approaching-head','red':ellipse(rx,ry),'teal':ellipse(max(rx,ry)+5,max(rx,ry)+5)})
 local=e.H/'lg04-observed-head-repair.json'
 save(local,{'sourceFile':source_file,'sourceSha256':sha(R/source_file),'coordinatePixels':[800,450],
  'keyframes':keys,'maxInterpolationGapSeconds':.11,'manualHideIntervals':[],'closed':True,
  'meaning':'Editorial head contour and round comparison; not engine collision data.',
  'observedSourceFrames':'production/local/private-polish-v1/lg04-tracking-repair/exact-8.0.png through exact-9.1.png',
  'reason':'Replaces drift to torch at10.5–11.2; ends before head leaves the frame. Labels moved away from the observed head.',
  'currentMovingReview':'pending'})
 registry['scenes']['LG04']['landmarkSources'].append(rel(local))
save(e.H/'available-annotation-registry.json',registry)
source=original.read_text(encoding='utf8')
start=source.index(' def spoken(keyword,fallback):');end=source.index(' red_at=spoken',start)
source=source[:start]+''' def spoken(keyword,fallback):
  for cue in slot.get('sentenceCues',[]):
   if keyword not in cue['text']:continue
   raw_at=cue['start'];at=raw_at+sum(p['seconds'] for p in slot.get('observationPauses',[]) if p['rawAt']<=raw_at)
   if at>=max(reveal,fallback)-.1:return at
  return fallback
'''+source[end:]
source=source.replace("events=[];sx,sy=2.4,2.4","events=[];sx=sy=2.0 if ident in INSETS else 2.4;ox=160 if ident in INSETS else 0")
source=source.replace('points=np.asarray(points)*[sx,sy]','points=np.asarray(points)*[sx,sy]+[ox,0]')
source=source.replace('x,y=np.array(p)*[sx,sy]','x,y=np.array(p)*[sx,sy]+[ox,0]')
source=source.replace('width=2.6','width=3.3')
source=source.replace('note_clear.append(clear)',"note_clear.append(clear and not spec.get('hideMathNote',False))")
source=source.replace('pts[key][:,1]>360',"pts[key][:,1]>(444 if ident in INSETS and track.get('allowInsetLowerSurface') else 360)")
source=source.replace(',15,True)',',22,True)')
source=source.replace("좌표',size=12)","좌표',size=18)")
source=source.replace("spec['mathNote'],'#ffe082',size=14)","spec['mathNote'],'#ffe082',size=20)")
source=source.replace("out=ROOT/'shared/output'/slug/'overlays'","out=LOCAL_OUT")
source=source.replace('[25,101]','[60,48]').replace('[25,124]','[60,75]').replace('[25,147]','[60,75 if not visible["blue"] else 102]')
source=source.replace("if last is not None and (source!=last[0] or abs(seg['in']-last[1])>.1):text", "if False:text")
source=source.replace('ny+58<330','ny+110<330').replace('ny+74','ny+126').replace('ny+58','ny+110')
source=source.replace("spec['mathNote'],'#ffe082',size=20)","wrap_note(spec['mathNote']),'#ffe082',size=22)")
source=source.replace("[nx+8,ny+26]","[nx+8,ny+30]")
from PIL import ImageFont
note_font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44)
def wrap_note(words):
 rows=[];line=''
 for word in words.split(' '):
  candidate=(line+' '+word).strip()
  if line and note_font.getlength(candidate)>750:rows.append(line);line=word
  else:line=candidate
 if line:rows.append(line)
 assert len(rows)<=2,words
 return '\n'.join(rows)
spec=importlib.util.spec_from_loader('restored_available_'+e.id,loader=None);module=importlib.util.module_from_spec(spec)
module.__file__=str(original);exec(compile(source,str(original),'exec'),module.__dict__)
base_read=module.read
def reviewed_read(path):
 path=path.resolve()
 if path==(e.P/'production/timeline.json').resolve():return copy.deepcopy(timeline)
 if path==(oldbase/f'{kind}-annotation-tracks.json').resolve():return copy.deepcopy(registry)
 if path in mapped:return copy.deepcopy(mapped[path])
 return base_read(path)
module.read=reviewed_read;module.wrap_note=wrap_note;module.INSETS=insets;module.LOCAL_OUT=out
all_events=[];header=None;runs=[];receipts=[]
def seconds(value):
 h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
for slot in timeline['scenes']:
 if slot['classification']!='actual' or slot['id'] not in selection:continue
 e.authorized();ass=module.write_overlay(e.slug,slot['id']);lines=ass.read_text(encoding='utf8').splitlines()
 if header is None:header='\n'.join(lines[:next(i for i,v in enumerate(lines) if v.startswith('Dialogue:'))])
 windows=[]
 for line in lines:
  if not line.startswith('Dialogue:'):continue
  fields=line.split(',',9);a,z=seconds(fields[1]),seconds(fields[2])
  if fields[0]=='Dialogue: 1' and fields[3]=='Shape':windows.append((a,z))
  fields[1]=module.stamp(a+slot['start']);fields[2]=module.stamp(z+slot['start']);all_events.append(','.join(fields))
 groups=[]
 for a,z in sorted(windows):
  if groups and a<=groups[-1][1]+.02:groups[-1][1]=max(z,groups[-1][1])
  else:groups.append([a,z])
 for a,z in groups:runs.append({'scene':slot['id'],'start':a,'end':z})
 receipts.append({'scene':slot['id'],'localAss':rel(ass),'localAssSha256':sha(ass),'sourceClip':rel(e.O/f'clips/{slot["id"]}.mp4'),'sourceClipSha256':sha(e.O/f'clips/{slot["id"]}.mp4'),'overlay':read(ass.with_suffix('.json'))})
 print(e.id,slot['id'],'original annotation data restored; pixel review required',flush=True)
dst=e.O/'composition-polish.ass';dst.write_text(header+'\n'+'\n'.join(all_events)+'\n',encoding='utf8')
plan=e.H/'restored-available-guides.json'
save(plan,{'status':'await-direct-restored-track-inspection','partial':True,'selectedScenes':insets,'fullMasterReady':False,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originalRenderer':rel(original),'originalRendererSha256':sha(original),'adapter':rel(Path(__file__)),'adapterSha256':sha(Path(__file__)),'registrySha256':sha(oldbase/f'{kind}-annotation-tracks.json'),'timelineSha256':sha(e.P/'production/timeline.json'),'tracks':track_records,'scenes':receipts,'visibleIntervals':runs,'captionClearanceScenes':insets,'semantics':'Original red visible contour/edge, blue selected screen extent/reference, teal comparison region; no engine-space measurements','speechGating':'Saved original sentence cues plus existing observation-pause map; original ASR/PCM unavailable, no new TTS','changes':'Original points/order/object IDs/occlusion gaps retained; stroke and label sizes enlarged; bottom HUD/dialogue protected by1600x900 inset on selected scenes','finalMovingReview':'pending'})
save(e.H/'observed-guide-composition.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'plan':rel(plan),'planSha256':sha(plan),'globalAss':rel(dst),'globalAssSha256':sha(dst),'guides':len(runs),'eventCount':len(all_events),'pixelReview':'pending','captionClearanceScenes':insets})
