"""Prepare only D25 clarity-v3 and D29 botw-v4 metadata; no platform writes."""
from pathlib import Path
import datetime,hashlib,json,math

ROOT=Path(__file__).resolve().parents[4]
DEFAULTS=json.loads((ROOT/'shared/publishing/youtube-defaults.json').read_text('utf-8'))
KO_FOOTER=(ROOT/DEFAULTS['description']['channelDefaultSnapshot']).read_text('utf-8').split('📚 수업 노트')[0].strip()
EN_FOOTER=f"""🎮 Build games with real programming skills.

YamYamCoding is a Korean game-programming channel covering DirectX, Unity, Unreal Engine and computer graphics.

━━━━━━━━━━━━━━━━━━

🚀 Premium 1:1 programming coaching

Learn to design and implement real projects with guided feedback.
DirectX11 / DirectX12 · Unity / Unreal Engine · Computer Graphics & PBR · Shaders / Rendering · Game engines · Graphics papers and implementation

Programming coaching
{DEFAULTS['coaching']['url']}

━━━━━━━━━━━━━━━━━━

💬 YamYamCoding community

Questions, code reviews, feedback and course materials.

Discord
https://discord.gg/wZuqe7fqkR

YouTube channel membership
{DEFAULTS['membershipUrl']}

━━━━━━━━━━━━━━━━━━"""

