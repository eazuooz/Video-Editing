"""Register the user's exact new12 selection and source-first production plans.

No media generation, resource ownership, automation or platform action.
"""
from pathlib import Path
import datetime,hashlib,html,json,shutil
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
ID='original-tech-twelve-20261115';KEY='explicitOriginalTechTwelve20261115'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
MEDIA=Path('C:/Users/1/Videos/YamyamProduction')/ID
NINJA='https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-The-Legend-of-Zelda-Ocarina-of-Time-3D/Vol-2-Original-Development-Staff-Part-1/3-Let-s-Go-to-Toei-Kyoto-Studio-Park-/3-Let-s-Go-to-Toei-Kyoto-Studio-Park--231680.html'
EVIDENCE=['새롭게 원래 우리 쇼츠만들던 10개 토픽 추천해줘 그리고 닌텐도64 카메라영상이랑, 젤다 시간의 오카리나 락온시스템 요것도 2개 넣어서 제작하자12개','락온 영상은 이걸로 주제잡아서 진행해줘']
# First two are user-selected; the remaining ten are the recommended new topics.
TOPICS=[
 ('oot-ninja-show-z-targeting','The Legend of Zelda: Ocarina of Time','닌자쇼에서 찾은 젤다 락온의 비밀','Z-Targeting (Z 주목)','사슬의 원운동과 상대 선택·공격 차례를 구별해 설명',NINJA,True),
 ('mario64-lakitu-camera','Super Mario 64','마리오64는 왜 카메라맨을 게임 안에 넣었을까?','Third-person Camera (3인칭 카메라)','쥬게무를 통해 플레이어에게 시점 조작을 설명하는 방식','https://m1.nintendo.net/docvc/NUS/EUR/NSMP/NSMP_E.pdf',True),
 ('journey-sand-sparkle','Journey','모래알을 하나씩 안 그려도 사막이 반짝이는 이유','Sand Rendering (모래 렌더링)','보이는 모래의 질감과 반짝임을 나누어 표현','https://advances.realtimerendering.com/s2012/index.html',False),
 ('horizon-gpu-placement','Horizon Zero Dawn','나무를 하나씩 놓지 않고 숲을 만드는 법','GPU Procedural Placement (GPU 절차적 배치)','아티스트의 배치 규칙과 플레이어 주변 환경 생성','https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn',False),
 ('inside-temporal-antialiasing','INSIDE','지난 프레임으로 이번 화면의 계단을 줄인다?','Temporal Reprojection Anti-Aliasing (시간 재투영 안티앨리어싱)','현재 픽셀과 과거 화면 정보를 연결하는 원리','https://github.com/playdeadgames/temporal/blob/master/README.md',False),
 ('spiderman-swing-anchor','Marvel’s Spider-Man (2018)','거미줄이 붙는 곳이 달라지면 스윙도 달라진다','Swing Anchor (스윙 부착점)','부착 위치·줄 방향과 이동 경로의 관계','https://media.gdcvault.com/gdc2019/presentations/Sheahan_Doug_ConcreteJungleGym.pdf',False),
 ('control-destruction-pipeline','Control','컨트롤의 사무실은 어떻게 부술 준비를 해둘까?','Procedural Destruction Pipeline (절차적 파괴 제작 과정)','부술 수 있는 자산을 준비하는 과정과 실제 반응','https://www.gdcvault.com/play/1030643/Destructible-Environments-in-Control-Lessons',False),
 ('returnal-particle-tentacles','Returnal','입자를 이어 붙여 꿈틀거리는 촉수를 만든다?','Particle Hierarchy (입자 계층)','Housemarque가 발표한 촉수 이펙트의 입자 계층','https://www.gdcvault.com/play/1027742/Visual-Effects-Summit-Can-We',False),
 ('ratchet-dimension-streaming','Ratchet & Clank: Rift Apart','차원을 넘는 순간, 다음 세계는 언제 불러올까?','World Streaming (월드 스트리밍)','차원 전환과 데이터 불러오기·압축 해제의 연결','https://blog.playstation.com/2023/07/18/ratchet-clank-rift-apart-pc-specs-and-new-features-revealed/',False),
 ('doom-push-forward-healing','DOOM (2016)','체력을 채우려면 적에게 다가가라?','Push Forward Combat (전진을 유도하는 전투)','회복 보상이 접근·공격 행동을 유도하는 전투 순환','https://www.gdcvault.com/play/1024940/Embracing-Push-Forward-',False),
 ('botw-chemistry-rules','The Legend of Zelda: Breath of the Wild','불·물·전기를 장면마다 따로 만들었을까?','Chemistry Engine (화학 상호작용 엔진)','물질과 원소의 공통 규칙으로 이어지는 상호작용','https://www.gdcvault.com/play/1024562/Change-and-Constant-Breaking-Conventions',True),
 ('mariokart8-spin-boost','Mario Kart 8','벽을 달릴 땐 왜 부딪히면 빨라질까?','Spin Boost (스핀 부스트)','반중력 구간에서 충돌이 가속 보상이 되는 설계','https://www.nintendo.com/en-gb/News/2014/April/New-items-characters-and-courses-make-for-gravity-defying-fun-in-Mario-Kart-8-launching-May-30th-on-Wii-U-870260.html',True),
]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=str(p.resolve()),sha256=sha(p))
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def replace_value(text,key,value):
 mark=json.dumps(key)+':';a=text.index(mark)+len(mark)
 while text[a].isspace():a+=1
 _,z=json.JSONDecoder().raw_decode(text,a)
 replacement=json.dumps(value,ensure_ascii=False,indent=2).replace('\n','\n  ')
 return text[:a]+replacement+text[z:]
