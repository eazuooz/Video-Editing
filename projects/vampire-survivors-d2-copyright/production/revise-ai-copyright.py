"""Selected, reversible editorial revision; no platform actions or full voice regeneration."""
from pathlib import Path
import json, datetime, hashlib, shutil

R=Path(__file__).resolve().parents[3]; P=R/'projects/vampire-survivors-d2-copyright'
V=P/'production/revision-ai-copyright-v2'; V.mkdir(exist_ok=True)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def rd(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

CHANGES={
2:("바로 비공식 팬게임, D2 서바이버입니다. 제작자는 이 프로젝트에 클로드와 여러 AI 에이전트를 활용하는 작업 방식을 공개했습니다. 게임을 만들기는 쉬워졌는데, 다른 게임의 그림과 소리도 쉽게 가져다 써도 되는 걸까요?",
   "This is the unofficial fan game D2 Survivors. Its creator shared a workflow using Claude and multiple AI agents on this project. Making games has become easier, but does that make it okay to take artwork and sound from other games?"),
3:("오늘은 먼저 이 게임들이 만드는 재미를 살펴보고, 규칙을 배우는 것과 실제 자산을 이용하는 것의 차이를 정리하겠습니다. 그 차이를 바탕으로, AI로 개발할 때 놓치기 쉬운 저작권 확인까지 함께 생각해 보겠습니다.",
   "First, we will look at what makes these games fun, then distinguish learning from rules from using actual assets. With that distinction in mind, we will consider the copyright checks that can be overlooked when developing with AI."),
4:("AI로 만든 게임을 판단하기 전에, 게임끼리 영향을 주고받는다는 사실부터 짚어 보겠습니다. 장르를 대중화한 뱀파이어 서바이버도, 앞선 다른 게임에서 영감을 받았기 때문입니다.",
   "Before judging a game developed with AI, let us start with the fact that games influence one another. Vampire Survivors, which popularized the genre, was itself inspired by an earlier game."),
30:("하지만 AI의 도움으로 그 재미를 구현했다고 해서, 사용한 그림과 소리의 권리까지 해결되지는 않습니다. 만들 수 있다는 것과 공개해도 된다는 것은 다른 질문입니다. 이제 그 차이를 구체적으로 나눠 보겠습니다.",
    "Implementing that fun with AI assistance does not settle the rights to the artwork and sound being used. Being able to build something and being allowed to release it are different questions. Let us now examine that distinction more closely."),
38:("이 구분은 AI 개발에서도 그대로 중요합니다. AI가 게임 코드를 새로 작성해 줬어도, 연결한 기존 게임의 그림과 음악까지 사용하도록 허락해 준 것은 아닙니다. 구매한 에셋도 마찬가지로, 허용된 용도와 조건을 따로 확인해야 합니다.",
    "This distinction matters just as much in AI development. Even if AI writes new game code, it does not grant permission to use the existing game artwork and music connected to that code. Purchased assets also require a separate check of their permitted uses and conditions."),
44:("이것만으로 D2 서바이버의 침해 여부나 제작자의 의도를 단정할 수는 없습니다. 여기서 주목할 것은 AI 사용 자체가 아니라, 제작이 쉬워질수록 자산의 출처와 허락 확인이 뒤로 밀릴 수 있다는 점입니다. 이 기준을 가지고 이용자들의 반응도 살펴보겠습니다.",
    "These facts alone do not establish infringement by D2 Survivors or its creator's intentions. The concern here is not AI use itself, but the risk of checking asset origins and permissions too late as development becomes easier. Let us also consider player reactions with that distinction in mind."),
51:("AI는 개인이나 작은 팀도 떠올린 게임을 실제로 구현할 기회를 넓혀 줍니다. 오래된 게임을 새로운 방식으로 만나게 하고, 원래 작품에 관심을 돌릴 가능성도 있습니다. 그래서 필요한 것은 가능성을 닫는 일보다, 무엇을 확인하고 공개할지 구분하는 일입니다.",
    "AI gives individuals and small teams more opportunities to turn a game idea into something playable. It can offer new ways to experience older games and renew interest in the originals. Rather than closing off those possibilities, we need to distinguish what must be checked before a release."),
55:("예를 들어 AI에게 게임 코드를 작성하게 하고, 내가 가진 게임 파일을 읽어 오게 했다고 해 보겠습니다. 코드가 작동하는지 확인하는 것과, 그 파일을 이런 프로젝트에 사용해도 되는지 확인하는 것은 별개의 작업입니다. 코드와 그림, 음악의 출처를 나누어 적고, 각 사용 조건과 필요한 표기를 확인해야 합니다. 허락이 불명확한 자산은 사용 가능한 다른 자산으로 바꾸거나 권리자에게 확인하는 편이 좋습니다.",
    "For example, suppose you ask AI to write game code that reads game files you own. Checking whether the code works and checking whether those files may be used in this project are separate tasks. Record the origins of the code, artwork and music separately, and check their conditions and required credits. If permission for an asset is unclear, use a suitable alternative or ask the rights holder."),
57:("그러나 AI로 만들었다는 말 하나로, 영향과 복제의 경계가 사라지지는 않습니다. 규칙에서 배운 점, 구체적인 표현의 유사성, 실제 이용한 자산과 허락을 각각 확인해야 합니다. AI가 얼마나 많이 작업했는지와는 별개의 질문입니다.",
    "Saying a game was made with AI does not erase the distinction between influence and copying. We still need to examine what was learned from its rules, similarities in concrete expression, and the assets actually used and their permissions. These questions are separate from how much work AI performed."),
58:("재미있는 결과물이 나왔다는 것과, 책임 있게 공개할 준비가 됐다는 것은 다릅니다. AI의 개발 능력이 좋아질수록, 사람에게는 무엇을 썼고 어떤 조건으로 썼는지 설명할 수 있는 판단이 더 중요해집니다.",
    "Creating something fun and being ready to release it responsibly are different achievements. As AI becomes better at development, human judgment about what was used and under which conditions becomes increasingly important."),
59:("여러분이 AI와 함께 게임을 만든다면, 공개 버튼을 누르기 전에 그 질문에 답할 수 있을까요? 반대로 오랫동안 만든 내 게임의 그림과 음악이 다른 프로젝트에 등장했다면, 어떤 조건이라야 받아들일 수 있을지도 생각해 보세요.",
    "If you build a game with AI, could you answer those questions before pressing the publish button? And if artwork and music from a game you spent years making appeared in another project, consider which conditions would make that acceptable to you.")}

if not (V/'baseline.json').exists():
 paths=['project.json','script/narration.ko.json','script/narration.spoken-ko.json','script/narration.en.json','production/edit-plan.json','production/checkpoint.json','production/master-files.json','production/audio-review.json','production/review-ledger.json','planning/production-plan.json','publishing/plan.json']
 rows=[]
 for rel in paths:
  src=P/rel; dst=V/'baseline'/rel; dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);rows.append({'path':rel,'sha256':sha(src)})
 wr(V/'baseline.json',{'createdAt':now,'files':rows,'master':'production/local/final.captioned.mp4','masterSha256':sha(P/'production/local/final.captioned.mp4'),'localMediaPreservedInPlace':True,'userReview':'not-approved; user selected editorial revision'})

