"""Create an independent KO/EN production from the current reviewed action bank."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[4]; P=Path(__file__).resolve().parent
T=ROOT/'projects/limited-color-world'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):
    assert not p.exists(), str(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bank=json.loads((P/'source-action-bank-v1.json').read_text(encoding='utf-8'))
assert bank['sourceAdoptionApproved'] and not T.exists()
check=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode==0,check.stdout+check.stderr
title='색이 달라도 읽히는 게임 화면 만들기'
enTitle='Designing Game Screens That Remain Readable When Colors Differ'
rows=[
('01-overview','색 없이도 다음 행동을 읽을 수 있을까',[
 '게임에서 색을 구별하기 어렵다면, 어디로 가고 무엇을 누를지 여전히 알 수 있을까요? 오늘은 색에만 기대지 않는 화면을 만드는 방법을 살펴봅니다.',
 '치커리의 실제 플레이에서 집의 윤곽, 식물의 높이와 움직임, 어두운 공간의 대비를 차례로 보겠습니다.',
 '각 장면을 도식과 연결하면서 중요한 정보에 다른 단서를 더하는 방법을 정리해 볼게요. 먼저 색칠해도 사라지지 않는 집의 선부터 보죠.'
],[
 'If colors are difficult to distinguish, can players still tell where to go and what to interact with? We will examine screens that communicate through more than color.',
 'In actual Chicory gameplay, we will look at house outlines, plant height and motion, and contrast in dark spaces, in that order.',
 'We will connect these examples to diagrams and add other cues to important information. Let us begin with the lines that remain when a house is painted.'
],'앞·옆·윗면이 보이는 작은 집, 높이가 다른 식물 발판, 어두운 방을 앞뒤 깊이에 배치한다. 세 사례를 순서대로 움직여 강조하고 첫 집으로 시선을 연결한다.'),
('02-contours','색칠과 윤곽을 나누기',[
 '집과 길 위로 여러 색이 칠해집니다. 그런데 창문과 지붕, 길의 경계는 검은 선으로 계속 보이죠.',
 '색칠은 자유롭게 달라져도, 어디가 벽이고 어디가 길인지 알려 주는 구조가 남아 있는 겁니다.',
 '도식에서도 면의 색만 바꿔 보겠습니다. 선까지 함께 사라지면 구분이 어려워지지만, 윤곽을 남기면 서로 다른 면을 따라갈 수 있습니다.'
],[
 'Different fills are painted over the house and path. Black lines still mark the windows, roof and path edges.',
 'The paint can vary while the structure that distinguishes a wall from a path remains visible.',
 'In our diagram, we change the fills. Removing the outlines as well makes the surfaces harder to separate; retaining them lets us follow their boundaries.'
],'입체 집의 앞·옆·윗면을 투영한다. 각 면의 채움색을 바꾸는 동안 윤곽은 유지하고, 비교 집에서는 윤곽을 실제로 사라지게 해 경계 차이를 보여 준다.'),
('03-pattern-and-erasing','무늬도 정보를 남긴다',[
 '지붕을 칠하거나 지우는 장면에서는 빗금 무늬가 남습니다. 화면의 일부 칠이 지워져도 집의 구조를 읽는 단서가 이어지죠.',
 '색과 함께 모양이나 무늬를 쓰면, 한 가지 단서를 놓쳤을 때 다른 단서로 구별할 수 있습니다.',
 '예를 들어 두 장치를 색으로 나눈다면, 둥근 손잡이와 각진 손잡이처럼 형태도 다르게 줄 수 있습니다. 이 장치 비교는 실제 게임의 규칙이 아닌 설계 예시입니다.'
],[
 'Roof hatching remains while the house is painted or partly erased. These marks continue to communicate its structure as fills disappear.',
 'Shape or pattern can provide another way to distinguish things when a color cue is missed.',
 'For a hypothetical pair of devices, color can be accompanied by round and angular handles. This device comparison is our design example, rather than a rule shown in the game.'
],'집 지붕 윗면의 빗금과 채움 레이어를 다른 깊이로 분리한다. 지우는 면이 이동해 채움만 없애고, 이어 둥근/각진 손잡이가 있는 입체 장치 두 개를 회전시켜 형태 차이를 드러낸다.'),
('04-height-and-motion','높이와 움직임으로 읽는 발판',[
 '이번에는 버섯을 칠하자 위로 솟아오르고, 캐릭터가 그 위를 튕기며 이동합니다. 서로 다른 색으로 칠한 버섯에서도 이 흐름을 볼 수 있습니다.',
 '여기서 다음 행동을 읽는 단서는 특정 색의 이름만이 아닙니다. 발판의 높이와 윗면, 캐릭터가 이동하는 모습도 함께 보세요.',
 '도식에서는 낮은 발판이 올라오고, 위에 닿은 뒤 다시 줄어들게 하겠습니다. 상태가 바뀌는 모습 자체를 읽을 수 있도록 만드는 겁니다.'
],[
 'Painting raises the mushrooms, and the character bounces across them. The footage shows this sequence with mushrooms painted in different hues.',
 'A specific color name is not the only cue for the next action here. Look at platform height, the top surface and the character moving across it.',
 'Our diagram raises a low platform and then compresses it after contact. The state change itself becomes readable.'
],'서로 다른 색의 입체 버섯 발판을 배치하고 높이가 실제로 커지게 한다. 캐릭터 토큰이 윗면에 착지해 발판이 줄어드는 연속 운동을 보여 준다. 앞뒤 가림과 발판 사이 거리 유지.'),
('05-state-not-hue','현재 상태를 보여 주기',[
 '꽃을 칠하면 높이가 줄어들고 캐릭터가 건너갑니다. 다른 장면에서는 칠을 지우자 꽃이 다시 높아집니다.',
 '칠했는지와 지금 얼마나 높은지를 함께 보여 주는 셈입니다. 일부 식물은 이동 중 다시 높아지므로, 한 번 칠하면 길이 영구히 열린다고 읽으면 안 됩니다.',
 '게임 화면도 현재 상태를 알려 줘야 합니다. 색만 바뀌는 표시보다 높이, 윤곽, 움직임이 함께 바뀌면 상태를 확인할 단서가 늘어납니다.'
],[
 'Painting shortens flowers so the character can cross. In a separate shot, erasing the fill makes flowers taller again.',
 'The screen shows both whether paint is present and the current height. Some plants become tall again during traversal, so this is not evidence of a permanently unlocked path.',
 'A screen needs to communicate the current state. Changes in height, silhouette and motion provide additional cues alongside a changing color.'
],'입체 꽃의 칠 여부와 현재 높이를 별도 속성으로 나타낸다. 칠하기→낮아짐→이동→일부 다시 높아짐과 별도 지우기→높아짐을 분리된 경로로 움직여 표시한다.'),
('06-route-information','중요한 단서를 겹쳐 놓기',[
 '꽃 위를 건너는 동안에는 캐릭터와 발판 윗면, 도착할 턱의 경계가 중요합니다. 이 정보가 배경의 장식보다 잘 읽혀야 하죠.',
 '색의 수를 줄이는 것만으로 문제가 끝나지는 않습니다. 서로 다른 대상에 비슷한 모양을 주거나, 중요한 경계를 배경 무늬 속에 묻으면 여전히 헷갈릴 수 있습니다.',
 '무엇을 반드시 구별해야 하는지 먼저 정하고, 그 차이에 윤곽과 모양을 더해 보세요. 장식은 그 단서를 가리지 않는 쪽으로 정리하는 겁니다.'
],[
 'When crossing flowers, the character, platform tops and destination ledge matter. These need to read more clearly than background decoration.',
 'Reducing the number of colors alone is insufficient. Similar shapes for distinct objects, or important boundaries buried in background patterns, can still cause confusion.',
 'First identify what the player must distinguish. Add outlines and shape to that difference, then keep decoration from obscuring those cues.'
],'투영된 꽃 발판과 도착 턱 사이의 경로를 토큰이 이동한다. 장식 면이 뒤에서 앞으로 겹쳐 경로를 가렸다가 뒤로 물러나고, 윗면/턱 경계가 다시 드러나는 비교를 한다.'),
('07-local-contrast','어둠 속에서 대비를 남기기',[
 '어두운 동굴에서는 캐릭터 주변의 밝은 원과 그 안의 윤곽을 볼 수 있습니다. 주변 전체가 밝아지는 장면은 아닙니다.',
 '색이 비슷해 보여도 밝고 어두운 차이를 남기면 가까운 물체를 구별할 단서가 됩니다. 다만 어둡게만 만들면 보이던 경계도 사라질 수 있죠.',
 '도식에서 전경과 배경의 밝기를 비교해 보겠습니다. 분위기를 위한 어둠과, 움직일 대상을 읽는 대비를 함께 설계해야 합니다.'
],[
 'In the dark cave, a pale circle around the character reveals nearby outlines. The footage does not show the entire surrounding scene becoming bright.',
 'Lightness differences can help distinguish nearby objects even when hues appear similar. Simply making everything darker can also remove visible boundaries.',
 'We will compare foreground and background lightness in the diagram. Darkness for atmosphere and contrast for reading the moving objects need to be designed together.'
],'입체 동굴 앞 벽이 뒤쪽 방 일부를 가리고, 캐릭터 주변의 제한된 밝은 영역만 이동한다. 전경 물체와 배경의 명도를 따로 바꾸며 경계가 사라짐/남음 비교를 보여 준다.'),
('08-check-and-conclusion','색은 더하고 단서는 남기기',[
 '화면을 흑백이나 색 인지 미리보기로 확인하면 놓친 문제를 찾는 데 도움이 됩니다. 하지만 그 결과만으로 모든 플레이어가 잘 읽는다고 확정할 수는 없습니다.',
 '실제 플레이에서 대상과 상태를 구별하고 다음 행동을 선택할 수 있는지 확인해 보세요. 윤곽, 무늬, 높이와 움직임, 밝기 차이를 역할에 맞게 함께 쓰는 겁니다.',
 '색은 화면을 풍부하게 만들 수 있습니다. 중요한 정보는 색 하나에만 맡기지 말고, 색이 달라져도 남는 단서를 설계해 보세요.'
],[
 'Grayscale and color-perception previews can help find problems. Their results alone cannot establish that every player will read the screen successfully.',
 'Check whether players can distinguish the target and its state, then choose the next action during actual play. Combine outlines, patterns, height, motion and lightness differences according to their roles.',
 'Color can enrich a screen. Give important information other cues that remain when colors differ.'
],'앞의 집·꽃 발판·동굴 입체 도식을 서로 다른 깊이에 모은다. 색 채움만 단계적으로 줄인 뒤 윤곽/무늬/높이/밝기의 단서를 순서대로 움직여 강조한다. 미리보기는 검수 보조라고 표시한다.')]
ko={'title':title,'language':'ko','independentlyWritten':True,'sourceResearchOnly':'obnjR8KJ9nk','scenes':[]}
en={'title':enTitle,'language':'en','independentlyWritten':True,'pairedSceneOrder':True,'scenes':[]}
for ident,st,kl,el,motion in rows:
 ko['scenes'].append({'id':ident,'title':st,'lines':kl}); en['scenes'].append({'id':ident,'title':st,'lines':el})
put(T/'script/narration.ko.json',ko);put(T/'script/narration.en.json',en)
put(T/'sources/game-candidates.json',bank)
template=(ROOT/'templates/video-project/project.json').read_text(encoding='utf-8')
for a,b in {'{{SLUG}}':'limited-color-world','{{TITLE_KO}}':title,'{{TITLE_EN}}':enTitle}.items():template=template.replace(a,b)
manifest=json.loads(template);manifest['status']='independent-script-prepared-awaiting-direct-review';manifest['engines']=['motion-canvas']
manifest['editing'].update(exampleSeconds=0,explanationStyle='research-black-v1',timingStatus='voice-not-yet-measured',
 sourceActionBank='production/batches/sakurai-planning-game-design/proof-limited-color-world/source-action-bank-v1.json',sourceActionBankSha256=sha(P/'source-action-bank-v1.json'),maximumUniqueSourceSeconds=101.5)
manifest['editing']['captionStyle'].update(gameOneLineMaximumCharacters=22,requireMeasuredPixelWidth=True)
manifest['audio']['backgroundMusic'].update(approvalStatus='channel-approved-continuous-Nimbus',title='Nimbus',artist='Eveningland',
 file='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',source='YouTube Audio Library',
 license='Preserved channel approval; original-library-file human review pending',attribution='No public credit required in existing channel approval')
manifest['audio'].update(mixStatus='not-created',sourceAudioPolicy='exclude all official B-roll audio/music; continuous approved Nimbus only',musicFallbackScenes=[r[0] for r in rows])
manifest['review']={'script':False,'narration':False,'mixedAsr':False,'allFinalPixels':False,'qa':False,'humanListening':False,'publicRights':False}
manifest['publishing'].update(actualId=None,uploaded=False,fullSettingsVerified=False,scheduleVerified=False,targetDate='2026-11-01',targetTime='09:00',timezone='Asia/Seoul',targetIsPlanOnly=True)
put(T/'project.json',manifest)
put(T/'planning/scene-intents-v1.json',{'schemaVersion':1,'timingMeasured':False,'style':'research-black-v1',
 'scenes':[{'id':r[0],'title':r[1],'paragraphs':3,'projectedMotion':r[4],'sourceWindows':[w['key'] for w in bank['windows'] if w['provisionalInsertion']==r[0]],'independentMotionCanvasSceneRequired':True} for r in rows]})
outline=['# '+title,'','원본 강의는 개념 연구에만 사용했다. 영상·음성 복제나 전체 번역이 아니며, 공식 Chicory B-roll에서 직접 본 윤곽·상태·이동·대비를 독립 한영 문단과 입체 도식에 연결한다.','',
 '고양이2초 뒤 안내3문장: 중심 질문=색을 구별하기 어려워도 다음 행동을 읽을 수 있는가; 얻는 점=중요한 정보에 다른 단서를 더하기; 실제 순서=집의 윤곽→식물의 높이와 움직임→어두운 공간의 대비. 안내의 마지막은 첫 집 사례로 연결된다.20–30초는 계획이고 아직 실측0이다.','',
 '본편 실제60:설명40, 최대1프레임 오차는 아직 목표다. 확보한16고유 구간 최대101.5초/6090원본프레임을 정상1배속으로만 배정한다. 음성 실측 후 부족하면 추가 고유 행동을 검수하며, 유용한 설명·승인PCM을 줄이거나 반복/저속/무관idle로 채우지 않는다. 원본 두B-roll은 별도 장면이며 하나의 연속 플레이나 최적 경로를 증명하지 않는다.','',
 '검정research-black-v1의 실제 앞·옆·윗면, 높이, 원근과 가림을 움직여 비교한다. 고정 자막은960,970이고 실제 폭을 측정해 큐를 분할하거나 소스를 재구성한다.283표본의48px두줄 시험 승인과 현재 실제 내레이션/모든 연속 움직임 승인은 구별한다.','']
for r in rows:outline += ['## '+r[0]+' '+r[1],'',r[4],'','대응 실제 후보: '+(', '.join(w['key'] for w in bank['windows'] if w['provisionalInsertion']==r[0]) or '독립 입체 설명')+'; 정확 배정은 PCM 실측 뒤 확정.','']
outline += ['형태·무늬·명도·움직임은 보조 단서이지 모든 플레이어에게 접근성을 보장한 결과가 아니다. 특정 색의 정답/영구 해제/전체 칠 제거/전체 동굴 밝기 상승/최적 경로를 주장하지 않는다. 장치 손잡이는 가상 설계 비교이고 Chicory에 존재하는 장치 규칙이 아니다. 흑백과 색 인지 미리보기는 문제 찾기 보조이며 실제 플레이 검토를 대체하지 않는다.','',
 '원본 고양이120프레임과 원래12회원 신원/600프레임10초 엔딩 및 정확 제목, Nimbus를 보존한다. 사람 청취·발음·최종 공개권리·Nimbus원본·잘린 핸들·외부백업은pending. 완성 검수/게시설정/Git 전달 후 현재Studio/ledger의 같은 분류 미래 빈 날짜09Asia/Seoul로 저장·재열람한다.11/01은 목표이며 플랫폼 예약이 아니다.']
(T/'planning/outline.md').write_text('\n'.join(outline)+'\n',encoding='utf-8')
(T/'sources/SOURCES.md').write_text('# 실제 게임 자료\n\nChicory: A Colorful Tale 공식 개발사 press kit에서 제공한 B-Roll1/2의16고유 행동을 독립 해설 계획에 채택했다. 원본 전체decode와143coarse/76native/56trimmed 판을 직접 읽었고 원래16후보의1배속 재생 시작/종료를 확인했다. 실제 원본PTS와 정확경계,48px자막시험 프레이밍 표본은 봉인됐다. 수정 프레이밍의 브라우저 동적검수와 실제최종자막/UI는 아직pending이다.\n\n공식press kit: https://impress.games/press-kit/wishes/chicory-a-colorful-tale\n공식게임: https://www.chicorygame.com/\n제공폴더: https://www.dropbox.com/sh/kzu705qlt8g4rjz/AABZD35PdofcrbLTZbiE-83wa?dl=0\n\n제공 사실과 포괄적수익화라이선스를 구별한다. broad monetized reuse license 미관찰 및 최종사람공개권리pending을 유지한다. 원음/음악은 모두제외한다. 원본강의/전체연구JA/미디어/QA/권리화면은local-only다. 선정·제외·최근사용·모든native인아웃/행동/관찰점/도식연결은game-candidates.json에 기록했다.\n',encoding='utf-8')
(T/'README.md').write_text('# '+title+'\n\n독립8씬/24KOEN문단 준비.55프로젝트384입력의 전체관련본문/현재Studio중복검토와 공식실제행동을 확보한 뒤 작성했다. 대본 전체직접대조가 다음이며 음성실측/MC/믹스/최종QA/수집/업로드/예약/Git은 아직완료되지 않았다.\n',encoding='utf-8')
put(P/'editorial-preparation-v1.json',{'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'scenes':8,'pairedParagraphs':24,
 'koCharacters':sum(len(x) for r in rows for x in r[2]),'overviewCharacters':sum(map(len,rows[0][2])),
 'protectedEditorialInputs':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [T/'project.json',T/'script/narration.ko.json',T/'script/narration.en.json',T/'planning/outline.md',T/'planning/scene-intents-v1.json',T/'sources/game-candidates.json',P/'source-action-bank-v1.json']],
 'scriptDirectReviewApproved':False,'ttsStarted':False,'mcCreated':False,'measuredSeconds':None,'actualId':None,'rasterGitAdditions':0})
print(json.dumps({'scenes':8,'pairedParagraphs':24,'koCharacters':sum(len(x) for r in rows for x in r[2]),'overviewCharacters':sum(map(len,rows[0][2]))}))
