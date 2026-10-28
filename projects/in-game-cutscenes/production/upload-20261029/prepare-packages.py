"""Prepare only the four user-approved uploads; no platform or source-media changes."""
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SLUGS=['computer-controlled-players','in-game-cutscenes','start-with-climax','respect-player-time']
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

DATA={
'computer-controlled-players':{
 'episode':'D26','introKo':'컴퓨터가 모든 공격을 완벽하게 막고 피하면, 정말 좋은 상대가 될까요? 스매시브라더스 얼티밋과 다이시 던전에서 정보·판단·공정함·반응 시간·공략할 빈틈을 살펴봅니다.\n\nUnity 시연으로 거리와 판단 우선순위, 반응 지연이 행동을 어떻게 바꾸는지 보여줍니다. 두 칸·세 칸과 12프레임은 원리를 설명하는 예시이며 실제 게임의 측정값이 아닙니다.',
 'introEn':'Would an opponent that blocks and dodges perfectly actually be fun to fight? Super Smash Bros. Ultimate and Dicey Dungeons illustrate information, decisions, perceived fairness, reaction time and openings a player can exploit.\n\nOriginal Unity demonstrations show how distance, priorities and response delays change behavior. The two-/three-square distances and 12-frame delay are illustrative values, not measurements of either game.',
 'alternatives':['게임 AI는 왜 완벽하게 싸우지 않을까? | 게임 디자인','너무 잘하는 게임 AI가 재미없는 이유','플레이어가 공략할 수 있는 AI는 어떻게 만들까?'],
 'reason':'반응 지연과 공격이 만드는 빈틈을 중심 질문으로 연결하며, 일부러 지는 AI라는 과장 없이 본문 전체를 포괄한다.',
 'tags':['게임디자인','게임AI','게임개발','CPU','스매시브라더스 얼티밋','다이시 던전','Game AI','Game Design','얌얌코딩'],
 'chapterEn':['What matters beyond winning','Movement and human-like decisions','When dice feel unfair','Reading the situation as data','Distance changes the decision','Conflicting priorities','Reaction time and mistakes','Attacks create openings','Designing a good opponent'],
 'credits':['Super Smash Bros. Ultimate CP gameplay — TallestBrake3: https://www.youtube.com/watch?v=I3LV8o_xhR8 (Creative Commons Attribution; excerpted and annotated).','Nintendo official fighter gameplay — Mario: https://www.youtube.com/watch?v=INk1W8OujQI ; Samus: https://www.youtube.com/watch?v=I9tcvSeemVo','Dicey Dungeons: Reunion — Terry Cavanagh: https://www.youtube.com/watch?v=fVsWXAAccVg','Super Smash Bros. Ultimate mode information: https://www.smashbros.com/en_US/howtoplay/mode.html','Dicey Dungeons official information: https://terrycavanaghgames.com/dice/presskit/desktop/'],
 'thumbnail':'로봇 상대가 공격을 크게 내밀고 빈틈을 보인다. 검정·주황·흰 얌얌 고양이가 그 빈틈을 발견해 반격하려는 독립 삽화. 작은 방패 아이콘을 줄줄이 배열하지 말고 하나의 대결 상황. 큰 문구: 완벽한 AI는 / 재미없다? 핵심 AI·재미없다 빨강 강조. 실제 게임 캐릭터 복제나 영상 캡처는 사용하지 않는다.',
 'hash':'99784ebcf48de6160b023c469cc3d06f0ddef655a28eebca25b8f5a4346261fe'},
'in-game-cutscenes':{
 'episode':'D27','introKo':'멋진 장면인데도 왜 자꾸 넘기고 싶어질까요? 하데스 II와 모여봐요 동물의 숲의 대화 장면을 보며, 컷신이 이야기·감정·휴식·보상과 이어지는 방법을 살펴봅니다.\n\n실시간 컷신과 프리렌더링 영상의 차이부터 재생 속도, 구간 이동, 전체 스킵, 퀵 타임 이벤트(QTE)까지. 장면의 길이뿐 아니라 플레이어가 받아들이는 속도와 다음 행동을 함께 설계합니다.',
 'introEn':'Why do we sometimes want to skip a beautiful cutscene? Dialogue in Hades II and Animal Crossing: New Horizons shows how directed scenes connect story, emotion, rest and rewards to play.\n\nWe examine real-time and pre-rendered cutscenes, playback speed, section navigation, full skips and quick time events (QTEs). The goal is to design both the scene and the player’s way of experiencing it.',
 'alternatives':['멋진 컷신인데 왜 자꾸 넘기고 싶을까? | 게임 연출과 스킵 설계','공들인 컷신을 플레이어가 넘기는 이유','컷신의 길이보다 먼저 설계해야 할 것'],
 'reason':'좋은 화면 품질만으로 시청 의욕이 생기지 않는다는 도입과, 감정·휴식·재생 선택으로 이어지는 본문에 정확히 대응한다.',
 'tags':['게임디자인','컷신','게임연출','스킵','QTE','하데스2','동물의숲','Cutscene','Game Design','얌얌코딩'],
 'chapterEn':['Image quality and the role of cutscenes','What happens during a long scene','Directing attention','Two ways to provide rest','Watching a scene as a reward','Dialogue units and playback control','Let players choose the pace','A new save is not a first viewing','Quick time events and the next action'],
 'credits':['Hades II © Supergiant Games. Gameplay: Boneless Walkthroughs — Hades 2 - Walkthrough Part 1 (No Commentary): https://www.youtube.com/watch?v=U1jS0lrW_4k — CC BY; excerpted and annotated. Recording uses the 2024 early-access version.','Hades II official game page: https://www.supergiantgames.com/games/hades-ii/','Animal Crossing: New Horizons © Nintendo. Gameplay: LongplayArchive / SpectreBull: https://www.youtube.com/watch?v=kfiiYm3iuKY — excerpted and annotated.'],
 'thumbnail':'얌얌 고양이가 웅장한 이야기 장면을 기다리다 컨트롤러의 건너뛰기 버튼에 손을 올리는 상황. 영화 스크린이나 실제 영상 inset 없이, 커다란 모래시계와 연기하는 작은 인물을 한 장의 독립 삽화로 연결. 큰 문구: 멋진 컷신인데 / 왜 넘길까? 넘길까 빨강. 시청자의 선택을 보여주며 컷신 자체가 항상 나쁘다는 뜻은 피한다.',
 'hash':'5b986e470158bfc558e918cb9fcc5b5f8d8301dfc050d6a27618e55ebf66196d'},
'start-with-climax':{
 'episode':'D28','introKo':'왜 어떤 게임은 사정을 다 몰라도 시작부터 빠져들게 할까요? DOOM(2016)의 첫 전투, 슈퍼 마리오 갤럭시 2의 조작과 위협, 역전재판의 첫 재판으로 도입부의 설계를 살펴봅니다.\n\n사건이 일어난 순서와 플레이어에게 알려주는 순서를 구분하고, 첫 행동·첫 위협·첫 판단으로 게임의 재미를 먼저 경험하게 하는 방법을 설명합니다.',
 'introEn':'Why can a game hook us before we know its whole story? The opening battle of DOOM (2016), the actions and threat in Super Mario Galaxy 2, and the first trial in Ace Attorney show different ways to design an opening.\n\nWe separate the order of events from the order of information and explore how a first action, first threat and first decision can let players experience the appeal of a game early.',
 'alternatives':['왜 어떤 게임은 시작하자마자 빠져들게 될까? | 게임 도입부 설계','게임 시작부터 설명만 하면 생기는 일','첫 행동으로 재미를 보여주는 게임 도입부'],
 'reason':'도입부의 작은 절정과 조작·위협·판단이라는 세 실제 사례를 포괄하며, 설명을 전부 없애자는 과장 없이 본문의 약속을 전달한다.',
 'tags':['게임디자인','게임도입부','튜토리얼','DOOM','슈퍼 마리오 갤럭시2','역전재판','Game Design','Game Opening','얌얌코딩'],
 'chapterEn':['An opening can have a climax','Experience the promise before the explanation','Event order and information order','Give control early','From a small action to a major threat','Background after curiosity','Participation in a quiet opening','Bring the opening’s high point forward','A first trial that shows the game'],
 'credits':['DOOM (2016) © id Software / Bethesda Softworks. Gameplay: NavJack27 — 01 The Begining - DOOM (2016) NO COMMENTARY PLAY-THRU: https://www.youtube.com/watch?v=ku4W7k4IzKk — CC BY; excerpted and annotated.','Super Mario Galaxy 2 © Nintendo. Gameplay: LongplayArchive: https://www.youtube.com/watch?v=OWl-ikWpNMU — excerpted and annotated.','Phoenix Wright: Ace Attorney Trilogy © CAPCOM CO., LTD. Official game footage: Capcom USA — Announce Trailer: https://www.youtube.com/watch?v=PnYpTj_aUoA — short educational excerpts and retained evidence-menu stills with annotations.'],
 'thumbnail':'게임 입구에서 긴 설명 두루마리를 들고 기다리는 작은 인물과, 이미 문을 통과해 모험에 뛰어든 얌얌 고양이를 하나의 장면으로 대비. 고양이의 첫 행동이 작은 불꽃·보상으로 바로 이어진다. 큰 문구: 설명보다 먼저 / 재미를 줘! 재미를 빨강. 실제게임 스크린이나 UI inset 없이 독립 삽화.',
 'hash':'7f29dae60cb1df0643dc3b87d52a7066fec6783aa1ecc7a057b7ab82dd09abc5'},
'respect-player-time':{
 'episode':'D30','introKo':'긴 플레이 시간은 구매 전에는 부담이 되지만, 재미를 느낀 뒤에는 즐거운 기록이 되기도 합니다. 언패킹, 스매시브라더스 얼티밋, 파워워시 시뮬레이터를 통해 플레이어가 시간을 쓰기로 결정하는 이유를 살펴봅니다.\n\n제목의 300시간은 특정 게임의 클리어 시간이 아닌 설명용 가정입니다. 기회비용과 시작 문턱을 짚고, 직접 조작하는 40초를 유지하면서 불필요한 대기를 줄이는 예시로 플레이어의 시간을 존중하는 설계를 설명합니다.',
 'introEn':'A long playtime can feel like a burden before purchase and a happy record after the fun begins. Unpacking, Super Smash Bros. Ultimate and PowerWash Simulator illustrate why players choose to spend their time.\n\nThe 300 hours in the title is an illustrative assumption, not a completion-time claim about any featured game. We discuss opportunity cost, barriers to starting, and a worked example that preserves 40 seconds of meaningful interaction while reducing unnecessary waiting.',
 'alternatives':['300시간짜리 게임, 왜 시작하기도 부담스러울까?','오래 즐긴 게임과 오래 해야 하는 게임의 차이','플레이 시간을 늘리기 전에 생각해야 할 것'],
 'reason':'300시간이 설명용 가정임을 도입과 설명란에서 명확히 하고, 구매 전 부담과 재미 뒤에 쌓인 결과라는 핵심 대비를 유지한다.',
 'tags':['게임디자인','플레이타임','기회비용','언패킹','스매시브라더스 얼티밋','파워워시 시뮬레이터','Game Design','Player Time','얌얌코딩'],
 'chapterEn':['Time before the fun','The commitment before starting','Long playtime as a result','Playtime is a cost','Free time still has alternatives','The barrier to starting','Offer an action worth doing','Measure meaningful interaction','Responsibility for the player’s time'],
 'credits':['Unpacking early work-in-progress footage (2019) — Witch Beam: https://www.youtube.com/watch?v=SSZTPO8eYss — excerpted and annotated; early promotional audio omitted.','Super Smash Bros. Ultimate gameplay — LongplayArchive / Spazbo4: https://www.youtube.com/watch?v=663UvTXbzbM — transformed educational excerpts.','PowerWash Simulator gameplay — LongplayArchive / SpectreBull: https://www.youtube.com/watch?v=jvlT0Q55_ss — transformed educational excerpts.','Unpacking official game information: https://www.unpackinggame.com/','PowerWash Simulator developer FAQ: https://steamcommunity.com/app/1290000/discussions/0/4353365966426924959/'],
 'thumbnail':'얌얌 고양이가 거대한 300시간 모래시계 앞에서 컨트롤러를 들고 잠시 망설인다. 반대쪽 작은 시계 옆에는 즐겁게 한 번 더 플레이하는 같은 고양이 표정의 변화를 표현. 한눈에 시간의 부담이 읽히는 독립 삽화. 큰 문구: 300시간? / 시작이 부담이다 300시간과 부담 빨강. 실제 게임의 공식 플레이시간처럼 포장하지 않는다.',
 'hash':'b5c4396ea2d210d5f3d6706a6126a0e008979f2702284e760396108a81af2c34'}
}

defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
footerKo=(ROOT/defaults['description']['channelDefaultSnapshot']).read_text('utf-8-sig').split('📚 수업 노트')[0].strip()
coaching=defaults['coaching']['url']
footerEn=f'''🎮 Build games with real programming skills.

YamYamCoding is a Korean game-programming channel covering DirectX, Unity, Unreal Engine and computer graphics.

━━━━━━━━━━━━━━━━━━
🚀 Premium 1:1 programming coaching
Learn to design and implement real projects with guided feedback.
DirectX11 / DirectX12 · Unity / Unreal Engine · Computer Graphics & PBR · Shaders / Rendering · Game engines
{coaching}

💬 YamYamCoding community
Discord: https://discord.gg/wZuqe7fqkR
YouTube channel membership: {defaults['membershipUrl']}
━━━━━━━━━━━━━━━━━━'''
assetProducts={}
for a in read(ROOT/'production/batches/design-25-30-unity-v2-20261028/asset-provenance.json')['assets']:
    assetProducts[a['productId']]=a
def stamp(seconds):
    seconds=int(seconds)
    return f'{seconds//60:02}:{seconds%60:02}'

for slug in SLUGS:
    p=ROOT/'projects'/slug;dest=p/'production/upload-20261029';dest.mkdir(parents=True,exist_ok=True)
    d=DATA[slug];m=read(p/'project.json');review=read(p/'production/unity-visual-v2/review-status.json')
    edit=read(p/'production/batch-v1/edit-plan.json')
    assert m['revision']=='unity-visual-v2' and review['fourOutputsVerified']
    planPath=p/('planning/batch-v1-plan.json' if slug in SLUGS[1:3] else 'planning/production-plan.json')
    sourcePlan=read(planPath)
    visualPath=p/('production/unity-visual-v2/plan.json' if slug in SLUGS[1:3] else 'production/unity-visual-v2/visual-plan.json')
    visual=read(visualPath)
    assets=visual.get('assetRecords') or [a for c in visual['cuts'] for a in c['assetRecords']]
    products=sorted(set(a['productId'] for a in assets if 'productId' in a))
    verified=[]
    for suffix,path in m['localFinalReview']['files'].items():
        f=ROOT/path;h=sha(f)
        assert h==m['localFinalReview']['sha256'][suffix]
        verified.append({'suffix':suffix,'path':rel(f),'absolutePath':str(f),'sha256':h,'bytes':f.stat().st_size})
    movie=next(x for x in verified if x['suffix']=='captioned.mp4')
    assert movie['sha256']==d['hash']==review['captionedSha256']
    chapters=[]
    for i,c in enumerate(edit['scenes']):
        seconds=0 if i==0 else c['startFrame']/60
        chapters.append({'sceneId':c['id'],'sourceFrame':0 if i==0 else c['startFrame'],'seconds':seconds,'timestamp':stamp(seconds),'ko':c['title'],'en':d['chapterEn'][i]})
    # Do not add a sub-10s chapter for the final member page. Whole-second stamps floor the exact measured scene entry.
    assert all(int(b['seconds'])-int(a['seconds'])>=10 for a,b in zip(chapters,chapters[1:]))
    credits=d['credits'][:]
    if any('CC BY' in c or 'Creative Commons' in c for c in credits):credits.append('Creative Commons Attribution license: https://creativecommons.org/licenses/by/4.0/')
    credits.append('Research reference — Masahiro Sakurai on Creating Games: '+sourcePlan['reference']['url']+' (research only; its video and audio are not included).')
    credits.append('Music: Nimbus — Eveningland (YouTube Audio Library): https://www.youtube.com/watch?v=ZOc84gXN-lg')
    names={'007':'Kitchen / Restaurant Megapack','011':'Cartoon City Massive Pack — Characters','032':'Cute Dungeon Megapack','076':'Free Blaster Pack — Mini Edition'}
    for product in products:
        a=assetProducts[product]
        credits.append(f"3D assets — RG Poly, {names.get(product,product)} ({a['license']}): {a['url']}")
    credits.append('Production: Unity https://unity.com/ ; FFmpeg https://ffmpeg.org/ ; ElevenLabs (creator’s own voice) https://elevenlabs.io/')
    creditsText='\n'.join(credits)
    descriptions={}
    for lang,footer in [('ko',footerKo),('en',footerEn)]:
        body=d['introKo' if lang=='ko' else 'introEn']
        chapterText=('챕터' if lang=='ko' else 'Chapters')+'\n'+'\n'.join(c['timestamp']+' '+c[lang] for c in chapters)
        hashtags='#게임디자인 #게임개발 #얌얌코딩' if lang=='ko' else '#GameDesign #GameDevelopment #YamYamCoding'
        heading='출처·자료 및 제작 도구' if lang=='ko' else 'Sources, assets and production tools'
        descriptions[lang]='\n\n'.join([body,chapterText,hashtags,footer,heading+'\n'+creditsText])+'\n'
        assert len(descriptions[lang])<=5000
        assert descriptions[lang].rstrip().endswith(credits[-1])
        (dest/f'description.{lang}.txt').write_text(descriptions[lang],encoding='utf-8')
        (dest/f'title.{lang}.txt').write_text(m['titles'][lang]+'\n',encoding='utf-8')
    (dest/'pinned-comment.ko.txt').write_text('영상에서 가장 공감한 설계나 떠오른 게임을 댓글로 알려주세요.\n\n프로그래밍 과외 안내\n'+coaching+'\n',encoding='utf-8')
    thumbnail={
        'status':'missing-needs-new-illustration','generateNow':False,
        'outputPath':rel(p/'publishing/upload-20261029/thumbnail.png'),'referenceImages':[
            'shared/assets/branding/yamyamcoding-cats-original.png',
            'projects/deconstruct-analyze-rebuild/publishing/thumbnail-v2.png',
            'projects/counting-animation-frames/publishing/thumbnail-v3.png'],
        'style':'16:9; white background; thin yellow top strip; exact 얌얌코딩 brand; large black/red Korean; natural black/orange/white cat; no video/PPT inset, screenshot, copied runtime badge or separate logo sticker.',
        'concept':d['thumbnail'],'requiredReview':'Actual Korean spelling, mascot form, 16:9 and 375px readability; verify selected file really saved in Studio.',
        'recommendedRoute':'Use imagegen with the three verified local references, generate one original illustration per approved video; validate actual output and upload-size constraints before selection.'}
    for f in thumbnail['referenceImages']:assert (ROOT/f).exists()
    thumbnailReview=p/'publishing/upload-20261029/thumbnail-review.json'
    if thumbnailReview.exists():
        ready=read(thumbnailReview)
        assert ready['status']=='pass' and sha(ROOT/ready['final']['path'])==ready['final']['sha256']
        thumbnail.update({'status':'ready-local-reviewed-platform-pending','generateNow':False,
            'reviewRecord':rel(thumbnailReview),'path':ready['final']['path'],
            'sha256':ready['final']['sha256'],'dimensions':ready['final']['dimensions'],
            'bytes':ready['final']['bytes'],'copy':ready['exactMainCopy'],
            'promptFile':ready['promptFile'],'provider':ready['provider']})
    write(dest/'thumbnail-brief.json',thumbnail)
    currentRecordFiles=[rel(f) for f in (p/'publishing').glob('*upload*.json')] if (p/'publishing').exists() else []
    package={
        'schemaVersion':1,'slug':slug,'episode':d['episode'],'revision':'unity-visual-v2','preparedAt':datetime.now(timezone.utc).isoformat(),
        'status':'ready-for-parent-studio-check-and-private-upload' if thumbnailReview.exists() else 'metadata-ready-thumbnail-needed-platform-not-touched',
        'authorization':{'privateUploadApprovedByUser':True,'evidence':'Parent relayed latest user selection on2026-10-29: approve D26,D27,D28,D30 latest unity-visual-v2; D25,D29 remain held. Root records exact user message in shared ledger.','approvedMasterSha256':movie['sha256'],'scheduling':False,'publicPublication':False,'deleteExisting':False,'adSelfAssessmentOwner':'user'},
        'video':movie,'fourVerifiedOutputs':verified,'reviewRecord':rel(p/'production/unity-visual-v2/review-status.json'),
        'technical':{'resolution':[1920,1080],'fps':60,'durationSeconds':review['durationSeconds'],'originalAudioAndCaptionsPreserved':True,'proof':review.get('evidence',review.get('directQA'))},
        'metadata':{'title':m['titles']['ko'],'descriptionFile':rel(dest/'description.ko.txt'),'description':descriptions['ko'],'privacyStatus':'private','defaultLanguage':'ko','madeForKids':False,'tags':d['tags'],'category':'retain verified game-design channel default; inspect Studio rather than invent category ID'},
        'englishMetadata':{'title':m['titles']['en'],'descriptionFile':rel(dest/'description.en.txt'),'description':descriptions['en'],'language':'en'},
        'titleReview':{'candidatesKo':d['alternatives'],'selectionReason':d['reason'],'selectedExistingApprovedProjectTitle':True,'performanceGuarantee':False},
        'chapters':{'sourceEditPlan':rel(p/'production/batch-v1/edit-plan.json'),'fps':60,'rounding':'floor exact measured entry to whole seconds; first begins00:00 over unchanged2s branding','rows':chapters},
        'sourceCredits':{'ko':creditsText,'en':creditsText,'position':'absolute-bottom-after-entire-channel-footer','records':[rel(planPath),rel(visualPath),'production/batches/design-25-30-unity-v2-20261028/asset-provenance.json','shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md'],'usedAssetProductIds':products,'includesUnusedFootageCandidates':False},
        'subtitles':[{'language':lang,'method':'manual-file-upload-with-timing','file':next(x for x in verified if x['suffix']==lang+'.srt'),'status':'pending-real-studio-publication'} for lang in ['ko','en']],
        'thumbnail':thumbnail,
        'playlist':{'name':'Planning & Game Design & Tech','historicalId':defaults['endScreen']['knownChannelPlaylists'][0]['id'],'historicalEvidence':'shared/publishing/youtube-defaults.json and projects/one-button-game-design/publishing/youtube-upload.json','actualCurrentStudioVerification':'pending; select observed own-channel playlist by name; never construct an ID'},
        'cards':[{'seconds':0,'kind':'external-link','url':coaching,'title':'프로그래밍 과외','teaser':'프로그래밍 과외','status':'pending-real-ui-or-record-actual-limitation'}],
        'endScreen':{'startSeconds':review['durationSeconds']-10,'endSeconds':review['durationSeconds'],'durationSeconds':10,'elements':['relevant-own-channel-playlist','subscribe-own-channel','programming-coaching-external-link'],'channelId':defaults['channelId'],'coachingUrl':coaching,'preserveMemberNamesAndTitle':True,'timecodeInput':'Inspect actual Studio frame/time unit; do not assume30or60fps input'},
        'pinnedComment':{'file':rel(dest/'pinned-comment.ko.txt'),'status':'prepared-only-pending-video-publication','changePrivacyToComment':False},
        'monetization':{'enableIfAvailable':True,'adSelfAssessment':'user performs; do not submit answers','automaticCopyrightAndAdsChecks':'observe and distinguish from human self-assessment'},
        'dedupe':{'localPriorUploadReceipts':currentRecordFiles,'actualVideoId':None,'actualStudioCheck':'pending-parent','scheduleLedger':'shared/publishing/daily-alternating-schedule.json','localLedgerHasTargetOnlyNoVideoId':True,'plannedTargetDoesNotAuthorizeScheduling':True},
        'remaining':([] if thumbnailReview.exists() else ['Create and inspect new channel illustration thumbnail'])+['Parent checks actual Studio existing/draft uploads before one new upload','Save private and reopen all available settings; manual KO/EN subtitles and localized metadata','Observe HD processing and actual CC-off gameplay/explanation captions','User completes advertising self-assessment'],
        'platformMutationPerformed':False,'gitMutationPerformed':False
    }
    write(dest/'package.json',package)
    print(d['episode'],movie['sha256'],[len(descriptions[x]) for x in ['ko','en']],rel(dest/'package.json'))
