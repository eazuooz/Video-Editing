# Production handoff — distinctive-ten-v1

This project is **producer-ready, not a completed video**. The approved Qwen voice is still waiting for the user's GPU/game boundary. Preserve source masters and old previews.

## Source and scene rebuild

From the repository root:

```powershell
node projects/shorts-rain-world-body-chunks/production/prepare-media.cjs
node projects/shorts-rain-world-body-chunks/production/render-visual.cjs NEW-VERSION FIRST-FRAME FRAME-COUNT
```

Replace the uppercase render placeholders with a lowercase version name and integer frame range. Without a range, the renderer uses `visual-timing.json`. **The active timing remains provisional until the actual-PCM preparation command succeeds.**

After the root producer has generated each project's approved PCM, `narration.timing.json` and `script/captions.json`, prepare all three in one command:

```powershell
python -X utf8 projects/shorts-noita-material-pixels/production/prepare-actual-visuals.py --all
```

Use `--slug shorts-rain-world-body-chunks` instead of `--all` to prepare this project alone. The helper validates current script/clauses/PCM hashes, actual paragraph starts, every canonical caption ID including added `b` clauses, genuine FHD originals, and exact 60fps frame coverage. It uses the captions' already-applied +0.20s voice offset and +0.40s tail; it never estimates duration from text. Meaningful state changes anchor to actual clause frames.

Every selected game source runs at native speed only until its inspected maximum cut length. If the spoken paragraph continues, a matching explanatory diagram carries the remaining narration. The helper writes a new fingerprinted source-frame directory and immutable actual-timing bundle, preserves prior active JSON bytes, then updates `production/visual-timing.json` and `production/local/visual-timing.json` identically. The latter includes the sources/sections and explicit native-audio exclusions consumed by the root mix pipeline. Existing previews, source masters and frame revisions are preserved. Source extraction is CPU FFmpeg; whole rendering and audio processing remain separate subsequent steps.

Code-only check (no PCM generation, media extraction or production timing mutation):

```powershell
python -X utf8 projects/shorts-noita-material-pixels/production/prepare-actual-visuals.py --self-test
```

The synthetic test passed frame coverage, finite-source overflow, event anchors, extra `b`-cue retention and invalid/stale input rejection. Shared composite and three scene entries passed syntax/transpile checks. **Actual-PCM preparation and final playback have not run.**

`YAMYAM_RENDER_PORT` selects the existing render server (default 9265). `YAMYAM_RENDER_OUTPUT_ROOT` must match that server's FFmpeg output directory; default is repository `shared/output/motion-canvas`. Root's new dedicated server is 9267 with C: output. Only one render may use a server/exporter at a time. A verified export is copied into this project's `production/local`, which now resolves to C:, and the new temporary exporter copy is removed only after SHA256 match. Existing versions are never overwritten.

`prepare-media.cjs` requires genuine source dimensions >=1920x1080 and refuses to overwrite incomplete frame folders. Changed in-points/crops use a new `frameDirectory`. The selected source manifest records source URL, rights basis, exact cuts, original dimensions/frame rate/hash and observations. Commercial gameplay sound is not silently substituted with unrelated audio: Noita source is natively silent; official Rain/Obra trailer soundtracks are excluded and the root producer must supply licensed BGM.

## Current evidence

- KO and EN clauses reconstruct each unchanged spoken paragraph; clause splits only improve subtitles.
- Editable Motion Canvas scene code exists and native 1080x1920 single-frame and three-second CFR60 render checks passed.
- Representative sequential source/render frames were actually inspected. This is not full moving playback, final listening or human approval.
- Cat diagrams shift left/up during the brief reaction, keeping material labels clear. Rain's current code fixes body/obstacle contact and uses full-FHD hook proxies for the closer crop.
- `motion-check-v2` is a preserved silent 3-second sample. Latest Rain fixes are also verified in the separately named single-frame files; v2 itself predates them.

## Still required

Approved voice generation; actual-audio section/cue timing; complete visual render; licensed BGM credit and final mix; clean/captioned MP4 and KO/EN SRT; complete decode/ASR plus real listening and full moving-picture/mobile review; final SHA256 delivery for the user's review. No YouTube, Drive, schedule, deletion or publication action has been performed or inferred.
