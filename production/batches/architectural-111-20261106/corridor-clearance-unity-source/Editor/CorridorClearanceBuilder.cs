using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Yamyam.LevelDesign.CorridorClearance.Editor
{
    public static class CorridorClearanceBuilder
    {
        private const string Parent = "Assets/VideoScenes/architectural-111-20261106";
        private const string FolderName = "02-07-CorridorClearanceV1";
        private const string Folder = Parent + "/" + FolderName;
        private const string ScenePath = Folder + "/CorridorClearance.unity";
        private const string ShaderPath = Parent + "/ArchitecturalSurface.shader";
        private const float WallThickness = 0.40f;
        private const float WallHeight = 2.7f;

        [MenuItem("Yamyam/Level Design/Build 02.07 Corridor Clearance")]
        public static void Build()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Build the corridor scene in edit mode.");
            if (Directory.Exists(Folder))
                throw new InvalidOperationException("The corridor scene folder already exists.");
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
            if (!shader)
                throw new InvalidOperationException("The shared architectural surface is required.");

            Material floor = MakeMaterial(shader, "Floor", new Color(0.12f, 0.16f, 0.15f));
            Material wall = MakeMaterial(shader, "Wall", new Color(0.29f, 0.39f, 0.37f));
            Material body = MakeMaterial(shader, "Body", new Color(0.31f, 0.83f, 0.80f));
            Material desired = MakeMaterial(shader, "Desired camera", new Color(0.99f, 0.59f, 0.47f));
            Material resolved = MakeMaterial(shader, "Resolved camera", new Color(0.67f, 0.88f, 0.55f));
            Material[] materials = { floor, wall, body, desired, resolved };
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            string folderGuid = null;
            try
            {
                var root = new GameObject("02.07 · corridor width comparison");
                SceneManager.MoveGameObjectToScene(root, scene);
                Transform narrow = new GameObject("A · narrow").transform;
                Transform wide = new GameObject("B · wide").transform;
                narrow.SetParent(root.transform, false);
                wide.SetParent(root.transform, false);
                narrow.localPosition = new Vector3(-2.1f, 0, 0);
                wide.localPosition = new Vector3(2.1f, 0, 0);

                var playback = root.AddComponent<CorridorClearancePlayback>();
                playback.narrow = CreateLane(narrow, 1.40f, floor, wall, body, desired, resolved);
                playback.wide = CreateLane(wide, 2.40f, floor, wall, body, desired, resolved);
                Camera observer = AddCamera(root.transform, "Top-down comparison", new Vector3(0, 9, 2.35f),
                    Quaternion.Euler(90, 0, 0));
                observer.orthographic = true;
                observer.orthographicSize = 6.6f;
                observer.enabled = true;

                Physics.SyncTransforms();
                playback.Apply(CorridorClearancePlayback.SampleZ);
                if (playback.narrow.BodyBlocked || playback.wide.BodyBlocked ||
                    !playback.narrow.DesiredCameraBlocked || playback.wide.DesiredCameraBlocked ||
                    playback.narrow.ResolvedCameraBlocked || playback.wide.ResolvedCameraBlocked)
                    throw new InvalidOperationException("The Unity wall overlap differs from the planned comparison.");
                playback.Apply(0.6f);

                folderGuid = AssetDatabase.CreateFolder(Parent, FolderName);
                if (AssetDatabase.GUIDToAssetPath(folderGuid) != Folder)
                    throw new InvalidOperationException("Unity did not create the expected corridor scene folder.");
                foreach (Material material in materials)
                    AssetDatabase.CreateAsset(material, Folder + "/" + material.name + ".mat");
                if (!EditorSceneManager.SaveScene(scene, ScenePath))
                    throw new InvalidOperationException("Unity could not save the editable corridor scene.");
                AssetDatabase.SaveAssets();
            }
            catch
            {
                EditorSceneManager.CloseScene(scene, true);
                if (!string.IsNullOrEmpty(folderGuid) && AssetDatabase.GUIDToAssetPath(folderGuid) == Folder)
                    AssetDatabase.DeleteAsset(Folder);
                foreach (Material material in materials)
                    if (material && !EditorUtility.IsPersistent(material))
                        UnityEngine.Object.DestroyImmediate(material);
                throw;
            }
        }

        private static CorridorClearancePlayback.Lane CreateLane(Transform origin, float width,
            Material floor, Material wall, Material body, Material desired, Material resolved)
        {
            float length = CorridorClearancePlayback.WallEnd - CorridorClearancePlayback.WallStart;
            float middle = CorridorClearancePlayback.WallStart + length * 0.5f;
            float wallCenter = (width + WallThickness) * 0.5f;
            Vector3 wallSize = new Vector3(WallThickness, WallHeight, length);
            Geometry(origin, "Test floor", PrimitiveType.Cube, new Vector3(0, -0.05f, 2.35f),
                new Vector3(3.6f, 0.10f, 4.8f), floor, false);
            Geometry(origin, "Door plane reference", PrimitiveType.Cube,
                new Vector3(0, 0.008f, CorridorClearancePlayback.WallStart),
                new Vector3(width, 0.016f, 0.055f), body, false);
            BoxCollider left = Geometry(origin, "Left wall", PrimitiveType.Cube,
                new Vector3(-wallCenter, WallHeight * 0.5f, middle), wallSize, wall, true)
                .GetComponent<BoxCollider>();
            BoxCollider right = Geometry(origin, "Right wall", PrimitiveType.Cube,
                new Vector3(wallCenter, WallHeight * 0.5f, middle), wallSize, wall, true)
                .GetComponent<BoxCollider>();
            float bodyDiameter = CorridorClearancePlayback.BodyRadius * 2;
            GameObject actor = Geometry(origin, "Body proxy", PrimitiveType.Capsule, Vector3.zero,
                new Vector3(bodyDiameter, 0.90f, bodyDiameter), body, false);
            float cameraDiameter = CorridorClearancePlayback.CameraRadius * 2;
            Transform intended = Geometry(origin, "Desired camera boundary", PrimitiveType.Sphere, Vector3.zero,
                Vector3.one * cameraDiameter, desired, false).transform;
            Transform adjusted = Geometry(origin, "Resolved camera boundary", PrimitiveType.Sphere, Vector3.zero,
                Vector3.one * cameraDiameter, resolved, false).transform;
            Camera view = AddCamera(origin, "Player camera", Vector3.zero, Quaternion.identity);
            view.nearClipPlane = 0.20f;
            return new CorridorClearancePlayback.Lane
            {
                origin = origin,
                leftWall = left,
                rightWall = right,
                body = actor.transform,
                desiredCameraMarker = intended,
                resolvedCameraMarker = adjusted,
                playerCamera = view
            };
        }

        private static Camera AddCamera(Transform parent, string name, Vector3 at, Quaternion rotation)
        {
            var obj = new GameObject(name, typeof(Camera));
            obj.transform.SetParent(parent, false);
            obj.transform.localPosition = at;
            obj.transform.localRotation = rotation;
            var camera = obj.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.035f, 0.033f);
            camera.enabled = false;
            return camera;
        }

        private static GameObject Geometry(Transform parent, string name, PrimitiveType type,
            Vector3 at, Vector3 scale, Material material, bool collider)
        {
            GameObject obj = GameObject.CreatePrimitive(type);
            obj.name = name;
            obj.transform.SetParent(parent, false);
            obj.transform.localPosition = at;
            obj.transform.localScale = scale;
            obj.GetComponent<Renderer>().sharedMaterial = material;
            if (!collider)
                UnityEngine.Object.DestroyImmediate(obj.GetComponent<Collider>());
            return obj;
        }

        private static Material MakeMaterial(Shader shader, string name, Color color)
        {
            return new Material(shader) { name = name, color = color };
        }
    }
}
