# Yamyam LOFI room — first Unity sample

Open this project with Unity **6000.6.0f1**, then open `Assets/LofiRoom/Scenes/LofiRoomSample.unity` and press Play. This is a separate lightweight project; the existing VideoEditing and LunaFortress projects are untouched.

- Imported Tripo H3.1 character, humanoid avatar, native Walk and Idle clips.
- Imported Tripo headphones on an authored gaming desk.
- Walk, rest, day/night, rain, camera and music controls.
- Walk translation consumes the imported animation's horizontal root displacement, clamped to route waypoints. No hand-authored joint waving replaces a missing clip.
- Runtime floor calibration uses the posed skinned mesh, rather than its bind-pose bounding box.
- Sitting, reading, detailed room decoration and the final browser game are not complete.

The Windows executable and 36-second 1080p60 video remain local under `projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1`. Keep the executable next to its `_Data`, DLL and runtime folders. The WebGL module/install/export was explicitly deferred by the user.

The official `com.unity.pipeline` package is included in the package manifest. Commands must specify this project path. The scoped MCP client is `projects/ai-3d-lofi-gaming-room/production/unity-mcp-client.py`.

Raw exports, additional texture maps, generated references and QA captures are local production evidence. The two BaseColor textures referenced by the scene are essential scene assets. Only BaseColor is currently connected; do not describe the sample as a finished PBR material workflow.

Music stays local under the repository's no-audio-in-Git policy: copy `sites/yamyam-cartographers-room/dist/music/01-morning-coffee.mp3` to `Assets/LofiRoom/Audio/morning-coffee.mp3` to restore it. The recording uses this same track.

Music: **Morning Coffee — HoliznaCC0**, CC0 1.0, from [Lo-Fi and Chill Collection](https://opengameart.org/content/lo-fi-and-chill-collection), [author](https://opengameart.org/users/holizna), [license](https://creativecommons.org/publicdomain/zero/1.0/). Other assets are original generated character/headphones and authored room geometry. Spirit City is an art-direction reference only; its assets and music are not used.