SPECS={
 'limited-color-world':{
  'episode':'D25','revision':'clarity-v3','sha':'8503a0a610d9cd1d3f0e33af7db63c8762bd4b4662e637ea527e4b4d291311a5','seconds':400.3,'date':'2026-11-02',
  'titleKo':'색깔만으로 구분하는 게임, 왜 누군가는 못 할까? | 게임 디자인',
  'titleEn':'Why Color Alone Can Make a Game Unplayable | Game Design',
  'bodyKo':'같은 색 네 개를 연결하는 간단한 규칙도, 그 색을 알아보기 어렵다면 첫 판단부터 막힐 수 있습니다.\n뿌요뿌요 테트리스 2와 슈퍼 마리오브라더스 원더를 살펴보고, 같은 Unity 장면에서 색·밝기·배경·모양을 하나씩 바꿔 봅니다. 색각 시뮬레이션과 흑백 검사를 구분하고, 길과 목표를 읽기 쉽게 만드는 과정을 함께 확인합니다.',
  'bodyEn':'Even a simple rule—connect four pieces of the same color—can become difficult when the colors are hard to distinguish.\nUsing Puyo Puyo Tetris 2, Super Mario Bros. Wonder and a controlled Unity scene, we change color, lightness, backgrounds and shape cues one at a time. See how color-vision simulation differs from a grayscale check, and how clearer boundaries guide players toward the path and goal.',
  'chapterKo':['같은 색을 알아봐야 다음 수를 고른다','색 하나에 맡겼던 정보','색각 시뮬레이션과 흑백 검사의 차이','명도·배경·모양으로 구분하기','마리오의 색과 모양이 행동으로 이어지는 과정','Unity 장면을 흑백으로 바꿔 보기','다른 검사로 같은 정보를 확인하기','색이 달라도 다음 행동을 고를 수 있게'],
  'chapterEn':['Reading color before choosing a move','Information carried by color alone','Color-vision simulation versus grayscale','Lightness, backgrounds and shape cues','Turning Mario’s visual cues into actions','Testing the same Unity scene in grayscale','Different checks for the same information','Keeping the next action readable'],
  'hashtags':'#게임디자인 #게임개발 #접근성',
  'tags':['게임디자인','게임개발','색각','색각이상','접근성','명도','시각적 위계','뿌요뿌요 테트리스 2','슈퍼 마리오브라더스 원더','Unity','game design','color accessibility'],
  'creditsKo':'''게임 화면·이미지
Puyo Puyo Tetris 2 — GATA TV: https://www.youtube.com/watch?v=ot4gqysX29c
원녹화: Creative Commons Attribution license (reuse allowed). 발췌·편집·해설·표식 추가.
©SEGA Tetris ® ＆ © 1985～2020 Tetris Holding.
색 조정 기능과 공식 이미지: https://puyo.sega.jp/puyopuyotetris2/information.html
Super Mario Bros. Wonder — Nintendo 공식 게임 화면: https://www.nintendo.com/jp/switch/aqmxa/index.html
물음표 블록 플레이 — FUNHOUSE Guymer: https://www.youtube.com/watch?v=VovX8xDYqQA
원녹화: Creative Commons Attribution license (reuse allowed). 발췌·편집·해설·표식 추가. © Nintendo.

참고 자료
Masahiro Sakurai on Creating Games — Limited Color World: https://www.youtube.com/watch?v=obnjR8KJ9nk
Adobe 색각 교정: https://helpx.adobe.com/photoshop/desktop/print/soft-proof-for-color-blindness.html
색 하나에만 정보를 맡기지 않는 접근성 지침: https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/
Unity Color Adjustments: https://docs.unity.cn/Packages/com.unity.render-pipelines.universal%4017.4/api/UnityEngine.Rendering.Universal.ColorAdjustments.html

Unity 시연 에셋
RG Poly — Cartoon City Massive Pack / Characters (CC0): https://rg-poly.itch.io/cartoon-city-massive-pack-characters
RG Poly — Cute Dungeon Megapack (CC0): https://rg-poly.itch.io/cute-dungeon-megapack
EmacEArt — Low Poly Stylized Tiny Forest (상업적 이용 허용 에셋 라이선스): https://emaceart.itch.io/low-poly-stylized-tiny-forest

음악·제작 도구
Nimbus — Eveningland, YouTube Audio Library.
Unity 6000.6 / URP 17.6: https://unity.com/
FFmpeg: https://ffmpeg.org/
ElevenLabs 본인 음성 내레이션: https://elevenlabs.io/''',
  'creditsEn':'''Gameplay and images
Puyo Puyo Tetris 2 — GATA TV: https://www.youtube.com/watch?v=ot4gqysX29c
Recording license: Creative Commons Attribution license (reuse allowed). Excerpted and edited with commentary and annotations.
©SEGA Tetris ® ＆ © 1985～2020 Tetris Holding.
Official color-adjustment update and images: https://puyo.sega.jp/puyopuyotetris2/information.html
Super Mario Bros. Wonder — Nintendo official game footage: https://www.nintendo.com/jp/switch/aqmxa/index.html
Question-block gameplay — FUNHOUSE Guymer: https://www.youtube.com/watch?v=VovX8xDYqQA
Recording license: Creative Commons Attribution license (reuse allowed). Excerpted and edited with commentary and annotations. © Nintendo.

References
Masahiro Sakurai on Creating Games — Limited Color World: https://www.youtube.com/watch?v=obnjR8KJ9nk
Adobe color-vision proofing: https://helpx.adobe.com/photoshop/desktop/print/soft-proof-for-color-blindness.html
Color accessibility: https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/
Unity Color Adjustments: https://docs.unity.cn/Packages/com.unity.render-pipelines.universal%4017.4/api/UnityEngine.Rendering.Universal.ColorAdjustments.html

Unity demonstration assets
RG Poly — Cartoon City Massive Pack / Characters (CC0): https://rg-poly.itch.io/cartoon-city-massive-pack-characters
RG Poly — Cute Dungeon Megapack (CC0): https://rg-poly.itch.io/cute-dungeon-megapack
EmacEArt — Low Poly Stylized Tiny Forest (commercial-use asset license): https://emaceart.itch.io/low-poly-stylized-tiny-forest

Music and production tools
Nimbus — Eveningland, YouTube Audio Library.
Unity 6000.6 / URP 17.6: https://unity.com/
FFmpeg: https://ffmpeg.org/
ElevenLabs narration using the channel creator’s own voice: https://elevenlabs.io/''',
  'alternatives':['왜 어떤 게임은 색깔만 바뀌어도 어려워질까?','게임 화면을 흑백으로 바꾸면 보이는 문제들'],
  'choiceReason':'Names a concrete accessibility problem and preserves the existing selected project title. The full lesson covers color, lightness, patterns and hierarchy, not only the grayscale scene.',
  'pinned':'게임 화면의 색을 잠깐 빼 봤을 때도 길과 목표가 잘 구분되나요? 색·명도·모양 중 어떤 단서가 가장 도움이 됐는지 남겨 주세요.'
 },
 'kind-to-beginners':{
  'episode':'D29','revision':'botw-v4','sha':'bc9398d52e3cdef0827c5c27ee9f66120085b80d3be8058232dcaf988a94b7b3','seconds':410.3,'date':'2026-11-03',
  'titleKo':'게임을 처음 켠 친구가 다시는 안 하는 이유 | 초보자에게 친절한 게임 디자인',
  'titleEn':'Why Your Friend Quits After Their First Game | Beginner-Friendly Game Design',
  'bodyKo':'게임을 처음 해 보는 친구에게 가장 빠른 공략을 알려 주면 정말 더 재미있어질까요?\n젤다의 전설 브레스 오브 더 와일드(야숨)의 줍기·추위 대비, Unpacking의 간단한 조작, A Short Hike의 자유로운 탐험을 통해 첫 경험을 돕는 방법을 살펴봅니다. 함께 하는 목표를 맞추고, 조작의 부담을 덜고, 다음 선택은 플레이어에게 돌려주는 과정입니다.',
  'bodyEn':'Does giving a first-time player the fastest route really make the game more fun?\nWe look at picking up items and preparing for cold in The Legend of Zelda: Breath of the Wild, simple interactions in Unpacking, and free exploration in A Short Hike. Align expectations, reduce the burden of the first interaction, and give players room to make the next choice themselves.',
  'chapterKo':['첫 시도를 지키는 설계','숙련자와 초보자가 원하는 경험','전력 승부에도 전제가 있다','첫 조작에서 재미까지: 온보딩','야숨의 추위 대비: 방법과 선택','Unpacking: 조작은 가볍게, 선택은 직접','A Short Hike: 도움에서 손을 떼는 타이밍','작은 관심을 다음 한 판으로'],
  'chapterEn':['Protecting the first attempt','Different expectations on the same screen','Full-effort competition needs shared expectations','From first interaction to fun: onboarding','Preparing for cold in Breath of the Wild','Unpacking: simpler controls, personal choices','A Short Hike: knowing when to step back','Turning interest into another attempt'],
  'hashtags':'#게임디자인 #게임개발 #젤다의전설',
  'tags':['게임디자인','게임개발','초보자','온보딩','튜토리얼','젤다의전설','브레스오브더와일드','야숨','Unpacking','A Short Hike','Unity','game design','onboarding'],
  'creditsKo':'''게임 화면
젤다의 전설 브레스 오브 더 와일드 — Archive 64 / NintendoBlackCrisis (편집 재사용 허용 녹화):
https://www.youtube.com/watch?v=tOvTBrO7bPo
https://www.youtube.com/watch?v=kjSH8R2fk2c
© Nintendo. 녹화 발췌·해설·표식 추가.
Unpacking — Witch Beam 공식 출시 트레일러의 게임 장면: https://www.youtube.com/watch?v=vPcoMltTVXE
개발사 게임·접근성 정보: https://www.unpackinggame.com/
A Short Hike — Adam Robinson-Yu 공식 프레스 B-roll; 게임 음악 Mark Sparling: https://ashorthike.com/press/
걷기: https://drive.google.com/file/d/1kChFKZcZGahvm77NHO_GRV9m5nBl6LUu/view
오르기: https://drive.google.com/file/d/1FZseCzIJUoTpvR7_aMzYX_aFwYNoBTpY/view
활공: https://drive.google.com/file/d/19KPyBDCuXjes97EVx_uIFcWnn_tims0b/view

참고 자료
Masahiro Sakurai on Creating Games — Being Kind to Beginners: https://www.youtube.com/watch?v=R7rd4-ua2AI
Piggyback 공식 라이선스 야숨 가이드: https://www.piggyback.com/online-guide/the-legend-of-zelda/en/
한국어 정식 용어 확인: https://www.nintendo.com/kr/zelda/totk/guide/index.html

Unity 시연 에셋
RG Poly — Cartoon City Massive Pack / Characters (CC0): https://rg-poly.itch.io/cartoon-city-massive-pack-characters
RG Poly — Kitchen/Restaurant Megapack (CC0): https://rg-poly.itch.io/kitchenrestaurant-megapack
EmacEArt — Low Poly Stylized Tiny Forest (상업적 이용 허용 에셋 라이선스): https://emaceart.itch.io/low-poly-stylized-tiny-forest

음악·제작 도구
Nimbus — Eveningland, YouTube Audio Library.
Unity 6000.6 / URP 17.6: https://unity.com/
FFmpeg: https://ffmpeg.org/
ElevenLabs 본인 음성 내레이션: https://elevenlabs.io/''',
  'creditsEn':'''Gameplay
The Legend of Zelda: Breath of the Wild — Archive 64 / NintendoBlackCrisis (recordings supplied with permission for edited reuse):
https://www.youtube.com/watch?v=tOvTBrO7bPo
https://www.youtube.com/watch?v=kjSH8R2fk2c
© Nintendo. Excerpted with commentary and annotations.
Unpacking — game-screen excerpts from Witch Beam’s official launch trailer: https://www.youtube.com/watch?v=vPcoMltTVXE
Developer game and accessibility information: https://www.unpackinggame.com/
A Short Hike — official press B-roll by Adam Robinson-Yu; game music by Mark Sparling: https://ashorthike.com/press/
Walking: https://drive.google.com/file/d/1kChFKZcZGahvm77NHO_GRV9m5nBl6LUu/view
Climbing: https://drive.google.com/file/d/1FZseCzIJUoTpvR7_aMzYX_aFwYNoBTpY/view
Gliding: https://drive.google.com/file/d/19KPyBDCuXjes97EVx_uIFcWnn_tims0b/view

References
Masahiro Sakurai on Creating Games — Being Kind to Beginners: https://www.youtube.com/watch?v=R7rd4-ua2AI
Piggyback officially licensed Breath of the Wild guide: https://www.piggyback.com/online-guide/the-legend-of-zelda/en/
Official Korean terminology corroboration: https://www.nintendo.com/kr/zelda/totk/guide/index.html

Unity demonstration assets
RG Poly — Cartoon City Massive Pack / Characters (CC0): https://rg-poly.itch.io/cartoon-city-massive-pack-characters
RG Poly — Kitchen/Restaurant Megapack (CC0): https://rg-poly.itch.io/kitchenrestaurant-megapack
EmacEArt — Low Poly Stylized Tiny Forest (commercial-use asset license): https://emaceart.itch.io/low-poly-stylized-tiny-forest

Music and production tools
Nimbus — Eveningland, YouTube Audio Library.
Unity 6000.6 / URP 17.6: https://unity.com/
FFmpeg: https://ffmpeg.org/
ElevenLabs narration using the channel creator’s own voice: https://elevenlabs.io/''',
  'alternatives':['게임 가르쳐 주다가 친구의 재미를 빼앗는 순간','초보자를 돕다가 재미를 빼앗는 이유 | 야숨으로 보는 게임 디자인'],
  'choiceReason':'Preserves the existing project hook about the first-time friend. The topic suffix accurately names beginner-friendly design; expectations, onboarding and independent choices are all covered in order.',
  'pinned':'처음 게임을 배울 때 도움이 됐던 한마디, 반대로 재미를 줄였던 과한 공략이 있었나요? 여러분이 직접 알아냈을 때 가장 즐거웠던 순간도 남겨 주세요.'
 }
}

