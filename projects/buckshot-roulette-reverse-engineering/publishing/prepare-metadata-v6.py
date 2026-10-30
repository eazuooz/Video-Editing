"""Prepare local v6 YouTube metadata; never performs a platform operation."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
SLUG = "buckshot-roulette-reverse-engineering"
P = ROOT / "projects" / SLUG
PUB = P / "publishing"
OUT = ROOT / "output" / SLUG
TITLE_KO = "AI에게 기존 프로그램을 분석시키면 어디까지 만들 수 있을까?｜REA"
TITLE_EN = "What Can AI Build by Analyzing Existing Software? | REA"
MASTER_SHA = "2dbf6b3dae05f43fff9c8a33e35498abeea9981e374d4f968c0a5e4fdf6ec77b"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


timeline = json.loads((P / "production/timeline-v6.json").read_text("utf-8"))
frames = {"opening": 0}
cursor = 120
for beat in timeline["beats"]:
    frames[beat["id"]] = cursor
    cursor += beat["frames"]
assert cursor + 600 == 26518
chapter_defs = [
    ("opening", "벅샷 룰렛 실제 플레이 · 2배속", "Buckshot Roulette gameplay at 2x speed"),
    ("v4-01-01", "분석에서 플레이 가능한 프로토타입까지", "From analysis to a playable prototype"),
    ("v4-02-01", "REA와 AI 에이전트는 무엇을 할까?", "What do REA and an AI agent do?"),
    ("v4-02-02", "MCP와 분석·제작 도구 연결", "MCP and the analysis-to-development workflow"),
    ("b04-02-p01", "실제 파일을 열어 규칙 찾기", "Inspecting real files and tracing the rules"),
    ("b06-03-p01", "탄환 순서와 아이템의 동작", "The ammunition queue and item behavior"),
    ("b10-04-p01", "차례·수갑·피해량을 상태로 나누기", "Turns, handcuffs and damage as state changes"),
    ("b19-05-p01", "딜러의 판단 구조", "How the dealer makes decisions"),
    ("b23-06-p01", "새 코드로 구현하고 검사하기", "Implementing and testing new code"),
    ("b25-07-p01", "Blender 모델을 Godot에 연결하기", "Bringing original Blender models into Godot"),
    ("v4-08-01", "분석을 내 아이디어의 출발점으로", "Using analysis to test your own ideas"),
]
chapters = []
for key, ko, en in chapter_defs:
    frame = frames[key]
    sec = frame // 60
    chapters.append({"beatId": key, "frame": frame, "exactSeconds": frame / 60,
                     "time": f"{sec // 60:02d}:{sec % 60:02d}", "ko": ko, "en": en})
assert all(b["exactSeconds"] - a["exactSeconds"] >= 10 for a, b in zip(chapters, chapters[1:]))

intro_ko = """AI가 기존 프로그램을 분석하면, 새로운 결과물을 어디까지 만들 수 있을까요?
REA(Reverse Engineer Anything)로 벅샷 룰렛의 파일 구조와 규칙을 조사하고, 새 코드와 3D 모델로 플레이 가능한 프로토타입을 만드는 과정을 보여드립니다.

탄환 순서, 차례 전환, 아이템 효과, 딜러의 판단을 하나씩 확인한 뒤 직접 구현한 결과와 비교합니다. 실제로 사용한 제작 경로는 REA CLI → 규칙 분석과 새 코드 작성 → Blender 모델 제작 → Godot 프로토타입입니다. 도구 연결과 개발 환경은 Unity 애니메이션으로 풀어 설명합니다.

이번 대상에는 읽을 수 있는 GDScript가 포함되어 있었습니다. Ghidra와 Tripo MCP는 가능한 도구 연결로 소개하며, 이번 프로토타입 제작에는 사용하지 않았습니다.

#AI개발 #리버스엔지니어링 #REA

