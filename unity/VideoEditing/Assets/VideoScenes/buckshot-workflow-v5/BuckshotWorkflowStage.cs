using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using System.Security.Cryptography;
using UnityEngine;
using UnityEngine.UI;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.BuckshotWorkflowV5
{
    // An original explanatory set, not a recording of REA, an MCP session or Godot.
    // The imported library's 002/066 CRT rooms and 082 vintage props were considered.
    // They do not express a file/request/branch/assembly operation; purpose-built
    // file sheets, tools and articulated parts make that abstraction visible.
    // No vendor assets or global scene/render settings are modified by this class.
    public sealed class BuckshotWorkflowStage : MonoBehaviour
    {
        public Camera RenderCamera;
        public string Mode;
        public int Frames;
        [Min(0)] public float PreviewTime;
        public const int CaptureLayer = 28;
        public const string AssetRoot = "Assets/VideoScenes/buckshot-workflow-v5";
        public const string GeneratedRoot = AssetRoot + "/Generated";
        public const string AssetSelectionReason = "Original semantic geometry for file inspection, tool requests, code branches and model assembly; library CRT/vintage props would add scenery without explaining these operations.";

        [Serializable] public class Cue { public string name; public float time; public string phrase; }
        [Serializable] public class Cut { public string mode; public int frames; public Cue[] cues; }
        [Serializable] public class Configuration { public Cue[] cues; public Cue[] cueTimes; public Cut[] entries; public Cut[] cuts; }
        [Serializable] sealed class Pose
        {
            public Transform transform; public Vector3 position, scale; public Quaternion rotation; public bool active;
            public bool rect; public Vector2 sizeDelta;
        }
        [Serializable] sealed class TextState { public Text text; public string content; public Color color; }
        [Serializable] sealed class SavedNode { public string key; public GameObject node; }
        [Serializable] sealed class SavedRenderer { public Renderer renderer; public Material material; }
        [Serializable] sealed class BitmapSpec { public string key, text, alignment; public int size, width, height; }
        [Serializable] sealed class BitmapRequest { public string mode, fontSha256, stageSourceSha256; public BitmapSpec[] specs; }
        [Serializable] sealed class BitmapBinding { public Text text; public RawImage image; }
        [Serializable] sealed class SavedBitmap { public string key; public Texture2D texture; }
        readonly Dictionary<string, GameObject> nodes = new Dictionary<string, GameObject>();
        readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        readonly Dictionary<string, float> cueTimes = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase);
        readonly Dictionary<GameObject, bool> desiredVisibility = new Dictionary<GameObject, bool>();
        [SerializeField] List<Pose> poses = new List<Pose>();
        [SerializeField] List<TextState> texts = new List<TextState>();
        [SerializeField] List<SavedNode> savedNodes = new List<SavedNode>();
        [SerializeField] List<SavedRenderer> savedRenderers = new List<SavedRenderer>();
        [SerializeField] List<Cue> savedCues = new List<Cue>();
        [SerializeField] List<BitmapBinding> bitmapBindings = new List<BitmapBinding>();
        [SerializeField] List<SavedBitmap> savedBitmaps = new List<SavedBitmap>();
        [SerializeField] string labelFontSha256;
        readonly Dictionary<string, BitmapSpec> bitmapSpecs = new Dictionary<string, BitmapSpec>();
        readonly Dictionary<string, Texture2D> bitmapTextures = new Dictionary<string, Texture2D>();
        bool collectingBitmaps;
        readonly Dictionary<Renderer, Material> rendererMaterials = new Dictionary<Renderer, Material>();
        [SerializeField] Canvas canvas;
        [SerializeField] Font font;
        [SerializeField] Text heading, detail, note;
        bool initialized;
        float duration;

        public static readonly Color White = Hex("F5F5F5"), Yellow = Hex("E8CF83"), Teal = Hex("73C7C2"),
            Red = Hex("ED9292"), Green = Hex("86CFA3"), Grey = Hex("B8B8B8"), Blue = Hex("9ABFE7"),
            Dark = Hex("1A252A"), Metal = Hex("596A73");
        static Color Hex(string h) { Color c; ColorUtility.TryParseHtmlString("#" + h, out c); return c; }

        public void Initialize(string mode, int frames, string configPath)
        {
            if (initialized) throw new InvalidOperationException("Create a new stage per saved cut; Initialize is single-use.");
            if (frames < 1) throw new ArgumentOutOfRangeException("frames");
            Mode = (mode ?? "").ToLowerInvariant(); Frames = frames; duration = frames / 60f;
            ReadCues(configPath);
            gameObject.layer = CaptureLayer;
            font = LoadFont();
            var cam = Child("Render camera", transform);
            RenderCamera = cam.AddComponent<Camera>();
            cam.transform.localPosition = new Vector3(0, 5.2f, -16);
            cam.transform.LookAt(transform.TransformPoint(new Vector3(0, 1.3f, 0)));
            RenderCamera.orthographic = true; RenderCamera.orthographicSize = 5.3f;
            RenderCamera.aspect = 1920f / 1080f;
            RenderCamera.nearClipPlane = .05f; RenderCamera.farClipPlane = 100;
            RenderCamera.clearFlags = CameraClearFlags.SolidColor; RenderCamera.backgroundColor = Color.black;
            RenderCamera.cullingMask = 1 << CaptureLayer; RenderCamera.enabled = false;
            RenderCamera.allowHDR = false; RenderCamera.allowMSAA = true;
            var cv = Child("Caption-safe explanatory labels", transform, true);
            canvas = cv.AddComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = RenderCamera; canvas.planeDistance = 1; canvas.sortingOrder = 100;
            var scaler = cv.AddComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080); scaler.matchWidthOrHeight = 0;
            Light("Key light", new Vector3(38, -32, 0), 1.85f, Color.white);
            Light("Fill light", new Vector3(25, 130, 0), .8f, Blue);
            Box("base", "Working surface", transform, new Vector3(0, -.52f, .4f), new Vector3(17.2f, .15f, 5), Hex("10181C"));
            heading = Label("title", "", 75, 74, 64, Yellow, 1270, 100, TextAnchor.MiddleLeft);
            detail = Label("detail", "", 75, 174, 50, White, 1750, 95, TextAnchor.MiddleLeft);
            Label("source-kind", "원리 설명 · Unity", 1370, 64, 48, Grey, 485, 80, TextAnchor.MiddleRight);
            note = Label("note", "", 90, 770, 52, White, 1740, 78, TextAnchor.MiddleCenter);
            switch (Mode)
            {
                case "workflow": BuildWorkflow(); break;
                case "rea": BuildRea(); break;
                case "tools": BuildTools(); break;
                case "inventory": BuildInventory(); break;
                case "trace": BuildTrace(); break;
                case "implement": BuildImplement(); break;
                case "tests": BuildTests(); break;
                case "recap": BuildRecap(); break;
                default: throw new ArgumentException("Unknown Buckshot workflow mode: " + Mode);
            }
            // Persist all generated render assets before root's additive-scene save.
            // No animation state is accumulated: arbitrary/backward sample times reset here.
            // Camera/Canvas transforms are engine-driven and are never animated by
            // this stage. Do not replay their pre-layout transforms at sample jumps.
            foreach (var tr in GetComponentsInChildren<Transform>(true))
                if (tr != transform && !(tr is RectTransform) && tr != RenderCamera.transform)
                    poses.Add(new Pose { transform = tr, position = tr.localPosition, rotation = tr.localRotation, scale = tr.localScale, active = tr.gameObject.activeSelf });
            foreach (var tx in GetComponentsInChildren<Text>(true)) texts.Add(new TextState { text = tx, content = tx.text, color = tx.color });
            foreach (var rr in GetComponentsInChildren<Renderer>(true)) { rendererMaterials[rr] = rr.sharedMaterial; savedRenderers.Add(new SavedRenderer { renderer = rr, material = rr.sharedMaterial }); }
            foreach (var pair in nodes) savedNodes.Add(new SavedNode { key = pair.Key, node = pair.Value });
            foreach (var pair in cueTimes) savedCues.Add(new Cue { name = pair.Key, time = pair.Value });
            // Prevent asset creation/import during the render loop.
            Mat(Green); Mat(Hex("193B31"));
            initialized = true;
            PrepareBitmapLabels();
            Apply(0);
        }

        // Saved references and initial poses make every .unity scene independently
        // editable. Select the component, set PreviewTime and invoke this context menu.
        // There is no ExecuteAlways/Update hook to disturb the user's active scene.
        [ContextMenu("Apply PreviewTime (seconds)")]
        public void Preview()
        {
            if (!initialized) RestoreSavedState();
            Apply(PreviewTime);
            #if UNITY_EDITOR
            EditorUtility.SetDirty(this);
            #endif
        }
        [ContextMenu("Preview from start")]
        public void PreviewFromStart() { PreviewTime = 0; Preview(); }
        void RestoreSavedState()
        {
            if (savedNodes == null || savedNodes.Count == 0 || !RenderCamera) throw new InvalidOperationException("The saved stage has no scene data");
            nodes.Clear(); foreach (var entry in savedNodes) { if (!entry.node) throw new InvalidOperationException("Missing saved node: " + entry.key); nodes.Add(entry.key, entry.node); }
            cueTimes.Clear(); foreach (var cue in savedCues) cueTimes.Add(cue.name, cue.time);
            rendererMaterials.Clear(); foreach (var entry in savedRenderers) if (entry.renderer) rendererMaterials.Add(entry.renderer, entry.material);
            bitmapTextures.Clear(); foreach (var entry in savedBitmaps) { if (!entry.texture) throw new InvalidOperationException("Missing saved label bitmap: " + entry.key); bitmapTextures.Add(entry.key, entry.texture); }
            duration = Frames / 60f; initialized = true;
        }

        void ReadCues(string path)
        {
            if (string.IsNullOrEmpty(path)) return;
            if (!System.IO.File.Exists(path)) throw new FileNotFoundException("Cue configuration is missing", path);
            var config = JsonUtility.FromJson<Configuration>(System.IO.File.ReadAllText(path));
            if (config == null) throw new InvalidDataException("Invalid cue configuration");
            Cue[] selected = config.cues ?? config.cueTimes;
            var cuts = config.entries ?? config.cuts;
            if (cuts != null) foreach (var cut in cuts)
                if (string.Equals(cut.mode, Mode, StringComparison.OrdinalIgnoreCase))
                {
                    if (cut.frames > 0 && cut.frames != Frames) throw new InvalidDataException("Cue frame count differs from capture request");
                    selected = cut.cues; break;
                }
            if (selected == null) throw new InvalidDataException("No cues for " + Mode);
            foreach (var cue in selected)
            {
                if (string.IsNullOrEmpty(cue.name) || float.IsNaN(cue.time) || float.IsInfinity(cue.time) || cue.time < 0 || cue.time > duration + .1f)
                    throw new InvalidDataException("Invalid cue in " + Mode);
                if (cueTimes.ContainsKey(cue.name)) throw new InvalidDataException("Duplicate cue: " + cue.name);
                cueTimes[cue.name] = cue.time;
            }
        }
        float At(string name, float fraction) { return cueTimes.TryGetValue(name, out float t) ? t : duration * fraction; }
        static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }
        static float Phase(float t, float a, float b) { return Ease((t - a) / Mathf.Max(.05f, b - a)); }
        bool Reached(float t, string cue, float fraction) { return t >= At(cue, fraction); }
        void Show(string key, bool show) { if (nodes.TryGetValue(key, out var go)) desiredVisibility[go] = show; }
        void Position(string key, Vector3 p) { nodes[key].transform.localPosition = p; }
        void Scale(string key, float s) { nodes[key].transform.localScale = Vector3.one * s; }
        void ColorNode(string key, Color color)
        {
            foreach (var rr in nodes[key].GetComponentsInChildren<Renderer>(true)) { var mat = Mat(color, rr is LineRenderer); if (rr.sharedMaterial != mat) rr.sharedMaterial = mat; }
        }
        void TextValue(string key, string value, Color? color = null)
        {
            var tx = nodes[key].GetComponent<Text>(); tx.text = value; if (color.HasValue) tx.color = color.Value;
        }
        public void Apply(float t)
        {
            if (!initialized) RestoreSavedState();
            t = Mathf.Clamp(t, 0, duration);
            desiredVisibility.Clear();
            foreach (var item in savedNodes) desiredVisibility[item.node] = true;
            foreach (var pose in poses)
            {
                if (!pose.transform) continue;
                pose.transform.localPosition = pose.position; pose.transform.localRotation = pose.rotation; pose.transform.localScale = pose.scale;
                if (pose.rect) ((RectTransform)pose.transform).sizeDelta = pose.sizeDelta;
                desiredVisibility[pose.transform.gameObject] = pose.active;
            }
            foreach (var tx in texts) { tx.text.text = tx.content; tx.text.color = tx.color; }
            foreach (var rr in rendererMaterials) if (rr.Key && rr.Key.sharedMaterial != rr.Value) rr.Key.sharedMaterial = rr.Value;
            switch (Mode)
            {
                case "workflow": AnimateWorkflow(t); break;
                case "rea": AnimateRea(t); break;
                case "tools": AnimateTools(t); break;
                case "inventory": AnimateInventory(t); break;
                case "trace": AnimateTrace(t); break;
                case "implement": AnimateImplement(t); break;
                case "tests": AnimateTests(t); break;
                case "recap": AnimateRecap(t); break;
            }
            // Apply each final visibility once, avoiding false→true→false toggles
            // which needlessly invalidate the editor's renderer registration.
            foreach (var pair in desiredVisibility) if (pair.Key && pair.Key.activeSelf != pair.Value) pair.Key.SetActive(pair.Value);
            RefreshTextGeometry();
        }

        void RefreshTextGeometry()
        {
            if (collectingBitmaps)
            {
                foreach (var tx in texts) if (tx.text && !string.IsNullOrEmpty(tx.text.text))
                { var spec = Spec(tx.text); if (!bitmapSpecs.ContainsKey(spec.key)) bitmapSpecs.Add(spec.key, spec); }
                return;
            }
            foreach (var binding in bitmapBindings)
            {
                var tx = binding.text; tx.enabled = false;
                bool visible = !string.IsNullOrEmpty(tx.text);
                binding.image.gameObject.SetActive(visible);
                if (!visible) continue;
                var spec = Spec(tx);
                if (!bitmapTextures.TryGetValue(spec.key, out var texture)) throw new InvalidOperationException("Unprepared label bitmap: " + tx.text + " / " + spec.key);
                binding.image.texture = texture; binding.image.color = tx.color; binding.image.SetAllDirty();
            }
            Canvas.ForceUpdateCanvases();
        }

        static string HashBytes(byte[] bytes)
        { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        BitmapSpec Spec(Text tx)
        {
            string align = tx.alignment == TextAnchor.MiddleLeft ? "left" : tx.alignment == TextAnchor.MiddleRight ? "right" : "center";
            var spec = new BitmapSpec { text = tx.text, size = tx.fontSize, width = Mathf.RoundToInt(tx.rectTransform.rect.width), height = Mathf.RoundToInt(tx.rectTransform.rect.height), alignment = align };
            string value = "buckshot-label-rgba-v1\n" + labelFontSha256 + "\n" + spec.text + "\n" + spec.size + "\n" + spec.width + "\n" + spec.height + "\n" + align;
            spec.key = HashBytes(Encoding.UTF8.GetBytes(value)); return spec;
        }
        void PrepareBitmapLabels()
        {
            #if UNITY_EDITOR
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));
            string production = Path.Combine(repo, "projects/buckshot-roulette-reverse-engineering/production");
            string cache = Path.Combine(production, "local/unity-v5/label-cache"); Directory.CreateDirectory(cache);
            string fontFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Fonts), "malgun.ttf");
            labelFontSha256 = HashBytes(System.IO.File.ReadAllBytes(fontFile));
            collectingBitmaps = true;
            // Only text/layout combinations actually produced by this mode are
            // requested. No frame rendering, TTS or audio operation occurs here.
            var times = new SortedSet<float> { 0, duration };
            foreach (var cue in savedCues) { times.Add(Mathf.Max(0, cue.time - 1f / 120)); times.Add(cue.time); times.Add(Mathf.Min(duration, cue.time + .05f)); }
            for (int i = 1; i < 41; ++i) times.Add(duration * i / 40f);
            foreach (float t in times) Apply(t);
            collectingBitmaps = false;
            var specs = new List<BitmapSpec>(bitmapSpecs.Values); specs.Sort((a, b) => string.CompareOrdinal(a.key, b.key));
            string stageSource = Path.Combine(Application.dataPath, "VideoScenes/buckshot-workflow-v5/BuckshotWorkflowStage.cs");
            var request = new BitmapRequest { mode = Mode, fontSha256 = labelFontSha256, stageSourceSha256 = HashBytes(System.IO.File.ReadAllBytes(stageSource)), specs = specs.ToArray() };
            string requestText = JsonUtility.ToJson(request, true);
            string requestPath = Path.Combine(cache, Mode + "-" + HashBytes(Encoding.UTF8.GetBytes(requestText)) + ".request.json");
            if (!System.IO.File.Exists(requestPath)) System.IO.File.WriteAllText(requestPath, requestText, new UTF8Encoding(false));
            string helper = Path.Combine(production, "rasterize-unity-labels-v5.py");
            var start = new System.Diagnostics.ProcessStartInfo
            {
                FileName = Path.Combine(repo, "qwen3-tts/.venv/Scripts/python.exe"),
                Arguments = "\"" + helper + "\" \"" + requestPath + "\" \"" + cache + "\"",
                UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true
            };
            using (var process = System.Diagnostics.Process.Start(start))
            {
                string stdout = process.StandardOutput.ReadToEnd(), stderr = process.StandardError.ReadToEnd(); process.WaitForExit();
                if (process.ExitCode != 0) throw new InvalidOperationException("Label rasterization failed: " + stderr);
                System.IO.File.WriteAllText(requestPath + ".execution.json", stdout, new UTF8Encoding(false));
            }
            EnsureFolder(GeneratedRoot + "/Labels");
            foreach (var spec in specs)
            {
                string assetPath = GeneratedRoot + "/Labels/" + spec.key + ".asset";
                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
                if (!texture)
                {
                    string png = Path.Combine(cache, spec.key + ".png");
                    texture = new Texture2D(2, 2, TextureFormat.RGBA32, false, false) { name = "Text " + spec.key, filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp };
                    if (!texture.LoadImage(System.IO.File.ReadAllBytes(png), false)) throw new InvalidDataException("Could not load label bitmap: " + spec.key);
                    AssetDatabase.CreateAsset(texture, assetPath);
                }
                if (texture.width != spec.width || texture.height != spec.height) throw new InvalidDataException("Stored label dimensions differ: " + spec.key);
                bitmapTextures.Add(spec.key, texture); savedBitmaps.Add(new SavedBitmap { key = spec.key, texture = texture });
            }
            foreach (var state in texts)
            {
                var tx = state.text;
                var child = Child("Static white type — " + tx.name, tx.transform, true);
                var rect = child.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one; rect.offsetMin = rect.offsetMax = Vector2.zero;
                var raw = child.AddComponent<RawImage>(); raw.raycastTarget = false; tx.enabled = false;
                bitmapBindings.Add(new BitmapBinding { text = tx, image = raw });
            }
            #else
            throw new InvalidOperationException("Prepare the editable bitmap stage in Unity Editor before runtime use");
            #endif
        }

        void BuildWorkflow()
        {
            heading.text = "기존 게임 → 새 프로토타입";
            detail.text = "구조를 확인하고, 규칙과 새로운 외형을 연결합니다";
            Package("w.source", new Vector3(-5.4f, .15f, 0));
            Server("w.agent", new Vector3(-1.8f, .1f, 0), Teal);
            Robot("w.model", new Vector3(1.8f, .02f, 0), .88f);
            Monitor("w.engine", new Vector3(5.2f, .1f, 0), Teal);
            Track("w.a", new Vector3(-4.5f, .9f, -.5f), new Vector3(-2.7f, .9f, -.5f), Teal);
            Track("w.b", new Vector3(-.8f, .9f, -.5f), new Vector3(.8f, .9f, -.5f), Yellow);
            Track("w.c", new Vector3(2.7f, .9f, -.5f), new Vector3(4.2f, .9f, -.5f), Green);
            Packet("w.packet", Teal);
            BottomLabel("w.l1", "기존 게임", 380); BottomLabel("w.l2", "구조 · 규칙", 770);
            BottomLabel("w.l3", "새 외형", 1160); BottomLabel("w.l4", "작동하는 결과", 1540);
            Label("w.engine-label", "Unity · Unreal · Godot", 1250, 290, 48, Grey, 590, 70);
        }
        void AnimateWorkflow(float t)
        {
            float logic = At("logic", .13f), resources = At("resources", .26f), agent = At("agent", .37f), assets = At("assets", .54f), engine = At("engine", .71f), result = At("result", .86f);
            Show("w.agent", t >= logic); Show("w.model", t >= assets); Show("w.engine", t >= engine);
            Show("w.a", t >= logic); Show("w.b", t >= assets); Show("w.c", t >= engine);
            Show("w.engine-label", t >= engine); Show("w.l2", t >= logic); Show("w.l3", t >= assets); Show("w.l4", t >= engine);
            OpenPackage("w.source", Phase(t, resources, resources + 2));
            AssembleRobot("w.model", Phase(t, assets, Mathf.Min(engine, assets + 3)));
            if (t < assets) Travel("w.packet", t, logic, agent, new Vector3(-4.5f, 1.1f, -.7f), new Vector3(-1.8f, 1.1f, -.7f));
            else if (t < engine) Travel("w.packet", t, assets, assets + 2.4f, new Vector3(-1, 1.1f, -.7f), new Vector3(1.8f, 1.1f, -.7f));
            else Travel("w.packet", t, engine, result, new Vector3(2.5f, 1.1f, -.7f), new Vector3(5.2f, 1.1f, -.7f));
            note.text = t < logic ? "완성된 게임에서 출발" : t < assets ? "게임 로직 + 모델·텍스처·애니메이션" : t < engine ? "분석한 규칙을 바탕으로 새로운 리소스 준비" : "규칙과 외형을 게임 엔진에서 연결";
            if (t >= result) { ScreenPulse("w.engine", t - result); note.color = Green; }
        }

        void BuildRea()
        {
            heading.text = "REA · Reverse Engineer Anything";
            detail.text = "게임 파일을 살펴보고, 분석 작업을 돕는 도구";
            Monitor("r.agent", new Vector3(-5.25f, .1f, 0), Blue);
            Server("r.tool", new Vector3(0, .1f, 0), Teal);
            Package("r.source", new Vector3(5.25f, .1f, 0));
            Magnifier("r.glass", new Vector3(4.7f, 2.25f, -.8f), .72f);
            Track("r.request", new Vector3(-4.1f, 1.5f, -.5f), new Vector3(4.1f, 1.5f, -.5f), Teal);
            Track("r.response", new Vector3(4.1f, .6f, -.9f), new Vector3(-4.1f, .6f, -.9f), Yellow);
            Packet("r.packet", Teal); File("r.answer", new Vector3(4, 1, -1), Yellow, .42f);
            BottomLabel("r.l1", "AI 에이전트", 395); BottomLabel("r.l2", "REA", 960); BottomLabel("r.l3", "게임 패키지", 1525);
            Label("r.message", "파일 목록 요청", 540, 315, 50, Teal, 840, 80);
        }
        void AnimateRea(float t)
        {
            float agent = At("agent", .26f), inspect = At("inspect", .46f), evidence = At("evidence", .65f), verify = At("verify", .81f);
            Show("r.agent", t >= agent); Show("r.l1", t >= agent); Show("r.glass", t >= inspect);
            Show("r.request", t >= inspect); Show("r.response", t >= evidence); Show("r.message", t >= inspect);
            Travel("r.packet", t, inspect, evidence, new Vector3(-4.1f, 1.5f, -.7f), new Vector3(4.1f, 1.5f, -.7f));
            Travel("r.answer", t, evidence, verify, new Vector3(4.1f, .7f, -1), new Vector3(-4.1f, .7f, -1));
            OpenPackage("r.source", Phase(t, inspect, inspect + 1.8f));
            if (t >= inspect) nodes["r.glass"].transform.localPosition += new Vector3(1.1f * Phase(t, inspect, evidence), -.25f * Phase(t, inspect, evidence), 0);
            note.text = t < agent ? "게임 구조를 읽기 위한 분석 도구" : t < inspect ? "에이전트: 목표에 맞춰 도구를 선택하는 AI" : t < evidence ? "요청 → REA가 파일을 확인" : t < verify ? "파일 목록과 읽은 내용을 에이전트에게 반환" : "근거를 읽고 → 필요한 파일을 다시 확인";
            if (t >= evidence) TextValue("r.message", "분석 결과 반환", Yellow);
            if (t >= verify)
            {
                TextValue("r.message", "다음 요청: 필요한 함수 읽기", Teal);
                Travel("r.packet", t, verify, verify + 2.2f, new Vector3(-4.1f, 1.5f, -.7f), new Vector3(0, 1.5f, -.7f));
            }
        }

        void BuildTools()
        {
            heading.text = "도구는 필요한 작업에 맞춰 연결";
            detail.text = "CLI는 직접 실행 · MCP는 AI와 외부 도구를 연결";
            var direct = Group("t.direct", transform);
            Monitor("t.cli", new Vector3(-5.1f, .1f, 0), Blue, direct.transform);
            Server("t.rea", new Vector3(0, .1f, 0), Teal, direct.transform);
            Package("t.file", new Vector3(5.1f, .1f, 0), direct.transform);
            Track("t.direct-line", new Vector3(-4, 1.1f, -.8f), new Vector3(4, 1.1f, -.8f), Teal, false, direct.transform);
            Packet("t.packet", Teal, direct.transform);
            var options = Group("t.options", transform);
            Magnifier("t.ghidra", new Vector3(-4.5f, 1.4f, 0), 1.1f, options.transform);
            File("t.resource", new Vector3(0, 1.1f, 0), Blue, 1, options.transform);
            Robot("t.model", new Vector3(4.6f, .1f, 0), .9f, options.transform);
            Track("t.option-a", new Vector3(-3.3f, .5f, -.7f), new Vector3(-1.2f, .5f, -.7f), Grey, true, options.transform);
            Track("t.option-b", new Vector3(1.2f, .5f, -.7f), new Vector3(3.3f, .5f, -.7f), Grey, true, options.transform);
            BottomLabel("t.l1", "명령줄 · CLI", 400); BottomLabel("t.l2", "REA", 960); BottomLabel("t.l3", "게임 자료", 1520);
            Label("t.route", "직접 실행", 460, 300, 54, Teal, 1000, 75);
            Label("t.engines", "Unity  ·  Unreal  ·  Godot", 330, 680, 52, Green, 1260, 75);
        }
        void AnimateTools(float t)
        {
            float mcp = At("mcp", .15f), definition = At("mcp_definition", .23f), logic = At("logic", .35f), resources = At("resources", .44f), assets = At("assets", .57f), blender = At("blender", .67f), engine = At("engine", .77f), result = At("result", .92f);
            bool optional = t >= logic;
            Show("t.direct", !optional); Show("t.options", optional); Show("t.engines", t >= engine);
            Show("t.option-a", t >= resources); Show("t.option-b", t >= assets); Show("t.resource", t >= resources); Show("t.model", t >= assets);
            if (!optional)
            {
                TextValue("t.l1", t < mcp ? "명령줄 · CLI" : "AI 에이전트", Blue);
                TextValue("t.route", t < mcp ? "직접 실행" : "MCP · 도구 연결 규격", Teal);
                Travel("t.packet", t, t < mcp ? 0 : mcp, t < mcp ? Mathf.Max(1, mcp - .4f) : logic, new Vector3(-4, 1.1f, -1), new Vector3(4, 1.1f, -1));
                note.text = t < mcp ? "CLI: 사람이 명령을 입력해 도구를 실행" : t < definition ? "AI 에이전트 ↔ MCP ↔ 외부 도구" : "MCP · Model Context Protocol";
            }
            else
            {
                detail.text = "일반 도구 선택지 · 작업에 필요한 경로를 선택";
                TextValue("t.route", "기계어 / 리소스 / 외형", Grey);
                TextValue("t.l1", "Ghidra", Blue); TextValue("t.l2", "리소스 도구", Teal);
                TextValue("t.l3", t < blender ? "Tripo MCP" : "Tripo · Blender", Yellow);
                Show("t.l2", t >= resources); Show("t.l3", t >= assets);
                AssembleRobot("t.model", Phase(t, assets, blender + 1.3f));
                note.text = t < resources ? "기계어를 분석해야 할 때: Ghidra" : t < assets ? "모델·텍스처·애니메이션의 구조 확인" : t < blender ? "Tripo MCP: 3D 생성 도구 연결" : t < engine ? "Blender: 모델을 만들고 편집" : "규칙과 외형을 게임 엔진에 통합";
                if (t >= engine) { Show("t.l1", false); Show("t.l2", false); Show("t.l3", false); }
                if (t >= result) { detail.text = "이제 이번 실험에서 실제 사용한 경로로"; note.text = "REA CLI → 새 코드 + Blender → Godot"; note.color = Green; }
            }
        }

        void BuildInventory()
        {
            heading.text = "실행 파일 안에는 무엇이 들어 있을까?";
            detail.text = "실제 REA CLI 분석 결과를 구조로 표현";
            Package("i.package", new Vector3(-5.1f, .1f, 0));
            Magnifier("i.glass", new Vector3(-1.8f, 1.9f, -.5f), 1);
            for (int i = 0; i < 9; ++i)
                File("i.file" + i, new Vector3(2.2f + (i % 3) * 1.05f, .55f + (i / 3) * .4f, .5f + (i / 3) * .3f), i >= 6 ? Yellow : Grey, .45f);
            Track("i.path", new Vector3(-3.9f, .8f, -.7f), new Vector3(1.2f, .8f, -.7f), Teal);
            Packet("i.packet", Teal);
            BottomLabel("i.l1", "게임 패키지", 405); BottomLabel("i.l2", "REA로 내부 확인", 900); BottomLabel("i.l3", "파일 목록", 1450);
            Label("i.count", "", 1030, 285, 64, White, 760, 90);
            Label("i.scripts", "", 1080, 355, 52, Yellow, 710, 75);
        }
        void AnimateInventory(float t)
        {
            float inspect = At("inspect", .28f), files = At("files", .54f), scripts = At("scripts", .74f), count = At("script_count", .85f);
            Show("i.glass", t >= inspect); Show("i.path", t >= inspect);
            OpenPackage("i.package", Phase(t, inspect, files));
            Travel("i.packet", t, inspect, files, new Vector3(-3.9f, .8f, -.8f), new Vector3(1.2f, .8f, -.8f));
            for (int i = 0; i < 9; ++i)
            {
                float enter = files + .085f * i;
                Show("i.file" + i, t >= enter);
                if (t >= enter) nodes["i.file" + i].transform.localPosition += Vector3.left * (1 - Phase(t, enter, enter + .6f)) * 1.6f;
            }
            if (t >= files) TextValue("i.count", "내부 파일  3,572개");
            if (t >= scripts) TextValue("i.scripts", t >= count ? "GDScript  195개" : "읽을 수 있는 GDScript");
            note.text = t < inspect ? "실행 파일에서 패키지 구조 확인" : t < scripts ? "파일 개수는 실제 분석 목록의 집계" : "텍스트 코드를 읽어 함수와 상태 변화를 추적";
        }

        void BuildTrace()
        {
            heading.text = "함수가 바꾸는 값을 따라갑니다";
            detail.text = "읽을 수 있는 GDScript · 함수와 공유 상태의 관계";
            Monitor("f.code", new Vector3(-5.3f, .1f, 0), Blue);
            CodeNode("f.shoot", new Vector3(-1.2f, 1.9f, 0), Teal);
            CodeNode("f.turn", new Vector3(2.3f, 2.15f, .3f), Yellow);
            CodeNode("f.items", new Vector3(2.3f, .3f, -.4f), Green);
            File("f.rules", new Vector3(5.6f, 1.25f, 0), White, .85f);
            Track("f.a", new Vector3(-4.1f, 1.5f, -.3f), new Vector3(-2, 1.9f, -.3f), Blue);
            Track("f.b", new Vector3(3.2f, 2.1f, -.3f), new Vector3(4.9f, 1.5f, -.3f), Yellow);
            Track("f.c", new Vector3(3.2f, .6f, -.6f), new Vector3(4.9f, 1.3f, -.6f), Green);
            Track("f.d", new Vector3(-.3f, 1.9f, -.9f), new Vector3(4.9f, 1.45f, -.9f), Teal);
            Packet("f.packet", Teal);
            Label("f.shoot-label", "사격 처리", 695, 304, 50, Teal, 300, 80);
            Label("f.turn-label", "차례 전환", 1090, 285, 50, Yellow, 330, 80);
            Label("f.items-label", "아이템 처리", 1090, 525, 50, Green, 330, 80);
            BottomLabel("f.l1", "텍스트 코드", 385); BottomLabel("f.l3", "규칙 정리", 1555);
        }
        void AnimateTrace(float t)
        {
            float funcs = At("functions", .25f), shoot = At("shoot", .43f), turn = At("turn", .57f), items = At("items", .69f), rules = At("rules", .83f);
            Show("f.shoot", t >= funcs); Show("f.shoot-label", t >= funcs); Show("f.a", t >= funcs);
            Show("f.turn", t >= turn); Show("f.turn-label", t >= turn); Show("f.b", t >= turn);
            Show("f.items", t >= items); Show("f.items-label", t >= items); Show("f.c", t >= items);
            Show("f.rules", t >= funcs); Show("f.l3", t >= funcs); Show("f.d", t >= shoot);
            TextValue("f.l3", t < rules ? "공유 상태" : "규칙 정리");
            if (t < turn) Travel("f.packet", t, shoot, turn, new Vector3(-1.2f, 1.9f, -1), new Vector3(5.6f, 1.45f, -1));
            else if (t < items) Travel("f.packet", t, turn, items, new Vector3(2.3f, 2.2f, -.5f), new Vector3(5.6f, 1.5f, -.5f));
            else if (t < rules) Travel("f.packet", t, items, rules, new Vector3(2.3f, .6f, -.7f), new Vector3(5.6f, 1.3f, -.7f));
            else Show("f.packet", false);
            note.text = t < funcs ? "이번에는 읽을 수 있는 텍스트 코드" : t < shoot ? "어떤 함수가 무엇을 바꾸는가?" : t < turn ? "사격: 탄환 사용과 피해" : t < items ? "차례: 다음 행동 주체 결정" : t < rules ? "아이템: 정보·피해·차례에 연결" : "공유 상태에 연결된 함수들을 규칙으로 정리";
        }

        void BuildImplement()
        {
            heading.text = "규칙을 새 코드로 옮겨 검사";
            detail.text = "검증 예시: 맨 앞 공포탄 + 자기 자신 선택";
            Monitor("p.code", new Vector3(-5.4f, .1f, 0), Blue);
            Robot("p.player", new Vector3(5.1f, .03f, 0), .9f);
            for (int i = 0; i < 4; ++i) Shell("p.shell" + i, new Vector3(-2 + i * .95f, .25f, -.2f), i == 0 ? Teal : i % 2 == 0 ? Teal : Red);
            Track("p.path", new Vector3(-1.8f, 1.25f, -.7f), new Vector3(4.1f, 1.25f, -.7f), Teal);
            Packet("p.packet", Teal);
            Label("p.fixture", "공포탄  →  자기 자신", 540, 290, 52, Teal, 720, 80);
            BottomLabel("p.l1", "독립 재구현", 380); BottomLabel("p.l2", "탄환 4", 900); BottomLabel("p.l3", "체력 3", 1490);
            Label("p.result", "차례: 플레이어", 1280, 290, 52, Green, 550, 80);
        }
        void AnimateImplement(float t)
        {
            float fixture = At("fixture", .2f), target = At("target", .38f), ammo = At("ammo", .51f), health = At("health", .64f), turn = At("turn", .75f), verify = At("verify", .86f);
            for (int i = 0; i < 4; ++i) Show("p.shell" + i, t >= fixture);
            Show("p.fixture", t >= fixture); Show("p.path", t >= target); Show("p.player", t >= target); Show("p.l3", t >= target); Show("p.result", t >= turn);
            Travel("p.packet", t, target, ammo + .55f, new Vector3(-1.8f, 1.25f, -.8f), new Vector3(4.1f, 1.25f, -.8f));
            if (t >= ammo)
            {
                var u = Phase(t, ammo, ammo + .7f); nodes["p.shell0"].transform.localPosition += new Vector3(0, -.8f * u, -u);
                Show("p.shell0", u < 1); TextValue("p.l2", "탄환 4 → 3", Teal);
                for (int i = 1; i < 4; ++i) nodes["p.shell" + i].transform.localPosition += Vector3.left * .95f * u;
            }
            if (t >= health) TextValue("p.l3", "체력 3 → 3", Green);
            note.text = t < fixture ? "새 프로젝트에 탄환·차례 관리 코드 작성" : t < target ? "입력 상태를 먼저 고정" : t < ammo ? "자기 자신에게 공포탄 사용" : t < health ? "탄환은 한 발 줄어듭니다" : t < turn ? "피해 0 · 체력 유지" : t < verify ? "자기 공포탄 · 같은 차례 유지" : "같은 입력 → 기대한 결과";
            if (t >= verify) { note.color = Green; ScreenPulse("p.code", t - verify); }
        }

        void BuildTests()
        {
            heading.text = "규칙 검사 다음에는 화면과 함께 검사";
            detail.text = "단위 검사 → 실제 입력·애니메이션·문구 연결";
            Server("q.rules", new Vector3(-5.2f, .1f, 0), Teal);
            Box("q.gate", "Input gate", transform, new Vector3(-.25f, .65f, -.25f), new Vector3(.18f, 1.8f, 1.3f), Red);
            for (int i = 0; i < 3; ++i) Sphere("q.dot" + i, transform, new Vector3(-2.1f - i * .6f, .85f, -.4f), .25f, Yellow);
            Robot("q.actor", new Vector3(3.7f, .1f, 0), .95f);
            Track("q.input", new Vector3(-3.5f, .9f, -.7f), new Vector3(2.6f, .9f, -.7f), Teal);
            BottomLabel("q.l1", "규칙 검사", 410); BottomLabel("q.l2", "입력 잠금", 930); BottomLabel("q.l3", "화면 · 동작", 1410);
            Label("q.count", "374개 통과", 115, 305, 62, Green, 590, 90);
            Label("q.reason", "동작 중", 665, 365, 54, Red, 660, 80);
            Label("q.cause", "수갑  ≠  자기 공포탄", 650, 275, 52, Yellow, 950, 75);
        }
        void AnimateTests(float t)
        {
            float integration = At("integration", .16f), input = At("input", .31f), cause = At("cause", .49f), fix = At("fix", .67f), passed = At("passed", .78f), verify = At("verify", .9f);
            Show("q.actor", t >= integration); Show("q.gate", t >= input); Show("q.reason", t >= input); Show("q.cause", t >= cause); Show("q.input", t >= integration);
            Show("q.l2", t >= input); Show("q.l3", t >= integration);
            for (int i = 0; i < 3; ++i)
            {
                Show("q.dot" + i, t >= input);
                float u = Phase(t, input + i * .15f, input + 1.4f + i * .15f);
                nodes["q.dot" + i].transform.localPosition += Vector3.right * (1.55f - i * .12f) * u;
                if (t >= fix) nodes["q.dot" + i].transform.localPosition += Vector3.right * 3.8f * Phase(t, fix + i * .2f, fix + 1.8f + i * .2f);
            }
            if (t >= input && t < fix) nodes["q.actor.handL"].transform.localPosition += Vector3.up * .4f * Phase(t, input, input + .8f);
            if (t >= fix)
            {
                float open = Phase(t, fix, fix + .7f);
                nodes["q.gate"].transform.localPosition += Vector3.up * 1.2f * open;
                nodes["q.gate"].transform.localRotation = Quaternion.Euler(0, 0, 90 * open);
                ColorNode("q.gate", Green); TextValue("q.reason", "완료 → 입력 허용", Green);
                TextValue("q.cause", "차례 유지 원인을 구분", Green);
            }
            if (t >= passed) { TextValue("q.count", "374 / 32 통과", Green); TextValue("q.l1", "규칙 / 통합"); }
            note.text = t < integration ? "독립 규칙 코드의 374개 검사 통과" : t < input ? "화면을 연결하면 새로운 확인 지점이 생깁니다" : t < cause ? "도구 동작이 끝나기 전에는 다음 입력 차단" : t < fix ? "같은 차례 유지도 원인은 다릅니다" : t < passed ? "입력 잠금과 안내 문구 수정" : t < verify ? "규칙 + 화면의 통합 검사 32개 통과" : "무엇을 막았고 어떤 문구를 고쳤는지 확인";
        }

        void BuildRecap()
        {
            heading.text = "분석을 내 아이디어의 기반으로";
            detail.text = "이번 실험의 실제 경로";
            Package("s.source", new Vector3(-6.4f, .1f, 0), null, .72f);
            Server("s.rea", new Vector3(-3.3f, .1f, 0), Teal, null, .72f);
            Monitor("s.code", new Vector3(-.2f, .1f, 0), Blue, null, .75f);
            Robot("s.model", new Vector3(2.7f, .1f, 0), .8f);
            Monitor("s.engine", new Vector3(5.8f, .1f, 0), Green, null, .82f);
            for (int i = 0; i < 4; ++i) Track("s.path" + i, new Vector3(-5.5f + i * 3.05f, 1, -.6f), new Vector3(-4.3f + i * 3.05f, 1, -.6f), i == 3 ? Green : Teal);
            Packet("s.packet", Teal);
            BottomLabel("s.l0", "기존 게임", 270, 285); BottomLabel("s.l1", "REA CLI", 605, 285); BottomLabel("s.l2", "새 코드", 940, 285); BottomLabel("s.l3", "Blender", 1250, 285); BottomLabel("s.l4", "Godot", 1590, 285);
            Label("s.result", "플레이 가능한 프로토타입", 1100, 300, 52, Green, 710, 100);
        }
        void AnimateRecap(float t)
        {
            float rea = At("rea", .08f), script = At("script", .2f), code = At("code", .31f), models = At("models", .44f), engine = At("engine", .56f), result = At("result", .67f), conclusion = At("conclusion", .81f);
            float[] starts = { rea, code, models, engine };
            string[] keys = { "s.rea", "s.code", "s.model", "s.engine" };
            for (int i = 0; i < 4; ++i) { Show(keys[i], t >= starts[i]); Show("s.path" + i, t >= starts[i]); Show("s.l" + (i + 1), t >= starts[i]); }
            Show("s.result", t >= result); OpenPackage("s.source", Phase(t, rea, script));
            AssembleRobot("s.model", Phase(t, models, engine));
            int leg = t < code ? 0 : t < models ? 1 : t < engine ? 2 : 3;
            float end = leg == 0 ? code : leg == 1 ? models : leg == 2 ? engine : result;
            Travel("s.packet", t, starts[leg], end, new Vector3(-5.5f + leg * 3.05f, 1, -.8f), new Vector3(-3.3f + leg * 3.05f, 1, -.8f));
            note.text = t < rea ? "실제 게임에서 출발" : t < script ? "REA로 게임의 구조 확인" : t < code ? "읽을 수 있는 코드에서 핵심 규칙 분리" : t < models ? "규칙을 독립적인 새 코드로 작성" : t < engine ? "Blender에서 새로운 외형 제작" : t < result ? "Godot에서 규칙과 외형 연결" : t < conclusion ? "직접 플레이하며 아이디어 확인" : "추측을 줄이고, 내 아이디어를 시험할 기반";
            if (t >= result) ScreenPulse("s.engine", t - result);
            if (t >= conclusion) note.color = Green;
        }

        // Reusable original models. The same concrete objects carry the narrative
        // between modes, while tool-route illustrations never masquerade as tool UI.
        GameObject Group(string key, Transform parent, Vector3? position = null)
        { var go = Child(key, parent ?? transform); go.transform.localPosition = position ?? Vector3.zero; nodes.Add(key, go); return go; }
        static GameObject Child(string name, Transform parent, bool rect = false)
        { var go = rect ? new GameObject(name, typeof(RectTransform)) : new GameObject(name); go.layer = CaptureLayer; go.transform.SetParent(parent, false); return go; }
        GameObject Primitive(string key, string name, PrimitiveType type, Transform parent, Vector3 pos, Vector3 scale, Color color)
        {
            var go = GameObject.CreatePrimitive(type); go.name = name; go.transform.SetParent(parent ?? transform, false); go.layer = CaptureLayer;
            go.transform.localPosition = pos; go.transform.localScale = scale;
            var collider = go.GetComponent<Collider>(); if (collider) DestroyImmediate(collider);
            go.GetComponent<Renderer>().sharedMaterial = Mat(color);
            if (!string.IsNullOrEmpty(key)) nodes.Add(key, go); return go;
        }
        GameObject Box(string key, string name, Transform parent, Vector3 pos, Vector3 scale, Color c) { return Primitive(key, name, PrimitiveType.Cube, parent, pos, scale, c); }
        GameObject Sphere(string key, Transform parent, Vector3 p, float diameter, Color c) { return Primitive(key, key ?? "Joint", PrimitiveType.Sphere, parent, p, Vector3.one * diameter, c); }
        void Rod(Transform parent, Vector3 a, Vector3 b, float radius, Color c)
        {
            var go = Primitive(null, "Articulated connector", PrimitiveType.Cylinder, parent, (a + b) / 2, new Vector3(radius * 2, (b - a).magnitude / 2, radius * 2), c);
            go.transform.localRotation = Quaternion.FromToRotation(Vector3.up, b - a);
        }
        void Light(string name, Vector3 rotation, float intensity, Color color)
        {
            var go = Child(name, transform); go.transform.localEulerAngles = rotation;
            var light = go.AddComponent<Light>(); light.type = LightType.Directional; light.color = color; light.intensity = intensity;
            light.cullingMask = 1 << CaptureLayer; light.shadows = LightShadows.Soft; light.shadowStrength = .5f;
        }
        void File(string key, Vector3 pos, Color c, float scale = 1, Transform parent = null)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            Box(null, "Thick file sheet", root.transform, Vector3.zero, new Vector3(1.1f, 1.42f, .14f), c);
            Box(null, "Folded corner", root.transform, new Vector3(.38f, .53f, -.1f), new Vector3(.26f, .24f, .06f), White).transform.localEulerAngles = new Vector3(0, 0, 45);
            for (int i = 0; i < 4; ++i) Box(null, "Readable content line", root.transform, new Vector3(-.06f, .28f - i * .23f, -.095f), new Vector3(i == 3 ? .42f : .68f, .055f, .04f), Dark);
        }
        void Package(string key, Vector3 pos, Transform parent = null, float scale = 1)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            Box(null, "Package base", root.transform, new Vector3(0, .13f, 0), new Vector3(2.2f, .24f, 1.3f), Metal);
            Box(null, "Package back", root.transform, new Vector3(0, .78f, .58f), new Vector3(2.2f, 1.4f, .15f), Dark);
            Box(null, "Package left", root.transform, new Vector3(-1.02f, .65f, 0), new Vector3(.16f, 1.15f, 1.2f), Metal);
            Box(null, "Package right", root.transform, new Vector3(1.02f, .65f, 0), new Vector3(.16f, 1.15f, 1.2f), Metal);
            Box(key + ".lid", "Package lid", root.transform, new Vector3(0, 1.38f, 0), new Vector3(2.23f, .12f, 1.3f), Teal);
            for (int i = 0; i < 3; ++i) File(key + ".file" + i, new Vector3(-.55f + .55f * i, .78f, -.13f - .08f * i), i == 2 ? Yellow : White, .48f, root.transform);
            Box(null, "Package nameplate", root.transform, new Vector3(0, .3f, -.69f), new Vector3(.78f, .17f, .055f), Teal);
        }
        void OpenPackage(string key, float progress)
        {
            nodes[key + ".lid"].transform.localPosition += new Vector3(0, 1.1f, .25f) * progress;
            nodes[key + ".lid"].transform.localRotation = Quaternion.Euler(-38 * progress, 0, 0);
            for (int i = 0; i < 3; ++i) nodes[key + ".file" + i].transform.localPosition += Vector3.up * (.5f + i * .12f) * progress;
        }
        void Server(string key, Vector3 pos, Color color, Transform parent = null, float scale = 1)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            Box(null, "Tool chassis", root.transform, new Vector3(0, 1.1f, .1f), new Vector3(1.7f, 2.35f, 1.15f), Metal);
            for (int i = 0; i < 3; ++i)
            {
                Box(null, "Tool module", root.transform, new Vector3(0, .38f + i * .63f, -.51f), new Vector3(1.45f, .44f, .12f), Dark);
                Box(null, "Module activity stripe", root.transform, new Vector3(-.25f, .38f + i * .63f, -.59f), new Vector3(.7f, .075f, .04f), color);
                Sphere(null, root.transform, new Vector3(.5f, .38f + i * .63f, -.62f), .105f, color);
            }
            Box(null, "Tool handle", root.transform, new Vector3(0, 2.4f, .1f), new Vector3(.7f, .12f, .32f), color);
        }
        void Monitor(string key, Vector3 pos, Color color, Transform parent = null, float scale = 1)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            Box(null, "Monitor foot", root.transform, new Vector3(0, .12f, 0), new Vector3(1.5f, .14f, .85f), Metal);
            Rod(root.transform, new Vector3(0, .13f, .1f), new Vector3(0, .72f, .1f), .13f, Metal);
            Box(null, "Monitor shell", root.transform, new Vector3(0, 1.48f, .1f), new Vector3(2.1f, 1.58f, .4f), Metal);
            Box(key + ".screen", "Semantic display", root.transform, new Vector3(0, 1.48f, -.13f), new Vector3(1.86f, 1.3f, .06f), Dark);
            for (int i = 0; i < 4; ++i) Box(null, "Code semantic line", root.transform, new Vector3(-.16f + .1f * (i % 2), 1.86f - .25f * i, -.18f), new Vector3(i % 2 == 0 ? 1.15f : .84f, .065f, .035f), i == 0 ? Yellow : i == 2 ? color : Grey);
            Box(null, "Keyboard", root.transform, new Vector3(0, .23f, -.63f), new Vector3(1.55f, .1f, .49f), Dark);
            for (int i = 0; i < 5; ++i) Box(null, "Keyboard key", root.transform, new Vector3(-.58f + .29f * i, .3f, -.63f), new Vector3(.17f, .055f, .23f), Grey);
        }
        void ScreenPulse(string key, float t)
        {
            // A single deterministic completion reveal, not a repeated idle pulse.
            if (t >= .2f) ColorNode(key + ".screen", Hex("193B31"));
        }
        void Robot(string key, Vector3 pos, float scale, Transform parent = null)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            Box(null, "Table top", root.transform, new Vector3(0, .45f, -.35f), new Vector3(2.2f, .16f, 1.2f), Metal);
            Rod(root.transform, new Vector3(-.8f, -.15f, -.35f), new Vector3(-.8f, .4f, -.35f), .09f, Metal);
            Rod(root.transform, new Vector3(.8f, -.15f, -.35f), new Vector3(.8f, .4f, -.35f), .09f, Metal);
            Primitive(null, "Robot torso", PrimitiveType.Capsule, root.transform, new Vector3(0, 1.4f, .35f), new Vector3(.85f, .72f, .6f), Teal);
            Sphere(null, root.transform, new Vector3(0, 2, .35f), .28f, Yellow);
            var head = Group(key + ".head", root.transform, new Vector3(0, 2.35f, .25f));
            Box(null, "Articulated head", head.transform, Vector3.zero, new Vector3(.95f, .69f, .65f), Grey);
            Box(null, "Face plate", head.transform, new Vector3(0, .03f, -.36f), new Vector3(.75f, .43f, .07f), Dark);
            for (int i = -1; i <= 1; i += 2) Sphere(null, head.transform, new Vector3(i * .21f, .08f, -.42f), .15f, Teal);
            Box(null, "Mouth indicator", head.transform, new Vector3(0, -.14f, -.42f), new Vector3(.33f, .045f, .04f), Yellow);
            Rod(head.transform, new Vector3(.3f, .34f, 0), new Vector3(.3f, .67f, 0), .035f, Metal);
            Sphere(null, head.transform, new Vector3(.3f, .72f, 0), .13f, Yellow);
            for (int side = -1; side <= 1; side += 2)
            {
                string handKey = key + (side < 0 ? ".handL" : ".handR");
                var hand = Group(handKey, root.transform, new Vector3(side * .76f, 1.09f, -.14f));
                Sphere(null, hand.transform, new Vector3(0, .32f, .2f), .27f, Yellow);
                Rod(hand.transform, new Vector3(0, .3f, .2f), new Vector3(side * .12f, -.1f, -.22f), .1f, Teal);
                Sphere(null, hand.transform, new Vector3(side * .12f, -.1f, -.22f), .24f, Metal);
                for (int finger = -1; finger <= 1; finger += 2) Rod(hand.transform, new Vector3(side * .12f + finger * .1f, -.12f, -.25f), new Vector3(side * .12f + finger * .16f, -.25f, -.48f), .045f, Grey);
            }
        }
        void AssembleRobot(string key, float progress)
        {
            nodes[key + ".head"].transform.localPosition += Vector3.up * 1.2f * (1 - progress);
            nodes[key + ".handL"].transform.localPosition += Vector3.left * 1.2f * (1 - progress);
            nodes[key + ".handR"].transform.localPosition += Vector3.right * 1.2f * (1 - progress);
        }
        void Shell(string key, Vector3 pos, Color color)
        {
            var root = Group(key, transform, pos);
            Primitive(null, "Shell body", PrimitiveType.Cylinder, root.transform, new Vector3(0, .43f, 0), new Vector3(.4f, .36f, .4f), color);
            Primitive(null, "Shell brass rim", PrimitiveType.Cylinder, root.transform, new Vector3(0, .12f, 0), new Vector3(.46f, .075f, .46f), Yellow);
        }
        void CodeNode(string key, Vector3 pos, Color color)
        {
            var root = Group(key, transform, pos);
            Box(null, "Function module", root.transform, Vector3.zero, new Vector3(1.7f, .72f, .75f), Dark);
            for (int side = -1; side <= 1; side += 2)
            {
                var line = new[] { new Vector3(side * .45f, .19f, -.42f), new Vector3(side * .7f, 0, -.42f), new Vector3(side * .45f, -.19f, -.42f) };
                Polyline(null, "Code bracket", root.transform, line, color, .065f);
            }
            Sphere(null, root.transform, new Vector3(0, 0, -.44f), .15f, Yellow);
        }
        void Magnifier(string key, Vector3 pos, float scale, Transform parent = null)
        {
            var root = Group(key, parent, pos); root.transform.localScale = Vector3.one * scale;
            var ring = Child("Magnifying ring", root.transform); var filter = ring.AddComponent<MeshFilter>();
            filter.sharedMesh = RingMesh(); ring.AddComponent<MeshRenderer>().sharedMaterial = Mat(Yellow);
            Rod(root.transform, new Vector3(.45f, -.45f, 0), new Vector3(1.03f, -1.12f, 0), .14f, Metal);
            Rod(root.transform, new Vector3(.83f, -.89f, 0), new Vector3(1.14f, -1.25f, 0), .18f, Teal);
        }
        Mesh RingMesh()
        {
            const string path = GeneratedRoot + "/Meshes/magnifier-ring.asset";
            #if UNITY_EDITOR
            var prior = AssetDatabase.LoadAssetAtPath<Mesh>(path); if (prior) return prior;
            EnsureFolder(GeneratedRoot + "/Meshes");
            #endif
            int rings = 64, sides = 10; var v = new Vector3[rings * sides]; var n = new Vector3[v.Length]; var tri = new int[rings * sides * 6];
            for (int i = 0; i < rings; ++i) for (int j = 0; j < sides; ++j)
            {
                float a = i * Mathf.PI * 2 / rings, b = j * Mathf.PI * 2 / sides;
                var normal = new Vector3(Mathf.Cos(a) * Mathf.Cos(b), Mathf.Sin(a) * Mathf.Cos(b), Mathf.Sin(b));
                int k = i * sides + j; v[k] = new Vector3(Mathf.Cos(a), Mathf.Sin(a), 0) * .64f + normal * .085f; n[k] = normal;
                int right = ((i + 1) % rings) * sides + j, up = i * sides + (j + 1) % sides, corner = ((i + 1) % rings) * sides + (j + 1) % sides, q = k * 6;
                tri[q] = k; tri[q + 1] = right; tri[q + 2] = up; tri[q + 3] = up; tri[q + 4] = right; tri[q + 5] = corner;
            }
            var mesh = new Mesh { name = "Original magnifier ring", vertices = v, normals = n, triangles = tri }; mesh.RecalculateBounds();
            #if UNITY_EDITOR
            AssetDatabase.CreateAsset(mesh, path);
            #endif
            return mesh;
        }
        void Packet(string key, Color color, Transform parent = null)
        { Sphere(key, parent ?? transform, Vector3.zero, .29f, color); }
        void Travel(string key, float t, float start, float end, Vector3 a, Vector3 b)
        {
            bool visible = t >= start && t <= end + .35f; Show(key, visible);
            if (visible) Position(key, Vector3.Lerp(a, b, Phase(t, start, end)));
        }
        void Track(string key, Vector3 a, Vector3 b, Color color, bool dashed = false, Transform parent = null)
        {
            var root = Group(key, parent);
            if (dashed) for (int i = 0; i < 10; ++i) Polyline(null, "Optional route dash", root.transform, new[] { Vector3.Lerp(a, b, i / 10f), Vector3.Lerp(a, b, (i + .55f) / 10f) }, color, .045f);
            else Polyline(null, "Request route", root.transform, new[] { a, b }, color, .055f);
            var delta = (b - a).normalized; var side = Vector3.Cross(Vector3.forward, delta).normalized;
            Polyline(null, "Direction arrow", root.transform, new[] { b - delta * .23f + side * .16f, b, b - delta * .23f - side * .16f }, color, .055f);
        }
        GameObject Polyline(string key, string name, Transform parent, Vector3[] points, Color color, float width)
        {
            var go = Child(name, parent); if (key != null) nodes.Add(key, go);
            var line = go.AddComponent<LineRenderer>(); line.useWorldSpace = false; line.positionCount = points.Length; line.SetPositions(points);
            line.widthMultiplier = width; line.numCapVertices = 6; line.numCornerVertices = 6; line.sharedMaterial = Mat(color, true); return go;
        }
        void BottomLabel(string key, string text, float x, float width = 430) { Label(key, text, x - width / 2, 685, 50, White, width, 80); }
        Text Label(string key, string value, float x, float y, int size, Color color, float width, float height, TextAnchor align = TextAnchor.MiddleCenter)
        {
            if (size < 48) throw new ArgumentOutOfRangeException("size", "Video labels must be at least 48px");
            var go = Child(key, canvas.transform, true); nodes.Add(key, go);
            var rect = go.GetComponent<RectTransform>(); rect.anchorMin = rect.anchorMax = new Vector2(.5f, .5f);
            float displayScale = size / 64f;
            rect.sizeDelta = new Vector2(width, height) / displayScale; rect.localScale = Vector3.one * displayScale;
            rect.anchoredPosition = new Vector2(x + width / 2 - 960, 540 - y - height / 2);
            var tx = go.AddComponent<Text>(); tx.font = font; tx.text = value; tx.fontSize = 64; tx.color = color; tx.alignment = align;
            tx.horizontalOverflow = HorizontalWrapMode.Wrap; tx.verticalOverflow = VerticalWrapMode.Truncate; tx.supportRichText = true; tx.raycastTarget = false; return tx;
        }
        Material Mat(Color color, bool unlit = false)
        {
            string key = ColorUtility.ToHtmlStringRGBA(color) + (unlit ? "-unlit" : "-lit");
            if (materials.TryGetValue(key, out var old)) return old;
            #if UNITY_EDITOR
            EnsureFolder(GeneratedRoot + "/Materials");
            string path = GeneratedRoot + "/Materials/" + key + ".mat";
            var stored = AssetDatabase.LoadAssetAtPath<Material>(path); if (stored) { materials[key] = stored; return stored; }
            #endif
            var shader = Shader.Find(unlit ? "Universal Render Pipeline/Unlit" : "Universal Render Pipeline/Lit");
            if (!shader) throw new InvalidOperationException("URP shader is unavailable");
            var mat = new Material(shader) { name = "Buckshot workflow " + key }; mat.SetColor("_BaseColor", color);
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", .35f);
            #if UNITY_EDITOR
            AssetDatabase.CreateAsset(mat, path);
            #endif
            materials[key] = mat; return mat;
        }
        Font LoadFont()
        {
            #if UNITY_EDITOR
            EnsureFolder(GeneratedRoot + "/Fonts");
            string path = GeneratedRoot + "/Fonts/MalgunGothic.fontsettings";
            var prior = AssetDatabase.LoadAssetAtPath<Font>(path); if (prior) return prior;
            #endif
            var created = Font.CreateDynamicFontFromOSFont("Malgun Gothic", 64);
            if (!created) throw new InvalidOperationException("Malgun Gothic is required for Korean video labels");
            created.name = "Buckshot workflow — Malgun Gothic OS reference";
            #if UNITY_EDITOR
            AssetDatabase.CreateAsset(created, path);
            #endif
            return created;
        }
        #if UNITY_EDITOR
        static void EnsureFolder(string path)
        {
            string[] bits = path.Replace('\\', '/').Split('/'); string current = bits[0];
            for (int i = 1; i < bits.Length; ++i) { string next = current + "/" + bits[i]; if (!AssetDatabase.IsValidFolder(next)) AssetDatabase.CreateFolder(current, bits[i]); current = next; }
        }
        #endif
    }
}