def insert_key(text,key,value):
 assert key not in json.loads(text)
 end=text.rfind('}');j=end-1
 while text[j].isspace():j-=1
 extra='  '+json.dumps(key)+': '+json.dumps(value,ensure_ascii=False,indent=2).replace('\n','\n  ')+'\n'
 return text[:j+1]+','+text[j+1:end]+extra+text[end:]

assert not (HERE/'batch.json').exists()
inventory=[]
for path in (ROOT/'projects').glob('shorts-*/project.json'):
 d=read(path);inventory.append(dict(slug=path.parent.name,title=d.get('title',d.get('titleKo','')),manifest=pin(path)))
AUTH=dict(id=KEY,userEvidence=EVIDENCE,recordedAtKst=NOW,fullProductionAuthorized=True,finiteBatch=True,
 intermediateApprovalRequired=False,localFinalReviewOnly=True,advanceWithinExactList=True,advanceOutsideList=False,
 automaticHeartbeatContinuation=False,youtubeAuthorized=False,driveAuthorized=False,schedulingAuthorized=False,
 deletionAuthorized=False,humanFinalReviewRequired=True)
projects=[]
for i,(suffix,game,title,term,focus,url,nintendo) in enumerate(TOPICS,1):
 slug='shorts-'+suffix;p=ROOT/'projects'/slug;assert not p.exists(),p
 row=dict(order=i,id=f'OT12-{i:02}',slug=slug,title=title,game=game,term=term,focus=focus,primarySource=url,
          selection='user-selected'if i<=2 else'agent-recommended-under-explicit-ten-topic-delegation',nintendoPrimaryExample=nintendo,
          project=f'projects/{slug}/project.json',status='source-research-active'if i==1 else'authorized-preproduction',
          fullSourceRead=i==1,independentFootageAcquired=False,footageRightsVerified=False,sourceFhdVerified=False,
          narrationLocked=False,voiceGenerated=False,finalOutputsVerified=False,humanApproval=False,platformStatus='not-uploaded')
 projects.append(row)
 manifest=dict(slug=slug,title=title+' #게임개발',format=dict(type='youtube-shorts',width=1080,height=1920,fps=60),
 status=row['status'],currentRevision='preproduction-v1',authorization=AUTH,mediaRoot=str(MEDIA/slug),
 paths=dict(checkpoint=f'projects/{slug}/production/checkpoint.json',productionPlan=f'projects/{slug}/planning/production-plan-v1.json'),
 primaryGame=game,researchSource=url,sourceRole='research-reference-only',publishReady=False,humanFinalReview=False)
 save(p/'project.json',manifest)
 plan=dict(schemaVersion=1,topicId=row['id'],batchId=ID,topic=title,technicalTerm=term,teachingFocus=focus,
 centralQuestion=title,sourceOrderRequired=True,source=dict(url=url,kind='primary-developer-or-publisher',role='research-reference-only',fullRelevantScopeRead=i==1),
 storyboardOrder=['actual independent game phenomenon and spoken mini-explanation','one hidden rule and one-variable own demonstration','actual game confirmation','answer opening question and brief spoken/visible recap'],
 independentGameplay=dict(status='not-acquired',rights='pending-recorder-and-publisher',decodedDimensions='not-verified',minimum=[1920,1080],nativeSpeed=True,originalAspect=True,sourceAudio='not-adopted-without-clearance'),
 exampleSelection=dict(game=game,role='specific implementation or documented development decision',reason='This named game is the subject of the mechanism; unrelated extra games would replace its teaching role.',nintendo=nintendo),
 rendererPlan=dict(default='Unity for own running demonstrations; Motion Canvas for labels/composition when useful',nativeScenesSaved=False,engineLaunched=False),
 preservation=dict(approvedQwenVoiceRequired=True,naturalSpeechSpeed=True,noArbitraryDurationCap=True,noUnrelatedReferenceFootage=True,fixedCaptionProfile=True),
 pending=['complete relevant primary-source read and claim mapping','independent rights-checked genuine FHD footage and actual before/action/result viewing','source-locked KO/EN narration and scene cues','guarded voice/native/composite work','clean/captioned/KO/EN output and real local final review'],
 music=dict(required=True,licensedFile='pending',duckMusicOnly=True,creditAtAbsoluteEndOfKoAndEnDescriptions=True),
 outputs=dict(clean=None,captioned=None,ko=None,en=None),actualViewing=False,actualListening=False,humanApproval=False)
 if suffix=='ratchet-dimension-streaming':plan['claimLimit']='Do not say SSD is universally required: the official PC article also specifies an HDD minimum configuration.'
 if suffix=='returnal-particle-tentacles':plan['claimLimit']='Only the documented particle hierarchy/tentacle VFX; do not infer gameplay collision or enemy AI from particles.'
 if suffix=='mariokart8-spin-boost':plan['claimLimit']='Spin Boost/Spin Turbo is scoped to anti-gravity interaction; do not describe all collisions as acceleration.'
 save(p/'planning/production-plan-v1.json',plan)
 save(p/'production/checkpoint.json',dict(schemaVersion=1,slug=slug,batchId=ID,updatedAtKst=NOW,phase=row['status'],
 sourceFactsVerified=i==1,sourceFootageVerified=False,narrationLocked=False,voiceGenerated=False,nativeCaptured=False,
 finalOutputsVerified=False,actualListening=False,humanApproval=False,platformActions=[],nextStep=plan['pending'][0 if i>1 else 1]))

