# Ink readability — URP source prepared and C# checked

This is an original teaching model for the selected Splatoon 2 ink-readability Short. It is **not Nintendo's shader or a reconstruction of its exact implementation**.

The controller, editor builder and capture entry point passed a CPU-only Roslyn compilation against the installed Unity 6000.6.0f1 managed assemblies and cached URP 17.6.0 runtime assemblies, with zero errors or warnings. No Unity Editor, shader compiler, builder, rendering or capture ran. No `.unity` scene, prefab, material or mesh has been generated yet. See `projects/shorts-splatoon-ink-readability/production/unity-code-validation.json` for builder/controller evidence, and `production/unity-capture-code-validation.json` for the capture source.

## Pipeline and preservation

PC quality (index 1) overrides the null global pipeline with `Assets/Settings/PC_RPAsset.asset`, a UniversalRenderPipelineAsset. The earlier inference that a null global setting meant Built-in was incorrect. The shader now targets URP with `UniversalForwardOnly`, `DepthOnly` and `DepthNormalsOnly` passes. The last two support the current deferred renderer's depth/SSAO configuration; they do not add lighting to our authored material calculation. Global graphics and quality settings are untouched.

After the parent's serial production checks, `InkReadabilityBuilder.Build` can create one shared testbed prefab and five independently editable scene variants. It checks all 13 output paths plus their `.meta` files before any folder/asset/scene change, rejects partial existing builds, and repeats the check before each write. It creates an additive scene, restores the previously active scene, closes only the scene it created and saves only its own assets. It does not call global `AssetDatabase.SaveAssets`. It refuses to run while Overwatch is present or the effective quality/default pipeline is not URP.

## Comparison contract

The same raised floor, wall, two ink colors, camera, light, mannequin and splash geometry persist across comparisons. `SetShadingComparison` varies only shade contribution; `SetSpecularComparison` varies only specular contribution. Both accept the same deterministic submerge phase for matched A/B playback. Restore the shared baseline between comparison families. “Balanced” is our illustrative preset, not the shipped game's settings.

The shader uses a small direct-light GGX calculation with explicit artistic multipliers. It does not implement full global illumination, shadow maps, Nintendo paint attachment, game logic, networking or performance measurements. Shader compilation and actual visual readability are pending; check real rendered samples before treating any comparison as successful.

Unity asset-library documentation and inventory were consulted. The narrated objects are plain floor/wall surfaces and a neutral diver stand-in, so these are original geometry; no vendor materials, characters, rigs or Nintendo assets are copied. Source article images remain research-only outside Git.

Output captures belong on the project's C: media root, not inside these source assets. Parent records: `projects/shorts-splatoon-ink-readability/planning/production-plan.json` and `production/checkpoint.json`.

## Finite PCM/cue capture

`InkReadabilityCapture.Run` is a prepared explicit batch entry point; it has never been invoked. Its job format, C: isolated-project requirements, still example, frame numbering, applied-state trace and MC label mapping are documented in `projects/shorts-splatoon-ink-readability/planning/capture-contract.md`. Parent owns launch/GPU scheduling; pass `-inkReadabilityJob` and omit `-quit`. New captures require a fresh empty output folder. Capture calls the real controller after scene loading and per frame; it does not infer rendered evidence or human review from code preparation.
