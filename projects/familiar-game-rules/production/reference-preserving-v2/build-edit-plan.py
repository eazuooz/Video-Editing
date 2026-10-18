"""Measured, concept-matched native-speed edit; no estimated voice timing."""
from pathlib import Path
import copy,hashlib,json,math
R=Path(__file__).resolve().parents[4];P=R/'projects/familiar-game-rules';H=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2';N=R/'shared/output/narration/familiar-game-rules/reference-preserving-v2';M=R/'motion-canvas/src/projects/familiar-game-rules/revision-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
timing=read(N/'source-scene-timings.json');rows=timing['scenes'];ids=[s['id'] for s in rows]
O={s['id']:s['sourceOrigin'] for s in rows};E={s['id']:s['duration'] for s in rows};B={s['id']:s['paragraphStarts'] for s in rows}
body=math.ceil((rows[-1]['sourceOrigin']+rows[-1]['duration'])*60-1e-7);target=round(body*.6)
F=lambda sid,t:120+round((O[sid]+t)*60)
sources={s['key']:s for s in read(H/'source-selection.json')['sources']}
# Reserved intervals prevent a montage/prompt/number example from being spent
# as generic background first. Every interval is unique and at native speed.
pools={
 'rage':[['rage2-fight',5,38],['rage2-fight',83,120],['rage2-combat',0,10],['rage2-combat',20,27],['rage2-combat',43,53]],
 'apex':[['apex',23,28],['apex',40,57],['apex',64,83],['apex',96,106],['apex',111,123],['apex',124,147],['apex',157,180]],
 'fps':[['cod-bo7-action',3,12],['halo-action',10,20],['farcry6',5,10],['farcry6',17,21],['titanfall2',4,10],['titanfall2',17,23],['battlefield1-early',8,15]],
 'ammo':[['apex',57,64],['rage2-fight',0,5],['battlefield1-early',0,5]],
 'prompt':[['apex',34,40],['rage2-combat',10,20]],
 'remap':[['sf6-bindings',13,24],['tales-controls',10.05,16],['sf6-permitted-menu',7.05,12]],
 'choice':[['smash-controls-ggrc',50,68],['smash-controls-ggrc',32,38],['smash-controls-ggrc',48,50],['smash-gameplay-cache',60,89.5]],
 'walk':[['smash-running-sprinkles',0,5.1]],
 'atomic':[['atomic-runner-kawaii-gameplay',0,45]],
}
cuts=[]
def add(sid,a,b,kind,**kw):
 start,end=F(sid,a),F(sid,b)
 if b==E[sid]:end=120+(body if sid==ids[-1] else round(O[ids[ids.index(sid)+1]]*60))
 if end<=start:return
 c=dict(scene=sid,startFrame=start,endFrame=end,frames=end-start,kind=kind,**kw);cuts.append(c);return c
def diagram(sid,a,b,kind,cues=None):
 return add(sid,a,b,'explanation',visual=kind,renderer='Motion Canvas',cues=cues or [0,1,2,3,4,5],implementationKind='authored illustration with inspected independent-gameplay stills')
def film(sid,a,b,pool,label):
 cursor,end=F(sid,a),F(sid,b)
 if b==E[sid]:end=120+(body if sid==ids[-1] else round(O[ids[ids.index(sid)+1]]*60))
 while cursor<end:
  assert pools[pool],('Inspected concept-matched source capacity exhausted',sid,pool,(end-cursor)/60)
  key,lo,hi=pools[pool][0];capacity=math.floor((hi-lo)*60+1e-6);count=min(capacity,end-cursor)
  if count<=0:pools[pool].pop(0);continue
  cuts.append(dict(scene=sid,startFrame=cursor,endFrame=cursor+count,frames=count,kind='independent-gameplay',source=key,sourceStart=lo,label=label,marks=[],playbackSpeed=1,loop=False))
  cursor+=count;pools[pool][0][1]=lo+count/60
  if count==capacity:pools[pool].pop(0)
def local(sid,a,indices):return [max(0,B[sid][i]-a) for i in indices]

film('01',0,E['01']*.5,'rage','처음 보는 공간에서 이동하고 무기를 사용')
film('01',E['01']*.5,E['01'],'apex','다른 게임에서도 대상을 바라보고 이동')
film('02',0,B['02'][2],'rage','일인칭 시점과 화면 가운데 조준점')
diagram('02',B['02'][2],B['02'][3],'controller',[0,1,2,3,4])
film('02',B['02'][3],E['02'],'apex','기기와 배치가 달라도 비교 가능한 행동 역할')
film('03',0,B['03'][2],'rage','황폐한 공간의 위치와 적을 보고 판단')
film('03',B['03'][2],E['03'],'apex','팀과 상대의 위치, 능력을 쓰는 순간')
film('04',0,B['04'][1],'rage','처음 보는 사람에게 이름과 반응을 짚어 줄 조준점·무기 정보')
film('04',B['04'][1],B['04'][2],'fps','익숙한 조작 위에서 달라진 게임 규칙을 확인')
span=(B['04'][3]-B['04'][2])/5
for i,(key,sourceStart) in enumerate([('cod-bo7-action',0),('halo-action',7),('farcry6',2),('titanfall2',1),('battlefield1-early',5)]):
 assert span<=3.01,('Montage narration longer than reserved inspected source',span)
 add('04',B['04'][2]+i*span,B['04'][2]+(i+1)*span,'independent-gameplay',source=key,sourceStart=sourceStart,label='겨누기·발사·탄약의 공통 행동',marks=[],playbackSpeed=1,loop=False)
