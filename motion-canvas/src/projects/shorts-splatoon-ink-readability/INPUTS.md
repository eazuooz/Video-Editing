# Actual-input compositor

This source has been strictly typechecked, not rendered. It fetches and hashes
the current files before constructing a scene. `inputsReady: false`, missing
PCM, preview timing, stale hashes or incomplete captures stop rendering.

The six source-order sections are `game`, `pbs`, `boundary`, `flat`, `specular`,
`close`. `production/clauses.json` contains29 display clauses; two splits retain
the original27-clause spoken content. `visual-timing.json` must provide every
clause ID, its actual ASR/PCM-linked frame bounds, contiguous paragraph sections,
and explicit voice0.20s lead and minimum0.40s tail. Nothing defaults to estimated
speech duration.

`production/prepare-actual-visuals.py prepare` writes this timing and a finite
capture job after actual voice/captions exist. Gameplay is native1920×1080/60,
within source66–68.2 and70–72.8, once at1×. Its two cuts end before `p1-3` and
within300frames. Additional opening speech uses our Unity model. Labels clearly
separate observed Splatoon3 from the historical Splatoon2 development case.

Unity uses1920×1080/60 and exact absolute timeline JPG indices. MC preserves
16:9 in a1000×562.5 picture at screeny620. No frame clamping, loops or freezes
hide missing sources. `readback.ndjson` carries applied shader parameters and
camera-projected labels. These values belong to our original demonstration,
never Nintendo's shader or a measured visibility/performance benchmark.

The current config holds nine inspected native-source `sourceFocus` keys.
Preparation maps them into actual timeline frames without extrapolation and
sets an explicit `focusWindow`. Surface glints are marked only66.25–67.5;
submerge splashes only70.000–70.250, before they disappear and the character
jumps back out. After actual native-motion and Unity-anchor review, pass
`capture-ready --native-reviewed --anchors-reviewed`.
The helper checks the exact job-used receipt, complete sequence and readback,
then binds five SHA256 inputs: timing, voice, readback, job, success. Manual
`hiddenLabels` frame intervals suppress projected labels during observed
occlusion. Visibility is not inferred from projection alone. The nine source
keys were reviewed in native1920×1080 stills; interpolation and final moving
playback are separate checks, still pending.

The external finishing header owns y0–440. Captions stay at their existing
fixed bandy1290–1470. Cat reactions occur at p1-4-b/p5-4/p6-7, below captions;
full-resolution labels remain outside that band. Native scene and moving375px
composite review remain necessary; typechecking is not visual approval.

Use only the own `vite.ink-readability.config.ts` server on127.0.0.1:9278 when
the parent explicitly reaches this serial stage. It keeps cache/output on C:.
No server or rendering starts on source import.
