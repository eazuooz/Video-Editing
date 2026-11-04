"""Collect A01's verified final pair into an isolated four-file local delivery.

    python build_delivery.py --dry-run
    python build_delivery.py --build
    python build_delivery.py --verify-existing

The naming/layout follows scripts/collect-video-output.cjs, but writes ONLY
this revision's local/delivery tree. It does not promote the shared project
manifest, edit a worklist/checkpoint, upload, or assert user review. Existing
deliveries are never replaced/deleted. Media is copied byte-for-byte only
after the current pair/structural/caption/audio-review receipts match.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import uuid

from storage_paths import HERE, LOCAL, PROJECT, ROOT, local_output, relative, repo_path

SLUG = "animation-assigning"
REVISION = "grid-v1"
DESTINATION = LOCAL / "delivery/output" / SLUG


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path):
    return {"path": relative(path), "sha256": sha(path), "bytes": Path(path).stat().st_size}


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def authorized_scope():
    """Read current local-production scope; no new approval or platform action."""
    control_path = ROOT / "shared/publishing/video-production-control.json"
    authorization_path = HERE / "authorization.json"
    grant_path = HERE / "execution-grant.json"
    control, auth, grant = read(control_path), read(authorization_path), read(grant_path)
    batch = control["finiteBatchAuthorizations"]["animation-18-20261031"]
    if not batch.get("productionAuthorized") or "A01" not in batch.get("episodeIds", []):
        raise ValueError("A01 finite batch local production is not authorized")
    if (auth.get("slug"), auth.get("revision")) != (SLUG, REVISION):
        raise ValueError("Wrong project/revision authorization")
    if not auth.get("localProductionAuthorized") or auth.get("platformMutation") is not False:
        raise ValueError("This collector requires the current local-only production scope")
    if grant.get("revision") != REVISION or "video-verify" not in grant.get("stages", []):
        raise ValueError("The parent has not granted this revision's final verification slot")
    return {"control": artifact(control_path), "authorization": artifact(authorization_path),
            "executionGrant": artifact(grant_path), "selectedSharedVideoUnchanged": True,
            "basis": "Parent-directed A01 local four-output delivery after verified pair; no platform authorization inferred."}


def parse_srt(path):
    result = []
    text = Path(path).read_text(encoding="utf-8-sig").strip()
    pattern = re.compile(r"^(\d+):(\d{2}):(\d{2}),(\d{3}) --> (\d+):(\d{2}):(\d{2}),(\d{3})$")
    for index, block in enumerate(re.split(r"\r?\n\s*\r?\n", text), 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(index):
            raise ValueError(f"Invalid SRT sequence: {path}/{index}")
        match = pattern.fullmatch(lines[1])
        if not match:
            raise ValueError(f"Invalid SRT clock: {path}/{index}")
        values = list(map(int, match.groups()))
        clock = lambda a: a[0]*3600 + a[1]*60 + a[2] + a[3]/1000
        start, end = clock(values[:4]), clock(values[4:])
        content = " ".join(" ".join(lines[2:]).split())
        if not content or start < 0 or end <= start or (result and start < result[-1]["end"]-.0001):
            raise ValueError(f"Empty/overlapping SRT cue: {path}/{index}")
        result.append({"cue": index, "start": start, "end": end, "text": content})
    if not result:
        raise ValueError("Empty subtitle file")
    return result


def sources_for(plan):
    edit = repo_path(plan["outputDir"])
    stem = plan["outputStem"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", stem):
        raise ValueError("Unsafe outputStem")
    return edit, {
        "captioned.mp4": edit / f"{stem}-captioned.mp4",
        "clean.mp4": edit / f"{stem}-clean.mp4",
        "ko.srt": edit / "captions.ko.srt",
        "en.srt": edit / "captions.en.srt",
    }


def check_verified_inputs(plan_path, plan, extra_review_paths):
    if plan.get("slug") != SLUG or int(plan["fps"]) != 60:
        raise ValueError("Collector is scoped to A01 FHD60")
    edit, sources = sources_for(plan)
    pair_path, structural_path = edit / "pair-build.json", edit / "structural-verification.json"
    pair, structural = read(pair_path), read(structural_path)
    plan_digest = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    if pair["signature"].get("planSha256") != plan_digest:
        raise ValueError("Final pair was built from a different edit plan")
    if pair["signature"].get("captionsAssSha256") != sha(edit / "captions.ko.ass"):
        raise ValueError("Encoded captions are not the current approved caption build")
    if structural.get("status") != "pass" or structural.get("identicalContinuousAudio") is not True:
        raise ValueError("Both final masters must pass full structural verification first")
    if pair.get("continuousAac") is not True:
        raise ValueError("Pair receipt does not establish a shared continuous AAC stream")
    source_artifacts = {key: artifact(path) for key, path in sources.items()}
    for suffix in ("clean", "captioned"):
        item, proof = source_artifacts[suffix+".mp4"], structural["outputs"][suffix]
        built = pair["outputs"][suffix]
        if item["sha256"] != proof["sha256"] or item["sha256"] != built["sha256"]:
            raise ValueError(f"Final {suffix} bytes differ from verified receipts")
        if repo_path(proof["path"]) != sources[suffix+".mp4"] or repo_path(built["path"]) != sources[suffix+".mp4"]:
            raise ValueError("Receipt points to a different master")
        video, pts = proof["video"], proof["pts"]
        if (video["width"], video["height"]) != (1920, 1080) or Fraction(video["avg_frame_rate"]) != 60:
            raise ValueError("Verified master is not1920x1080/60fps")
        if pts.get("allDecodedFramesScanned") is not True or pts.get("strictlyIncreasing") is not True or pts["frames"] != plan["totalFrames"]:
            raise ValueError("Complete final frame/PTS verification is missing")
        if abs(proof["durationSeconds"]-plan["totalFrames"]/60) > 1/60:
            raise ValueError("Verified master duration differs from this plan")
    audio_packets = {structural["outputs"][key]["audioPacketsSha256"] for key in ("clean", "captioned")}
    if len(audio_packets) != 1:
        raise ValueError("Paired audio packet hashes differ")
    tracks = {lang: parse_srt(sources[lang+".srt"]) for lang in ("ko", "en")}
    if [(x["start"], x["end"]) for x in tracks["ko"]] != [(x["start"], x["end"]) for x in tracks["en"]]:
        raise ValueError("Paired subtitle clocks differ")
    duration = plan["totalFrames"]/60
    if tracks["ko"][-1]["end"] > duration:
        raise ValueError("Subtitles exceed the master")
    scripts = {}
    for lang in ("ko", "en"):
        script_path = PROJECT / f"script/{REVISION}/narration.{lang}.json"
        script = read(script_path)
        expected = " ".join(" ".join(text.split()) for scene in script["scenes"] for text in scene["lines"])
        if " ".join(cue["text"] for cue in tracks[lang]) != expected:
            raise ValueError(f"{lang} SRT no longer preserves the complete canonical narration")
        scripts[lang] = {"data": script, "artifact": artifact(script_path)}
    text_review_path = HERE / "caption-text-review.json"
    text_review = read(text_review_path)
    if text_review.get("issues") or text_review["counts"]["pairedCues"] != len(tracks["ko"]):
        raise ValueError("Current complete bilingual caption text review is required")
    reviewed = {item["path"]: item["sha256"] for item in text_review["inputs"]}
    for path in [sources["ko.srt"], sources["en.srt"], edit/"captions.ko.ass", edit/"captions.en.ass"]:
        if reviewed.get(relative(path)) != sha(path):
            raise ValueError("Caption review hash is stale")
    asr_review_path = HERE / "final-mix-asr-review.json"
    asr_review = read(asr_review_path)
    if asr_review.get("fullTextDirectReview") is not True or asr_review.get("all17ParagraphsRead") is not True:
        raise ValueError("Current full final-mix text review is required")
    audio_hashes = {item["sha256"] for item in asr_review.get("evidence", []) if item["path"].endswith(".m4a")}
    if pair["signature"]["aacSha256"] not in audio_hashes:
        raise ValueError("Final ASR text review does not bind the AAC source used by this pair")
    evidence = [plan_path, pair_path, structural_path, text_review_path, asr_review_path,
                HERE/"source-stem-continuity-review.json", LOCAL/"qa/final-audio-v1/continuity.json"]
    evidence.extend(repo_path(path) for path in extra_review_paths)
    evidence = list(dict.fromkeys(evidence))
    return {"sources": sources, "sourceArtifacts": source_artifacts, "tracks": tracks,
            "scripts": scripts, "duration": duration, "structural": structural,
            "audioPacketsSha256": next(iter(audio_packets)), "evidence": [artifact(path) for path in evidence]}


def page(title, duration, cues, files, captioned_hash):
    escape = html.escape
    seconds = round(duration)
    clock = f"{seconds//60}분 {seconds%60:02}초"
    captions = f"{SLUG}.captioned.mp4"
    links = "\n".join(f"<li><a href='{escape(item['name'])}' download>{escape(item['label'])}</a><small>{item['bytes']/1024/1024:.1f} MB</small></li>" for item in files)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · 얌얌코딩 검수본</title>
<style>:root{{--bg:#0b0d0b;--text:#f4f4ee;--muted:#b3bab0;--heading:#e8cf83;--line:#394037}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 'Malgun Gothic',sans-serif}}main{{max-width:1120px;margin:40px auto;padding:0 24px 48px}}.brand{{color:var(--heading);font-weight:700}}h1{{font-size:30px;line-height:1.35;margin:12px 0}}h2{{font-size:22px;color:var(--heading)}}.meta,small{{color:var(--muted)}}.status{{border-left:4px solid var(--heading);padding:10px 16px;margin:24px 0}}video{{display:block;width:100%;aspect-ratio:16/9;background:#000}}a{{color:var(--heading);text-underline-offset:4px}}ul{{padding:0;list-style:none}}li{{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid var(--line);padding:12px 0}}code{{overflow-wrap:anywhere;font-size:13px}}details{{margin-top:28px}}@media(max-width:600px){{main{{margin-top:24px;padding:0 16px 32px}}h1{{font-size:24px}}body{{font-size:16px}}li{{gap:12px}}}}</style></head>
<body><main><div class="brand">얌얌코딩 · 애니메이션 A01</div><h1>{escape(title)}</h1>
<p class="meta">1920×1080 · 60fps · {clock} · 한영 자막 각 {cues}개</p>
<p class="status">전체 영상 검수용 파일입니다. 사용자 최종 검수와 전체 음성 청취는 아직 완료로 기록하지 않았습니다.</p>
<video controls playsinline preload="metadata"><source src="{captions}" type="video/mp4">브라우저에서 재생되지 않으면 아래 영상 파일을 열어 주세요.</video>
<p><a href="{captions}">전체 자막 영상 열기</a></p><h2>영상과 자막 받기</h2><ul>{links}</ul>
<details><summary>파일 버전 확인</summary><p>자막 영상 SHA256</p><code>{captioned_hash}</code><p><a href="delivery-manifest.json">파일 기록</a> · <a href="README.md">검수 안내</a></p></details>
</main></body></html>"""


