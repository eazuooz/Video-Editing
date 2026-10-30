# Exact ten-project local production

This batch is the explicit 2026-10-30 selection in `shorts-research-20261030-ten.json`. It starts no platform action and never treats technical completion as human review. Existing media, attempts and foreign jobs are preserved.

## Selected structure

- `batch.json` pins the exact ten candidates and local production boundary.
- `gpu-authorization.json` records the user's exact existing-Editor exception. The guard does not inherit the old Factorio exception or ignore arbitrary Unity/game processes.
- `scoped_context.py` supplies project paths, authorization, safe process metadata and resource checks.
- `template-sources.json` pins the reviewed Factorio speech/finishing algorithms by SHA256. `scoped_pipeline.py` binds them to a new project through thin wrappers, changes only documented path/title adapters, and records the used source/wrapper/context hashes. The old source project is never written.
- `run-batch.py` owns one exclusive finite-batch serial lock, logs each command separately, and reuses a passed stage only if all its output hashes still match.
- `motion-canvas/src/projects/tech-ten-shorts-20261030` composites independent game frames, actual native Unity frames, existing original Yamyam cat reactions, and three explicitly selected 2D mechanism models. The grid, EUD and replay models are authored illustrations/state simulations, never labeled Unity output or commercial internal buffers.

## Project files before production

1. `planning/production-plan.json`: actual evidence flags `scriptFinalized`, `independentFootageViewed`, `rightsAndFhdReady`; retain supporting sources/observations rather than setting flags from inference.
2. `sources/selected-footage.json`: current selected independent files, URLs, hash, decoded native FHD, observed cuts, rights and audio conditions.
3. `script/narration.spoken.ko.json`: `{slug, revision, scenes:[{id:'main', lines:[whole spoken paragraphs]}]}`; `narration.ko.txt` contains exactly the same prose without headings.
4. `script/caption-clauses.json`: `{clauses:[{id:'p1-1',lineIndex:0,spoken,ko,en}],pronunciationAliases:{}}`. Spoken clauses exactly cover each paragraph. `ko` may contain one intentional line break. `emphasis:{text,role}` optionally uses `term`, `result`, or `problem`; SRT remains plain. Display aliases do not authorize hiding an actual mispronunciation.
5. `production/section-plan.json`: array of `{id,paragraph,firstCue,purpose}`; paragraph indices are zero-based.
6. `publishing/metadata.json`: exact `title` and `description`, including required source/music credits at the bottom.
7. `production/visual-config.json`: `{slug,game,head:[two headline lines],term,english,plainMeaning,frameRoot,annotations?,catReactions?,diagramType?}`. Annotation keyframe times are **seconds local to the current section**, and centers/sizes are in original source pixels. Mark roles are focus/problem/result; marks clear at every cut.
8. `production/visual-pipeline.json`: scoped commands and artifact paths shown below.

```json
{
  "revision": "tech-ten-v1",
  "usesUnity": true,
  "prepareCommand": ["{PYTHON}", "-B", "-X", "utf8", "{ROOT}/production/batches/tech-ten-shorts-20261030/prepare-visual.py", "{SLUG}"],
  "nativeCaptureCommand": ["{PYTHON}", "-B", "-X", "utf8", "{ROOT}/production/batches/tech-ten-shorts-20261030/capture-unity.py", "{SLUG}"],
  "nativeCaptureReceipt": "{LOCAL}/unity-capture/native-receipt.json",
  "renderCommand": ["node", "{ROOT}/production/batches/tech-ten-shorts-20261030/render-one.cjs", "{SLUG}", "EXACT_UNIQUE_RENDER_NAME", "0", "{FRAMES}"],
  "visualOutput": "{LOCAL}/motion-canvas-output/EXACT_UNIQUE_RENDER_NAME.mp4",
  "renderReceipt": "{LOCAL}/EXACT_UNIQUE_RENDER_NAME-render.json",
  "codePaths": ["production/batches/tech-ten-shorts-20261030/render-one.cjs", "motion-canvas/src/projects/tech-ten-shorts-20261030/model.ts", "motion-canvas/src/projects/tech-ten-shorts-20261030/diagrams.tsx", "motion-canvas/src/projects/tech-ten-shorts-20261030/scene-factory.tsx", "motion-canvas/src/projects/tech-ten-shorts-20261030/vite.config.ts"]
}
```

The native receipt is `{success:true,voiceSha256,artifacts:[{path,bytes,sha256}]}`. Include current native scene/capture source paths in `codePaths`, as well as the project MC entries and visual-preparation code. Code fingerprints are inspected and explicitly recorded in `readiness.json`, never inferred from mere file existence.

