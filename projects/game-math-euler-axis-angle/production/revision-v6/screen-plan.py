"""Author the shared screen grammar and finite mathematical demonstrations."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
script=read(P/'script/revision-v6-article-flow/narration.ko.json')
TERMS={
 1:('Orientation','3차원 자세','앞·위·옆 방향까지 정해진 상태'),2:('Orientation','위치와 자세','옮기는 것과 돌리는 것을 구별'),3:('Euler Angles','오일러 각','축과 순서가 정해진 세 번의 회전'),4:('Heading','헤딩','처음의 수직 Y축 주위 회전'),5:('Pitch','피치','헤딩 뒤 물체 X축 주위 회전'),6:('Bank','뱅크','현재 물체 Z축 주위의 비틀림'),7:('Viewing Direction','관찰 방향','어느 쪽에서 축을 보는지 확인'),8:('Orientation','방향과 자세','앞 방향에 위·옆의 기울기까지 포함'),9:('Rotation Convention','회전 규약','축 · 양의 방향 · 적용 순서'),10:('Intrinsic / Extrinsic','움직이는 축과 고정 축','축의 기준이 바뀌면 같은 회전의 순서도 바뀜'),11:('Intrinsic / Extrinsic','두 경로, 같은 자세','물체축 Y-X-Z ↔ 고정축 Z-X-Y'),12:('Yaw / Heading','요와 헤딩','현재 물체 Y축과 직립 Y축을 구별'),13:('Proper Euler / Tait–Bryan','오일러 각의 규약들','반복하는 축인지 서로 다른 축인지 확인'),14:('Rotation Convention','회전 규약 변환','같은 회전을 공통 표현으로 옮겨 읽기'),15:('Euler Angles','오일러 각의 장점','사람이 읽고 편집하기 쉬운 각도'),16:('Quantization','양자화','가까운 간격의 대표값으로 저장'),17:('Euler Angles','유효한 세 각도','유한한 세 실수는 회전을 만든다'),18:('Aliasing','중복 표현','다른 숫자가 같은 끝 자세를 나타냄'),19:('Canonical Euler Angles','대표 범위와 정규형','같은 자세의 여러 표현 중 하나 선택'),20:('Gimbal Lock','짐벌 락','독립적이던 두 조절 방향의 효과가 겹침'),21:('Canonicalization','대표값으로 출력하기','중복 정리와 연속성 문제는 별개'),22:('Linear Interpolation','선형 보간','시작값에 차이의 진행 비율만큼 더함'),23:('Angle Interpolation','각도 보간','한 바퀴 차이와 의도한 경로 구별'),24:('Angle Wrapping','각도 차이 감싸기','같은 끝 회전을 만드는 짧은 차이'),25:('Floor / Angle Wrapping','내림과 각도 랩','한 바퀴를 몇 번 빼는지 계산'),26:('Radian / wrapPi','라디안과 각도 랩','단위를 맞추고 경계값을 정리'),27:('Euler Interpolation','3차원 보간의 한계','끝 자세와 중간 경로는 별개'),28:('Local / Global','국소와 전역','작은 범위의 표현과 모든 자세의 표현'),29:('Euler Angles','오일러 각 정리','편한 입력과 조심할 계산을 구별'),30:('Euler Rotation Theorem','오일러의 회전 정리','같은 원점의 두 자세 차이 = 한 축 회전'),31:('Axis–Angle','축·각 표현','단위축과 회전각을 함께 기록'),32:('Rotation Vector','회전벡터','방향은 축, 길이는 라디안 각도'),33:('Normalization','회전벡터 읽기','길이로 각도, 정규화로 단위축 복원'),34:('Scaled Rotation','회전량의 배수','같은 축에서 회전각만 배로 조절'),35:('Exponential Map','지수 사상','회전벡터를 실제 회전으로 보내는 연산'),36:('Axis–Angle','영 회전과 부호','축의 모호함과 동시 부호 반전'),37:('Angular Velocity','각속도와 회전 이력','끝 자세와 초당 회전량을 구별'),38:('Principal Rotation Vector','회전벡터의 대표 범위','0과 π 경계 조건까지 함께 확인'),39:('Rotation Composition','회전 합성','유한한 두 회전은 벡터 덧셈과 다름'),40:('Angular Velocity','작은 회전과 순간 각속도','근사 · 정확한 합성 · 같은 좌표계 구별'),41:('3D Rotations','축·순서·단위 확인','숫자와 동작과 끝 자세를 함께 확인')}
M={}
def put(s,b,kind,prompt,rows=(),**extra):
 key=f'v6-{s:02d}.B{b:02d}';M[key]=dict(kind=kind,prompt=prompt,rows=list(rows),**extra)

put(9,1,'rows','이름보다 약속을 확인',['Heading ↔ Yaw ?','Bank ↔ Roll ?','축 / 양의 방향 / 적용 순서'])
put(9,2,'rows','같은 이름 ≠ 같은 규약',['α, β, γ : 이름만으로 축을 알 수 없음','내재적: 물체와 함께 도는 축','외재적: 처음 방향을 유지하는 축'])
put(14,1,'rows','숫자 칸만 바꾸면 될까?',['규약 A: 축 · 부호 · 순서','규약 B: 축 · 부호 · 순서','숫자 이름 교환만으로는 부족'])
put(14,2,'flow','같은 자세를 거쳐 다른 규약으로',['규약 A의 각도','같은 회전 R','규약 B의 각도'])
put(14,3,'matrix','행벡터는 숫자 셋을 가로 한 줄로',['v직립 = v물체 R','R = Rz(b) Rx(p) Ry(h)','물체축 h→p→b = 고정축 b→p→h'])
put(16,1,'rows','같은 정밀도로 그대로 저장할 때',['오일러 각: 3개 × 4 B = 12 B','회전 행렬: 9개 × 4 B = 36 B','예시 전제: 성분 하나당 32 bit'])
put(16,2,'quantize','1° 간격의 대표값',['20.4° → 20°','성분 반올림 오차: 0.4°','가장 가까운 정수: 오차 ≤ 0.5°'])
put(16,3,'sine','성분 간격과 각도 간격은 다르다',['sin θ 성분의 변화 ≠ 같은 각도 변화','성분 오차와 최종 자세 오차를 구별','다른 표현도 압축할 수 있음'])
put(17,1,'rows','범위 밖 숫자도 회전을 만든다',['(h,p,b) = (720°,135°,0°)','유한한 실수 → 유효한 회전','유효한 자세 ≠ 의도한 자세'])
put(17,2,'matrix','모든 숫자 표가 회전은 아니다',['회전 행렬: 축 길이 1 · 서로 수직','임의의 3×3 표: 늘림/비틀림 가능','회전에 쓰는 쿼터니언도 조건 관리'])
put(19,1,'ranges','대표 범위',['−180° < h ≤ 180°','−90° ≤ p ≤ 90°','−180° < b ≤ 180°'])
put(19,2,'rows','피치만 따로 감싸면 끝날까?',['(0°,135°,0°)','같은 자세 → (180°,45°,180°)','p를 정리하면 h·b도 함께 변할 수 있음'])
put(19,3,'ranges','경계 p = ±90°',['안쪽: 세 조절 방향을 구별','경계: 헤딩·뱅크 효과가 겹침','대표값 규칙을 추가로 확인'])
put(21,1,'rows','뱅크를 0으로 고른 대표값',['p=+90° → h′=h−b, b′=0','(30°,90°,10°) → (20°,90°,0°)','p=−90° → h′=h+b, b′=0'])
put(21,2,'rows','물체는 조금, 숫자는 크게',['같은 연속 회전: p 89° → 91°','정규형 p: 89° → 89°','h·b: 0° → 180°'])
put(21,3,'flow','입력과 출력의 목적 구별',['입력: 유한한 세 각도','같은 회전','출력: 대표 범위/경계 규칙'])
put(22,1,'progress','t는 전체 움직임의 진행 비율',['0 = 0%','0.5 = 50%','1 = 100%'])
put(22,2,'rows','10°에서30°의 중간 값',['Δθ = 30° − 10° = 20°','θ(t) = 10° + t × 20°','t=0.5 → θ=20°'])
put(22,3,'rows','중간 자세까지 확인',['출발 자세 → 공중 자세 → 착지 자세','끝점이 같아도 경로는 여러 개','실제 동작의 중간 모습을 관찰'])
put(23,1,'circle','720° → 45°',['45° − 720° = −675°','같은 시작 자세라도 불필요한 여러 바퀴'],startAngle=720,delta=-675)
put(23,2,'circle','0° → 45°',['720° ≡ 0°','45° − 0° = +45°','여러 바퀴를 의도했다면 별도 관리'],startAngle=0,delta=45)
put(24,1,'circle','−170° → +170°',['원시 차이 = +340°','중간 값 = 0° : 길게 우회'],startAngle=-170,delta=340)
put(24,2,'circle','차이 자체를 감싼다',['340° − 360° = −20°','뒤쪽 경계를 지나 짧게 연결'],startAngle=-170,delta=-20)
put(24,3,'circle','짧은 경로의 중간',['−170° + 0.5 × (−20°) = −180°','−180° ≡ +180°'],startAngle=-170,delta=-20,progress=.5)
put(25,1,'floor','floor는 입력보다 크지 않은 정수',['floor(−0.1) = −1','0 쪽으로 버리는 trunc와 다름'])
put(25,2,'rows','340°에서 한 바퀴를 찾는다',['(340°+180°)/360° = 1.444…','floor(1.444…) = 1','340° − 360° × 1 = −20°'])
put(25,3,'ranges','floor 식과 끝점 보정',['w = x − 360 floor((x+180)/360)','위 식: [−180°,180°)','w=−180°이면 +180°로 → (−180°,180°]'])
put(26,1,'radian','호 길이 = 반지름이면 1 rad',['s = r','θ = s/r = 1 rad'])
put(26,2,'radian','반 바퀴의 호 길이는 πr',['180° = π rad','360° = 2π rad = τ','radians = degrees × π/180'],halfTurn=True)
put(26,3,'code','가장 가까운 한 바퀴 배수 빼기',['double w = std::remainder(angle, tau);','if (w <= -pi) w += tau;','return w;'],notes=['remainder: 최근접 정수 배 · 동점은 짝수','출력: −π < w ≤ π · 유한한 rad 입력'])
put(26,4,'code','입력·경계·보간 테스트',['double delta = wrapPiCanonical(end-start);','double value = start + t*delta;'],notes=['340° 해당 rad → −20° 해당 rad','+π → +π,  −π → +π','범위 밖을 줄이는 조건은 > π'])
put(28,1,'local','한 자세 주변과 모든 자세',['국소: 한 자세 주변의 작은 범위','전역: 가능한 모든 3D 자세','한 체계로 유일·연속·특이점 없음은 불가'])
put(28,2,'flow','표현마다 유리한 연산이 다르다',['사람이 편한 입력','회전 계산','사람이 읽는 출력'])
put(29,1,'flow','세 각도의 역할',['헤딩: 수직 Y','피치: 이동한 X','뱅크: 이동한 Z'])
put(29,2,'rows','사람에게 편리한 세 숫자',['축 · 양의 방향 · 순서 확인','읽기/편집 · 저장량/정밀도','유한한 세 각도는 회전을 만듦'])
put(29,3,'rows','중복 정리와 경로 문제 구별',['대표 범위 + p=±90°에서 b=0','wrap은 한 축의 주기 경계를 정리','짐벌 락과 실제 회전 경로는 별도 확인'])
put(33,1,'rows','e = (0,π/2,0)의 길이',['θ = √(ex²+ey²+ez²)','θ = √(0²+(π/2)²+0²)','θ = π/2 rad = 90°'])
put(33,2,'rows','영이 아닌 벡터를 길이로 나누기',['n = e / ‖e‖','n = (0,π/2,0) / (π/2)','n = (0,1,0) : 단위 Y축'])
put(33,3,'rows','영 벡터에서는 나누지 않는다',['e = (0,0,0) → θ = 0','영으로 나누어 축을 만들지 않음','회전이 없으면 특정 축이 필요 없음'])
put(35,1,'flow','자료와 연산을 나눈다',['회전벡터 e','지수 사상 Exp','회전 R'])
put(35,2,'rows','쓰임새와 범위',['애니메이션 회전 데이터','같은 축의 회전량 배수/미분','특정 범위 보간에 유용 · 경계는 남음'])
put(35,3,'rows','회전량과 회전 속도의 단위',['회전벡터 e : rad','각속도 ω : rad/s','방향은 축 · 길이는 서로 다른 양'])
put(41,1,'flow','오늘 사용한 자료와 연산',['축·각 (n,θ)','회전벡터 e=θn','지수 사상 e→R'])
put(41,2,'question','+170° → −170° : 짧은 차이는?',['짧은 차이 Δ = ?','중간 자세 θ(0.5) = ?'],answerRows=['−340° + 360° = +20°','170° + 0.5×20° = 180°'])
put(41,3,'question','e = (0,π/2,0) : 축과 각도는?',['길이 ‖e‖ = ?','단위축 n = ?'],answerRows=['θ = ‖e‖ = π/2 rad = 90°','n = (0,1,0) : +Y축'])

scenes=[]
for s in script['scenes']:
 n=int(s['id'][-2:]);en,ko,meaning=TERMS[n]
 beats=[]
 for b in s['teachingBeats']:
  spec=M.get(b['id']);beats.append({'id':b['id'],'renderer':'Manim' if spec else 'Unity','demonstration':spec,'explanationMeaning':b['visual']['targetActionResult'],'observationPurpose':b['hold']['purpose'],'guide':'actual clips may replace only their relevant observed action; full useful narration retained on the same testbed otherwise'})
 scenes.append({'id':s['id'],'title':s['title'],'termChip':{'term':ko,'en':en,'meaning':meaning,'sourceKind':'우리 Unity 씬 / 해설용 계산','definitionAtStart':True,'position':[96,64],'collapseAfter':'first defined passage, actual reading time'},'pictureLabel':'우리 Unity 씬 · 해설용 모형','beats':beats,'fixedCaptions':[960,970],'contentBounds':[96,230,1824,850],'transitionToNext':s['transitionToNext']})
out={'schemaVersion':1,'revision':'article-flow-v6-production','scriptSha256':hashlib.sha256((P/'script/revision-v6-article-flow/narration.ko.json').read_bytes()).hexdigest(),'grammar':'technical-explainer-grammar-v1','testbed':'same detailed aircraft, same primary camera, fixed reference/attached axes; finite clip states retained through narration and observation','measurementKind':'authored illustrative math, actual values computed in our implementation; commercial-game overlays editorial only','scenes':scenes,'mathematicalBeats':len(M),'renderTiming':'finite authored demonstrations, actual line/quiet-seam timing defines placement; no footage ratio or total runtime quota','credits':'complete verified KO/EN description sources last; no editor-added on-screen source lines'}
(H/'screen-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Authored',len(scenes),'screen plans;',len(M),'finite Manim beats; remaining spatial Unity')