챕터"""
intro_en = """What can AI build by analyzing an existing program?
We use REA (Reverse Engineer Anything) to inspect Buckshot Roulette's file structure and rules, then build a playable prototype with new code and original 3D models.

Follow the ammunition queue, turn changes, item effects and dealer decisions, then compare them with our implementation. The actual workflow is REA CLI → rule analysis and new code → Blender models → a Godot prototype. Unity animations explain the tools and development environment.

This particular game package contained readable GDScript. Ghidra and Tripo MCP are introduced as possible tool connections; they were not used to build this prototype.

#AIDevelopment #ReverseEngineering #REA

Chapters"""

credits_ko = """실제 게임·게임 음악: Buckshot Roulette — Mike Klubnika / CRITICAL REFLEX. 설치된 Steam 버전을 직접 녹화했습니다.
https://store.steampowered.com/app/2835570/Buckshot_Roulette/
원작 OST 제작: Mike Klubnika. 개발자 답변: https://steamcommunity.com/app/2835570/discussions/0/4364626769116524112/

실제로 사용한 분석·제작 도구
REA 6.8.0 CLI — morluto: https://github.com/morluto/rea
REA의 Godot PCK 분석 문서: https://github.com/morluto/rea/blob/main/docs/godot-pck.md
Blender 5.2.3 LTS — 독자적인 모델·재질 제작: https://www.blender.org/
Godot 4.7.2 — 실제 프로토타입: https://godotengine.org/
Unity — 설명용 애니메이션: https://unity.com/
OBS Studio — 직접 플레이 녹화: https://obsproject.com/
Qwen3-TTS — 내레이션: https://github.com/QwenLM/Qwen3-TTS
FFmpeg — 영상·오디오 편집: https://ffmpeg.org/
프로토타입의 코드·모델·재질은 이번 실험을 위해 직접 작성·제작했습니다.

도구 개념을 설명할 때 참고한 공식 자료
MCP: https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro
Ghidra: https://github.com/NationalSecurityAgency/ghidra
Tripo MCP: https://github.com/Tripo-Developer/tripo-mcp
제작 흐름 참고 — Stefan 3D AI, I Reverse Engineered Mario 64 to Make My Own Game: https://www.youtube.com/watch?v=6MpHBHw30OE

Music: Nimbus — Eveningland (YouTube Audio Library)
https://www.youtube.com/watch?v=ZOc84gXN-lg"""
credits_en = """Recorded game and in-game music: Buckshot Roulette — Mike Klubnika / CRITICAL REFLEX. We recorded our installed Steam copy.
https://store.steampowered.com/app/2835570/Buckshot_Roulette/
Original soundtrack by Mike Klubnika. Developer reply: https://steamcommunity.com/app/2835570/discussions/0/4364626769116524112/

Tools actually used
REA 6.8.0 CLI — morluto: https://github.com/morluto/rea
Godot PCK documentation: https://github.com/morluto/rea/blob/main/docs/godot-pck.md
Blender 5.2.3 LTS — original models/materials: https://www.blender.org/
Godot 4.7.2 — playable prototype: https://godotengine.org/
Unity — explanatory animations: https://unity.com/
OBS Studio — original gameplay capture: https://obsproject.com/
Qwen3-TTS — narration: https://github.com/QwenLM/Qwen3-TTS
FFmpeg — video/audio editing: https://ffmpeg.org/
The prototype code, models and materials were independently created for this experiment.

Official references for the tool overview
MCP: https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro
Ghidra: https://github.com/NationalSecurityAgency/ghidra
Tripo MCP: https://github.com/Tripo-Developer/tripo-mcp
Workflow reference — Stefan 3D AI, I Reverse Engineered Mario 64 to Make My Own Game: https://www.youtube.com/watch?v=6MpHBHw30OE

Music: Nimbus — Eveningland (YouTube Audio Library)
https://www.youtube.com/watch?v=ZOc84gXN-lg"""

body = {lang: intro + "\n" + "\n".join(c["time"] + " " + c[lang] for c in chapters)
        for lang, intro in [("ko", intro_ko), ("en", intro_en)]}
