using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo : MonoBehaviour
    {
        public int episode = 1;
        public int shot = 1;
        public float seconds = 11;
        public float speechStart, speechEnd = 8;
        public Camera view;
        public bool walkthroughV8;
        public bool observedV10;
        public bool causalV11;

        static readonly Color Ink = new Color32(13, 25, 34, 255);
        static readonly Color Slate = new Color32(65, 91, 107, 255);
        static readonly Color Paper = new Color32(213, 227, 221, 255);
        static readonly Color Gold = new Color32(249, 196, 94, 255);
        static readonly Color Aqua = new Color32(74, 219, 193, 255);
        static readonly Color Red = new Color32(248, 113, 104, 255);
        static readonly Color Blue = new Color32(111, 147, 248, 255);
        readonly Dictionary<Color, Material> palette = new Dictionary<Color, Material>();
        readonly List<UnityEngine.Object> owned = new List<UnityEngine.Object>();
        Action<float> animate;
        Transform stage;
        float begin;
        bool Second => shot == 3;

        static Vector3 V(float x, float y, float z) => new Vector3(x, y, z);
        static float Ease(float t) => Mathf.SmoothStep(0, 1, Mathf.Clamp01(t));
        static float Range(float t, float from, float to) => Ease((t - from) / (to - from));
        static float Pulse(float t) => 0.5f + 0.5f * Mathf.Sin(t * Mathf.PI * 2);

        void Start()
        {
            Build();
            begin = Time.time;
        }

        void Update() => Evaluate(Mathf.Repeat(Time.time - begin, seconds));

        void OnDestroy()
        {
            foreach (var asset in owned)
            {
                if (Application.isPlaying) Destroy(asset);
                else DestroyImmediate(asset);
            }
        }

        Material Paint(Color color)
        {
            if (palette.TryGetValue(color, out var existing)) return existing;
            var material = new Material(Shader.Find(UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline ?
                "Universal Render Pipeline/Lit" : "Standard"));
            material.color = color;
            material.SetFloat(material.HasProperty("_Smoothness") ? "_Smoothness" : "_Glossiness", 0.17f);
            palette.Add(color, material);
            owned.Add(material);
            return material;
        }

        Transform Shape(PrimitiveType kind, string name, Vector3 position, Vector3 size, Color color, Transform parent = null)
        {
            var item = GameObject.CreatePrimitive(kind);
            item.name = name;
            item.transform.SetParent(parent ? parent : stage, false);
            item.transform.localPosition = position;
            item.transform.localScale = size;
            item.GetComponent<Renderer>().sharedMaterial = Paint(color);
            DressPrimitive(item.transform, name);
            return item.transform;
        }

        Transform Block(string name, Vector3 p, Vector3 size, Color color, Transform parent = null) =>
            Shape(PrimitiveType.Cube, name, p, size, color, parent);
        Transform Orb(string name, Vector3 p, float size, Color color, Transform parent = null) =>
            Shape(PrimitiveType.Sphere, name, p, Vector3.one * size, color, parent);

        Transform Group(string name, Vector3 p)
        {
            var group = new GameObject(name).transform;
            group.SetParent(stage, false);
            group.localPosition = p;
            return group;
        }

        void Tint(Transform item, Color color)
        {
            if (item.TryGetComponent<Renderer>(out var renderer)) renderer.sharedMaterial = Paint(color);
        }

        Transform Bar(string name, Vector3 a, Vector3 b, float width, Color color)
        {
            var bar = Block(name, a, Vector3.one, color);
            Segment(bar, a, b, width);
            return bar;
        }

        static void Segment(Transform bar, Vector3 a, Vector3 b, float width)
        {
            var delta = b - a;
            bar.localPosition = (a + b) * .5f;
            if (delta.sqrMagnitude > .00001f) bar.localRotation = Quaternion.FromToRotation(Vector3.forward, delta);
            bar.localScale = V(width, width, Mathf.Max(.001f, delta.magnitude));
        }

        void Route(Color color, params Vector3[] anchors)
        {
            for (int i = 1; i < anchors.Length; i++) Bar("Route", anchors[i - 1], anchors[i], .075f, color);
        }

        Transform Ring(string name, Vector3 p, float radius, Color color)
        {
            var ring = Group(name, p);
            for (int i = 0; i < 28; i++)
            {
                float a = i * 2 * Mathf.PI / 28, b = (i + 1) * 2 * Mathf.PI / 28;
                var bit = Block("Ring edge", V(0, 0, 0), Vector3.one, color, ring);
                Segment(bit, V(Mathf.Cos(a) * radius, 0, Mathf.Sin(a) * radius), V(Mathf.Cos(b) * radius, 0, Mathf.Sin(b) * radius), .06f);
            }
            return ring;
        }

        Transform Pawn(string name, Vector3 p, Color color)
        {
            var root = Group(name, p);
            if (walkthroughV8 || observedV10 || causalV11) AddWalkthroughActor(root, color);
            else AddLibraryActor(root, name, color);
            return root;
        }

        Transform Mount(Vector3 p)
        {
            var root = Group("Library mount", p);
            Attach("horse", root, new Vector3(1.45f, .83f, .95f), true, 90);
            return root;
        }

        Transform Landmark(string name, Vector3 p, float size, Color color)
        {
            var center = Block(name, p + V(0, size * .5f, 0), V(size * .9f, size, size * .85f), color);
            if (center.GetComponent<Renderer>().enabled)
            {
                var role = name.Contains("chapel") || name.Contains("doorway") ? "house" :
                    name.Contains("opportunity") || name.Contains("Distinct outcome") ? "chest" :
                    name.Contains("Mountain") ? "cliff" : name.Contains("castle") || name.Contains("Destination") ? "tower" : "landmark";
                Attach(role, center, Vector3.one, false);
                center.GetComponent<Renderer>().enabled = false;
            }
            return center;
        }

        void Tree(Vector3 p, float size)
        {
            Attach("tree", Group("Foreground library tree", p), V(1.15f, 1.8f, 1.15f) * size, true);
        }

        void FrameCamera(Vector3 position, Vector3 center, float height)
        {
            view.transform.SetPositionAndRotation(position, Quaternion.LookRotation(center - position));
            view.orthographicSize = height;
        }

        public void Build()
        {
            stage = Group("Editable principle stage", Vector3.zero);
            if (!view)
            {
                view = new GameObject("Principle camera").AddComponent<Camera>();
                view.transform.SetParent(transform, false);
            }
            view.orthographic = true;
            view.clearFlags = CameraClearFlags.SolidColor;
            view.backgroundColor = Ink;
            view.nearClipPlane = .1f;
            view.farClipPlane = 80f;
            view.depthTextureMode = DepthTextureMode.Depth;
            FrameCamera(V(8, 9, -13), V(0, .45f, 0), 4.35f);
            RenderSettings.ambientLight = new Color(.48f, .48f, .49f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            var light = new GameObject("Key light").AddComponent<Light>();
            light.transform.SetParent(stage, false);
            light.transform.rotation = Quaternion.Euler(42, -35, 0);
            light.type = LightType.Directional;
            light.intensity = 1.18f;
            Block("Model table", V(0, -.22f, 0), V(11.1f, .30f, 7.6f), Ink);

            animate = causalV11 ? BuildCausalV11() : observedV10 ? BuildObservedEpisodes() :
                walkthroughV8 ? BuildWalkthroughV8() : episode <= 12 ? BuildRenderingAndWorld() :
                episode <= 24 ? BuildDesignAndProduction() : BuildPresentationAndTesting();
            AddSupportingAssets();
            Evaluate(0);
        }

        public void Evaluate(float time)
        {
            float t = Mathf.Clamp01((time - speechStart) / Mathf.Max(.5f, speechEnd - speechStart));
            animate?.Invoke(t);
            if (walkthroughV8 || observedV10 || causalV11) PlayWalkthroughActors(time);
            else PlayLibraryActors(time);
        }

        Action<float> BuildObservedEpisodes()
        {
            if (episode < 11 || episode > 36) throw new ArgumentOutOfRangeException(nameof(episode));
            if (episode <= 19) return BuildObserved11To19();
            if (episode <= 28) return BuildObserved20To28();
            return BuildObserved29To36();
        }
    }
}
