using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Yamyam.LevelDesign.RhythmRunner;

namespace Yamyam.LevelDesign.RhythmRunnerV2.Editor
{
    public static class RhythmCourseBuilderV2
    {
        public const string Folder = "Assets/VideoScenes/architectural-111-20261106/13-02-RhythmCourseV2";
        private const string Knight = "Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
        private const string Surface = "Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader";

        [MenuItem("Yamyam/Level Design/Build 13.02 articulated rhythm scenes V2")]
        public static void Build()
        {
            string[] paths = { Folder + "/P03-RegularRhythm.unity", Folder + "/P04-OneShiftedObstacle.unity" };
            if (paths.Any(File.Exists)) throw new InvalidOperationException("Preserve existing editable V2 scenes.");
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Knight);
            var shader = AssetDatabase.LoadAssetAtPath<Shader>(Surface);
            if (!prefab || !shader) throw new InvalidOperationException("The verified CC0 Knight and shared surface are required.");
            var clips = AssetDatabase.LoadAllAssetsAtPath(Knight).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__", StringComparison.OrdinalIgnoreCase) &&
                    (c.name == "Walking_A" || c.name.EndsWith("|Walking_A", StringComparison.Ordinal))).ToArray();
            if (clips.Length != 1 || clips[0].empty || clips[0].length <= 0)
                throw new InvalidOperationException("One actual non-preview Walking_A clip required.");
            Directory.CreateDirectory(Folder);
            AssetDatabase.Refresh();
            var track = MaterialAsset(shader, "Track", new Color(.19f, .26f, .29f));
            var baseline = MaterialAsset(shader, "Baseline", new Color(.29f, .83f, .64f));
            var changed = MaterialAsset(shader, "Changed", new Color(.96f, .43f, .31f));
            var pulse = MaterialAsset(shader, "Input", new Color(1, .84f, .41f));
            for (int sceneIndex = 0; sceneIndex < paths.Length; sceneIndex++)
            {
                bool compare = sceneIndex == 1;
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
                var root = new GameObject(compare ? "P04 - one delayed obstacle" : "P03 - regular rhythm");
                SceneManager.MoveGameObjectToScene(root, scene);
                var player = root.AddComponent<RhythmCoursePlaybackV2>();
                player.comparison = compare;
                player.walkingClip = clips[0];
                player.baselineRunner = Lane(root.transform, compare ? 1.5f : 0, false, prefab, track, baseline, out player.baselineModel);
                player.baselineInput = Marker(player.baselineRunner, "Jump input", 1.05f, pulse);
                if (compare)
                {
                    player.delayedRunner = Lane(root.transform, -1.5f, true, prefab, track, changed, out player.delayedModel);
                    player.delayedInput = Marker(player.delayedRunner, "Same jump input", 1.05f, pulse);
                    player.delayedCollision = Marker(player.delayedRunner, "Own model collision", .95f, changed);
                }
                var cameraObject = new GameObject("Native 1920x1080 explanation camera", typeof(Camera));
                cameraObject.transform.SetParent(root.transform, false);
                cameraObject.transform.localPosition = new Vector3(3, 0, -15);
                var camera = cameraObject.GetComponent<Camera>();
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
                camera.orthographic = true;
                camera.orthographicSize = 4.2f;
                camera.aspect = 1920f / 1080;
                player.cameraRig = cameraObject.transform;
                Label(cameraObject.transform, "Own implementation (자체 구현)", -6.6f, 3.9f, .07f);
                Label(cameraObject.transform, compare ? "같은 속도 · 같은 입력 / 마지막 장애물 위치만 변경" : "일정 속도 · 일정 간격 · 성공 순간의 음", -6.6f, 3.45f, .07f);
                Label(cameraObject.transform, "기준", -6.6f, compare ? 2.8f : 1.5f, .085f);
                if (compare) Label(cameraObject.transform, "비교", -6.6f, -.3f, .085f);
                player.Initialize();
                player.ApplyFrame(0);
                if (!EditorSceneManager.SaveScene(scene, paths[sceneIndex]))
                    throw new InvalidOperationException("Unity scene save failed.");
                EditorSceneManager.CloseScene(scene, true);
            }
            AssetDatabase.SaveAssets();
        }

        private static Transform Lane(Transform root, float laneY, bool shifted, GameObject prefab,
            Material track, Material actor, out Transform model)
        {
            var lane = new GameObject(shifted ? "Last obstacle moved" : "Regular obstacle spacing").transform;
            lane.SetParent(root, false);
            lane.localPosition = new Vector3(0, laneY, 0);
            Geometry(lane, "Course surface", new Vector3(14, -.085f, 0), new Vector3(32, .17f, .55f), track);
            for (int i = 0; i < 4; i++)
                Geometry(lane, "Obstacle " + (i + 1), new Vector3(RhythmCourseModel.ObstacleX(i, shifted), .3f, 0),
                    new Vector3(.26f, .6f, .42f), i == 3 && shifted ? actor : track);
            var runner = new GameObject(shifted ? "Comparison articulated runner" : "Baseline articulated runner").transform;
            runner.SetParent(root, false);
            runner.localPosition = lane.localPosition;
            model = ((GameObject)PrefabUtility.InstantiatePrefab(prefab)).transform;
            model.SetParent(runner, false);
            model.localRotation = Quaternion.Euler(0, 90, 0);
            var renderers = model.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) throw new InvalidOperationException("Knight mesh missing.");
            Bounds bounds = renderers[0].bounds;
            foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            if (bounds.size.y <= 0) throw new InvalidOperationException("Invalid Knight height.");
            model.localScale = Vector3.one * (.75f / bounds.size.y);
            bounds = renderers[0].bounds;
            foreach (var renderer in renderers)
            {
                bounds.Encapsulate(renderer.bounds);
                renderer.sharedMaterial = actor;
            }
            model.position += new Vector3(runner.position.x - bounds.center.x, runner.position.y - bounds.min.y,
                runner.position.z - bounds.center.z);
            foreach (var animator in model.GetComponentsInChildren<Animator>()) { animator.enabled = false; animator.applyRootMotion = false; }
            foreach (var animation in model.GetComponentsInChildren<Animation>()) animation.enabled = false;
            foreach (var skin in model.GetComponentsInChildren<SkinnedMeshRenderer>()) { skin.updateWhenOffscreen = true; skin.forceMatrixRecalculationPerRender = true; }
            foreach (var collider in model.GetComponentsInChildren<Collider>()) UnityEngine.Object.DestroyImmediate(collider);
            return runner;
        }

        private static GameObject Geometry(Transform parent, string name, Vector3 at, Vector3 scale, Material material)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = at;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = material;
            UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());
            return go;
        }

        private static GameObject Marker(Transform parent, string name, float y, Material material)
        {
            var go = Geometry(parent, name, new Vector3(0, y, 0), new Vector3(.12f, .32f, .08f), material);
            go.SetActive(false);
            return go;
        }

        private static Material MaterialAsset(Shader shader, string name, Color color)
        {
            string path = Folder + "/" + name + ".mat";
            if (File.Exists(path)) throw new InvalidOperationException("Preserve existing V2 material: " + name);
            var material = new Material(shader) { color = color };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static void Label(Transform parent, string text, float x, float y, float size)
        {
            var go = new GameObject(text, typeof(TextMesh));
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(x, y, 12);
            var label = go.GetComponent<TextMesh>();
            string fontPath = Folder + "/KoreanFont.asset";
            label.font = AssetDatabase.LoadAssetAtPath<Font>(fontPath);
            if (!label.font)
            {
                label.font = Font.CreateDynamicFontFromOSFont("Malgun Gothic", 48);
                if (!label.font) throw new InvalidOperationException("Korean font unavailable.");
                AssetDatabase.CreateAsset(label.font, fontPath);
            }
            label.fontSize = 48;
            label.characterSize = size;
            label.anchor = TextAnchor.UpperLeft;
            label.color = new Color(1, .87f, .58f);
            label.text = text;
            go.GetComponent<Renderer>().sharedMaterial = label.font.material;
        }
    }
}
