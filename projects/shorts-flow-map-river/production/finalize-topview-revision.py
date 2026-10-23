"""Record the locally reviewed V3 master and four outputs; preserve platform receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil

P=Path(__file__).resolve().parents[1];R=P.parents[1]
L=P/'production/local/topview-v3';O=P/'production/local/final-topview-v3';A=P/'production/local/audio'
REV='flow-map-topview-v3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(R).as_posix()

now=datetime.now(timezone.utc).isoformat();cp=read(P/'production/checkpoint.json')
assert cp['revision']==REV and cp['revisionAuthorization']['id']==REV
assert cp.get('stage')!='ready-for-local-final-review','Already finalized; preserve the existing review state.'
assert read(R/'shared/publishing/video-production-control.json')['selectedShortVideo']==P.name
b=read(O/'build.json');integrity=read(O/'integrity.json');head=read(O/'header-integrity.json')
assert integrity['status']==head['status']=='pass'
assert sha(O/'captioned.mp4')==b['captionedSha256']==head['masterSha256']
assert len(set(b['audioPcmHashes'].values()))==1
assert read(O/'qa/browser-playback.json')['ended'] is True
assert 'leader' in read(L/'source-audio-asr.json')['text']
receipt_before=sha(P/'publishing/youtube-upload.json')
master=dict(path=rel(O/'captioned.mp4'),sha256=b['captionedSha256'])
out=R/'output'/P.name/'topview-v3';out.mkdir(parents=True,exist_ok=True);files=[]
for source,name in [(O/'captioned.mp4',P.name+'.captioned.mp4'),(O/'clean.mp4',P.name+'.clean.mp4'),(A/'captions.ko.srt',P.name+'.ko.srt'),(A/'captions.en.srt',P.name+'.en.srt')]:
    dest=out/name
    if dest.exists():assert sha(dest)==sha(source)
    else:shutil.copyfile(source,dest)
    files.append(dict(name=name,source=rel(source),bytes=dest.stat().st_size,sha256=sha(dest)))
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>플로 맵 · 탑뷰 도입 수정본</title><style>body{background:#151a17;color:white;font:17px sans-serif;margin:24px}a{color:#ffd25a}video{width:375px;max-width:100%}</style><h1>플로 맵 · 탑뷰 도입 수정본</h1><p>51초 · 1080×1920 · 60fps</p><p>실제 게임에서 물길 관찰 → Unity 플로 맵 시연</p><video controls src="'''+P.name+'.captioned.mp4"></video><ul>'+''.join('<li><a href="'+f['name']+'">'+f['name']+'</a></li>' for f in files)+'</ul><p>기존 음성·배경음악·한영 자막 유지 · 최종 검수 대기</p></html>'
(out/'index.html').write_text(html,encoding='utf-8')
delivery=dict(directory=rel(out),captioned=rel(out/(P.name+'.captioned.mp4')),index=rel(out/'index.html'))
save(P/'production/delivery-output.json',dict(slug=P.name,revision=REV,createdAt=now,**delivery,previousDeliveryDirectories=['output/'+P.name,'output/'+P.name+'/gameplay-v2'],publishReady=False,files=files,cues=24,captionAlignment='unchanged24KO/ENcueTiming',video=dict(width=1080,height=1920,fps=60,frames=3067,durationSeconds=3067/60)))

source=dict(id='choyas-eow-zora-river',kind='independent-gameplay',url='https://www.youtube.com/watch?v=Vdo4j20k0Rg',
    title="Zelda: Echoes of Wisdom - Let's Play Part 7: River & Sea Zora Village",creator='ChoyasGaming',
    channelUrl='https://www.youtube.com/channel/UCINhOMvGcHV7GUsfPRJAmqA',originalUpload='2024-12-11',
    file=b['source'],sha256=b['sourceSha256'],recordingSize=[1920,1080],decodedFps='60/1',playbackSpeed=1,
    originalWindow=[0,300],selectedWindow=[253.5,257.9],license='Creative Commons Attribution license (reuse allowed)',
    licenseEvidence=rel(L/'Vdo4j20k0Rg.info.json'),licenseDefinition='https://support.google.com/youtube/answer/2797468',
    publisherPolicy='https://www.nintendo.co.jp/networkservice_guideline/en/index.html',
    publisherEvidence='https://www.nintendo.com/ph/switch/bdge/products/soft.html',
    adaptation='Short excerpt, proportional contextual crop, educational narration and editorial rock outline. No endorsement implied.',
    genre='Action adventure / environmental puzzles',teachingRole='Observed water flowing through separate stone channels from an elevated downward camera; opening question only.',
    actualShaderImplementation='Unverified. This recording is not evidence that this game uses flow maps. All declarative shader steps remain on our own Unity implementation.',
    audio='Source commentary detected: so now we know who the leader is. Omit inseparable commentator/game mix; preserve exact approved narration+BGM PCM.',
    audioEvidence=rel(L/'source-audio-asr.json'),viewingEvidence=[rel(L/'opening-start.jpg'),rel(L/'opening-contact.jpg'),rel(O/'qa/sheet0.jpg')],
    reason='Native FHD60, CC recording, elevated view with visibly downward foam and separated channels. Replaces low-angle swamp where camera motion obscured water motion.',
    activeRevision=REV)
sources=read(P/'sources/sources.json')
for s in sources['sources']:
    if s.get('id')=='scuprikov-l4d2-swamp':s.update(activeRevision='flow-map-gameplay-v2',usedInCurrentRevision=False,retainedFor='Preserved V2 master and actual uploaded receipt')
sources['sources']=[s for s in sources['sources'] if s.get('id')!=source['id']]+[source]
save(P/'sources/sources.json',sources)
plan=read(P/'planning/production-plan.json')
if 'baselineV2' not in plan:
    plan['baselineV2']={**cp['baselineV2'],'gameplayCuts':plan.get('gameplayCuts',[]),'screenShare':plan['screenShare'],'finalMaster':plan.get('finalMaster')}
plan.update(revision=REV,status='ready-for-local-final-review',latestUserSteering=cp['revisionAuthorization'],finalMaster=master,
    humanFinalReview='pending-for-this-exact-v3-master',platformActionsAuthorized='No V3 upload/publication/scheduling/deletion requested; retain private H7wG7HODyww.')
plan['gameplayCuts']=[dict(id='topview-game-opening',startFrame=0,endFrame=264,sourceId=source['id'],sourceIn=253.5,sourceOut=257.9,
    kind='independent-gameplay',renderer='FFmpeg composite; native game recording',beforeActionResult='Above-water camera shows white foam crossing shallow surfaces and descending through stone-separated channels; camera follows the player.',
    crop=dict(native=[360,160,1248,840],destination=[20,600,1040,700],scale='5/6 uniformly',reason='Enlarge the narrated water and stone channels; crop nonessential outer combat/minimap UI, no source watermark present.'),
    audio=source['audio'],annotation=dict(meaning='Editorial identification of the rock between two visible water channels, not measured flow data',times=[.1,.7],shape='hollow green contour and 바위 label',tracking='Manually inspected camera translation; fade out before target approaches crop edge'),
    speech=['p1-1','p1-2'],hold=0,captionClearance='Picture ends1300; unchanged fixed caption box begins below it; title/source-kind header above540, game title562.',
    gameSpecificTechnicalClaim=False)]
plan['screenShare'].update(independentGameplay=264/3067,explanation=2803/3067,independentGameplaySeconds=4.4,explanationSeconds=2803/60,
    reason='User-selected technical Short: open on the clearest observed overhead game water. Original shader demonstration stays intact; no footage quota padding.')
plan['continuity']='Frame0 actual overhead river → question about simulating water → at4.4s our Unity scene, before 이 장면은 at4.6s → original direction map, RG example, texture-coordinate movement, two-phase reset, moving-obstacle limit. BGM and speech remain sample-identical; no chapter reset.'
plan['recommendedChoices'].append(dict(choice='Use native1080p60 Echoes of Wisdom for the first4.4s; restore own demonstration during later shader explanations',reason='Clear downward camera and visible stone channels satisfy the latest request. Do not use an unverified game screenshot to assert its shader implementation. Source commentary excluded after actual ASR; no unnecessary TTS/GPU work.'))
plan['exampleCount']=dict(primaryGames=1,nintendoGames=1,nintendoEvidence=source['publisherEvidence'],reason='Smallest sufficient actual-game observation for this technical Short; no added unrelated games to force a fraction.')
save(P/'planning/production-plan.json',plan)

# The actual V2 upload receipt is immutable here. Description files describe the
# new local candidate only, ready for a later reviewed-version upload request.
for lang in ['ko','en']:
    for name in [f'description.{lang}.txt',f'upload-description.{lang}.txt']:
        path=P/'publishing'/name;text=path.read_text(encoding='utf-8')
        begin=text.find('- 실제 게임 녹화: SCuprikov') if lang=='ko' else text.find('- Gameplay recording: SCuprikov')
        end=text.find('- Alex Vlachos',begin)
        if begin>=0 and end>begin:
            if lang=='ko':
                credit='- 실제 게임 녹화: ChoyasGaming, Zelda: Echoes of Wisdom - Let\'s Play Part 7: River & Sea Zora Village\n  https://www.youtube.com/watch?v=Vdo4j20k0Rg\n  Creative Commons Attribution (YouTube CC BY): https://support.google.com/youtube/answer/2797468\n  4:13.5–4:17.9 발췌·비례 크롭·설명 및 표식 합성·원본 음성 제외. 제휴·보증을 의미하지 않습니다.\n- Nintendo 영상 이용 가이드라인: https://www.nintendo.co.jp/networkservice_guideline/en/index.html\n'
            else:
                credit='- Gameplay recording: ChoyasGaming, Zelda: Echoes of Wisdom - Let\'s Play Part 7: River & Sea Zora Village\n  https://www.youtube.com/watch?v=Vdo4j20k0Rg\n  Creative Commons Attribution (YouTube CC BY): https://support.google.com/youtube/answer/2797468\n  Excerpt4:13.5–4:17.9, proportionally cropped and annotated; original commentary omitted. No endorsement implied.\n- Nintendo Game Content Guidelines: https://www.nintendo.co.jp/networkservice_guideline/en/index.html\n'
            text=text[:begin]+credit+text[end:]
        if lang=='ko':
            text=text.replace('플로 맵(Flow Map)에 움직일 방향을 저장하고, 셰이더가 물결 무늬를 이동시키는 방법을 《레프트 4 데드 2》 실제 게임 장면과 직접 만든 Unity 시연으로 보여드립니다.',
                '《젤다의 전설: 지혜의 투영》에서 물길을 먼저 관찰한 뒤, 직접 만든 Unity 시연으로 플로 맵(Flow Map)에 방향을 저장하고 물결 무늬를 이동시키는 원리를 설명합니다. 게임 장면은 물의 모습에 대한 예시이며, 해당 게임의 내부 셰이더를 분석한 장면은 아닙니다.')
        else:
            text=text.replace('Real Left 4 Dead 2 footage and our Unity shader demonstration reveal the direction texture behind the effect: a flow map.',
                'We first observe river water in The Legend of Zelda: Echoes of Wisdom, then demonstrate a flow map in our own Unity shader. The game footage illustrates water appearance; it is not evidence of that game\'s internal shader implementation.')
        path.write_text(text,encoding='utf-8')

m=read(P/'project.json');m.update(currentRevision=REV,status='ready-for-local-final-review',updatedAt=now,delivery=delivery)
m['paths'].update(videoClean=rel(O/'clean.mp4'),videoBurnedCaptions=master['path'],audioMix=rel(O/'final-mix.m4a'))
m['finalRender']=dict(revision=REV,sha256=master['sha256'],technicalChecks='passed',knownIssues=[],openItems=['Human review of this exact V3 master pending; no new upload authorized.'])
m['uploadReview']=dict(status='pending-v3-human-review',masterSha256=master['sha256'],scope='Local review only; current V2 upload retained privately.')
save(P/'project.json',m)
cp.update(stage='ready-for-local-final-review',updatedAt=now,finalMaster=master,delivery=delivery,technicalChecks='passed',
    humanFinalReview='pending-v3-human-review',nextAction='User reviews exact V3 captioned master locally. Keep private H7wG7HODyww; do not upload/replace/delete/publish/schedule without new explicit authorization.')
cp['priorV2UploadAuthorization']=cp['youtubeUploadAuthorization']
cp['youtubeUploadAuthorization']=dict(status='not-authorized-for-v3',masterSha256=master['sha256'])
cp['uploadReview']=m['uploadReview'];save(P/'production/checkpoint.json',cp)
ledger=dict(slug=P.name,revision=REV,updatedAt=now,masterSha256=master['sha256'],baselineV1=cp['baselineV1'],baselineV2=cp['baselineV2'],
    checks=[dict(id='native-fhd-source-and-rights',status='pass',evidence=rel(P/'sources/sources.json')),
        dict(id='frame0-gameplay',status='pass',frames=[0,264],evidence=rel(O/'qa/sheet0.jpg')),
        dict(id='game-observation-vs-own-implementation',status='pass',summary='Switch at4.4s before declarative own-shader explanation4.6s. No game-specific flow-map implementation assertion.'),
        dict(id='video-integrity',status='pass',evidence=rel(O/'integrity.json')),
        dict(id='header-all-frames',status='pass',evidence=rel(O/'header-integrity.json')),
        dict(id='voice-bgm-pcm-and-caption-preservation',status='pass',evidence=rel(O/'build.json'),pcmHashes=b['audioPcmHashes'],cueCount=24,summary='Exact decoded PCM matches approved V1; unchanged voice pronunciation/timing/audio evidence reused.'),
        dict(id='source-commentary-excluded',status='pass',evidence=rel(L/'source-audio-asr.json')),
        dict(id='native-mobile-and-join-review',status='pass',evidence=rel(O/'qa'),summary='16nativeframes,375pxsheets and actual browser playback. Water enlarged proportionally; game chip/contour/caption clearance checked; cut at4.4s has no black frame.'),
        dict(id='human-final-review',status='pending',masterSha256=master['sha256'])],
    platform=dict(youtubeV3='not-uploaded',currentUploadedVideoId='H7wG7HODyww',currentUploadedRevision='flow-map-gameplay-v2',privacy='private',oldVideo9cRdnf8wKEI='permanently-deleted-after-user-confirmation',drive='ExistingV1preserved;noV3request',automaticNextVideo=False))
save(P/'production/review-ledger.json',ledger)
wpath=R/'shared/publishing/shorts-worklist.json';w=read(wpath);matches=[]
def visit(x):
    if isinstance(x,list):
        for y in x:visit(y)
    elif isinstance(x,dict):
        if x.get('slug')==P.name and 'title' in x:matches.append(x)
        else:
            for y in x.values():visit(y)
visit(w);assert len(matches)==1
if matches[0].get('youtubeUploadAuthorization',{}).get('masterSha256')!=master['sha256']:
    matches[0]['priorV2UploadAuthorization']=matches[0].get('youtubeUploadAuthorization')
matches[0].update(revision=REV,status=m['status'],updatedAt=now,production='Complete51.1167s1080x1920/60;real overhead game fromframe0,thenUnity/MC',review='InternalQApassed;exactV3humanfinalreviewpending',finalMaster=master,delivery=delivery,
    youtube='V2 H7wG7HODyww uploaded-private; V3 not uploaded',youtubeUploadAuthorization=cp['youtubeUploadAuthorization'],
    v3Platform='Not uploaded; existingH7wG7HODywwV2private preserved',gameplaySource=source['id'])
w['updatedAt']=now;save(wpath,w)
assert sha(P/'publishing/youtube-upload.json')==receipt_before,'Actual V2 receipt must not be rewritten by local V3 delivery.'
print(json.dumps(dict(master=master,delivery=delivery,platform='V3 not uploaded; V2 retained'),ensure_ascii=False))