def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,text):p.write_text(text.rstrip()+'\n','utf-8')
def save(p,obj):write(p,json.dumps(obj,ensure_ascii=False,indent=2))
def stamp(s):return f'{int(s)//60:02d}:{int(s)%60:02d}'

def main():
 for slug,s in SPECS.items():
  p=ROOT/'projects'/slug;out=p/'publishing'/s['revision'];out.mkdir(parents=True,exist_ok=True)
  m=json.loads((p/'project.json').read_text('utf-8'));ep=p/'production'/s['revision']/'edit-plan.json';edit=json.loads(ep.read_text('utf-8'))
  video=ROOT/m['paths']['videoBurnedCaptions'];assert sha(video)==s['sha'];assert edit['totalFrames']/60==s['seconds']
  chapters=[]
  for i,c in enumerate(edit['scenes']):
   seconds=0 if i==0 else math.floor(c['startFrame']/60)
   chapters.append({'scene':c['id'],'startSeconds':seconds,'actualSceneStartFrame':c['startFrame'],'titleKo':s['chapterKo'][i],'titleEn':s['chapterEn'][i]})
  assert len(chapters)==8 and all(b['startSeconds']-a['startSeconds']>=10 for a,b in zip(chapters,chapters[1:]))
  desc={}
  for lang,footer,heading in [('ko',KO_FOOTER,'출처·자료 및 제작 도구'),('en',EN_FOOTER,'Sources, assets and production tools')]:
   cap=lang.title();body=s['body'+cap]+'\n\n'+('챕터'if lang=='ko'else'Chapters')+'\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['title'+cap] for c in chapters)+'\n\n'+s['hashtags']
   desc[lang]=body+'\n\n'+footer+'\n\n'+heading+'\n'+s['credits'+cap]
   assert len(desc[lang])<=5000 and len(s['title'+cap])<=100
   assert desc[lang].count(DEFAULTS['coaching']['url'])==1 and desc[lang].count(DEFAULTS['membershipUrl'])==1
   assert desc[lang].endswith(s['credits'+cap]) and '여기에-GitHub-주소'not in desc[lang]
   write(out/f'title.{lang}.txt',s['title'+cap]);write(out/f'description.{lang}.txt',desc[lang])
  subtitles=[]
  for lang,key in [('ko','captionsKo'),('en','captionsEn')]:
   q=ROOT/m['paths'][key];cues=q.read_text('utf-8-sig').count(' --> ');assert cues==113
   subtitles.append({'language':lang,'path':rel(q),'sha256':sha(q),'cues':cues,'method':'manual-file-upload-with-timing','status':'prepared-not-uploaded'})
  write(out/'tags.txt',', '.join(s['tags']))
  comment=s['pinned']+'\n\n직접 구현해 보고 막힌 부분을 함께 점검하고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해 보세요.\n'+DEFAULTS['coaching']['url'];write(out/'pinned-comment.ko.txt',comment)
  now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  receipt={'schemaVersion':1,'slug':slug,'episode':s['episode'],'revision':s['revision'],'status':'prepared-not-uploaded','preparedAt':now,'videoId':None,'video':{'path':rel(video),'sha256':s['sha'],'bytes':video.stat().st_size,'seconds':s['seconds'],'width':1920,'height':1080,'fps':60,'frames':edit['totalFrames'],'captioned':True,'metadataProbe':'Actual FFprobe width,height,60/1,frames,duration directly verified 2026-10-30.'},'authorization':{'userEvidence':['25,29편도 업로드 해줘~ 업로드 안됬으면','다음영상 다음일로 예약도 맞춰주고'],'selection':'Latest delivered D25 clarity-v3 and D29 botw-v4 exact hashes','actualWholeViewingOrListeningSeparatelyAsserted':False,'uploadRequested':True,'scheduleRequested':True,'deleteAuthorized':False},'metadata':{'title':s['titleKo'],'description':desc['ko'],'tags':s['tags'],'privacyStatus':'private','defaultLanguage':'ko','defaultAudioLanguage':'ko'},'englishMetadata':{'title':s['titleEn'],'description':desc['en']},'sourceCredits':{'ko':s['creditsKo'],'en':s['creditsEn']},'descriptionSourceCredits':{'policy':'description-sources-last-v1','position':'absolute-bottom','languages':['ko','en'],'evidence':m['paths']['scenePlan']},'subtitles':subtitles,'chapters':chapters,'chapterTiming':{'path':rel(ep),'sha256':sha(ep),'method':'Scene startFrame/60 floored to a whole second; first chapter intentionally00:00 includes original2s branding.'},'thumbnail':{'status':'root-owned-preparation-pending'},'coachingCard':{'url':DEFAULTS['coaching']['url'],'title':'프로그래밍 과외','teaser':'프로그래밍 과외','startSeconds':0,'status':'pending-platform-save'},'endScreen':{'startSeconds':s['seconds']-10,'endSeconds':s['seconds'],'elements':DEFAULTS['endScreen']['elements'],'status':'pending-platform-save','preserveMemberIdentityAndTitle':True},'pinnedComment':{'path':rel(out/'pinned-comment.ko.txt'),'status':'prepared-pending-publication','commentId':None,'pinnedVerified':False},'schedule':{'status':'target-only-not-saved','date':s['date'],'time':'09:00','timezone':'Asia/Seoul','basis':'Root inspected current Studio schedules and selected two available days after D27 Nov1, before existing lectures begin Nov4. D25 then D29; existing uploads preserved.'},'advertiserSelfAssessment':{'owner':'human-user','status':'pending-user-action-if-required','submittedByAgent':False},'actualPlatformState':{'uploadStarted':False,'settingsSaved':False,'scheduleSaved':False},'localMetadataVerification':{'sourceCreditsLast':True,'canonicalLinksExactlyOnce':True,'descriptionCharacters':{k:len(v)for k,v in desc.items()},'titleCharacters':{'ko':len(s['titleKo']),'en':len(s['titleEn'])},'cueCounts':{'ko':113,'en':113},'oldDraftsPreserved':True}}
  save(out/'youtube-upload.json',receipt)
  save(out/'title-selection.json',{'selected':{'ko':s['titleKo'],'en':s['titleEn']},'alternativesKo':s['alternatives'],'audience':'Game players and beginning game developers','reason':s['choiceReason'],'evidenceScenes':[c['scene']for c in chapters],'searchOrCtrBenefitGuaranteed':False,'selectionOnlyNoPlatformMutation':True})
  print(slug,rel(out),{k:len(v)for k,v in desc.items()},s['titleKo'])

if __name__=='__main__':main()
