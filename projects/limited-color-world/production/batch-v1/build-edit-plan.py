"""Measured native footage + packed explanation builder; no voice/media generation.
--dry-run validates a placement without writing plans/wrappers/captions.
Requires root's reviewed actual source-scene-timings.json. Unavailable semantic
capacity fails; no invented silence, repeated footage, speed fitting or clocks.
"""
from pathlib import Path
import argparse,json,math,hashlib,copy
from storage_paths import repo_path,relative,write_path,local_output
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];SLUG=PROJECT.name
LOCAL=PROJECT/'production/local/batch-v1';MC=ROOT/'motion-canvas/src/projects'/SLUG/'batch-v1'
FPS=60;INTRO=120;OUTRO=600

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):
 p=write_path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for c in iter(lambda:f.read(4*1024*1024),b''):h.update(c)
 return h.hexdigest()
def fr(t):return math.floor(t*FPS+.5)
def img(k):return '/@fs/'+(LOCAL/'visual-assets'/k).as_posix()

def capacity(layout):return {k:sum(math.floor((b['out']-b['in'])*60+1e-6) for b in banks) for k,banks in layout['pools'].items()}
def validate_layout(layout,inventory,ko):
 sources={x['id']:x for x in inventory['sources']};expected={f"{s['id']}-p{i+1:02d}" for s in ko['scenes'] for i in range(len(s['lines']))}
 if set(layout['paragraphs'])!=expected:raise ValueError('Complete source-order paragraphs must be mapped exactly once')
 intervals={}
 for pool,banks in layout['pools'].items():
  for b in banks:
   src=sources[b['source']];meta=src['decoded']
   if src['role']!='independent-gameplay' or min(int(meta['width']),int(meta['height']))<1080:raise ValueError('Only independently verified native FHD sources may enter actual banks')
   if not 0<=b['in']<b['out']<=float(meta['duration'])+1e-5:raise ValueError('Native bank exceeds original source duration')
   intervals.setdefault(src['id'],[]).append((b['in'],b['out']))
 for sid,spans in intervals.items():
  spans.sort()
  if any(a[1]>b[0]+1e-6 for a,b in zip(spans,spans[1:])):raise ValueError('Overlapping/reused native source interval: '+sid)
 for pid,r in layout['paragraphs'].items():
  if not 0<=r['minActualShare']<=r['preferredActualShare']<=r['maxActualShare']<=1:raise ValueError('Invalid semantic placement bounds: '+pid)
 return True