lock=ROOT/'projects/shorts-oot-ninja-show-z-targeting'
image=Path('C:/Users/1/AppData/Local/Temp/codex-clipboard-1f087669-81f0-4a97-a1df-4314114c3dfc.png')
image_copy=MEDIA/lock.name/'research/user-topic-reference.png';image_copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(image,image_copy)
ko=[
 '젤다에서 적을 주목하면, 옆으로 돌아도 그 상대를 바라봅니다. 이 전투 방식에 교토의 닌자 공연이 어떤 힌트를 줬을까요?',
 '개발진은 도에이 교토 스튜디오 파크에서 서로 다른 두 가지를 봤습니다. 하나는 팽팽한 사슬을 사이에 두고 상대 주위를 도는 움직임이었죠.',
 '게임에서는 상대와 보이지 않는 줄로 이어졌다고 생각하면 쉽습니다. 앞뒤 입력은 거리를 바꾸고, 옆 입력은 상대 주위를 도는 움직임이 됩니다.',
 '다른 하나는 여러 적의 공격 차례였습니다. 공연에서는 한 명이 싸우는 동안 나머지가 기다렸습니다. 개발자는 이것을 여럿과 싸우는 문제의 해법으로 설명했죠.',
 '인터뷰에서 든 게임 사례는 숲의 신전의 두 스탈포스 전투입니다. 적을 주목하는 조작과, 여러 적의 공격 참여를 조절하는 설계를 함께 보겠습니다.',
 '사슬에서 본 상대 중심의 이동, 활극에서 본 공격의 차례. 닌자 공연은 적을 바라보는 방법뿐 아니라 전투를 읽기 쉽게 만드는 데에도 힌트를 준 겁니다.'
]
save(lock/'planning/narration-draft-v1.json',dict(schemaVersion=1,status='draft-before-independent-footage-lock',language='ko',paragraphs=ko,
 wordCountWhitespace=sum(len(x.split())for x in ko),source=NINJA,englishDraftPending=True,approvedForTts=False,reason='Actual independent footage and exact observation remain required before final narration lock.'))
