"""Initial package bootstrap only; existing revisions must not be overwritten."""
from pathlib import Path
import datetime, hashlib, json, subprocess

R = Path(__file__).resolve().parents[3]
P = R / 'projects/ai-games-showcase-2026'
L = R / 'production/preflight/ai-games-showcase-2026/local'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

if (P / 'planning/production-plan.json').exists():
    raise SystemExit('Existing plan preserved. Edit its current fields and use production/render-outline.py to refresh the readable script.')

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

research = read(P / 'sources/research.json')
ko = read(P / 'script/narration.ko.json')
en = read(P / 'script/narration.en.json')
assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
assert all(len(a['lines']) == len(b['lines']) for a,b in zip(ko['scenes'],en['scenes']))

pronunciations = {
    'I Just Wanted to Fish': '아이 저스트 원티드 투 피시',
    'Emberfall — Luminati': '엠버폴, 루미나티',
    'Nightshoal': '나이트숄', 'VECTOR: Anti-Gravity Racing': '벡터, 안티 그래비티 레이싱',
    'AUGURY': '오거리', 'Rally Road Rash': '랠리 로드 래시',
    'Claude Opus 5.5': '클로드 오퍼스 오 점 오', 'Opus 5.5': '오퍼스 오 점 오',
    'Codex Astra': '코덱스 아스트라', 'Astra 6': '아스트라 식스',
    'Blender MCP': '블렌더 엠씨피', 'Unity 6': '유니티 식스',
    'Three.js': '쓰리 제이에스', 'WebGPU': '웹 지피유', 'WebGL 2': '웹 지엘 투',
    'Godot': '고도', 'Tripo AI': '트리포 에이아이', 'ElevenLabs': '일레븐랩스',
    'Stable Audio': '스테이블 오디오', 'Phaser': '페이저', 'TypeScript': '타입스크립트',
    'DreamLayer': '드림레이어', 'Sandscape': '샌드스케이프', 'Meshy': '메쉬'
}
save(P/'script/pronunciation.json', {
    'aliases': pronunciations,
    'policy': 'Speech aliases only. Display canonical game/model/tool spellings in cards and captions. Verify actual generated pronunciation before delivery.',
    'scriptState': 'Korean draft currently contains speech-friendly names; canonical caption replacement is required in caption generation.'
})

clip_specs = [
    ('fish','fish-creator-demo.mp4','https://x.com/ForkedPush/status/2106313584829431901','ForkedPush',[[6,92],[100,118]],'1440p HTTP format http-10368'),
    ('nightshoal','nightshoal-trailer.mp4','https://www.youtube.com/watch?v=b7M4JUFSzTg','Nightshoal / ProFactor',[[0,25]],'YouTube399+251; creator environment trailer, not footage of fishing UI'),
    ('vector','vector-creator-demo.mp4','https://www.reddit.com/r/threejs/comments/1wwigsb/vector_antigravity_racing/','W2DGAMES',[[10,32],[38,62],[97,110]],'Observed Reddit1080p video at https://v.redd.it/atdsr716v7th1/CMAF_1080.mp4; no audio'),
    ('rally','rally-creator-demo.mp4','https://www.reddit.com/r/aigamedev/comments/1x1lkiu/made_a_road_rash_x_dirt_mashup_in_about_3_days/','titkun',[[0,32]],'Reddit player selected1080p; downloaded through visible video control')
]
media=[]
for game,filename,url,credit,ranges,format_evidence in clip_specs:
    file=L/filename
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)],text=True))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert video['width']>=1920 and video['height']>=1080
    media.append(dict(game=game,path=file.relative_to(R).as_posix(),sha256=sha(file),sourceUrl=url,credit=credit,
        role='independent-creator-gameplay',width=video['width'],height=video['height'],fps=video['r_frame_rate'],
        durationSeconds=float(probe['format']['duration']),formatEvidence=format_evidence,
        candidateSourceRangesSeconds=ranges,exactEditTimingLocked=False,
        review={'contactSheet':'viewed','movingSelectedRanges':'pending','wholeOutput':'not-created'},
        audioUse='mute-source-music; original mixed music rights not established',
        rights={'basis':'Limited attributed excerpts for original game-specific commentary; not a reusable asset license',
                'permissionGranted':False,'publicReuseReview':'pending exact excerpt selection',
                'restrictions':['No standalone redistribution','No reviewer narration','Keep game and creator credit','No false attribution to Tripo or our own production']},
        crop='Preserve original frame/aspect ratio and letterbox; do not stretch or invent frames. 30fps sources use frame repetition in60fps master, no optical-flow claims.'))
