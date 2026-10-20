"""Part1 right-pane specifications; no media, engine or model is started here."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / 'projects/game-math-euler-axis-angle'
H = Path(__file__).parent
O = P / 'production/local/revision-v7-part1/explanation'
V6 = P / 'production/local/revision-v6'
ENGINE = ROOT / 'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6'
ISO = V6 / 'unity-capture'
SCRIPT = P / 'script/revision-v7-two-part/part-01.ko.json'
W, HGT, FPS = 900, 660, 60

# Pairs retain A on the left and B on the right *inside* the explanation pane:
# spoken "left/right model" never refers to the commercial-game pane.
# State: 0=first exact state, 1=last exact state, m=one native-speed motion.
# Abstract boards use an unchanged controlled-model context under readable text.
SPECS = {
 1: [('v6-01.B01','0')]*2 + [('v6-01.B01','m'),('v6-01.B01','1')],
 2: [('v7-sail-move','m'),('v7-sail-raise','m'),('v6-08.B01','m'),('v6-08.B01','1'),('v6-02.B02','0'),('v6-02.B02','m'),('v6-02.B02','1'),('v6-02.B03','m'),('v7-sail-raise','1')],
 3: [('board-euler','m'),('v6-03.B02','0'),('v7-hook-rotate','m'),('v6-03.B02','0'),('v6-03.B02','m'),('board-sign','m'),('v6-03.B02','1')],
 4: [('v6-04.B01','0'),('v6-04.B01','m'),('v6-04.B01','1'),('v6-04.B02','m'),('v6-04.B01','1'),('v6-04.B01','1')],
 5: [('v6-05.B01','0'),('v6-05.B01','0'),('v6-05.B01','m'),('v6-05.B02','m'),('v6-05.B02','1'),('v6-05.B02','1'),('v6-05.B01','1')],
 6: [('v6-06.B01','0'),('v6-06.B01','m'),('v6-06.B01','1'),('v6-06.B02','1'),('v6-06.B02','m'),('v7-sail-raise','1')],
 7: [('v6-04.B02','1'),('v6-07.B01','m'),('v6-07.B01','1'),('v6-07.B02','m'),('v6-07.B02','1'),('v6-07.B02','1')],
 8: [('v6-08.B01','m'),('board-direction','m'),('v6-08.B01','0'),('v6-08.B01','1'),('v6-08.B01','1'),('v6-08.B01','1'),('board-contract','1')],
 9: [('board-contract','m'),('board-names','m'),('board-other-names','m'),('board-contract','m'),('v6-10.B01','0')],
10: [('v6-10.B01','0'),('v6-10.B01','m'),('v6-10.B02','0'),('v6-10.B02','m'),('v6-10.B02','1'),('v6-11.B01','0')],
11: [('v6-11.B01','m'),('v6-11.B02','m'),('v6-11.B02','1'),('v6-11.B02','1'),('v6-11.B03','m'),('v6-11.B03','1')],
12: [('v6-12.B01','0'),('v6-12.B01','m'),('v6-12.B02','m'),('v6-12.B02','m'),('v6-12.B02','1'),('board-camera','m'),('v6-12.B02','1')],
13: [('v6-13.B01','0'),('v6-13.B01','m'),('board-stage','m'),('board-ground','m'),('v6-13.B02','m'),('board-tait-bryan','m')],
14: [('board-contract','m'),('board-rename','m'),('board-convert','m'),('board-basis','m'),('board-row-matrix','m'),('board-contract','1')],
15: [('v6-15.B01','0'),('v7-math-storage','1'),('v6-15.B01','m'),('v7-log-align','m'),('v7-sail-raise','m'),('board-input','m'),('v7-math-storage','1')],
16: [('v7-math-storage','m'),('board-many-poses','m'),('v7-math-half-step','m'),('v7-math-quantize','m'),('board-total-error','m'),('board-sine-error','m'),('board-compression','m'),('board-valid','1')],
17: [('board-valid','m'),('v7-math-stretch','m'),('board-quaternion-condition','m'),('board-contract','1'),('v6-18.B01','0')],
18: [('v6-18.B01','m'),('board-periodic','m'),('v6-18.B01','1'),('v6-18.B02','m'),('v6-18.B02','1'),('board-representative','m')],
19: [('board-ranges','m'),('board-representative','m'),('v6-18.B02','1'),('v6-20.B01','0'),('v6-20.B01','m')],
20: [('v6-20.B01','m'),('v6-20.B01','1'),('v6-20.B01','1'),('v6-20.B02','m'),('v6-20.B02','1'),('v6-20.B03','m'),('board-gimbal-limit','m'),('v6-20.B01','1')],
21: [('board-bank-zero','m'),('board-boundary-sign','m'),('board-continuity','m'),('board-input-output','m'),('v6-08.B01','1'),('v7-sail-raise','1'),('board-endpoints','m'),('board-next','m')],
}

# All values below are controlled lesson examples, never commercial-game data.
# At most three short lines are shown at once. The unchanged detailed aircraft
# remains dimly visible behind a board, rather than resetting to a blank slide.
BOARDS = {
 'euler': ('오일러 각', ['헤딩 h · Heading', '피치 p · Pitch', '뱅크 b · Bank']),
 'sign': ('부호도 약속입니다', ['좌표계', '양의 방향', '적용 순서']),
 'direction': ('앞 방향 + 비틀림', ['헤딩·피치 → 앞', '뱅크 → 위·옆']),
 'contract': ('숫자보다 먼저 확인', ['어느 축?', '어느 쪽이 +?', '어떤 순서?']),
 'names': ('이름은 대응 후보', ['heading / yaw', 'pitch', 'bank / roll']),
 'other-names': ('다른 표기 예', ['방위각·고도각·틸트', '알파·베타·감마', '이름만 바꾸지 않기']),
 'camera': ('아래를 보는 카메라', ['기운 물체 Y', '수직 기준 Y', '서로 다른 회전축']),
 'stage': ('어느 단계의 축인가', ['중간 피치 입력', '완성 뒤 물체 X', '일반적으로 다름']),
 'ground': ('지면 기준의 세 동작', ['수직 Y → 헤딩', '돌아간 X → 피치', '현재 Z → 뱅크']),
 'tait-bryan': ('축 순서를 확인', ['Y → X → Y · 고유 오일러', 'Y → X → Z', '테이트–브라이언 각']),
 'rename': ('칸 교환 ≠ 규약 변환', ['H / P / B', 'X / Y / Z', '먼저 축·부호·순서']),
 'convert': ('같은 자세를 옮기기', ['규약 A의 세 각', '공통 회전 행렬', '규약 B의 세 각']),
 'basis': ('행렬이 담는 정보', ['오른쪽은 어디로?', '위쪽은 어디로?', '앞쪽은 어디로?']),
 'row-matrix': ('행벡터 · 오른쪽 곱', ['vᵤ = vₒ R', 'R = Rz(b) Rx(p) Ry(h)', '동작 순서: Y → X → Z']),
 '3-vs-9': ('같은 자세의 저장', ['세 각도 · 3개', '행렬 · 3 × 3 = 9개']),
 'input': ('사람이 편집할 손잡이', ['조작 → 관찰 → 맞추기', '내부 표현의 증거 아님']),
 'many-poses': ('기록이 쌓이면', ['프레임 × 뼈 × 자세', '자세당 저장량도 중요']),
 'round-error': ('1° 간격으로 반올림', ['한 성분 오차', '최대 0.5°']),
 'quantize': ('작은 차이를 저장칸에', ['20.0° → 20°', '20.4° → 20°', '양자화 · Quantization']),
 'total-error': ('성분 오차와 자세 오차', ['성분별 최대 0.5°', '전체 자세도 0.5°?', '조합·현재 자세 확인']),
 'sine-error': ('오차의 뜻을 구분', ['각도 값의 오차', 'sin / cos 성분 오차', '같은 숫자로 읽지 않기']),
 'compression': ('다른 표현도 압축 가능', ['오일러만 가능한 일 아님', '각도·작은 저장량의 장점']),
 'valid': ('유한한 세 각도', ['h = 720°', 'p = 135°', '정한 규약에서 회전 생성']),
 'not-rotation': ('임의의 9개 숫자', ['늘어남·비뚤어짐 가능', '순수 회전 조건 필요']),
 'quaternion-condition': ('표현마다 조건이 다름', ['쿼터니언도 길이 관리', '유효함 ≠ 원하는 자세']),
 'periodic': ('숫자는 달라도 같은 끝', ['0° / 360° / 720°', '중복 표현 · Aliasing']),
 'representative': ('여러 표현 → 대표 하나', ['같은 끝 자세', '읽기 좋은 숫자 선택']),
 'ranges': ('정규형의 대표 범위', ['-180° < h, b ≤ 180°', '-90° ≤ p ≤ 90°']),
 'canonical-alias': ('피치만 접지 않기', ['(0, 135, 0)', '(180, 45, 180)', 'h·b도 함께 바뀜']),
 'gimbal-limit': ('물체가 못 도는 것 아님', ['표현의 조절 방향이 겹침', '물리적 회전은 가능']),
 'bank-zero': ('경계에서는 b = 0', ['p = +90° : h - b', 'p = -90° : h + b']),
 'boundary-sign': ('부호를 나누어 계산', ['+90° : 빼기', '-90° : 더하기']),
 'continuity': ('대표값 정리의 한계', ['작은 자세 변화', '출력 각도의 큰 변화 가능']),
 'input-output': ('입력과 출력을 구별', ['유한한 세 각 → 회전', '출력 → 대표 정규형']),
 'endpoints': ('끝 자세 다음의 질문', ['시작과 끝을 저장', '중간 경로는 아직 남음']),
 'next': ('다음 편으로 잇는 결과', ['시간에 따라 각도 바꾸기', '축 하나·각도 하나']),
}

ACTIVE_AXES = {
 2: ['a.bodyX','a.bodyY','a.bodyZ'], 3: ['a.bodyY','a.bodyZ'],
 4: ['a.uprightY','a.bodyZ'], 5: ['a.bodyX','b.uprightX'],
 6: ['a.bodyZ','a.bodyY'], 7: ['a.bodyZ'], 8: ['a.bodyZ','b.bodyY'],
10: ['a.bodyX','b.uprightX'], 11: ['a.bodyZ','b.bodyZ'],
12: ['a.bodyY','b.uprightY'], 13: ['a.bodyX','b.bodyX'],
15: ['a.bodyZ'], 18: ['a.bodyZ','b.bodyZ'],
20: ['a.uprightY','a.bodyZ'], 21: ['a.uprightY','a.bodyZ'],
}

REUSE_NOTE = ('V6 source geometry/rotation programs/camera and exact old capture are preserved. '
 'The optional new label-free capture changes only obsolete baked labels/leader objects and adds '
 'four finite motions of three independently authored sail/log/hook objects. Small original labels are never painted over '
 'moving geometry. New panel layout, larger labels, timing and final pixels require fresh review.')

# These phrases select actual speech clauses/words. The root resolves their
# sourceKoOffset against source-ASR. They are not paragraph-start autoplay.
# Multi-step keys retain each native step interval in right-assets.json.
ACTION_CUES = {
 'v7-a02.L01': ['이 돛을 들어 올려도'],
 'v7-a02.L02': ['누워 있던 돛을 세우고'],
 'v7-a02.L03': ['날개만 옆으로 기울 수'],
 'v7-a02.L06': ['돌아가면 같이 돌아갑니다'],
 'v7-a02.L08': ['나란히 맞춥니다'],
 'v7-a03.L03': ['방향 버튼으로 회전시키면'],
 'v7-a03.L05': ['기수가 오른쪽으로 돌아가는'],
 'v7-a04.L02': ['헤딩을 양의 사십오 도로'],
 'v7-a04.L04': ['원점을 내려다보면'],
 'v7-a05.L03': ['피치를 양의 이십 도로'],
 'v7-a05.L04': ['직립 엑스를 잡고 돌리겠습니다'],
 'v7-a06.L02': ['양의 삼십 도를 주면'],
 'v7-a06.L05': ['헤딩 사십오 도', '피치 이십 도', '뱅크 삼십 도'],
 'v7-a07.L02': ['양의 뱅크를 주면'],
 'v7-a08.L01': ['뱅크가 그 기수 주위에서'],
 'v7-a10.L02': ['헤딩을 한 뒤', '피치하고', '뱅크합니다'],
 'v7-a10.L04': ['뱅크·피치·헤딩을'],
 'v7-a11.L01': ['헤딩 삼십 도', '피치 이십 도'],
 'v7-a11.L02': ['피치 이십 도를 먼저', '헤딩 삼십 도'],
 'v7-a11.L05': ['고정 엑스 구십 도', '고정 와이 구십 도', '순서를 바꾸면'],
 'v7-a12.L02': ['기수가 수직 아래로 향하게'],
 'v7-a12.L03': ['요를 구십 도 주면'],
 'v7-a12.L04': ['헤딩 값을 바꾸면'],
 'v7-a13.L02': ['뱅크를 주고 나면'],
 'v7-a13.L05': ['세차', '장동', '자전'],
 'v7-a15.L03': ['헤딩 슬라이더', '피치 슬라이더'],
 'v7-a15.L04': ['옆으로 가져와', '나란히 붙입니다'],
 'v7-a15.L05': ['누운 돛을 들어 올리고', '세워서'],
 'v7-a16.L01': ['세 개의 양이 필요합니다','아홉 칸의 행렬'],
 'v7-a16.L03': ['일 도 단위로','최대 영 점 오 도'],
 'v7-a16.L04': ['이십 점 사 도'],
 'v7-a17.L02': ['길이가 늘어나거나'],
 'v7-a18.L01': ['영 도에서 삼백육십 도까지'],
 'v7-a18.L04': ['첫 모형은', '둘째는'],
 'v7-a19.L05': ['경계까지 비행기를 조금씩 숙이면'],
 'v7-a20.L01': ['사십오 도에서 팔십 도로', '다시 구십 도로'],
 'v7-a20.L04': ['헤딩 삼십 도와 뱅크 십 도', '헤딩 이십 도와 뱅크 영 도'],
 'v7-a20.L06': ['마이너스 구십 도인 경계'],
}

# A paragraph may discuss more than one object. Preserve the approved wording
# and switch our corresponding model on the same spoken action as the game.
WITHIN_PARAGRAPH_ASSETS = {
 'v7-a15.L05': [
   {'sourceBeatId':'v7-sail-move','cue':'누운 돛을 들어 올리고','window':0,'object':'a'},
   {'sourceBeatId':'v7-sail-raise','cue':'세워서 뗏목에 붙이는','window':0,'object':'a'},
   {'sourceBeatId':'v7-hook-rotate','cue':'갈고리를 돌려','window':0,'object':'a'},
 ],
}

# Source-frame names for a repeated end-state verification do not imply that
# the whole source motion is replayed. All intervals below are selected from
# the one finite native source; capture retains the saved source program.
PARAGRAPH_WINDOWS = {
 'v7-a18.L01': [
   {'cue':'영 도에서 삼백육십 도까지','sourceFrames':[0,270],'endMeaning':'360° exact endpoint'},
   {'cue':'칠백이십 도까지','sourceFrames':[270,540],'endMeaning':'720° exact endpoint'},
 ],
 'v7-a19.L05': [{'cue':'경계까지 비행기를 조금씩 숙이면','sourceFrames':[0,240],'endMeaning':'80° exact endpoint'}],
 'v7-a20.L01': [
   {'cue':'사십오 도에서 팔십 도로','sourceFrames':[0,240],'endMeaning':'p80°'},
   {'cue':'다시 구십 도로','sourceFrames':[240,480],'endMeaning':'p90°'},
 ],
 'v7-a20.L04': [{'cue':'헤딩 삼십 도와 뱅크 십 도','sourceFrames':[0,216],'endMeaning':'A(20,90,0) = B(20,90,0)'}],
}

# Serial teaching from an originally simultaneous A/B capture. A comparison
# pane is frozen at its real native endpoint while the other pane moves.
PAIR_ACTIONS = {
 'v7-a10.L04': [{'object':'b','cue':'뱅크·피치·헤딩을','fixedOtherFrame':'last'}],
 'v7-a11.L01': [{'object':'a','cue':'헤딩 삼십 도','stepCues':['헤딩 삼십 도','피치 이십 도'],'fixedOtherFrame':'first'}],
 'v7-a11.L02': [{'object':'b','cue':'피치 이십 도를 먼저','stepCues':['피치 이십 도를 먼저','헤딩 삼십 도'],'fixedOtherFrame':'last'}],
 'v7-a11.L05': [
   {'object':'a','cue':'고정 엑스 구십 도','stepCues':['고정 엑스 구십 도','고정 와이 구십 도'],'fixedOtherFrame':'first'},
   {'object':'b','cue':'순서를 바꾸면','fixedOtherFrame':'last'},
 ],
 'v7-a12.L03': [{'object':'a','cue':'요를 구십 도 주면','fixedOtherFrame':'first'}],
 'v7-a12.L04': [{'object':'b','cue':'헤딩 값을 바꾸면','fixedOtherFrame':'last'}],
 'v7-a18.L04': [
   {'object':'a','cue':'첫 모형은','fixedOtherFrame':'first'},
   {'object':'b','cue':'둘째는','fixedOtherFrame':'last'},
 ],
}

COINCIDENT_CONFIRMATIONS = {
 'v7-a11.L03':'겹치면',
 'v7-a18.L05':'겹쳐 놓으면',
}

PRETERM_READOUTS = {
 'v7-a02.L01':'위치 이동 · 눕힌 자세 유지',
 'v7-a02.L02':'중심 고정 · 자세 변화',
 'v7-a02.L03':'앞이 같아도 · 위와 옆은 다름',
 'v7-a02.L04':'앞·위·옆이 정해진 상태',
 'v7-a02.L05':'몸에 붙은 축 / 바깥 기준 축',
 'v7-a02.L06':'몸에 붙은 축은 같이 회전',
 'v7-a02.L07':'바깥 기준 축은 방향 유지',
 'v7-a02.L08':'항등 자세 · 두 축 일치',
 'v7-a02.L09':'우리 모형의 조건 · 중심 고정',
}
