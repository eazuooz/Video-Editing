"""Create the new character episode only after content and source gates."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;T=ROOT/'projects/character-parameters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 assert not p.exists(),f'Preserve existing {p}'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bank=json.loads((P/'source-action-bank-v1.json').read_text(encoding='utf-8'))
assert bank['sourceAdoptionApproved'] and not T.exists()
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
title='능력치는 어떻게 캐릭터의 개성을 만들까?'
enTitle='How Do Abilities Give a Character Its Identity?'
rows=[
('01-overview','숫자에서 플레이 방식으로',[
 '공격력과 속도만 다르면, 캐릭터의 플레이 방식도 달라질까요?',
 '라이벌즈 오브 이더의 대전과 고유 기술을 보고, 던전스 오브 이더의 능력치와 자원 변화를 비교하겠습니다.',
 '먼저 공통 동작에서 출발해, 강점과 약점이 어떤 선택을 만드는지 정리해 보죠.'
],[
 'Does changing attack power and speed automatically change how a character plays?',
 'We will examine combat and distinctive abilities in Rivals of Aether, then compare changes to stats and resources in Dungeons of Aether.',
 'Starting with shared actions, we will work out what choices a character’s strengths and limitations create.'
],'공통 행동→고유 규칙→상황별 선택을 서로 다른 높이의 투영된 세 블록과 연결 경로로 순서대로 드러낸다.'),
('02-common-baseline','공통 기준부터 만들기',[
 '이 대전에서는 두 캐릭터 모두 움직이고, 뛰고, 공격하며 발판을 오갑니다. 같은 게임을 한다는 공통 기준이 먼저 보이죠.',
 '이 기준 없이 모든 수치를 따로 정하면, 차이가 얼마나 큰지 비교하기도 어렵습니다. 먼저 누구나 할 수 있는 행동과 필요한 최소 성능을 정해 보세요.',
 '그다음 차이를 넣어야 합니다. 똑같은 공격 버튼을 눌러도 어느 거리에서 기회를 만들고, 어디로 이동하는지가 달라지는지 살펴보는 거죠.'
],[
 'Both fighters move, jump, attack and travel between platforms. Their actions first establish that they are playing the same game.',
 'If every value is chosen independently, even the size of a difference becomes hard to judge. Begin with shared actions and the minimum performance needed to use them.',
 'Then introduce differences. With the same attack button available, look at where each character creates an opportunity and where they choose to move.'
],'같은 높이의 공통 바닥 위에 이동·점프·공격의 투영 블록을 나란히 놓고, 비교할 캐릭터의 경로를 분기한다.'),
('03-rule-not-scale','숫자 밖의 차이',[
 '공식 플레이 장면에는 상대에게 남는 불 효과, 물과 거품, 연기처럼 서로 다른 현상이 등장합니다. 공격력을 조금씩 바꾸는 것과는 다른 차이죠.',
 '라이벌즈 오브 이더의 제터번과 오르케인을 보세요. 불이 붙은 상대를 보는 일과 물이 생긴 위치를 보는 일은, 플레이어가 주목할 정보를 다르게 만듭니다.',
 '고유 규칙을 설계할 때는 무엇이 달라지는지 먼저 쓰세요. 상대의 상태인지, 공간인지, 사용할 수 있는 행동인지가 분명해야 수치 조정도 의미를 갖습니다.'
],[
 'Official gameplay shows different phenomena: fire persisting on an opponent, water and bubbles, and smoke. These differences go beyond small changes to attack power.',
 'Look at Zetterburn and Orcane in Rivals of Aether. Watching a burning opponent and watching the location of water direct the player’s attention to different information.',
 'Before tuning a distinctive rule, name what it changes: the opponent’s state, a location or an available action. Clear rules give numerical tuning a purpose.'
],'상대 상태를 둘러싸는 고리와 공간에 놓인 물 타일을 다른 깊이에 투영하고, 상태 변화와 위치 변화의 화살표를 각각 움직인다.'),
('04-information-rule','상대가 읽는 정보도 바뀐다',[
 '포스번 장면에는 닮은 두 형체가 보이고, 뒤이어 연기가 인물을 가립니다. 상대가 어디를 보고 판단해야 하는지가 달라지는 예시입니다.',
 '이런 차이는 피해량 표 하나로 설명하기 어렵습니다. 공격이 강한지뿐 아니라 상대에게 어떤 판단을 요구하는지를 살펴봐야 하죠.',
 '다만 연기가 있다는 사실만으로 무적이라고 말할 수는 없습니다. 효과의 겉모습, 실제 판정, 상대가 대응할 방법은 나눠서 설계하고 확인해야 합니다.'
],[
 'Forsburn’s footage shows two similar figures, followed by smoke obscuring the fighters. It changes where an opponent must look to make a decision.',
 'A damage table alone cannot describe this difference. Ask not only how strong an attack is, but also what judgment it demands from the opponent.',
 'Smoke does not by itself prove invulnerability. Design and verify the appearance, actual interaction rules and available responses separately.'
],'앞·뒤 두 입체 인물 블록 사이에 연기 면을 이동시켜 실제 가림을 만들고, 관찰 방향을 바꾸면 보이는 부분이 달라지게 한다.'),
('05-useful-strength','강점이 선택을 바꾸는가',[
 '다시 대전을 보면 두 캐릭터가 지상과 공중, 발판 바깥을 오갑니다. 같은 기술도 서로 떨어진 거리와 현재 위치에 따라 쓰일 기회가 달라지죠.',
 '강점은 수치가 큰 항목이라는 설명에서 끝나면 부족합니다. 어떤 상황에서 유리한 선택을 만들고, 그 상황에 어떻게 들어가는지까지 연결해 보세요.',
 '예를 들어 가까이 붙어 압박하는 역할을 설계한다면, 접근 방법과 공격 뒤의 선택이 함께 필요합니다. 공격력만 올리고 접근할 수 없게 만들면 그 강점을 사용하기 어렵습니다.'
],[
 'The fighters travel across the ground, through the air and beyond the platform edge. Distance and position change the opportunities to use an ability.',
 'A strength needs more than a large number in a table. Connect it to an advantageous choice and to the means of reaching that situation.',
 'For a hypothetical close-pressure role, approach tools and choices after an attack belong together. Raising damage without any way to get close can leave that strength unusable.'
],'투영된 지상·높은 발판·바깥 공간의 높이를 구분하고, 근접 역할 블록이 경로를 따라 이동해 접근 가능/불가능을 비교한다. 수치는 설계 예시로 표시한다.'),
('06-role-and-limitation','약점에도 역할을 남기기',[
 '강점을 넣었다면 약점도 생각해야 합니다. 하지만 모든 능력을 낮춰 아무것도 할 수 없게 만드는 것은 개성 있는 약점과 다릅니다.',
 '화면처럼 위치가 계속 바뀌는 게임에서는, 불리한 거리에서 빠져나오거나 자신이 잘하는 거리로 돌아갈 선택이 있는지 확인할 수 있습니다.',
 '상대에게도 대응을 남겨 주세요. 유리한 상황을 만들기 위한 준비가 보이고, 실패했을 때 빈틈이 생기면 강점과 약점이 하나의 플레이 방식으로 연결됩니다.'
],[
 'Once a strength exists, consider its limitations. Reducing every ability until nothing works is different from giving a character a distinctive weakness.',
 'In a game with constantly changing positions, check whether a character can leave an unfavorable distance or return to a range where their tools are useful.',
 'Keep responses available to the opponent too. Readable preparation and openings after failure connect strengths and limitations into a coherent playstyle.'
],'넓은/좁은 통로의 투영된 벽과 경로를 비교한다. 역할 블록이 막힌 길 앞에서 다른 높이의 돌아오는 경로를 선택하게 움직인다.'),
('07-state-not-base','기본 성능과 현재 상태',[
 '경기 아래쪽의 퍼센트는 공격력 표가 아닙니다. 맞으면서 바뀌는 현재 피해 상태이고, 남은 목숨 수도 별도로 표시됩니다.',
 '캐릭터를 비교할 때는 기본 성능, 지금 걸린 효과, 플레이어의 판단을 구분해야 합니다. 한 순간의 높은 퍼센트만으로 그 캐릭터가 더 강하다고 판단하면 이유를 뒤섞게 됩니다.',
 '이 자료는 과거 경기입니다. 여기서는 실제 행동과 상태의 차이를 관찰하며, 지금의 캐릭터 순위나 보편적인 피해 배율을 계산하는 근거로 쓰지 않습니다.'
],[
 'The percentages at the bottom are not an attack-power table. They show current damage state, while remaining stocks are displayed separately.',
 'Separate base capabilities, active effects and player decisions when comparing characters. A high percentage in one moment cannot establish which character is stronger.',
 'This is historical match footage. We use it to observe actions and states, not to derive current character rankings or universal damage multipliers.'
],'기본값의 고정 입체 기둥과 변화하는 상태 토큰을 별도 깊이에 놓는다. 현재 상태 토큰만 이동하고 기본 기둥은 고정해 구분한다.'),
('08-resources-and-actions','기술이 능력치를 바꾸는 순간',[
 '던전스 오브 이더에서는 주사위와 기술이 전투 중 수치를 바꿉니다. 하미르의 리액트 장면은 방어 값이 바뀐 뒤 상대의 공격이 막히는 흐름을 보여 줍니다.',
 '슬레이드의 스틸은 맞힌 뒤 동전이 늘고, 아르테미스의 스턴은 상대의 주사위 상태에 영향을 줍니다. 서로 다른 장면이므로 하나의 연속 전투로 연결해서 읽지는 마세요.',
 '기술의 개성은 피해량에만 있지 않습니다. 방어, 자원, 상대의 선택지를 바꾸는 효과도 역할을 만들 수 있습니다. 이때 화면의 주사위 값은 해당 턴의 상태이지 영구 기본값이 아닙니다.'
],[
 'Dice and abilities change combat values in Dungeons of Aether. Hamir’s REACT sequence shows a defense change followed by a blocked enemy attack.',
 'Slade’s STEAL increases coins after connecting, while Artemis’s STUN affects the opponent’s dice state. These are separate shots, not one continuous battle.',
 'An ability’s identity is not limited to damage. Defense, resources and the opponent’s options can also define a role. The displayed dice values belong to the current turn, rather than permanent base stats.'
],'기술→현재 방어/동전/상대 주사위의 세 연결을 다른 입체 높이로 구분한다. DEF3→6 기둥이 실제로 높아지고, 자원 토큰과 상대 주사위가 각기 다른 방향으로 이동한다.'),
('09-condition-and-time','효과에는 조건과 시점이 있다',[
 '플릿의 스나이프 설명은 공격이 맞으면 피해를 주고, 다음 턴에 스태미나 주사위 두 개를 준다고 말합니다. 지금 스태미나가 즉시 여섯 늘었다는 뜻은 아닙니다.',
 '다른 보스 장면의 스트라이크는 공격에 맞춰 하트가 줄어드는 모습을 보여 줍니다. 같은 공격 효과처럼 보여도 무엇을 언제 바꾸는지는 따로 읽어야 하죠.',
 '설계 문장에도 발동 조건, 바뀌는 대상, 적용 시점을 함께 적어 보세요. 그래야 구현과 화면 설명이 서로 다른 규칙을 말하는 일을 줄일 수 있습니다.'
],[
 'Fleet’s SNIPE description says that connecting deals damage and grants two stamina dice on the next turn. It does not mean six stamina is added immediately to the current value.',
 'STRIKE in a separate boss shot shows a heart decreasing with the hit. Similar-looking attack effects still need separate descriptions of what changes and when.',
 'Write the trigger, affected target and application time together. This helps the implementation and the on-screen explanation describe the same rule.'
],'현재 턴과 다음 턴을 앞뒤로 투영한 두 플랫폼에 나눈다. 접촉 토큰은 현재 하트를 바꾸고 두 주사위는 다음 턴 플랫폼으로 이동해 시점을 비교한다.'),
('10-balance-preserves-role','조정하면서 개성 보존하기',[
 '차이가 있다고 해서 모든 조합이 공정해지는 것은 아닙니다. 반대로 모든 성능을 평균으로 맞춘다고 재미있는 차이가 남는 것도 아니죠.',
 '특정 상대나 장소에서 아무 대응도 못 하는지, 준비 없이 모든 상황을 해결하는지부터 확인해 보세요. 한 경기의 승패만 보고 전체 밸런스를 확정하지 말고 조건을 나눠 반복해서 검토해야 합니다.',
 '문제가 있는 조건과 수치를 고치되, 그 캐릭터가 무엇을 잘하는지는 남기는 겁니다. 조정 뒤에도 같은 역할을 한 문장으로 설명할 수 있는지 확인해 보세요.'
],[
 'Differences alone do not make every combination fair. Making every capability average does not automatically preserve interesting distinctions either.',
 'Check for opponents or locations with no workable response, and for tools that solve every situation without preparation. Review conditions across repeated tests rather than declaring balance from one match.',
 'Repair problematic conditions and values while preserving what the character does well. After a change, check whether the role still fits the same concise description.'
],'여러 상황 플랫폼에 역할 블록을 번갈아 놓아 대응 경로를 비교한다. 문제가 있는 한 경로만 조정하며 역할 기둥의 실루엣은 유지한다. 실제 밸런스 수치가 아닌 설계 도식이다.'),
('11-cost-and-summary','고유 규칙의 구현 비용',[
 '고유 규칙이 늘면 확인할 조합도 늘어납니다. 효과가 끝나는 순간, 다음 턴으로 넘어가는 순간, 다른 기술과 만나는 순간을 함께 다뤄야 합니다.',
 '불, 물, 연기처럼 구별되는 현상을 넣을 때도, 처음부터 예외를 끝없이 붙이기보다는 핵심 규칙을 짧게 정리해 보세요. 필요한 상태와 전환이 드러나면 테스트할 질문도 구체적이 됩니다.',
 '이 캐릭터는 어떤 상황에서 무엇으로 유리해지고, 상대는 어떻게 대응할 수 있는가. 이 문장을 팀원에게 설명할 수 있어야 기술과 능력치가 같은 방향으로 발전합니다.'
],[
 'More unique rules create more combinations to verify: an effect ending, a turn changing and an interaction with another ability.',
 'When adding distinct phenomena such as fire, water or smoke, begin with a concise core rule rather than an endless list of exceptions. Explicit states and transitions make test questions more concrete.',
 'In what situation does this character gain an advantage, through what tool, and how can an opponent respond? A shared answer keeps abilities and numerical tuning moving in the same direction.'
],'상태의 입체 노드를 공간에 배치하고 발동·유지·종료 경로를 움직여 연결한다. 조건이 추가될 때 검사 경로가 하나씩 늘어나는 비교를 한다.'),
('12-conclusion','한 문장으로 기억되는 역할',[
 '캐릭터의 개성은 숫자의 차이를 플레이어의 선택으로 연결할 때 선명해집니다. 공통 기준 위에 강점과 약점, 고유 규칙을 함께 놓아 보세요.',
 '기본 성능과 현재 상태를 구분하고, 효과의 조건과 시점을 정확히 적어 주세요. 쓸 수 없는 약점이나 모든 상황을 지배하는 강점은 고치면서도 역할은 남기는 겁니다.',
 '다음 캐릭터를 만들 때는 능력치 표부터 채우기 전에, 어떤 상황에서 어떤 선택으로 기억될지 한 문장으로 적어 보세요.'
],[
 'A character’s identity becomes clear when numerical differences create different player choices. Build strengths, limitations and distinctive rules on a shared baseline.',
 'Separate base capabilities from current state, and specify the conditions and timing of effects. Repair unusable weaknesses or universally dominant strengths while keeping the role intact.',
 'Before filling out the next character’s stat table, write one sentence about the situation and choice you want players to remember.'
],'공통 기준 위의 세 입체 요소가 역할 문장 아래로 모이되 서로 다른 높이와 면을 유지한다. 마지막에 조건·대응 경로를 순서대로 강조한다.')]
ko={'title':title,'language':'ko','independentlyWritten':True,'sourceResearchOnly':'zwiS1L6QVY0','scenes':[]}
en={'title':enTitle,'language':'en','independentlyWritten':True,'pairedSceneOrder':True,'scenes':[]}
for ident,st,kl,el,motion in rows:
 ko['scenes'].append({'id':ident,'title':st,'lines':kl})
 en['scenes'].append({'id':ident,'title':st,'lines':el})
put(T/'script/narration.ko.json',ko);put(T/'script/narration.en.json',en)
put(T/'sources/game-candidates.json',bank)
template=(ROOT/'templates/video-project/project.json').read_text(encoding='utf-8')
for a,b in {'{{SLUG}}':'character-parameters','{{TITLE_KO}}':title,'{{TITLE_EN}}':enTitle}.items():template=template.replace(a,b)
manifest=json.loads(template)
manifest['status']='independent-script-prepared-awaiting-direct-review'
manifest['engines']=['motion-canvas']
manifest['editing'].update(exampleSeconds=0,explanationStyle='research-black-v1',timingStatus='voice-not-yet-measured',
 sourceActionBank='production/batches/sakurai-planning-game-design/proof-character-parameters/source-action-bank-v1.json',
 sourceActionBankSha256=sha(P/'source-action-bank-v1.json'),maximumUniqueSourceSeconds=bank['maximumUniqueSeconds'])
manifest['editing']['captionStyle']['gameOneLineMaximumCharacters']=18
manifest['editing']['captionStyle']['requireMeasuredPixelWidth']=True
manifest['audio']['backgroundMusic'].update(approvalStatus='channel-approved-continuous-Nimbus',title='Nimbus',artist='Eveningland',
 file='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',source='YouTube Audio Library',
 license='Preserved channel approval; original-library-file human review pending',attribution='No public credit required in existing channel approval')
manifest['audio'].update(mixStatus='not-created',sourceAudioPolicy='exclude historical broadcast speech and source music; continuous approved Nimbus only',musicFallbackScenes=[r[0] for r in rows])
manifest['review']={'script':False,'narration':False,'mixedAsr':False,'allFinalPixels':False,'qa':False,'humanListening':False,'publicRights':False}
manifest['publishing'].update(actualId=None,uploaded=False,fullSettingsVerified=False,scheduleVerified=False,
 targetDate='2026-10-30',targetTime='09:00',timezone='Asia/Seoul',targetIsPlanOnly=True)
put(T/'project.json',manifest)
put(T/'planning/scene-intents-v1.json',{'schemaVersion':1,'timingMeasured':False,'style':'research-black-v1',
 'scenes':[{'id':r[0],'title':r[1],'paragraphs':3,'projectedMotion':r[4],'sourceWindows':[w['key'] for w in bank['windows'] if w['provisionalInsertion']==r[0]],'independentMotionCanvasSceneRequired':True} for r in rows]})
outline=['# '+title,'','이 영상은 캐릭터의 수치를 플레이 선택과 연결하는 설계 질문을 다룬다. 원본 강의는 연구에만 사용했으며 독립 한국어·영어 문단과 확보한 실제 행동을 바탕으로 구성했다.','',
 '고양이2초 다음 독립 안내3문장: 중심 질문=수치 차이가 플레이 방식의 차이를 만드는가; 얻는 점=강점·약점이 만드는 선택을 정리하기; 실제 순서=공통 대전 행동→불·물·연기 고유 규칙→던전의 능력치·자원/다음 턴 효과→역할과 조정. 첫 사례는 공통 이동·점프·공격으로 이어진다.20–30초는 계획이고 아직 음성 실측은0이다.','',
 '본편 실제60:설명40은 현재 목표다. 확보한19고유 행동 최대226.776667초를 넘겨 반복·저속으로 채우지 않는다. PCM 실측 뒤 장별 길이와 컷을 배정하고 부족하면 새 실제 행동을 검수한다. 설명을 유용하지 않게 줄여 비율을 맞추지 않는다.','',
 '설명은 검정research-black-v1이며 아래 모든 씬에서 실제 앞·옆·윗면, 원근·가림·의미 있는 비교를 움직인다. 고정 자막960,970은 유지하고 게임 큐는 한 줄18글자 이내 및 실제 폭을 확인한다. 최종 연속 움직임/자막/UI 승인은 아직 없다.','']
for r in rows:outline += ['## '+r[0]+' '+r[1],'',r[4],'','대응 실제 후보: '+', '.join(w['key'] for w in bank['windows'] if w['provisionalInsertion']==r[0])+'; 구체적 배정은 PCM 실측 후 확정.','']
outline += ['기본 성능/현재 피해·주사위 상태/판단을 구분한다. 역사 경기의 승패·퍼센트를 현재 순위나 피해 배율로 일반화하지 않는다. SNIPE는 다음 턴 두3STA 주사위이며 즉시현재+6STA가 아니다. STEAL은 동전/타격, STUN은 상대 주사위 변화이고 회피/재생을 증명하는 장면이 아니다. 적의 배치·조합은 원본 개념을 참고한 설계 도식으로만 설명하며 선정 몽타지가 배치 효과를 실험했다고 주장하지 않는다.','',
 '원본 고양이/회원12명 신원과10초 엔딩, 정확 제목, Nimbus를 보존한다. 사람 청취·발음·최종 공개권리·잘린 핸들 등은pending이다.09시 교대 예약은 완성·기술/게시검수·Git 전달 뒤 현재Studio/ledger의 미래 빈 디자인 날짜에 실제 저장하고 재열람한다. 목표10/30은 플랫폼 예약이 아니다.']
(T/'planning/outline.md').write_text('\n'.join(outline)+'\n',encoding='utf-8')
(T/'sources/SOURCES.md').write_text('# 검수한 실제 게임 자료\n\nRivals of Aether 공식 캐릭터 영상6개와 Aether Studios 공식 과거RCS 방송, Dungeons of Aether 공식 Switch Launch의 고유 전투5구간을 사용 후보로 채택했다. 정확 원본SHA/PTS/in-out/동작/도식 연결/최근 사용 및 선정·제외는 game-candidates.json과 proof source-action-bank-v1.json에 기록한다.\n\n공식 허용 페이지 https://aetherstudios.com/press-releases/ 의 상업/비상업방송·수익화 범위를 직접 읽었다. 원음과 음악은 채택하지 않는다. 최종 사람 권리 검토는pending이다. 원본연구JA글, 모든미디어/QA표본/권리화면은local-only다.\n',encoding='utf-8')
(T/'README.md').write_text('# '+title+'\n\n현재 독립12씬/36KOEN문단 준비. 원본 전체 연구 내용과 기존 내용/Studio 중복 검수 후 실제 게임 행동을 먼저 확보했다. 대본 직접대조와 GPU협력인계가 다음 단계이며 음성/실측/MC/최종QA/수집/업로드/예약/Git은 아직 완료되지 않았다.\n',encoding='utf-8')
put(P/'editorial-preparation-v1.json',{'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),
 'scenes':12,'pairedParagraphs':36,'koCharacters':sum(len(x) for r in rows for x in r[2]),'overviewCharacters':sum(map(len,rows[0][2])),
 'protectedEditorialInputs':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [T/'project.json',T/'script/narration.ko.json',T/'script/narration.en.json',T/'planning/outline.md',T/'planning/scene-intents-v1.json',T/'sources/game-candidates.json',P/'source-action-bank-v1.json']],
 'scriptDirectReviewApproved':False,'ttsStarted':False,'mcCreated':False,'measuredSeconds':None,'actualId':None,'rasterGitAdditions':0})
print(json.dumps({'scenes':12,'pairedParagraphs':36,'koCharacters':sum(len(x) for r in rows for x in r[2]),'overviewCharacters':sum(map(len,rows[0][2]))}))
