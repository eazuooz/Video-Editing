# M04 — Euler angles and axis–angle illustration assets

These are self-authored teaching illustrations, not Superflight footage or a measured flight model. The aircraft has a tapered body, cockpit glazing and frame, swept thick wings, tailplane and fin, intake/exhaust and independently hinged ailerons/elevator/rudder. No downloaded asset, fabricated detector result or physics measurement is used.

Canonical editor: **Unity6000.6.0f1**. Main project: **URP17.6.0** (existing PC quality setting). The disposable local capture project uses the **built-in pipeline**, linear color, two directional lights, no shadows or postprocessing. It changes only its own pipeline selection. White background preserves this lecture's approved style; semantic axes are X red, Y green and Z blue.

## Mathematical contract

All displayed equations are **right-handed, column-vector, local-to-world**. Forward is +z and up is +y. Intrinsic body Y–X–Z is `R = Ry(h) Rx(p) Rz(b)`, equivalent to extrinsic fixed Z–X–Y. Unity Euler values are never substituted for that equation.

`C = diag(1,1,-1)` reflects mathematical coordinates into Unity coordinates:

- `pUnity = C pMath`
- `RUnity = C RMath C`
- Authored mesh vertices use C and triangle winding is reversed.
- The converted matrix's forward/up columns produce the Unity quaternion. The physical nose was authored in math +z, therefore rests along Unity −z.
- +90° mathematical X sends +z to −y; +90° Y sends +z to +x. These, aliases, gimbal h−b and conversion round trips are explicit checks in the builder.

## Editable scenes and capture

`Scenes/` contains one independent scene per spatial lesson passage:03,04,06,07,09,10,12,16,18,19,21,22. `Shared/` holds reusable deduplicated geometry/material assets after actual isolated editor saving. Each scene has `EulerAircraftScene` with its own mode, camera, duration and normalized timeline. The context command **Build editable lesson objects** regenerates only that component's `Generated lesson geometry` child. It never auto-runs in the editor. Keep all `.meta` files.

The isolated project is under the selected video's `production/local/revision-v2/unity-capture`. `prepare-isolated-assets.py` copies only these owned Assets, existing Packages/lockfile and necessary ProjectSettings; no foreign Library/binary is copied. Its copied QualitySettings has unrelated pipeline asset references cleared. Existing Unity windows are preserved.

Explicit batch entrypoints are restricted to that isolated project:

- `EulerSceneAssetBuilder.BuildAndCaptureInIsolatedProject`: check math, bake all12 scenes, then execute the supplied finite sample job.
- `EulerCaptureBatch.Run`: capture only job-listed finite clips after compiling/importing.
- `-m04Job` points to a JSON with outputDirectory, explicit ffmpegPath and clips. Each clip has sceneId, fileStem, frames and either startNormalized/endNormalized or measured `keys: [{frame,normalized},…]`. Keys allow narration-aligned phases and hold frames without rendering an entire lecture.
- Actual capture is **1920×1080/60fps**, RGB24 direct pipe to x264/yuv420p, with vertical orientation corrected. No whole-lecture framebuffer sequence is written. Audio is composited later.
- `.anchors.ndjson` gives each frame's exact mathematical matrices, named aircraft points and body/world axis endpoints in top-left1920×1080 coordinates. `inFrame` means viewport visibility; it is not an occlusion detector. Parent compositing must verify occlusion and label clearance.
- Parent composites canonical terms, formulas and labels, reserving the fixed caption center960,970,48px,max2lines and lower clear band from approximatelyy890. The geometry is intentionally framed above it.

The current runtime layout places a single aircraft at pixel580,470, approximately650px wide, leaving x1050–1800 for large formulas. Paired comparisons use centers560,470 and1320,470, approximately500px each, with formula space near y780. The +Y guide may reach the upper-left band aroundy90: place the heading in the right pane or away from that axis. These are presentation translations, not extra physical motion or changes to the mathematical rotation. The original sample is a centered-camera visual-system check; this updated layout and revised narration profiles still need the one coordinated production capture/bake.

`prepare-capture-job.py --timeline <path>` accepts exactly `{ "scenes": [{ "id": "16", "frames": 1080, "seconds": 18, "lineStarts": [0,3,6,9,12,15] }] }`. Line starts are seconds relative to each scene and must match the current `production/revision-v2/lesson.json` line count. It emits a finite clip per narrated state/motion and a placement file giving exact start/end frames, source clip length and `holdFinalFrames`. Static diagram states need1rendered frame; they are held explicitly during their narration. A `resetAtCue` is an intentional comparison/reset, never a claim of continuous recorded flight.

After TTS and full source ASR release the GPU, the parent may explicitly run `run-isolated-capture.py --job <absolute job JSON> --bake`. It synchronizes only owned source assets into the warm isolated project, acquires its own cooperative lease, saves all12 current scenes, captures job-listed finite motions and releases the lease even on failure. `sync-baked-assets.py` then copies the editor-saved sources back to canonical Scenes/ while reducing identical mesh/material instances to shared assets. This has no automatic trigger.

No automatic full capture, installation, package upgrade, YouTube mutation or next-video work is performed by this asset package. See `scene-plan.json` and `baked-scene-provenance.json` for actual per-scene file and save status. Sample QA belongs to the selected video's existing review ledger.