## Timing and rendering

Actual TTS PCM → full unprompted ASR → exact clause matching → measured 60fps caption edges. No target-duration padding, guessed word times or hidden ASR replacements. The generated `visual-timing.json` is identical in `production/` and `production/local/`; it includes `revision`, `previewOnly:false`, `fps:60`, exact `frames`, `timingInputs.voiceSha256`, contiguous `sections`, and rights-backed `sources`. Each section carries `startFrame/endFrame/start/end`.

- `kind:'game'`: selected source ID, sourceStart/sourceEnd, rate1, nativeAudioAdopted flag and original source dimensions; use inspected frame folder and original aspect ratio. Footage opens each Short.
- `kind:'unity'`: actual native per-section frame folder, firstFrame0/digits5, width1080/height1080, `unityStage`0/1/2 and optional exact speech events.
- `kind:'diagram'`: `diagramType:'grid'|'eud'|'replay'`, `unityStage`0/1/2 is the explanatory state index; it is not a claim that Unity produced that diagram.

`frameDirectory` may be a relative folder under `config.frameRoot` or an absolute browser `/@fs/C:/...` directory. MC draws actual 1080-square Unity output proportionally in an800px square; full gameplay stays16:9 unless an inspected crop is explicitly supplied. The header occupies y0–440. Fixed final captions remain unchanged. The large cat uses the existing approved lower-right reserve, without covering technical objects.

`timing.events` keys may be section-scoped (`sectionId:eventName`) and contain exact startFrame/endFrame. Supported diagram events: grid-reveal, fine-grid, path-trace, request-travel, read-other-data, value-return, replay-run, move-command and attack-command. `timing.reactions`/config.catReactions list actual start/end seconds and kindrealize/relief. They must be deliberately authored; an empty reaction list does not fabricate completion.

## Inspected source annotations

`visual-config.json` may contain `sourceAnnotations`, keyed by the adopted source ID. Each mark has `start/end` in **file-local seconds**, `label`, `kind` (`box`, `ellipse`, `arrow`), semantic `role`, and observed `keyframes` with `at`, original decoded-pixel `center:[x,y]` and `size:[w,h]`. Source keyframes must cover the full mark interval; extrapolation is rejected. Do not substitute requested-download offsets for frame-exact original times when a source has keyframe preroll.

Optional `labelCenter:[x,y]` places the label away from UI; set it once on the mark for a fixed position or on every keyframe for inspected moving labels. `visible:false` on a keyframe hides an occluded target until a later visible keyframe. Use only directly inspected geometry and record its source-frame evidence on the mark.

Visual preparation intersects each mark with each actually used cut, interpolates boundary geometry within the observed keyframes, and writes `timing.annotations[sectionId]` in section-local seconds with source SHA/time provenance. Marks clear at every source cut, never carry into Unity/diagram sections, and disappear when their target geometry falls beyond source or display-crop bounds. The compositor maps both target and label from source pixels without altering the source image or branding. `test-source-annotations.py` exercises synthetic clipping/interpolation/visibility cases without producing media.

## Readiness and execution

From the repository root:

```powershell
& 'qwen3-tts/.venv/Scripts/python.exe' -B -X utf8 production/batches/tech-ten-shorts-20261030/run-batch.py
& 'qwen3-tts/.venv/Scripts/python.exe' -B -X utf8 production/batches/tech-ten-shorts-20261030/run-batch.py --resources
& 'qwen3-tts/.venv/Scripts/python.exe' -B -X utf8 production/batches/tech-ten-shorts-20261030/run-batch.py --slug SELECTED_SLUG --fingerprints
```

After reviewing code/inputs, put the emitted fingerprint object into `readiness.projects[slug].fingerprints` and set `codeReadyForActualProduction:true`. This is an internal implementation check, not another user approval loop.

```powershell
& 'qwen3-tts/.venv/Scripts/python.exe' -B -X utf8 production/batches/tech-ten-shorts-20261030/run-batch.py --execute --slug SELECTED_SLUG
```

`--through voice` stops after the requested existing stage. `--retry-failed` permits an inspected failed stage to run again; it does not overwrite mismatched media. Default validation performs no costly job. The runner stops on the first new blocker and preserves an existing lock, lease or server. On completion it produces clean/captioned/KO/EN plus hash-bound review artifacts. Full moving review, actual full listening, mobile inspection and human final approval remain explicit pending states until performed.