from PIL import Image
for game,files in [('emberfall',['emberfall-title-1080.png','emberfall-village-1080.png','emberfall-rotated-1080.png']),('augury',['augury-title-1080.png','augury-before-1080.png','augury-preview-1080.png','augury-after-1080.png'])]:
    for filename in files:
        f=L/filename
        assert f.exists(),f
        dimensions=Image.open(f).size
        assert dimensions==(1920,1080),dimensions
        media.append(dict(game=game,path=f.relative_to(R).as_posix(),sha256=sha(f),width=1920,height=1080,
            role='direct-browser-screenshot',sourceUrl=next(g for g in research['games'] if g['id']==game).get('playUrl',next(g for g in research['games'] if g['id']==game)['url']),
            classification='explanation-still-analysis',notContinuousGameplayRecording=True,
            review={'actualInteractionObserved':True,'captionLayout':'pending'},
            rights={'basis':'Own screenshot of public playable build for limited attributed commentary; no claim to game asset ownership','publicReuseReview':'pending final composition'}))
save(P/'sources/media.json',{'checkedAt':now,'assets':media,'referenceVideoExcluded':True,'rawMediaInGit':False})

scene_details = [
    ('01',None,'Fish opening then brief VECTOR/Rally glimpses; game titles persist through source changes.','Six games; game first, then creator-reported milestone and tools.','Island from overview becomes Fish opening.','No six-card collage; one game at a time.'),
    ('02','fish','Beach fishing and crab from creator footage, followed by a compact Blender MCP → Unity6 flow beside a relevant frame.','Visible character, water and crab; connect modeling/animation to the actual shown subject.','3D asset pipeline → browser miniature world.','Mark crab only during crab sentence; source motion reviewed before anchor lock.'),
    ('03','emberfall','Village and rotated-camera screenshots; two-state comparison labelled actual captured views. Editor controls named only when their screen is shown.','Same village from two camera angles; yellow house contour and numbered view labels.','Small world → ongoing story and systems in Nightshoal.','Static captures remain still analysis; do not fake continuous game movement.'),
    ('04','nightshoal','25s environment trailer plus authored task/tool map beside one selected environment frame and creator update excerpt.','Forest, cliff, water and boat visible; quests/inventory are creator-reported development, not demonstrated by aerial trailer.','World building → responsive racing.','Do not say trailer demonstrates fishing or inventory. Need additional action footage if that wording changes.'),
    ('05','vector','Creator racing segments showing corners and boost path. Compact Three.js/WebGPU label after game introduction.','Follow visible craft; briefly mark boost pad then clear; no invented telemetry.','Fast input → paused tactical decisions.','Preserve speed/UI; any numbers are native game UI, not independent measurements.'),
    ('06','augury','Actual1920×1080 before/preview/result tutorial screenshots, then minimal illustration of picture → prepared sprite → animation.','Yellow current character; green predicted silhouette; label CHOOSE / PREVIEW / COMMIT in Korean, avoid game tutorial text.','Preparation and refinement → short initial Rally milestone.','State sequence uses real screenshots and explicit step labels; no interpolated fake gameplay.'),
    ('07','rally','Creator trailer action excerpts: dirt track, jump and vehicles. Keep creator title shot out of repeated closing.','Jump/vehicle silhouette only when narrated; brief period label 約3days INITIAL VERSION.','Initial milestone → cross-game conclusion.','Show about3days, creator report, still refining. Preserve widescreen source aspect.'),
    ('08',None,'Three concise contrasts over relevant retained game frames: code / assets / human selection; final single question, then original10s member outro.','Creation tasks and disclosed uncertainty, not model ranking.','Carry music into original membership outro.','No fabricated total cost or productivity ranking.')
]
scenes=[]
for id,game,visual,focus,transition,limitation in scene_details:
    lines=next(s['lines'] for s in ko['scenes'] if s['id']==id)
    scenes.append(dict(id=id,game=game,narration=f'script/narration.ko.json#{id}',renderer='FFmpeg/ASS compositing + acquired media; existing Motion Canvas branding' ,
        rendererReason='This selected showcase needs clean source footage, short labels and still-state comparison. Reuse the actual ASS layout sample and existing branding instead of recreating games or duplicating a scene in an engine.',
        implementationKind='editorial-analysis-of-actual-game',visualEvidence=visual,focus=focus,
        sourceAssets=[a['path'] for a in media if a['game']==game] if game else [],
        transitionToNext={'narrative':transition,'lastLine':lines[-1],'visual':'Carry the relevant game frame or label into the following opening; no chapter-black reset','audio':'Continuous approved music under speech; no artificial scene pause'},
        annotations={'policy':'footage-focus-annotations-v1','cue':focus,'keyframes':'pending final clip selection and speech timing','clearance':'Keep fixed caption zone960,970/max2lines; source credit above caption zone, clear at source cut'},
        limitation=limitation,timingStatus='pending measured TTS; no fixed total runtime'))