def verify_existing(destination):
    manifest_path = destination / "delivery-manifest.json"
    manifest = read(manifest_path)
    if manifest.get("slug") != SLUG or manifest.get("revision") != REVISION or len(manifest["files"]) != 4:
        raise ValueError("Existing delivery is not this four-file revision")
    for item in [*manifest["files"], *manifest["metadataArtifacts"]]:
        name = item["name"]
        if Path(name).name != name:
            raise ValueError("Unsafe delivery filename")
        target = destination / name
        if not target.is_file() or sha(target) != item["sha256"]:
            raise ValueError(f"Existing delivery changed: {target}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--dry-run", action="store_true")
    actions.add_argument("--build", action="store_true")
    actions.add_argument("--verify-existing", action="store_true")
    parser.add_argument("--plan", default=str(HERE / "edit-plan.json"))
    parser.add_argument("--review-evidence", action="append", default=[])
    args = parser.parse_args()
    plan_path = repo_path(args.plan)
    plan = read(plan_path)
    destination = local_output(DESTINATION)
    edit, sources = sources_for(plan)
    if args.dry_run:
        print(json.dumps({"status": "prepared-only-no-copy-or-output-write", "destination": str(destination),
            "files": [{"source": str(source), "destinationName": f"{SLUG}.{key}"} for key, source in sources.items()],
            "requiredReceipts": [str(edit/"pair-build.json"), str(edit/"structural-verification.json"),
                                 str(HERE/"caption-text-review.json"), str(HERE/"final-mix-asr-review.json")],
            "userFinalReview": False, "uploads": False}, ensure_ascii=False))
        return
    scope = authorized_scope()
    if args.verify_existing:
        existing = verify_existing(destination)
        print(json.dumps({"status": "existing-four-files-hash-verified", "manifest": str(destination/"delivery-manifest.json"),
                          "userFinalReview": existing["review"]["userFinalReview"]}, ensure_ascii=False))
        return
    verified = check_verified_inputs(plan_path, plan, args.review_evidence)
    if destination.exists():
        existing = verify_existing(destination)
        if {item["role"]: item["sha256"] for item in existing["files"]} != {
                role: item["sha256"] for role, item in verified["sourceArtifacts"].items()}:
            raise FileExistsError("Preserve existing delivery; a changed master needs a separately named revision")
        print(json.dumps({"status": "identical-existing-delivery-reused", "directory": str(destination)}, ensure_ascii=False))
        return
    required = sum(item["bytes"] for item in verified["sourceArtifacts"].values()) + 64*1024*1024
    if shutil.disk_usage(LOCAL).free < required:
        raise OSError(f"Insufficient free space for byte-preserved four-file copy ({required} bytes needed)")
    delivery_root = local_output(LOCAL / "delivery")
    stage = local_output(delivery_root / "staging" / ("A01-" + uuid.uuid4().hex))
    stage.mkdir(parents=True, exist_ok=False)
    labels = {"captioned.mp4": "한글 자막 영상", "clean.mp4": "자막 없는 영상", "ko.srt": "한글 자막 SRT", "en.srt": "영어 자막 SRT"}
    files = []
    for role, source in verified["sources"].items():
        target = stage / f"{SLUG}.{role}"
        if target.exists():
            raise FileExistsError(target)
        shutil.copy2(source, target)
        evidence = verified["sourceArtifacts"][role]
        if sha(target) != evidence["sha256"] or sha(source) != evidence["sha256"]:
            raise ValueError(f"Copy/source hash mismatch; staging retained at {stage}")
        files.append({"name": target.name, "role": role, "label": labels[role],
                      "source": evidence["path"], "sha256": evidence["sha256"], "bytes": evidence["bytes"]})
    title = verified["scripts"]["ko"]["data"]["title"]
    master_hash = verified["sourceArtifacts"]["captioned.mp4"]["sha256"]
    (stage/"index.html").write_text(page(title, verified["duration"], len(verified["tracks"]["ko"]), files, master_hash), encoding="utf-8")
    file_lines = "\n".join(f"- `{item['name']}` — SHA256 `{item['sha256']}`" for item in files)
    readme = f"""# {title}

이 폴더의 전체 자막 영상을 열어 최종 검수해 주세요. 사용자 검수와 전체 음성 청취는 미완료로 남겨 두었습니다.

- 영상: 1920×1080, 60fps, {plan['totalFrames']}프레임, {verified['duration']:.6f}초.
- 한국어·영어 SRT: 각 {len(verified['tracks']['ko'])}개, 같은 큐 시간.
- 검증된 clean/captioned 제작 마스터를 재인코딩 없이 복사했습니다. 두 영상의 AAC 패킷은 같습니다.
- `index.html`에서 자막 영상을 재생하거나 네 파일을 직접 열 수 있습니다. SRT는 별도 편집기나 업로드용 자막입니다.
- 파일 모음 생성과 기술 검사 통과는 사람의 시청·청취 승인이나 게시 승인이 아닙니다. 업로드·예약은 수행하지 않았습니다.
- 원본 제작 파일, 이전 버전과 외부 플랫폼 상태는 변경하지 않았습니다.

## 파일

{file_lines}

원본 경로·검사 기록과 현재 해시는 `delivery-manifest.json`에 있습니다. 이후 수정으로 영상 해시가 바뀌면 그 버전을 다시 검수합니다.
"""
    (stage/"README.md").write_text(readme, encoding="utf-8")
    metadata = [{"name": name, "sha256": sha(stage/name), "bytes": (stage/name).stat().st_size}
                for name in ("index.html", "README.md")]
    manifest = {"schemaVersion": 1, "slug": SLUG, "episode": "A01", "revision": REVISION,
                "status": "collected-verified-master-pair-user-review-pending",
                "createdAt": datetime.now(timezone.utc).isoformat(), "title": title,
                "directory": relative(destination), "files": files, "metadataArtifacts": metadata,
                "captionedMasterSha256": master_hash, "format": {"width": 1920, "height": 1080, "fps": 60,
                    "frames": plan["totalFrames"], "durationSeconds": verified["duration"]},
                "subtitles": {"koCues": len(verified["tracks"]["ko"]), "enCues": len(verified["tracks"]["en"]),
                              "sameCueTiming": True, "completeCanonicalTextPreserved": True},
                "verification": {"structuralFinalPair": "pass", "sameContinuousAacPackets": True,
                    "audioPacketsSha256": verified["audioPacketsSha256"], "copiesMatchVerifiedSourceBytes": True,
                    "evidence": verified["evidence"], "scripts": {k: v["artifact"] for k, v in verified["scripts"].items()},
                    "visualReview": "Use the attached current review evidence; collection does not create or upgrade pixel/motion approval."},
                "review": {"userFinalReview": False, "userReviewedSha256": None,
                           "actualWholeListening": False, "status": "pending-actual-human-review-of-this-hash"},
                "platform": {"youtubeUploadAuthorized": False, "youtubeUploaded": False, "scheduled": False,
                             "googleDriveUploadPerformed": False, "existingPlatformStateChanged": False},
                "scope": scope, "collector": artifact(Path(__file__)),
                "sharedProjectManifestOrWorklistChanged": False, "mediaReencoded": False}
    save(stage/"delivery-manifest.json", manifest)
    # Both explicitly resolved paths must remain in this one local delivery tree.
    if not stage.resolve().is_relative_to(delivery_root) or not destination.resolve().is_relative_to(delivery_root):
        raise ValueError("Staging/destination escaped the isolated delivery tree")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError("Another collector created the destination; staging preserved")
    stage.rename(destination)
    verify_existing(destination)
    print(json.dumps({"status": manifest["status"], "directory": str(destination),
                      "index": str(destination/"index.html"), "captioned": str(destination/f"{SLUG}.captioned.mp4"),
                      "captionedMasterSha256": master_hash, "manifestSha256": sha(destination/"delivery-manifest.json"),
                      "userFinalReview": False, "uploads": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
