"""Draft the two architecture Shorts; source inspection must precede locking TTS."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

topics={
'shorts-d2r-renderer-logic-separation':{
 'title':'G키 하나로 20년 전 그래픽으로 돌아가는 비밀',
 'englishTitle':'One game, two looks: Diablo II Resurrected’s graphics toggle',
 'term':'게임 로직과 렌더링의 분리 · Separation of Game Logic and Rendering',
 'source':'https://www.well-played.com.au/all-things-diablo-ii-resurrected-blizzcon-insights-from-the-developers-bringing-hell-back-to-life/',
 'paragraphs':[
 [('같은 전투인데, 버튼 하나로 옛날 그래픽이 됩니다.','One battle switches to classic graphics with a button.'),('디아블로 투 레저렉션은 어떻게 이게 가능할까요?','How does Diablo II: Resurrected do this?')],
 [('게임에는 두 가지 일이 있습니다.','A game has two different jobs.'),('위치와 공격 결과를 계산하는 일,','One calculates positions and attack results.'),('그 결과를 화면에 그리는 일이죠.','The other draws those results on screen.')],
 [('레저렉션은 기존 게임의 동작 위에,','Resurrected builds on the underlying game.'),('새 삼차원 그래픽을 그리는 층을 얹었습니다.','A new layer renders it in 3D.'),('위치와 행동을 받아 새 모델로 보여주는 거예요.','It presents the positions and actions using new models.')],
 [('우리 그림에서 캐릭터가 한 칸 움직이면,','In our diagram, move the character one cell.'),('옛 모습과 새 모습이 같은 위치를 따라갑니다.','Both appearances follow the same position.'),('그리는 방식이 달라져도, 움직임의 기준은 하나죠.','The presentation changes; the underlying state is shared.')],
 [('그래서 화면을 전환해도,','That is why switching the view'),('충돌과 길 찾기의 기준은 이어집니다.','preserves the underlying collision and pathfinding rules.'),('같은 게임 상태를 다른 모습으로 보는 거예요.','You see the same game state through another presentation.')],
 [('이것이 게임 로직과 렌더링의 분리입니다.','This is separation of game logic and rendering.'),('익숙한 게임의 동작 위에, 새로운 화면을 입힌 거죠.','A new visual layer wraps the familiar game behavior.')]
 ],
 'sections':['game','jobs','layer','state','confirm','close']
},
'shorts-d2r-controller-input-adapter':{
 'title':'패드로 조작하는데, 속에서는 옛 마우스 게임이 돌아간다?',
 'englishTitle':'A controller talks to an old mouse-driven game: Diablo II Resurrected',
 'term':'입력 변환 계층 · Input Adaptation Layer',
 'source':'https://www.playstationlifestyle.net/2021/09/21/behind-diablo-ii-resurrected-authenticity-developer-interview/',
 'paragraphs':[
 [('패드로 움직이는 디아블로 투.','Diablo II, controlled with a gamepad.'),('그런데 속의 오래된 게임은 마우스와 키보드를 기준으로 돌아갑니다.','Its legacy game was built around mouse and keyboard.'),('어떻게 연결했을까요?','How do the two connect?')],
 [('원작은 클릭한 곳으로 이동하고,','In the original, you click a destination'),('선택한 적에게 행동하는 게임이었죠.','or act on a selected enemy.'),('패드의 스틱과 버튼은 입력 방식부터 다릅니다.','Sticks and buttons provide a different kind of input.')],
 [('그래서 둘 사이에 통역을 놓았습니다.','So the developers put a translator between them.'),('패드의 조작을, 기존 게임이 이해하는 입력으로 바꿔 주는 거예요.','It translates controller actions into input the existing game understands.')],
 [('우리 도식에서 스틱을 오른쪽으로 움직이면,','In our diagram, push the stick right.'),('변환 계층을 지나 이동 명령으로 이어집니다.','It passes through an adaptation layer to a movement command.'),('버튼 입력도 해당 행동에 연결하죠.','A button press is connected to its action.')],
 [('버튼 배치와 스킬 사용은 패드에 맞게 다듬습니다.','Buttons and skill use are also tailored to the controller.'),('입력을 옮기는 일과 조작감을 다듬는 일이 함께 가는 거예요.','Input translation and comfortable controls work together.')],
 [('정리하면, 새 조작기와 기존 게임 사이에 입력 변환 계층을 둔 겁니다.','An input adaptation layer connects a new device to the existing game.'),('통역을 붙여, 익숙한 게임을 다른 손맛으로 즐기게 한 거죠.','That translator lets familiar gameplay work with a different device.')]
 ],
 'sections':['game','original','adapter','commands','confirm','close']
}}
for slug,d in topics.items():
    p=R/'projects'/slug
    for folder in ['script','planning','sources','production/local','publishing']:(p/folder).mkdir(parents=True,exist_ok=True)
    assert not (p/'project.json').exists(), 'Do not overwrite an existing project'
    lines=[' '.join(x[0] for x in para) for para in d['paragraphs']]
    clauses=[dict(id=f'p{i+1}-{j+1}',lineIndex=i,spoken=ko,ko=ko.replace('디아블로 투','디아블로 II').replace('삼차원','3D'),en=en) for i,para in enumerate(d['paragraphs']) for j,(ko,en) in enumerate(para)]
    save(p/'script/narration.spoken.ko.json',dict(slug=slug,revision='distinctive-ten-v1',scenes=[dict(id='main',lines=lines)]))
    (p/'script/narration.ko.txt').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
    save(p/'script/clauses.json',dict(clauses=clauses,pronunciationAliases={'디아블로 II':'디아블로 투','3D':'삼차원'}))
    save(p/'production/section-plan.json',[dict(id=section,paragraph=i,firstCue=f'p{i+1}-1',purpose=section,kind='game' if section in ['game','confirm'] else 'diagram') for i,section in enumerate(d['sections'])])
    save(p/'project.json',dict(slug=slug,title=d['title'],format=dict(type='youtube-shorts',width=1080,height=1920,fps=60),video=dict(width=1080,height=1920,fps=60),status='preproduction',currentRevision='distinctive-ten-v1',currentFinalDirectory='production/local/final-reviewed-v1',authorizationId='explicit-ten-distinctive-shorts-20261025',paths=dict(script=f'projects/{slug}/script/narration.spoken.ko.json',checkpoint=f'projects/{slug}/production/checkpoint.json',productionPlan=f'projects/{slug}/planning/production-plan.json'),publishReady=False))
    save(p/'planning/production-plan.json',dict(slug=slug,revision='distinctive-ten-v1',independentFootageViewed=False,scriptFinalized=False,source=d['source'],sourceRead='Direct developer explanation read in full relevant section; independently phrased mechanism',terminology=d['term'],renderer='Motion Canvas',rendererReason='Architecture and input translation are abstract state relationships; a progressive running 2D diagram makes the shared state visible without claiming recovered game internals.',boundaries=['2021 launch architecture; no exact simulation frequency claim','Illustrated arrows/values are explanatory, not a game debugger capture','Actual input/view transition must be verified before finalizing associated narration'],footageReview='pending-official-broll',audio=dict(engine='Qwen3-TTS-12Hz-1.7B-Base',voice='shared/voice-reference/reference-15-35s.wav',speechSpeed=1,bgm='Pixel Peeker Polka - faster; existing CC BY4.0 file',gpu='wait-until-user-game-exits'),humanReview='pending'))
    save(p/'production/checkpoint.json',dict(status='draft-script-and-visual-planning',next='Inspect official FHD gameplay for the exact narrated behavior; then lock source cuts/script and create voice.'))
    (p/'publishing/title.ko.txt').write_text(d['title']+' | 디아블로2 게임개발 #Shorts\n',encoding='utf8')
    (p/'publishing/title.en.txt').write_text(d['englishTitle']+'\n',encoding='utf8')
    save(p/'production/visual-config.json',dict(headline=d['title'],term=d['term'],sections=d['sections'],renderer='Motion Canvas',gameLabel='디아블로 II: 레저렉션 · 출시 버전'))
print('Drafted two architecture scripts; footage and final narration gates remain open.')
