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

### Bounded ASR orthography review

A raw ASR mismatch stays false in its original immutable report. The runner may accept a separately reviewed `audio-v1/asr-reconciliation.json` (or `asr-mix-reconciliation.json`) only when the **complete** normalized text matches after the documented orthographic changes. The existing caption algorithm reads the same voice reconciliation and retains each application in its alignment evidence. This does not complete pronunciation, full listening or playback review.

Required receipt fields: `status:'reviewed-orthography-only'`, `role`, exact `inputSha256`, `voiceSha256`, `asrSha256`, `scriptSha256`, `unresolvedCount:0`, `unresolved:[]`, `rawAsrPreserved:true`, `actualListening:'pending'`, `humanListening:'pending'`, nonempty `aliases`, `changes` and `independentEvidence`. Each change contains exact `source`, `target`, `kind`, explanatory `reason`, positive `occurrences` and `evidenceIds`. The basic accepted kinds are `mesh-loanword-orthography` (`메쉬` → `메시`, other characters identical) and `contextual-possessive-pronunciation` (one `에` → `의`, with both surrounding contexts retained). Names, semantic replacements, missing words and unresolved cases cannot be accepted through this path.

Each independent evidence record has a unique `id`, `path`, `sha256` and an unmodified, unprompted recognition report. Normally it binds the current voice hash. Evidence from a preserved prior voice additionally requires hash-bound `sourceVoice`, `priorLineLevels`, `currentLineLevels` file records and `unchangedParagraphs:[{lineIndex,evidenceParagraphId}]`. The validator checks the old crop sample bounds and current raw/normalized paragraph files against both assembly receipts. This lets an unchanged paragraph retain its evidence after another paragraph is repaired; it cannot carry evidence across changed PCM. All referenced files become validated artifacts/dependencies. A new receipt never changes the source recognizer's flags or claims human listening.

Regenerated FLOAT WAV containers can differ solely because libsndfile writes a new `PEAK` creation timestamp. If normalized file hashes differ, the paragraph selection must additionally identify its preserved `priorNormalizedTake:{path,sha256}`. Both file hashes still must match their respective assembly receipts; the WAV format and complete mono24kHz IEEE FLOAT32 data chunks must then be exactly equal, and the sample hash must equal the independent recognizer's original crop hash. No numerical tolerance or sample modification is permitted.

`test-asr-reconciliation.py` uses isolated synthetic fixtures to check bounded acceptance and rejection of wrong voice, raw/evidence tampering, unresolved or name substitutions, incomplete content coverage and changed reused PCM. It performs no media production.

The Grid episode additionally permits only two full-context Korean homophone cases after independent unprompted evidence: `이 스타크래프트 달이, 대각선으로 놓여 있죠.` → `이 스타크래프트 다리, 대각선으로 놓여 있죠.` (liaison yields the same /다리/), and `같은 넓이의 가로 네 칸` → `같은 넓이에 가로 네 칸` (context establishes the authored locative). Neither enables a general noun/name alias or a global 의/에 swap. An independent decoder may spell either exact homophonic form; the original report remains untouched and actual listening remains pending. Separately recorded Grid display/speech aliases32/8/4/16 preserve the exact authored quantities. They do not replace the voice or rewrite the raw recognition report.

The EUD episode has two further exact-context cases, independently recognized from the current unchanged paragraph PCM: `새 게임 사이의 통역기를 둔다면 어떨까요` → `새 게임 사이에 통역기를 둔다면 어떨까요`, and `그 값을 찾아 주는 시기죠` → `그 값을 찾아 주는 식이죠` (the latter shares the pronounced /시기죠/). These do not enable arbitrary particles, noun substitutions or name corrections. Numeric ASR fragments for the authored patch number `1.21.0` are recorded separately as display/speech tokenization, with the original full recognition and word chunks retained. Neither recognition nor reconciliation is actual full listening.

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

## Final review collection

`build-review-overview.py` reads the ten current manifests, delivery receipts, publication metadata and successful final pipeline stages. It verifies all four files against their recorded hashes and writes only the owned local `delivery/` review page and immutable JSON snapshots. Run with `--require-all` for the final ten-video handoff. It neither marks human approval nor changes a project, pipeline stage or platform. Individual sampled visual reviews remain in each project's existing review ledger; full listening and real-time playback are not inferred from a contact sheet or technical checks.

After all seven native captures have current successful receipts, use `native-export-tools/usage.md` to preserve independently editable scene versions and their exact captured source snapshots. Export-time dependency evidence is separate from capture-time hashes. Do not install the export helper into an active capture source tree or the user's open Unity project.
