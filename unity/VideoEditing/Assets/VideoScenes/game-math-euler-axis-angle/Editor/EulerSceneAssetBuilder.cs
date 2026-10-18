using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace YamyamCoding.GameMath.EulerAxisAngle.Editor
{
    public static class EulerSceneAssetBuilder
    {
        public const string Root = "Assets/VideoScenes/game-math-euler-axis-angle";
        public static readonly string[] Ids = { "03", "04", "06", "07", "09", "10", "12", "16", "18", "19", "21", "22" };
        public static readonly string[] Modes = { "euler", "intrinsic", "extrinsic", "order", "aliases", "gimbal",
            "gimbal-values", "interpolation", "axis-angle", "rotation-vector", "axis-aliases", "nonadd" };

        // Explicit invocation only. It creates additive scenes and restores the
        // former active scene. Never call this while a foreign editor is active.
        public static void BuildAllInIsolatedProject()
        {
            BuildAll();
            EditorApplication.Exit(0);
        }

        public static void BuildAndCaptureInIsolatedProject()
        {
            BuildAll();
            EulerCaptureBatch.Run();
        }

        private static void BuildAll()
        {
            RequireIsolatedBatch();
            RunMathChecks();
            UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline = null;
            QualitySettings.renderPipeline = null;
            // The isolated editor may reopen the last captured scene. Start
            // from a saved bootstrap so additive baking cannot duplicate a
            // currently loaded scene path or meet an unsaved blank scene.
            Scene original = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EditorSceneManager.SaveScene(original, Root + "/CaptureBootstrap.unity");
            for (int i = 0; i < Ids.Length; i++)
            {
                Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
                SceneManager.SetActiveScene(scene);
                GameObject root = new GameObject("Yamyam M04 scene " + Ids[i]);
                EulerAircraftScene controller = root.AddComponent<EulerAircraftScene>();
                controller.sceneId = Ids[i]; controller.lessonMode = Modes[i];
                if (controller.HasTwoAircraft) controller.orthographicSize = 5.4f;
                controller.Build(); controller.Evaluate(0f);
                PersistGeneratedObjects(controller, Ids[i]);
                string path = Root + "/Scenes/" + Ids[i] + "-" + Modes[i] + ".unity";
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                if (!EditorSceneManager.SaveScene(scene, path)) throw new IOException("Could not save " + path);
                EditorSceneManager.CloseScene(scene, true);
            }
            if (original.IsValid() && original.isLoaded) SceneManager.SetActiveScene(original);
            AssetDatabase.SaveAssets(); AssetDatabase.Refresh();
            File.WriteAllText("m04-scene-build-success.json", "{\"sceneCount\":12,\"mathChecks\":\"passed\",\"editor\":\"" + Application.unityVersion + "\"}");
        }

        private static void PersistGeneratedObjects(EulerAircraftScene controller, string id)
        {
            string directory = Root + "/Baked/" + id;
            Directory.CreateDirectory(directory);
            var savedMeshes = new Dictionary<Mesh, Mesh>(); var savedMaterials = new Dictionary<Material, Material>();
            int meshIndex = 0, matIndex = 0;
            foreach (MeshFilter filter in controller.GetComponentsInChildren<MeshFilter>(true))
            {
                Mesh mesh = filter.sharedMesh;
                if (mesh == null || EditorUtility.IsPersistent(mesh)) continue;
                if (!savedMeshes.TryGetValue(mesh, out Mesh saved))
                {
                    saved = UnityEngine.Object.Instantiate(mesh);
                    AssetDatabase.CreateAsset(saved, directory + "/mesh-" + (meshIndex++).ToString("D3") + ".asset");
                    savedMeshes.Add(mesh, saved);
                }
                filter.sharedMesh = saved;
            }
            foreach (Renderer renderer in controller.GetComponentsInChildren<Renderer>(true))
            {
                Material material = renderer.sharedMaterial;
                if (material == null || EditorUtility.IsPersistent(material)) continue;
                if (!savedMaterials.TryGetValue(material, out Material saved))
                {
                    saved = UnityEngine.Object.Instantiate(material);
                    AssetDatabase.CreateAsset(saved, directory + "/material-" + (matIndex++).ToString("D3") + ".mat");
                    savedMaterials.Add(material, saved);
                }
                renderer.sharedMaterial = saved;
            }
        }
        public static void RequireIsolatedBatch()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, "..")).Replace('\\', '/');
            if (!Application.isBatchMode || !project.EndsWith("/production/local/revision-v2/unity-capture", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("M04 batch authoring/capture is restricted to its isolated revision-v2/unity-capture project.");
        }
        public static void RunMathChecks()
        {
            const float e = 2e-5f;
            CheckVector(EulerMathContract.Rx(90f).MultiplyVector(Vector3.forward), Vector3.down, "Rx +90 sends +z to -y", e);
            CheckVector(EulerMathContract.Ry(90f).MultiplyVector(Vector3.forward), Vector3.right, "Ry +90 sends +z to +x", e);
            CheckVector((EulerMathContract.Ry(90f) * EulerMathContract.Rx(90f)).MultiplyVector(Vector3.forward), Vector3.down, "X then Y", e);
            CheckVector((EulerMathContract.Rx(90f) * EulerMathContract.Ry(90f)).MultiplyVector(Vector3.forward), Vector3.right, "Y then X", e);
            CheckMatrix(EulerMathContract.EulerYXZ(0f, 135f, 0f), EulerMathContract.EulerYXZ(180f, 45f, 180f), "Euler alias", e);
            CheckMatrix(EulerMathContract.EulerYXZ(30f, 90f, 10f), EulerMathContract.EulerYXZ(20f, 90f, 0f), "+90 gimbal h-b", e);
            CheckMatrix(EulerMathContract.EulerYXZ(5f, 90f, 5f), EulerMathContract.EulerYXZ(0f, 90f, 0f), "+5 heading and bank cancel at+90", e);
            CheckMatrix(EulerMathContract.EulerYXZ(30f, -90f, 10f), EulerMathContract.EulerYXZ(40f, -90f, 0f), "-90 gimbal h+b", e);
            CheckMatrix(EulerMathContract.AxisAngle(Vector3.up, 90f), EulerMathContract.AxisAngle(Vector3.down, 270f), "axis aliases", e);
            CheckMatrix(EulerMathContract.RotationVector(Vector3.zero), Matrix4x4.identity, "zero vector is identity", e);
            if (EulerMathContract.MaxDifference(EulerMathContract.EulerYXZ(0f, 67.5f, 0f), EulerMathContract.EulerYXZ(90f, 22.5f, 90f)) < .1f)
                throw new InvalidOperationException("Euler interpolation midpoints must differ.");
            Matrix4x4 downBodyYaw = EulerMathContract.Rx(90f) * EulerMathContract.Ry(35f);
            Matrix4x4 downWorldHeading = EulerMathContract.Ry(35f) * EulerMathContract.Rx(90f);
            CheckVector(downWorldHeading.MultiplyVector(Vector3.forward), Vector3.down, "world heading keeps downward forward", e);
            if (Vector3.Distance(downBodyYaw.MultiplyVector(Vector3.forward), Vector3.down) < .1f)
                throw new InvalidOperationException("Body-y yaw must change downward forward.");
            if (EulerMathContract.MaxDifference(EulerMathContract.Ry(90f) * EulerMathContract.Rx(90f),
                EulerMathContract.RotationVector(new Vector3(Mathf.PI * .5f, Mathf.PI * .5f, 0f))) < .1f)
                throw new InvalidOperationException("Finite vector sum must differ from ordered composition.");
            Matrix4x4 r = EulerMathContract.EulerYXZ(33f, 71f, -29f);
            Vector3 v = new Vector3(.8f, -1.3f, 2.1f);
            CheckVector(EulerMathContract.UnityMatrix(r).MultiplyVector(EulerMathContract.ToUnity(v)),
                EulerMathContract.ToUnity(r.MultiplyVector(v)), "C R C conjugation", e);
            CheckMatrix(EulerMathContract.MathMatrix(EulerMathContract.UnityRotation(r)), r, "Unity quaternion round trip", e);
        }
        private static void CheckVector(Vector3 a, Vector3 b, string name, float tolerance)
        { if (Vector3.Distance(a, b) > tolerance) throw new InvalidOperationException(name + " failed: " + a + " != " + b); }
        private static void CheckMatrix(Matrix4x4 a, Matrix4x4 b, string name, float tolerance)
        { if (EulerMathContract.MaxDifference(a, b) > tolerance) throw new InvalidOperationException(name + " failed"); }
    }
}
