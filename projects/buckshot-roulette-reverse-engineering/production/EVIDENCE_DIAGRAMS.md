# Evidence diagrams

`render_evidence_diagrams.py` prepares fourteen paragraph clips for narration scenes 02, 03, 04, 05, 06 and 08. These are independently authored **analysis visualizations**, not original gameplay or filmed tool operation. Scene 07 model footage is handled separately. No recovered source code is displayed.

Each clip uses a continuous diagram whose states follow exact narration phrases. Queue consumption moves the remaining cells forward; magnifier inspection preserves the queue; beer ejection advances it. Other diagrams progressively reveal state conditions, mode-specific AI branches, independently authored code excerpts, actual test counts and the final evidence chain. One-off reveals are used instead of looping or extending idle gameplay.

## Timing and rendering

Copy `evidence-diagram-timings.template.json` into ignored `production/local`, supply actual measured paragraph duration/speech end, and set `timingVerified: true` only for those measured durations. `cueTimes` contains paragraph-local seconds keyed by the supplied cue IDs. Without an offset, its position is estimated proportionally from the approved spoken text and **reported as an estimate**. `cueAlignmentReviewed` stays false until the actual speech and moving result are checked.

When the current narration and word ASR are available, run `align_evidence_diagram_cues.py` first. It reads their existing files, maps exact phrase characters to actual word timestamps, and writes `production/local/evidence-diagram-timings.json` with per-anchor evidence. It never launches another transcription job. Paragraph frames run to the next paragraph start, preserving only the existing breathing gap. Spoken Korean quantities and their ASR digit spellings are explicitly normalized; a low match or an unreliable anchor beginning stops preparation instead of silently guessing. This automatic timestamp match remains separate from actual listening.

```powershell
C:/Python/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/render_evidence_diagrams.py --timings projects/buckshot-roulette-reverse-engineering/production/local/evidence-diagram-timings.json
```

Preparation writes ASS, a receipt per paragraph, and an index under `production/local/evidence-diagrams`. It does not invoke FFmpeg. Add `--only 03-p02` to select a paragraph. After the parent authorizes the render, add `--render`; `--encoder libx264` is the CPU default, while `--encoder h264_nvenc` explicitly chooses the GPU. Existing outputs are protected unless `--overwrite` is requested.

The generated picture is 1920×1080/60fps without audio. All text is at least 48px; content ends before y876, leaving the full y892–1060 caption region clear. The compositor retains the approved narration, captions and final source-kind labels. Every receipt includes evidence and narration hashes, cue methods, source classification, text bounds and unverified review flags. Encoded dimensions, rate and frame count are checked after rendering; this does not replace actual moving/mobile review.

`--self-check` generates synthetic 32-second ASS timing solely for layout inspection and can never be combined with `--render`. Its receipts are explicitly marked `syntheticLayoutTest: true`, `timingVerified: false` and `motionReviewed: false`.

## Evidence boundaries

- Package values come from `planning/package-inventory.json`: 3,572 entries and 195 readable GDScript files. The diagram does not claim full binary decompilation or full project recovery.
- Mechanics are independently paraphrased from the hashed evidence in `planning/mechanics-findings.json`; queue drawings are illustrative states, not a reveal of the original recording's hidden shell order.
- The displayed 374 and 32 values are actual passed **assertion checks** in the independently written model and integration reports. They are not a claim that every original-game behavior was reproduced.
- Code excerpts come only from our `prototype/scripts/rules.gd` and `main.gd`. The colored line marker follows the currently narrated excerpt, not a fabricated runtime trace. Syntax colors remain separate from that marker.
- Original dealer item branches are identified as analysis of the original. The current prototype dealer only shoots; it does not reproduce the full original item strategy.
- Measured original-shot values are handled in the footage audit: the observed saw shot changes dealer HP **4→2**. The separate prototype/test fixtures must not be mislabeled as that recording.
