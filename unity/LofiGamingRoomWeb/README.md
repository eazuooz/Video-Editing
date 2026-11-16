# Yamyam LOFI room — PC atmosphere review

Open this project with Unity **6000.6.0f1**, then open **`Assets/LofiRoom/Scenes/LofiAtmosphereRoom.unity`** and press Play. The previous `LofiNatureRoom.unity`, original `LofiRoomSample.unity` and earlier review files are retained. This is a separate lightweight project; the existing VideoEditing and LunaFortress projects are untouched.

- Imported Tripo H3.1 character, humanoid avatar, native Walk and Idle clips.
- Imported Tripo headphones on an authored gaming desk.
- Walk, rest, day/night, rain, camera and music controls.
- Walk translation consumes the imported animation's horizontal root displacement, clamped to route waypoints. No hand-authored joint waving replaces a missing clip.
- Runtime floor calibration uses the posed skinned mesh, rather than its bind-pose bounding box.
- Nature v2 adds 311 curved leaves with stems/veins, hanging vines and window plants; wood/cloth/plaster surface detail; mug, tea, cables, fans, book and chair finishes; original forest-map artwork.
- Original 4096-pixel BaseColor exports and normal/roughness/metallic maps are connected in the custom URP material. Other map resolutions remain their genuine source resolution, not all 4K.
- The v3 loose-hair mask uses a five-node constrained chain with inertia, restoring force, length/angle limits and head/upper-shoulder collisions. The scalp and imported body motions are preserved.
- Walking uses native root displacement, 0.38s state blending, Humanoid foot IK and a continuous curved route instead of stationary corner swivels.
- Foliage uses size-scaled bending, pinned roots, spatially varying slow gusts and restrained tip flutter.
- A bounded depth-clipped light-scattering shader, shadowed four-pane window light, dust and restrained bloom provide the window-light effect. This is not a path-traced/global-illumination claim.
- A separate PC URP profile uses native 1.0 render scale, MSAA4, contact occlusion and a reflection probe. The previous 0.8 mobile-scale profile is retained for later platform tuning.
- PC shortcuts: **1 walk, 2 rest, 3 day/night, 4 rain, 5 music, 6 desk camera, 7 room camera, 8 breeze, 9 light shafts, 0 hair**. Breeze, shafts and hair also have on-screen comparison buttons.
- Sitting, reading and the final browser game are not complete.

The current Windows executable and 48-second 1080p60 video remain local under `projects/ai-3d-lofi-gaming-room/production/local/atmosphere-v3`, with review at http://127.0.0.1:9321/. Previous deliveries remain under `production/local/nature-v2` and `production/local/unity-sample-v1`. Keep the executable next to its `_Data`, DLL and runtime folders. The user explicitly deferred WebGL in favor of PC review. Its official module installer has only been downloaded and verified, not installed. PC quality settings need profiling and a separate fallback before the final browser build.

The official `com.unity.pipeline` package is included in the package manifest. Commands must specify this project path. The scoped MCP client is `projects/ai-3d-lofi-gaming-room/production/unity-mcp-client.py`.

Raw exports, generated references and QA captures remain local. The v1 BaseColor atlases and the nine v2 textures referenced by the scenes are essential scene assets. In v2, all four material inputs are actually connected. Do not describe the room as finished gameplay: sitting, reading and the full production video remain pending.

Music stays local under the repository's no-audio-in-Git policy: copy `sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3` to `Assets/LofiRoom/Audio/morning-coffee.mp3` to restore it. The recording uses this same track.

Music: **Morning Coffee — HoliznaCC0**, CC0 1.0, from [Lo-Fi and Chill Collection](https://opengameart.org/content/lo-fi-and-chill-collection), [author](https://opengameart.org/users/holizna), [license](https://creativecommons.org/publicdomain/zero/1.0/). Other assets are original generated character/headphones and authored room geometry. Spirit City is an art-direction reference only; its assets and music are not used.