beats=[
 dict(id='S01',paragraphs=[1],kind='independent-gameplay',target='N64-version Z-target strafe around one opponent',observed=False),
 dict(id='S02',paragraphs=[2,3],kind='own-Unity-demonstration',target='same actors/cameras; facing changes from free movement to target-relative orbit',sceneSaved=False),
 dict(id='S03',paragraphs=[4],kind='own-Unity-demonstration',target='same enemy set; one attack participant versus simultaneous attacks',sceneSaved=False,claim='teaching illustration, not Nintendo code or measured AI'),
 dict(id='S04',paragraphs=[5],kind='independent-gameplay',target='Forest Temple two-Stalfos encounter; actually inspect target and waiting behavior',observed=False),
 dict(id='S05',paragraphs=[6],kind='recap-over-existing-demonstration',target='two relationships visibly recapped with existing speech',sceneSaved=False)
]
save(lock/'planning/topic-source-review-v1.json',dict(schemaVersion=1,reviewedAtKst=NOW,userSelectedAngle='Kyoto ninja show and Ocarina of Time Z-targeting',source=NINJA,
 fullRelevantScopeRead='section3 article paragraphs from first-person-camera discussion through final studio-park recollection',
 factualDistinction='Osawa recalled the chain/orbit; Koizumi described attack turn-taking and the two-Stalfos example. Preserve their different perspectives rather than attributing one simple invention story to both.',
 limits=['No claim of inventing the first lock-on in all games.','Do not claim all enemies universally stop whenever Z is held.','Do not identify the attached clip as authentic historical footage of that visit.'],
 image=dict(original=pin(image),preservedCopy=pin(image_copy),role='user-topic-reference-only',productionReuseApproved=False),
 canonicalTerm=dict(english='Z-Targeting',korean='Z 주목',button='N64 Z; distinguish the 3DS L-button version'),
 gameplaySourcePolicy=dict(nintendoGuidelines='https://www.nintendo.co.jp/networkservice_guideline/en/index.html',reviewed=True,recorderPermissionVerified=False),
 teachingBeats=beats,actualSourceFootageAcquired=False,actualListening=False,humanApproval=False))
save(lock/'planning/scene-plan-v1.json',dict(schemaVersion=1,beats=beats,layout=dict(master=[1080,1920],fps=60,mobileCheckWidth=375,blackBackground=True,fixedCaptions=True),
 inputChangeOnly=True,gameInternalMeasurementClaim=False,speechTiming='pending-actual-voice',nativeCaptureStarted=False))

batch=dict(schemaVersion=1,batchId=ID,recordedAtKst=NOW,authorization=AUTH,selectedFirstTopic=projects[0]['slug'],topicCount=12,
 projects=projects,delivery=dict(mode='local-final-review',count=12,videoCompletionCount=0),existingArchitectural111ListModified=False,
 existingOutputsOrPlatformsModified=False,newAutomationCreated=False,nintendoPrimaryExampleCount=dict(numerator=4,denominator=12,basis='Nintendo official manuals/interviews/announcement and Nintendo-authored GDC session; topic-specific short examples are not padded.'),
 research='research-v1.json',checkpoint='checkpoint.json',reviewPage='preproduction-v1.html')
save(HERE/'batch.json',batch)
save(HERE/'checkpoint.json',dict(schemaVersion=1,batchId=ID,updatedAtKst=NOW,phase='lockon-source-and-scene-preproduction',
 currentSlug=projects[0]['slug'],registeredTopics=12,localFinalVideos=0,sourceNarrationDraftCount=1,independentFootageVerifiedCount=0,
 actualGpuJobsStarted=0,intermediateApprovalRequired=False,platformActions=[],nextStep='Acquire rights-checked genuine FHD independent N64 Z-target/Stalfos footage; inspect and bind the draft and visual cues before TTS.'))
