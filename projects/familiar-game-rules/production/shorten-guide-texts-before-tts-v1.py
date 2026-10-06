"""Tighten only unsynthesized new guides; retain concrete observations and original PCM."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
requestPath=BASE/'observation-guide-tts-request-v1.json';request=read(requestPath)
assert not request['pairedWholeTextReview'] and not (BASE/'observation-guide-tts-execution-v1.json').exists()
revisions={
'12':('분홍색 문 앞의 대상을 겨눕니다. 다음 계단 컷에서는 높은 쪽으로 화면을 돌리죠. 대상의 높이와 방향 잡기를 함께 따라가 보세요.', 'The player aims at a target by the pink door. The next stairway shot turns the view upward. Follow the target’s height and the change in direction together.'),
'13':('문을 발로 차고, 다른 방에서는 총을 겨눕니다. 대상을 향해도 실행하는 행동은 다르죠. 새 발차기와 방향 잡기의 연결을 나누어 보세요.', 'The player kicks a door, then aims in another room. Facing a target can lead to different actions. Examine how the new kick connects to establishing a direction.'),
'14':('시장에서 총을 쏘는 컷과 우산을 펴고 줄 근처를 지나는 컷을 보세요. 몸의 이동과 도구의 상태는 함께 바뀌죠. 같은 도구가 여러 행동에 쓰입니다.', 'Compare firing at the market with opening the umbrella near a wire in a separate shot. The body moves while the tool changes state. The same tool appears in several actions.'),
'15':('기찻길과 시장, 늪과 컨테이너 전투는 별도 구간입니다. 몸이 있는 높이와 총의 방향을 나누어 보세요. 도구 사용과 방향 선택을 함께 점검합니다.', 'The rail, market, swamp and container fights are separate intervals. Compare the body’s height with the gun’s direction. Examine tool use together with direction selection.'),
'17':('뛰어오른 순간에는 두 총이 서로 반대쪽을 향합니다. 몸의 이동 방향 하나로 두 대상을 고르는 문제를 대신할 수는 없죠. 이동과 목표 선택을 따로 설계할 이유입니다.', 'During the jump the two guns point in opposite directions. One movement direction cannot stand in for selecting both targets. This illustrates why movement and target selection need separate design.'),
'18':('지붕 위로 움직이는 동안 총은 아래를 향합니다. 몸의 위치만 따라가면 아래쪽 목표를 놓칠 수 있죠. 이동 경로와 총이 향하는 쪽을 각각 확인해 보세요.', 'The gun points downward as the body moves above the roof. Following the body alone can miss the lower target. Check the traversal route and the gun’s direction separately.'),
'19':('회전하며 뛰던 몸이 지붕으로 돌아왔다가 객차 안으로 내려갑니다. 총이 향하는 대상도 바뀌죠. 새로운 길에서도 이동과 목표 선택의 연결이 이어지는지 점검합니다.', 'After a spinning jump the body returns to the roof and descends into the carriage. The guns change targets. Check whether movement and target selection remain connected on a new route.')}
outlinePath=BASE.parent/'planning/outline.md';outline=outlinePath.read_text('utf-8')
creatorPath=BASE/'prepare-observation-guides-v1.py';creator=creatorPath.read_text('utf-8')
for g in request['guides']:
    assert not (ROOT/g['path']).exists()
    if g['id'] in revisions:
        ko,en=revisions[g['id']]
        for old,new in [(g['ko'],ko),(g['en'],en)]:
            assert old in outline and old in creator
            outline=outline.replace(old,new);creator=creator.replace(old,new)
        g.update(ko=ko,en=en,text=ko)
save(requestPath,request);save(BASE.parent/'planning/observation-guides-v1.json',request)
for language in ['ko','en']:
    p=BASE.parent/f'script/observation-guides.{language}.json';d=read(p)
    for s in d['scenes']:s['lines']=[next(g for g in request['guides'] if g['id']==s['id'])[language]]
    save(p,d)
outlinePath.write_text(outline,encoding='utf-8');creatorPath.write_text(creator,encoding='utf-8')
print(json.dumps([dict(id=g['id'],chars=len(g['ko']),estimateSeconds=round(len(g['ko'])/8.5,2)) for g in request['guides']],ensure_ascii=False))