def measured_rows(timing,ko,layout):
 rows=[];scenes=[]
 for s,k in zip(timing['scenes'],ko['scenes']):
  assert s['id']==k['id'];origin=s['startSample']/48000+2
  # A scene protects every original PCM sample; the visual cut clock remains rounded below.
  scenes.append({'id':s['id'],'title':k['title'],'voiceStart':origin,'voiceDuration':s['duration'],'sourceStartSample':s['startSample'],'sourceEndSample':s['endSample'],'startFrame':INTRO+s['startSample']//800,'endFrame':INTRO+(s['endSample']+799)//800,'audioFile':s['path'],'audioSha256':s['sha256'],'paragraphStarts':s['paragraphStarts']})
  for i,p in enumerate(s['paragraphs']):
   pid=f"{s['id']}-p{i+1:02d}";begin=fr(origin+(p['start'] if i else 0));end=fr(origin+(s['paragraphs'][i+1]['start'] if i+1<len(s['paragraphs']) else s['duration']))
   rows.append({'id':pid,'scene':s['id'],'title':k['title'],'ko':p['text'],'startFrame':begin,'endFrame':end,'frames':end-begin,**layout['paragraphs'][pid]})
 # Contiguous image clock; source PCM remains placed on its exact unrounded origin.
 for i,r in enumerate(rows):r['startFrame']=INTRO if not i else rows[i-1]['endFrame'];r['frames']=r['endFrame']-r['startFrame']
 return rows,scenes

def allocate(rows,caps,target):
 work=copy.deepcopy(rows)
 for r in work:
  n=r['frames'];r['minActualFrames']=fr(n/60*r['minActualShare']);r['maxActualFrames']=fr(n/60*r['maxActualShare']);r['actualFrames']=min(r['maxActualFrames'],max(r['minActualFrames'],round(n*r['preferredActualShare'])))
 for r in work:
  if 'fixedActualFrames' in r:
   value=r['fixedActualFrames']
   if not isinstance(value,int) or not 0<=value<=r['frames']:raise ValueError('Measured explicit actual allocation must fit its unchanged paragraph')
   r['actualFrames']=r['minActualFrames']=r['maxActualFrames']=value
 # Respect each game's observed unique source capacity before balancing total.
 for pool,cap in caps.items():
  group=[r for r in work if r['pool']==pool]
  excess=sum(r['actualFrames'] for r in group)-cap
  for r in sorted(group,key=lambda r:r['preferredActualShare']):
   d=min(max(0,excess),r['actualFrames']-r['minActualFrames']);r['actualFrames']-=d;excess-=d
  if excess>0:raise ValueError(f'{pool}: semantic minimum exceeds observed native bank capacity by{excess}frames')
 delta=target-sum(r['actualFrames'] for r in work)
 for _ in range(3):
  if not delta:break
  candidates=sorted(work,key=lambda r:(r['preferredActualShare'],r['frames']),reverse=delta>0)
  for r in candidates:
   if not r['pool']:continue
   used=sum(a['actualFrames'] for a in work if a['pool']==r['pool'])
   room=min(r['maxActualFrames']-r['actualFrames'],caps[r['pool']]-used) if delta>0 else r['actualFrames']-r['minActualFrames']
   d=min(abs(delta),max(0,room))*(1 if delta>0 else -1);r['actualFrames']+=d;delta-=d
 if delta:raise ValueError(f'Actual60:explanation40 infeasible; {delta}frames short. Native capacities{caps}; no padding/speed changes allowed')
 return work

def source_parts(pool,n,state,layout):
 out=[];banks=layout['pools'][pool]
 while n:
  idx,used=state[pool];b=banks[idx];cap=math.floor((b['out']-b['in'])*60+1e-6);take=min(n,cap-used)
  if take:out.append((b['source'],b['in']+used/60,take));n-=take;used+=take
  if used==cap:idx+=1;used=0
  state[pool]=(idx,used)
  if n and idx>=len(banks):raise ValueError('Native bank exhausted without repeats: '+pool)
 return out

def make_plan(dry=False):
 import audio_pipeline as audio
 audio.require_authorized('measured edit and captions')
 ko,en,spoken,files=audio.scripts();timing_path=LOCAL/'voice/source-scene-timings.json'
 if not timing_path.is_file():raise ValueError('Actual reviewed voice timing is absent; no estimated-clock edit is created')
 timing=read(timing_path);layout=read(PROJECT/'planning/scene-layout.json');inventory=read(PROJECT/'sources/independent-footage.json');sources={s['id']:s for s in inventory['sources']}
 validate_layout(layout,inventory,ko)
 if timing['sampleRate']!=48000:raise ValueError('48k unchanged approved PCM required')
 rows,scenes=measured_rows(timing,ko,layout);body=math.ceil(timing['scenes'][-1]['endSample']/800);rows[-1]['endFrame']=INTRO+body;rows[-1]['frames']=rows[-1]['endFrame']-rows[-1]['startFrame']
 allocated=allocate(rows,capacity(layout),round(body*.6));states={k:(0,0) for k in layout['pools']};cuts=[];mcframe=0;seen=set()
 for r in allocated:
  n=r['actualFrames'];a=r['startFrame'];d=r['frames']-n
  # Concrete phenomenon first; the parameter/condition diagram follows under its explanation.
  if r.get('diagramFirst') and d:
   a+=d
  if n:
   for sid,t,num in source_parts(r['pool'],n,states,layout):
    src=sources[sid];c={'id':f'cut{len(cuts):03d}','scene':r['scene'],'paragraphIds':[r['id']],'startFrame':a,'endFrame':a+num,'frames':num,'kind':'independent-gameplay','source':sid,'gameId':src['gameId'],'sourceFile':src['path'],'sourceSha256':src['sha256'],'sourceStart':t,'sourceAttribution':src['url']+' | '+src['licenseLabel'],'sourceAudioEnabled':src.get('sourceAudioEnabled',True),'sourceAudioReason':src.get('sourceAudioReason','Original synchronized gameplay stereo retained under recorded game and recorder video-use terms; no competing external commentary in selected windows.'),'sourceAudioReviewStatus':'technical-source-review-original-mix-retained' if src.get('sourceAudioEnabled',True) else 'verified-original-source-has-no-audio-stream','viewport':[256,80,1408,792],'nativeSpeed':True,'marks':[],'sourceProtectedRects':[[224,52,1472,75],[224,755,1472,125]],'sourceRole':'independent-gameplay','semanticPurpose':r['summary'],'narratedInternalStateIsMeasurement':False}
    if src['gameId'] not in seen:
     name=next(g['title'] for g in inventory['games'] if g['id']==src['gameId']);c['marks'].append({'id':'game-name','shape':'rect','t0':0,'t1':min(3,num/60),'color':'#e8cf83','thickness':6,'label':name,'fontSize':42,'labelPosition':[275,7],'x':256,'y':80,'w':1408,'h':792});seen.add(src['gameId'])

    if sid=='puyo-intro' and r['id'] in ('01-p01','04-p03','08-p01'):
     c['marks'].append({'id':'puyo-field','shape':'rect','t0':0,'t1':min(4,num/60),'color':'green','thickness':8,'label':'왼쪽 필드 · 같은 색 연결','labelPosition':[430,155],'x':425,'y':220,'w':365,'h':560})
    if sid=='smash-cpu' and r['id']=='02-p02':
     c['marks'].append({'id':'cpu-sonic','shape':'rect','t0':0,'t1':min(4,num/60),'color':'green','thickness':8,'label':'CP = 소닉','labelPosition':[1280,681],'x':1260,'y':735,'w':260,'h':130})
    if sid=='smash-cpu' and r['id']=='04-p02':
     c['marks'].append({'id':'damage-percent','shape':'rect','t0':0,'t1':min(5,num/60),'color':'green','thickness':8,'label':'누적 대미지 %','labelPosition':[1260,670],'x':1370,'y':748,'w':175,'h':80})
    cuts.append(c);a+=num
  if d:
   if r.get('diagramFirst'):a=r['startFrame']
   images=[]
   if SLUG=='limited-color-world':
    images=[img('puyo.jpg'),img('mario-gray.jpg')] if r['mode']=='compareChecks' else [img('puyo.jpg'),img('flower.jpg'),img('mario-gray.jpg')] if r['mode']=='overview' else [img('puyo-filter-11.jpg'),img('puyo-filter-12.jpg')] if r['mode']=='setting' else [img('mario.jpg'),img('mario-gray.jpg')] if r['mode']=='grayscale' else [img('mario.jpg')] if r['pool']=='mario' else [img('puyo.jpg')]
   else:images=[img('dice.jpg')] if r['pool']=='dice' else [img('smash.jpg')]
   c={'id':f'cut{len(cuts):03d}','scene':r['scene'],'paragraphIds':[r['id']],'startFrame':a,'endFrame':a+d,'frames':d,'kind':'explanation','mode':r['mode'],'title':r['title'],'labels':r['labels'],'summary':r['summary'],'images':images,'renderedSource':relative(LOCAL/'rendered'/f'{SLUG}-explanations.mp4'),'renderedStartFrame':mcframe,'mcStartFrame':mcframe,'mcEndFrame':mcframe+d,'marks':[],'illustrationNotMeasuredGameOutput':True};mcframe+=d;cuts.append(c)
 cuts.sort(key=lambda c:c['startFrame'])
 for i,c in enumerate(cuts):c['id']=f'cut{i:03d}'
 music=ROOT/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3';license=music.with_name('Nimbus-Eveningland.LICENSE.md');brand=ROOT/'projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'
 result={'schemaVersion':1,'slug':SLUG,'revision':'batch-v1','status':'measured-native-edit-awaiting-moving-review','fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':body+720,'actualFrames':sum(r['actualFrames'] for r in allocated),'explanationFrames':mcframe,'mcFrames':mcframe,'expectedGameplayShare':.6,'ratioToleranceFrames':1,'scenes':scenes,'cuts':cuts,'measuredParagraphs':allocated,'captionProtectedRect':[150,892,1784,1060],'captionAliases':read(PROJECT/'script/batch-v1/caption-aliases.json'),'brandingFile':relative(brand),'membershipFile':relative(brand.with_name('membership.mp4')),'outputDir':relative(LOCAL/'edit'),'outputStem':SLUG+'-batch-v1','mixFile':relative(LOCAL/'edit/final-mix.wav'),'captionsAss':relative(LOCAL/'edit/captions.ko.ass'),'audio':{'preserveGameAudio':True,'targetLufs':-16,'voicePeakDbfs':-2.5,'gameLufs':-23,'gameNarrationRelativeDb':-10,'matchSceneRms':False,'musicLufs':-28,'music':{'path':relative(music),'sha256':sha(music),'licenseRecord':relative(license),'title':'Nimbus','artist':'Eveningland'}},'inputRecords':{'timing':{'path':relative(timing_path),'sha256':sha(timing_path)},'scripts':files,'sourceInventory':{'path':relative(PROJECT/'sources/independent-footage.json'),'sha256':sha(PROJECT/'sources/independent-footage.json')}},'noLoops':True,'sourceRatePreserved':True,'narrationTimeStretch':False,'editorAddedSourceCreditsRendered':False,'sourceCreditsPlacement':'description bottom only','humanWholeListening':'pending','humanFinalReview':'pending','automaticNextVideo':False}
 import video_pipeline as video
 ratio=video.validate_plan(result)
 report={'slug':SLUG,'bodyFrames':body,'totalFrames':body+720,'mcFrames':mcframe,'ratio':ratio,'capacities':capacity(layout),'actualFramesByPool':{p:sum(r['actualFrames'] for r in allocated if r['pool']==p) for p in layout['pools']},'paragraphs':[{k:r[k] for k in ('id','frames','pool','actualFrames','mode')} for r in allocated]}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if dry:return result
 save(HERE/'edit-plan.json',result)
 # Caption preparation uses the source word-clock, never interpolated display counts.
 audio.caption_input(HERE/'edit-plan.json',local_output(LOCAL/'edit'))
 import caption_pipeline as caption
 caption.build(read(LOCAL/'edit/caption-input.json'),local_output(LOCAL/'edit'))
 captions=read(LOCAL/'edit/captions.json')['cues'];imports=[];names=[]
 if SLUG=='limited-color-world':
  clear=next(x for x in captions if x['paragraph']=='01-p01' and x['ko'].startswith('연결된 뿌요'))
  target=clear['start']+min(.5,(clear['end']-clear['start'])/2)
  delta=1082-(target-2)-1070
  first=next(c for c in cuts if c.get('source')=='puyo-intro')
  if not first['sourceStart']+delta<=1078 or first['sourceStart']+delta+first['frames']/60<1082.6:raise ValueError('Opening lackscomplete inspected Puyo fall/land/clear; revise nativeallocation instead of padding')
  for c in cuts:
   if c.get('source')=='puyo-intro':
    c['sourceStart']+=delta
    if c['sourceStart']<1070 or c['sourceStart']+c['frames']/60>1216:raise ValueError('Measured opening shift exceeds directlyinspected Puyo scope')
  result['actualGameAbstractAnchor']={'sourceEventCenter':1082,'globalCaptionClause':[clear['start'],clear['end']],'nativeClockShiftSeconds':delta,'targetGlobalSeconds':target,'completeBeforeActionResult':True}
  from supplement_question_block import apply as apply_question_block
  apply_question_block(result,sources)
  video.validate_plan(result)
 if SLUG=='computer-controlled-players':
  first=[c for c in cuts if c['paragraphIds']==['01-p01']];assert sum(c['frames'] for c in first)==678
  second_clause=next(c for c in captions if c['paragraph']=='01-p01' and c['ko'].startswith('멀리서'))
  change=fr(second_clause['start']);assert change==319
  originals={c.get('source'):c for c in first if c['kind']=='independent-gameplay'}
  mario=copy.deepcopy(first[0]);mario.update(startFrame=120,endFrame=249,frames=129,sourceStart=3.85385)
  freeze=copy.deepcopy(next(c for c in first if c['kind']=='explanation'));freeze.update(startFrame=249,endFrame=319,frames=70,mode='evidenceFreeze',title='가까운 주먹 · 명중 결과',images=[img('mario-result.jpg')],labels=[],summary='명중 결과 정지 분석',renderedStartFrame=0,mcStartFrame=0,mcEndFrame=70)
  def native(template,start,end,source_start):
   n=copy.deepcopy(template);n.update(startFrame=start,endFrame=end,frames=end-start,sourceStart=source_start,marks=[]);return n
  fludd=native(first[1],319,420,6.006)
  beam=native(originals['smash-samus'],420,535,10.7)
  ice=native(originals['smash-samus'],535,649,12.629283)
  cpu_template=next(c for c in cuts if c.get('source')=='smash-cpu')
  cp=native(cpu_template,649,798,118.4);cp['paragraphIds']=['01-p01']
  remaining=[c for c in cuts if c not in first]
  for c in remaining:
   if c.get('source')=='smash-cpu':c['sourceStart']+=149/60
  cuts[:]=[mario,freeze,fludd,beam,ice,cp,*remaining]
  # The one-second overview tail inherits the next movement/decision diagram;
  # it does not reset to a separate slide before the historical example.
  i=next(i for i,c in enumerate(cuts) if c['kind']=='explanation' and c['paragraphIds']==['01-p02'])
  a,b=cuts[i],cuts[i+1];assert b['kind']=='explanation' and b['paragraphIds']==['02-p01'] and a['endFrame']==b['startFrame']
  b.update(startFrame=a['startFrame'],frames=a['frames']+b['frames'],paragraphIds=['01-p02','02-p01'],visualParagraphIds=['02-p01'],renderedStartFrame=a['renderedStartFrame'],mcStartFrame=a['mcStartFrame'])
  cuts.pop(i)
  for i,c in enumerate(cuts):c['id']=f'cut{i:03d}'
  result['actualFramesBySource']={sid:sum(c['frames'] for c in cuts if c.get('source')==sid) for sid in sources}
  result['measuredSemanticJoinCorrections']={'openingClause2Frame':change,'firstPunchResultFreezeFrames':70,'sourceAudioOriginalsPreserved':True,'unusedOpeningSamusGrabFrames':149,'cpuClockShiftForNonreuseFrames':149,'overviewTailMergedIntoNextDiagram':True,'endingOnActualGame':True,'bodyAndRatioUnchanged':True}
  video.validate_plan(result)

 for c in cuts:
  if c['kind']!='explanation':continue
  cues=[x['start']-c['startFrame']/60 for x in captions if x['paragraph'] in c.get('visualParagraphIds',c['paragraphIds'])]
  opts={k:c[k] for k in ('mode','title','labels','summary','images')};opts.update(duration=c['frames']/60,cues=cues)
  name=c['id'];fn=MC/(name+'.tsx');fn.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(opts,ensure_ascii=False)+");});\n",encoding='utf-8');imports.append(f"import {name} from './{name}?scene';");names.append(name);c['visualCues']=cues
 (MC/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+"\nexport default makeProject({scenes:["+','.join(names)+"]});\n",encoding='utf-8')
 save(HERE/'edit-plan.json',result);save(HERE/'edit-allocation-report.json',report)
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--capacity-audit',action='store_true');args=ap.parse_args()
 if args.capacity_audit:print(json.dumps(capacity(read(PROJECT/'planning/scene-layout.json')),indent=2));return
 make_plan(args.dry_run)
if __name__=='__main__':main()