ko=rd(V/'baseline/script/narration.ko.json'); en=rd(V/'baseline/script/narration.en.json')
old=[x for s in ko['scenes'] for x in s['lines']]; n=0; mapping=[]
for sk,se in zip(ko['scenes'],en['scenes']):
 for j in range(len(sk['lines'])):
  n+=1
  if n in CHANGES:
   sk['lines'][j],se['lines'][j]=CHANGES[n]
   mapping.append({'paragraph':n,'scene':sk['id'],'before':old[n-1],'after':sk['lines'][j],'english':se['lines'][j]})
ko['scenes'][0]['title']='AI로 만들면 공개해도 괜찮을까?';en['scenes'][0]['title']='Built with AI: ready to publish?'
ko['scenes'][-2]['title']='AI 개발의 가능성과 권리 확인';en['scenes'][-2]['title']='AI development: possibilities and rights checks'
ko['scenes'][-1]['title']='공개하기 전에 답해야 할 질문';en['scenes'][-1]['title']='Questions to answer before publishing'
wr(P/'script/narration.ko.json',ko);wr(P/'script/narration.en.json',en)
spoken=json.loads(json.dumps(ko));
for s in spoken['scenes']:
 s['lines']=[x.replace('D2','디투').replace('2019년','이천십구년').replace('AI','에이아이') for x in s['lines']]
