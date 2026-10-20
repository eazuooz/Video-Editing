"""Local drafts only. This script never calls a platform or uploads media."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/'production/local';D=P/'publishing';D.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def tm(s):m,s=divmod(round(s),60);h,m=divmod(m,60);return f'{h}:{m:02}:{s:02}' if h else f'{m:02}:{s:02}'
t=rd(L/'timing.json');defaults=rd(R/'shared/publishing/youtube-defaults.json')
titles=[{'ko':'재미있으면 괜찮을까? 뱀파이어 서바이버 vs D2 서바이버','en':'Does Fun Make It Okay? Vampire Survivors vs D2 Survivors','support':'Opening viewer question; gameplay/growth comparison followed by expression/permission distinctions and final creator question.'},{'ko':'규칙을 닮으면 표절일까? 디아블로 팬게임이 던진 질문','en':'Is a Similar Rule Plagiarism? The Question Behind a Diablo Fan Game','support':'Paragraphs31–43 distinguish gameplay rules, expression, creative combination and permissions without declaring a verdict.'},{'ko':'무료 팬게임이라면 괜찮을까? D2 서바이버를 보는 두 기준','en':'Is a Free Fan Game Okay? Two Ways to Look at D2 Survivors','support':'Paragraphs39–50 distinguish free access from permission and enjoyment from rights evaluation.'}]
chaptersKo=['재미와 권리, 두 질문','뱀파이어 서바이버와 매직 서바이벌','강해지는 경험의 설계','디아블로의 직업과 장비가 만나면','재미와 완성도는 별개','규칙·표현·이용허락 구분','같은 게임, 서로 다른 평가','팬게임의 가능성과 책임','내가 원래 게임의 개발자라면']
chaptersEn=['Two questions: fun and rights','Vampire Survivors and Magic Survival','Designing the feeling of power','Diablo classes and equipment','Fun versus polish','Rules, expression and permission','Different standards for the same game','Fan games: possibilities and responsibility','If you were the original developer']
ko='''디아블로 2의 직업과 장비가 서바이버류 전투를 만나면 어떤 재미가 생길까요?
Vampire Survivors, Magic Survival, 비공식 팬게임 D2 Survivors의 실제 장면을 비교하고, 규칙의 영향·구체적인 표현·자산 이용·이용허락을 나눠 살펴봅니다.
무료 배포와 정품 보유가 왜 이용허락과 다른 질문인지, 2026년10월21일 확인한 프로젝트 고지와 관련 자료를 바탕으로 설명합니다. 특정 게임의 침해 여부를 확정한 판결로 소개하지 않습니다.

'''
en='''What happens when Diablo II classes and loot meet survivors-style combat?
We compare actual footage of Vampire Survivors, Magic Survival and the unofficial fan game D2 Survivors, then distinguish influence on rules, concrete expression, asset use and permission.
Free distribution, ownership of a copy and permission are separate questions. Project notices and related sources were checked on October21,2026. This video does not present an infringement verdict on D2 Survivors.

'''
cks=['00:00 '+chaptersKo[0]];ces=['00:00 '+chaptersEn[0]]
for s,k,e in list(zip(t['scenes'],chaptersKo,chaptersEn))[1:]:cks.append(tm(s['start']+2)+' '+k);ces.append(tm(s['start']+2)+' '+e)
ko+='\n'.join(cks);en+='\n'.join(ces)
footerKo='''

프리미엄1:1 프로그래밍 코칭
https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328
게임 프로그래밍·DirectX·Unity·Unreal·그래픽스와 렌더링을 직접 설계하고 구현하는 실력을 함께 기릅니다.

얌얌코딩 커뮤니티
https://discord.gg/wZuqe7fqkR
YouTube 멤버십
https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join
'''
footerEn='''

Premium1:1 programming coaching
https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328
Build practical skills in game programming, DirectX, Unity, Unreal, graphics and rendering.

Yamyam Coding community
https://discord.gg/wZuqe7fqkR
YouTube membership
https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join
'''
credits='''

Sources / footage / credits
D2 Survivors project and legal notice (unofficial; not Blizzard-approved):
https://d2survivors.lol/
https://d2survivors.lol/legal/
D2 Survivors gameplay — Paco / framara:
https://x.com/framara/status/2110406793000321224
D2 Survivors gameplay — MrLlamaSC, “Diablo2VampireSurvivors”:
https://www.youtube.com/watch?v=KlxyIREH63M
Vampire Survivors gameplay — The Game Archivist, “Full Game Walkthrough | No Commentary”:
https://www.youtube.com/watch?v=bzYEU3rBD-Y
Magic Survival gameplay — Transcendent:
https://www.youtube.com/watch?v=oqTFK2ErLhg
Official Magic Survival listing — LEME:
https://play.google.com/store/apps/details?id=com.vkslrzm.Zombie
Developer interview — PC Gamer, March30,2022:
https://www.pcgamer.com/vampire-survivors-creator-didnt-have-a-vision-when-he-started-making-the-game-that-allowed-him-to-quit-his-job/
United States Copyright Office — Games:
https://www.copyright.gov/register/tx-games.html
Supreme Court of Korea,2019.6.27,2017다212095 (separate game case, not D2):
https://law.go.kr/LSW/precInfoP.do?precSeq=208504
Individual community reactions (not a representative poll):
https://www.reddit.com/r/diablo2/comments/1x7g4ss/have_you_ever_wondered_what_would_diablo_2_look/
Related reporting — KH Games / Next:
https://www.khgames.co.kr/news/articleView.html?idxno=309348
https://next.ink/brief-article/lidd-diablo-ii-rencontre-vampire-survivors-adieu-productivite/
Blizzard Video Policy (does not grant third-party recording permissions or approve the fan game):
https://www.blizzard.com/en-us/legal/dd76b654-f2c4-4aaa-ba49-ca3122de2376/blizzard-video-policy
Game artwork/audio remain with their respective rights holders. Limited excerpts are used for critical comparison and explanation; no blanket reuse license is claimed.
Music: Nimbus — Eveningland (YouTube Audio Library)
https://www.youtube.com/audiolibrary
https://www.youtube.com/watch?v=ZOc84gXN-lg
Original explanatory diagrams and brand assets — Yamyam Coding.
Tools: Motion Canvas (https://motioncanvas.io/), FFmpeg (https://ffmpeg.org/), own-voice narration via ElevenLabs (https://elevenlabs.io/), thumbnail illustration via OpenAI image generation (https://openai.com/).
Font: Noto Sans KR — Google Noto, SIL Open Font License (https://github.com/notofonts/noto-cjk).
'''
ko+=footerKo+credits;en+=footerEn+credits
assert len(ko)<5000 and len(en)<5000,(len(ko),len(en))
for language,text in [('ko',ko),('en',en)]:
 (D/f'description.{language}.txt').write_text(text,encoding='utf8')
wr(D/'plan.json',{'status':'prepared-local-only-pending-complete-video-human-review','candidates':titles,'selectedTitle':titles[0],'thumbnail':'production/local/thumbnail-v1.png','sourceCreditsPosition':'absolute-bottom-after-all-body-chapters-and-channel-footer','sourceCreditInventory':'production/edit-plan.json#sourceUsage and sources/research.json','privacyOnFutureAuthorizedUpload':'private','youtubeUploadAuthorized':False,'adSuitability':'human user evaluates personally','humanFinalReview':'pending','canonicalCoachingUrl':defaults['coaching']['url'],'settingsPending':['manual KO/EN subtitles','English title/description','00:00 coaching card','member10s end screen','user ad self-evaluation'],'automaticPublication':False,'automaticNextVideo':False})
print(json.dumps({'koCharacters':len(ko),'enCharacters':len(en),'chapters':len(cks),'platformMutations':0}),flush=True)