film('04',B['04'][3],B['04'][4],'ammo','발사 전후 탄창의 남은 탄약 숫자')
film('04',B['04'][4],B['04'][5],'prompt','아는 행동의 입력을 짧게 알려 주는 실제 화면 안내')
film('04',B['04'][5],E['04'],'fps','경험으로 이어지는 조작과 화면 반응')
film('05',0,B['05'][1],'fps','여러 게임에 이어지는 익숙한 약속')
diagram('05',B['05'][1],E['05'],'standard',[0,0,B['05'][2]-B['05'][1],B['05'][3]-B['05'][1]])
menuSpan=B['06'][1]/3
for i,(key,ss,crop) in enumerate([('sf6-permitted-menu',4,[0,150,1120,630]),('tales-controls',7,None),('acc-bindings',0,[0,0,1600,1080])]):
 assert menuSpan<=3.05
 add('06',i*menuSpan,(i+1)*menuSpan,'independent-gameplay',source=key,sourceStart=ss,sourceCrop=crop,label='실제 행동·입력 설정 항목',marks=[],playbackSpeed=1,loop=False)
film('06',B['06'][1],B['06'][2],'remap','실제 행동에 연결된 입력을 선택하는 메뉴')
diagram('06',B['06'][2],B['06'][4],'remap',[0,0,4,B['06'][3]-B['06'][2],B['06'][4]-B['06'][2]])
film('06',B['06'][4],E['06'],'remap','실제 행동·입력 설정 항목; 저장 완료를 주장하지 않음')
choiceEnd=min(B['07'][3],26.)
film('07',0,choiceEnd,'choice','플레이어가 입력 배치를 선택하고 확인할 실제 행동')
diagram('07',choiceEnd,E['07'],'preference',[0,0,0,max(0,B['07'][3]-choiceEnd)])
film('08',0,5.1,'walk','실제 마리오의 걷는 자세에서 달리는 자세로 변화')
diagram('08',5.1,E['08'],'analog',[0,*[max(0,x-5.1) for x in B['08'][1:]]])
diagram('09',0,B['09'][3],'limits',B['09'])
film('09',B['09'][3],E['09'],'atomic','낯선 조작의 예로 이어지는 실제 게임 행동')
film('10',0,B['10'][1],'atomic','실제 달리기·점프·원형 탄환 공격')
diagram('10',B['10'][1],B['10'][3],'unusual',[0,0,3,B['10'][3]-B['10'][1],B['10'][3]-B['10'][1]])
film('10',B['10'][3],E['10'],'atomic','낯선 조작의 배움과 부담을 비교할 실제 게임 행동')

actual=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')
summary=(target-actual)/60
assert 3<=summary<=E['11']-2,('Revisit semantic allocation, never pad or shorten useful explanation',summary,E['11'])
film('11',0,summary,'apex','이미 본 공통 역할을 다른 미사용 장면에서 되짚기')
diagram('11',summary,E['11'],'conclusion',[0,0,0,max(0,B['11'][3]-summary)])
delta=target-sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')
if delta:
 a,b=cuts[-2:];assert abs(delta)<=2 and a['kind']=='independent-gameplay' and b['kind']=='explanation'
 a['frames']+=delta;a['endFrame']+=delta;b['frames']-=delta;b['startFrame']+=delta

