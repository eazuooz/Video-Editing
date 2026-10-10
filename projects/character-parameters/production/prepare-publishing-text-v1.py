"""Prepare local metadata and lossless thumbnail packaging; no platform action."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
PUB=BASE.parent/'publishing'; read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not (PUB/'publishing-text-preparation-v1.json').exists(), 'Read existing preparation rather than replace it.'
request=read(BASE/'narration-tts-request-v1.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
ko=read(BASE.parent/'script/narration.ko.json'); en=read(BASE.parent/'script/narration.en.json')
assert len(ko['scenes'])==12 and sum(len(s['lines']) for s in ko['scenes'])==37
assert [s['id'] for s in ko['scenes']]==[s['id'] for s in en['scenes']]
coaching=defaults['coaching']['url']; member=defaults['membershipUrl']; discord='https://discord.gg/wZuqe7fqkR'
snapshot=(ROOT/defaults['description']['channelDefaultSnapshot']).read_text('utf-8-sig')
footer=snapshot.split('📚 수업 노트')[0].rstrip().rstrip('━').rstrip()
assert all(x in footer for x in [coaching,member,discord])
body_ko=('공격력과 속도만 다르면 캐릭터의 플레이 방식도 달라질까요? 라이벌즈 오브 이더의 공통 동작과 불·물·연기 같은 고유 규칙을 보며, 강점과 약점이 플레이어의 선택을 어떻게 만드는지 살펴봅니다.\n\n'
 '던전스 오브 이더에서는 방어, 동전, 주사위와 다음 턴 효과를 구분합니다. 기본 성능과 현재 상태, 효과의 조건·대상·시점을 나눠 읽고, 수치를 조정해도 캐릭터의 역할을 남기는 방법을 정리합니다.\n\n'
 '대전 자료는 과거 경기이며 현재 캐릭터 순위를 평가하지 않습니다. 적의 통로 배치와 조합은 설계 예시로, 실제 플레이테스트가 필요한 부분입니다.')
body_en=('Does changing attack power and speed automatically change a character’s playstyle? Examine shared actions and distinctive fire, water and smoke rules in Rivals of Aether, then connect strengths and limitations to player choices.\n\n'
 'Dungeons of Aether provides separate examples of defense, coins, dice and effects applied on the next turn. We distinguish base capabilities from current state, specify triggers, targets and timing, and preserve a character’s role while tuning values.\n\n'
 'The match footage is historical and does not establish current character rankings. Enemy placement and combinations are hypothetical design examples that require actual playtests.')
footer_en=('🎮 YamYamCoding helps you build practical game-programming skills through design and implementation.\n\n'
 '🚀 Premium one-to-one coaching\nDirectX 11/12, Unity, Unreal Engine, computer graphics, PBR, shaders, rendering, game engines, and graphics research implementation.\n'+coaching+'\n\n'
 '💬 Community: questions, code reviews, feedback, and study materials\nDiscord\n'+discord+'\n\nYouTube membership\n'+member)
for lang,script,body,foot,tags in [('ko',ko,body_ko,footer,'#게임개발 #게임디자인 #캐릭터디자인'),('en',en,body_en,footer_en,'#GameDevelopment #GameDesign #CharacterDesign')]:
    desc=body+'\n\n'+foot+'\n\n'+tags+'\n'
    (PUB/f'description-body.{lang}.txt').write_text(body+'\n','utf-8')
    (PUB/f'description-prepared.{lang}.txt').write_text(desc,'utf-8')
    chapters='\n'.join('- '+s['title'] for s in script['scenes'])
    (PUB/f'youtube.{lang}.md').write_text('# 게시 정보 초안 — 준비만 완료\n\n실제 음성과 최종 편집 검수 후 챕터 시간을 추가한다. 업로드·설정·예약 증거가 아니다.\n\n## 제목\n\n'+script['title']+'\n\n## 설명\n\n'+desc+'\n## 챕터 순서 — 시간 미측정\n\n'+chapters+'\n','utf-8')
(PUB/'pinned-comment.ko.txt').write_text('내 캐릭터가 어떤 상황에서 어떤 선택으로 기억될지 한 문장으로 적어 보세요. 게임 프로그래밍을 함께 설계하고 구현하는 1:1 과외 안내: '+coaching+'\n','utf-8')
original=PUB/'thumbnail-v1.png'; packed=PUB/'thumbnail-upload-v1.png'
assert original.exists() and not packed.exists()
with Image.open(original) as im:
    dimensions=list(im.size); im.save(packed,optimize=True,compress_level=9)
with Image.open(original) as a,Image.open(packed) as b:assert a.mode==b.mode and a.tobytes()==b.tobytes(), 'Lossless packaging must preserve every pixel.'
thumbnail=packed
if packed.stat().st_size>=2*1024*1024:
    thumbnail=PUB/'thumbnail-upload-v1.jpg'
    with Image.open(original) as im:im.convert('RGB').save(thumbnail,quality=94,subsampling=0,optimize=True)
assert thumbnail.stat().st_size<2*1024*1024
proof=dict(schemaVersion=1,slug='character-parameters',preparedAt=datetime.now(timezone.utc).isoformat(),status='prepared-only-before-measured-voice-and-final-media',titles={'ko':ko['title'],'en':en['title']},actualVideoId=None,uploaded=False,scheduled=False,targetDate='2026-10-30',targetTime='09:00',timezone='Asia/Seoul',targetIsPlatformReservation=False,
 plannedChapters=[dict(scene=s['id'],titleKo=s['title'],titleEn=t['title'],startSeconds=None) for s,t in zip(ko['scenes'],en['scenes'])],measuredChaptersPrepared=False,exactCanonicalLinks={'coaching':coaching,'discord':discord,'membership':member},channelIntroductionPreserved=True,unfilledChannelPlaceholdersOmitted=True,publicSourceCredits=False,
 thumbnail=rel(thumbnail),thumbnailOriginal=rel(original),thumbnailPackaging={'losslessPng':rel(packed),'sameDecodedPixelsVerified':True,'jpegEncodingOnly':thumbnail.suffix=='.jpg','semanticImageEdits':False,'bytes':thumbnail.stat().st_size,'dimensions':dimensions},
 card={'startSeconds':0,'url':coaching,'saved':False},endScreen={'durationSeconds':10,'startSeconds':None,'elements':defaults['endScreen']['elements'],'saved':False},pinnedComment={'path':rel(PUB/'pinned-comment.ko.txt'),'status':'pending-video-publication','posted':False,'pinned':False},
 platformSettingsVerified=False,savedPlatformThumbnailVerified=False,manualSrtPublished=False,englishMetadataPublished=False,uploadedCcOffPixelsVerified=False,actualAdChecksComplete=False,humanListening='pending',humanPronunciation='pending',finalPublicRights='pending',localOnly=True,imagesGitAdded=0)
proof['files']=[dict(path=rel(p),sha256=sha(p)) for p in sorted(PUB.iterdir()) if p.is_file()]
save(PUB/'publishing-text-preparation-v1.json',proof)
thumb=dict(schemaVersion=1,reviewedAt=proof['preparedAt'],generationMethod='built-in image_gen',sourceGeneratedPath='C:/Users/eazuo/.codex/generated_images/01a0f1af-3710-7742-b7c9-87594dc45400/exec-c4e13383-884e-4c5c-8970-21ca4f79fe41.png',original={'path':rel(original),'sha256':sha(original),'bytes':original.stat().st_size,'dimensions':dimensions},uploadCandidate={'path':rel(thumbnail),'sha256':sha(thumbnail),'bytes':thumbnail.stat().st_size},
 exactTexts=['얌얌코딩 | 게임 기획·디자인','능력치만 바꾸면','개성이 생길까?'],directOriginalReview={'entireImageRead':True,'yellowHeaderWhiteGroundBlackRedHeadline':True,'naturalCalicoCats':True,'defenseAndMobilityRolesShown':True,'illustratedConceptNotVideoInset':True,'noPptPaste':True},uploadCandidateDirectlyRead=False,preparedOnly=True,essentialGitRegistryAdded=False,imagesGitAdded=0,savedPlatformThumbnailVerified=False)
save(BASE/'prepared-thumbnail-direct-review-v1.json',thumb)
print(json.dumps({'thumbnail':rel(thumbnail),'bytes':thumbnail.stat().st_size,'dimensions':dimensions,'uploaded':False,'chaptersMeasured':False},ensure_ascii=False))
