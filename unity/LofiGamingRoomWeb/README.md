# Yamyam LOFI room — PC activities and hearth review

Open this project with Unity **6000.6.0f1**, then open **`Assets/LofiRoom/Scenes/LofiHearthRoom.unity`** and press Play. The previous `LofiAtmosphereRoom.unity`, `LofiNatureRoom.unity`, original `LofiRoomSample.unity` and earlier review files are retained. This is a separate lightweight project; the existing VideoEditing and LunaFortress projects are untouched.

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
- V4 adds licensed KayKit chair entry/idle/exit and EmacEArt reading, with queued walk–align–sit–read/computer–stand transitions. Humanoid IK fits hands, feet and seat contact. Computer use has keyboard contact, not newly captured finger typing.
- A smaller oak desk has one iMac-style all-in-one. Two tiers of bookshelves sit on both sides of a stone hearth, with layered flame, ember and smoke particles, warm light variation and a separate CC0 crackle loop.
- A small table under the window holds a walnut record player. Music playback drives its platter at 33⅓ rpm and moves the tonearm. Click the player to pause/resume; on-screen controls independently adjust music and fire sound. **C computer, B read, V stand** supplement the existing shortcuts.

The current Windows executable and 72-second 1080p60 video remain local under `projects/ai-3d-lofi-gaming-room/production/local/hearth-v4`, with review at http://127.0.0.1:9322/. Previous deliveries remain under `production/local/atmosphere-v3`, `production/local/nature-v2` and `production/local/unity-sample-v1`. Keep the executable next to its `_Data`, DLL and runtime folders. The user explicitly deferred WebGL in favor of PC review. Its official module installer has only been downloaded and verified, not installed. PC quality settings need profiling and a separate fallback before the final browser build.

The official `com.unity.pipeline` package is included in the package manifest. Commands must specify this project path. The scoped MCP client is `projects/ai-3d-lofi-gaming-room/production/unity-mcp-client.py`.

Raw exports, generated references and QA captures remain local. The v1 BaseColor atlases and the nine v2 textures referenced by the scenes are essential scene assets. In v2, all four material inputs are actually connected. The full game and production video remain pending; this is the PC interaction sample.

Music stays local under the repository's no-audio-in-Git policy: copy `sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3` to `Assets/LofiRoom/Audio/morning-coffee.mp3` to restore it. The recording uses this same track.

Music: **Morning Coffee — HoliznaCC0**, CC0 1.0, from [Lo-Fi and Chill Collection](https://opengameart.org/content/lo-fi-and-chill-collection), [author](https://opengameart.org/users/holizna), [license](https://creativecommons.org/publicdomain/zero/1.0/). Fire sound: [Fireplace Sound loop — PaGDev](https://opengameart.org/content/fireplace-sound-loop), CC0. [KayKit Character Animations](https://kaylousberg.itch.io/kaykit-character-animations) are CC0; the owned [EmacEArt PHILIPP](https://emaceart.itch.io/philipp-stylized-modular-low-poly-character) reading clip permits personal/commercial project use and stays local under its asset license. See `production/hearth-v4-asset-record.json` for provenance. Other assets are original generated character/headphones and authored room geometry. Spirit City is an art-direction reference only; its assets and music are not used.
