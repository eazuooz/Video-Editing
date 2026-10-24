"""Explicit scene choices from inspected sources; not automatic duration expansion."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def patch(sid,source,start,duration,title,phases,speech,observed,offset=0):
 return dict(scene=sid,source=source,offset=offset,duration=duration,title=title,meaning='',segments=[dict(kind='motion',**{'in':start},seconds=duration)],guides=[],phases=phases,modelCrop=[80,150,850,750],sourceReview=observed,speechMapping=speech)
def save(ep,slug,sources,patches,before,notes):
 d=dict(episode=ep,slug=slug,revision='gameplay-motion-v4',patchSet='reviewed-native-1',status='source-sequence-reviewed',newTts=False,sources=sources,patches=patches,sourceReview={'method':'Ordered source frames at0.5–2seconds; continuous sound review not inferred','nativeSpeed':1,'analyticalFreeze':0,'notes':notes},coverage={'previousNativeSeconds':before,'newNativeSeconds':sum(p['duration']for p in patches),'examples':len(patches),'finalAudiovisualReview':'pending'},preservation={'voicePcm':'unchanged','mathExplanations':'unchanged','totalFrames':'unchanged'})
 (B/(ep.lower()+'-plan.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ep,d['coverage'])

slug='game-math-quaternion-foundations-v3';sources=read(R/'projects'/slug/'production/concept-fit-v2/composition.json')['sources']
for s in sources.values():s['rightsEvidence']='projects/'+slug+'/production/concept-fit-v2/source-evidence.json'
save('M05',slug,sources,[
 patch('02','totk',417,21,'통나무의 위치와 긴 방향을 따로 조절',[(0,5,'조립한 통나무를 잡고 들어 올리기'),(5,14,'건너편에 놓을 위치 맞추기'),(14,18,'긴 방향을 돌려 맞추기'),(18,21,'내려놓아 다리로 배치')],
 '0–9.7s pickup/placement introduction;9.7–14.5s separate position from long direction;14.5–20.7s turning near destination then release. Right model remains through the rest.',
 'TotK417–438 inspected1fps;rotation431–433;release434;attached bridge result435–438. End before traversal becomes unrelated.'),
 patch('GA01','se2',98.5,13.5,'복사할 부품 선택부터 배치 결과까지',[(0,4,'복사할 부품의 범위 선택'),(4,8,'배치 미리보기의 앞면과 옆면'),(8,13.5,'새 위치로 옮겨 배치')],
 'The22s passage describes copy/place, faces, and camera differences; show the entire13.5s copy/preview/place action before the unchanged model continues.',
 'SE2vs1.2 source98.5–112 inspected1fps; selection99–102,copy103,preview104–110,solid111. Stop before weapons112+.'),
 patch('QF30','dorf',38,6.68,'집 타일을 돌려 주변과 맞추기',[(0,2,'집 타일 선택'),(2,4,'선택 타일의 방향 변경'),(4,6.68,'주변 지도에 배치')],
 'The original6.683s sentence names house tile then rotation/placement. Keep its complete action, not artificially extend into the following numerical example.',
 'Dorf38–44.68 inspected1fps; house tileturn40–41 andplacement42–44. Full action fits source and narration; no inserted still.'),
 patch('GA04','totk',291,13,'자세와 위치는 서로 다른 상태',[(0,4,'붙인 고리와 판을 함께 잡기'),(4,10,'같은 형태를 유지하며 이동'),(10,13,'레일에 내려놓기')],
 'GA04 separates unchanged front/up directions from translation. Game illustrates visible placement; original defined red/blue axes are retained on the right model, not claimed to be measured from game.',
 'TotK291–304 inspected2fps, rigid assembly lifting and placement. Different object from first log example, meaningful contrast; previous M04 used it for rotation-vector versus path.')
],35,'Retain brief house action because the entire action is visible; add a separate translation/unchanged-orientation example rather than pad with frozen houses.')

slug='game-math-quaternion-calculations-v3';old=read(B.parent/'m06-gameplay-plan.json');sources=old['sources']
save('M06',slug,sources,[
 patch('14','se2',46,7.25,'붙일 부품의 방향을 먼저 맞추기',[(0,2,'둥근 두 면이 있는 부품'),(2,5,'붙일 방향과 위치 맞추기'),(5,7.25,'결합된 결과 확인')],
 'Opening8s names two round faces and assembly. Return to unchanged inverse model when narration explicitly changes to it; no8.7s freeze.',
 'SE2launch46–53.25 inspected0.5s; rotate46–48,place49–52,solid52.5. Cut before trailer switches to unrelated interior53.3.'),
 patch('QC20','se2',94.4,4.95,'목표 앞면을 향하도록 돌린 뒤 배치',[(0,1.2,'기준이 되는 옆 부품'),(1.2,3.6,'미리보기 앞면 돌리기'),(3.6,4.95,'방향을 맞춘 뒤 배치')],
 'Original5.97s spoken insert; complete4.95s action. It is not falsely lengthened into the antenna cut.',
 'SE2launch94.4–99.35 inspected0.5s;preview95.5,turn96–98,place98.5–99.2; source cut99.4 excluded.'),
 patch('20','vs',99,13,'놓을 위치와 부품의 자세 비교',[(0,4,'부품 선택과 복사'),(4,9,'배치할 위치 찾기'),(9,13,'앞면과 옆면을 보며 배치')],
 'Scene20 first13s distinguishes placement point, target orientation and pose difference; genuine uninterrupted copy/placement shown with unchanged own target-pose model.',
 'SE2vs99–112 inspected1fps;complete selection→preview→solid placement; no shooting tail.'),
 patch('QC30','vs',104,7.7,'부품의 앞면과 위쪽을 함께 관찰',[(0,3,'배치할 부품의 앞면'),(3,5.5,'같은 부품의 윗면과 옆면'),(5.5,7.7,'배치된 상태')],
 'Original7.73s sentence explicitly names front/top. Earlier scene20 used same placement for target location; this bounded return compares two faces and is recorded as a return, not another different game.',
 'SE2vs104–111.7 inspected1fps;native preview camera orbit andfinalplacement. No still for surface guides.')
],15.1,'Three unique actions plus one explicitly identified face-comparison return. Very short original QC20 action remains short because source cut follows; main new13s action supports current/target distinction.')

slug='game-math-rotation-conversions-v2';sources=read(B.parent/'m08-gameplay-plan.json')['sources']
save('M08',slug,sources,[
 patch('17','besiege',53,16,'선택한 부품의 자세 변화와 표현 구분',[(0,6,'주황색으로 선택된 부품'),(6,10,'회전 도구 선택'),(10,16,'부품의 실제 자세 변화')],
 'Scene17 first passage names rotated part and facing; right model compares representations. Game shows actual change, not a fictional matrix readback.',
 'Besiege53–69 inspected1fps;selected assembly rotation occurs63–68 with native ring. No analytical freeze.'),
 patch('IG05','besiege',59,10,'고정된 자세와 실제 추가 회전 구분',[(0,4,'선택한 부품을 고정해 관찰'),(4,10,'회전 도구로 실제 기울이기')],
 'IG05 first9.27s fixed model versus representation; actual extra rotation spoken9.27s. Offset5.3s aligns native rotation63.5 at9.8s with speech; prefix unchanged explanation continues.',
 'Besiege59–69 inspected1fps;rotation63.5+. This is an identified return to the manipulation introduced earlier; not a new game counted.',offset=5.3),
 patch('IG08','besiege',33,8,'카메라를 움직여 같은 물체 관찰',[(0,3.5,'정면에서 같은 물체 보기'),(3.5,6.5,'위쪽으로 시점 이동'),(6.5,8,'몸체를 돌린 것과 구분')],
 'IG08 first7.54s fixed part and changed camera; camera shift37–38 aligns3.54s screen slope explanation.',
 'Besiege33–41 inspected1fps. Stop before object-editing; the rest of unchanged model shows controlled camera orbit.')
],15.9,'Third distinct action still needed for full final readiness: rotation introduced twice is a comparison return, not three unique examples. This plan stays source-review stage until a different verified action is added.')
