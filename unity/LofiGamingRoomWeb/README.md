# Yamyam LOFI room — supported sofa and Tripo sleeping calico

The selected scene is **`Assets/LofiRoom/Scenes/LofiSofaRoomV10.unity`** in Unity **6000.6.0f1 / URP**. The v10 Web build succeeded with zero errors. Run `projects/ai-3d-lofi-gaming-room/production/local/living-room-v10/webgl` over HTTP; the canonical local review is http://127.0.0.1:9324/. Notes keep the existing browser storage keys. Previous scenes, captures and builds remain intact.

V10 uses an actual Tripo H3.1 sleeping calico generated from an image-AI-cleaned derivative of Am9489's CC0 [Calico Cat Asleep](https://commons.wikimedia.org/wiki/File:Calico_Cat_Asleep.jpg). Generation used 55 credits and Smart Mesh P1.0 retopology used 35; the imported mesh has 19,398 triangles. This is distinct from the older procedural cat. Base Color and Normal are connected; Metallic is zero and Smoothness is .08. Only subtle breathing is added, without claiming a generated cat rig.

Reading uses the CC0 [RG Poly Vintage Retro Stylized Pack](https://rg-poly.itch.io/vintage-retro-stylized-pack) sofa, scaled to 2.35m. A rounded back cushion and footrest support the existing native reclining body clip `Tourist_sit_03`. An Avatar Mask blends only the arms/fingers from `Tourist_sit_02_Map`. Book hand targets and elbow hints are fitted after those native clips. Entry and exit use KayKit sit/stand clips, with a path around the footrest rather than through it.

Restore the local FBX inputs using `production/cat-v10-import.json` and `production/sofa-v10-source.json` in the project. Their file hashes and original archive/library locations are recorded there. Model binaries, music, voice references and captured media stay local. The exact five newly referenced material textures are registered essential scene assets; unused exported maps remain local. Do not substitute a procedural animal when restoring the Tripo model.

Scoped tooling is `production/sofa-v10-tools.py`: `play`, `read`, `metrics`, `stop`, and `lofi_sofa_web_build`. Keep the project path explicit. The full tutorial v4, copyable requests and companion wiki are tracked separately from game-build completion and human final review.

## Preserved PC garden sample and implementation history

Open this project with Unity **6000.6.0f1**, then open **`Assets/LofiRoom/Scenes/LofiGardenRoom.unity`** and press Play. The previous `LofiHearthRoom.unity`, `LofiAtmosphereRoom.unity`, `LofiNatureRoom.unity`, original `LofiRoomSample.unity` and earlier review files are retained. This is a separate lightweight project; the existing VideoEditing and LunaFortress projects are untouched.

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

The preserved Windows executable and 48-second 1080p60 video remain local under `projects/ai-3d-lofi-gaming-room/production/local/garden-v5`, with review at http://127.0.0.1:9323/. Previous deliveries remain under `production/local/hearth-v4`, `production/local/atmosphere-v3`, `production/local/nature-v2` and `production/local/unity-sample-v1`. Keep the executable next to its `_Data`, DLL and runtime folders. The earlier WebGL deferral ended when the user installed the module; v10 now has an actual Web build and desktop-browser QA.

The official `com.unity.pipeline` package is included in the package manifest. Commands must specify this project path. The scoped MCP client is `projects/ai-3d-lofi-gaming-room/production/unity-mcp-client.py`.

Raw exports, generated references and QA captures remain local. The v1 BaseColor atlases and the nine v2 textures referenced by the scenes are essential scene assets. In v2, all four material inputs are actually connected. These historical notes describe the PC interaction sample; consult the v10 section for the current game and current material connections.

Music stays local under the repository's no-audio-in-Git policy: copy `sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3` to `Assets/LofiRoom/Audio/morning-coffee.mp3` to restore it. The recording uses this same track.

Music: **Morning Coffee — HoliznaCC0**, CC0 1.0, from [Lo-Fi and Chill Collection](https://opengameart.org/content/lo-fi-and-chill-collection), [author](https://opengameart.org/users/holizna), [license](https://creativecommons.org/publicdomain/zero/1.0/). Fire sound: [Fireplace Sound loop — PaGDev](https://opengameart.org/content/fireplace-sound-loop), CC0. [KayKit Character Animations](https://kaylousberg.itch.io/kaykit-character-animations) are CC0; the owned [EmacEArt PHILIPP](https://emaceart.itch.io/philipp-stylized-modular-low-poly-character) reading clip permits personal/commercial project use and stays local under its asset license. See `production/hearth-v4-asset-record.json` for provenance. Other assets are original generated character/headphones and authored room geometry. Spirit City is an art-direction reference only; its assets and music are not used.

V5 lowers and narrows the chair back without changing seat contact, lowers the display by 13 cm, and adds an original upright three-layer forest/moon panorama with day/night colors. Leaf wind amplitude increases from .028 to .085; hair keeps its length/head/shoulder constraints with stronger breeze and a 12 cm displacement cap.

Press **N** or **메모** for a multiline Korean note. It autosaves after 0.7 seconds, also flushes on focus loss/quit, and restores on reopening. JSON storage uses Unity's [Application.persistentDataPath](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/application/persistentdatapath): on this PC, `C:/Users/1/AppData/LocalLow/YamyamCoding/Yamyam Lofi Room/room-memo.json`. Temporary-file replacement and `.bak` recovery preserve the previous saved copy. A save failure remains visible and does not clear the input. The former room PlayerPrefs note is migrated without deleting that key. No network transmission is involved. Native QA uses `-lofi-memo-store <isolated directory>` to keep the user's normal note untouched. Memo mode suppresses game keyboard shortcuts and record-player world clicks. Web persistence is deferred with the WebGL build.

Current selected revision, 2026-11-18: **v11 wood/woven furniture and sleeping-cat motion**. The retained v10 game remains at <http://127.0.0.1:9324/>. The actual Tripo cat's localized chest breath and small tail motion can be inspected in the 12-second FHD60 [native sample](http://127.0.0.1:9330/); its face/forepaws stay anchored. This is mesh deformation of the original generated model, not a replacement cat made from primitives or a generated skeletal rig.

The matching sofa and low table are completed Tripo H3.1 jobs (90 credits each, generation plus retopology). Their normal FBX/Mixamo/4K ZIP downloads await the user after Chrome returned `ERR_BLOCKED_BY_CLIENT`; no protection bypass was used. Import the two actual ZIPs with `production/import-rattan-v11.py`, then call `lofi_rattan_prepare` through the official project-scoped Unity CLI MCP. The target scene is `Assets/LofiRoom/Scenes/LofiRattanRoomV11.unity`. Verify native sit/stand, heel/table clearance and book/palm contacts before recording or building. A successful code compile does not establish those visual contacts.

`lofi_sofa_entry_record` records the single continuous approach → sit → lift feet onto the table → raise book sequence. `lofi_living_record` records the wider 90-second feature source. The complete tutorial v5 has 31 same-reference local Qwen3 voice paragraphs and 249 KO/EN caption cues ready; full final rendering awaits these actual furniture captures. Preserve the older game/film outputs. The selected delivery boundary remains local full review before a new YouTube upload or public website release.
