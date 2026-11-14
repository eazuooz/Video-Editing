using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Yamyam.LevelDesign.ApertureV1.Editor
{
    public static class ApertureDirectionBuilderV1
    {
        public const string Folder = "Assets/VideoScenes/architectural-111-20261106/01-02-ApertureV1";
        public const string ScenePath = Folder + "/P04-FixedApertureDirection.unity";
        // Scene-local visibility convention. Do not change shared Tags/Layers settings.
        private const int SectionHiddenLayer = 31;

        [MenuItem("Yamyam/Level Design/Build 01.02 aperture direction V1")]
        public static void Build()
        {
            if (File.Exists(ScenePath)) throw new InvalidOperationException("Preserve the existing editable scene.");
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit");
            if (!lit || !unlit) throw new InvalidOperationException("Verified URP lit/unlit shaders required.");
            Directory.CreateDirectory(Folder);
            AssetDatabase.Refresh();
            Material stone = MaterialAsset(lit, "MatteStone", new Color(.37f, .39f, .38f));
            Material dark = MaterialAsset(lit, "DarkStage", new Color(.035f, .04f, .04f));
            Material target = MaterialAsset(lit, "TargetSurface", new Color(.95f, .83f, .41f));
            Material guide = MaterialAsset(unlit, "EditorialGuide", new Color(.25f, .9f, .72f));
            var previousActiveScene = SceneManager.GetActiveScene();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            SceneManager.SetActiveScene(scene);
            try
            {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = Color.black;
            RenderSettings.ambientIntensity = 0f;
            RenderSettings.reflectionIntensity = 0f;
            RenderSettings.fog = false;
            var root = new GameObject("01.02 - fixed thick wall, aperture, source and target");
            SceneManager.MoveGameObjectToScene(root, scene);
            var playback = root.AddComponent<ApertureDirectionPlaybackV1>();

            // Wall faces Z=0 and Z=1, aperture Y=[1.8,2.2], X=[-.7,.7].
            Box(root.transform, "Front or inside wall", new Vector3(0f, .9f, .5f), new Vector3(10f, 1.8f, 1f), stone);
            Box(root.transform, "Upper wall", new Vector3(0f, 3.35f, .5f), new Vector3(10f, 2.3f, 1f), stone);
            var nearSide = Box(root.transform, "Near side wall (section cutaway)", new Vector3(-2.85f, 2f, .5f), new Vector3(4.3f, .4f, 1f), stone);
            nearSide.layer = SectionHiddenLayer;
            Box(root.transform, "Far side wall", new Vector3(2.85f, 2f, .5f), new Vector3(4.3f, .4f, 1f), stone);
            Box(root.transform, "Floor", new Vector3(0f, -.1f, 3f), new Vector3(11f, .2f, 15f), dark);
            Box(root.transform, "Back wall", new Vector3(0f, 2.25f, 9.2f), new Vector3(10f, 4.5f, .2f), dark);
            // The target's front collider is exactly Z=9, Y=[.55,.95].
            Box(root.transform, "Target (표적)", new Vector3(0f, .75f, 9.025f), new Vector3(1.4f, .4f, .05f), target);
            var emitter = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            emitter.name = "Fixed light source";
            emitter.transform.SetParent(root.transform, false);
            emitter.transform.position = ApertureDirectionPlaybackV1.Source;
            emitter.transform.localScale = Vector3.one * .14f;
            UnityEngine.Object.DestroyImmediate(emitter.GetComponent<Collider>());
            emitter.GetComponent<Renderer>().sharedMaterial = guide;
            NoShadow(emitter);

            var spot = new GameObject("Finite actual Unity spotlight", typeof(Light));
            spot.transform.SetParent(root.transform, false);
            playback.finiteSpot = spot.GetComponent<Light>();
            playback.finiteSpot.type = LightType.Spot;
            playback.finiteSpot.color = Color.white;
            playback.finiteSpot.intensity = 25f;
            playback.finiteSpot.range = 25f;
            playback.finiteSpot.spotAngle = 1.2f;
            playback.finiteSpot.innerSpotAngle = .8f;
            playback.finiteSpot.shadows = LightShadows.Hard;
            playback.finiteSpot.shadowBias = .001f;
            playback.finiteSpot.shadowNormalBias = .001f;
            playback.finiteSpot.shadowNearPlane = .1f;

            var ray = new GameObject("Editorial center ray - not an irradiance sensor", typeof(LineRenderer));
            ray.transform.SetParent(root.transform, false);
            playback.editorialCenterRay = ray.GetComponent<LineRenderer>();
            playback.editorialCenterRay.sharedMaterial = guide;
            playback.editorialCenterRay.startWidth = .035f;
            playback.editorialCenterRay.endWidth = .035f;
            playback.editorialCenterRay.useWorldSpace = true;
            playback.editorialCenterRay.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            playback.editorialCenterRay.receiveShadows = false;
            ray.layer = 30;
            var arrow = new GameObject("Direction arrow at the actual source");
            arrow.transform.SetParent(root.transform, false);
            playback.sourceArrow = arrow.transform;
            var stem = Box(arrow.transform, "Direction shaft", new Vector3(0f, 0f, .25f), new Vector3(.035f, .035f, .5f), guide);
            UnityEngine.Object.DestroyImmediate(stem.GetComponent<Collider>());
            var tip = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            tip.name = "Arrow endpoint";
            tip.transform.SetParent(arrow.transform, false);
            tip.transform.localPosition = new Vector3(0f, 0f, .5f);
            tip.transform.localScale = Vector3.one * .085f;
            UnityEngine.Object.DestroyImmediate(tip.GetComponent<Collider>());
            tip.GetComponent<Renderer>().sharedMaterial = guide;
            NoShadow(stem);
            NoShadow(tip);
            stem.layer = tip.layer = 30;

            playback.playerCamera = CameraObject(root.transform, "Player view - actual Unity light", ApertureDirectionPlaybackV1.Source, new Vector3(0f, .75f, 9f), false);
            playback.playerCamera.fieldOfView = 16f;
            playback.playerCamera.cullingMask = ~(1 << 30);
            playback.sectionCamera = CameraObject(root.transform, "Section view - near side omitted", new Vector3(-11f, 4.2f, 3f), new Vector3(0f, 1.5f, 3f), true);
            playback.sectionCamera.cullingMask = ~(1 << SectionHiddenLayer);
            float playerHalfHeight = Mathf.Tan(8f * Mathf.Deg2Rad) * 1.5f;
            Label(playback.playerCamera.transform, "Unity light output (자체 조명 출력)", -playerHalfHeight * playback.playerCamera.aspect * .94f, playerHalfHeight * .9f, playerHalfHeight * .08f);
            Label(playback.sectionCamera.transform, "Section (단면) · 가까운 옆벽 생략", -6f, 3.25f, .15f);
            playback.stateLabel = Label(playback.sectionCamera.transform, "First contact", -6f, -2.8f, .13f);
            playback.autoPlay = false;
            playback.ApplyFrame(0);
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new InvalidOperationException("Scene save failed.");
            AssetDatabase.SaveAssets();
            EditorSceneManager.CloseScene(scene, true);
            }
            finally
            {
                if (previousActiveScene.IsValid() && previousActiveScene.isLoaded)
                    SceneManager.SetActiveScene(previousActiveScene);
            }
        }

        private static GameObject Box(Transform parent, string name, Vector3 position, Vector3 scale, Material material)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = name;
            obj.transform.SetParent(parent, false);
            obj.transform.localPosition = position;
            obj.transform.localScale = scale;
            obj.GetComponent<Renderer>().sharedMaterial = material;
            return obj;
        }

        private static Camera CameraObject(Transform parent, string name, Vector3 position, Vector3 lookAt, bool ortho)
        {
            var obj = new GameObject(name, typeof(Camera));
            obj.transform.SetParent(parent, false);
            obj.transform.position = position;
            obj.transform.LookAt(lookAt);
            var camera = obj.GetComponent<Camera>();
            camera.backgroundColor = Color.black;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.aspect = 1920f / 1080f;
            camera.fieldOfView = 42f;
            camera.orthographic = ortho;
            camera.orthographicSize = 3.6f;
            camera.nearClipPlane = .05f;
            camera.farClipPlane = 60f;
            return camera;
        }

        private static Material MaterialAsset(Shader shader, string name, Color color)
        {
            string path = Folder + "/" + name + ".mat";
            if (File.Exists(path)) throw new InvalidOperationException("Preserve existing material: " + path);
            var material = new Material(shader);
            material.SetColor("_BaseColor", color);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", .05f);
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static void NoShadow(GameObject obj)
        {
            var renderer = obj.GetComponent<Renderer>();
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static TextMesh Label(Transform parent, string text, float x, float y, float size)
        {
            var obj = new GameObject(text, typeof(TextMesh));
            obj.transform.SetParent(parent, false);
            obj.transform.localPosition = new Vector3(x, y, 1.5f);
            var label = obj.GetComponent<TextMesh>();
            string path = Folder + "/KoreanFont.asset";
            label.font = AssetDatabase.LoadAssetAtPath<Font>(path);
            if (!label.font)
            {
                label.font = Font.CreateDynamicFontFromOSFont("Malgun Gothic", 48);
                if (!label.font) throw new InvalidOperationException("Korean font unavailable.");
                AssetDatabase.CreateAsset(label.font, path);
            }
            label.fontSize = 48;
            label.characterSize = size;
            label.color = Color.white;
            label.anchor = TextAnchor.UpperLeft;
            obj.GetComponent<Renderer>().sharedMaterial = label.font.material;
            NoShadow(obj);
            return label;
        }
    }
}
