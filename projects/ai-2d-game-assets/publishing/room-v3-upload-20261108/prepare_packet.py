"""Prepare metadata for the approved room-v3 master; never upload or render."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/ai-2d-game-assets'
OUT = Path(__file__).resolve().parent
MEDIA = Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video/review')
PLAY = 'https://yamyam-cartographers-room.eazuooz.chatgpt.site/'
COACH = 'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'
DISCORD = 'https://discord.gg/wZuqe7fqkR'
MEMBERSHIP = 'https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join'
NOW = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(name, value):
    path = OUT / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n' if not isinstance(value, str) else value.rstrip() + '\n', encoding='utf-8')

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

expected = {
    'captioned.mp4': '8e5fc1902c8c1ade2637769a496c613a5bb45d45758ca14eb94c7b345c6a3d1c',
    'clean.mp4': 'e194fb2d123872ac7e3e12b5e901eb50eb2aa28d1b5a1faf3405a3c4d58440b7',
    'ko.srt': '7e0af95d2b648a7a6aadfaa80dd3354246f83193f9087f46a0518bb0ab2aa877',
    'en.srt': '5346f43b51d5fdd6e6329a992931235a36bb0479af2520c73d413476777ff137',
}
files = []
for suffix, digest in expected.items():
    path = MEDIA / ('ai-2d-game-assets.' + suffix)
    actual = sha(path)
    assert actual == digest, (path, actual)
    files.append({'name': path.name, 'path': path.as_posix(), 'sha256': actual, 'bytes': path.stat().st_size})
probe = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate',
    '-of', 'json', str(MEDIA / 'ai-2d-game-assets.captioned.mp4')], text=True))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
assert (video['width'], video['height'], video['r_frame_rate']) == (1920, 1080, '60/1')
assert abs(float(probe['format']['duration']) - 1231.4) < 0.01

timeline_path = PROJECT / 'production/local/room-v3/timeline.json'
timeline = read(timeline_path)
scenes = {s['id']: s for s in timeline['scenes']}
chapter_specs = [
    ('01', 'AI 그림을 게임으로 만들려면', 'From AI art to a playable game'),
    ('R01', '직접 플레이할 작은 작업실', 'The playable workshop'),
    ('03', '캐릭터 디자인과 일관된 설정화', 'Character design and consistent references'),
    ('05', '학습 데이터·LoRA·실제 제작 경로', 'Datasets, LoRA, and our actual workflow'),
    ('08', 'ComfyUI와 스타일 LoRA 비교', 'ComfyUI and style LoRA comparison'),
    ('11', '픽셀 격자·팔레트·투명도 정리', 'Pixel grids, palettes, and transparency'),
    ('15', '배경 확장과 의자 접촉점 맞추기', 'Background expansion and chair contact'),
    ('17', '걷기와 행동 사이의 중간 동작', 'Walking and action transitions'),
    ('V32', '보폭을 실제 이동 거리와 연결', 'Matching stride to travel distance'),
    ('18', '2dimg2motion: 지도 읽기 14프레임', '2dimg2motion: a 14-frame map-reading loop'),
    ('19', 'sprite-gen: 시트 분할과 기준점', 'sprite-gen: slicing and registration'),
    ('20', 'pixelfx: 비·눈·불꽃과 조명', 'pixelfx: rain, snow, flames, and lighting'),
    ('21', 'PixelOE: 실제 표시 크기로 정리', 'PixelOE: cleanup at native display size'),
    ('22', 'Agent Sprite Forge: 프레임 조립', 'Agent Sprite Forge: assembling frames'),
    ('23', 'Codixel: 관절로 책 읽기·필기', 'Codixel: rigged reading and writing'),
    ('24', 'Pixelbolt: 픽셀 레시피와 소품', 'Pixelbolt: pixel recipes and props'),
    ('25', 'Sprite-Sheet-Diffusion 재현 시도', 'Sprite-Sheet-Diffusion reproduction attempt'),
    ('26', '내 작업에 맞는 도구 고르기', 'Choosing the right workflow'),
    ('27', 'Unity 적용과 웹 게임 연결', 'Unity import and web-game integration'),
    ('28', '게임 안에서 동작·가독성 검수', 'Checking motion and readability in-game'),
    ('29', '무료 코드와 생성 비용의 차이', 'Open-source code and generation costs'),
    ('30', '완성한 작업실과 로파이 라디오', 'The finished workshop and lo-fi radio'),
    ('R30', '직접 실행하고 제작 기록 보기', 'Play and inspect the production records'),
]
chapters = []
for i, (sid, ko, en) in enumerate(chapter_specs):
    seconds = 0 if i == 0 else math.floor(scenes[sid]['start'])
    chapters.append({'sceneId': sid, 'seconds': seconds, 'timestamp': f'{seconds//60:02d}:{seconds%60:02d}', 'ko': ko, 'en': en, 'exactSceneStart': scenes[sid]['start']})
assert all(b['seconds'] - a['seconds'] >= 10 for a, b in zip(chapters, chapters[1:]))
assert 1231.4 - chapters[-1]['seconds'] >= 10
write('chapters.json', {'source': timeline_path.relative_to(ROOT).as_posix(), 'sourceSha256': sha(timeline_path), 'durationSeconds': 1231.4, 'rounding': 'floor scene start to whole seconds; first chapter starts at branding 00:00', 'chapters': chapters})
for language in ['ko', 'en']:
    write('chapters.' + language + '.txt', '\n'.join(f"{c['timestamp']} {c[language]}" for c in chapters))

titles = [
    {'ko': 'AI 그림으로 진짜 게임 만들기 | 픽셀아트·애니메이션·웹게임 제작', 'en': 'Turning AI Art into a Playable Game | Pixel Art, Animation & Web Development', 'audience': 'AI 그림을 실제 게임 리소스로 활용하려는 입문 개발자', 'promise': '같은 캐릭터·방의 실제 제작 과정과 실행 가능한 결과', 'selected': True, 'reason': '썸네일의 AI 그림→실제 게임 약속과 일치하며, 도구·정리·동작·게임 연결을 모두 담는 본문 범위를 정확히 표현한다.'},
    {'ko': 'AI로 그렸는데 왜 게임에 못 쓸까? | 픽셀아트부터 움직이는 게임까지', 'en': 'Why AI Art Is Not Game-Ready Yet | From Pixel Art to a Playable Room', 'audience': '일관성·픽셀 크기·동작 연결 문제를 겪는 제작자', 'promise': '생성 이미지가 실제 게임에 들어가기까지 필요한 수정', 'selected': False},
    {'ko': 'AI 캐릭터를 직접 움직여봤습니다 | 2D 게임 리소스 제작 실전', 'en': 'Making an AI Character Playable | A Practical 2D Game-Asset Workflow', 'audience': 'AI 제작 사례와 작동 결과를 보고 싶은 게이머·개발자', 'promise': '실제 실행 결과 중심의 리소스 파이프라인', 'selected': False},
]
write('title-candidates.json', titles)
for language in ['ko', 'en']:
    assert len(titles[0][language]) <= 100
    write('title.' + language + '.txt', titles[0][language])

records_path = ROOT / 'sites/yamyam-cartographers-room/dist/tool-records.json'
records = read(records_path)
tool_rows = []
for item in records:
    tool_rows.append({k: item[k] for k in ['name', 'status', 'use', 'url']})
introduced = [
    {'name': 'NovelAI', 'url': 'https://docs.novelai.net/en/image/tutorial-charactercreation/', 'role': 'Character-design alternative introduced in narration; not used to create this room.'},
    {'name': 'kohya_ss', 'url': 'https://github.com/bmaltais/kohya_ss', 'role': 'LoRA-training alternative only; no character LoRA trained.'},
    {'name': 'OneTrainer', 'url': 'https://github.com/Nerogar/OneTrainer', 'role': 'LoRA-training alternative only; no character LoRA trained.'},
    {'name': 'Aseprite', 'url': 'https://www.aseprite.org/docs/sprite-sheet/', 'role': 'Retouching alternative introduced; not executed for this product.'},
    {'name': 'Pixel Snapper', 'url': 'https://www.spritefusion.com/pixel-snapper', 'role': 'Pixel-cleanup alternative introduced; not executed for this product.'},
]
write('tool-execution-matrix.json', {'recordedAt': NOW, 'primaryEvidence': records_path.relative_to(ROOT).as_posix(), 'primaryEvidenceSha256': sha(records_path), 'executedAndAttempted': tool_rows, 'introducedOnly': introduced, 'importantDistinctions': ['Seven of the eight featured OSS workflows produced actual outputs. Sprite-Sheet-Diffusion setup was audited but inference remained incomplete because the official multi-scale PoseGuider weights were missing from the checked release.', '2dimg2motion used its reference-image workflow and validator; Agent Sprite Forge used its local assembler, not an external video-generation API.', 'ComfyUI compared ILXL with and without an existing style LoRA; no new character LoRA training is claimed.', 'The current public site has later desk, radio UI and memo refinements. The approved video retains its room-v3 production capture.', 'The twenty HoliznaCC0 tracks are bundled in the web-game radio, not a claim that all twenty are heard in this video.']})

source_ko = '''자료·도구 출처
실제 실행한 도구
2dimg2motion — 지도 읽기 14프레임·검증
https://github.com/WU-HAOTIAN34/2dimg2motion
sprite-gen — 시트 분할·투명도·기준점 정리
https://github.com/aldegad/sprite-gen
pixelfx — 불꽃·비·눈 효과
https://github.com/patch-gg/pixelfx
PixelOE — 배경·캐릭터 픽셀 규격 정리
https://github.com/KohakuBlueleaf/PixelOE
Agent Sprite Forge — 기존 프레임 조립(외부 영상 생성 API 미사용)
https://github.com/0x0funky/agent-sprite-forge
Codixel — 책 읽기·깃털펜 관절 동작
https://github.com/mankidev/codixel
Pixelbolt — 정령·펼친 장부 레시피
https://github.com/skulitom/Pixelbolt
ChatGPT 이미지 생성 — 같은 참조로 캐릭터·방·동작 원화 제작
https://chatgpt.com/
ComfyUI — ILXL와 기존 스타일 LoRA 비교 실행
https://github.com/Comfy-Org/ComfyUI
Illustrious XL v0.1
https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
PixelArt SakuLike ILXL
https://civitai.com/models/1788100/pixelart-sakulikeilxl

실제 설치·재현 시도: Sprite-Sheet-Diffusion
확인 시점의 공식 공개 파일에 필수 PoseGuider 가중치가 없어 추론 미완료. 게임에 이 모델의 생성 프레임은 사용하지 않았습니다.
https://github.com/chenganhsieh/Sprite-Sheet-Diffusion
https://github.com/chenganhsieh/Sprite-Sheet-Diffusion/issues/3

소개한 대안(이번 제품 제작에는 미사용)
NovelAI: https://docs.novelai.net/en/image/tutorial-charactercreation/
kohya_ss: https://github.com/bmaltais/kohya_ss
OneTrainer: https://github.com/Nerogar/OneTrainer
Aseprite: https://www.aseprite.org/docs/sprite-sheet/
Pixel Snapper: https://www.spritefusion.com/pixel-snapper
새 캐릭터 전용 LoRA 학습은 진행하지 않았습니다.

기술·제작 과정 참고
https://docs.comfy.org/tutorials/basic/lora
https://github.com/microsoft/LoRA
https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=214752

실습 캐릭터·방·시트는 이번 제작의 이미지 생성 및 직접 편집 결과이며, 게임·도구 화면은 자체 실행 캡처입니다. pixelfx의 제3자 고지는 배포 소스·라이선스 기록에 보존했습니다.
웹 게임 라디오 음악: HoliznaCC0 — Lo-Fi and Chill Collection (CC0)
https://opengameart.org/content/lo-fi-and-chill-collection
https://creativecommons.org/publicdomain/zero/1.0/'''
source_en = '''Sources and tools
Actually used
2dimg2motion — 14-frame map loop and validation
https://github.com/WU-HAOTIAN34/2dimg2motion
sprite-gen — slicing, alpha cleanup and registration
https://github.com/aldegad/sprite-gen
pixelfx — fire, rain and snow
https://github.com/patch-gg/pixelfx
PixelOE — background and character pixel cleanup
https://github.com/KohakuBlueleaf/PixelOE
Agent Sprite Forge — local frame assembly; no external video-generation API
https://github.com/0x0funky/agent-sprite-forge
Codixel — reading and quill-writing rigs
https://github.com/mankidev/codixel
Pixelbolt — spirit and open-ledger recipes
https://github.com/skulitom/Pixelbolt
ChatGPT image generation — reference-based character, room and pose art
https://chatgpt.com/
ComfyUI — ILXL and existing style-LoRA comparison
https://github.com/Comfy-Org/ComfyUI
Illustrious XL v0.1
https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
PixelArt SakuLike ILXL
https://civitai.com/models/1788100/pixelart-sakulikeilxl

Setup attempted: Sprite-Sheet-Diffusion
Inference was not completed: required PoseGuider weights were missing from the official files checked. No frames from this model are used in the game.
https://github.com/chenganhsieh/Sprite-Sheet-Diffusion
https://github.com/chenganhsieh/Sprite-Sheet-Diffusion/issues/3

Introduced alternatives, not used for this product
NovelAI: https://docs.novelai.net/en/image/tutorial-charactercreation/
kohya_ss: https://github.com/bmaltais/kohya_ss
OneTrainer: https://github.com/Nerogar/OneTrainer
Aseprite: https://www.aseprite.org/docs/sprite-sheet/
Pixel Snapper: https://www.spritefusion.com/pixel-snapper
No new character LoRA was trained.

Technical and process references
https://docs.comfy.org/tutorials/basic/lora
https://github.com/microsoft/LoRA
https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=214752

Character, room and sheets: generated and edited for this production. Game and tool footage: our own execution captures. pixelfx third-party notices are retained in the distributed source/license records.
Web-game radio: HoliznaCC0 — Lo-Fi and Chill Collection (CC0)
https://opengameart.org/content/lo-fi-and-chill-collection
https://creativecommons.org/publicdomain/zero/1.0/'''
channel_ko = f'''🎮 게임 개발은 '따라 치기'가 아니라 직접 만드는 실력입니다.
얌얌코딩은 DirectX, Unity, Unreal, Computer Graphics를 기반으로 실무에서 통하는 개발 역량을 기르는 게임 프로그래밍 채널입니다.

🚀 프리미엄 1:1 코칭
실무 과제 중심으로 직접 설계하고 구현하는 개발 습관을 만들어드립니다.
DirectX11/12 · Unity/Unreal · Computer Graphics & PBR · Shader/Rendering · 게임 엔진 개발 · 최신 Graphics 논문 리뷰 및 구현
{COACH}

💬 얌얌코딩 커뮤니티
질문, 코드 리뷰, 피드백, 수업 자료를 함께 공유합니다.
Discord: {DISCORD}
YouTube 멤버십: {MEMBERSHIP}'''
channel_en = f'''Yamyam Coding teaches game programming through DirectX, Unity, Unreal and computer graphics, with a focus on designing and building things yourself.

1:1 programming coaching
DirectX11/12, Unity/Unreal, graphics and PBR, shaders, rendering, engine development, and research-paper implementation.
{COACH}
Discord: {DISCORD}
Membership: {MEMBERSHIP}'''
intro_ko = f'''AI 그림 한 장을 실제로 클릭하며 노는 작은 게임으로 만들었습니다. 같은 캐릭터와 작업실을 유지하며, 픽셀 정리부터 걷기·앉기·지도 읽기·깃털펜 필기까지 실제 요청문과 설정, 수정 과정을 보여드립니다.

▶ 직접 플레이 / 설치·로그인 없이 실행
{PLAY}
의자 앉기 · 지도 읽기 · 책 꺼내 읽기 · 창밖 보기 · 필기, 날씨 4종과 CC0 로파이 20곡 라디오를 체험할 수 있습니다. 공개 웹 버전에는 영상 제작 후 개선한 책상·라디오 UI·메모 기능도 반영했습니다.

7개 오픈소스 도구의 실제 결과와 ComfyUI 실습을 담았습니다. 8번째 도구의 재현 실패도 구분해 기록했습니다. 각 도구의 역할·링크·실행 범위는 설명 맨 아래에서 확인하세요.'''
intro_en = f'''We turn AI-assisted art into a small playable room, keeping the same character and setting throughout. Follow the actual prompts, settings and fixes for pixel cleanup, walking, sitting, map reading and writing with a quill.

Play in your browser — no installation or login:
{PLAY}
Try five actions, four weather states and a twenty-track CC0 lo-fi radio. The live site also includes later desk, radio-UI and memo improvements.

Seven featured open-source workflows produced outputs, alongside a ComfyUI comparison. The eighth tool's incomplete reproduction is reported separately. Tool roles, links and execution limits are at the bottom.'''
for lang, intro, channel, sources in [('ko', intro_ko, channel_ko, source_ko), ('en', intro_en, channel_en, source_en)]:
    chapter_text = (OUT / f'chapters.{lang}.txt').read_text(encoding='utf-8').rstrip()
    description = '\n\n'.join([intro, ('챕터' if lang == 'ko' else 'Chapters') + '\n' + chapter_text, channel, sources])
    assert len(description) <= 5000, (lang, len(description))
    write(f'description.{lang}.txt', description)
write('source-credits.json', {'sourceCredits': {'ko': source_ko, 'en': source_en}, 'mustBeLastBlock': True, 'claimsUseInternalExecutionRecordsNotRepositoryMarketing': True})

tags = ['AI 게임 만들기', 'AI 게임 개발', '픽셀아트', '2D 게임', '게임 리소스', '게임 애니메이션', 'ComfyUI', 'LoRA', 'PixelOE', 'sprite-gen', '2dimg2motion', 'pixelfx', 'Agent Sprite Forge', 'Codixel', 'Pixelbolt', 'Sprite-Sheet-Diffusion', 'AI pixel art', 'game assets', 'web game', '얌얌코딩']
write('tags.json', tags)
write('tags.txt', ', '.join(tags))
assert len(','.join(tags)) < 450
write('pinned-comment.ko.txt', f'영상 속 작업실을 직접 플레이해 보세요!\n{PLAY}\n어떤 동작이나 도구가 가장 도움이 됐는지 댓글로 알려주세요.\n\n프로그래밍 코칭: {COACH}')
write('pinned-comment.en.txt', f'Play the workshop from the video:\n{PLAY}\nWhich animation or tool helped you most?\n\nProgramming coaching: {COACH}')

user_quote = '2d 픽셀 게임만들기 영상도 이제 완성된거같으니 병렬로 영상 완성시키고 업로드해줘 유튜브에\n\n설명란에 사용된 도구들 잘 넣어주고\n\n웹빌드해서 접속간능한 링크도 넣어서 적어주고 마무리 지어줘~'
project = read(PROJECT / 'project.json')
worklist = read(ROOT / 'shared/publishing/video-worklist.json')
row = next(r for values in worklist.values() if isinstance(values, list) for r in values if isinstance(r, dict) and r.get('id') == 'S-AI2D')
platform_receipt_path = OUT / 'youtube-upload.json'
platform_receipt = read(platform_receipt_path) if platform_receipt_path.exists() else {}
write('local-duplicate-check.json', {'checkedAt': NOW, 'scope': 'Read-only local records; direct YouTube Studio verification belongs to root.', 'sources': ['projects/ai-2d-game-assets/project.json', 'projects/ai-2d-game-assets/production/room-v3/delivery.json', 'shared/publishing/video-worklist.json#S-AI2D', 'projects/ai-2d-game-assets/publishing/room-v3-upload-20261108'], 'worklistVideoId': row.get('videoId'), 'worklistUrl': row.get('url'), 'preUploadLocalRecordCheck': 'No video ID was recorded when preparation began.', 'rootPlatformReceiptLocated': bool(platform_receipt), 'currentVideoId': platform_receipt.get('videoId'), 'currentReceipt': 'youtube-upload.json' if platform_receipt else None, 'studioVerifiedByThisAgent': False, 'action': 'Continue metadata on the root-owned recorded ID; do not upload a second copy.' if platform_receipt else 'Root must search Studio before a first upload.'})
write('metadata-patch-spec.json', {'applyBy': 'root only after reconciling current platform receipt', 'project': 'projects/ai-2d-game-assets/project.json', 'preserveAllOtherKeys': True, 'changes': [
    {'path': 'video.durationSeconds', 'previous': project['video']['durationSeconds'], 'value': 1231.4, 'reason': 'Actual approved master probe; old baseline duration is stale.'},
    *[{'path': 'paths.' + key, 'previous': project.get('paths', {}).get(key), 'value': str(MEDIA / filename).replace('\\', '/'), 'reason': 'Match approved room-v3 deliverable; existing delivery object already points to it.'} for key, filename in [('videoBurnedCaptions', 'ai-2d-game-assets.captioned.mp4'), ('videoClean', 'ai-2d-game-assets.clean.mp4'), ('captionsKo', 'ai-2d-game-assets.ko.srt'), ('captionsEn', 'ai-2d-game-assets.en.srt')]]], 'sharedControlAndWorklist': 'Root owns latest upload authorization, human evidence, platform status and selective Git; this script does not edit them.'})
packet = {
    'preparedAt': NOW, 'status': 'metadata-ready-root-platform-work-separate', 'projectSlug': 'ai-2d-game-assets',
    'platformReceipt': 'youtube-upload.json' if platform_receipt else None, 'existingVideoId': platform_receipt.get('videoId'),
    'authorizationRecord': (OUT / 'authorization.json').relative_to(ROOT).as_posix(), 'userRequestVerbatim': user_quote,
    'userReviewEvidence': 'User accepted the currently delivered 9286 room-v3 video for upload. Full human watch/listening is not claimed.',
    'newRender': False, 'privacy': 'private', 'schedule': None, 'publicPublicationAuthorized': False, 'deletionAuthorized': False,
    'reviewUrl': 'http://127.0.0.1:9286/', 'playableUrl': PLAY, 'files': files, 'uploadFile': files[0],
    'mediaProbe': probe, 'durationSeconds': 1231.4, 'selectedTitle': {'ko': titles[0]['ko'], 'en': titles[0]['en']},
    'descriptions': {'ko': 'description.ko.txt', 'en': 'description.en.txt'}, 'sourceCredits': 'source-credits.json',
    'captions': [{'language': 'ko', 'kind': 'manual', 'path': str(MEDIA / 'ai-2d-game-assets.ko.srt')}, {'language': 'en', 'kind': 'manual', 'path': str(MEDIA / 'ai-2d-game-assets.en.srt')}],
    'thumbnail': {'path': (OUT / 'thumbnail-v1.png').as_posix(), 'sha256': sha(OUT / 'thumbnail-v1.png'), 'qa': 'thumbnail-v1.qa.json'},
    'tagsFile': 'tags.json', 'chaptersFile': 'chapters.json', 'videoLanguage': 'ko', 'titleDescriptionLanguage': 'ko',
    'categorySuggestion': 'Education', 'playlist': 'Root verify current channel inventory; select AI game-development or appropriate tech playlist, not animation series by default.',
    'pinnedComment': {'ko': 'pinned-comment.ko.txt', 'en': 'pinned-comment.en.txt', 'state': 'prepared; private-video posting waits for supported publication state'},
    'card': {'timeSeconds': 0, 'type': 'external-link', 'url': COACH, 'teaser': '프로그래밍과외', 'message': '프로그래밍과외', 'state': 'prepared-not-applied'},
    'endScreen': {'startSeconds': 1221.4, 'endSeconds': 1231.4, 'elements': ['existing appropriate playlist', 'own-channel subscription', COACH], 'state': 'prepared-not-applied'},
    'advertiserAssessment': 'User submits personally; do not infer submission from upload.',
    'platformChecks': ['Studio duplicate search', 'exact file selected', 'private save', 'KO/EN manual subtitles', 'KO/EN localized title and description', 'thumbnail and tags', 'playlist', 'coaching card and end screen', '1080p60 processing and source hash record', 'advertiser status', 'no schedule or public publication'],
    'technicalQaScope': 'Existing final-review.json plus current four-file hash and ffprobe verification; no new render, full decode, ASR or human listening performed.',
    'descriptionCharacters': {lang: len((OUT / f'description.{lang}.txt').read_text(encoding='utf-8').rstrip()) for lang in ['ko', 'en']},
}
write('upload-packet.json', packet)
write('README.md', f'''# AI 2D room-v3 upload packet

Prepared for root's YouTube workflow. No upload, render, shared metadata mutation or Git action was performed by this helper.

- Approved captioned master: `{files[0]['path']}`
- SHA256: `{files[0]['sha256']}`
- Verified media: 1920×1080, 60fps, 1231.4 seconds (20:31.4).
- Use `title.ko.txt`, `description.ko.txt`, `tags.json`, `thumbnail-v1.png`, then English localization and both manual SRT files from `upload-packet.json`.
- Description chapter times derive from the actual final timeline. Sources and credits occupy the final block; the playable link is near the beginning.
- Seven featured OSS workflows produced results. Sprite-Sheet-Diffusion was attempted but did not produce inference output. Introduced-only alternatives and new-character-LoRA non-execution are stated explicitly.
- Public game: {PLAY}
- Private upload only. No scheduling, deletion or public publication is authorized by this packet. The user submits advertiser self-certification.
- `metadata-patch-spec.json` proposes only stale duration/path corrections for root. Existing control/worklist and unrelated bytes remain untouched.
- `authorization.json` and thumbnail files are root-owned and were only read.

The user's exact latest request is recorded in `upload-packet.json`. Acceptance for upload does not imply full human watch/listening.
''')
print(json.dumps({'packet': str(OUT / 'upload-packet.json'), 'filesVerified': len(files), 'chapters': len(chapters), 'descriptions': packet['descriptionCharacters'], 'title': titles[0]['ko']}, ensure_ascii=False))