wr(P/'script/narration.spoken-ko.json',spoken)
flat=[x for s in spoken['scenes'] for x in s['lines']]
(V/'tts-changed-only.txt').write_text('\n\n'.join(flat[i-1] for i in CHANGES),encoding='utf8')
(V/'narration-continuous.ko.txt').write_text('\n\n'.join(x for s in ko['scenes'] for x in s['lines']),encoding='utf8')
sources=rd(P/'sources/research.json')
primary={'id':'d2-ai-workflow','url':'https://x.com/framara/status/2110666711867548028','kind':'developer-primary','browserActualRead':True,'observedAt':now,'claims':['Creator states Claude with swarms of agents plus Linear workflow. Expanded attached image explicitly names Projects / D2 Survivors and D2-specific tasks.','Creator replies just claude to a question about other AI.'],'corroboratingReply':'https://x.com/framara/status/2110673033950081347','scopeLimit':'Claude-assisted D2 development verified. Exact model/version, duration, percentage of AI work and AI-generated artwork not established.','mediaUse':'research/reference only; independently authored workflow explanation, no reuse of X screenshots planned'}
sources['sources']=[s for s in sources['sources'] if s['id'] not in ['d2-ai-workflow','anthropic-commercial-terms']]+[primary,{'id':'anthropic-commercial-terms','url':'https://www.anthropic.com/legal/commercial-terms','kind':'primary-terms','checkedAt':now,'claims':['Output ownership between service provider and customer is not a third-party game-asset license.'],'mediaUse':'research only; no full terms quotation or legal verdict'}];wr(P/'sources/research.json',sources)
revision={'id':'ai-copyright-awareness-v2','requestedAt':now,'userEvidence':'AI 게임 개발의 부작용(저작권)인식의 관점에서 영상을 다시 조금 다듬어야 할거같아.','scope':'Selected video only through complete local final review; no upload/next video.','centralQuestion':'AI로 게임을 만들기 쉬워진 지금, 만들 수 있다는 것과 공개해도 된다는 것을 구분하고 있는가?','confirmedAiEvidence':primary,'changedParagraphs':list(CHANGES),'changes':mapping,'unchangedParagraphs':[i for i in range(1,61) if i not in CHANGES],'approvedUnchangedPcm':'preserve source samples exactly; replace changed paragraphs only at verified speech-safe joins','structure':'Retain gameplay/inspiration/growth/familiarity/polish/rules-expression-permissions/reactions/possibilities/conclusion order; AI framing and practical checks beside relevant passages.','claimsNotMade':['D2 is legally adjudicated infringement','AI use itself is infringement','all assets or all code AI-generated','specific Claude model/version or development duration','all users or AI developers ignore copyright'],'visualChanges':[{'paragraph':3,'kind':'overview-ai','meaning':'AI development -> fun analysis -> asset origin and permission'},{'paragraph':30,'kind':'ai-rights','meaning':'working code versus asset use permission'},{'paragraph':55,'kind':'ai-checklist','meaning':'code/art/music provenance -> permitted use/credits -> release decision'},{'paragraph':57,'kind':'ai-conclusion','meaning':'AI contribution and copyright checks are separate axes'},{'paragraph':59,'kind':'ai-questions','meaning':'publish as developer; consider original asset creator'}],'humanListening':'pending','finalReview':'pending'}
wr(V/'revision.json',revision)
plan=rd(P/'planning/production-plan.json');plan['selectedEditorialRevision']=revision;plan['updatedAt']=now;wr(P/'planning/production-plan.json',plan)
project=rd(P/'project.json');project['status']='selected-editorial-revision-in-production';project['titles']={'ko':'AI로 만들면 다 내 게임일까? D2 서바이버와 저작권','en':'Does AI Make It All Yours? D2 Survivors and Copyright'};project['selectedRevision']=revision['id'];project['publishReady']=False;wr(P/'project.json',project)
control=rd(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
control['newProductionAuthorization']['latestRevision']={'id':revision['id'],'userEvidence':revision['userEvidence'],'scope':revision['scope'],'requestedAt':now};wr(R/'shared/publishing/video-production-control.json',control)
wr(P/'production/checkpoint.json',{'schemaVersion':1,'slug':P.name,'updatedAt':now,'revision':revision['id'],'stage':'script-and-primary-ai-evidence-revised','status':'in-progress','jobs':[],'blockers':[],'nextAction':'Generate only11 changed paragraphs in approved ElevenLabs Sample B, preserve all unchanged PCM; revised visuals and final local review.','baselineMasterSha256':rd(V/'baseline.json')['masterSha256'],'humanWholeListening':'pending','humanFinalReview':'pending','automaticNextVideo':False})
print(json.dumps({'changedParagraphs':list(CHANGES),'unchangedCount':60-len(CHANGES),'ttsCharacters':len((V/'tts-changed-only.txt').read_text(encoding='utf8')),'revision':str(V)},ensure_ascii=False))
