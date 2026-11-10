using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Yamyam.LevelDesign.RhythmRunner.Editor
{
    public static class RhythmCourseBuilder
    {
        private const string Folder = "Assets/VideoScenes/architectural-111-20261106/13-02-RhythmCourseV1";
        private const string ScenePath = Folder + "/RunnerComparison.unity";
        private const string Surface = "Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader";

        [MenuItem("Yamyam/Level Design/Build 13.02 Rhythm Course")]
        public static void Build()
        {
            if (File.Exists(ScenePath))
                throw new InvalidOperationException("The editable rhythm course already exists.");
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(Surface);
            if (!shader)
                throw new InvalidOperationException("The shared architectural surface is required.");

            Directory.CreateDirectory(Folder);
            AssetDatabase.Refresh();
            Material track = MaterialAsset(shader, "Track", new Color(0.19f, 0.26f, 0.29f));
            Material baseline = MaterialAsset(shader, "Baseline", new Color(0.29f, 0.83f, 0.64f));
            Material changed = MaterialAsset(shader, "Changed", new Color(0.96f, 0.55f, 0.30f));
            Material pulse = MaterialAsset(shader, "Input", new Color(1, 0.84f, 0.41f));

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            var root = new GameObject("13.02 · fixed runner and one changed obstacle");
            SceneManager.MoveGameObjectToScene(root, scene);
            var player = root.AddComponent<RhythmCoursePlayback>();
            player.baselineRunner = Lane(root.transform, 1.55f, false, track, baseline);
            player.delayedRunner = Lane(root.transform, -1.55f, true, track, changed);

            var cameraObject = new GameObject("Portrait comparison camera", typeof(Camera), typeof(AudioListener));
            cameraObject.transform.SetParent(root.transform, false);
            cameraObject.transform.localPosition = new Vector3(1, 0, -15);
            Camera camera = cameraObject.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.026f, 0.039f, 0.041f);
            camera.orthographic = true;
            camera.orthographicSize = 3.9f;
            player.cameraRig = cameraObject.transform;

            player.baselineInput = Marker(player.baselineRunner, "Same jump input · baseline", 1.05f, pulse);
            player.delayedInput = Marker(player.delayedRunner, "Same jump input · changed", 1.05f, pulse);
            player.delayedCollision = Marker(player.delayedRunner, "Collision at shifted obstacle", 0.95f, changed);
            player.baselineFeedback = root.AddComponent<AudioSource>();
            player.baselineFeedback.playOnAwake = false;
            player.baselineFeedback.spatialBlend = 0;
            AddLabels(cameraObject.transform);

            if (!EditorSceneManager.SaveScene(scene, ScenePath))
                throw new InvalidOperationException("Unity could not save the editable comparison scene.");
            AssetDatabase.SaveAssets();
        }

        private static Transform Lane(Transform root, float y, bool shifted, Material track, Material actor)
        {
            string label = shifted ? "Last obstacle moved" : "Regular obstacle spacing";
            var lane = new GameObject(label).transform;
            lane.SetParent(root, false);
            lane.localPosition = new Vector3(0, y, 0);
            Geometry(lane, "Course surface", PrimitiveType.Cube, new Vector3(14, -0.085f, 0),
                new Vector3(32, 0.17f, 0.55f), track);
            for (int i = 0; i < 4; i++)
            {
                float height = RhythmCourseModel.ObstacleHeight;
                float x = RhythmCourseModel.ObstacleX(i, shifted);
                Geometry(lane, $"Obstacle {i + 1}", PrimitiveType.Cube, new Vector3(x, height * 0.5f, 0),
                    new Vector3(0.26f, height, 0.42f), i == 3 && shifted ? actor : track);
            }

            var runner = new GameObject(label + " · runner").transform;
            runner.SetParent(root, false);
            runner.localPosition = lane.localPosition;
            Geometry(runner, "Runner body", PrimitiveType.Capsule, new Vector3(0, 0.36f, 0),
                new Vector3(0.44f, 0.36f, 0.32f), actor);
            return runner;
        }

        private static GameObject Geometry(Transform parent, string name, PrimitiveType shape, Vector3 at, Vector3 scale, Material material)
        {
            GameObject obj = GameObject.CreatePrimitive(shape);
            obj.name = name;
            obj.transform.SetParent(parent, false);
            obj.transform.localPosition = at;
            obj.transform.localScale = scale;
            obj.GetComponent<Renderer>().sharedMaterial = material;
            UnityEngine.Object.DestroyImmediate(obj.GetComponent<Collider>());
            return obj;
        }

        private static GameObject Marker(Transform parent, string name, float y, Material material)
        {
            GameObject marker = Geometry(parent, name, PrimitiveType.Cube, new Vector3(0, y, 0),
                new Vector3(0.12f, 0.32f, 0.08f), material);
            marker.SetActive(false);
            return marker;
        }

        private static Material MaterialAsset(Shader shader, string name, Color color)
        {
            string path = $"{Folder}/{name}.mat";
            Material previous = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (previous)
            {
                if (previous.shader != shader || previous.color != color)
                    throw new InvalidOperationException($"Existing scene material differs: {name}");
                return previous;
            }
            var material = new Material(shader) { color = color };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static void AddLabels(Transform camera)
        {
            string path = Folder + "/KoreanFont.asset";
            Font font = AssetDatabase.LoadAssetAtPath<Font>(path);
            if (!font)
            {
                font = Font.CreateDynamicFontFromOSFont("Malgun Gothic", 48);
                if (!font)
                    throw new InvalidOperationException("The Korean preview font is required.");
                AssetDatabase.CreateAsset(font, path);
            }
            Label(camera, font, "기준 · 일정 간격", 3.64f);
            Label(camera, font, "비교 · 마지막 장애물만 이동", 0.52f);
        }

        private static void Label(Transform parent, Font font, string line, float y)
        {
            var go = new GameObject(line, typeof(TextMesh));
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(-1.91f, y, 12);
            var text = go.GetComponent<TextMesh>();
            text.font = font;
            text.fontSize = 48;
            text.characterSize = 0.07f;
            text.anchor = TextAnchor.UpperLeft;
            text.color = new Color(1, 0.87f, 0.58f);
            text.text = line;
            go.GetComponent<Renderer>().sharedMaterial = font.material;
        }
    }
}
