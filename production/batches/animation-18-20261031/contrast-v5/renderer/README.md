# Animation contrast revision: explanation plates

Selected scope: A01, A02, A04–A18. A03 is rejected by the source adapter and is not included in either range export. Parent owns commercial gameplay, narration changes, full assembly, review links, control/worklist and Git.

## What is rendered

`compose.py` produces 1920×1080 RGB frames from existing actual Unreal captures. Comparison variants share a source crop and pixel scale. A representation or camera comparison is labeled as such; it is not presented as a different animation. Face, hand and elbow demonstrations use close crops. The stages panel shows actual frames of the same study. Head curves, blend weights, collision capsules and joint paths come from the saved authored inputs/pose tracks, not invented commercial-game telemetry.

`frame(episode, key, source_frame, mode='compare')` supports native, compare and stages modes; A02 also has screen-size mode. Native passes retain the existing pacing plan's pass indices. Where two inserted passes precede the first body pass, that body's normal-speed portion is kept once; later explanation cuts use slow analysis instead of repeatedly restarting unannotated normal playback. Existing relation maps and body repairs are protected.

A08 now uses one actual editable pose. Its head/torso, arm/wrist and pelvis/leg corrections accumulate on the same rig, camera and lighting. A new isolated UE project captured four 180-frame studies. The final feet initially penetrated the floor; `a08-ground-calibration.json` records observed sole pixels and the corresponding orthographic root-height correction. This is a placement correction, not a centre-of-mass simulation. Existing external editors/assets were not modified. `a08-capture-plan.json` and the local capture receipt identify the precise source inputs.

## Entry points

```powershell
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/prepare.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/validate.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/render_rows.py --episodes A01 A02 A04 A05 A06 A07 A08 A09 A10 A11 A12 A13 A14 A15 A16 A17 A18
```

One CPU worker, four encoder threads, no GPU encoding or audio. Rendering checks current explicit authorization. Existing outputs are reused only when the current code, row, source signature and output SHA match. Source signatures include metadata, five actual PNG hashes and all sequence file sizes/mtimes; they are not described as full sequence hashes.

`replacement-plan.json` has 444 explanation ranges. `frameStart/frameEnd` refer to the original authoring timeline, `pacingFrameStart/End` to pacing-v3, and `relationFrameStart/End` to relations-v4. End frames are exclusive. Insertions have explicit anchors. Parent can rebase them after its new game/speech edits. Each output has a sibling receipt with exact frames, dimensions, fps, no-audio confirmation and SHA256.

`export_game_ranges.py` separately exports all 594 existing gameplay ranges in `game-baseline-ranges.json`. An independently built frame mask matches each current assembly's `actualGameplayFrames`; relation maps, repairs and authored demonstrations are excluded. Native gameplay repeat labels and normal source clocks are retained. This export is metadata only and does not approve the old or new game sources.

## Checks and honest limits

`validation.json` verifies saved FK points against available motion evidence and A15's actual stepped/continuous hand tracks: same endpoints, one stepped change at frame65, continuous intermediate changes, identical non-finger tracks. A05's impact comparison uses adjacent actual frames75/76 rather than mislabeling two arbitrary poses as one frame apart.

Source previews were inspected at 1080 and approximately375px. The A02 7.25-second encoded sample uses the real current ASS and its exact relations-v4 clock; decoding and sampled1080/375 inspection passed. Other source previews use a caption placeholder, not a claim of final caption review. `encoded_audit.py` samples completed output plates and records its exact coverage. Full integrated audiovisual review and current changed captions belong to parent assembly. No human listening/full-watch approval is inferred from these checks.

All generated guide lines are editorial aids on actual authored poses. Colours are explained at first appearance. The fixed caption area starts at y920 and stays clear. The output does not fabricate hit-stop, live detector confidence, commercial-game collision measurements, physical forces or animation authoring history.

## Final completion passes and integration precedence

After the single base-render worker completes, run these sequentially on CPU:

```powershell
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/a15_complete_repeats.py --render
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/complete_observation_results.py --render
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/clean_legends.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/complete_blend_bounds.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/collect_delivery.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/assemble_integration_manifest.py
python -X utf8 production/batches/animation-18-20261031/contrast-v5/renderer/encoded_audit.py
```

Use **integration-manifest.json** for final assembly once it exists. It resolves all overrides into one list. Do not independently apply the base list again. All baseline ranges still use the original relations-v4 clock.

A15's old music-only214-frame observation window becomes444 frames: source0–129 at1× plus18-frame end hold, three times. The actual continuous fingers finish changing by122F. The old body portion that supplied an incomplete third pass becomes narrated slow analysis without changing its duration or PCM. This is the only length change here: +230frames, or3.8333seconds. Parent must carry music across that window and shift later old-clock material once alongside its own gameplay/speech edits. The final finger stage uses130F.

A08's overview must reach the accumulated completed pose at171F, including the legs. Its chapter02/08 comparisons hold that completed pose, chapter07 presents the four actual stages, and the opening progressively reaches it. A06's input-recovery comparison reaches72F. These are same-length visual overrides.

The generic current/previous/path colour key is correct for A02 and retained there. Other studies use different marks (head-height, planted feet, facial controls, weight tracks), so their generic key is removed from the empty top strip; their actual per-picture labels, marks and charts remain. `legend-corrections.json` records the exact48-pixel strip filter and source/output hashes.

The final encoded middle-frame inspection found A14's blended foot briefly outside the crop chosen from seven samples. `complete_blend_bounds.py` measures all180 captured frames per blend study and re-renders only those A14 rows with a shared expanded crop. Original source pixels, weights and motion remain unchanged. The source itself has no foot-lock IK; the reference line and the resulting foot movement are preserved, not cosmetically corrected. `blend-crop-corrections.json` has final precedence for these rows.

The editable A08 assets are preserved under `ue-assets/Content/YamyamAnimationSeries/A08ContrastV5`, with20 matching saved assets and no copied vendor dependencies. No shared control, worklist, platform record or Git commit is changed by these scripts.
