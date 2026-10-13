# Historical draft: running it would overwrite the current independently sourced script.
raise SystemExit('Superseded draft. Read the current narration.ko.json / narration.en.json and final-timeline-v1.json. No regeneration from this historical source plan.')
from pathlib import Path
import json, copy, datetime
ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/hierarchical-game-outlines'; OUT=Path(__file__).parent
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
rows=[
('01','생각을 찾을 수 있는 구조','A structure for finding ideas',[
'아이디어를 많이 적었는데, 정작 필요한 내용을 찾기 어렵다면 어떻게 할까요?',
'이번에는 사쿠라이가 소개한 계층형 아웃라인의 순서대로, 게임 메뉴의 묶음에서 출발해 글의 단계를 나누고, 필요한 부분만 펼쳐 보겠습니다.',
'그다음 캐릭터의 기술 설명을 한 묶음으로 옮겨 보고, 다른 사람이 읽을 문서로 정리하는 데까지 이어가겠습니다.'
],[
'What if you have written down many ideas but cannot find the one you need?',
'Following the progression of Sakurai’s lesson on hierarchical outlines, we will start with groups in a game menu, organize text into levels, and expand only the parts we need.',
'Then we will move a character’s move description as one branch and prepare the information for someone else to read.'
]),
('02','메뉴에서 글의 계층으로','From menus to text levels',[
'아웃라인은 큰 항목 아래에 작은 항목을 넣어, 글의 포함 관계를 드러내는 방식입니다. 여기서 계층은 중요도 순위가 아니라, 어느 설명이 어디에 속하는지를 뜻합니다.',
'사쿠라이가 든 게임은 슈퍼 스매시브라더스 얼티밋입니다. 화면의 큰 메뉴를 고르면 그 안의 선택지가 나타납니다.',
'지금은 기록 메뉴 안에서 통계와 대전 데이터를 나누어 보여 줍니다. 큰 제목이 먼저 범위를 정하고, 하위 항목이 그 범위를 자세히 나누는 것이죠.'
],[
'An outline places smaller items under larger ones to make their grouping visible. Here, a level shows where an explanation belongs, rather than how important it is.',
'Sakurai’s game example is Super Smash Bros. Ultimate. Selecting a main category reveals choices inside it.',
'The Records menu groups statistics and battle data. The parent sets the scope, while its children divide that scope into more specific parts.'
]),
('03','필요한 가지를 따라 내려가기','Following the relevant branch',[
'설정이라는 큰 묶음에는 소리와 밝기, 언어처럼 서로 다른 선택지가 있습니다. 소리를 열면 다시 음악과 효과음, 목소리를 조절하는 항목이 보입니다.',
'글도 이렇게 정리할 수 있습니다. 설정을 첫 단계에, 소리를 그 아래에, 효과음 크기를 한 단계 더 아래에 두는 겁니다.',
'들여쓰기 하나가 관계를 보여 줍니다. 소리와 밝기는 나란한 항목이고, 효과음 크기는 소리의 세부 항목입니다. 메뉴의 내부 코드를 설명하는 것이 아니라, 글을 묶는 방법을 비교하는 예입니다.'
],[
'Options contains different choices such as sound, brightness, and language. Inside Sound, the controls distinguish music, sound effects, and voices.',
'We can organize text the same way: Options at the first level, Sound below it, and sound-effect volume one level deeper.',
'Indentation makes the relationship visible. Sound and Brightness are peers, while effect volume belongs under Sound. This is an analogy for organizing text, not a claim about the game’s internal code.'
]),
('04','캐릭터에서 기술의 세부로','From a fighter to move details',[
'메뉴를 이해했다면, 이제 캐릭터의 기술 설명에 같은 방법을 적용해 보죠. 게임 안에서도 미 파이터의 설정 아래에 여러 필살기 항목이 모여 있습니다.',
'설명용 문서에는 캐릭터, 필살기, 개별 기술 순서로 제목을 만듭니다. 한 기술 아래에는 입력 방법과 동작, 결과를 적습니다.',
'가령 버튼을 어떻게 누르는지와 그 뒤 어떤 동작이 나오는지는 같은 기술의 세부 설명입니다. 여기서는 실제 게임의 수치나 개발사의 기획서를 재현하지 않고, 항목을 묶는 구조만 보여 줍니다.'
],[
'Now apply the same approach to a fighter’s moves. The game also groups several special moves inside the Mii Fighter settings.',
'In our illustrative document, the levels are Fighter, Special Moves, and an individual move. Under that move, we write its input, action, and result.',
'How to press the button and what action follows are details of the same move. We are illustrating document structure, not recreating measured game values or Nintendo’s internal design document.'
]),
('05','접기와 이동은 다른 작업','Collapsing and moving a branch',[
'기술이 많아지면 모든 세부 사항을 동시에 읽을 필요는 없습니다. 제목 아래 내용을 접으면 큰 목록을 살피기 쉬워지고, 다시 펼치면 설명이 그대로 나타납니다.',
'접기는 삭제가 아닙니다. 지금 보이는 범위만 바뀝니다. 반대로 순서를 바꾸고 싶을 때는 제목과 그 아래 설명을 한 묶음으로 옮깁니다.',
'옆으로 한 단계 옮기면 소속이 달라집니다. 같은 층으로 올린 것인지, 다른 제목의 아래에 넣은 것인지 확인하세요. 순서 이동과 단계 변경을 구분하면 내용이 엉뚱한 곳에 붙는 일을 줄일 수 있습니다.'
],[
'When the move list grows, you do not need to read every detail at once. Collapse the details to scan the headings, then expand them to reveal the same content.',
'Collapsing does not delete anything; it changes what is visible. To change the order, move the heading together with its subordinate content.',
'Changing the level changes the grouping. Check whether an item became a peer or moved under another heading. Distinguishing order changes from level changes helps avoid misplaced explanations.'
]),
('06','워드에서 시작하는 방법','Starting in Word',[
'이 기능을 써 보기 위해 특별한 기획 도구부터 만들 필요는 없습니다. 데스크톱 워드에서는 보기 탭의 개요 보기에서 문서의 단계를 다룰 수 있습니다.',
'먼저 큰 제목과 작은 제목을 구분한 뒤, 표시할 단계를 줄여 전체 구조를 보고 필요한 가지를 펼쳐 보세요.',
'프로그램과 버전에 따라 조작 위치는 다를 수 있습니다. 중요한 것은 글자를 크게 보이게 만드는 일이 아니라, 제목과 하위 내용의 관계를 지정하는 것입니다.'
],[
'You do not need to build a special planning tool to try this. In desktop Word, Outline view under the View tab lets you work with document levels.',
'Assign the main headings and subheadings, display fewer levels to inspect the overall structure, and expand the branch you need.',
'The controls may differ by program and version. The essential step is assigning the relationship between headings and their content, rather than merely making text larger.'
]),
('07','내 작업 메모와 전달 문서','Working notes and a document for others',[
'사쿠라이는 오래전부터 이런 방식으로 자신의 생각을 정리해 왔다고 설명합니다. 그 경험을 우리 이야기처럼 바꾸기보다, 작업 방법의 차이에 주목해 보겠습니다.',
'내가 생각을 발전시키는 메모에는 아직 결정하지 못한 질문도 남을 수 있습니다. 반면 다른 사람에게 전달하는 문서는 무엇이 결정됐고, 어디를 읽어야 하는지 분명해야 합니다.',
'같은 기술 설명이라도 작업 중에는 입력과 결과를 따로 비교하고, 전달할 때는 제목과 설명을 읽는 순서대로 다듬습니다. 구조를 잡는 도구와 완성된 문서의 표현은 같을 필요가 없습니다.'
],[
'Sakurai describes using this approach to organize his ideas over many years. Rather than presenting his experience as ours, let us focus on the distinction between the two kinds of document.',
'Working notes can contain questions that are still unresolved. A document for someone else should make the decisions and the reading path clear.',
'For the same move, working notes may separate input and result for comparison. A handoff document arranges the headings and explanation for the reader. The organizing tool and the final presentation need not look identical.'
]),
('08','작은 목록부터 직접 정리하기','Try it with a small list',[
'이 방법은 게임 기획서에만 쓰이지 않습니다. 사쿠라이도 채널의 주제와 내용을 정리하는 데 아웃라인을 사용한다고 소개합니다.',
'여러분도 작은 목록 하나를 골라 보세요. 큰 제목 아래에 관련 항목을 넣고, 한 가지의 세부 내용을 펼쳤다가 다시 접어 보는 겁니다.',
'제목만 읽어도 원하는 설명을 찾을 수 있나요? 그렇다면 목록이 단순히 길어진 것이 아니라, 생각을 찾아가고 고칠 수 있는 구조가 된 것입니다.'
],[
'This method is not limited to game design documents. Sakurai also describes organizing the topics and content of his channel with outlines.',
'Try a small list of your own. Place related items under a heading, expand one branch to inspect its details, then collapse it again.',
'Can you find the explanation you want from the headings alone? If so, you have more than a long list: you have a structure for finding and revising ideas.'
])]
ko={'language':'ko','scenes':[{'id':i,'title':k,'lines':a} for i,k,e,a,b in rows]};en={'language':'en','scenes':[{'id':i,'title':e,'lines':b} for i,k,e,a,b in rows]}
for language,d in [('ko',ko),('en',en)]:save(OUT/f'narration.{language}.json',d)
base=json.loads((P/'project.json').read_text('utf-8-sig'));manifest=copy.deepcopy(base)
manifest['paths']['script']=(OUT/'narration.ko.json').relative_to(ROOT).as_posix();manifest['tts'].update(outputDir=(OUT/'narration').relative_to(ROOT).as_posix(),filenameStem='hierarchical-reference-v1',maxRenderAttempts=1)
save(OUT/'voice-manifest.json',manifest)
design=[]
for i,k,e,a,b in rows:
 design.append({'id':i,'title':k,'contentRole':['overview','menu-parent-children','levels','fighter-specifications','collapse-reorder-relevel','Word-outline','notes-versus-handoff','broader-use'][int(i)-1], 'palette':'research-paper-white-v1','captionCenter':[960,970],'captionReservedY':[894,1080], 'narrationParagraphs':3, 'visual':'Full-screen observed menu footage interleaved with a projected document branch; no fabricated game UI or internal-engine claims.', 'timing':'Current measured voice word/paragraph landmarks will drive each reveal; no fixed letter-count final timing.'})
plan=json.loads((P/'planning/production-plan.json').read_text('utf-8-sig'));plan['scripts']={'ko':(OUT/'narration.ko.json').relative_to(ROOT).as_posix(),'en':(OUT/'narration.en.json').relative_to(ROOT).as_posix(),'status':'paired-independent-draft-awaiting-capacity-and-cue-design'};plan['sceneDesigns']=design;plan['updatedAt']=now();save(P/'planning/production-plan.json',plan)
print('Prepared 8 source-aligned scenes /24 bilingual paragraphs; pending source timing/capacity, no TTS started.')
