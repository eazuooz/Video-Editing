"""Source-action choices inspected as ordered decoded frames. No time padding."""
from pathlib import Path
import json,copy
R=Path(__file__).resolve().parents[4]; V=Path(__file__).resolve().parent; B=V.parent
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(d):
 d.update(revision='gameplay-motion-v4',patchSet='reviewed-native-1',status='native-source-reviewed-patch-qa-pending',newTts=False)
 d['preservation']={'narrationPcm':'unchanged','explanations':'unchanged','order':'unchanged','frames':'unchanged'}
 d['sourceReview']={'method':'Ordered decoded source frames, 0.5–1 second spacing, examined before these choices','nativeSpeed':1,'analyticalFreeze':0,'audioReview':'pending final mix'}
 d['coverage']={'nativeSeconds':round(sum(p['duration'] for p in d['patches']),3),'examples':len(d['patches']),'internalQa':'pending','humanReview':'pending'}
 (V/(d['episode'].lower()+'-plan.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(d['episode'],d['coverage'])
def load(ep):
 d=read(B/(ep.lower()+'-gameplay-plan.json'));d['patches']=[];return d
def add(d,sid,source,start,end,title,observed,phase,offset=0,key=None):
 t=read(R/'projects'/d['slug']/'production/concept-fit-v2/timeline.json');s=next(s for s in t['scenes'] if s['id']==sid)
 duration=round(end-start,3);assert offset+duration<=s['seconds']+.01,(d['episode'],sid)
 p=dict(scene=sid,key=key or sid,source=source,offset=offset,duration=duration,title=title,meaning='',segments=[{'kind':'motion','in':start,'seconds':duration}],guides=[],modelCrop=[80,150,850,750],sourceReview=observed,speechMapping={'offset':offset,'cues':s['cues'],'decision':'Native action shown beside unchanged explanation; exact internal values belong only to the model.'},phases=phase)
 d['patches'].append(p);return p

if __name__=='__main__':
 d=load('M07')
 d['sources']['release']={'path':'shared/output/private-math-gameplay-20261024/motion-v4/source-review/escape-candidates/release.mp4','game':'Escape Simulator','rightsEvidence':'projects/game-math-interpolation-paths-v2/production/concept-fit-v2/source-evidence.json','acquisitionEvidence':'shared/output/private-math-gameplay-20261024/motion-v4/source-review/escape-candidates/release.json'}
 add(d,'02','escape',8,11.6,'수납장 문이 열리는 중간 자세','Original editor trailer8–11.6: closed cabinet, button, hinge rotation, open result. Stop before unrelated key/door cut.',[(0,1.7,'닫힌 문과 경첩 위치'),(1.7,2.8,'문이 돌아가는 중간 자세'),(2.8,3.6,'열린 뒤의 자세')])
 add(d,'05','release',24.6,33.8,'거울을 돌리는 과정과 끝 방향','Release trailer24.6–33.8 inspected1fps: mirror selected, beam direction changes26–28, overhead29–30, mirror turns31–32, result33. Game mirror is adjacent orientation example; the red turntable is explicitly the own model.',[(0,2,'거울의 현재 방향'),(2,5.7,'거울을 돌리며 달라지는 방향'),(5.7,9.2,'다른 쪽에서 돌린 결과 확인')],offset=29.27,key='05-mirror')
 add(d,'08','escape',12.3,15.7,'열쇠를 사용한 뒤 문이 열리는 과정','Original editor12.3–15.7 key use then single door hinge opening14.2–14.8 and result15; community footage16+ excluded.',[(0,1.7,'열쇠 사용과 닫힌 문'),(1.7,2.6,'문이 열리는 중간 자세'),(2.6,3.4,'열린 문과 통로')])
 d['limitations']=['The two door motions are intrinsically short at native speed. Complete actions are shown without freezes; the9.2s mirror example adds continuous rotation observation. Do not count the original short bridge as a new adequate example.']
 save(d)

 d=load('M09')
 add(d,'02','grapple',407,421,'바위에 연결하고 다음 발판에 도착하기','Uncle407–421: connect408–410,second connection411–417,release418,landing420. End before next jump.',[(0,4,'손에서 바위로 연결'),(4,11,'다음 바위 쪽으로 연결 방향 변경'),(11,14,'연결을 놓고 발판에 도착')])
 add(d,'LG01','factory',71.5,75.2,'케이블을 잇는 두 접점','Only71.5–75.2 is wire operation; before/after trailer cuts are different topics. Complete native action ends before switch75.3. Narration returns to model at4.1s.',[(0,1.5,'연결할 첫 번째 접점'),(1.5,3.7,'다른 접점까지 케이블 연결')])
 add(d,'LG03','grapple',370,388,'다른 두 끝점 사이의 연결','Uncle370–388: two grapple attachments371–379,travel380–386,landing387. Distinct observed action from407–421, used for endpoint contrast, not hidden parameter measurement.',[(0,5,'앞의 바위를 향한 연결'),(5,10,'다른 바위로 연결 방향 변경'),(10,18,'연결을 따라 이동한 뒤 착지')])
 add(d,'03','bridge',5.5,11.9,'원형 편집 가이드에서 완성된 다리까지','Poly5.5–7.8 circle/triangle construction,8–11.9 car crosses resulting bridge. Explicit edit→test source cut; no claim of same visible circle during driving.',[(0,2.3,'편집 화면의 중심과 원형 가이드'),(2.3,6.4,'조립한 다리 위로 차량 통과')])
 save(d)

 d=load('M10')
 add(d,'LG05','tinyglade',10.5,17,'건물 생성부터 폭 변경까지','TinyA10.5–17: new building11–12, width/height adjustments13–16, finish before next tower edit.',[(0,2,'건물 놓기'),(2,5,'건물의 너비 변경'),(5,6.5,'바뀐 지붕과 벽의 범위')])
 add(d,'LG07','tinyglade',17,22,'건물 높이와 지붕의 범위','TinyA17–22: tower roof selected, height changes18–21; stop before color menu.',[(0,1,'높이를 바꿀 건물'),(1,4,'벽과 지붕을 위로 늘리기'),(4,5,'달라진 꼭대기 높이')])
 add(d,'19','tinyglade',53.25,58.7,'같은 성을 다른 방향에서 관찰','TinyA53.25–58.7 camera orbit of completed castle; logo begins59. Object geometry unchanged.',[(0,2,'같은 성의 정면과 옆면'),(2,5.45,'카메라를 옮겨 보이는 범위 비교')])
 add(d,'10','big',1708,1717,'둥근 머리의 윤곽을 다른 각도에서 보기','Big1708–1717 continuous close view of red head turning toward camera then camera pulling back. Rounded bound is own right model, not hitbox measurement.',[(0,4,'옆쪽에서 보이는 둥근 윤곽'),(4,9,'정면에서 보이는 둥근 윤곽')])
 add(d,'LG06','besiege',59,69,'물체를 돌리면 함께 바뀌는 윤곽','Besiege59–69 selected part then rotation63–68 with native ring. No camera-only substitution for object rotation.',[(0,4,'선택한 부품의 현재 모양'),(4,10,'제자리 회전과 바뀐 화면 윤곽')])
 save(d)

 d=load('M11')
 add(d,'02','bridge',5.5,11.9,'다리를 만든 뒤 차량이 통과하는 높이','Poly5.5–7.8 editor→8–11.9 test, car crosses complete bridge. Surface is visible throughout test; no unrelated ship clip.',[(0,2.3,'다리의 연결과 윗면'),(2.3,6.4,'윗면 위를 통과하는 차량')])
 add(d,'PG02','bridge',12,19.8,'다리의 연결을 만든 뒤 가운데 열기','Poly12–15.8 editor builds connected members,16–19.8 bridge opens for ship. One editor→test sequence, no replay.',[(0,3.8,'양쪽에 연결된 다리 만들기'),(3.8,7.8,'가운데가 열리며 면 방향 변경')])
 add(d,'08','bridge',0,5.4,'삼각형 연결과 실제 움직이는 다리','Poly0–2 bridge member construction,2–5.4 assembled bridge opens. Native sequence includes diagram-relevant three connection points, then result.',[(0,2,'편집 화면의 세 점과 연결선'),(2,5.4,'연결된 다리가 움직이는 결과')])
 d['limitations']=['Official source uses short edit→test sequences. No action is slowed or frozen; full source actions retained. Mathematical plane/normal claims stay in own model.']
 save(d)

 d=load('M12')
 town=read(B/'m18-gameplay-plan.json')['sources']['town']
 d['sources']['townlong']=town
 add(d,'11','townlong',1203,1212,'지붕과 벽을 만든 뒤 다른 면 보기','Town1203–1212 platform→roofed building1205–1207→camera1208–1211; stop before deletion1212. Three mathematical reference points are on right model, not claimed to be mesh vertices.',[(0,2,'건물의 바닥과 벽 생성'),(2,5,'지붕이 생기고 모서리가 드러남'),(5,9,'같은 지붕을 다른 쪽에서 보기')])
 add(d,'17','townlong',1504,1512,'같은 건물의 정면과 윗면 비교','Town1504–1512 camera rises from front to overhead and behind. Depth differs although front projections overlap; no depth values measured.',[(0,2,'정면에서 보이는 건물'),(2,5,'위에서 드러나는 앞뒤 간격'),(5,8,'반대편에서 같은 건물 확인')])
 # Colour changes cannot be asserted from a sequence that also builds geometry.
 # Preserve the original mathematical colour explanation alone in PG07.
 add(d,'21','townlong',1207,1212,'같은 지붕과 벽의 서로 다른 색','Town1207–1212 orbit shows orange roof and cream wall of same building before deletion; earlier construction is an explicit return with different surface-property focus.',[(0,2,'주황 지붕과 밝은 벽'),(2,5,'보는 면에 따라 달라지는 화면 색')])
 d['removedMismatch']={'PG07':'Original footage changed building geometry while narration holds point position and changes vertex colours. Retain unchanged mathematical model; do not use unrelated building as proof.'}
 save(d)

 d=load('M13')
 add(d,'02','dorf',38,45,'육각형 타일을 돌려 빈자리에 배치','Dorf38–45 house tile selection,rotation40–41,placement42–44; complete action. Native hex perimeter visible.',[(0,2,'타일의 가운데와 바깥 변'),(2,4,'타일을 돌려 방향 맞추기'),(4,7,'빈자리에 놓은 결과')])
 add(d,'11','dorf',116,123.8,'타일 추가와 달라지는 전체 경계','Dorf116–123.8 placement117,undo119,new tile120–123, stop before loading124.',[(0,3,'육각형 타일을 빈자리에 추가'),(3,5,'추가한 타일을 다시 제거'),(5,7.8,'다른 타일 배치와 전체 경계')])
 add(d,'QG01','tinyA',10.5,17,'같은 건물의 크기와 바깥선','TinyA10.5–17 creation then width/height; exact fixed center comparison remains right model.',[(0,2,'건물과 기준 위치'),(2,6.5,'늘어난 벽과 지붕의 바깥선')])
 add(d,'QG02','tinyB',0,11.9,'벽을 지우고 통로를 만드는 전 과정','TinyB0–5 erase,6–8 redraw,9–11 path creates arch. Full action order matches narration.',[(0,5,'벽을 지워 빈 공간 만들기'),(5,8.5,'굽은 벽 다시 그리기'),(8.5,11.9,'길이 지나며 아치 생성')])
 add(d,'QG03','tinyB',22,30.8,'고정된 건물 아래 땅 높이 바꾸기','TinyB22–30.8 terrain height raise/lower then outline; stop before31 color menu.',[(0,4,'땅 높이를 올리기'),(4,6,'다시 낮춘 지형'),(6,8.8,'높이와 평면 경계를 구분')])
 save(d)
