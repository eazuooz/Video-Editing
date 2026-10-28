# D25–D30 Unity explanation revision

The user approved the previous story and order, then requested improvements to text-heavy explanations in all six delivered videos using the imported Unity asset library. This is a finite visual revision, not authorization for a new episode or platform action.

## Preservation

- `authorization.json` freezes the 24 previous deliverable files. The previous delivery directories remain intact.
- Narration, mixed AAC including Nimbus music, Korean/English subtitle bytes, gameplay source cuts, timeline clocks, branding and the silent membership link ending are reused.
- Only explanation visuals change. An existing useful game screenshot or demonstration may remain where it directly explains the point. Our Unity scenes remain explanation footage.
- Current revised versions require new human review. Previous praise for story/order is recorded separately from viewing these new files.

## Editable Unity sources

Project: `unity/VideoEditing`, editor `6000.6.0f1`, its existing URP configuration. The user's ShopSample scene is preserved while each owned cut is built in an additive scene and closed after capture.

Each selected explanation cut is saved independently at `Assets/VideoScenes/<slug>/unity-visual-v2/<cutId>.unity`. These files contain the editable camera, lighting, imported object instances and labels at the initial pose. Shared vendor originals are unchanged. Deterministic movement, rig sampling and speech cues are authored in the three `D25D26Stage`, `D27D28Stage`, `D29D30Stage` classes under `Assets/VideoScenes/design-25-30-unity-v2`. Use the capture/rebuild bridge to reproduce their timed animation; simply opening the saved initial-state scene is not a timed playback test.

`asset-provenance.json` and each project's visual plan identify exact asset paths, GUIDs, source/license evidence and scene roles. Generated screenshot textures stay local, with `.source.json` provenance and `.meta` GUIDs in source control. Rebuild them from their recorded independently obtained source screenshots when restoring on another computer. No raw vendor package or media is redistributed in Git.

## Capture and version proof

`freeze_sources.py` writes separate compiled fingerprints for the three scene classes. Refresh the already-open Unity editor after changing a class. `run_capture.py` requests only the selected cut(s) and refuses stale inputs. The editor waits until the request's fingerprint matches the compiled code, then returns the assembly identity, native frame count, scene path and actual used assets/animations.

Preflight uses seven states per cut, with optional exact frame samples for short events. Earlier v2 preflights were diagnostic: their stale compiled-code discrepancy was found and corrected before final capture. Use current project review records for the final approved internal sample set.

All media and QA rasters are stored in `C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028`. Costly captures/encodes run sequentially. Final pair assembly reuses baseline AAC packets and preserves exact 60 fps clocks. Human full-video review remains pending until explicitly received.

## Continuous animation correction

Final native-video inspection found that several D26 clip transitions retained the preceding skeletal pose even though sparse preflight images were correct. `pose-sequence-repair/repair.json` records the direct decoded evidence and controlled correction. The common stage now collects pose requests and samples the last requested pose once per actor/frame. D26 is recaptured in `render/v6` and recomposited separately; failed v5 outputs remain diagnostic only.

Unchanged completed captures in the other five projects retain their actual compiled-source fingerprints, including the exact common-source snapshots in `pose-sequence-repair`. Their reviewed output is not relabeled as a new render. Project records distinguish sampled motion proof, complete stream checks and pending human review. New renders use the corrected common stage; any historical reproduction must consult the source version recorded in its native receipt.

## User gaming / background control

The user asked to use Unity MCP/CLI-style control without screen interaction, then said they were starting a game. Prefer an available Unity connector or this project's existing editor file-request bridge for scene work and capture; do not assume an MCP connection exists. All six final encodes were already finished at that point. Remaining work is bounded CPU file verification, inspection of saved frames, collection and Git. Do not activate windows, operate the mouse/keyboard, refresh the user's editor through its UI or launch a new GPU job while the user is gaming. Defer a newly discovered GPU correction instead of interrupting the game. Saved-image QA does not require desktop control.
