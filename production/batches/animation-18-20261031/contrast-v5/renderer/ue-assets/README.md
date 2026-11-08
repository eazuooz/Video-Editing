# Editable A08 cumulative pose studies

These are only the20 newly authored UE5.8 assets (about1.77MB): four levels, four sequences, eight controlled animation variants and four capture configurations. No vendor mesh, skeleton or animation-pack assets are bundled here.

Keep the `Content/YamyamAnimationSeries/A08ContrastV5` relative path when copying this subtree into the existing GameAnimationSample project. Its installed UEFN mannequin and the engine primitives/materials must be available. The isolated production worker and full PNG captures remain at `production/batches/animation-18-20261031/local/contrast-v5/a08-cumulative`.

The editable study names are `flow`, `edge`, `stance` and `overview`. Each has its own saved Level and Level Sequence. They accumulate corrections on the same rig: head/torso, shoulders/arms/wrist, then pelvis/legs/feet. The first three compare the preceding retained state with the next corrections; overview compares the initial pose with the full accumulated result.

`prepare_a08.py` reproduces the pose definitions, and `capture_a08.py` uses the guarded isolated UE commandlet. The final root-height correction is documented in `a08-ground-calibration.json`; it keeps the supporting sole at the floor and is not a claim of physical mass simulation. `assets-manifest.json` records the saved asset hashes and the matching capture receipt.
