"""D30 measured source clock to native-speed cut list and packed MC diagrams."""
from pathlib import Path
import json,math,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4]
SLUG='respect-player-time';PROJECT=ROOT/'projects'/SLUG;LOCAL=PROJECT/'production/local/batch-v1'
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def relative(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Native motion and speech-bound diagrams, not a duration-filler montage.
# scene-local end seconds, kind, native-source key/start or diagram purpose.
SPECS={
'01':[(9,'G','unpacking',87),(14,'E','thesis',0),(23,'G','unpacking',97),(None,'E','thesis',1)],
'02':[(8,'E','commitment',0),(17,'G','unpacking',25),(25,'E','calendar',0),(34,'G','unpacking',35),(39,'E','opportunity',0),(None,'G','unpacking',54)],
'03':[(9,'G','smash',4),(14,'E','return',0),(23,'G','smash',15),(29,'E','damage',0),(38,'G','smash',25),(42,'E','result',0),(None,'G','unpacking',149)],
'04':[(8,'G','unpacking',45),(12,'E','cost',0),(24,'G','powerwash',97),(28,'E','alternatives',0),(None,'G','powerwash',70)],
'05':[(8,'G','powerwash',85),(14,'E','choice',0),(23,'G','powerwash',124.5),(28,'E','wash',0),(36,'G','powerwash',140),(None,'E','cost',1)],
'06':[(14,'E','phone',0),(28,'G','smash',58.4),(37,'E','barriers',0),(None,'G','unpacking',154.5)],
'07':[(14,'G','unpacking',61),(24,'G','unpacking',120),(29,'E','action-loop',0),(None,'G','unpacking',132)],
'08':[(16.8,'E','timeline-before',0),(32.7,'E','timeline-after',0),(40,'G','smash',186),(46,'E','menu-control',0),(55,'G','unpacking',165),(None,'E','waiting',0)],
'09':[(9,'G','unpacking',176),(16,'E','comparison',0),(25,'G','unpacking',186),(30,'E','summary',0),(None,'G','smash',197)]}
TEXT={
 'thesis':('시간이 쌓이는 순서를 보자',['직접 행동','재미를 확인','다음 시도']),
 'commitment':('시작 전에 300시간을 약속한다면',['가정한 분량: 300시간','아직 재미는 모른다','먼저 보이는 부담']),
 'calendar':('하루 1시간이면 300일',['300시간 ÷ 하루 1시간','매일 해도 300일','설명용 가정']),
 'opportunity':('기회비용 · 고르지 못한 다른 기회',['다른 게임','영화·휴식·친구','같은 시간을 나눠 쓰기']),
 'return':('재미있어서 고르는 다음 한 판',['한 판의 재미','자발적인 다음 선택','뒤따라 쌓인 시간']),
 'damage':('누적 피해 퍼센트 · 점수와 다르다',['공격을 받는다','피해가 쌓인다','더 멀리 날아가기 쉬워진다']),
 'result':('재미 → 다음 선택 → 플레이 시간',['재미가 이유','계속은 선택','시간은 결과']),
 'cost':('시작 전의 시간은 비용',['돈과 함께 쓰는 시간','돌아오지 않는 오늘','그 시간의 가치']),
 'alternatives':('경쟁 상대는 여가 전체에 있다',['게임 한 판','영상·휴식','오늘 저녁 1시간']),
 'choice':('남는 시간에도 선택지는 많다',['대전의 즐거움','청소의 즐거움','내가 원하는 집중']),
 'wash':('내 행동이 표면을 바꾼다',['물줄기를 움직인다','지나간 때가 사라진다','깨끗한 면이 드러난다']),
 'phone':('손 닿는 곳의 낮은 시작 문턱',['짧은 글','사진과 영상','바로 시작할 선택지']),
 'barriers':('게임이 요구하는 준비를 살핀다',['시간 확보','플레이 환경','집중과 기억']),
 'appeal':('준비 뒤에 만날 재미를 보여준다',['우리 게임의 준비','문턱을 넘을 이유','실제로 할 만한 경험']),
 'fun-first':('플레이 시간보다 재미를 먼저',['좋아하는 행동','재미를 뒷받침','시간은 뒤따른다']),
 'action-loop':('선택 → 행동 → 확인',['물건을 본다','놓을 곳을 고른다','방의 변화를 확인']),
 'timeline-before':('설명용 시간표 · 직접 조작과 대기',['40 ÷ 60 = 2/3','조작 40초','대기 20초']),
 'timeline-after':('같은 놀이에서 불필요한 대기만 줄이기',['40 ÷ 50 = 80%','조작 40초 유지','대기 20초 → 10초']),
 'menu-control':('메뉴의 의미 있는 선택도 조작이다',['할 수 있는 선택','입력에 대한 반응','직접 개입하는 시간']),
 'waiting':('재미를 돕는 시간과 쓸모없는 대기',['의미 있는 연출','불필요한 전환 줄이기','기다리는 중의 선택']),
 'comparison':('같은 시간도 바라보는 쪽이 다르다',['제작자의 분량','플레이어의 삶','그 시간을 쓸 이유']),
 'summary':('그 시간을 쓰길 잘했다는 경험',['재미를 먼저','부담과 대기를 줄이기','선택한 시간을 존중'])}
SHOT={'01':('unpacking',91),'02':('unpacking',57),'03':('smash',20),'04':('smash',20),'05':('powerwash',110),'06':('smash',60),'07':('unpacking',146),'08':('unpacking',160),'09':('unpacking',190)}
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
    src=bank[key];c.update(source=key,game=key,sourceFile=src['file'],sourceSha256=src['sha256'],sourceStart=offset,sourceAttribution=f"{src['creator']} | {src['url']}",sourceAudioEnabled=(key!="unpacking"),sourceAudioReviewStatus="reviewed-native-retain" if key!="unpacking" else "reviewed-early-promo-mix-exception",audioRightsReview="projects/respect-player-time/planning/audio-source-review.json",onScreenAttributionRequired=False)
   else:c.update(purpose=key,variant=offset,renderedSource=f'projects/{SLUG}/production/local/batch-v1/rendered/{SLUG}-diagrams-v2.mp4')
   cuts.append(c);cursor=cutend
 # Exact 60/40 rounding is accomplished in the concluding shared example, not by stretching useful explanations.
 actual=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay');delta=round(body*.6)-actual
 for scene,purpose,minimum in [('09','comparison',300),('09','summary',240),('07','fun-first',240)]:
  if delta<=0:break
  e=next(c for c in cuts if c['scene']==scene and c.get('purpose')==purpose)
  g=cuts[cuts.index(e)+1];n=min(delta,max(0,e['frames']-minimum))
  assert g['kind']=='independent-gameplay'
  e['endFrame']-=n;e['frames']-=n;g['startFrame']-=n;g['frames']+=n;delta-=n
 assert delta==0,'Select an observed demonstration instead of reducing a necessary explanation'
 # Preserve actual source cuts; editorial marks clear even across an internal source camera cut.
 detected={'unpacking':[16.2,113.55], 'smash':[37.6,44.4,57.1,78.2,97.2,105.2,164.5,171.2,176.8,183.1,192.4,195.5,218.0], 'powerwash':[]} # source edit transitions: refine during final cut pixel review
 split=[]
 for c in cuts:
  if c['kind']=='explanation':split.append(c);continue
  a=c['sourceStart'];n=c['frames'];points=[0]+[round((x-a)*60) for x in detected.get(c['source'],[]) if a+.12<x<a+n/60-.12]+[n];points=sorted(set(points))
  for j,(lo,hi) in enumerate(zip(points,points[1:])):
   d=dict(c);d.update(id=c['id']+f'-{j+1}',startFrame=c['startFrame']+lo,endFrame=c['startFrame']+hi,frames=hi-lo,sourceStart=a+lo/60)
   split.append(d)
 cuts=split
 # Retain only the actual mission/party choices; remove the source's black load transitions.
 menu_a=next(c for c in cuts if c['id']=='08-03-1');menu_b=next(c for c in cuts if c['id']=='08-03-2')
 boundary=menu_a['startFrame']+99
 menu_a.update(sourceStart=182.25,frames=99,endFrame=boundary)
 menu_b.update(sourceStart=184.4,startFrame=boundary,frames=menu_b['endFrame']-boundary)
 assets=LOCAL/'diagram-assets';assets.mkdir(exist_ok=True)
 for sid,(key,sec) in SHOT.items():
  f=assets/f'scene-{sid}.jpg'
  if not f.exists():subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-ss',str(sec),'-i',str(ROOT/bank[key]['file']),'-frames:v','1',str(f)],check=True)
 packed=0;diagrams=[]
 for c in cuts:
  if c['kind']=='explanation':
   c['renderedStartFrame']=packed;title,labels=TEXT[c['purpose']];shot=assets/f"scene-{c['scene']}.jpg"
   if c['purpose']=='timeline-before':
    pass # default screenshot is dimmed behind the illustrative40/20 time bar
   elif c['purpose']=='timeline-after':
    pass
   spec={'id':c['id'],'scene':c['scene'],'purpose':c['purpose'],'title':title,'labels':labels,'frames':c['frames'],'startFrame':packed,'endFrame':packed+c['frames'],'sourceImage':'/@fs/'+str(shot.resolve()).replace('\\','/'),'globalStartFrame':c['startFrame'],'globalEndFrame':c['endFrame'],'pictureKind':'게임 스크린샷 + 원리 도식','variant':c.get('variant',0),'metrics':({'control':40,'wait':20,'total':60,'share':'2/3'} if c['purpose']=='timeline-before' else {'control':40,'wait':10,'total':50,'share':'80%'} if c['purpose']=='timeline-after' else None)}
   if c['purpose']=='timeline-before':spec['stageCueTimes']=[8.2,10.9,14.8]
   elif c['purpose']=='timeline-after':spec['stageCueTimes']=[0,3.5,9.1]
   diagrams.append(spec);packed+=c['frames']
  elif c['frames']>=50:
   key=c['source'];dur=c['frames']/60;label={'unpacking':'Unpacking · 초기 개발 빌드','smash':'슈퍼 스매시브라더스 얼티밋','powerwash':'PowerWash Simulator · 표면 청소'}[key]
   c['viewport']=[0,0,1920,880] # preserve the full native aspect while protecting bottom HUD from fixed captions
   c['marks']=[{'id':'game-name','shape':'path','t0':0,'t1':max(.02,dur-.01),'color':'yellow','thickness':6,'label':label,'labelPosition':[75,120],'points':[[75,190],[150,190]],'revealSeconds':.18}]
   if key=='powerwash':
    c['marks'][0]['labelPosition']=[600,110];c['marks'][0]['points']=[[600,180],[675,180]]
    c['protectedRects']=[[178,0,560,155],[1480,0,1742,80],[198,295,457,347]]
   def focus(name,rect,start,end,text,color='green'):
    if end<=start:return
    nx,ny,nw,nh=rect;x=178+round(nx*1564/1920);y=round(ny*880/1080);w=round(nw*1564/1920);h=round(nh*880/1080)
    c['marks'].append({'id':name,'shape':'rect','t0':start,'t1':min(end,dur-.08),'color':color,'thickness':7,'label':text,'labelPosition':([75,190] if key=='powerwash' else [75,240]),'x':x,'y':y,'w':w,'h':h,'revealSeconds':.3})
   if c['scene']=='01' and c['source']=='unpacking':focus('shelf',(1290,370,310,460),.3,min(4.8,dur-.1),'상자 → 내가 고른 선반')
   if c['scene']=='03' and c['source']=='smash' and 15<=c['sourceStart']<24:focus('damage',(530,895,210,155),max(.1,20-c['sourceStart']),min(dur-.1,24-c['sourceStart']),'누적 피해 · 점수와 다르다','blue')
   if c['scene']=='05' and c['source']=='powerwash':focus('cleaning',(550,300,700,550),.3,min(3,dur-.1),'물줄기가 지나간 표면')
   if c['scene']=='07' and c['source']=='unpacking' and c['sourceStart']>=120:focus('placement',(680,100,330,340),.4,min(4.5,dur-.1),'선택 → 배치 → 방의 변화')
   if c['scene']=='08' and c['source']=='smash':focus('menu-choice',(70,80,1400,690),.3,min(4.6,dur-.1),'메뉴의 의미 있는 선택도 조작')
 # Two small corrected purpose renders retain every unaffected v2 diagram cue.
 for c in cuts:
  if c.get('purpose') in ('wash','menu-control'):
   c['renderedSource']=f"projects/{SLUG}/production/local/batch-v1/rendered/{SLUG}-{c['purpose']}-v3.mp4"
   c['renderedStartFrame']=0
 plan={'schemaVersion':1,'slug':SLUG,'revision':'batch-v1','fps':60,'width':1920,'height':1080,'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':total,'expectedGameplayShare':.6,'ratioToleranceFrames':1,'captionProtectedRect':[150,892,1784,1060],'annotationFontFile':'C:/Windows/Fonts/malgun.ttf','captionAliases':load(PROJECT/'script/batch-v1/caption-aliases.json'),'scenes':scenes,'cuts':cuts,'outputDir':f'projects/{SLUG}/production/local/batch-v1/final-v3','captionsAss':f'projects/{SLUG}/production/local/batch-v1/edit/captions.ko.ass','outputStem':SLUG+'-batch-v1-final-v3','audio':{'sourceReviewPath':f'projects/{SLUG}/planning/audio-source-review.json','sourceReviewSha256':sha(PROJECT/'planning/audio-source-review.json'),'musicLufs':-28,'preserveGameAudio':True,'gameLufs':-23,'gameNarrationRelativeDb':-10,'targetLufs':-16,'voicePeakDbfs':-2.5,'music':{'path':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3','sha256':'06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08','licenseRecord':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md','title':'Nimbus','artist':'Eveningland'}},'notes':'Voice origins are exact PCM sample-aligned floats; visual chapter frames may overlap by one at fractional PCM boundaries. No voice trimming/stretching.'}
 save(PROJECT/'production/batch-v1/edit-plan.json',plan);save(LOCAL/'diagram-assets/packed-cues.json',{'slug':SLUG,'fps':60,'totalFrames':packed,'cues':diagrams})
 # Keep editable chapter modules and their packed-clock snapshot synchronized.
 mc=ROOT/'motion-canvas/src/projects'/SLUG/'batch-v1';mc.mkdir(parents=True,exist_ok=True)
 for scene in scenes:
  chapter=[x for x in diagrams if x['scene']==scene['id']]
  text="import {type View2D} from '@motion-canvas/2d';\nimport {explain,type Cue} from './visuals';\nconst cues: Cue[]="+json.dumps(chapter,ensure_ascii=False,indent=2)+";\nexport function* run(view:View2D){for(const cue of cues)yield* explain(view,cue); }\n"
  (mc/f"scene-{scene['id']}.tsx").write_text(text,'utf-8')
 save(LOCAL/'diagram-assets/module-clock-binding.json',{'packedFrames':packed,'packedCuesSha256':sha(LOCAL/'diagram-assets/packed-cues.json'),'modules':[{ 'path':relative(mc/f"scene-{scene['id']}.tsx"),'sha256':sha(mc/f"scene-{scene['id']}.tsx")} for scene in scenes]})
 print(json.dumps({'bodyFrames':body,'totalFrames':total,'gameplayFrames':sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay'),'diagramFrames':packed,'cuts':len(cuts)},ensure_ascii=False))
