# Cuphead animation-tick-v1 input contract

Code-only preparation. No server, TTS or render has run. `production-input.ts`
discovers the two project JSON files with a Vite glob and deliberately refuses
to run until **actual current PCM-derived inputs** exist. It never supplies a
synthetic duration, provisional timing or invented source frames.

`projects/shorts-cuphead-animation-tick/production/visual-timing.json` requires:

- `revision: "animation-tick-v1"`, `fps: 60`, positive integer `frames`,
  `previewOnly: false`, and `timingInputs.voiceSha256`.
- Six contiguous `sections` covering `[0, frames)` in this order:
  `game`, `frames`, `source-rates`, `pose24`, `position24`, `close`.
  Each has `startFrame`/`endFrame`; optional `forceDiagram` skips a real cut.
- `events` keyed by all19 `p1-1`…`p6-3` clause IDs from the actual caption/voice
  alignment, each with `startFrame`/`endFrame`.
- Optional `reactions` overrides the three cue-linked original-cat reactions.

`visual-config.json` requires `game: "Cuphead"`, `framesPrepared: true`, `frameRoot` and
`poseImages: {A, B, C}` with local Vite-accessible URLs. Source/pixel provenance
is in the project's `sources/selected-footage.json`. The three source-image
crops exist on C under `local/sources/pose-analysis/`; they are explanatory
frame examples, never a recovered game sprite sheet or measured24Hz samples.
The saved preproduction config deliberately has `framesPrepared: false` until
the coordinating task actually extracts the native source cut frame files.

`cuts` can supply `game`, `source-rates` and `close`, with `frameDirectory`,
`maxDuration`, optional `firstFrame`, `pattern` (default `{frame}.jpg`) and
`digits` (default6). Extract source frames at native60fps on C. When speech
outlasts an inspected cut, the same timing diagram takes over; footage is never
looped, slowed or held and misclassified as moving gameplay.

Optional `focus` on each cut accepts inspected `{time,x,y,radiusX,radiusY}`
keyframes in native1920×1080 source coordinates, with strictly increasing
cut-local seconds. The green editorial outline interpolates only within that
verified range and clears at the cut; no invented detector measurement appears.

The scene owns portrait y460…1275; the finishing stage supplies the fixed
headline/captions. Cat reserve is x600…1060/y1110…1670. The full-width second
position row suppresses the cat. Final1080p/375px motion, source-annotation,
caption collision and actual audio QA are still pending.

`node src/projects/shorts-cuphead-animation-tick/model.check.cjs` verifies the
CPU-only sample schedule and one-variable/end-point invariants without loading
Motion Canvas or launching any media job.
