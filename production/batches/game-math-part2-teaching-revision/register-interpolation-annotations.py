"""Scoped draft registry; every final moving source stays pending until reviewed."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
scenes={};notes=[]
messages={'IG01':(2,'계산 예시45° ≠ 이 화면의 측정 각도'),'IG02':(1,'이동 거리 ≠ 자세 사이의 비율 t'),'IG03':(1,'방향을 수로 읽기 전 기준축을 정함'),'IG04':(2,'같은 대상의 방향 벡터로 결과 비교'),'IG05':(1,'표현 변환 ≠ 추가로 회전시키는 동작'),'IG06':(3,'작은 수 검산은 축·카메라를 정한 예시'),'IG07':(1,'현재 자세 ≠ 누적 회전 이력'),'IG08':(1,'화면 기울기 ≠ 게임세계3D 각도'),'IG09':(0,'한 화면 선만으로3D 회전축이 정해지지 않음'),'IG10':(1,'저장값의 단위 길이 ≠ 물체·화면 길이'),'IG11':(2,'같은 자세 → 편집·보간·벡터 적용')}
blue_start={'IG01':1,'IG02':0,'IG03':0,'IG04':0,'IG05':2,'IG06':1,'IG07':2,'IG08':0,'IG09':1,'IG10':0,'IG11':0}
for row in read(B/'interpolation-game-insertions.json')['scenes']:
    ident=row['id'];sources=[f'production/batches/game-math-part2-teaching-revision/interpolation-tracks/{ident.lower()}-{i+1}-torso.json' for i in range(len(row['intervals']))]
    blue=[x.replace('-torso.json','-board.json') for x in sources]
    scenes[ident]={'landmarkSources':sources,'blueLandmarkSources':blue,'revealAtLine':0,'redAtLine':0,'blueAtLine':blue_start[ident],'redLabel':'몸체 방향','blueLabel':'보이는 보드 방향','showScreenReference':False,'showProjectedAngle':False,'showWheel':ident!='IG08','mathNotePosition':[28,20],'labelOutline':3.5,'movingPixelApproval':False}
    # Explicitly rejected detector spans: shin, overlong shadow and a foreign NPC.
    rejected={'IG02':[[109.5,110.7]],'IG07':[[144,152.6],[198.3,202.2]],'IG08':[[344.5,356],[525,537.7]],'IG09':[[543.5,544.3],[546.7,548.5]],'IG06':[[584.1,586.1]],'IG10':[[105,107.5]]}
    scenes[ident]['blueHideSourceIntervals']=rejected.get(ident,[])
    notes.append({'scene':ident,'line':messages[ident][0],'text':messages[ident][1],'geometry':'separately observed body/board projections, revealed in current narration order; no game-world values inferred'})
old_notes={'02':(1,'앞쪽·카메라·길을 구분 / 중간 자세가 필요'),'05':(1,'두 끝 자세 ≠ 지나온 회전·이동 이력'),'08':(1,'서로 다른 발췌 / 화면 선은 계산 축과 구분'),'11':(2,'HUD의 주행 속도 ≠ 몸체의 각속도'),'14':(0,'몸체 방향·화면 방향 구분 / 기어 컷은 별도'),'17':(1,'같은 자세의 표현 변환 ≠ 새 회전 추가'),'20':(0,'차체·도로 기울기 / 내부 저장값을 읽은 것 아님'),'23':(1,'서로 다른 발췌 / 방향 검산과 충돌 검사는 별도')}
for ident,(line,text) in old_notes.items():
    name=f'original-{ident}-'+('flight' if ident in ['14','17'] else 'car')+'.json'
    scenes[ident]={'landmarks':f'production/batches/game-math-part2-teaching-revision/interpolation-tracks/{name}','revealAtLine':0,'redAtLine':0,'blueAtLine':1,'redLabel':('날개 가로 투영선' if ident=='17' else '보이는 몸체선' if ident=='14' else '차체 중심 투영선'),'blueLabel':'차체 가로 투영선','showWheel':ident not in ['14','17'],'showScreenReference':False,'showProjectedAngle':False,'mathNotePosition':[407,104],'labelOutline':3.5,'movingPixelApproval':False}
    notes.append({'scene':ident,'line':line,'text':text,'geometry':'directly observed visible body projections; reset at cuts and suppress interior/hidden objects; no engine/world calibration'})
write(B/'interpolation-annotation-tracks.json',{'scope':'Editable observed draft tracks; moving review is independent','scenes':scenes})
write(B/'interpolation-on-footage-math.json',{'scope':'Small narration-matched reminders above fixed bottom captions','classification':'action-led moving footage only; no frozen/diagram quota double counting','numbers':'Defined lecture examples, never measured game-world/engine values','labels':notes})
print('Nineteen actual scene registries saved; all moving approvals remain false.')
