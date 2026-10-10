"""Preserve older takes; repair new endings and add two observed closings."""
from pathlib import Path
import json,copy,re,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
slug='game-math-quaternion-teaching-additions-v5';P=ROOT/'projects'/slug
assert not (ROOT/f'shared/output/narration/{slug}').exists(),'Frozen audio exists; make a separate version'
old={lang:read(ROOT/f'projects/game-math-quaternion-teaching-additions-v4/script/narration.{lang}.json')['scenes'] for lang in ['ko','en']}
refs={s['additionId']:s for s in read(B/'quaternion-v4-tts-map.json')}
items=[];overrides=[]
for ident in ['B08','B23','GA06','GA04']:
 at=int(refs[ident]['ttsScene'])-1
 # Only additions: sentence boundaries become complete line batches. All words retained.
 ko_source=old['ko'][at]['lines'];en_source=old['en'][at]['lines']
 if ident=='GA04':
  ko_source=[line.replace('스키','바퀴') for line in ko_source]
  en_source=[line.replace('skis','wheels').replace('ski direction','visible wheel direction') for line in en_source]
 ko=[x for line in ko_source for x in re.split(r'(?<=[.!?])\s+',line)]
 en=[x for line in en_source for x in re.split(r'(?<=[.!?])\s+',line)]
 assert len(ko)==len(en),(ident,ko,en)
 assert ' '.join(ko)==' '.join(ko_source)
 s={'id':ident,'title':old['ko'][at]['title'],'ko':ko,'en':en,'sourceType':refs[ident]['sourceType'],'retakeOf':{'project':'game-math-quaternion-teaching-additions-v4','scene':refs[ident]['ttsScene']}}
 items.append(s);overrides.append(s)
closing=[
 {'id':'GA10','episode':1,'after':'13','title':'되돌리기에서 두 회전의 합성으로','sourceId':'4Odvp_TIeQU','intervals':[[522,539]],'maximumSeconds':17,
  'ko':['역원은 회전만 상쇄했죠. 빨간 몸체 선과 이동을 따로 보세요.','그럼 두 회전을 잇는 계산은요? 다음 편에서 곱으로 확인합니다.'],
  'en':['An inverse cancelled rotation. Read the red torso line separately from traveled position.','How do we connect two rotations? The next episode verifies their product.'],
  'annotation':{'landmarks':'visible upper back and waist; projected body direction','revealDuringLine':0}},
 {'id':'GB07','episode':2,'after':'25','title':'벡터의 결과에서 중간 자세의 질문으로','sourceId':'4Odvp_TIeQU','intervals':[[539,546],[546,552]],'maximumSeconds':13,'sourceGroupStartsAtLines':[0,1],
  'ko':['벡터를 돌렸죠. 비행으로 바뀝니다.','빨간 날개 선을 보세요. 중간 자세는 어떻게 만들까요?'],
  'en':['We rotated the vector. The equipment changes to flight.','Observe the red wing line. How do we construct an intermediate orientation?'],
  'annotation':{'landmarks':'visible wing tips after equipment change; hide through transition','revealDuringLine':1}}
]
for s in closing:
 assert sum(map(len,s['ko']))/5.4+.6<=s['maximumSeconds']
 items.append(dict(s,sourceType='actual-footage'))
write(B/'quaternion-game-closings-v5.json',{'scope':'two purposeful closing observations; no original narration replaced','scenes':closing,'movingRenderApproval':False})
write(B/'quaternion-retakes-v5.json',{'overrides':overrides,'newEndingRetakeWordsPreserved':['B08','B23','GA06'],'newGA04GearWordsCorrected':'Source317–350 shows bicycle wheels. Only this addition replaces skis with wheels; original26 scenes and v4 script/audio preserved.','baselineChanged':False})
mapping=[{'ttsScene':f'{i:02}','additionId':s['id'],'sourceType':s['sourceType'],'retakeOf':s.get('retakeOf'),'after':s.get('after')} for i,s in enumerate(items,1)]
for lang in ['ko','en']:write(P/f'script/narration.{lang}.json',{'project':slug,'language':lang,'status':'additions-only-authorized','scenes':[{'id':ref['ttsScene'],'title':s['title'],'lines':s[lang]} for s,ref in zip(items,mapping)]})
m=copy.deepcopy(read(ROOT/'projects/game-math-quaternion-teaching-additions-v4/project.json'))
m=json.loads(json.dumps(m).replace('game-math-quaternion-teaching-additions-v4',slug));m.update(slug=slug,title='쿼터니언 연결 해설 끝맺음과 두 편의 관찰 결론')
m['tts'].update(renderMode='line',lineGapSeconds=.28);m['preservation']['v4AudioOverwritten']=False
write(P/'project.json',m);write(B/'quaternion-v5-tts-map.json',mapping)
write(B/'quaternion-v5-pretts-audit.json',{'original26ScenesAnd155KoLinesExact':read(B/'quaternion-episode-flow-audit.json')['all26OriginalScenesAnd155KoLinesExact'],'scriptSha256':{lang:hashlib.sha256((P/f'script/narration.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']},'jobs':len(items),'lineBatchReason':'Repeated incomplete endings of three additions, plus one new-only source-gear correction before any v5 synthesis; preserve approved voice/unchanged quality thresholds','currentHashAsrAndFinalPixelsPassed':False})
write(B/'closing-source-playback-comparison.json',{'playedAt':'2026-10-10','normalSpeedMutedNativePlayback':True,'candidates':[
 {'id':'V','source':'4Odvp_TIeQU','interval':[522,539],'ended':True,'chosenFor':'GA10','before':'red-vest rider banked at gate','action':'riding across raised route and bends','after':'more upright visible back near next crest','camera':'follow camera changes with route; HUD and brief source dialogue stay at edges/bottom','reason':'Same clear torso and forward travel separate orientation from translation before composition question','gearLabel':'do not infer bicycle/board internals from unclear wheels'},
 {'id':'W','source':'_dw9jjRpanA','interval':[91,108],'ended':True,'chosen':False,'reason':'Early equipment/silhouette change distracts from the first closing inverse-versus-translation comparison'},
 {'id':'X','source':'4Odvp_TIeQU','interval':[539,552],'ended':True,'chosenFor':'GB07','before':'rider travels toward crest','action':'equipment changes to winged flight near546','after':'wide wing/body silhouette descends through gate while camera banks','reason':'Continuous visible orientation change creates the next interpolation question; flight line revealed only after transition','camera':'moving projection, not a measured world rotation; source dialogue may occur and final caption clearance needs review'}],
 'priorUse':'These selected intervals are outside original quaternion source intervals and the other new additions','rights':'Preserve baseline source records; human/game-IP review remains pending','annotationApproval':False})
print(json.dumps({'jobs':len(items),'lines':sum(len(s['ko']) for s in items),'extraActualCapacity':30,'originalChanged':False}))
