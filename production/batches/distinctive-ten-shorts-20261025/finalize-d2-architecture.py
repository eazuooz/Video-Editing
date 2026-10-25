"""Finalize source-matched narration for the two owned architectural Shorts."""
from pathlib import Path
import json, datetime
R=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows={
'shorts-d2r-renderer-logic-separation':[
 [('이 게임, 버튼 하나로 옛날 그래픽을 볼 수 있습니다.','This game can switch to classic graphics with a button.'),('전투는 그대로고요.','The battle keeps going.')],
 [('게임에는 두 가지 일이 있습니다.','A game has two different jobs.'),('위치와 공격 결과를 계산하는 일,','One calculates positions and attack results.'),('그 결과를 화면에 그리는 일이죠.','The other draws those results on screen.')],
 [('디아블로 투 레저렉션은 기존 게임의 동작 위에,','Diablo II: Resurrected builds on the underlying game.'),('새 삼차원 그래픽을 그리는 층을 얹었습니다.','A new layer renders it in 3D.'),('위치와 행동을 받아 새 모델로 보여주는 거예요.','It presents positions and actions using new models.')],
 [('우리 그림에서 캐릭터가 한 칸 움직이면,','In our diagram, move the character one cell.'),('옛 모습과 새 모습이 같은 위치를 따라갑니다.','Both appearances follow the same position.'),('그리는 방식이 달라져도, 움직임의 기준은 하나죠.','The presentation changes; the underlying state is shared.')],
 [('그래서 화면을 바꾸어도,','That is why switching the view'),('캐릭터와 몬스터의 상태가 처음으로 돌아가지 않습니다.','does not reset the characters or monsters.'),('같은 게임 상태를 다른 모습으로 보는 거예요.','You see the same game state through another presentation.')],
 [('이것이 게임 로직과 렌더링의 분리입니다.','This is separation of game logic and rendering.'),('익숙한 게임의 동작 위에, 새로운 화면을 입힌 거죠.','A new visual layer wraps familiar gameplay.')]
],
'shorts-d2r-controller-input-adapter':[
 [('클릭으로 움직이던 디아블로 투.','Diablo II was built around click movement.'),('패드는 어떻게 연결했을까요?','How did the developers connect a gamepad?')],
 [('클릭은 목적지를 정하는 방식입니다.','A click specifies a destination.'),('게임이 거기까지 길을 찾아가죠.','The game finds a path to it.'),('스틱은 지금 움직일 방향을 정합니다.','A stick specifies the direction to move right now.')],
 [('그래서 사이에 입력을 바꾸는 통역을 넣었습니다.','An input translator connects the two.'),('스틱과 버튼을, 기존 게임이 이해하는 행동으로 연결한 거예요.','It connects sticks and buttons to actions the existing game understands.')],
 [('그런데 이동은 명령만 바꾸면 끝일까요?','But is translating the command enough?'),('패드에서는 자동 길 찾기를 끄고,','With the controller, automatic pathfinding is turned off.'),('플레이어가 방향을 직접 조절하게 했습니다.','The player directly controls the direction.'),('그래서 벽으로 밀면, 벽에 막히기도 하죠.','Push toward a wall and the character can run into it.')],
 [('우리 그림에서도 목적지는 같은데,','In our diagram, the intended destination is the same.'),('클릭은 장애물을 돌아가고,','Click movement finds a route around the obstacle.'),('스틱은 방향을 바꿔 줘야 합니다.','Stick movement needs you to change direction.'),('조작의 의미가 달라진 겁니다.','The meaning of the control has changed.')],
 [('입력 변환 계층으로 옛 게임과 새 조작기를 연결하고,','An input adaptation layer connects the old game to the new device.'),('이동 방식까지 다듬어, 패드의 손맛을 만든 거죠.','Adapting movement makes it feel natural on a controller.')]
]}
comparison=read(B/'local/d2r-official/comparison/receipt.json')
broll=read(B/'local/d2r-official/receipt.json')
for slug,paras in rows.items():
    p=R/'projects'/slug
    assert not (p/'production/local/audio-v1/voice/narration.wav').exists(), 'Preserve generated PCM'
    lines=[' '.join(x[0] for x in para) for para in paras]
    clauses=[dict(id=f'p{i+1}-{j+1}',lineIndex=i,spoken=ko,ko=ko.replace('디아블로 투','디아블로 II').replace('삼차원','3D'),en=en) for i,para in enumerate(paras) for j,(ko,en) in enumerate(para)]
    save(p/'script/narration.spoken.ko.json',dict(slug=slug,revision='distinctive-ten-v1',scenes=[dict(id='main',lines=lines)]))
    save(p/'script/clauses.json',dict(clauses=clauses,pronunciationAliases={'디아블로 II':'디아블로 투','3D':'삼차원'}))
    (p/'script/narration.ko.txt').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
    (p/'script/narration.en.txt').write_text('\n\n'.join(' '.join(x[1] for x in para) for para in paras)+'\n',encoding='utf8')
    plan=read(p/'planning/production-plan.json')
    plan.update(scriptFinalized=True,independentFootageViewed=slug.endswith('logic-separation'))
    plan['sourceMatchNotes']={'logic-separation':'Official independent paired gameplay captures viewed through sequential frames. Editorial comparison must be labelled classic/remastered and not represented as a captured live keypress.','input-adapter':'Official launch PC gameplay introduces the legacy mouse-based game. Controller-specific behavior is independently authored schematic supported by direct design-director explanation; no PC recording is labelled controller gameplay.'}
    plan['primarySources']=[plan['source'],'https://news.blizzard.com/en-us/article/23722094/bringing-the-original-diablo-ii-experience-to-console','https://diablo2.blizzard.com/en-us/']
    plan['sourceCorrections']=['No exact 25Hz claim. No claim that all later patches retain every 2021 rule.','Controller translation does not imply synthetic OS mouse events or a hidden real cursor. Automatic pathfinding is explicitly turned off for direct controller movement.']
    plan['footageReview']='Sequential frames reviewed; moving playback and actual narration sync remain pending.'
    save(p/'planning/production-plan.json',plan)
    chosen=[r for r in comparison if 'tristram_' in r['path'] or 'barracks_' in r['path']] if slug.endswith('logic-separation') else [broll]
    save(p/'sources/selected-footage.json',dict(sources=chosen,rightsReceipt='production/batches/distinctive-ten-shorts-20261025/blizzard-rights-receipt.json',controllerGifExcluded=dict(reason='600x337 below FHD; research only, not inserted',source='https://news.blizzard.com/en-us/article/23722094/bringing-the-original-diablo-ii-experience-to-console')))
    save(p/'production/checkpoint.json',dict(status='script-ready-visual-build',audio='waiting-for-user-game-exit',finalReview='pending',next='Build and inspect source-matched diagrams, then sync to actual narration PCM.'))
    sections=read(p/'production/section-plan.json')
    if slug.endswith('input-adapter'):
        for s in sections:s['kind']='game' if s['id']=='game' else 'diagram'
        save(p/'production/section-plan.json',sections)
for row in read(B/'batch.json')['projects']:
    p=R/'projects'/row['slug']/'production/finish-video.py'
    text=p.read_text(encoding='utf8')
    old="assert visual.is_relative_to(R), 'Use an owned recorded render.'"
    new="owned_media=Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025').resolve()\n    assert visual.is_relative_to(R) or visual.is_relative_to(owned_media), 'Use an owned recorded render.'"
    if old in text:p.write_text(text.replace(old,new),encoding='utf8')
print('Finalized two source-matched scripts; controller footage review still pending.')
