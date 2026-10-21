"""Reuse the original editable polygon tracks on restored original game cuts.

Original PCM and ASR caches are unavailable. Narration gates therefore use the
saved sentence cues and original pause map, never a newly generated voice.
Source byte hashes may change on restoration; every replacement is recorded and
must pass direct composited source/track inspection before full production.
"""
import copy,datetime,importlib.util,re,sys
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M13','M14'];e.authorized()
oldbase=R/'production/batches/game-math-part2-teaching-revision'
original=oldbase/'create-polygons-overlay.py';registry=read(oldbase/'polygons-annotation-tracks.json')
out=e.O/'polygon-overlays';out.mkdir(exist_ok=True)
insets={'M13':['05','QG01','QG02','08','QG03','QG08'],'M14':['QG04','14','QG05','17','19','QG07']}[e.id]
timeline=copy.deepcopy(e.T);track_records=[];mapped={};baseline={}
for slot in timeline['scenes']:
 if slot['classification']!='actual':continue
 if slot.get('preservedOriginal'):
  baseline[slot['baselineClip']]=rel(e.O/f'clips/{slot["id"]}.mp4');slot['baselineClip']=baseline[slot['baselineClip']]
 for name in registry['scenes'][slot['id']]['landmarkSources']:
  track=read(R/name);current=copy.deepcopy(track);current['sourceFile']=baseline.get(track['sourceFile'],track['sourceFile'])
  current['sourceSha256']=sha(R/current['sourceFile']);mapped[(R/name).resolve()]=current
  track_records.append({'scene':slot['id'],'track':name,'trackSha256':sha(R/name),'originalSource':track['sourceFile'],'originalSourceSha256':track['sourceSha256'],'restoredSource':current['sourceFile'],'restoredSourceSha256':current['sourceSha256'],'sameBytes':track['sourceSha256']==current['sourceSha256'],'reason':'Original cuts/frame count/framing restored; observed track retained. Changed source hashes require current pixel equivalence review.'})
source=original.read_text(encoding='utf8')
start=source.index(' def spoken(keyword,fallback):');end=source.index(' red_at=spoken',start)
source=source[:start]+''' def spoken(keyword,fallback):
  for cue in slot.get('sentenceCues',[]):
   if keyword not in cue['text']:continue
   raw_at=cue['start'];at=raw_at+sum(p['seconds'] for p in slot.get('observationPauses',[]) if p['rawAt']<=raw_at)
   if at>=max(reveal,fallback)-.1:return at
  return fallback
'''+source[end:]
gate_at=" track_reveals={}"
source=source.replace(gate_at," if ident=='QG08':red_at=8.5  # Original reviewed first-ledge speech gate.\n"+gate_at)
source=source.replace("events=[];sx,sy=2.4,2.4","events=[];sx=sy=2.0 if ident in INSETS else 2.4;ox=160 if ident in INSETS else 0")
source=source.replace('points=np.asarray(points)*[sx,sy]','points=np.asarray(points)*[sx,sy]+[ox,0]')
source=source.replace('x,y=np.array(p)*[sx,sy]','x,y=np.array(p)*[sx,sy]+[ox,0]')
source=source.replace('width=2.6','width=3.3')
source=source.replace(',15,True)',',22,True)')
source=source.replace("좌표',size=12)","좌표',size=18)")
source=source.replace("spec['mathNote'],'#ffe082',size=14)","spec['mathNote'],'#ffe082',size=20)")
source=source.replace("out=ROOT/'shared/output'/slug/'overlays'","out=LOCAL_OUT")
spec=importlib.util.spec_from_loader('restored_polygons_'+e.id,loader=None);module=importlib.util.module_from_spec(spec)
module.__file__=str(original);exec(compile(source,str(original),'exec'),module.__dict__)
base_read=module.read
def reviewed_read(path):
 path=path.resolve()
 if path==(e.P/'production/timeline.json').resolve():return copy.deepcopy(timeline)
 if path in mapped:return copy.deepcopy(mapped[path])
 return base_read(path)
module.read=reviewed_read;module.INSETS=insets;module.LOCAL_OUT=out
all_events=[];header=None;runs=[];receipts=[]
def seconds(value):
 h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
for slot in timeline['scenes']:
 if slot['classification']!='actual':continue
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
plan=e.H/'restored-polygon-guides.json'
save(plan,{'status':'await-direct-restored-track-inspection','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originalRenderer':rel(original),'originalRendererSha256':sha(original),'adapter':rel(Path(__file__)),'adapterSha256':sha(Path(__file__)),'registrySha256':sha(oldbase/'polygons-annotation-tracks.json'),'timelineSha256':sha(e.P/'production/timeline.json'),'tracks':track_records,'scenes':receipts,'visibleIntervals':runs,'captionClearanceScenes':insets,'semantics':'Original red exposed contour / blue editorial reference / yellow visible empty area; no engine-space measurements','speechGating':'Saved original sentence cues plus existing observation-pause map; original ASR/PCM unavailable, no new TTS','changes':'Original points/order/object IDs/occlusion gaps retained; stroke and label sizes enlarged; bottom HUD/dialogue protected by1600x900 inset on selected scenes','finalMovingReview':'pending'})
save(e.H/'observed-guide-composition.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'plan':rel(plan),'planSha256':sha(plan),'globalAss':rel(dst),'globalAssSha256':sha(dst),'guides':len(runs),'eventCount':len(all_events),'pixelReview':'pending','captionClearanceScenes':insets})