video = OUT / f"{SLUG}.captioned.mp4"
assert sha(video) == MASTER_SHA
subtitles = []
for language in ["ko", "en"]:
    file = OUT / f"{SLUG}.{language}.srt"
    subtitles.append({"language": language, "path": file.relative_to(ROOT).as_posix(),
                      "sha256": sha(file), "cues": len(file.read_text("utf-8").strip().split("\n\n")),
                      "status": "prepared-not-published", "method": "manual-file-upload-with-timing"})

receipt = {
    "schemaVersion": 1, "slug": SLUG, "status": "local-package-prepared-platform-pending",
    "preparedAt": datetime.now(timezone.utc).isoformat(),
    "video": {"name": video.name, "path": video.relative_to(ROOT).as_posix(),
              "sha256": MASTER_SHA, "bytes": video.stat().st_size,
              "seconds": 26518 / 60, "frames": 26518, "width": 1920, "height": 1080, "fps": 60},
    "qa": f"projects/{SLUG}/production/final-review-v6.json",
    "metadata": {"title": TITLE_KO, "description": body["ko"], "privacyStatus": "private",
                 "category": "Education", "language": "ko", "madeForKids": False,
                 "tags": ["AI 개발", "REA", "Reverse Engineer Anything", "리버스 엔지니어링", "AI 에이전트", "프로토타입", "벅샷 룰렛", "Buckshot Roulette", "Godot", "MCP"]},
    "englishMetadata": {"title": TITLE_EN, "description": body["en"], "language": "en", "status": "prepared-not-saved"},
    "descriptionBody": body, "sourceCredits": {"ko": credits_ko, "en": credits_en},
    "chapters": chapters,
    "chapterEvidence": {"timeline": f"projects/{SLUG}/production/timeline-v6.json",
                        "method": "Sequential beat frames after the verified 120-frame branding. Public timestamps floor exact frame starts to whole seconds. Opening includes 2-second branding and the requested 30-second gameplay sequence.",
                        "endingStartFrame": cursor, "endingStartSeconds": cursor / 60},
    "subtitles": subtitles,
    "thumbnail": {"status": "not-yet-prepared", "savedVerified": False},
    "actualVideoId": None, "scheduled": False, "privateUploadSaved": False, "fullSettingsVerified": False,
    "automaticChecks": {"status": "not-yet-observed"},
    "rightsEvidence": [f"projects/{SLUG}/planning/primary-sources.json", f"projects/{SLUG}/prototype/assets/provenance.json", "shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md"],
    "preparationEvidence": {"script": f"projects/{SLUG}/script/revision-v4/narration.ko.json",
                            "toolFacts": f"projects/{SLUG}/planning/rea-explainer-v4.json",
                            "titleChosenByUser": True, "titleUserEvidence": TITLE_KO + " 이걸로 업로드해줘~",
                            "platformActionPerformedByPreparer": False,
                            "thumbnailNeeded": True},
}
receipt_file = PUB / "youtube-upload.json"
if receipt_file.exists():
    raise SystemExit("Existing receipt preserved. Edit the current record instead of reinitializing it.")
PUB.mkdir(parents=True, exist_ok=True)
receipt_file.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", "utf-8")
(PUB / "title.ko.txt").write_text(TITLE_KO + "\n", "utf-8")
(PUB / "title.en.txt").write_text(TITLE_EN + "\n", "utf-8")
(PUB / "pinned-comment.ko.txt").write_text("기존 프로그램을 분석해 새 아이디어를 시험한다면, 어떤 기능부터 만들어 보고 싶으신가요?\n\n직접 만든 코드와 프로젝트를 바탕으로 피드백을 받고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해 주세요.\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\n", "utf-8")
print(json.dumps({"prepared": str(receipt_file), "sha256": MASTER_SHA,
                  "chapters": len(chapters), "subtitles": subtitles}, ensure_ascii=False))