save(HERE/'research-v1.json',dict(schemaVersion=1,checkedAtKst=NOW,candidates=projects,existingManifestInventory=inventory,
 duplicateReview=dict(existingShortsCompared=True,selectedSlugsAllNew=True,notes='Original game-tech shorts rather than the architectural111 curriculum. The DOOM topic is the health/aggression reward loop, not the existing classic DOOM sound alert or the lock-on turn-taking topic. Portal geometry shorts differ from Ratchet world streaming.'),
 referencesAreProductionFootage=False,allCandidateLectureVideosFullyViewed=False,sourceFootageRightsAndFhdRemainPending=True))

control=ROOT/'shared/publishing/video-production-control.json';before=control.read_bytes();text=before.decode('utf-8-sig');value=dict(id=KEY,status='explicit-twelve-preproduction',requestedAtKst=NOW,userEvidence=EVIDENCE,
 batch=str((HERE/'batch.json').relative_to(ROOT)).replace('\\','/'),scope='Exactly these new12 original technical shorts through local final review; lock-on first with the user-selected ninja-show angle.',
 automaticAdvanceWithinExactList=True,automaticAdvanceOutsideList=False,automaticHeartbeatContinuation=False,humanFinalReviewRequired=True,
 youtubeAuthorized=False,driveAuthorized=False,schedulingAuthorized=False,deletionAuthorized=False,currentSelectedProject=projects[0]['project'],
 resourcePolicy='Existing full resource guards and cooperative singleton/lease; one costly job, preserve all other apps/jobs and automation scopes.',
 intermediateApprovalRequired=False)
after=insert_key(text,KEY,value);assert {k:v for k,v in json.loads(after).items()if k!=KEY}==json.loads(text)
control.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+after.encode('utf8'))
work=ROOT/'shared/publishing/video-worklist.json';before=work.read_bytes();text=before.decode('utf-8-sig');d=json.loads(text);old_rows=list(d['rows']);assert not any(x['id'].startswith('OT12-')for x in old_rows)
last=max(x.get('seriesOrder',0)for x in old_rows if x['series']=='S')
new_rows=[dict(id=x['id'],slug=x['slug'],series='S',seriesOrder=last+x['order'],title=x['title'],productionComplete=False,
 productionStatus='락온 자료·장면 구성 중'if x['order']==1 else'신규 12편 명시 제작 선택',executionStatus='이번12편 제작 선택',
 reviewStatus='완성본 미생성',humanApproval=None,platformStatus='미업로드',localMasterAvailable=False,latestRulesPassed=None,
 notes='새 유한12편 선택. 기존111편·완성본·업로드 상태 보존.',sourceEvidence=x['primarySource'],evidence=[str((HERE/'batch.json').relative_to(ROOT)).replace('\\','/')])for x in projects]
text=replace_value(text,'rows',old_rows+new_rows)
text=insert_key(text,KEY,dict(batch=str((HERE/'batch.json').relative_to(ROOT)).replace('\\','/'),ids=[x['id']for x in projects],selectedFirst=projects[0]['id'],updatedAtKst=NOW,authorization=AUTH))
after=json.loads(text);assert after['rows'][:len(old_rows)]==old_rows
assert {k:v for k,v in after.items()if k not in('rows',KEY)}=={k:v for k,v in d.items()if k!='rows'}
work.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+text.encode('utf8'))

