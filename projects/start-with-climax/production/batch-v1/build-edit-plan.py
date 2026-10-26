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
  # PCM inclusion bounds cover the exact sample-contiguous scene. Visual cuts
  # remain on their separate nearest-frame clock below; never shift the voice.
  scenes.append({'id':s['id'],'title':k['title'],'voiceStart':origin,'voiceDuration':s['duration'],'sourceStartSample':s['startSample'],'sourceEndSample':s['endSample'],'startFrame':INTRO+int(s['startSample'])//800,'endFrame':INTRO+(int(s['endSample'])+799)//800,'audioFile':s['path'],'audioSha256':s['sha256'],'paragraphStarts':s['paragraphStarts']})
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

def actual_marks(c,src,r,first):
 # All coordinates name actually viewed source objects; no detector data.
 # Fixed captions are protected. Original bottom HUD/dialogue fits above864.
 n=c['frames']/60;sid=src['id'];start=c['sourceStart'];marks=[]
 def box(label,rect,color='green',duration=3):
  x,y,w,h=rect
  marks.append({'id':'focus-'+str(len(marks)),'shape':'rect','t0':0,'t1':min(n,duration),'color':color,'thickness':8,'label':label,'fontSize':42,'labelPosition':[210,12],'x':x,'y':y,'w':w,'h':h,'meaning':'Authored explanatory focus; no measured game data.','motionReview':'pending encoded moving review'})
 if sid=='acnh-dialogue':
  if r['id']=='03-p02':box('모여봐요 동물의 숲 · 고개와 손',[1008,250,240,250],duration=min(n,6))
  else:box('한 부분씩 이어지는 대사',[468,490,990,317],duration=3)
 elif sid.startswith('hades2') and ((sid.endswith('run') and 124<=start<145) or(sid.endswith('crossroads') and(38<=start<59 or 95<=start<123))):
  box(('하데스 II · ' if first else '')+'인물과 대화',[223,170,470,620],duration=3)
 elif sid=='doom-2016-opening' and r['id']=='01-p01':
  box(('DOOM(2016) · ' if first else '')+'중앙으로 조준',[908,380,104,104],duration=1.4)
 elif sid=='galaxy2-opening' and r['id']=='05-p02':
  box('스핀 동작 안내',[650,60,730,105],duration=min(n,3))
 elif sid=='ace-trilogy-official-first-case' and start<59.2:
  box('역전재판 · 제시할 증거 선택',[400,418,1100,112],duration=min(n,max(0,59.20-start)))
 if first and not marks:
  names={'hades2':'하데스 II','acnh':'모여봐요 동물의 숲','doom':'DOOM(2016)','galaxy2':'슈퍼 마리오 갤럭시 2','ace':'역전재판123 나루호도 셀렉션'}
  box(names[src['gameId']],[184,4,1550,856],color='yellow',duration=2)
 return marks

def diagram_options(r):
 if SLUG=='start-with-climax':
  if r['mode']=='control':return {'image':'/@fs/'+(LOCAL/'sources/doom-review/fine-first-fight/004.png').as_posix()}
  if r['mode']=='firstAct':return {'image':'/@fs/'+(LOCAL/'sources/ace-announce-review/fine-first-case/007.png').as_posix()}
  if r['mode']=='earlyPeak':return {'showFallback':r['id']=='08-p01'}
  if r['mode']=='evidenceSelection':
   base=LOCAL/'sources/ace-announce-review/fine-first-case'
   return {'images':{'before':'/@fs/'+(base/'006.png').as_posix(),'after':'/@fs/'+(base/'007.png').as_posix(),'aspect':16/9}}
  if r['mode']=='ruleUse':return {'images':{'before':img('spin-before.png'),'after':img('spin-after.png'),'aspect':2560/1404}}
  return {}
 if r['mode']=='storyFocus':
  if r['id']=='02-p01':return {'image':img('painting.png'),'focus':[.28,.24,.4,.48]}
  if r['id']=='03-p02':return {'image':'/@fs/'+(LOCAL/'sources/acnh-dialogue-review/hands/128.png').as_posix(),'focus':[.54,.3,.14,.28]}
  return {'image':img('melinoe.png'),'focus':[.18,.24,.12,.22]}
 return {}

def semantic_cues(c,captions):
 origin=c['startFrame']/60;duration=c['frames']/60
 related=[x for x in captions if x['paragraph'] in c['paragraphIds']]
 def at(pid,index=0):
  part=[x for x in captions if x['paragraph']==pid]
  return max(0,min(duration,part[index]['start']-origin))
 cues=[max(0,min(duration,x['start']-origin)) for x in related]
 if SLUG=='start-with-climax':
  if c['mode']=='overview':
   import re
   words=read(LOCAL/'voice/whole-source-asr.json')['words'];lo=min(x['start']for x in related)-2;hi=max(x['end']for x in related)-2
   clean=lambda t:re.sub(r'[^가-힣a-z0-9]','',t.lower())
   def phrase(q):
    for i,w in enumerate(words):
     if lo-.05<=w['timestamp'][0]<=hi and clean(''.join(x['text']for x in words[i:i+3])).startswith(q):return max(0,min(duration,w['timestamp'][0]+2-origin))
    raise ValueError('Current measured overview phrase missing: '+q)
   return [phrase('첫전투'),phrase('거대한'),phrase('첫재판'),at('01-p02',3)]
  if c['paragraphIds']==['01-p03']:return [0,0,at('01-p03',3)]
  if c['paragraphIds']==['08-p01']:return [0,at('08-p01',1),at('08-p01',3)]
  if c['scene']=='03' and c['mode']=='informationOrder':
   if '03-p02' in c['paragraphIds']:return [0,at('03-p02',1)]
   c['diagramOptions']['orderState']='reordered';return [0,0]
  if c['scene']=='06' and c['mode']=='informationOrder':c['diagramOptions']['orderState']='reordered';return [0,0]
  if c['paragraphIds']==['08-p02']:return [0,at('08-p02',1),at('08-p02',1)]
 else:
  if c['paragraphIds']==['01-p02']:return [at('01-p02',2),at('01-p02',3),at('01-p02',3)]
  if c['paragraphIds']==['01-p03']:return [0,at('01-p03',2)]
  if c['mode']=='qte':
   last=next(x for x in captions if x['paragraph']=='09-p02' and '갑자기' in x['ko'])
   return [0,at('09-p01',2),max(0,min(duration,last['start']-origin))]
  if c['paragraphIds']==['08-p03']:return [0,at('08-p03',2)]
 return cues

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
    src=sources[sid];c={'id':f'cut{len(cuts):03d}','scene':r['scene'],'paragraphIds':[r['id']],'startFrame':a,'endFrame':a+num,'frames':num,'kind':'independent-gameplay','source':sid,'gameId':src['gameId'],'sourceFile':src['path'],'sourceSha256':src['sha256'],'sourceStart':t,'sourceAttribution':src['url']+' | '+src['licenseLabel'],'sourceAudioEnabled':True,'sourceAudioReason':'Original synchronized gameplay stereo retained under recorded game and recorder video-use terms; no competing external commentary in selected windows.','sourceAudioReviewStatus':'original-mix-retained-perceptual-listening-pending','viewport':[0,0,1920,864],'nativeSpeed':True,'marks':[],'sourceProtectedRects':[[224,52,1472,75],[224,755,1472,125]],'sourceRole':'independent-gameplay','semanticPurpose':r['summary'],'narratedInternalStateIsMeasurement':False}
    c['marks']=actual_marks(c,src,r,src['gameId'] not in seen)
    if sid=='ace-trilogy-official-first-case':
     c['sourceAudioEnabled']=False
     c['sourceAudioReason']='mixed-promo-audio exception, limited to5.5s actual first-case UI. Official announcement description has only general CAPCOM copyright, no track-specific promo-score ownership. Current policy permits only Capcom-owned music. This is not an assertion of third-party music; retain all independently documented game-recording audio elsewhere.'
     c['sourceAudioReviewStatus']='bounded-rights-exception; see source-audio-review.json'
    seen.add(src['gameId'])
    cuts.append(c);a+=num
  if d:
   if r.get('diagramFirst'):a=r['startFrame']
   opts=diagram_options(r)
   c={'id':f'cut{len(cuts):03d}','scene':r['scene'],'paragraphIds':[r['id']],'startFrame':a,'endFrame':a+d,'frames':d,'kind':'explanation','mode':r['mode'],'title':r['title'],'diagramOptions':opts,'renderedSource':relative(LOCAL/'rendered'/f'{SLUG}-explanations.mp4'),'renderedStartFrame':mcframe,'mcStartFrame':mcframe,'mcEndFrame':mcframe+d,'marks':[],'illustrationNotMeasuredGameOutput':True};mcframe+=d;cuts.append(c)
 cuts.sort(key=lambda c:c['startFrame'])
 merged=[]
 for c in cuts:
  if merged and c['kind']=='explanation' and merged[-1]['kind']=='explanation' and c['scene']==merged[-1]['scene'] and c['mode']==merged[-1]['mode'] and c['mode'] in ('informationOrder','qte'):
   prev=merged[-1];prev['endFrame']=c['endFrame'];prev['frames']+=c['frames'];prev['paragraphIds']+=c['paragraphIds']
  else:merged.append(c)
 cuts=merged;packed=0
 for i,c in enumerate(cuts):
  c['id']=f'cut{i:03d}'
  if c['kind']=='explanation':
   c['renderedStartFrame']=c['mcStartFrame']=packed;packed+=c['frames'];c['mcEndFrame']=packed
 assert packed==mcframe
 music=ROOT/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3';license=music.with_name('Nimbus-Eveningland.LICENSE.md');brand=ROOT/'projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'
 result={'schemaVersion':1,'slug':SLUG,'revision':'batch-v1','status':'measured-native-edit-awaiting-moving-review','fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':body+720,'actualFrames':sum(r['actualFrames'] for r in allocated),'explanationFrames':mcframe,'mcFrames':mcframe,'expectedGameplayShare':.6,'ratioToleranceFrames':1,'scenes':scenes,'cuts':cuts,'measuredParagraphs':allocated,'captionProtectedRect':[150,892,1784,1060],'captionAliases':read(PROJECT/'script/batch-v1/caption-aliases.json'),'brandingFile':relative(brand),'membershipFile':relative(brand.with_name('membership.mp4')),'outputDir':relative(LOCAL/'edit'),'outputStem':SLUG+'-batch-v1','mixFile':relative(LOCAL/'edit/final-mix.wav'),'captionsAss':relative(LOCAL/'edit/captions.ko.ass'),'audio':{'preserveGameAudio':True,'targetLufs':-16,'voicePeakDbfs':-2.5,'gameLufs':-23,'gameNarrationRelativeDb':-10,'matchSceneRms':False,'musicLufs':-28,'music':{'path':relative(music),'sha256':sha(music),'licenseRecord':relative(license),'title':'Nimbus','artist':'Eveningland'}},'inputRecords':{'timing':{'path':relative(timing_path),'sha256':sha(timing_path)},'scripts':files,'sourceInventory':{'path':relative(PROJECT/'sources/independent-footage.json'),'sha256':sha(PROJECT/'sources/independent-footage.json')}},'noLoops':True,'sourceRatePreserved':True,'narrationTimeStretch':False,'editorAddedSourceCreditsRendered':False,'sourceCreditsPlacement':'description bottom only','humanWholeListening':'pending','humanFinalReview':'pending','automaticNextVideo':False}
 # A reviewed visual-only patch reuses the unchanged full narration/captions.
 # Its four explanation exports are packed separately from the preserved base.
 patch_file=HERE/'visual-patch-v2.json'
 if patch_file.is_file():
  patch=read(patch_file)
  for item in patch['cuts']:
   target=next(c for c in cuts if c['id']==item['cut'])
   if target['kind']!='explanation' or target['frames']!=item['frames']:raise ValueError('Visual patch mapping is stale')
   target['renderedSource']=relative(LOCAL/'rendered'/'start-with-climax-explanations-patch-v2.mp4')
   target['renderedStartFrame']=item['patchStartFrame']
  result['outputStem']='start-with-climax-batch-v1-r2'
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
 captions=read(LOCAL/'edit/captions.json')['cues'];segments=[]
 for c in cuts:
  if c['kind']!='explanation':continue
  cues=semantic_cues(c,captions)
  opts=dict(c['diagramOptions']);opts.update(kind=c['mode'],title=c['title'],duration=c['frames']/60,cues=cues)
  segments.append(opts);c['visualCues']=cues
 save(MC/'motion-data.json',{'status':'measured-ready','slug':SLUG,'revision':'batch-v1','packedFrames':mcframe,'segments':segments,'voiceTimingSha256':sha(timing_path),'captionSha256':sha(LOCAL/'edit/captions.json')})
 save(HERE/'edit-plan.json',result);save(HERE/'edit-allocation-report.json',report)
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--capacity-audit',action='store_true');args=ap.parse_args()
 if args.capacity_audit:print(json.dumps(capacity(read(PROJECT/'planning/scene-layout.json')),indent=2));return
 make_plan(args.dry_run)
if __name__=='__main__':main()