mc=0;modules=[]
for i,c in enumerate(cuts):
 c['id']=f'cut{i:02}';c['clearAtSourceCut']=True
 if c['kind']=='independent-gameplay':
  if c['id']=='cut28':
   c.update(source='sf6-bindings',sourceStart=8);c.pop('sourceCrop',None)
  if c['id']=='cut35':
   c.update(source='acc-bindings',sourceStart=3.05,sourceCrop=[0,0,1600,1080])
  s=sources[c['source']];c.update(sourceFile=s['media']['path'],sourceSha256=s['media']['sha256'],sourceUrl=s['sourceUrl'],game=s['game'],credit=dict(text=s['game']+' · '+s['uploader'],position=[24,16],fontSize=23),viewport=[0,0,1920,900],sourceAudioEnabled=c['source']=='apex',audioExclusionReason=None if c['source']=='apex' else 'Inseparable source music/commentary not separately cleared; preserve original bytes locally and use approved quiet music.',editorialUse='Limited concept-matched quotation with original educational commentary; recorder and publisher conditions recorded separately.')
  if c['source']=='sf6-permitted-menu':c['sourceCrop']=[0,150,1120,630]
 else:
  c.update(renderedSource='shared/output/motion-canvas/familiar-controls-production-v2b.mp4',renderedStartFrame=mc,mcStartFrame=mc,mcEndFrame=mc+c['frames']);mc+=c['frames']
  c['cues']=[min(max(0,x),max(0,c['frames']/60-.1)) for x in c['cues']]
  if c['visual']=='remap':c.update(renderedSource='shared/output/motion-canvas/familiar-controls-remap-correction-v2.mp4',renderedStartFrame=0)
  name='production-'+c['id'];modules.append(name)
  credits={'controller':"RAGE2: JVGS · Apex: EA 공식 설정",'remap':'Avataryaya · Magic Game World · Gopher Community Racing','analog':'Jb Sprinkles · Nintendo','unusual':'Kawaii Games · Data East','standard':'개념도: 얌얌코딩','newcomer':'Apex Legends · Silent Gaming','preference':'Street Fighter6 · Avataryaya','conclusion':'Avataryaya · Kawaii Games'}
  # A quarter-frame margin avoids floating-point endpoint truncation.
  # Verified for every current scene; export range is exactly 0..mcFrames-1.
  (M/(name+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(c['visual'])+','+json.dumps(dict(duration=(c['frames']-.75)/60,cues=c['cues'],retainMismatch=c['visual']=='remap',credit=credits.get(c['visual'],'실제 화면과 출처: 제작 설계표')),ensure_ascii=False)+');});\n',encoding='utf-8')
for a,b in zip(cuts,cuts[1:]):assert a['endFrame']==b['startFrame'],(a,b)
for key in sources:
 spans=sorted((c['sourceStart'],c['sourceStart']+c['frames']/60,c['id']) for c in cuts if c.get('source')==key)
 for a,b in zip(spans,spans[1:]):assert b[0]>=a[1]-.001,('Repeated source interval',key,a,b)
plan=dict(revision='reference-preserving-v2',timing='current-complete-ASR-and-signal-pause-aligned',fps=60,width=1920,height=1080,bodyFrames=body,totalFrames=body+720,actualFrames=target,explanationFrames=body-target,mcFrames=mc,expectedGameplayShare=.6,ratioToleranceFrames=1,outputDir=L.relative_to(R).as_posix()+'/edit',outputStem='familiar-game-rules',captionAliases=read(P/'script/reference-preserving-v2/caption-aliases.json'),scenes=[dict(id=s['id'],voiceStart=2+s['sourceOrigin'],voiceDuration=s['duration'],startFrame=120+math.floor(s['sourceOrigin']*60+1e-7),endFrame=120+math.ceil((s['sourceOrigin']+s['duration'])*60-1e-7),paragraphStarts=s['paragraphStarts']) for s in rows],cuts=cuts,audio=dict(targetLufs=-16,voicePeakDbfs=-2.5,musicLufs=-31,gameRmsDbfs=-33,matchSceneRms=False,preserveGameAudio=True,music=dict(path='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',sha256='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08',licenseRecord='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md',title='Nimbus',artist='Eveningland')),narrationPcmPreserved=True,sourceIntervalsUnique=True,noLoops=True,noSlowdown=True,annotationsReview='pending current native cut target entry and moving QA',humanWholeListening='pending',youtubeUploadAuthorized=False)
plan['captionAliases'].update({'레이지2':'레이지투','1인칭':'일인칭','6':'식스','De':'디','facto':'팩토','standard':'스탠더드','.25':'점이오','.75':'점칠오','0':'영','1':'일','3':'삼','4':'사','A':'에이','B':'비','X':'엑스'})
plan['motionCanvasFrameConvention']='Endpoint=(requestedFrames-.75)/60; all8scene spans verified by Renderer metadata; exact export range0..11416.'
annotation_file=H/'source-annotations.json'
if annotation_file.exists():
 by_id={c['id']:c for c in cuts}
 for row in read(annotation_file)['annotations']:
  c=by_id[row['cutId']]
  assert (c['sourceSha256'],c['sourceStart'],c['frames'],c['viewport'],c.get('sourceCrop'))==(row['sourceSha256'],row['sourceStartSeconds'],row['cutFrames'],row['viewport'],row.get('sourceCrop')),row['cutId']
  c.setdefault('marks',[]).append(row['mark'])
 plan['annotationSource']=annotation_file.relative_to(R).as_posix()
 plan['annotationsReview']='Native targets and every visible frame geometry checked; current moving encoded pixels pending.'
(H/'edit-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'production-project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import s{i} from './{name}?scene';" for i,name in enumerate(modules))+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(len(modules)))+']});\n',encoding='utf-8')
print(json.dumps(dict(duration=plan['totalFrames']/60,actual=target/60,explanation=(body-target)/60,summaryActual=summary,cuts=len(cuts),sceneDurations=E),indent=2))
