"""Build a local, evidence-backed progress page. No production state is changed."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
OUTPUT = ROOT / "output" / PROJECT.name
LOCAL = PROJECT / "production" / "local"
EVIDENCE_PAGE = LOCAL / "analysis" / "evidence-view.html"
FINAL_OUTPUT = ROOT / "output" / "buckshot-roulette-reverse-engineering-v4"
# assemble_documentary.py writes this receipt only after both masters decode.
FINAL_QA = LOCAL / "documentary-v4" / "technical-qa.json"
FINAL_AUDIO_QA = LOCAL / "final-qa-v4" / "audio-review.json"
LISTENING_PAGE = LOCAL / "audio-v4" / "review" / "listening" / "index.html"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def url(path: Path, base: Path) -> str:
    return quote(os.path.relpath(path, base).replace("\\", "/"), safe="/:-._")


def link(path: Path, label: str, base: Path, css: str = "") -> str:
    if not path.exists():
        return ""
    return f'<a class="{esc(css)}" href="{url(path, base)}">{esc(label)}</a>'


def integrity_matches(report: dict) -> bool:
    files = report.get("files", {})
    if not files:
        return False
    for name, record in files.items():
        expected = record.get("sha256") if isinstance(record, dict) else record
        path = PROJECT / name.replace("\\", "/")
        if not expected or not path.is_file():
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            return False
    return True


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def final_review_state(directory: Path = FINAL_OUTPUT, report_path: Path = FINAL_QA) -> dict:
    """Fail closed while rendering, or when a receipt belongs to older files."""
    stem = PROJECT.name
    files = {kind: directory / f"{stem}.{suffix}" for kind, suffix in {
        "clean": "clean.mp4", "captioned": "captioned.mp4",
        "ko": "ko.srt", "en": "en.srt",
    }.items()}
    state = {"ready": False, "files": files, "report": report_path, "reason": "four-outputs-or-report-pending"}
    if not report_path.is_file() or not all(path.is_file() and path.stat().st_size > 0 for path in files.values()):
        return state
    try:
        report = read_json(report_path)
        if report.get("technicalDecodePassed") is not True or report.get("pairedAudioIdentical") is not True or not report.get("checkedAt"):
            state["reason"] = "technical-check-not-passed"
            return state
        recorded = report.get("outputs", {})
        for kind in ("clean", "captioned"):
            item = recorded.get(kind, {})
            if not item.get("file") or Path(item["file"]).resolve() != files[kind].resolve():
                state["reason"] = "receipt-file-mismatch"
                return state
            if not item.get("sha256") or file_digest(files[kind]) != item["sha256"]:
                state["reason"] = "receipt-hash-mismatch"
                return state
            video = next((s for s in item.get("probe", {}).get("streams", []) if s.get("codec_type") == "video"), {})
            if video.get("width") != 1920 or video.get("height") != 1080 or video.get("avg_frame_rate") not in ("60/1", "120/2"):
                state["reason"] = "receipt-format-mismatch"
                return state
            audio = next((s for s in item.get("probe", {}).get("streams", []) if s.get("codec_type") == "audio"), {})
            video_duration = float(video.get("duration", 0))
            audio_duration = float(audio.get("duration", 0))
            container_duration = float(item.get("probe", {}).get("format", {}).get("duration", 0))
            if video_duration <= 0 or audio_duration <= 0 or abs(video_duration - audio_duration) > 0.08 or abs(video_duration - container_duration) > 0.08:
                state["reason"] = "receipt-audio-video-duration-mismatch"
                return state
        clean_audio = recorded["clean"].get("decodedAudioHash")
        if not clean_audio or clean_audio != recorded["captioned"].get("decodedAudioHash"):
            state["reason"] = "receipt-audio-mismatch"
            return state
        audio_review = read_json(FINAL_AUDIO_QA)
        if audio_review.get("technicalPassed") is not True or audio_review.get("wholeMixAsrCompared") is not True:
            state["reason"] = "current-encoded-audio-review-not-passed"
            return state
        if audio_review.get("masterSha256") != recorded["captioned"]["sha256"]:
            state["reason"] = "encoded-audio-review-master-mismatch"
            return state
        for kind in ("ko", "en"):
            text = files[kind].read_text(encoding="utf-8-sig")
            if not re.search(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", text):
                state["reason"] = "subtitle-format-missing"
                return state
        state.update(ready=True, reason="current-masters-match-technical-receipt", checkedAt=report["checkedAt"],
                     captionedSha256=recorded["captioned"]["sha256"],
                     durationSeconds=float(recorded["captioned"].get("probe", {}).get("format", {}).get("duration", 0)),
                     remaining=report.get("remaining", []))
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        state["reason"] = "receipt-not-readable-or-incomplete"
    return state


def final_review_html(state: dict) -> str:
    if not state["ready"]:
        return ""
    files = state["files"]
    downloads = "".join(link(files[key], label, OUTPUT, "button") for key, label in (
        ("captioned", "전체 자막 영상"), ("clean", "자막 없는 영상"),
        ("ko", "한국어 자막"), ("en", "영어 자막")))
    support = "".join(link(path, label, OUTPUT) for path, label in (
        (PROJECT / "production/launch-prototype.ps1", "프로토타입 실행 스크립트"),
        (PROJECT / "prototype/project.godot", "Godot 프로젝트"),
        (PROJECT / "planning/mechanics-findings.json", "규칙 분석 근거"),
        (PROJECT / "planning/original-footage-audit.json", "원작 촬영 검수 근거"),
        (state["report"], "현재 파일의 기술 검사 결과"),
        (FINAL_AUDIO_QA, "현재 영상의 음성 검사 결과")))
    audition = (f'<p class="subtle">새 도입·REA 설명과 기존 발음 확인 후보를 문맥과 함께 들을 수 있습니다. '
                f'{link(LISTENING_PAGE, "문단별 청취 클립 열기", OUTPUT)}</p>') if LISTENING_PAGE.exists() else ""
    total = round(state["durationSeconds"])
    duration = f' · {total // 60}분 {total % 60:02d}초' if total else ""
    return f'''<section class="section" id="final-review"><h2>완성본 검수</h2>
<p>1920×1080 · 60fps{duration} · 두 영상의 전체 디코딩과 동일 음성 검사를 통과한 현재 파일입니다.</p>
<span class="status">렌더링·기술 검사 완료</span><span class="status pending">사용자 검수 대기</span>
<p class="subtle" style="margin-top:12px">기술 검사는 실제 시청·청취를 대신하지 않습니다. 표본 화면·자막 연결은 확인했으며, 전체 사용자 시청·청취와 최종 검수가 남아 있습니다.</p>
<video class="review-video" controls playsinline preload="metadata" aria-label="벅샷 룰렛 분석·독립 재구현 전체 자막 검수 영상" src="{url(files['captioned'], OUTPUT)}"></video>
<div class="links">{downloads}</div>{audition}<div class="links">{support}</div>
<p class="evidence" style="margin-top:14px">자막 영상 SHA256: {esc(state['captionedSha256'])}<br>기술 검사 기록: {esc(state['checkedAt'])}</p></section>'''


CSS = """
:root{color-scheme:dark;--bg:#090b0c;--panel:#121617;--ink:#f4f5f0;--muted:#aeb9b5;--gold:#f4cf77;--line:#303a38;--green:#a4e6c6;--red:#ffb4a9}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 'Malgun Gothic',system-ui,sans-serif}a{color:var(--gold);text-underline-offset:4px}a:hover{color:#fff}a:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:5px}main{max-width:1180px;margin:auto;padding:34px 32px 76px}.brand{font-size:14px;letter-spacing:.16em;color:var(--gold);font-weight:700}.eyebrow{color:var(--muted);font-size:14px;margin:25px 0 6px}h1{font-size:clamp(30px,4.1vw,52px);line-height:1.24;margin:0 0 20px;letter-spacing:-.04em}h2{font-size:26px;color:var(--gold);line-height:1.35;margin:0 0 16px}h3{font-size:18px;margin:0 0 8px}p{margin:0 0 16px}.lead{max-width:850px;font-size:19px;color:#d8dfdc}.status{display:inline-block;font-size:14px;padding:4px 11px;border:1px solid var(--line);color:var(--green);margin-right:8px}.pending{color:var(--gold)}.subtle{font-size:14px;color:var(--muted)}.hero{margin:30px 0 0;border:1px solid var(--line)}figure{margin:0}figure img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;background:#000}figcaption{padding:13px 17px;color:var(--muted);font-size:14px}.links{display:flex;gap:13px 24px;flex-wrap:wrap;margin:20px 0 0}.button{display:inline-block;border:1px solid var(--gold);padding:9px 15px;text-decoration:none}.metrics{display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid var(--line);margin:34px 0}.metric{padding:18px 16px;border-right:1px solid var(--line)}.metric:last-child{border-right:0}.metric strong{font-size:32px;line-height:1.3;color:var(--gold);display:block}.metric span{font-size:14px;color:var(--muted);display:block}.section{margin-top:46px}.tablewrap{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:15px}th,td{padding:14px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:13px;color:var(--muted);font-weight:400}td:first-child{white-space:nowrap}.good{color:var(--green)}.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}.two figure{border:1px solid var(--line)}details{border-top:1px solid var(--line);padding:16px 0}details:last-child{border-bottom:1px solid var(--line)}summary{cursor:pointer;font-weight:700;padding:2px 0}summary::marker{color:var(--gold)}details .body{padding:15px 0 0 22px}.evidence{font:13px/1.65 ui-monospace,Consolas,monospace;color:var(--muted);overflow-wrap:anywhere}.limits{border-left:2px solid var(--gold);padding:8px 14px;margin-top:14px;font-size:14px;color:var(--muted)}ul{padding-left:23px;margin:12px 0}li+li{margin-top:8px}.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:26px 0}.flow div{border-top:2px solid var(--gold);padding-top:12px}.flow b{display:block;color:var(--gold);font-size:14px}.flow span{display:block;margin-top:7px}.record{background:var(--panel);padding:20px;border-left:3px solid var(--gold);overflow-wrap:anywhere}.footer{border-top:1px solid var(--line);margin-top:45px;padding-top:20px;color:var(--muted);font-size:13px}.evidence-view main{max-width:1650px;padding:55px 65px}.evidence-view h1{font-size:48px}.evidence-view .metric strong{font-size:44px}.evidence-view .claim{font-size:25px;line-height:1.55;margin:22px 0}.evidence-view .metric{padding:20px}.evidence-view .record{font-size:18px}.evidence-view .metrics{margin:30px 0}
@media(max-width:700px){main{padding:25px 20px 52px}.lead{font-size:17px}.metrics{grid-template-columns:1fr 1fr}.metric:nth-child(2){border-right:0}.metric:nth-child(-n+2){border-bottom:1px solid var(--line)}.metric strong{font-size:27px}.two,.flow{grid-template-columns:1fr}.flow{gap:15px}.tablewrap table{min-width:590px}.section{margin-top:35px}.links{gap:12px}details .body{padding-left:0}.evidence-view main{padding:25px 20px}.evidence-view h1{font-size:30px}.evidence-view .claim{font-size:20px}.evidence-view .metric strong{font-size:30px}}
"""
CSS += "\n.review-video{display:block;width:100%;aspect-ratio:16/9;background:#000;border:1px solid var(--line);margin-top:20px}.review-video:focus-visible{outline:3px solid var(--gold);outline-offset:4px}#final-review .links{margin-bottom:18px}"


def shell(title: str, content: str, evidence: bool = False) -> str:
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body class="{'evidence-view' if evidence else ''}"><main>{content}</main></body></html>'''


def main() -> None:
    inventory = read_json(PROJECT / "planning/package-inventory.json")
    mechanics = read_json(PROJECT / "planning/mechanics-findings.json")
    tests = read_json(LOCAL / "test-evidence/rules-test-report.json")
    stage = read_json(LOCAL / "asset-evidence/stage-validation/stage-validation-report.json")
    final = final_review_state()
    final_section = final_review_html(final)
    original_audit = read_json(PROJECT / "planning/original-footage-audit.json")
    findings = mechanics.get("findings", [])
    test_hash_current = integrity_matches(tests)
    stage_hash_current = integrity_matches(stage)
    checks = tests.get("checks", 0)
    passed = bool(tests.get("passed")) and tests.get("exitCode") == 0 and not tests.get("failures")
    test_status = "통과 · 현재 코드 확인" if passed and test_hash_current else "통과 기록 · 수정 후 재검증 필요" if passed else "검증 대기"
    current = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")
    metadata = inventory.get("packMetadata", {})
    pack_engine = ".".join(str(metadata.get("engine_" + x, "?")) for x in ("major", "minor", "patch"))
    count = inventory.get("fileCount", 0)
    gd_count = inventory.get("scriptInventory", {}).get("gdCount", 0)
    stage_view = LOCAL / "asset-evidence/stage-validation/stage-view.png"
    beauty = LOCAL / "asset-evidence/neon-chamber-beauty.png"
    stage_live = LOCAL / "asset-evidence/stage-validation/stage-live-shot.png"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PAGE.parent.mkdir(parents=True, exist_ok=True)

    def metrics() -> str:
        return '<div class="metrics">' + ''.join(f'<div class="metric"><strong>{esc(value)}</strong><span>{esc(label)}</span></div>' for value, label in [(f'{count:,}', 'REA로 확인한 패키지 파일'), (gd_count, 'UTF-8 확인 GDScript 파일'), (len(findings), '정리한 규칙·조건'), (checks if passed else '대기', '독립 규칙 모델 검사 통과')]) + '</div>'

    figures = ''
    for path, title, caption in [(beauty, 'Blender에서 만든 새 외형', '우리 로봇·테이블·도구 모델의 실제 렌더. 원작 모델을 사용한 화면이 아닙니다.'), (stage_live, 'Godot에서 실행한 동작', '독립 제작 장면의 실탄 발사 동작 검증 프레임. 원작과의 실행 결과 대조는 별도 단계입니다.')]:
        if path.exists():
            figures += f'<figure><a href="{url(path, OUTPUT)}"><img src="{url(path, OUTPUT)}" alt="{esc(title)}" loading="lazy"></a><figcaption><strong>{esc(title)}</strong><br>{esc(caption)}</figcaption></figure>'

    labels = {'ammo-sequence': '탄환은 언제 결정될까?', 'ammo-shuffle': '진열과 장전 순서는 어떻게 다른가?', 'endless-generation': '무한 모드는 무엇을 새로 정할까?', 'self-blank-extra-turn': '공포탄인데 다음 차례가 다른 이유', 'damage-and-saw': '톱을 쓰면 무엇이 바뀔까?', 'beer': '배출은 사격과 무엇이 다를까?', 'magnifier': '관찰과 탄환 소모의 차이', 'cuffs': '수갑은 어느 차례를 건너뛸까?', 'dealer-target-choice': '딜러는 누구를 겨눌까?', 'dealer-inference-and-items': '딜러는 정보와 아이템을 어떻게 쓸까?'}
    limits_ko = {
        'Animation event wiring that invokes ejection is not decoded yet; actual timing must be checked in recorded play.': '배출 함수를 호출하는 애니메이션 연결과 실제 처리 시점은 녹화 플레이로 확인해야 합니다.',
        'Story-mode exact per-round counts and exported shuffle booleans live in scene/resource data and are not established by these script defaults alone.': '스토리 모드의 라운드별 수량과 섞기 설정은 씬·리소스에 있습니다. 스크립트 기본값만으로 확정하지 않았습니다.',
        'Two shuffle calls are an implementation fact, not a claim of doubled randomness.': '섞기 함수를 두 번 부른다는 사실이 무작위성이 두 배가 된다는 뜻은 아닙니다.',
        'Do not infer an unconditional saw reset on every item action; beer does not directly call EndTurn in the observed item branch.': '모든 아이템 사용 뒤 톱 효과가 초기화되는 것은 아닙니다. 확인한 맥주 처리 부분은 EndTurn을 직접 호출하지 않습니다.',
        'Verify last-shell/special death handling in runtime before broader claim.': '마지막 탄환과 특수 사망 처리는 실제 실행 대조가 남아 있습니다.',
        'Beer animation-to-function method tracks have not been decoded; runtime footage should confirm binding.': '맥주 애니메이션과 배출 함수의 연결은 실제 실행 화면으로 확인해야 합니다.',
        'SetupShell connection to the magnifier animation is a scene wiring detail still awaiting runtime confirmation.': 'SetupShell 함수가 돋보기 애니메이션에 연결되는 부분은 실행 확인이 남아 있습니다.',
        'This is static branch analysis, not proof of optimality or all reachable states.': '조건 분기를 읽은 결과이며, 모든 상황에서 최선의 선택을 한다는 증명은 아닙니다.',
        'Dealer does have direct state access in code; player-facing fairness must be described using actual decision conditions rather than claiming it never reads hidden state.': '코드에서 딜러는 상태 값에 접근합니다. 숨은 정보를 전혀 읽지 않는다고 단정하지 않고, 실제 선택에 사용하는 조건으로 설명합니다.'
    }
    rows = []
    for number, finding in enumerate(findings, 1):
        sources = []
        for item in finding.get("evidence", []):
            lines = item.get("lines", [])
            suffix = f' · L{lines[0]}–{lines[-1]}' if lines else ''
            sources.append(esc(str(item.get("sourcePath", "")) + ' · ' + str(item.get("function", "")) + suffix))
        limits = finding.get("limits", [])
        limit_html = '<div class="limits">분석 범위: ' + '<br>'.join(esc(limits_ko.get(x, x)) for x in limits) + '</div>' if limits else ''
        title = labels.get(finding.get("id"), finding.get("id", "규칙"))
        rows.append(f'<details><summary>{number:02d} · {esc(title)}</summary><div class="body"><p>{esc(finding.get("claimKo", ""))}</p><div class="evidence">{"<br>".join(sources)}</div>{limit_html}</div></details>')

    resources = [
        (PROJECT / 'prototype/project.godot', 'Godot 프로젝트'),
        (PROJECT / 'production/launch-prototype.ps1', '프로토타입 실행 스크립트'),
        (PROJECT / 'planning/mechanics-findings.json', '규칙 분석 근거'),
        (PROJECT / 'planning/package-inventory.json', 'REA 파일 구조 기록'),
        (LOCAL / 'test-evidence/rules-test-report.json', '실제 규칙 검사 보고서'),
        (LOCAL / 'asset-evidence/stage-validation/stage-validation-report.json', '실제 장면 검증 보고서'),
        (PROJECT / 'captures', '촬영 자료 폴더'),
        (PROJECT / 'planning/primary-sources.json', '공식 자료·사용 조건 기록'),
        (PROJECT / 'planning/original-footage-audit.json', '원작 촬영 검수 기록'),
        (LISTENING_PAGE, '발음 청취용 클립 5개')
    ]
    resources_html = ''.join('<li>' + link(path, label, OUTPUT) + '</li>' for path, label in resources if path.exists())
    hero = f'<figure class="hero"><a href="{url(stage_view, OUTPUT)}"><img src="{url(stage_view, OUTPUT)}" alt="독립 제작한 Neon Chamber: 로봇과 도구가 배치된 Godot 3D 실험 장면"></a><figcaption>우리의 독립 프로토타입 · Godot 실제 렌더 · 원작 벅샷 룰렛 화면과 구별하여 기록합니다.</figcaption></figure>' if stage_view.exists() else ''
    test_detail = f'Godot {esc(tests.get("engine", "미확인"))}에서 실행. 원작과 완전히 같다는 판정은 아닙니다.'
    stage_detail = "저장된 씬과 렌더의 해시 일치 확인." if stage_hash_current else "저장된 검증 프레임이며, 이후 씬 수정의 최종 재검증은 별도로 확인해야 합니다."
    if final["ready"]:
        top_status = '<span class="status">렌더링·기술 검사 완료</span><span class="status pending">사용자 검수 대기</span>'
        final_row = '<tr><td>완성 영상</td><td class="good">현재 4종 산출물 확인</td><td><a href="#final-review">전체 영상과 한영 자막</a> · 기술 검사 기록 및 MP4 해시 일치. 시청·청취와 사용자 검수는 별도입니다.</td></tr>'
        footer_note = '현재 4종 산출물과 기술 검사 기록을 연결한 로컬 검수 페이지입니다. 사용자 시청·청취 승인이나 업로드 완료를 뜻하지 않습니다.'
    else:
        top_status = '<span class="status">분석·프로토타입 기록</span><span class="status pending">영상 제작·검증 진행 중</span>'
        final_row = '<tr><td>완성 영상</td><td class="pending">제작·검증 진행 중</td><td>영상 2종·한영 자막과 현재 파일에 일치하는 기술 검사 결과가 모두 확인되면 이 페이지에 검수 영상을 표시합니다.</td></tr>'
        footer_note = '이 페이지는 실험 진행표입니다. 영상의 기술 검증과 사용자 시청·청취, 업로드 상태는 각각 구분합니다.'
    original_row = ('<tr><td>원작 플레이 대조</td><td class="good">선택 장면의 관찰 근거 확보</td><td>직접 녹화한 게임에서 자기 공포탄·수갑·톱의 선택과 결과를 확인한 기록입니다. 전체 동작 동일성이나 최종 편집본 시청 완료를 뜻하지 않습니다.</td></tr>'
                    if original_audit.get('verifiedFacts') else '<tr><td>원작 플레이 대조</td><td class="pending">실행 비교·촬영 확인 필요</td><td>원작의 실제 동작·시간과 프로토타입을 대조해야 합니다.</td></tr>')
    content = f'''
<div class="brand">YAMYAM CODING / 얌얌코딩</div><p class="eyebrow">REA와 AI · 분석에서 기반 프로토타입까지</p>
<h1>기존 게임을 분석해,<br>새 프로토타입의 출발점으로.</h1>
<p class="lead">REA가 AI의 분석 작업을 어떻게 돕는지부터 살펴보고, 규칙 분석 → 새 코드와 외형 제작 → 게임 엔진 실행으로 이어집니다. v4는 원작·자체 구현 비교와 전체 제작 흐름을 도입에 넣고, 검증한 본문은 보존한 수정본입니다.</p>
{top_status}{final_section}
{hero}{metrics()}
<div class="links">{link(PROJECT / 'prototype/project.godot', 'Godot 프로젝트 열기', OUTPUT, 'button')}{link(PROJECT / 'production/launch-prototype.ps1', '실행 스크립트 보기', OUTPUT, 'button')}<a href="#progress">진행표</a><a href="#findings">확인한 규칙</a><a href="#files">파일·증거</a></div>
<section class="section" id="progress"><h2>어디까지 진행됐나요?</h2><div class="tablewrap"><table><thead><tr><th>작업</th><th>현재 상태</th><th>확인 범위</th></tr></thead><tbody>
<tr><td>원작 파일 구조</td><td class="good">REA 분석 기록 확보</td><td>내장 Godot PCK, {count:,}개 항목. 헤더의 엔진 버전 {esc(pack_engine)}.</td></tr>
<tr><td>규칙 읽기</td><td class="good">{len(findings)}개 항목 정리</td><td>실제 .gd 텍스트의 조건·상태 전이를 확인. 디컴파일했다고 표시하지 않습니다.</td></tr>
<tr><td>독립 규칙 모델</td><td class="{'good' if passed and test_hash_current else 'pending'}">{esc(test_status)} · {checks}건</td><td>{test_detail}</td></tr>
<tr><td>새 외형·동작</td><td class="good">Blender 모델 · Godot 실행 기록</td><td>발사·도구 사용·관절 동작 검증. {stage_detail}</td></tr>
{original_row}{final_row}
</tbody></table></div></section>
<section class="section"><h2>같은 규칙을 다른 외형에 연결하기</h2><div class="two">{figures}</div><p class="subtle" style="margin-top:14px">두 이미지 모두 우리 제작물입니다. 스테이지 테스트는 최종 게임 UI 검수나 사용자 검수를 대신하지 않습니다.</p></section>
<section class="section" id="findings"><h2>확인한 규칙과 남은 검증</h2><p>아래 내용은 설치본의 스크립트 분석입니다. 코드에서 확인한 조건과 실제 플레이에서 확인해야 할 부분을 함께 남겼습니다.</p>{''.join(rows)}</section>
<section class="section"><h2>촬영에서 보여 줄 과정</h2><div class="flow"><div><b>01 / 원작</b><span>탄 공개 → 선택 → 결과를 직접 관찰</span></div><div><b>02 / 분석</b><span>파일 구조와 실제 조건문을 근거로 규칙 정리</span></div><div><b>03 / 재구현</b><span>새 모델에 독립 상태 모델과 동작 연결</span></div><div><b>04 / 비교</b><span>같은 조건에서 예상 결과와 실제 결과 대조</span></div></div><div class="record">도구의 분석 결과와 시험 실행 기록은 실제 수행 자료입니다. 화면 녹화 여부가 확인되지 않은 백그라운드 작업은 촬영한 과정처럼 표시하지 않습니다.</div></section>
<section class="section" id="files"><h2>로컬 파일과 근거</h2><ul>{resources_html}</ul><p class="subtle">프로젝트 파일은 Godot로 열고 실행할 수 있습니다. 브라우저에서 실행 스크립트 링크를 누르면 파일 보기 또는 다운로드로 동작할 수 있습니다.</p></section>
<div class="footer">기록 생성: {esc(current)} · 설치 빌드 {esc(mechanics.get('buildId', '미확인'))}<br>{footer_note}</div>'''
    output_html = shell("벅샷 룰렛 분석·재구현 | 얌얌코딩 진행표", content)
    (OUTPUT / "index.html").write_text(output_html, encoding="utf-8")

    key_claims = ''.join(f'<p class="claim">{esc(finding.get("claimKo", ""))}</p>' for finding in findings if finding.get("id") in ['ammo-sequence', 'self-blank-extra-turn'])
    evidence_content = f'''<div class="brand">YAMYAM CODING / 실제 분석 결과</div><p class="eyebrow">Buckshot Roulette · 설치 빌드 {esc(mechanics.get('buildId', '?'))}</p><h1>탄환 순서와 다음 차례는<br>서로 다른 규칙으로 정해진다.</h1><p class="lead">REA 파일 목록과 실제 스크립트 검토를 바탕으로 정리한 결과입니다. 실행 중인 터미널을 흉내 낸 화면이 아닙니다.</p>{metrics()}<div class="record">패키지: 내장 Godot PCK · 형식 {metadata.get('format_version', '?')} · 헤더 엔진 {esc(pack_engine)}<br>규칙 검사: {esc(test_status)} · {checks}건<br>검사 대상: 우리의 독립 모델. 원작 실행 결과와의 동일성 검증은 별도입니다.</div>{key_claims}<div class="footer">실제 파일 해시: <span class="evidence">{esc(mechanics.get('sourceExeSha256', '미확인'))}</span><br>{link(PROJECT / 'planning/mechanics-findings.json', '규칙별 근거', EVIDENCE_PAGE.parent)} · {link(LOCAL / 'test-evidence/rules-test-report.json', '시험 실행 보고서', EVIDENCE_PAGE.parent)} · {link(OUTPUT / 'index.html', '전체 진행표', EVIDENCE_PAGE.parent)}<br>기록 생성 {esc(current)}</div>'''
    EVIDENCE_PAGE.write_text(shell("실제 REA 분석·규칙 시험 결과", evidence_content, True), encoding="utf-8")
    print(json.dumps({"page": str(OUTPUT / 'index.html'), "evidencePage": str(EVIDENCE_PAGE), "findings": len(findings), "checks": checks, "testsPassed": passed, "testSourceHashesCurrent": test_hash_current, "stageHashesCurrent": stage_hash_current, "finalReviewVisible": final["ready"], "finalReviewReason": final["reason"], "humanReview": "pending"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