marker='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
section='\n'+marker+'\n## 새 게임 개발 기술 쇼츠 12편\n\n2026-11-15 사용자 명시 선택. 새 추천10개와 마리오64 카메라·오카리나의 시간 락온2개를 제작한다. 락온은 교토 닌자 공연의 영감으로 먼저 구성하며, 전체 완성 영상은 아직0편이다. 중간 승인 없이 로컬 최종 검수까지 진행하고 업로드·예약·다른 자동화는 변경하지 않는다.\n\n| 순서 | 토픽 | 상태 |\n|---:|---|---|\n'
section+='\n'.join(f"| {x['order']} | {x['title']} | {'자료·장면 구성 중'if x['order']==1 else'제작 선택·자료 준비'} |"for x in projects)+'\n\n[12편 제작 목록](../production/batches/'+ID+'/preproduction-v1.html)\n'+end+'\n'
doc=ROOT/'docs/VIDEO_WORKLIST.md';before=doc.read_text(encoding='utf-8-sig');assert marker not in before;doc.write_text(before+section,encoding='utf8',newline='\n')
doc=ROOT/'docs/VIDEO_WORKFLOW.md';before=doc.read_text(encoding='utf-8-sig');assert marker not in before
doc.write_text(before+'\n'+marker+'\n2026-11-15 사용자 새 명시 선택은 추천10개와 지정한 N64 카메라·오카리나의 시간 락온2개의 정확12편을 기존 쇼츠 문법으로 로컬 최종검수까지 제작하는 유한 허가다. [제작 목록](../production/batches/'+ID+'/batch.json)의 편만 대상이며, 락온은 사용자가 제공한 교토 닌자공연 주제로 먼저 진행한다. 중간 승인 없이 기술적 선택을 하되 실제 독립 FHD 영상·권리·원문 근거·승인 음성·자체 검수 조건을 유지한다. 새 자동화 생성이나 기존111 목록·다른 작업·플랫폼 상태 변경을 허용하지 않는다.\n'+end+'\n',encoding='utf8',newline='\n')

esc=html.escape
rows=''.join(f'<tr><td>{x["order"]}</td><td><b>{esc(x["title"])}</b><br>{esc(x["game"])}</td><td>{esc(x["focus"])}</td><td><a href="{esc(x["primarySource"],quote=True)}">1차 자료</a><br>{"구성 초안·자료 확보 중"if x["order"]==1 else"제작 선택"}</td></tr>'for x in projects)
page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>새 기술 쇼츠12편 제작 목록</title><style>body{max-width:1100px;margin:36px auto;padding:0 20px;background:#111;color:#eee;font:17px/1.7 system-ui}h1,h2{color:#f5da8a}a{color:#c6e3ff}table{width:100%;border-collapse:collapse}td,th{padding:14px;border-bottom:1px solid #444;text-align:left;vertical-align:top}small{color:#bbb}</style><h1>새 게임 개발 기술 쇼츠12편</h1><p>추천10개 + 사용자 지정2개. 실제 완성 영상 <b>0/12</b>. 현재는 출처·대본·장면 준비이며 영상 검수 페이지가 아닙니다.</p><table><tr><th>순서</th><th>제목·게임</th><th>핵심</th><th>근거·상태</th></tr>'+rows+'</table><h2>락온 편 구성 초안</h2><p>교토 닌자공연에서 얻은 서로 다른 두 힌트를 구별합니다. 아래 대사는 독립 영상 대조 전 초안이며 TTS 확정본이 아닙니다.</p>'+''.join('<p>'+esc(x)+'</p>'for x in ko)+'<h2>제작 경계</h2><p>독립 게임 영상의 실제 권리·FHD·동작을 확인한 뒤 대사를 잠그고 제작합니다. clean / captioned / KO / EN 완성본은 로컬 최종 검수로 전달합니다. 아직 음성·엔진 촬영·완성 영상·사람 검수·업로드는 없습니다.</p></html>'
(HERE/'preproduction-v1.html').write_text(page,encoding='utf8')
save(HERE/'registration-validation-v1.json',dict(schemaVersion=1,registeredAtKst=NOW,topicCount=12,distinctSlugs=len({x['slug']for x in projects}),
 recommendedCount=10,userSelectedCount=2,originalGlobalRowsPreserved=True,originalControlKeysPreserved=True,
 newProjectCount=12,lockonDraftParagraphs=len(ko),localFinalVideoCount=0,newAutomationCreated=False,platformActions=[],
 files=[pin(path)for path in [HERE/'batch.json',HERE/'checkpoint.json',HERE/'research-v1.json',HERE/'preproduction-v1.html',lock/'planning/topic-source-review-v1.json',lock/'planning/narration-draft-v1.json']]))
print(json.dumps(dict(batch=str(HERE/'batch.json'),page=str(HERE/'preproduction-v1.html'),topics=12,lockonDraftWords=sum(len(x.split())for x in ko),localFinalVideos=0),ensure_ascii=False))
