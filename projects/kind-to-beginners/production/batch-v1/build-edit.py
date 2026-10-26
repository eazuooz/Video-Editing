"""D29 measured source clock to native-speed cut list and packed MC diagrams."""
from pathlib import Path
import json,math,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4]
SLUG='kind-to-beginners';PROJECT=ROOT/'projects'/SLUG;LOCAL=PROJECT/'production/local/batch-v1'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def relative(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Native motion and speech-bound diagrams, not a duration-filler montage.
# scene-local end seconds, kind, native-source key/start or diagram purpose.
SPECS={
'01':[(10,'G','mk8',0),(16,'E','flow',0),(24,'G','mk8',20),(29,'E','flow',1),(None,'G','sf6-match',7)],
'02':[(6,'E','arcade',0),(15,'G','sf6-match',11),(21,'E','intent',0),(28,'G','sf6-match',21),(33,'E','intent',1),(43,'G','sf6-match',30),(None,'E','intent',2)],
'03':[(7,'G','sf6-match',50),(12,'E','goal',0),(20,'G','sf6-match',97),(27,'E','goal',1),(36,'G','sf6-match',60),(41,'E','feedback',0),(None,'G','sf6-match',122)],
'04':[(9,'G','mk8',40),(16,'E','onboarding',0),(25,'G','mk8',60),(31,'E','onboarding',1),(40,'G','mk8',75),(None,'E','burden',0)],
'05':[(8.7,'E','steering',0),(16.8,'E','acceleration',0),(29.8,'G','mk8',103),(37.8,'E','turbo',0),(None,'G','mk8',155)],
'06':[(9.5,'G','sf6-dynamic',2.5),(14.8,'E','distance',0),(23,'G','sf6-dynamic',16),(29,'E','offline',0),(37,'G','sf6-dynamic',33),(None,'E','handoff',0)],
'07':[(6,'G','hike-climbing',0),(14,'E','instructions',0),(23,'G','hike-walk',1),(29,'E','route',0),(38,'G','hike-glide',0),(43,'E','choice',0),(None,'G','hike-glide',11)],
'08':[(9,'G','hike-glide',18),(16,'E','interest',0),(25,'G','mk8',180),(31,'E','summary',0),(None,'G','mk8',230)]}
TEXT={
'flow':('다음 한 판을 스스로 고르게', ['직접 시도','결과를 이해','다음 선택']),
'arcade':('화면 너머의 사람은 보이지 않는다',['공격은 보인다','기대는 숨겨져 있다','의도를 먼저 읽기']),
'intent':('같은 경기, 서로 다른 목적',['진지한 승부','가벼운 첫 시도','목표 확인']),
'goal':('전력 승부는 서로 원할 때',['승부 방식 합의','할 수 있는 행동','배울 수 있는 결과']),
'feedback':('내 조작과 결과를 연결하기',['방어를 알려주기','한 번 막아보기','다음 행동 선택']),
'onboarding':('온보딩 · 첫 재미까지 가는 길',['버튼을 안다','하나를 해본다','결과를 느낀다']),
'burden':('한꺼번에 요구하는 입력을 나눈다',['방향 조절','가속 유지','아이템 선택']),
'steering':('Smart Steering · 핸들 어시스트',['코스를 벗어나려 할 때','방향 조절 지원','뒤쪽 안테나로 확인']),
'acceleration':('Auto-Accelerate · 가속 유지',['가속 버튼 유지 부담 ↓','코너·아이템을 볼 여유 ↑','필요한 보조만 선택']),
'turbo':('익숙해지면 더 정교하게',['미니 터보','슈퍼 미니 터보','울트라: 보조를 끈 뒤']),
'distance':('Dynamic · 입력과 판단을 나누기',['버튼 입력','상대와의 거리','상황에 맞는 공격']),
'offline':('오프라인의 일부 모드에서',['Dynamic controls','Fighting Ground','첫 흐름을 경험하는 선택지']),
'handoff':('입력 부담을 덜고, 선택을 남긴다',['대신할 입력','직접 해볼 판단','도움을 멈출 때']),
'instructions':('모든 지시를 주면, 선택이 줄어든다',['다음 버튼','다음 길','남이 정한 순서']),
'route':('스스로 가보고 싶은 길',['지금 보이는 장소','내가 고른 방향','직접 확인한 결과']),
'choice':('필요한 정보 뒤에 선택을 돌려준다',['조작·규칙 안내','한 걸음 물러서기','본인이 다음 행동']),
'interest':('처음 생긴 작은 관심을 지킨다',['첫 시도','알아낸 결과','다음 시도']),
'summary':('친절함의 목표는 스스로 즐기는 것',['목표 합의','입력 지원','선택 돌려주기'])}
SHOT={'01':('mk8',25),'02':('sf6-match',33),'03':('sf6-match',61),'04':('mk8',68),'05':('mk8',84),'06':('sf6-dynamic',21),'07':('hike-glide',15),'08':('mk8',189)}
if __name__=='__main__':
 timing=load(LOCAL/'voice/source-scene-timings.json');sources=load(PROJECT/'planning/sources.json')['sources'];bank={s['id']:s for s in sources}
 duration=timing['scenes'][-1]['sourceOrigin']+timing['scenes'][-1]['duration'];body=math.ceil(duration*60);total=body+720
 scenes=[];cuts=[]
 for si,s in enumerate(timing['scenes']):
  sid=s['id'];base=120+round(s['sourceOrigin']*60);end=120+round((s['sourceOrigin']+s['duration'])*60)
  if si==len(timing['scenes'])-1:end=120+body
  scenes.append({'id':sid,'title':s['title'],'voiceStart':2+s['sourceOrigin'],'startFrame':120+math.floor(s['sourceOrigin']*60),'endFrame':120+math.ceil((s['sourceOrigin']+s['duration'])*60)})
  cursor=base
  for j,(last,kind,key,offset) in enumerate(SPECS[sid]):
   cutend=end if last is None else base+round(last*60);frames=cutend-cursor
   c={'id':f'{sid}-{j+1:02d}','scene':sid,'startFrame':cursor,'endFrame':cutend,'frames':frames,'kind':'independent-gameplay' if kind=='G' else 'explanation','normalSpeed':True,'playbackSpeed':1,'loop':False}
   if kind=='G':
    src=bank[key];c.update(source=key,game=key,sourceFile=src['file'],sourceSha256=src['sha256'],sourceStart=offset,sourceAttribution=f"{src['creator']} | {src['url']}",sourceAudioEnabled=True,sourceAudioReviewStatus="reviewed-native-retain",audioRightsReview="projects/kind-to-beginners/planning/audio-source-review.json",onScreenAttributionRequired=False)
   else:c.update(purpose=key,variant=offset,renderedSource=f'projects/{SLUG}/production/local/batch-v1/rendered/{SLUG}-diagrams-v1.mp4')
   cuts.append(c);cursor=cutend
 # Exact 60/40 rounding is accomplished in the concluding shared example, not by stretching useful explanations.
 actual=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay');delta=round(body*.6)-actual
 for scene,purpose,minimum in [('08','interest',330),('08','summary',270),('01','flow',270)]:
  if delta<=0:break
  e=next(c for c in cuts if c['scene']==scene and c.get('purpose')==purpose)
  g=cuts[cuts.index(e)+1];n=min(delta,max(0,e['frames']-minimum))
  assert g['kind']=='independent-gameplay'
  e['endFrame']-=n;e['frames']-=n;g['startFrame']-=n;g['frames']+=n;delta-=n
 assert delta==0,'Select an observed demonstration instead of reducing a necessary explanation'
 # Preserve actual source cuts; editorial marks clear even across an internal source camera cut.
 detected={'mk8':[101.4,219.883333,350.95], 'sf6-match':[48.88,92.68,94.22,141.0], 'sf6-dynamic':[14.36435,32.849483]} # visually confirmed source transitions; ignore hit/boost flashes
 split=[]
 for c in cuts:
  if c['kind']=='explanation':split.append(c);continue
  a=c['sourceStart'];n=c['frames'];points=[0]+[round((x-a)*60) for x in detected.get(c['source'],[]) if a+.12<x<a+n/60-.12]+[n];points=sorted(set(points))
  for j,(lo,hi) in enumerate(zip(points,points[1:])):
   d=dict(c);d.update(id=c['id']+f'-{j+1}',startFrame=c['startFrame']+lo,endFrame=c['startFrame']+hi,frames=hi-lo,sourceStart=a+lo/60)
   split.append(d)
 cuts=split
 assets=LOCAL/'diagram-assets';assets.mkdir(exist_ok=True)
 for sid,(key,sec) in SHOT.items():
  f=assets/f'scene-{sid}.jpg'
  if not f.exists():subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-ss',str(sec),'-i',str(ROOT/bank[key]['file']),'-frames:v','1',str(f)],check=True)
 packed=0;diagrams=[]
 for c in cuts:
  if c['kind']=='explanation':
   c['renderedStartFrame']=packed;title,labels=TEXT[c['purpose']];shot=assets/f"scene-{c['scene']}.jpg"
   if c['purpose']=='steering':shot=LOCAL/'sources/mk8-official-035.jpg'
   elif c['purpose']=='acceleration':shot=LOCAL/'sources/mk8-official-034.jpg'
   spec={'id':c['id'],'scene':c['scene'],'purpose':c['purpose'],'title':title,'labels':labels,'frames':c['frames'],'startFrame':packed,'endFrame':packed+c['frames'],'sourceImage':'/@fs/'+str(shot.resolve()).replace('\\','/'),'globalStartFrame':c['startFrame'],'globalEndFrame':c['endFrame'],'pictureKind':'게임 스크린샷 + 원리 도식','variant':c.get('variant',0)}
   diagrams.append(spec);packed+=c['frames']
  elif c['frames']>=50:
   key=c['source'];dur=c['frames']/60;label={'mk8':'마리오 카트 8 디럭스 · 주행','sf6-match':'스트리트 파이터 6 · 대전','sf6-dynamic':'스트리트 파이터 6 · 다이내믹','hike-climbing':'A Short Hike · 오르기','hike-walk':'A Short Hike · 걷기','hike-glide':'A Short Hike · 활공'}[key]
   c['viewport']=[0,0,1920,880] # preserve the full native aspect while protecting bottom HUD from fixed captions
   c['marks']=[{'id':'game-name','shape':'path','t0':0,'t1':max(.02,dur-.01),'color':'yellow','thickness':6,'label':label,'labelPosition':[75,120],'points':[[75,190],[150,190]],'revealSeconds':.18}]
   def focus(name,rect,start,end,text,color='green'):
    if end<=start:return
    nx,ny,nw,nh=rect;x=178+round(nx*1564/1920);y=round(ny*880/1080);w=round(nw*1564/1920);h=round(nh*880/1080)
    c['marks'].append({'id':name,'shape':'rect','t0':start,'t1':min(end,dur-.08),'color':color,'thickness':7,'label':text,'labelPosition':[75,240],'x':x,'y':y,'w':w,'h':h,'revealSeconds':.3})
   if c['scene']=='01' and c['source']=='mk8' and c['sourceStart']==0:focus('kart',(740,400,440,640),.5,4.8,'내 손으로 이어가는 주행')
   if c['scene']=='02' and c['source']=='sf6-match' and 20<=c['sourceStart']<23:focus('health',(1040,26,650,70),.5,min(5,dur-.1),'공격 → 체력 변화','red')
   if c['scene']=='03' and c['source']=='sf6-match' and 60<=c['sourceStart']<69:focus('guard',(500,200,1000,650),max(.1,64-c['sourceStart']),min(dur-.1,69-c['sourceStart']),'방어할 기회 → 다음 행동','blue')
   if c['scene']=='04' and c['source']=='mk8' and c['sourceStart']>=75:focus('kart-input',(740,400,440,640),.4,min(4,dur-.1),'방향·가속·아이템')
   if c['scene']=='07' and c['source']=='hike-climbing':focus('climb',(800,200,500,580),1.5,min(5.7,dur-.1),'직접 올라가는 길')
 # Exact whole-cue visual corrections retain the initial validated packed master for every unchanged cut.
 for c in cuts:
  if c.get('purpose') in ('steering','turbo','acceleration'):
   revision='v3' if c['purpose']=='turbo' else 'v2'
   c['renderedSource']=f"projects/{SLUG}/production/local/batch-v1/rendered/{SLUG}-{c['purpose']}-{revision}.mp4"
   c['renderedStartFrame']=0
 plan={'schemaVersion':1,'slug':SLUG,'revision':'batch-v1','fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':total,'expectedGameplayShare':.6,'ratioToleranceFrames':1,'captionProtectedRect':[150,892,1784,1060],'annotationFontFile':'C:/Windows/Fonts/malgun.ttf','captionAliases':load(PROJECT/'script/batch-v1/caption-aliases.json'),'scenes':scenes,'cuts':cuts,'outputDir':f'projects/{SLUG}/production/local/batch-v1/edit','outputStem':SLUG+'-batch-v1-native-audio-v3','audio':{'sourceReviewPath':f'projects/{SLUG}/planning/audio-source-review.json','sourceReviewSha256':sha(PROJECT/'planning/audio-source-review.json'),'musicLufs':-28,'preserveGameAudio':True,'gameLufs':-23,'gameNarrationRelativeDb':-10,'targetLufs':-16,'voicePeakDbfs':-2.5,'music':{'path':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3','sha256':'06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08','licenseRecord':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md','title':'Nimbus','artist':'Eveningland'}},'notes':'Voice origins are exact PCM sample-aligned floats; visual chapter frames may overlap by one at fractional PCM boundaries. No voice trimming/stretching.'}
 save(PROJECT/'production/batch-v1/edit-plan.json',plan);save(LOCAL/'diagram-assets/packed-cues.json',{'slug':SLUG,'fps':60,'totalFrames':packed,'cues':diagrams})
 # Keep editable chapter modules and their packed-clock snapshot synchronized.
 mc=ROOT/'motion-canvas/src/projects'/SLUG/'batch-v1';mc.mkdir(parents=True,exist_ok=True)
 for scene in scenes:
  chapter=[x for x in diagrams if x['scene']==scene['id']]
  text="import {type View2D} from '@motion-canvas/2d';\nimport {explain,type Cue} from './visuals';\nconst cues: Cue[]="+json.dumps(chapter,ensure_ascii=False,indent=2)+";\nexport function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }\n"
  (mc/f"scene-{scene['id']}.tsx").write_text(text,'utf-8')
 save(LOCAL/'diagram-assets/module-clock-binding.json',{'packedFrames':packed,'packedCuesSha256':sha(LOCAL/'diagram-assets/packed-cues.json'),'modules':[{ 'path':relative(mc/f"scene-{scene['id']}.tsx"),'sha256':sha(mc/f"scene-{scene['id']}.tsx")} for scene in scenes]})
 print(json.dumps({'bodyFrames':body,'totalFrames':total,'gameplayFrames':sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay'),'diagramFrames':packed,'cuts':len(cuts)},ensure_ascii=False))
