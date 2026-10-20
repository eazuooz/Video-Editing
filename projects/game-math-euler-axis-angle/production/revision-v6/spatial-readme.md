# M04 V6 spatial production

This is new V6 source. V5 scenes, media, voice and project settings are preserved.
The detailed aircraft construction is reused as procedural source; its geometry
is rebuilt in native +Z-forward coordinates. No V5 right-hand label substitution
or Z-reflection/conjugation is used.

- Authoring: Unity 6000.6.0f1, canonical URP 17.6.0.
- Actual capture: separate `production/local/revision-v6/unity-capture`, built-in
  pipeline, linear project settings, native 1920×1080/60, no audio.
- Math: left-hand positive rotations, row vectors, object→upright,
  `R = Rz(b) Rx(p) Ry(h)`. Engine column transform is `R.transpose`.
- Palette: selected V6 nearblack `#080b0d`, the same aircraft, bright labeled
  semantic axes. Solid body axes and dashed upright axes share the object origin.
- Editable source-recipe `.unity` files exist. The explicit isolated bake must
  still save their detailed editable hierarchy. CPU recipes are not evidence
  that this Editor save or a render occurred.

## Existing inputs and outputs

`spatial-plan.json` maps all 41 scenes / 106 teaching beats. It selects 48 finite
Unity motion beats across 25 scenes; the other beats use root 2D or independent
footage. Each physical beat has exact planned `durationFrames`, first/last image
paths and the authored before/after programs. Null source motion values have
explicit finite budgets in this plan.

`spatial-capture.py` reads the measured `timeline.json` with the original beat
IDs (`v6-04.B01`). Capture frames are:

`round(visualEnd * 60) - round(visualStart * 60)`.

Beat timestamps may be global video seconds. Only their difference is used.
The parent holds the first image during explanation, plays native motion, then
holds the last image for observation/results. Whole narration is never rendered
as repeated Unity frames. `lineStarts`/`lineEnds` remain scene-relative.

Final clip directory: `production/local/revision-v6/spatial-clips/`.
Each beat outputs MP4, `.first.png`, `.last.png`, `.anchors.ndjson`.
Anchors include actual projected body/upright axis endpoints and row matrices.
Labels/leaders are editorial guides; geometry uses the camera depth buffer.
No commercial-game axes, detector measurements or flight physics are invented.

Sample output is separate: `production/local/revision-v6/spatial-sample/`.
Its 180-frame timing is a visual-system sample, not the final beat duration.
The sample also captures one neutral identity-pose `testbed-still.png` with the
same aircraft/camera and axes/active arcs hidden, then copies it into
`spatial-clips/` for the parent's dimmed 2D background. A sample does not occupy
the final clip path.

## CPU preparation

From repository root:

```text
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-prepare.py --stage
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-check.py
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-capture.py --sample --bake
```

These do not start Unity. `spatial-check.py` verifies rotation programs and
compiles source against the installed Unity module/API assemblies. Executing
the engine's quaternion checks, rendering glyphs and saving source scenes still
require the explicit isolated Editor job.

## Coordinated sample, then stop

Only after the parent's explicit GPU handoff, following TTS and whole source ASR:

```text
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-capture.py --sample --bake --run
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-sync.py
```

The one sample job saves all 26 spatial `.unity` scenes and the shared testbed,
captures `v6-04.B01`, exits its own Editor normally and releases only its own
GPU lease. It requires at least 4096 MiB free, no visible Python GPU owner and
no other lease. No main or foreign Editor is closed. It records only its own
PID/creation time/project, plus WDDM per-process memory when available; no token
arguments are logged.

Inspect current native/mobile sample and actual caption clearance before full
capture. Full capture needs the next explicit GPU handoff. With a measured
timeline available, use:

```text
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-capture.py --timeline projects/game-math-euler-axis-angle/production/revision-v6/timeline.json --run
```

When the parent explicitly authorizes the existing fixed finite budgets before
global speech timing is ready, use the separate mode:

```text
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-capture.py --plan-durations
python projects/game-math-euler-axis-angle/production/revision-v6/spatial-capture.py --plan-durations --run
```

The first command only prepares a job. This mode reads no speech timeline and
does not create one. It checks all 48 primary clips total 19,020 frames and the
auxiliary clip has 180 frames, cross-checking each budget against the shot
catalog. The receipt says `fixed-plan-durations`, binds both plan/catalog
hashes and leaves `timelineSha256` null. The later compositor must still check
each measured visual interval equals its captured clip's exact frame count;
this mode does not authorize changing speech timing or silently stretching clips.

No rebake is required if source geometry/profile is unchanged. Saved source
sync changes only V6 copied materials to installed URP shader GUIDs. Actual
capture remains built-in. Direct playback in the main URP editor is not claimed.

`spatial-capture-receipt.json` binds actual clip/image/anchor hashes and exact
container/anchor frame counts; it does not claim a full decode or human review.
The parent owns final assembly, captions, moving/native/mobile QA and commits.
