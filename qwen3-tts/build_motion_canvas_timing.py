"""Generate motion-canvas/src/narration.ts from the rendered narration timing.

Each Motion Canvas scene must last exactly as long as the narration segment it
illustrates, so the on-screen visual changes on the same frame the narrator
starts that part. Cut points are snapped to the 60 fps render grid: Motion
Canvas rounds every wait to whole frames anyway, and scene start times are the
running sum of previous scene durations -- snapping first keeps that sum from
drifting away from the audio over a 5-minute video.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# The summary printed at the end contains Korean labels and em dashes, which
# the default Windows console codepage (cp949) cannot encode.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
NARRATION_DIR = ROOT / "shared" / "output" / "narration" / "qwen3-balanced"
TIMING_JSON = NARRATION_DIR / "jump-physics-qwen3-balanced.timing.json"
FINAL_WAV = NARRATION_DIR / "jump-physics-qwen3-balanced.wav"
OUTPUT_TS = ROOT / "motion-canvas" / "src" / "narration.ts"
# @motion-canvas/ffmpeg's exporter can't render audio Vite has to serve from
# outside the project root (see narrated.ts for why), so the audio the
# narrated project actually imports is this synced-on-every-build copy, not
# the canonical shared/output/ one directly.
AUDIO_COPY = ROOT / "motion-canvas" / "src" / "assets" / "narration" / "jump-physics-qwen3-balanced.wav"

RENDER_FPS = 60
# Cut points are snapped to 30 fps rather than 60. Motion Canvas rounds every
# wait up to a whole frame, so a duration that is not a whole number of frames
# gets padded -- and that padding accumulates across scenes. 30 divides both the
# preview (30 fps) and render (60 fps) rates, so snapping here keeps the video
# locked to the audio in the editor and in the final render alike. Worst-case
# cost is 1/60 s of drift against the narration, which is inaudible.
SNAP_FPS = 30

# Which Motion Canvas scene illustrates which part of the narration. A segment
# ends where the next one begins, so each entry only needs its start point,
# given as (narration scene id, 1-based line number inside that scene). Keying
# off the script's own scene ids keeps this readable and stops it from silently
# shifting if a line is ever added or removed. `key` must match the scene module
# name under src/scenes/narrated/.
SEGMENTS = [
    ("intro", ("01", 1), "도입 — 점프가 결정하는 것"),
    ("basic", ("02", 1), "프레임마다 더해지는 중력 + 최고점과 낙하"),
    ("axes", ("04", 1), "가로 이동(X축)과 설계 목표"),
    ("mario", ("05", 1), "슈퍼 마리오브라더스"),
    ("metroid", ("06", 1), "메트로이드"),
    ("ghosts", ("07", 1), "마계촌"),
    ("sf2", ("08", 1), "스트리트 파이터 II — 장기에프"),
    ("smashSquat", ("09", 1), "스매시브라더스 — 점프 스쿼트"),
    ("smashUltimate", ("10", 1), "스매시브라더스 얼티밋 — 초기 가속"),
    ("jumpKing", ("11", 1), "점프킹 — 차지 후 발사"),
    ("celeste", ("12", 1), "셀레스트 — 홀드 길이로 조절"),
    ("megaman", ("13", 1), "록맨 X — 대시 점프"),
    ("outro", ("14", 1), "결론 — 정답은 없다"),
]


def snap_frame(seconds: float) -> int:
    """Round a time to the nearest whole frame on the shared 30 fps grid."""
    return round(seconds * SNAP_FPS)


def main() -> None:
    data = json.loads(TIMING_JSON.read_text(encoding="utf-8"))
    total = data["duration_seconds"]

    by_scene: dict[str, list[dict]] = {}
    for entry in data["entries"]:
        by_scene.setdefault(entry["scene_id"], []).append(entry)

    def locate(anchor: tuple[str, int]) -> dict:
        scene_id, line_number = anchor
        lines = by_scene.get(scene_id)
        if not lines:
            raise KeyError(f"narration scene {scene_id!r} not found in timing data")
        if not 1 <= line_number <= len(lines):
            raise IndexError(
                f"narration scene {scene_id!r} has {len(lines)} lines; "
                f"line {line_number} was requested"
            )
        return lines[line_number - 1]

    starts = [locate(anchor) for _, anchor, _ in SEGMENTS]

    # A segment starts when its first narration line starts. Work in whole
    # frames so start/end/duration stay exactly consistent with each other --
    # the durations are summed by the player to place each scene, so they must
    # not carry independent rounding error.
    cut_frames = [snap_frame(entry["start"]) for entry in starts]
    cut_frames.append(snap_frame(total))

    rows = []
    for index, ((key, _anchor, label), entry) in enumerate(zip(SEGMENTS, starts)):
        start_frame, end_frame = cut_frames[index], cut_frames[index + 1]
        rows.append(
            {
                "key": key,
                "label": label,
                "start": start_frame / SNAP_FPS,
                "end": end_frame / SNAP_FPS,
                "duration": (end_frame - start_frame) / SNAP_FPS,
                # Reported at the render rate, which is what the exported video
                # actually contains.
                "frames": (end_frame - start_frame) * (RENDER_FPS // SNAP_FPS),
                "firstLine": entry["text"],
            }
        )

    lines = [
        "// GENERATED by qwen3-tts/build_motion_canvas_timing.py -- do not edit by hand.",
        "//",
        "// Cut points come from the rendered narration's measured per-line timings",
        "// (shared/output/narration/qwen3-balanced/*.timing.json), snapped to the",
        "// 60 fps render grid. Each scene below runs for exactly `duration`",
        "// seconds, so scene N starts on the same frame the narrator begins the",
        "// matching sentence.",
        "",
        "export type NarrationSegment = {",
        "  /** Scene module name under src/scenes/narrated/. */",
        "  key: string;",
        "  /** Human-readable segment name (Korean). */",
        "  label: string;",
        "  /** Absolute start time in the narration audio, in seconds. */",
        "  start: number;",
        "  /** Absolute end time in the narration audio, in seconds. */",
        "  end: number;",
        "  /** Exact scene length in seconds (end - start). */",
        "  duration: number;",
        "  /** Exact scene length in whole frames at NARRATION_FPS. */",
        "  frames: number;",
        "  /** First narrated sentence of this segment, for reference. */",
        "  firstLine: string;",
        "};",
        "",
        f"export const NARRATION_FPS = {RENDER_FPS};",
        f"export const NARRATION_TOTAL_SECONDS = {cut_frames[-1] / SNAP_FPS};",
        f"export const NARRATION_TOTAL_FRAMES = {cut_frames[-1] * (RENDER_FPS // SNAP_FPS)};",
        "",
        "export const SEGMENTS = {",
    ]
    for row in rows:
        lines.append(f"  {row['key']}: {{")
        lines.append(f"    key: {json.dumps(row['key'], ensure_ascii=False)},")
        lines.append(f"    label: {json.dumps(row['label'], ensure_ascii=False)},")
        lines.append(f"    start: {row['start']},")
        lines.append(f"    end: {row['end']},")
        lines.append(f"    duration: {row['duration']},")
        lines.append(f"    frames: {row['frames']},")
        lines.append(f"    firstLine: {json.dumps(row['firstLine'], ensure_ascii=False)},")
        lines.append("  },")
    lines.append("} satisfies Record<string, NarrationSegment>;")
    lines.append("")
    lines.append("/** Scene order, matching the narration audio. */")
    order = ", ".join(f"'{row['key']}'" for row in rows)
    lines.append(f"export const SEGMENT_ORDER = [{order}] as const;")
    lines.append("")

    OUTPUT_TS.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_TS}")

    AUDIO_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FINAL_WAV, AUDIO_COPY)
    print(f"Synced {AUDIO_COPY}")
    print()
    total_frames = 0
    for row in rows:
        total_frames += row["frames"]
        print(
            f"  {row['key']:<14} {row['start']:7.3f} -> {row['end']:7.3f}  "
            f"({row['duration']:6.3f}s / {row['frames']:5d}f)  {row['label']}"
        )
    expected_frames = cut_frames[-1] * (RENDER_FPS // SNAP_FPS)
    print()
    print(
        f"  sum of scene durations: {total_frames / RENDER_FPS:.3f}s "
        f"({total_frames} frames @ {RENDER_FPS}fps)"
    )
    print(
        f"  narration audio length: {expected_frames / RENDER_FPS:.3f}s "
        f"({expected_frames} frames, raw {total:.3f}s)"
    )
    if total_frames != expected_frames:
        raise SystemExit("scene durations do not sum to the narration length")


if __name__ == "__main__":
    main()
