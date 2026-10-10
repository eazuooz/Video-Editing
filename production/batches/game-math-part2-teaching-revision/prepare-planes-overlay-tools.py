"""Reuse the reviewed source-map method with explicit plane teaching semantics."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
source=(B/'create-lines-overlay.py').read_text(encoding='utf8').replace('lines-annotation-tracks.json','planes-annotation-tracks.json')
source=source.replace("spoken('빨간',","spoken(spec.get('redKeyword','빨간'),").replace("spoken('파란',","spoken(spec.get('blueKeyword','파란'),").replace("spoken('청록',","spoken(spec.get('tealKeyword','청록'),")
needle=" note_start=starts[spec.get('mathNoteAtLine',0)];nx,ny=spec.get('mathNotePosition',[390,42])"
insert=""" track_reveals={}
 for track in tracks:
  values={'red':red_at,'blue':blue_at,'teal':teal_at}
  for key,definition in spec.get('trackReveal',{}).get(track['keyframes'][0]['object'] if track['keyframes'] else '',{}).items():
   values[key]=spoken(definition['keyword'],starts[definition['line']])
  track_reveals[track['sourceFile']+'|'+track['seedDefinition']['id']]=values
"""
assert needle in source;source=source.replace(needle,insert+needle)
needle=" panel_runs=[];begin=None"
insert=""" # Reject brief flashes after narration gating, without inventing a hold.
 drawable={};minimum_run=45
 for track in tracks:
  track_id=track['sourceFile']+'|'+track['seedDefinition']['id'];drawable[track_id]={}
  for key in ['red','blue','teal']:
   mask=[]
   for i,current in enumerate(observations):
    pts=next((points for candidate,points in current if candidate is track),None)
    mask.append(i/60>=max(reveal,track_reveals[track_id][key]) and pts is not None and key in pts and not np.any(pts[key][:,1]>360))
   valid=[False]*len(mask);begin=None
   for i,present in enumerate([*mask,False]):
    if present and begin is None:begin=i
    if not present and begin is not None:
     if i-begin>=minimum_run:valid[begin:i]=[True]*(i-begin)
     begin=None
   drawable[track_id][key]=valid
"""
assert needle in source;source=source.replace(needle,insert+needle)
source=source.replace("if key not in pts or a<{'red':red_at,'blue':blue_at,'teal':teal_at}[key]:continue","if key not in pts or not drawable[track['sourceFile']+'|'+track['seedDefinition']['id']][key][i]:continue")
source=source.replace("'movingPixelApproval':False}","'shortFlashRule':'only narration-gated stable color runs of at least0.75s; otherwise hidden', 'movingPixelApproval':False}")
source=source.replace("[('red','#ef5350'),('blue','#42a5f5'),('teal','#26c6b8')]", "[('blue','#42a5f5'),('teal','#26c6b8'),('red','#ef5350')]")
(B/'create-planes-overlay.py').write_text(source,encoding='utf8')
prefix=(B/'planes-tracks').relative_to(ROOT).as_posix()+'/'
scenes={}
def add(ident,tracks,note,red,blue='파랑: 관찰 기준점',teal='청록: 화면 비교 삼각형 · 실제 메시 아님',**extra):
 scenes[ident]={'landmarkSources':[prefix+t+'.json' for t in tracks],'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'tealAtLine':0,'redLabel':red,'blueLabel':blue,'tealLabel':teal,'mathNote':note,'mathNoteAtLine':0,'mathNotePosition':[390,42],'movingPixelApproval':False,**extra}
add('02',['02'],'정의한 바닥 y=2 / 법선은 면에 수직','빨강: 보이는 해안 경계의 일부')
add('05',['05'],'잔차 ÷ ‖n‖ → 수직 거리','빨강: 보이는 물 표면 경계')
add('08',['08'],'외적: 방향 / 길이는 평행사변형 넓이','빨강: 관찰한 바닥 표시')
add('PG01',['PG01-gel','PG01-cube'],'같은 바닥 기준 / 화면 높이≠월드 거리','빨강: 가리지 않은 바닥·벽 접선','파랑: 접선의 관찰 기준점',blueKeyword='푸른')
add('PG02',['PG02-slope'],'수평 바닥 → 기울어진 면 / 법선 역할','빨강: 보이는 경사 발판 가장자리')
add('PG03',['PG03-panel','PG03-door'],'정렬된 경계 → 방향 / 내부 구현 미확인','빨강: 보이는 패널 경계·문 옆 세로선')
add('11',['11'],'정의한6×4 삼각형 넓이12 / 별도4×3은6','빨강: 목재 발판의 관찰 경계')
add('14',['14'],'p=.2A+.3B+.5C=(1.8,2,0)','빨강: 보이는 유한한 발판 경계')
add('17',['17'],'같은 p → 넓이 비율 .2/.3/.5','빨강: 보이는 지형 경계')
add('19',['19'],'면 거리0 확인 → 가중치로 내부 검사','빨강: 가려지지 않은 발판 앞쪽 경계')
add('21',['21'],'선형 RGB 예제 / 실제 젤·화면 색 구현은 별개','빨강: 보이는 목재 발판의 선택 부분')
add('PG04',['PG04-floor','PG04-wall'],'면 방향을 아는 것 ≠ 실제 통로 범위','빨강: 보이는 바닥 타일 경계')
add('PG06',['PG06-tile','PG06-turret'],'투영 삼각형 ≠ 실제 메시 / 공면성 먼저','빨강: 타일 경계의 관찰 부분','파랑: 타일의 설명용 기준점',trackReveal={'PG06-tile-observed-patch':{k:{'keyword':'모서리','line':1} for k in ['red','blue','teal']}})
add('PG07',['PG07-pad','PG07-wall'],'표면의 위치 → 그 위치에 저장된 값','빨강: 보이는 발판 끝·벽의 경계')
data={'scope':'Edited observations over real1x footage; brief/uncertain geometry stays hidden. Direct final pixel review remains separate.','semanticColors':{'red':'visible physical edge/tile boundary or connection, never inferred engine collider','blue':'explicit observed reference point/object; new shot re-establishes reference','teal':'illustrative projected comparison triangle, not actual engine mesh'},'scenes':scenes,'finalPixelApproval':False}
(B/'planes-annotation-tracks.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'actualScenes':len(scenes),'briefGeometryHeldOrExtrapolated':False,'movingPixelApproval':False}))
