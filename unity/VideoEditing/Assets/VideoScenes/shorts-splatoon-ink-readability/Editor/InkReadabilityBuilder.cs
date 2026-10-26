#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace YamyamCoding.Shorts.SplatoonInkReadability.Editor
{
    /// <summary>
    /// Prepared source only. Execute after the parent's actual-game/GPU checks.
    /// Creates editable scenes; does not render, capture or change project settings.
    /// </summary>
    public static class InkReadabilityBuilder
    {
        private const string Root = "Assets/VideoScenes/shorts-splatoon-ink-readability";
        private const string ShaderName = "Yamyam/Shorts/InkReadabilityLesson";
        private static readonly string[] GeneratedPaths =
        {
            "/Materials/Ink-two-colours.mat",
            "/Materials/Neutral-stand-in.mat",
            "/Materials/Eye-and-joint-detail.mat",
            "/Materials/Fixed-splash-signal.mat",
            "/Meshes/Raised-ink-floor.asset",
            "/Meshes/Raised-ink-wall.asset",
            "/Meshes/Original-submerge-ring.asset",
            "/Prefabs/InkReadabilityTestbed.prefab",
            "/Scenes/02-PBSBoundary.unity",
            "/Scenes/03-NoShading.unity",
            "/Scenes/04-SpecularBaseline.unity",
            "/Scenes/05-StrongSpecular.unity",
            "/Scenes/06-BalancedIllustration.unity",
        };

        [MenuItem("Yamyam/Shorts/Splatoon Ink Readability/Build Editable Testbed")]
        public static void Build()
        {
            if (System.Diagnostics.Process.GetProcessesByName("Overwatch").Length > 0)
                throw new InvalidOperationException("User game is running. Leave it running and defer Unity production.");
            // Quality overrides take precedence over the global default. In this
            // project PC quality selects URP even though the global asset is null.
            RenderPipelineAsset pipeline = QualitySettings.renderPipeline
                ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            if (!(pipeline is UniversalRenderPipelineAsset))
                throw new InvalidOperationException("This authored shader requires the selected quality/default URP asset. Do not change global settings to run this builder.");
            // Check ALL outputs and orphan .meta files before any folder, asset
            // or scene mutation. A previous partial build is never overwritten.
            foreach (string path in GeneratedPaths) AssertNewAsset(Root + path);
            Shader shader = Shader.Find(ShaderName);
            if (!shader) throw new InvalidOperationException("Import the project-specific shader before building.");

            foreach (string folder in new[] {"Meshes", "Materials", "Prefabs", "Scenes"})
                EnsureFolder(Root + "/" + folder);
            Scene previous = SceneManager.GetActiveScene();
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            try
            {
                if (SceneManager.GetActiveScene() != scene && !EditorSceneManager.SetActiveScene(scene))
                    throw new InvalidOperationException("New additive lesson scene is not active. Defer building until Editor startup completes; do not create objects in the previous scene.");
                RenderSettings.skybox = null;
                RenderSettings.ambientMode = AmbientMode.Flat;
                RenderSettings.ambientLight = Color.black;
                var testbed = new GameObject("Ink readability — original teaching model");
                var demo = testbed.AddComponent<InkReadabilityDemo>();
                Material ink = MakeMaterial("Ink-two-colours", shader, Hex("#42B5BA"), true, 0.3f);
                Material neutral = MakeMaterial("Neutral-stand-in", shader, Hex("#D9DEDA"), false, 0.15f);
                Material dark = MakeMaterial("Eye-and-joint-detail", shader, Hex("#25383D"), false, 0.05f);
                Material splash = MakeMaterial("Fixed-splash-signal", shader, Hex("#42B5BA"), false, 0.3f);

                Mesh floorMesh = MakeSurface("Raised-ink-floor", false);
                Mesh wallMesh = MakeSurface("Raised-ink-wall", true);
                Renderer floor = Surface("Floor — unchanged in every comparison", floorMesh, ink, testbed.transform);
                Renderer wall = Surface("Wall — unchanged in every comparison", wallMesh, ink, testbed.transform);
                demo.inkSurfaces = new[] {floor, wall};

                var diver = new GameObject("Original articulated diver stand-in");
                diver.transform.SetParent(testbed.transform, false);
                demo.diver = diver.transform;
                Part("Torso", PrimitiveType.Capsule, new Vector3(0, 0.35f, 0), new Vector3(0.42f, 0.35f, 0.3f), neutral, diver.transform);
                Part("Head", PrimitiveType.Sphere, new Vector3(0, 0.9f, 0), Vector3.one * 0.35f, neutral, diver.transform);
                for (int sign = -1; sign <= 1; sign += 2)
                {
                    Part("Shoulder joint " + sign, PrimitiveType.Sphere, new Vector3(sign * 0.28f, 0.58f, 0), Vector3.one * 0.14f, dark, diver.transform);
                    Part("Arm " + sign, PrimitiveType.Capsule, new Vector3(sign * 0.34f, 0.32f, 0), new Vector3(0.13f, 0.24f, 0.13f), neutral, diver.transform);
                    Part("Leg " + sign, PrimitiveType.Capsule, new Vector3(sign * 0.12f, -0.12f, 0), new Vector3(0.16f, 0.26f, 0.16f), neutral, diver.transform);
                    Part("Eye " + sign, PrimitiveType.Sphere, new Vector3(sign * 0.075f, 0.93f, -0.15f), Vector3.one * 0.045f, dark, diver.transform);
                }
                Mesh ringMesh = MakeRing();
                demo.ripple = Surface("Fixed submerge ring", ringMesh, splash, testbed.transform).transform;
                demo.droplets = new Transform[12];
                for (int i = 0; i < demo.droplets.Length; i++)
                    demo.droplets[i] = Part("Fixed splash droplet " + i, PrimitiveType.Sphere, Vector3.zero, Vector3.one * 0.07f, splash, testbed.transform).transform;

                var cameraObject = new GameObject("Locked lesson camera");
                cameraObject.transform.SetParent(testbed.transform, false);
                Camera camera = cameraObject.AddComponent<Camera>();
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = Color.black;
                camera.fieldOfView = 40;
                camera.nearClipPlane = 0.1f;
                camera.farClipPlane = 100;
                camera.allowHDR = true;
                camera.transform.position = new Vector3(6.6f, 6.1f, -7.3f);
                camera.transform.LookAt(new Vector3(0, 0.8f, 0.1f));
                demo.lessonCamera = camera;
                var lampObject = new GameObject("Fixed light direction — shader reference");
                lampObject.transform.SetParent(testbed.transform, false);
                Light light = lampObject.AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 1;
                light.shadows = LightShadows.None;
                light.transform.rotation = Quaternion.LookRotation(-demo.fixedLightDirection.normalized);

                demo.SetBalancedIllustration(0.62f);
                AssertNewAsset(Root + "/Prefabs/InkReadabilityTestbed.prefab");
                GameObject prefab = PrefabUtility.SaveAsPrefabAssetAndConnect(testbed,
                    Root + "/Prefabs/InkReadabilityTestbed.prefab", InteractionMode.AutomatedAction);
                if (!prefab) throw new InvalidOperationException("Could not save the scoped testbed prefab.");
                SaveVariant(scene, demo, "02-PBSBoundary", 1, 0.3f);
                SaveVariant(scene, demo, "03-NoShading", 0, 0.3f);
                SaveVariant(scene, demo, "04-SpecularBaseline", 0.55f, 0.3f);
                SaveVariant(scene, demo, "05-StrongSpecular", 0.55f, 3.5f);
                SaveVariant(scene, demo, "06-BalancedIllustration", 0.55f, 0.3f);
                // Do not flush unrelated dirty project assets with SaveAssets.
                foreach (string path in GeneratedPaths)
                {
                    Object generated = AssetDatabase.LoadMainAssetAtPath(Root + path);
                    if (generated) AssetDatabase.SaveAssetIfDirty(generated);
                }
                Debug.Log("INK_READABILITY_BUILT: five independently editable scenes, one shared original testbed. No frames rendered.");
            }
            finally
            {
                // No unrelated scene is closed or saved.
                if (scene.IsValid()) EditorSceneManager.CloseScene(scene, true);
                if (previous.IsValid() && previous.isLoaded && SceneManager.GetActiveScene() != previous) EditorSceneManager.SetActiveScene(previous);
            }
        }

        private static void SaveVariant(Scene scene, InkReadabilityDemo demo, string name, float shade, float specular)
        {
            string path = Root + "/Scenes/" + name + ".unity";
            AssertNewAsset(path);
            demo.shadingStrength = shade;
            demo.specularStrength = specular;
            demo.submergePhase = 0.62f;
            demo.Apply();
            PrefabUtility.RecordPrefabInstancePropertyModifications(demo);
            EditorSceneManager.MarkSceneDirty(scene);
            if (!EditorSceneManager.SaveScene(scene, path))
                throw new IOException("Failed to save scoped scene " + name);
        }

        private static void AssertNewAsset(string assetPath)
        {
            if (!Array.Exists(GeneratedPaths, suffix => assetPath == Root + suffix))
                throw new InvalidOperationException("Unexpected generated asset path: " + assetPath);
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string scope = Path.GetFullPath(Path.Combine(project, Root)) + Path.DirectorySeparatorChar;
            string absolute = Path.GetFullPath(Path.Combine(project, assetPath));
            if (!absolute.StartsWith(scope, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Generated path leaves this lesson: " + assetPath);
            if (File.Exists(absolute) || Directory.Exists(absolute) || File.Exists(absolute + ".meta")
                || !string.IsNullOrEmpty(AssetDatabase.AssetPathToGUID(assetPath)))
                throw new InvalidOperationException("Existing asset or metadata must be preserved: " + assetPath);
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = path.Substring(0, path.LastIndexOf('/'));
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, path.Substring(path.LastIndexOf('/') + 1));
        }

        private static Color Hex(string value)
        {
            ColorUtility.TryParseHtmlString(value, out Color colour);
            return colour;
        }

        private static Material MakeMaterial(string name, Shader shader, Color colour, bool ink, float specular)
        {
            string path = Root + "/Materials/" + name + ".mat";
            AssertNewAsset(path);
            var material = new Material(shader) {name = name};
            material.SetColor("_BaseColor", colour);
            material.SetColor("_TeamA", Hex("#42B5BA"));
            material.SetColor("_TeamB", Hex("#DB8546"));
            material.SetFloat("_InkPattern", ink ? 1 : 0);
            material.SetFloat("_SpecularStrength", specular);
            material.SetFloat("_ShadingStrength", ink ? 1 : 0.65f);
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static Renderer Surface(string name, Mesh mesh, Material material, Transform parent)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = item.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            return renderer;
        }

        private static GameObject Part(string name, PrimitiveType kind, Vector3 position, Vector3 scale, Material material, Transform parent)
        {
            GameObject item = GameObject.CreatePrimitive(kind);
            item.name = name;
            item.transform.SetParent(parent, false);
            item.transform.localPosition = position;
            item.transform.localScale = scale;
            item.GetComponent<Renderer>().sharedMaterial = material;
            Object.DestroyImmediate(item.GetComponent<Collider>());
            return item;
        }

        private static Mesh MakeSurface(string name, bool wall)
        {
            string path = Root + "/Meshes/" + name + ".asset";
            AssertNewAsset(path);
            const int columns = 64;
            int rows = wall ? 36 : 64;
            var vertices = new Vector3[(columns + 1) * (rows + 1)];
            var uv = new Vector2[vertices.Length];
            var triangles = new int[columns * rows * 6];
            for (int row = 0; row <= rows; row++)
            for (int column = 0; column <= columns; column++)
            {
                float u = column / (float)columns;
                float v = row / (float)rows;
                float x = (u - 0.5f) * 6;
                float distance = wall ? 6 + v * 3.2f : v * 6;
                // Actual small raised geometry stays unchanged in every state.
                float height = 0.045f + 0.022f * Mathf.Sin(x * 5.2f) * Mathf.Sin(distance * 7.5f)
                    + 0.012f * Mathf.Sin(x * 11.1f + distance * 8.3f);
                int index = row * (columns + 1) + column;
                vertices[index] = wall ? new Vector3(x, v * 3.2f, 3 - height)
                    : new Vector3(x, height, v * 6 - 3);
                uv[index] = new Vector2(u, distance / 9.2f);
                if (row == rows || column == columns) continue;
                int t = (row * columns + column) * 6;
                triangles[t] = index;
                triangles[t + 1] = index + columns + 1;
                triangles[t + 2] = index + 1;
                triangles[t + 3] = index + 1;
                triangles[t + 4] = index + columns + 1;
                triangles[t + 5] = index + columns + 2;
            }
            var mesh = new Mesh {name = name, vertices = vertices, uv = uv, triangles = triangles};
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh, path);
            return mesh;
        }

        private static Mesh MakeRing()
        {
            string path = Root + "/Meshes/Original-submerge-ring.asset";
            AssertNewAsset(path);
            const int segments = 64;
            var vertices = new Vector3[segments * 2];
            var uv = new Vector2[vertices.Length];
            var triangles = new int[segments * 6];
            for (int i = 0; i < segments; i++)
            {
                float angle = i * Mathf.PI * 2 / segments;
                Vector3 radial = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                vertices[i * 2] = radial * 0.21f;
                vertices[i * 2 + 1] = radial * 0.25f;
                int a = i * 2;
                int b = ((i + 1) % segments) * 2;
                int t = i * 6;
                triangles[t] = a; triangles[t + 1] = b; triangles[t + 2] = a + 1;
                triangles[t + 3] = a + 1; triangles[t + 4] = b; triangles[t + 5] = b + 1;
            }
            var mesh = new Mesh {name = "Original-submerge-ring", vertices = vertices, uv = uv, triangles = triangles};
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh, path);
            return mesh;
        }
    }
}
#endif
