"""Create the two owned source/script plans from inspected actual inputs only."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parents[4]
NOW = datetime.now(timezone.utc).isoformat()
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
def artifact(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': h.hexdigest(), 'bytes': path.stat().st_size}
def video(path):
    x = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height,r_frame_rate,duration','-of','json',str(path)], text=True))['streams'][0]
    assert x['width'] >= 1920 and x['height'] >= 1080, str(path)
    return x

specs = {
 'limited-color-world': {
  'episode':'D25','referenceId':'obnjR8KJ9nk','referenceSeconds':174,
  'thesis':'Essential information must survive differences in color perception; check lightness and additional cues, then use grayscale to inspect foreground/background visual hierarchy.',
  'sections':[
   ('R01',4,33,'Color-dependent puzzle information can become inaccessible; omit creator biography while preserving the design problem.'),
   ('R02',33,43,'Art/theme changes alter the combinations that must remain distinguishable.'),
   ('R03',43,71,'Use color-vision simulations, including Protanopia-type and Deuteranopia-type views.'),
   ('R04',71,107,'Increase useful lightness differences without merging objects into the background; reinforce with distinct patterns.'),
   ('R05',107,123,'Apply the same consideration to power-ups and interactive stage objects.'),
   ('R06',132,157,'Grayscale reveals the hierarchy of light/dark: a distant background must not overpower the relevant foreground.'),
   ('R07',157,166,'Like horizontally flipping artwork, removing color can reveal problems hidden by familiarity.')],
  'games':[
   {'id':'puyo2','title':'Puyo Puyo Tetris 2','genre':'falling-block action puzzle','nintendo':False,
    'publisher':'SEGA','official':'https://www.sega.jp/game/detail/puyopuyotetris2/',
    'role':'Color-dependent matching rule; inspect varied backgrounds and reinforce color with another clue.',
    'equivalence':'Replaces Meteos in the same teaching role: the player must distinguish matching types while puzzle objects and backgrounds coexist. Puyo uses four connected Puyos, not Meteos launches.',
    'beginnerRules':'Concentrate on the left Puyo field; move/rotate a falling pair and connect at least four of one color. Exclude dialogue and use pure Puyo rounds where possible.',
    'versionReason':'2020 game with verified2021 color-adjustment update. New2S edition does not change the selected four-connect teaching role; retain the independently inspectable FHD recording.',
    'rights':{'publisherPolicy':'https://puyo.sega.jp/puyopuyotetris2/agreement.html','generalPolicy':'https://www.sega.co.jp/en/streaming_guideline/',
      'recorderPermission':'Both GATA TV sources explicitly carry Creative Commons Attribution license (reuse allowed) in their current YouTube metadata.',
      'requiredDescriptionCredit':'©SEGA Tetris ® ＆ © 1985～2020 Tetris Holding. Recording: GATA TV, original URLs, Creative Commons Attribution (reuse allowed).',
      'conditions':'Own educational commentary, fair portrayal, source attribution; no story/dialogue excerpts and no standalone music release.',
      'sourceAudio':'Preserve synchronized game audio for selected gameplay; do not select story/dialogue or external commentary. No external narrator in the recorder-described SANS COMMENTAIRE captures.'}},
   {'id':'wonder','title':'Super Mario Bros. Wonder','genre':'2D platform action','nintendo':True,
    'publisher':'Nintendo','official':'https://www.nintendo.com/jp/switch/aqmxa/index.html',
    'role':'Flower versus question-mark block recognition, visible interaction/result and foreground/background hierarchy.',
    'equivalence':'Concrete interactive objects replace generic power-up/stage-mechanism examples; ordinary and Wonder states make the background hierarchy observable without a reference-lesson clip.',
    'beginnerRules':'Mario runs/jumps on solid foreground paths, hits blocks and touches flowers. A Wonder Flower visibly changes the scene.',
    'versionReason':'Original2023 product-page captures demonstrate the same object/visual hierarchy mechanics; Switch2 additions are not claimed.',
    'rights':{'publisherPolicy':'https://www.nintendo.co.jp/networkservice_guideline/en/index.html',
      'recordingProvenance':'Direct non-narrated1920x1080 MP4s linked by the official product page, not a Nintendo Direct or stage demo.',
      'sourceAudio':'Keep actual synchronized game mix under narration; content remains original educational commentary, not a standalone music/video reupload.'}}],
  'files':[
   ('puyo-intro','puyo2','puyo-intro-ot4gqysX29c.mp4','https://www.youtube.com/watch?v=ot4gqysX29c','Creative Commons Attribution license (reuse allowed)'),
   ('puyo-late','puyo2','puyo-qMkZArWp4wA.mp4','https://www.youtube.com/watch?v=qMkZArWp4wA','Creative Commons Attribution license (reuse allowed)'),
   ('wonder-before','wonder','wonder-before.mp4','https://www.nintendo.com/jp/switch/aqmxa/assets/img/top/before_movie.mp4','Nintendo official promotional gameplay'),
   ('wonder-after','wonder','wonder-after.mp4','https://www.nintendo.com/jp/switch/aqmxa/assets/img/top/after_movie.mp4','Nintendo official promotional gameplay')],
  'addedExplanation':['Four-connected-Puyo prerequisite beside the opening actual game example.','One-variable color-loss illustration, then contrast against background and redundant shape/pattern cues.','Actual2021 PPT2 color-adjustment options, verified against SEGA product update.','Different purposes of CVD simulation and grayscale; complement simulated views with diverse player experience.'],
  'primaryEvidence':[
   'https://puyo.sega.jp/puyopuyotetris2/information.html',
   'https://helpx.adobe.com/photoshop/desktop/print/soft-proof-for-color-blindness.html',
   'https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/'],
  'corrections':[
   {'issue':'Automatic captions misrecognize the final background example as circle/gold.','resolution':'Viewed the actual English burned captions and images: distant background should not be more prominent than foreground.','sourceTime':[150,157]},
   {'issue':'Automatic Japanese/translated captions misrecognize Protanopia-type.','resolution':'Actual source screen shows Color Blindness–Protanopia-type and Deuteranopia-type; verified official Adobe names.'}],
  'rejected':['Lumines short promotional shots are insufficient for a full continuous before/action/result bank.','Lumines CC candidates720p and1072p fail the genuine1080p source rule.','Enhance anniversary stream sample1200–1440 contains hosts and unreleased Lumines Arise footage; not adopted as Remastered or independent gameplay.','Small Mario power-up inline MP4s340–480px are not adopted as actual footage.']},
 'computer-controlled-players': {
  'episode':'D26','referenceId':'uleauI0IwZM','referenceSeconds':305,
  'thesis':'A CPU opponent needs coherent situation-based decisions, humanly readable response timing and exploitable openings; maximizing victory is not the purpose of opponent design.',
  'sections':[
   ('R01',5,36,'Old attract-mode movement can look unlike intentional human play.'),
   ('R02',36,85,'Define CP/CPU, increasing freedom increases design difficulty, impossible reaction speed feels unfair.'),
   ('R03',85,106,'Dice/card/board outcomes can be distrusted because the same computer controls both randomness and the opponent; perception alone is not evidence of rigging.'),
   ('R04',106,134,'Complex free-action games require difficult CPU design to support solo play; creator-specific delegation/biography is omitted.'),
   ('R05',134,173,'Use position/state and both characters\u2019 attack/movement ranges and timings as decision inputs.'),
   ('R06',173,195,'Behavior tendencies can depend on health, spacing, speed/jump and match situation; the handicap example remains a general possibility.'),
   ('R07',195,212,'Conflicting decision conditions can stall behavior; explain priority/switching beside this point.'),
   ('R08',212,236,'Ultimate uses reaction delay and brief confusion under reversed controls without leaving CPUs permanently helpless.'),
   ('R09',236,274,'More aggressive CPUs leave defensive/exploitation openings so players can read and counter their actions.'),
   ('R10',280,297,'Perfect defensive execution may create an uninteresting opponent; the purpose remains player enjoyment.')],
  'games':[
   {'id':'smash','title':'Super Smash Bros. Ultimate','genre':'platform fighting','nintendo':True,
    'publisher':'Nintendo','official':'https://www.nintendo.com/kr/products/switch/smashbros/',
    'role':'Free-action CPU movement/attack/response and the specific design facts about reaction delay, control reversal and aggression.',
    'equivalence':'Retain this reference game because those design choices are game-specific. Its independent CPU recorder and official individual move recordings replace all finished-lesson clips.',
    'beginnerRules':'Deal accumulated damage and launch opponents out of the stage. Percentages are damage, not remaining HP. The recorder identifies Player2 as the human; the opposing default-name fighter is the CPU.',
    'versionReason':'Ultimate is the same documented title; no patch-specific reaction-delay number or measured hidden CPU data is asserted.',
    'rights':{'publisherPolicy':'https://www.nintendo.co.jp/networkservice_guideline/en/index.html',
      'recorderPermission':'I3LV8o_xhR8 has explicit Creative Commons Attribution license (reuse allowed), No Commentary/Free to Use title and Player2 description.',
      'officialMoveProvenance':'Per-fighter YouTube IDs are linked by smashbros.com/assets_v2/data/fighter_movie_en.json; not a Direct or stage demo.',
      'sourceAudio':'Preserve selected synchronized Nintendo game mix; avoid unrelated intros/results and non-game commentary.',
      'candidatesWithAdditionalIp':'The first inspected CP battle uses a Minecraft stage; prefer original Nintendo stages where available. Any adopted third-party IP needs its applicable public-use review before publication.'}},
   {'id':'dicey','title':'Dicey Dungeons: Reunion','genre':'turn-based dice/deck-building roguelike','nintendo':False,
    'publisher':'Terry Cavanagh','official':'https://terrycavanaghgames.com/dice/presskit/desktop/',
    'role':'Observable enemy dice/card action connects the general perception-of-fairness passage to a different genre.',
    'equivalence':'Replaces the board-game dice example without claiming the game rigs rolls. The selected Reunion footage is named as that edition.',
    'beginnerRules':'Place rolled dice into equipment; values and conditions select allowed effects. An enemy turn displays enemy moves.',
    'versionReason':'2022 official Reunion footage preserves the same dice/equipment decision role; no2018 prototype AI algorithm is claimed for the release.',
    'rights':{'publisherPolicy':'https://distractionware.com/blog/video-policy/',
      'provenance':'Original official developer trailer, current uploader Terry Cavanagh; no third-party finished review/lesson used.',
      'policyEvidenceScope':'Primary developer video-policy search excerpt permits videos of the developer\u2019s games for any purpose; full page is currently behind a public Cloudflare check, so final publication rights remain separately reviewable.',
      'sourceAudio':'Preserve synchronized official game mix when footage has no competing narration; never distribute source music by itself.'}}],
  'files':[
   ('smash-cpu','smash','smash-cpu-I3LV8o_xhR8-section.mp4','https://www.youtube.com/watch?v=I3LV8o_xhR8','Creative Commons Attribution license (reuse allowed)'),
   ('smash-mario','smash','smash-mario-INk1W8OujQI.mp4','https://www.youtube.com/watch?v=INk1W8OujQI','Nintendo official promotional gameplay'),
   ('smash-samus','smash','smash-samus-I9tcvSeemVo.mp4','https://www.youtube.com/watch?v=I9tcvSeemVo','Nintendo official promotional gameplay'),
   ('dicey-reunion','dicey','dicey-reunion-fVsWXAAccVg.mp4','https://www.youtube.com/watch?v=fVsWXAAccVg','Original official developer trailer')],
  'addedExplanation':['Smash accumulated-damage and launch-out rule beside its first named example.','Explicitly labeled2-space reach/3-space separation model, not measured game statistics.','Decision priority/switch conditions resolve approach/retreat conflict beside the original contradiction point.','A60fps illustration with12frames/0.2seconds defines reaction delay; never a claimed Ultimate setting.'],
  'primaryEvidence':['https://www.smashbros.com/en_US/howtoplay/mode.html','https://www.smashbros.com/ko_KR/item/index.html','https://terrycavanaghgames.com/dice/presskit/desktop/'],
  'corrections':[{'issue':'An initial title could imply invincibility and deliberate hit-taking.','resolution':'Before TTS, replace with the accurate question: why does game AI not fight perfectly? The argument concerns exploitable aggression, not intentional losing.'}],
  'rejected':['Hamster KOF95 source has no genuine1080p format; not adopted.','Original Dicey launch video and Nintendo VR trailer unavailable through current source fetch; no low-resolution substitute used.','Dicey Switch trailer lacks1080p; use official1080p Reunion clip instead.']}
}

for slug, spec in specs.items():
    project = ROOT / 'projects' / slug
    draft = json.loads((project/'planning/script-draft.json').read_text('utf-8-sig'))
    local = project/'production/local/batch-v1'
    source_rows=[]
    for sid,game,filename,url,license_text in spec['files']:
        path=local/'sources'/filename
        source_rows.append({'id':sid,'gameId':game,'role':'independent-gameplay',
            'url':url,**artifact(path),'decoded':video(path),'licenseLabel':license_text,
            'sourceAudioEnabled':True,'nativeSpeed':True,'finalSelectedWindows':'pending measured allocation; no repeated source intervals'})
    ref_id=spec['referenceId'];ref=local/'research'/('reference-'+ref_id+'.mp4')
    reference={'role':'research-reference-only','url':'https://www.youtube.com/watch?v='+ref_id,
        'durationSeconds':spec['referenceSeconds'],'video':artifact(ref),
        'captionJa':artifact(project/'sources'/('reference-'+ref_id+'.ja.vtt')),
        'wholeCaptionRead':True,'relevantVisualsViewed':True,
        'visualReviewScope':'Entire reference sampled at5s(D25)/8s(D26), with English burned captions and relevant exact stills read. Not a claim of human playback/listening.',
        'mustNeverEnterCutList':True}
    sections=[{'id':sid,'start':a,'end':b,'retainedTeachingPoint':point,
        'newScenes':[s['id'] for s in draft['scenes'] if sid in s['referenceSections']]}
        for sid,a,b,point in spec['sections']]
    scene_rows=[]
    for i,s in enumerate(draft['scenes']):
        scene_rows.append({'id':s['id'],'title':s['title'],'referenceSections':s['referenceSections'],
            'paragraphIds':[f"{s['id']}-p{n+1:02d}" for n in range(len(s['paragraphs']))],
            'renderer':'Motion Canvas for abstract relationships and screenshot analysis; independent FHD game recordings for actual behavior.',
            'rendererReason':'These are2D information/state diagrams, not self-authored commercial-game simulations.',
            'inheritedBoundary':None if i==0 else {'priorResult':' '.join(draft['scenes'][i-1]['paragraphs'][-1]['ko'].split('|')),
                'nextNeed':' '.join(s['paragraphs'][0]['ko'].split('|'))},
            'visualEvidence':'Actual source frames/gameplay plus progressive labeled2D diagrams; exact cut/word cues are measured after root voice arrives.',
            'holdSeconds':0,'timingStatus':'awaiting actual approved-source PCM; no invented seconds or speech retiming'})
    inputs=[artifact(project/'script/batch-v1'/('narration.'+lang+'.json')) for lang in ['ko','en','spoken-ko']]
    plan={'schemaVersion':1,'slug':slug,'episode':spec['episode'],'revision':'batch-v1','batchId':'design-finish-six-20261026',
        'status':'source-script-frozen-awaiting-root-sample-b','updatedAt':NOW,
        'authorization':{'userEvidence':'25~30도 한번에 만들어줘 그리고 검수표 만들어서 보여줘',
            'scope':'Finite six-video production to local four-output final review; no upload/scheduling/deletion/automatic continuation.'},
        'thesis':spec['thesis'],'reference':reference,'referenceMap':sections,'sourceCorrections':spec['corrections'],
        'omissions':[{'item':'Creator introduction, personal production history/delegation, loading music, end slate','reason':'Noninstructional creator framing omitted; no experience attributed to us.'}],
        'addedExplanation':spec['addedExplanation'],'games':spec['games'],'sources':source_rows,
        'nintendoExampleCount':{'numerator':1,'denominator':2,'targetOneThird':True,'nearestFeasibleRounding':1,
            'reason':'Two smallest sufficient concept-matched games; round2/3 to one Nintendo example. Game variants/cuts are not additional examples.'},
        'genreReview':{'previousCompletedEpisode':'D22 similar-game-design','previousGenres':['survival mining action','2D platform/level creation'],
            'selected':[g['genre'] for g in spec['games']],'reason':'Choose concept-matched different game mechanics/genres rather than only renaming the same kind of combat clip.'},
        'primaryEvidence':spec['primaryEvidence'],'rejectedCandidates':spec['rejected'],
        'scenes':scene_rows,'scriptInputs':inputs,
        'preTtsReview':{'wholeKoReadWithoutHeadings':True,'wholePairedEnRead':True,'referenceClaimOrderPreserved':True,
            'noCreatorFraming':True,'noRedundantHedges':True,'sourceExperienceClaimedAsOurs':False,
            'actualHumanListening':False,'scriptFreeze':'Do not alter these exact files after root starts paid voice generation without a material correctness reason.'},
        'contract':{'width':1920,'height':1080,'fps':60,'introFrames':120,'membershipFrames':600,
            'actualShare':0.6,'explanationShare':0.4,'ratioToleranceFrames':1,'nativeSourceSpeed':True,
            'noSourceIntervalReuse':True,'noLoopsSlowdownOrIdlePadding':True,
            'caption':{'style':'boxed-white-forest-v1/caption-clause-keyword-v1','fontSize':48,'center':[960,970],'maxLines':2},
            'proposedGameViewport':[224,52,1472,828],'palette':'research-black-v1','onscreenEditorialCredits':False,
            'bgm':'Original approved Nimbus — Eveningland, -28LUFS starting level and normal ducking; root common runtime.',
            'packedExplanationTimeline':True,'actualTimings':'pending root measured voice'},
        'delivery':{'localStorageRoot':f'projects/{slug}/production/local/batch-v1/delivery','provider':'local-filesystem',
            'requiredFiles':['captioned.mp4','clean.mp4','ko.srt','en.srt'],'userReviewClaimed':False},
        'platform':{'uploadAuthorized':False,'scheduleAuthorized':False,'driveAuthorized':False,'existingD22Preserved':True}}
    save(project/'planning/production-plan.json',plan)
    save(project/'sources/independent-footage.json',{'schemaVersion':1,'slug':slug,'revision':'batch-v1',
        'sources':source_rows,'games':spec['games'],'reference':reference,'selectedBankClock':'pending measured voice; source files preserved'})
    project_manifest={'schemaVersion':1,'slug':slug,'series':'D','episode':spec['episode'],'revision':'batch-v1',
        'status':plan['status'],'updatedAt':NOW,'titles':{'ko':draft['titleKo'],'en':draft['titleEn']},
        'sourceConcept':{'videoId':ref_id,'url':reference['url'],'role':'research-reference-only'},
        'currentRevision':{'id':'batch-v1','status':plan['status'],'productionComplete':False,
            'humanFinalReview':'not-observed','automaticNextVideo':False},
        'format':{'width':1920,'height':1080,'fps':60},
        'paths':{'script':inputs[0]['path'],'scriptEnglish':inputs[1]['path'],'scriptEn':inputs[1]['path'],
            'scriptSpoken':inputs[2]['path'],'productionPlan':f'projects/{slug}/planning/production-plan.json',
            'sources':f'projects/{slug}/sources/independent-footage.json',
            'checkpoint':f'projects/{slug}/production/batch-v1/checkpoint.json',
            'finalPlan':f'projects/{slug}/production/batch-v1/edit-plan.json'},
        'audio':{'backgroundMusic':'Nimbus — Eveningland, original approved file; -28LUFS/normal ducking',
            'humanWholeListening':'not-observed','newTtsOwner':'root; ElevenLabs own voice Sample B'},
        'delivery':plan['delivery'],
        'publishing':{'uploaded':False,'privateUploadAuthorized':False,'scheduleAuthorized':False,'automaticNextVideo':False},
        'approvals':{'script':'Internal whole paired KO/EN and source-order review completed; actual human listening not claimed',
            'render':False,'qa':False,'collected':False,'uploaded':False}}
    save(project/'project.json',project_manifest)
    save(project/'production/batch-v1/checkpoint.json',{'schemaVersion':1,'slug':slug,'revision':'batch-v1',
        'stage':plan['status'],'status':'active','updatedAt':NOW,'jobs':[],
        'nextAction':'Receive root-approved Sample B PCM/timings, lock native semantic banks and build the measured60:40 timeline/packed explanatory scenes.',
        'actualHumanListening':False,'uploadAuthorized':False,'automaticNextVideo':False})
    outline=['# '+draft['titleKo'],'','내부 제작용 전체 대본·씬 계획. 원본은 연구용이며 화면/소리/자막을 제작에 재사용하지 않습니다.','']
    for s in draft['scenes']:
        outline += ['## '+s['id']+' '+s['title'],'']
        for p in s['paragraphs']: outline += [' '.join(p['ko'].split('|')),'']
    (project/'planning/outline.md').write_text('\n'.join(outline),'utf-8')
    print(slug,len(source_rows),'FHD sources',len(scene_rows),'scenes; source/script plans saved')
