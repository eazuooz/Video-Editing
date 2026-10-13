"""Current user-requested text. Historical research attribution stays in its records."""
from pathlib import Path
import json,sys,datetime,hashlib
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent;ROOT=P.parents[3];PREV=P.parent/'reference-preserving-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'narration.ko.json').exists()
ko=read(PREV/'narration.ko.json');en=read(PREV/'narration.en.json')
ko['scenes'][0]['lines']=[
'포켓몬 초기작을 기획한다고 생각해 볼까요? 이동과 전투, 몬스터볼 사용을 한 줄 목록에 섞으면 원하는 규칙을 찾기 어렵습니다.',
'이번에는 기획 메모를 큰 항목과 세부 항목으로 묶어 보겠습니다.',
'포켓몬 문서 예시로 이유를 이해하고, 게임 메뉴와 기술 설명에서 접기와 이동을 익힌 뒤, 전달할 문서로 다듬겠습니다.']
en['scenes'][0]['lines']=[
'Imagine planning an early Pokémon game. Mixing movement, battles, and Poké Ball use in one flat list makes a specific rule hard to find.',
'We will organize those notes into headings and subordinate details.',
'We will start with an illustrative Pokémon document, use game menus and move descriptions to learn folding and moving, and then prepare a document for a reader.']
ko['scenes'][1]['lines'][1]='슈퍼 스매시브라더스 얼티밋의 메뉴를 예로 들어 보죠. 화면의 큰 메뉴를 고르면 그 안의 선택지가 나타납니다.'
en['scenes'][1]['lines'][1]='Take the menus in Super Smash Bros. Ultimate. Selecting a main category reveals the choices inside it.'
ko['scenes'][6]['lines'][0]='아웃라인으로 구조를 잡았다면, 이제 누가 읽을 문서인지 생각해 보세요. 아이디어를 발전시키는 작업 메모와 다른 사람에게 건네는 문서는 목적이 다릅니다.'
en['scenes'][6]['lines'][0]='Once the outline has a structure, consider who will read it. Notes for developing ideas and a document handed to someone else serve different purposes.'
ko['scenes'][7]['lines'][0]='이 방법은 게임 기획서에만 쓰이지 않습니다. 영상 주제와 세부 설명을 묶거나, 공부할 내용과 질문을 정리할 때도 사용할 수 있습니다.'
en['scenes'][7]['lines'][0]='This method is not limited to game design documents. It also helps group video topics and explanations, or organize study material and questions.'
ko['scenes'].insert(1,dict(id='01a',title='포켓몬 기획 메모를 계층으로 묶기',lines=[
'화면은 포켓몬 초기작을 소재로 만든 설명용 기획문서입니다. 실제 개발사의 원본은 아닙니다.',
'게임 규칙을 탐험과 전투로 나눈 뒤, 전투 아래에 기술 선택과 아이템 사용을 둡니다. 몬스터볼의 사용 조건과 처리 결과는 아이템 사용 아래의 같은 가지에 넣습니다.',
'포획 규칙을 수정하려면 이제 그 가지만 펼치면 됩니다. 관련 조건과 결과를 함께 찾고, 다른 규칙과 섞이거나 일부를 빠뜨릴 위험도 줄일 수 있죠.']))
en['scenes'].insert(1,dict(id='01a',title='Grouping Pokémon planning notes into levels',lines=[
'This is an illustrative planning document based on an early Pokémon game, not an original document from its developer.',
'Divide the rules into Exploration and Battles. Under Battles, place Move Selection and Item Use. Put the conditions and results for using a Poké Ball together under Item Use.',
'To revise the catching rule, expand that branch. You can find the related conditions and results together, reducing the risk of mixing them with unrelated rules or overlooking a detail.']))
for lang,j in [('ko',ko),('en',en)]:
 assert not any(name in json.dumps(j,ensure_ascii=False).lower() for name in ['사쿠라이','sakurai','桜井'])
 write(P/f'narration.{lang}.json',j)
changed={'01':None,'01a':None,'02':1,'07':0,'08':0};requests=[]
for s in ko['scenes']:
 if s['id'] not in changed:continue
 p=changed[s['id']];requests.append(dict(id=s['id'] if p is None else s['id']+'p'+str(p+1).zfill(2),title=s['title'],lines=s['lines'] if p is None else [s['lines'][p]],targetScene=s['id'],replaceParagraph=None if p is None else p+1))
write(P/'tts-request.ko.json',dict(scenes=requests))
manifest=read(PREV/'voice-manifest.json');manifest['paths']['script']=(P/'tts-request.ko.json').relative_to(ROOT).as_posix();manifest['tts'].update(outputDir=(P/'generated-narration').relative_to(ROOT).as_posix(),maxRenderAttempts=1,filenameStem='hierarchical-pokemon-opening-v2')
write(P/'voice-manifest.json',manifest)
write(P/'script-review.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='draft-awaiting-selected-native-source-review',changedRequests=changed,unchangedScenes=['03','04','05','06'],unchangedParagraphsPreservedByQuietBoundarySplice=True,personalExperienceRemoved=True,referenceNamesInNarration=0,referenceNamesInCaptionsRequired=0,pokemonDocument='independently authored illustration, never described as original developer material',actualGameClaims='generic menu/action relationships; no catch probabilities or implementation claims',sourceViewRequiredBeforeTts=True))
print('Prepared paired 9-scene narration; 5 bounded new TTS requests, unchanged voice reuse planned.')
