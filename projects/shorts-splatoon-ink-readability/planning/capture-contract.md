# Ink readability capture contract v1

Prepared source only. The controller, builder and capture entry point passed CPU C# compilation against the actual Unity6000.6 managed assemblies and URP17.6 runtime references with zero errors/warnings. The capture entry point has not been executed. No images, encoded video or capture readback exist from this source yet. Root owns GPU/process guards and serial launch.

## Isolated project and entry point

Copy the own source folder, relevant URP Settings assets, Packages/lockfile and ProjectSettings into the parent's isolated C: Unity project. Preserve GUIDs; do not change global pipeline/quality to Built-in. Current PC quality selects URP even with a null global pipeline. Job `expectedProjectPath` must exactly match that C: project. Output must be another empty C: directory, outside the isolated project. Keep an empty startup scene: capture refuses other loaded geometry instead of disabling or closing it.

Batch entry point: `YamyamCoding.Shorts.SplatoonInkReadability.Editor.InkReadabilityCapture.Run`. Pass `-inkReadabilityJob <absolute JSON path>` with `-batchmode -projectPath <isolated C project>`. **Do not pass `-quit`**: the finite `EditorApplication.update` capture loop exits on success/failure. GPU/no-graphics flags and launch timing belong to the parent. No source in this folder launches Unity automatically.

`scenePath` must be this lesson's saved scene under `Assets/VideoScenes/shorts-splatoon-ink-readability/Scenes/`. `buildIfMissing:true` explicitly runs the guarded builder if that scene does not exist. Otherwise a missing scene fails. Existing partial build outputs are preserved. A loaded editing scene with that path also fails. Capture opens a new additive instance, finds the actual saved controller/camera/references, verifies the imported material shader, calls `demo.Apply()` after loading and calls the stage method again for each captured frame. It never saves transient capture state or alters the baseline scenes.

## Frame and PCM contract

- `fps:60`, `totalFrames`: whole final PCM timeline length. All sections, cues and file numbers use that **absolute** timeline, starting at zero; intervals are `[startFrame,endFrame)`.
- Job `startFrame,endFrame`: capture only the authored part. For example, start at the historical/model transition after actual-game opening. The first JPG keeps that absolute frame number; there is no renumbering to zero.
- `mode:stills`: explicit unique `sampleFrames`, JPG only. Provisional timing is allowed and remains labelled `timingVerified:false`.
- `mode:sequence`: all frames in the capture interval. Requires `timingVerified:true`, actual `pcmPath`, matching `pcmSha256` and `timingEvidence` path/description. The source hashes the actual PCM before rendering; it does not infer ASR correctness.
- `sections`: ordered unique contiguous intervals covering the capture range. Each provides `id`, optional `visualId`, `stage`, optional `comparison` and `phase` tracks, term/step/label requests.
- `cues`: unique `{id,startFrame,endFrame}` records from actual PCM/ASR. No timing is inferred from text length inside Unity.

The sample `production/capture-job.preview.example.json` is deliberately a **stills-only 600-frame provisional coordinate example**, not a speech duration or production job. Change its project/output locations before use if the parent chooses other C: folders. Rebuild full sequence timing from actual PCM; do not promote these example timings.

## Stages and normalized tracks

| stage | `comparison=0` | `comparison=1` | fixed condition |
|---|---|---|---|
| `shading` | shade contribution1 | shade contribution0 | specular0.3 |
| `specular` | specular0.3 | specular3.5 | shade0.55 |
| `balanced` | shade0.55/specular0.3 | ignored | our illustrative preset |

`phase` controls the same deterministic diver/ring/droplet action from0 to1; omitted phase holds0.62. It is independent of comparison strength. For matched A/B, use the same scene/camera/resolution and **identical phase track and frame numbers** in two jobs, changing only the comparison value. These are our shader parameters, not measured Nintendo values, performance figures or a recovered game BRDF.

A track is `{from,to,ease,startCueId,endCueId,startFrame,endFrame}`. Values are normalized0..1. If `from==to`, it is constant and no anchors are needed. Otherwise `startCueId` resolves to that cue's start; `endCueId` resolves to that cue's exclusive end (omitting endCueId uses the same cue). If startCueId is empty, use explicit frame boundaries. No missing-cue fallback is permitted. `linear` and `smoothstep` reach `to` at the last frame before end; `step` switches at start. Before/after the interval the values clamp to endpoints. Section progress similarly ranges0..1 over its first/last frames.

## Motion Canvas handoff

Captured JPG path: `outputDirectory/frames/frame-%06d.jpg`, **absolute timeline frame**. JPEG dimensions are the job width/height; use native aspect. Recommended testbed is1920×1080 before portrait compositing. The alternate raw pipe encodes a silent `unity-explanation.mp4` with RGB24→vertical flip→H.264/yuv420p, preserving the interval's native60fps. Video local frame0 corresponds to job.startFrame. `encodeVideo:true` requires an explicit existing ffmpeg path; JPG and video may both be requested for a sequence. `writeJpg:false` avoids intermediate frame storage.

`readback.ndjson` contains one JSON record per successfully rendered/output frame: absolute `frame`, seconds, section/visualId/stage, section progress, normalized comparison/phase, **post-Apply `appliedState`**, canonical term, step list/current step, and `labelRequests`. These labels are requests to MC, never burned into the Unity pixels. Preserve the fixed heading/caption layout and clear labels at source cuts.

Label inputs: `{id,target,textKo,textEn,role,localOffset,startCueId,endCueId,startFrame,endFrame}`. Targets: `floor`, `wall`, `boundary`, `join`, `diver`, `splash`. Optional cue/direct-frame window limits visibility; no window means this section only. `localOffset` adjusts the known original testbed target in model units. The emitted anchor includes world point, top-left pixels `x,y`, normalized top-left `u,v`, depth, `inFrontAndInFrame`, and `targetActive`. Hide if either Boolean is false. **Occlusion is not ray-tested** (`occlusionVerified:false`); root must verify final moving annotations and hide at real occlusion. These are editorial anchors, not a detector or measured commercial-game data.

For a rendered picture rectangle with top-left `(left,top)` and size `(displayWidth,displayHeight)`, MC anchor is `(left+u*displayWidth, top+v*displayHeight)`. For a centered MC canvas subtract half the canvas dimensions after that mapping. Use the same letterboxing/crop transform as the picture; do not stretch coordinates independently. Useful roles: heading/warm yellow, concept/teal, changed value, problem/red, secondary/white. `steps` plus zero-based `activeStep` can drive the object-attached list; supplied `termEn,termKo,meaningKo` can drive the initial definition and persistent chip. Keep picture label `우리 Unity 모형` visible.

## Results and preservation

An empty output directory receives `job-used.json`, JPG/video as requested, `readback.ndjson`, and only after completion `success.json` with `render-completed-not-reviewed`. It records rendered count, graphics device, dimensions, timing status and output mode. This confirms execution, **not visual QA or human review**. Failure preserves partial output and records `failure.json`; rerun into a new empty directory. Existing output is never deleted/replaced. An optional `cancelFile` lets the parent stop this owned run. Only this run's ffmpeg child may be stopped during cleanup.

Root's exact sync back to D: should include only the lesson's generated editable source assets (`Scenes/*.unity` plus metadata, `Meshes`, `Materials`, `Prefabs`, any scoped Generated assets) and source metadata. Keep C: captures, compiler binaries, Unity caches and encoder outputs out of D:/Git.