plan=dict(schemaVersion=1,slug='ai-games-showcase-2026',updatedAt=now,status='research-and-script-draft-ready',
    userScope='Six specified AI-assisted games; showcase format exception, no forced standard lesson construction',
    primaryResearch='sources/research.json',media='sources/media.json',narrationKo='script/narration.ko.json',narrationEn='script/narration.en.json',
    formatException={'id':'user-selected-ai-game-showcase-v1','userEvidence':'해당게임들을 ai 로만든걸 소개하는 영상이니까 우리 방식처럼 만들필요난 없어','ratioTarget':None,'scope':'This episode only','kept':['1080p-minimum sources','1920x1080/60fps master','original branding2s','original membership10s','fixed captions','source credit','natural speech and final QA','Drive review before YouTube']},
    titleCandidates=[{'title':'이 낚시 게임도 AI로 만들었다고?','support':'02 fishing game, then six distinct projects','thumbnailIdea':'Fishing character and rod as one clear illustration; yellow header, white background, original cat brand; no PPT inset'}, {'title':'AI로 만든 게임, 지금은 어디까지 왔을까?','support':'All six observed games and creator-disclosed workflows'}, {'title':'3일짜리 레이싱부터 11주째 낚시 게임까지, AI 게임 제작 근황','support':'07 initial3day Rally /04 ongoing week11 Nightshoal; preserve stage qualification'}],
    terminology=[{'canonical':key,'speechAlias':value,'display':'canonical name','source':'sources/research.json','checked':'creator/game primary sources; unknown exact versions remain unknown'} for key,value in pronunciations.items()],
    stages={'duplicateReview':'passed','research':'completed-with-explicit-unknowns','script':'paired-draft','allSceneDesign':'drafted','footageMotionReview':'pending-selected-ranges','visualSample':'pending','tts':'waiting-user-GPU-availability','edit':'not-started','finalQa':'not-started','drive':'not-created','youtube':'not-authorized'},
    audio={'model':'Qwen3-TTS1.7B approved reference','reference':'shared/voice-reference/reference-15-35s.wav','gpu':'Do not start before user confirms game/Unity use ended; prior wait instruction persists. No CPU fallback without change of preference.', 'narrationTargetLufs':-16,'bgmTargetLufs':-31,'music':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3','musicLicense':'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md','musicHash':sha(R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'),'musicHashMatchesExistingRecord':sha(R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3').upper()=='06DDB8D0F2AA82E499AB2CB398B8A241C626D9D3DA82BBAF274D1178435F8C08','sourceMusic':'excluded unless separately cleared','joins':'Continuous greeting in same take; preserve sentence endings and speech-active gain. One whole PCM ASR and one final mix ASR, local loudness and contextual listening required.'},
    scenes=scenes)
save(P/'planning/production-plan.json',plan)
project=dict(schemaVersion=2,slug='ai-games-showcase-2026',status='preproduction',titles={'ko':ko['title'],'en':en['title']},video={'width':1920,'height':1080,'fps':60,'durationSeconds':None},
    editing={'ratioPolicyVersion':'user-selected-ai-game-showcase-v1','targetGameplayShare':None,'targetExplanationShare':None,'fixedDurationSeconds':None},
    paths={'script':'projects/ai-games-showcase-2026/script/narration.ko.json','scriptEn':'projects/ai-games-showcase-2026/script/narration.en.json','sources':'projects/ai-games-showcase-2026/sources/research.json','sceneProductionPlan':'projects/ai-games-showcase-2026/planning/production-plan.json'},
    engines=['motion-canvas'],visualStyle='yamyam-video-ui-v1 / research-black-v1 for explanation',
    tts={'engine':'qwen3-tts','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','status':'waiting-user-GPU-availability'},
    membershipOutro={'enabled':True,'durationSeconds':10,'rosterPath':'motion-canvas/src/shared/membership/members.json','scenePath':'motion-canvas/src/shared/membership/membership-outro.tsx','appliedToFinal':False},
    delivery={'directory':'output/ai-games-showcase-2026','collector':'node scripts/collect-video-output.cjs ai-games-showcase-2026','required':['captioned.mp4','clean.mp4','ko.srt','en.srt'],'complete':False},
    publishing={'driveFinalReviewRequired':True,'driveId':None,'userReviewedVersion':None,'youtubeUploadAuthorized':False,'videoId':None},
    preflight={'duplicateReview':'production/preflight/ai-games-showcase-2026.json'},publishReady=False)
save(P/'project.json',project)
ledger=dict(schemaVersion=1,slug=project['slug'],updatedAt=now,checks=[
    {'name':'duplicate content and live Studio','status':'pass','evidence':'production/preflight/ai-games-showcase-2026.json'},
    {'name':'six game source research','status':'pass-with-disclosed-unknowns','evidence':'sources/research.json','sha256':sha(P/'sources/research.json')},
    {'name':'four downloaded video dimensions','status':'pass','evidence':'sources/media.json','note':'1440p59.94 /1080p60 /1080p30 /1080p30. Final60fps must not be described as all native60fps footage.'},
    {'name':'browser interaction evidence','status':'pass-with-scope','scope':'Emberfall movement/camera; AUGURY choice,preview,commit','evidence':'sources/media.json','notVerified':'ContinuousFHD gameplay recording'},
    {'name':'KO EN scene and paragraph correspondence','status':'pass','koSha256':sha(P/'script/narration.ko.json'),'enSha256':sha(P/'script/narration.en.json')},
    {'name':'source moving cuts and caption sample','status':'pending'},
    {'name':'speech generation and listening','status':'pending','reason':'User previously requested GPU after game/Unity use. Availability question pending.'},
    {'name':'current output full audiovisual QA','status':'pending','reason':'No final output exists'},
    {'name':'Google Drive user final review','status':'pending'},
    {'name':'YouTube upload','status':'not-authorized'}])
save(P/'production/review-ledger.json',ledger)
save(P/'production/checkpoint.json',dict(updatedAt=now,stage='research-script-and-scene-design',selectedVideo=project['slug'],runningJob=None,
    completed=['Primary research for six games with unknowns recorded','IndependentFHD-or-higher creator movies for four games','FHD screenshots of two browser games','PairedKOEN narration draft','Eight-scene design and transitions','Duplicate content/Studio review'],
    blockers=[{'stage':'TTS','reason':'Waiting for confirmation that game/Unity GPU use has ended; no CPU generation authorized'}],
    nextAction='Finish selected source motion and visual sample review; then generate one approved-voice TTS batch when GPU handoff is confirmed.',
    delivery={'finalVideoExists':False,'driveUploaded':False,'youtubeUploaded':False},otherProjects='D19 remains awaiting human Drive review; do not resume or upload other projects'))

outline=['# AI 게임 제작 근황 — 여섯 게임 소개','','2026-10-18 공개 자료 확인 기준. 현재는 **자료 조사·대본 초안·씬 설계** 단계이며 완성 영상은 아직 없다. 이번 편은 사용자가 선택한 게임 소개 형식으로 제작한다. 정해진60:40 비율이나 Unity 재현 씬을 강제하지 않는다. 최종 마스터는1080p60이며 완성본은Drive에서 먼저 검수한다.','','## 조사 결과','','| 게임 | 제작 기간의 의미 | 모델 | 제작 도구 |','|---|---|---|---|']
for g in research['games']:
    period=g['development']['value'] or '전체 기간 미공개/미확인'
    models=' / '.join((m['name'] or '정확한 모델 미공개')+(' (소개자 언급만 확인)' if m['confidence']=='reviewer-reported-only' else '') for m in g['models'])
    outline.append(f"| [{g['name']}]({g['url']}) | {period} · {g['development']['stage']} | {models} | {', '.join(g['tools'])} |")
outline+=['','기간은 완료까지 걸린 동일한 척도가 아니다. 첫 버전의3일, 진행 중인11주 차, 약3주 작업을 구분한다. 출처별 주장과 반례는 [연구 기록](../sources/research.json), 확보 파일·해상도·권리는 [자료 목록](../sources/media.json)에 연결했다.','','## 전체 대본과 화면 구성','']
for n,s in zip(ko['scenes'],scenes):
    outline += [f"### {n['id']}. {n['title']}",'',*sum(([line,''] for line in n['lines']),[]),f"화면: {s['visualEvidence']}",'',f"다음 연결: {s['transitionToNext']['narrative']}",'']
outline+=['## 제작 상태','','- 완료: 제작자 자료 조사, 미확인 정보 분리, 네 작품1080p이상 영상 확보, 두 브라우저 게임 실제 조작·1080p 캡처, 한영 대본 초안과8개씬 구성.','- 진행: 사용할 움직이는 구간의 세부 검수와 자막을 포함한 화면 샘플.','- 대기: 사용자의 이전 지시에 따른 게임·Unity 사용 종료/GPU 인계 확인 후Qwen3 음성 생성.','- 미완료: 음성·전체 편집·최종QA·4파일·Drive 검수본.','- 별도 승인 경계: 이 버전의Drive 사용자 검수 후YouTube 업로드. 자동 다음 편 없음.','']
(P/'planning/outline.md').write_text('\n'.join(outline),encoding='utf8')
print(json.dumps({'slug':project['slug'],'scenes':len(scenes),'assets':len(media),'stage':project['status'],'gpuJobStarted':False}))
