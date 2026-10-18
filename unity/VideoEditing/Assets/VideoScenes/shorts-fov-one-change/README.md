# FOV one-change — original Unity teaching scene

Owned source scene: `Scenes/FovOneChange.unity`. It is initially an editable
bootstrap with the `FovDemoScene` component. The first explicitly launched
isolated preview builds the complete original geometry, persists its materials
and generated meshes in `Baked/`, saves the full scene, and copies only those
owned text assets back here. Do not describe the bootstrap as a completed bake.

All vehicle, window, wheel, light, grille, bumper, road and tree arrangements,
and generated body/cabin/cone meshes are original Yamyam Coding procedural
assets. Unity built-in cube/cylinder primitives and the built-in Standard shader
are engine resources. There are no downloaded car models, textures, animations
or third-party asset licenses to infer. No model is intended to represent a
licensed real-world vehicle. This scene is an actual camera rendering, not a
mock Forza setting, detector output, measured commercial-game data or gameplay.

The camera stays at `(0,1.5,0)`, identity rotation, looking along world `+Z`,
with a fixed `1920x1080` / `16:9` viewport. The original center car is at
`(0,0,10)`; the blue/green side cars are at `(-9,0,11)` and `(9,0,11)`. The center
car includes a shaped body, hood, roof/cabin, windshield, rear/side windows,
mirrors, four tire/rim/spoke assemblies, grille, headlights, rear lights,
bumpers and a blank license plate. Approximate outside width is2.42m; the
projection report records the actual generated Renderer bounds.

Only horizontal FOV varies: `60 + 40*i/60` degrees for `i=0..60`. Unity's camera
property is vertical FOV, so the code uses
`Camera.HorizontalToVerticalFieldOfView(horizontal,16f/9f)` explicitly. There
is no animation time, object movement, camera dolly, crop or transform change.
The batch compares a complete hierarchy transform hash at every frame and
asserts that the side cars are outside60degrees and inside100degrees, while the
center car remains fully inside both viewports.

Rendering is built-in / Linear / Standard materials /4xMSAA / fixed directional
light and ambient light. The black background and lit asphalt/trees establish
spatial relationships without decorative glow, gradients or post-processing.
The canonical live editor's URP settings are not modified. Open this scene in
the documented isolated built-in project for the same material appearance.

Root-only commands, after inspecting the source and source/plan readiness:

```powershell
& 'D:/Github/VideoEditing/qwen3-tts/.venv/Scripts/python.exe' 'projects/shorts-fov-one-change/production/capture-unity.py' --preview
& 'D:/Github/VideoEditing/qwen3-tts/.venv/Scripts/python.exe' 'projects/shorts-fov-one-change/production/capture-unity.py' --capture
```

The runner creates only `projects/shorts-fov-one-change/production/local/unity-capture`,
using this folder's sources, Unity6000.6.0f1 and its already installed official
`com.unity.modules.physics:1.0.0` and `com.unity.modules.imageconversion:1.0.0`
built-in modules. Image Conversion supplies the actual PNG encoder. No external
package is added. The earlier own empty or Physics-only manifest is preserved
before the explicit upgrade; other dependency configurations are refused.
It never clones M04 or changes its captures, the live editor, package setup,
foreign GPU jobs or pause controls. It requires the exact selected Short,
refuses any existing GPU lease, requires at least2GiB free VRAM, owns its token,
starts hidden batch Unity and releases only its own lease in `finally`.

`--preview` produces only `output/preview/frame-000.png` and `frame-060.png`.
`--capture` produces only the finite61frames in `output/capture/`. Both modes
write `capture-projection.json` with actual camera FOV, fixed camera transform,
world bounds, un-clamped viewport bounds, top-left-origin pixel bounds and
anchors for `center`, `left`, `right`. Bounds are conservative projections of
actual MeshRenderer world AABBs; they are annotation guides, not segmentation
or occlusion measurements. PNGs, logs, jobs and QA evidence stay local and are
not Git assets. Persisted source `.unity/.cs/.meta/.mat/.asset` files are
eligible for selective source control.
