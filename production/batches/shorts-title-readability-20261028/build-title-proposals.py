from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

ROOT=Path('D:/Github/VideoEditing')
OUT=Path(__file__).resolve().parent
covermap=json.loads((ROOT/'production/batches/shorts-private-schedule-20261028/covermap.json').read_text(encoding='utf-8-sig'))
studio=json.loads((ROOT/'production/batches/shorts-private-schedule-20261028/studio-after.json').read_text(encoding='utf-8-sig'))
titles={x['videoId']:x['title'] for x in studio['rows']}
data=[
('ULUDi4gKgzw','픽셀 하나에 불을 붙이면 벌어지는 일 | 노이타',['픽셀 하나가','동굴을 태운다'],'불과 물을 그림이 아니라 물질로 만든 게임 | 노이타','각 칸에는 색뿐 아니라, 물이나 기름 같은 물질의 종류가 들어 있습니다.','픽셀 하나라는 작은 출발점과 동굴 화재라는 큰 결과를 대비한다. 모든 배경 픽셀이 항상 움직인다는 종전 문구는 제거한다.','Terrain/material simulation; not every decorative background pixel moves.'),
('X27rK3qlrto','사진 한 장을 놓았더니 진짜 길이 생겼다 | 뷰파인더',['사진 한 장이','진짜 길이 된다'],'사진 속 길을 실제로 걸어가는 게임의 비밀 | 뷰파인더','화면에 그림만 덮는 게 아니라, 공간의 모양을 바꾸는 거죠.','사진과 실제로 걸을 수 있는 공간의 차이를 바로 이해하게 한다.','Do not imply arbitrary photographs are reconstructed by AI.'),
('pT9UgRewqxw','이렇게 움직이는데 몸체는 공 2개? | 레인월드',['몸속에는','공 2개뿐?'],'레인월드의 자연스러운 움직임은 공 2개에서 시작됐다','기본 몸체를 두 개의 둥근 덩어리로 표현해요.','실제 캐릭터 동작과 단순한 기본 몸체의 대비를 강조한다.','Two chunks describe Slugcat base body; limbs and tail have additional procedural drawing.'),
('QlIwFupj9Dk','현실 중력을 넣었더니 행성 탈출이 너무 쉬웠다 | 아우터 와일즈',['작은 행성의','중력을 바꿨다'],'작은 행성을 만들려고 중력 공식까지 바꾼 게임 | 아우터 와일즈','작은 행성에서 너무 쉽게 탈출 속도에 도달하는 문제를 겪었습니다.','기술명보다 실제 설계 문제와 의외의 선택을 앞세운다.','Planets used modified falloff; Sun retained inverse-square gravity. Public release remains rights-blocked.'),
('NwgrLJhu1UI','색은 단 2개인데 그림자까지 보인다? | 오브라 딘',['색은 2개','그림자는 있다'],'두 가지 색만으로 입체감을 만든 게임 | 오브라 딘의 디더링','밝고 어두운 점을 섞어서 중간 밝기를 표현합니다.','화면의 풍부한 명암과 실제 색 수의 대비를 짧게 제시한다.','Two-color rendering does not mean absence of 3D geometry or lighting calculation.'),
('ijGOYaPZi3c','화면을 넓혔더니 몬스터가 반격을 못 했다? | 디아블로2 레저렉션',['화면 넓히니','적이 안 싸운다?'],'디아블로2가 화면 양옆을 가린 이유 | 울트라와이드의 함정','당시에는 넓어진 화면 끝의 적을 공격할 수 있었지만, 그 거리에서는 적의 반응이 시작되지 않았어요.','모니터 폭을 늘리는 무해한 변화가 전투 규칙을 깨는 의외성을 드러낸다.','Past-tense 2021 testing example. Do not frame as a present-day exploit or all monsters freezing.'),
('qpoUJd_S0LA','아이템이 안 보이자 개발자는 풀을 비켜 줬다 | 디아블로2 레저렉션',['아이템을 위해','풀이 비킨다'],'더 예쁜 그래픽이 아이템을 숨겨버렸다면? | 디아블로2 레저렉션','아이템이 떨어지면, 주변 풀을 비켜 주는 기술이었습니다.','아이템을 찾는 플레이어의 문제와 구체적인 해결책을 함께 보여 준다.','Nearby vegetation is displaced; do not imply every plant is removed permanently.'),
('KcnUqy8tcfI','갑옷을 갈아입힐 때 그림을 갈아 끼웠다 | 디아블로2',['갑옷 바꾸기?','그림 바꿔치기'],'디아블로2 캐릭터는 한 장의 그림이 아니었다','머리와 몸통, 다리와 양팔, 무기와 방패를 따로 렌더링했습니다.','갑옷 교체라는 익숙한 행동과 부위별 스프라이트 조합을 연결한다.','Original Diablo II, not Resurrected rendering; prere​ndered body-part sprites are combined.'),
('IaU43puuLuI','전투는 그대로인데 그래픽만 20년 전으로? | 디아블로2 레저렉션',['버튼 한 번에','20년 전으로'],'버튼 하나로 옛날 그래픽이 되는 게임의 비밀 | 디아블로2 레저렉션','같은 게임 상태를 다른 모습으로 보는 거예요.','전투 상태는 유지된다는 핵심을 그래픽 전환의 놀라움과 함께 전한다.','One shared game state with rendering layers; not two independent simulations or literal time travel.'),
('tocRD4fGhJ0','패드로 바꾸자 자동 길 찾기를 꺼야 했다 | 디아블로2 레저렉션',['패드 넣으려다','길 찾기를 껐다'],'디아블로2 패드 조작은 버튼만 연결한 게 아니었다','패드에서는 자동 길 찾기를 끄고, 플레이어가 방향을 직접 조절하게 했습니다.','기능을 추가하려다 기존 기능을 끈 선택의 역설을 보여 준다.','Player stick movement only; do not imply AI pathfinding was disabled globally.'),
('Tt7hCWPjcpc','그림은 24프레임, 게임은 60프레임? | 컵헤드',['24프레임인데','왜 부드럽지?'],'24프레임인데 왜 이렇게 부드럽지? | 컵헤드 애니메이션','그림을 초당 이십사 프레임으로 재생하고, 게임은 초당 육십 프레임으로 실행합니다.','그림 교체와 게임 실행의 서로 다른 주기를 숫자 두 개로 직관적으로 대비한다.','Animation playback rate vs game execution/movement update; not invented intermediate hand drawings.'),
('utm0fy9Smyc','페인트를 칠했는데 바뀐 건 번호였다 | 티어다운',['색칠했는데','번호만 바뀐다'],'게임 속 스프레이에 숨은 번호 바꾸기 꼼수 | 티어다운','뿌릴 때는 팔레트 변환표를 보고, 해당 복셀의 번호만 바꿔요.','보이는 색칠과 내부 데이터 변화의 차이를 강조한다.','Describes documented palette-index approach and early capacity limits, not a claim about every current paint path.'),
('5-QZzmXlTLM','잉크를 더 반짝이게 했더니 적을 놓쳤다? | 스플래툰 2',['더 반짝이면','적을 놓친다'],'그래픽을 더 예쁘게 했더니 적이 안 보였다? | 스플래툰 2','반짝임을 세게 하자 적이 잠기는 흔적이 잘 안 보였습니다.','예쁜 그래픽이 플레이 정보 전달을 방해하는 구체적 결과에 초점을 맞춘다.','Enemy dive traces became hard to see during development; not a stealth exploit or claim of literal invisibility.'),
('RYjQZiKtU30','스플래툰 잉크는 벽에 어떻게 붙을까? 닌텐도 특허 속 원리',['잉크는 왜','벽에 붙을까?'],'벽에 남는 잉크를 만드는 방법 | 스플래툰과 닌텐도 특허','닌텐도 특허에 공개된 방식은 표면에 투명한 색칠 종이를 연결하는 겁니다.','눈에 보이는 벽의 잉크를 질문으로 제시하고 실제 근거인 특허를 제목에서 명확히 한다.','Patent describes a technique; do not assert exact shader/code shipped in every commercial Splatoon version.'),
]
items=[]
for vid,title,hook,alternate,snippet,reason,limit in data:
    cover=next(c for c in covermap['covers'] if c['videoId']==vid)
    script=ROOT/'projects'/cover['slug']/'script'/'narration.ko.txt'
    if not script.exists():script=script.with_name('narration.spoken.ko.json')
    source=script.read_text(encoding='utf-8-sig')
    assert snippet in source,(vid,snippet)
    assert len(title)<=100 and len(hook)==2
    item={
        'videoId':vid,'slug':cover['slug'],'currentTitle':titles[vid],
        'proposedTitle':title,'thumbnailLines':hook,'alternateTitle':alternate,
        'evidence':{'path':str(script),'sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'snippet':snippet,'fullShortNarrationRead':True},
        'rationale':reason,'essentialCondition':limit,
        'claimSourceRecord':str(ROOT/'projects'/cover['slug']/'sources'/'selected-footage.json'),
        'newFactsAdded':False,'viewIncreaseGuaranteed':False,
        'titleLength':len(title),'thumbnailSyllables':[sum('\uac00'<=c<='\ud7a3' for c in x) for x in hook],
    }
    if vid=='RYjQZiKtU30': item['primaryClaimRecord']=str(ROOT/'projects'/cover['slug']/'sources'/'primary-evidence.json')
    items.append(item)
OUT.mkdir(parents=True,exist_ok=True)
output={'createdAt':datetime.now(timezone.utc).isoformat(),'scope':'Recent 14 only; keep schedules and Outer Wilds private hold','status':'copy-ready-for-root-review','purpose':'Shorten thumbnail wording for large type; viewer-observable hook before game keyword in titles','factBasis':'Existing finalized narration/metadata and source records; no new technical claims or new primary-web audit','performanceClaim':'No guarantee of views or ranking. Titles and covers change together, so any later performance difference is not attributable to one component alone.','items':items}
(OUT/'title-proposals.json').write_bytes((json.dumps(output,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(str(OUT/'title-proposals.json'))
