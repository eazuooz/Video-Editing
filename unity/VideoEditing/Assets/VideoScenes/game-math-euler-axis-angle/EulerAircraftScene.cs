using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace YamyamCoding.GameMath.EulerAxisAngle
{
    /// <summary>
    /// Deterministic, self-authored explanation illustration. This is not
    /// commercial gameplay or a measured flight simulation. Each .unity asset
    /// stores its own lesson scene and timing. No editor auto-run or capture.
    /// </summary>
    public sealed class EulerAircraftScene : MonoBehaviour
    {
        public string sceneId = "03";
        public string lessonMode = "euler";
        [Min(1f)] public float durationSeconds = 30f;
        [Range(0f, 1f)] public float normalizedTime;
        public bool playInRuntime = false;
        public bool showWorldAxes = true;
        public bool showBodyAxes = true;
        public Color background = Color.white;
        public Vector3 cameraMathPosition = new Vector3(7f, 4.5f, 8f);
        public float orthographicSize = 4.9f;
        public Vector3 cameraMathTarget = new Vector3(0f, -.35f, 0f);
        public bool useLectureLayout = true;
        public Vector2 singleFocusPixels = new Vector2(580f, 470f);
        public Vector2 leftFocusPixels = new Vector2(560f, 470f);
        public Vector2 rightFocusPixels = new Vector2(1320f, 470f);
        public float singleLayoutOrthoSize = 3.6f;
        public float pairLayoutOrthoSize = 3.9f;
        public float pairAircraftScale = .80f;
        public const int CaptureWidth = 1920, CaptureHeight = 1080, CaptureFps = 60;
        [SerializeField, HideInInspector] private Camera savedSceneCamera;
        [SerializeField, HideInInspector] private Transform savedAircraftA, savedAircraftB;
        public Camera SceneCamera { get => savedSceneCamera; private set => savedSceneCamera = value; }
        public Transform AircraftA { get => savedAircraftA; private set => savedAircraftA = value; }
        public Transform AircraftB { get => savedAircraftB; private set => savedAircraftB = value; }
        public Matrix4x4 MathRotationA { get; private set; } = Matrix4x4.identity;
        public Matrix4x4 MathRotationB { get; private set; } = Matrix4x4.identity;
        public string StageLabel { get; private set; } = "initial";

        [SerializeField, HideInInspector] private Transform generated, worldAxes, axisAngleGuide;
        [SerializeField, HideInInspector] private Transform alternateAxisGuide;
        private readonly List<Material> ownedMaterials = new List<Material>();
        private readonly Dictionary<string, Material> materialCache = new Dictionary<string, Material>();
        private readonly List<Mesh> ownedMeshes = new List<Mesh>();
        [SerializeField, HideInInspector] private Transform aileronLeftA, aileronRightA, elevatorA, rudderA;
        [SerializeField, HideInInspector] private Transform aileronLeftB, aileronRightB, elevatorB, rudderB;
        private float startTime;
        private Vector3 eulerA, eulerB, rotationVectorA, rotationVectorB;
        private bool hasEulerA, hasEulerB, hasRotationVectorA, hasRotationVectorB;
        private static readonly Color AxisX = new Color32(213, 52, 66, 255);
        private static readonly Color AxisY = new Color32(21, 133, 76, 255);
        private static readonly Color AxisZ = new Color32(34, 100, 195, 255);

        private void Start()
        {
            // Keep the editor-saved editable hierarchy, meshes and manual
            // source edits on playback. Older source scenes are rebound by
            // name rather than discarded because private fields were unsaved.
            if (!BindSavedGeometry())
            {
                if (transform.Find("Generated lesson geometry") != null)
                {
                    Debug.LogError("M04 saved geometry is incomplete; restore its aircraft/camera or explicitly rebuild. Existing edits were preserved.", this);
                    enabled = false;
                    return;
                }
                Build();
            }
            AdaptSavedMaterialsToActivePipeline();
            startTime = Time.time;
            Evaluate(normalizedTime);
        }
        private void Update()
        {
            if (Application.isPlaying && playInRuntime)
                Evaluate(Mathf.Clamp01((Time.time - startTime) / durationSeconds));
        }
        public bool HasTwoAircraft => lessonMode == "extrinsic" || lessonMode == "order"
            || lessonMode == "aliases" || lessonMode == "gimbal-values" || lessonMode == "interpolation"
            || lessonMode == "axis-aliases" || lessonMode == "nonadd";

        private static bool UsesSrp()
        {
            // Before the first rendered frame currentRenderPipeline may be
            // null although the selected quality/default asset is already URP.
            return GraphicsSettings.currentRenderPipeline != null
                || QualitySettings.renderPipeline != null || GraphicsSettings.defaultRenderPipeline != null;
        }
        public bool BindSavedGeometry()
        {
            if (generated == null) generated = transform.Find("Generated lesson geometry");
            if (generated == null) return false;
            if (SceneCamera == null) SceneCamera = generated.GetComponentInChildren<Camera>(true);
            if (AircraftA == null) AircraftA = generated.Find("Aircraft A");
            if (AircraftB == null) AircraftB = generated.Find("Aircraft B");
            if (worldAxes == null) worldAxes = generated.Find("Fixed world axes");
            if (axisAngleGuide == null) axisAngleGuide = generated.Find("Axis angle guide");
            if (alternateAxisGuide == null) alternateAxisGuide = generated.Find("B explicit rotation axis");
            if (AircraftA != null)
            {
                if (aileronLeftA == null) aileronLeftA = AircraftA.Find("Port hinged aileron");
                if (aileronRightA == null) aileronRightA = AircraftA.Find("Starboard hinged aileron");
                if (elevatorA == null) elevatorA = AircraftA.Find("Hinged elevator");
                if (rudderA == null) rudderA = AircraftA.Find("Hinged rudder");
            }
            if (AircraftB != null)
            {
                if (aileronLeftB == null) aileronLeftB = AircraftB.Find("Port hinged aileron");
                if (aileronRightB == null) aileronRightB = AircraftB.Find("Starboard hinged aileron");
                if (elevatorB == null) elevatorB = AircraftB.Find("Hinged elevator");
                if (rudderB == null) rudderB = AircraftB.Find("Hinged rudder");
            }
            return SceneCamera != null && AircraftA != null && worldAxes != null && (!HasTwoAircraft || AircraftB != null);
        }

        [ContextMenu("Adapt saved materials to active render pipeline")]
        public void AdaptSavedMaterialsToActivePipeline()
        {
            if (!BindSavedGeometry()) return;
            bool srp = UsesSrp();
            var adapted = new Dictionary<Material, Material>();
            foreach (Renderer renderer in generated.GetComponentsInChildren<Renderer>(true))
            {
                Material original = renderer.sharedMaterial;
                if (original == null || original.shader == null) continue;
                string originalName = original.shader.name;
                bool alreadyCompatible = srp ? originalName.StartsWith("Universal Render Pipeline/", StringComparison.Ordinal)
                    : !originalName.StartsWith("Universal Render Pipeline/", StringComparison.Ordinal);
                if (alreadyCompatible) continue;
                if (!adapted.TryGetValue(original, out Material copy))
                {
                    bool unlit = originalName.IndexOf("Unlit", StringComparison.OrdinalIgnoreCase) >= 0;
                    Shader target = Shader.Find(srp ? (unlit ? "Universal Render Pipeline/Unlit" : "Universal Render Pipeline/Lit")
                        : (unlit ? "Unlit/Color" : "Standard"));
                    if (target == null)
                    {
                        Debug.LogError("M04 target shader is unavailable; install/restore the existing project package lock before preview. Original source material was preserved.", this);
                        continue;
                    }
                    Color color = original.HasProperty("_BaseColor") ? original.GetColor("_BaseColor")
                        : original.HasProperty("_Color") ? original.GetColor("_Color") : Color.white;
                    float smoothness = original.HasProperty("_Smoothness") ? original.GetFloat("_Smoothness")
                        : original.HasProperty("_Glossiness") ? original.GetFloat("_Glossiness") : .22f;
                    // Clone only the material instance; never edit a canonical
                    // .mat asset, switch the project pipeline, or rebuild meshes.
                    copy = new Material(target) { name = original.name + " active-pipeline instance" };
                    copy.color = color;
                    if (copy.HasProperty("_BaseColor")) copy.SetColor("_BaseColor", color);
                    if (copy.HasProperty("_Color")) copy.SetColor("_Color", color);
                    if (copy.HasProperty("_Smoothness")) copy.SetFloat("_Smoothness", smoothness);
                    if (copy.HasProperty("_Glossiness")) copy.SetFloat("_Glossiness", smoothness);
                    if (copy.HasProperty("_Metallic")) copy.SetFloat("_Metallic", 0f);
                    if (copy.HasProperty("_Cull")) copy.SetFloat("_Cull", 0f);
                    ownedMaterials.Add(copy); adapted.Add(original, copy);
                }
                renderer.sharedMaterial = copy;
            }
        }

        [ContextMenu("Build editable lesson objects")]
        public void Build()
        {
            ClearOwned();
            generated = NewObject("Generated lesson geometry", transform);
            SceneCamera = NewObject("1080p60 fixed camera", generated).gameObject.AddComponent<Camera>();
            SceneCamera.clearFlags = CameraClearFlags.SolidColor;
            SceneCamera.backgroundColor = background;
            SceneCamera.orthographic = true;
            SceneCamera.orthographicSize = useLectureLayout
                ? (HasTwoAircraft ? pairLayoutOrthoSize : singleLayoutOrthoSize) : orthographicSize;
            SceneCamera.aspect = CaptureWidth / (float)CaptureHeight;
            SceneCamera.nearClipPlane = .05f; SceneCamera.farClipPlane = 80f;
            SceneCamera.allowHDR = false; SceneCamera.allowMSAA = true;
            SceneCamera.transform.position = EulerMathContract.ToUnity(cameraMathPosition);
            SceneCamera.transform.LookAt(EulerMathContract.ToUnity(cameraMathTarget), Vector3.up);
            // The camera is scene-owned; this does not modify PlayerSettings or active render pipeline.
            var key = NewObject("Key light", generated).gameObject.AddComponent<Light>();
            key.type = LightType.Directional; key.intensity = 1.05f;
            key.transform.rotation = Quaternion.Euler(38f, -27f, 0f); key.shadows = LightShadows.None;
            var fill = NewObject("Fill light", generated).gameObject.AddComponent<Light>();
            fill.type = LightType.Directional; fill.intensity = .55f;
            fill.transform.rotation = Quaternion.Euler(325f, 145f, 0f); fill.shadows = LightShadows.None;
            worldAxes = NewObject("Fixed world axes", generated);
            BuildAxes(worldAxes, 2.75f, .023f, .58f);
            worldAxes.gameObject.SetActive(showWorldAxes && !HasTwoAircraft);
            float separation = HasTwoAircraft ? 3.6f : 0f;
            AircraftA = BuildAircraft("Aircraft A", new Vector3(-separation, .25f, 0f),
                out aileronLeftA, out aileronRightA, out elevatorA, out rudderA);
            if (HasTwoAircraft)
            {
                AircraftB = BuildAircraft("Aircraft B", new Vector3(separation, .25f, 0f),
                    out aileronLeftB, out aileronRightB, out elevatorB, out rudderB);
                if (showWorldAxes)
                {
                    Transform fixedA = NewObject("A fixed world axes", generated);
                    fixedA.localPosition = AircraftA.localPosition;
                    BuildAxes(fixedA, 2.75f, .022f, .55f);
                    Transform fixedB = NewObject("B fixed world axes", generated);
                    fixedB.localPosition = AircraftB.localPosition;
                    BuildAxes(fixedB, 2.75f, .022f, .55f);
                }
            }
            axisAngleGuide = NewObject("Axis angle guide", generated);
            BuildArrow(axisAngleGuide, Vector3.zero, Vector3.up * 3.3f, AxisY, .045f);
            axisAngleGuide.gameObject.SetActive(lessonMode == "axis-angle" || lessonMode == "rotation-vector"
                || lessonMode == "axis-aliases");
            if (lessonMode == "axis-aliases" || lessonMode == "nonadd")
            {
                alternateAxisGuide = NewObject("B explicit rotation axis", generated);
                Vector3 axis = lessonMode == "nonadd" ? new Vector3(1f, 1f, 0f).normalized : Vector3.down;
                BuildArrow(alternateAxisGuide, Vector3.zero, axis * 3.3f,
                    lessonMode == "nonadd" ? new Color32(177, 129, 0, 255) : AxisY, .045f);
            }
            if (lessonMode == "gimbal" || lessonMode == "gimbal-values")
            {
                // Rings are orientation guides, with centerlines defined by the exact matrices.
                BuildRing(NewObject("Heading fixed Y ring", generated), Vector3.up, 2.40f, AxisY, .028f);
            }
            ApplyLectureLayout();
            Evaluate(normalizedTime);
        }

        private void ApplyLectureLayout()
        {
            if (!useLectureLayout) return;
            float depth = SceneCamera.WorldToViewportPoint(Vector3.zero).z;
            PlaceAtPixel(AircraftA, HasTwoAircraft ? leftFocusPixels : singleFocusPixels, depth);
            if (AircraftB != null)
            {
                AircraftA.localScale = Vector3.one * pairAircraftScale;
                AircraftB.localScale = Vector3.one * pairAircraftScale;
                PlaceAtPixel(AircraftB, rightFocusPixels, depth);
            }
            worldAxes.position = AircraftA.position;
            Transform fixedA = generated.Find("A fixed world axes"), fixedB = generated.Find("B fixed world axes");
            if (fixedA != null) { fixedA.position = AircraftA.position; fixedA.localScale = AircraftA.localScale; }
            if (fixedB != null) { fixedB.position = AircraftB.position; fixedB.localScale = AircraftB.localScale; }
            axisAngleGuide.position = AircraftA.position;
            if (alternateAxisGuide != null && AircraftB != null) alternateAxisGuide.position = AircraftB.position;
            Transform ring = generated.Find("Heading fixed Y ring");
            if (ring != null) ring.position = AircraftA.position;
        }
        private void PlaceAtPixel(Transform target, Vector2 pixel, float depth)
        {
            target.position = SceneCamera.ViewportToWorldPoint(new Vector3(pixel.x / CaptureWidth,
                1f - pixel.y / CaptureHeight, depth));
        }

        public void Evaluate(float t)
        {
            normalizedTime = Mathf.Clamp01(t);
            float s = normalizedTime;
            Matrix4x4 a = Matrix4x4.identity, b = Matrix4x4.identity;
            float h = 0f, p = 0f, bank = 0f;
            eulerA = eulerB = rotationVectorA = rotationVectorB = Vector3.zero;
            hasEulerA = hasEulerB = hasRotationVectorA = hasRotationVectorB = false;
            switch (lessonMode)
            {
                case "euler":
                    if (s < .32f)
                        bank = 35f * SmoothStage(s, .12f, .24f);
                    else if (s < .48f)
                    {
                        bank = 35f * (1f - SmoothStage(s, .32f, .38f));
                        h = 30f * SmoothStage(s, .38f, .44f) * (1f - SmoothStage(s, .44f, .48f));
                    }
                    else
                    {
                        h = 45f * SmoothStage(s, .48f, .61f);
                        p = 30f * SmoothStage(s, .63f, .76f);
                        bank = 35f * SmoothStage(s, .78f, .91f);
                    }
                    a = EulerMathContract.EulerYXZ(h, p, bank);
                    eulerA = new Vector3(h, p, bank); hasEulerA = true;
                    StageLabel = s < .48f ? "define fixed world frame, body frame, handedness, then apply rotations"
                        : "heading y, moved pitch x, moved bank z";
                    break;
                case "intrinsic":
                    h = 45f * SmoothStage(s, .02f, .16f);
                    p = 30f * SmoothStage(s, .19f, .32f);
                    bank = 35f * SmoothStage(s, .36f, .49f);
                    a = EulerMathContract.EulerYXZ(h, p, bank);
                    eulerA = new Vector3(h, p, bank); hasEulerA = true;
                    StageLabel = s < .18f ? "heading about fixed +y" : s < .35f
                        ? "pitch about moved body +x" : "bank about twice-moved body +z";
                    break;
                case "extrinsic":
                    // A intrinsic Y-X-Z, B extrinsic fixed Z-X-Y, same final pose.
                    if (s < .56f)
                    {
                        h = 45f * SmoothStage(s, .02f, .10f);
                        p = 30f * SmoothStage(s, .12f, .20f);
                        bank = 35f * SmoothStage(s, .22f, .30f);
                        a = EulerMathContract.EulerYXZ(h, p, bank);
                        float eb = 35f * SmoothStage(s, .02f, .10f);
                        float ep = 30f * SmoothStage(s, .12f, .20f);
                        float eh = 45f * SmoothStage(s, .22f, .30f);
                        b = EulerMathContract.Ry(eh) * EulerMathContract.Rx(ep) * EulerMathContract.Rz(eb);
                        eulerA = new Vector3(h, p, bank); eulerB = new Vector3(eh, ep, eb);
                        hasEulerA = hasEulerB = true;
                        StageLabel = s >= .30f ? "same final matrix; different sequence descriptions" : "intrinsic Y-X-Z versus fixed Z-X-Y";
                    }
                    else
                    {
                        // Starting downward: body yaw is post-multiplication,
                        // world heading is pre-multiplication. They differ.
                        float yaw = 35f * SmoothStage(s, .62f, .83f);
                        Matrix4x4 downward = EulerMathContract.Rx(90f);
                        a = downward * EulerMathContract.Ry(yaw);
                        b = EulerMathContract.Ry(yaw) * downward;
                        StageLabel = "downward body: local-y yaw changes forward; fixed-y heading keeps forward down";
                    }
                    break;
                case "order":
                    float first = 90f * SmoothStage(s, .10f, .25f), second = 90f * SmoothStage(s, .29f, .43f);
                    float otherFirst = 90f * SmoothStage(s, .54f, .68f), otherSecond = 90f * SmoothStage(s, .73f, .86f);
                    a = EulerMathContract.Ry(second) * EulerMathContract.Rx(first);
                    b = EulerMathContract.Rx(otherSecond) * EulerMathContract.Ry(otherFirst);
                    StageLabel = s < .50f ? "A fixed X then fixed Y" : "B same starting orientation; fixed Y then fixed X";
                    break;
                case "aliases":
                    if (s < .18f)
                    {
                        h = 360f * SmoothStage(s, .02f, .15f);
                        a = EulerMathContract.Ry(h); b = Matrix4x4.identity;
                        eulerA = new Vector3(h, 0f, 0f); eulerB = Vector3.zero;
                    }
                    else
                    {
                        float aliasA = SmoothStage(s, .22f, .38f), aliasB = SmoothStage(s, .48f, .64f);
                        a = EulerMathContract.EulerYXZ(0f, 135f * aliasA, 0f);
                        b = EulerMathContract.EulerYXZ(180f * aliasB, 45f * aliasB, 180f * aliasB);
                        eulerA = new Vector3(0f, 135f * aliasA, 0f); eulerB = new Vector3(180f * aliasB, 45f * aliasB, 180f * aliasB);
                    }
                    hasEulerA = hasEulerB = true;
                    StageLabel = s > .64f ? "identical final pose; unequal three numbers" : "fullturn then two Euler aliases";
                    break;
                case "gimbal":
                    p = s < .18f ? Mathf.Lerp(45f, 80f, SmoothStage(s, .02f, .15f))
                        : Mathf.Lerp(80f, 90f, SmoothStage(s, .21f, .34f));
                    h = bank = 5f * SmoothStage(s, .51f, .64f);
                    a = EulerMathContract.EulerYXZ(h, p, bank);
                    eulerA = new Vector3(h, p, bank); hasEulerA = true;
                    StageLabel = s < .35f ? "pitch45 then80 then90; body +z approaches fixed -y"
                        : s < .51f ? "+y and body +z share one line, opposite signs"
                        : "at+90pitch, h+5 and b+5 cancel; same endpoint, not a physical loss of rotation";
                    if (s > .82f)
                    {
                        a = EulerMathContract.Rz(20f * SmoothStage(s, .84f, .94f)) * a;
                        hasEulerA = false;
                        StageLabel = "a direct matrix rotation still moves the physical object; Euler singularity is representational";
                    }
                    break;
                case "gimbal-values":
                    float pitchSwitch = SmoothStage(s, .48f, .56f);
                    bool negativePitch = s >= .56f;
                    p = Mathf.Lerp(90f, -90f, pitchSwitch);
                    float collapsedHeading = Mathf.Lerp(20f, 40f, pitchSwitch);
                    a = EulerMathContract.EulerYXZ(30f, p, 10f);
                    b = EulerMathContract.EulerYXZ(collapsedHeading, p, 0f);
                    eulerA = new Vector3(30f, p, 10f); eulerB = new Vector3(collapsedHeading, p, 0f);
                    hasEulerA = hasEulerB = true;
                    StageLabel = negativePitch ? "p=-90: h+b=40; equal full matrices" : "p=+90: h-b=20; equal full matrices";
                    if (pitchSwitch > 0f && pitchSwitch < 1f)
                    {
                        // An explicitly illustrative transition between two
                        // equal-pose examples; no Euler values are asserted
                        // during the transition itself. Endpoints retain the
                        // exact stated positive/negative singular examples.
                        Quaternion from = EulerMathContract.UnityRotation(EulerMathContract.EulerYXZ(30f, 90f, 10f));
                        Quaternion to = EulerMathContract.UnityRotation(EulerMathContract.EulerYXZ(30f, -90f, 10f));
                        a = b = EulerMathContract.MathMatrix(Quaternion.Slerp(from, to, pitchSwitch));
                        hasEulerA = hasEulerB = false;
                        StageLabel = "illustrative transition between equal-pose endpoint examples; displayed Euler triples apply only at endpoints";
                    }
                    break;
                case "interpolation":
                    // Both paths linearly interpolate Euler triples from
                    // identity. Their endpoints are aliases; their middles differ.
                    float u = s;
                    eulerA = new Vector3(0f, 135f * u, 0f);
                    eulerB = new Vector3(180f * u, 45f * u, 180f * u);
                    a = EulerMathContract.EulerYXZ(eulerA.x, eulerA.y, eulerA.z);
                    b = EulerMathContract.EulerYXZ(eulerB.x, eulerB.y, eulerB.z);
                    hasEulerA = hasEulerB = true;
                    StageLabel = "two Euler paths from identity; t=.5 gives(0,67.5,0) versus(90,22.5,90); endpoints equal";
                    break;
                case "axis-angle":
                    float angle = s < .70f ? 90f * SmoothStage(s, .20f, .46f)
                        : Mathf.Lerp(90f, 45f, SmoothStage(s, .72f, .84f));
                    a = EulerMathContract.AxisAngle(Vector3.up, angle);
                    rotationVectorA = Vector3.up * angle * Mathf.Deg2Rad; hasRotationVectorA = true;
                    StageLabel = "unit axis (0,1,0); whole body rotates, not only forward arrow";
                    break;
                case "rotation-vector":
                    float theta = Mathf.PI * .5f * (1f - SmoothStage(s, .64f, .76f));
                    if (s > .83f) theta = Mathf.PI * .5f * SmoothStage(s, .84f, .96f);
                    rotationVectorA = new Vector3(0f, theta, 0f); hasRotationVectorA = true;
                    a = EulerMathContract.RotationVector(rotationVectorA);
                    if (axisAngleGuide != null)
                    {
                        axisAngleGuide.localScale = new Vector3(1f, Mathf.Max(.0001f, theta / 3.3f), 1f);
                        axisAngleGuide.gameObject.SetActive(theta > 1e-7f);
                    }
                    StageLabel = theta < 1e-7f ? "e=zero: identity; axis undefined; normalization prohibited"
                        : "theta>=0; theta=length(e); n=e/length(e) is defined only when nonzero";
                    break;
                case "axis-aliases":
                    float ar = SmoothStage(s, .16f, .78f);
                    float angleA = 90f * ar, angleB = 270f * ar;
                    if (s >= .84f)
                    {
                        float halfTurn = SmoothStage(s, .85f, .94f);
                        angleA = Mathf.Lerp(90f, 180f, halfTurn);
                        angleB = Mathf.Lerp(270f, 180f, halfTurn);
                    }
                    if (s >= .97f) angleA = angleB = 180f * (1f - SmoothStage(s, .97f, 1f));
                    a = EulerMathContract.AxisAngle(Vector3.up, angleA);
                    b = EulerMathContract.AxisAngle(Vector3.down, angleB);
                    rotationVectorA = Vector3.up * angleA * Mathf.Deg2Rad;
                    rotationVectorB = Vector3.down * angleB * Mathf.Deg2Rad;
                    hasRotationVectorA = hasRotationVectorB = true;
                    StageLabel = s < .84f ? "+90 about +y equals +270 about -y only at final pose"
                        : s < .97f ? "at180degrees opposite axes yield same endpoint" : "zero angle gives identity, axis arbitrary";
                    break;
                case "nonadd":
                    float nr = SmoothStage(s, .18f, .65f);
                    a = EulerMathContract.Ry(90f) * EulerMathContract.Rx(90f);
                    rotationVectorB = new Vector3(Mathf.PI * .5f, Mathf.PI * .5f, 0f) * nr;
                    hasRotationVectorB = true;
                    b = EulerMathContract.RotationVector(rotationVectorB);
                    StageLabel = "A sequential fixedX90 thenY90; B sum vector axis(1,1,0)/sqrt2 and angle127.279degrees";
                    break;
            }
            MathRotationA = a; MathRotationB = b;
            if (AircraftA != null) AircraftA.localRotation = EulerMathContract.UnityRotation(a);
            if (AircraftB != null) AircraftB.localRotation = EulerMathContract.UnityRotation(b);
            Deflect(aileronLeftA, aileronRightA, elevatorA, rudderA, p, bank, h);
            Deflect(aileronLeftB, aileronRightB, elevatorB, rudderB, 0f, 0f, 0f);
        }
        private static float SmoothStage(float t, float start, float end)
        {
            float u = Mathf.InverseLerp(start, end, t);
            return u * u * (3f - 2f * u);
        }
        private static void Deflect(Transform left, Transform right, Transform elevator, Transform rudder,
            float pitch, float bank, float heading)
        {
            if (left != null) left.localRotation = EulerMathContract.UnityRotation(EulerMathContract.Rx(-bank * .12f));
            if (right != null) right.localRotation = EulerMathContract.UnityRotation(EulerMathContract.Rx(bank * .12f));
            if (elevator != null) elevator.localRotation = EulerMathContract.UnityRotation(EulerMathContract.Rx(pitch * .12f));
            if (rudder != null) rudder.localRotation = EulerMathContract.UnityRotation(EulerMathContract.Ry(heading * .12f));
        }

        private Transform BuildAircraft(string label, Vector3 mathPosition, out Transform leftAileron,
            out Transform rightAileron, out Transform elevator, out Transform rudder)
        {
            Transform root = NewObject(label, generated);
            root.localPosition = EulerMathContract.ToUnity(mathPosition);
            Color fuselage = new Color32(244, 188, 51, 255);
            Color ivory = new Color32(220, 224, 229, 255);
            Color dark = new Color32(37, 49, 64, 255);
            Color canopy = new Color32(44, 72, 89, 255);
            float[] z = { -2.08f, -1.70f, -1.1f, -.5f, .25f, .85f, 1.45f, 1.86f, 2.08f };
            float[] r = { .04f, .13f, .22f, .28f, .31f, .29f, .21f, .10f, .025f };
            Lathe("Tapered rounded fuselage", root, z, r, fuselage);
            Ellipsoid("Dark cockpit canopy", root, new Vector3(0f, .27f, .45f), new Vector3(.43f, .30f, .93f), canopy);
            Ellipsoid("Cockpit rear frame", root, new Vector3(0f, .28f, .04f), new Vector3(.45f, .32f, .045f), dark);
            Ellipsoid("Nose cone", root, new Vector3(0f, 0f, 1.84f), new Vector3(.23f, .23f, .42f), dark);
            // Each wing has a tapered planform and actual thickness, not a cuboid.
            Wing("Port main wing", root, new[] { new Vector2(-.20f, .52f), new Vector2(-2.22f, -.10f),
                new Vector2(-2.12f, -.51f), new Vector2(-.21f, -.35f) }, .02f, .09f, ivory);
            Wing("Starboard main wing", root, new[] { new Vector2(.20f, .52f), new Vector2(.21f, -.35f),
                new Vector2(2.12f, -.51f), new Vector2(2.22f, -.10f) }, .02f, .09f, ivory);
            Wing("Port yellow wing-tip", root, new[] { new Vector2(-1.98f, -.03f), new Vector2(-2.22f, -.10f),
                new Vector2(-2.12f, -.51f), new Vector2(-1.96f, -.49f) }, .078f, .035f, fuselage);
            Wing("Starboard yellow wing-tip", root, new[] { new Vector2(1.98f, -.03f), new Vector2(1.96f, -.49f),
                new Vector2(2.12f, -.51f), new Vector2(2.22f, -.10f) }, .078f, .035f, fuselage);
            leftAileron = NewObject("Port hinged aileron", root);
            leftAileron.localPosition = EulerMathContract.ToUnity(new Vector3(-1.35f, .03f, -.36f));
            Wing("Port aileron panel", leftAileron, new[] { new Vector2(-.60f, 0f), new Vector2(.55f, .04f),
                new Vector2(.55f, -.12f), new Vector2(-.57f, -.15f) }, 0f, .065f, dark);
            rightAileron = NewObject("Starboard hinged aileron", root);
            rightAileron.localPosition = EulerMathContract.ToUnity(new Vector3(1.35f, .03f, -.36f));
            Wing("Starboard aileron panel", rightAileron, new[] { new Vector2(-.55f, .04f), new Vector2(.60f, 0f),
                new Vector2(.57f, -.15f), new Vector2(-.55f, -.12f) }, 0f, .065f, dark);
            Wing("Tailplane", root, new[] { new Vector2(-1.00f, -1.62f), new Vector2(-.12f, -1.35f),
                new Vector2(.12f, -1.35f), new Vector2(1.00f, -1.62f), new Vector2(.89f, -1.88f),
                new Vector2(-.89f, -1.88f) }, .14f, .065f, ivory);
            elevator = NewObject("Hinged elevator", root);
            elevator.localPosition = EulerMathContract.ToUnity(new Vector3(0f, .14f, -1.76f));
            Wing("Elevator trailing surface", elevator, new[] { new Vector2(-.87f, 0f), new Vector2(.87f, 0f),
                new Vector2(.81f, -.18f), new Vector2(-.81f, -.18f) }, 0f, .055f, fuselage);
            Fin("Vertical tail fin", root, new[] { new Vector2(.14f, -1.16f), new Vector2(.93f, -1.58f),
                new Vector2(.83f, -1.88f), new Vector2(.12f, -1.95f) }, .07f, ivory);
            rudder = NewObject("Hinged rudder", root);
            rudder.localPosition = EulerMathContract.ToUnity(new Vector3(0f, .15f, -1.80f));
            Fin("Rudder trailing surface", rudder, new[] { new Vector2(0f, 0f), new Vector2(.65f, .02f),
                new Vector2(.57f, -.15f), new Vector2(0f, -.15f) }, .075f, fuselage);
            Ellipsoid("Engine exhaust port", root, new Vector3(0f, .0f, -2.035f), new Vector3(.105f, .105f, .07f), dark);
            Ellipsoid("Visible engine intake", root, new Vector3(0f, -.17f, 1.10f), new Vector3(.24f, .11f, .37f), dark);
            // Seams and cabin frame give readable articulated construction at mobile size.
            Segment("Canopy center frame", root, new Vector3(0f, .422f, .14f), new Vector3(0f, .422f, .70f), dark, .022f);
            Segment("Port wing root seam", root, new Vector3(-.30f, .09f, .46f), new Vector3(-.30f, .09f, -.33f), dark, .015f);
            Segment("Starboard wing root seam", root, new Vector3(.30f, .09f, .46f), new Vector3(.30f, .09f, -.33f), dark, .015f);
            if (showBodyAxes)
            {
                Transform axes = NewObject("Moving body axes", root);
                BuildAxes(axes, 2.7f, .038f, 1f);
            }
            return root;
        }

        private void Lathe(string label, Transform parent, float[] zs, float[] radii, Color color)
        {
            const int sides = 32;
            var verts = new List<Vector3>(); var tris = new List<int>();
            for (int k = 0; k < zs.Length; k++) for (int j = 0; j < sides; j++)
            {
                float a = j * Mathf.PI * 2f / sides;
                verts.Add(new Vector3(Mathf.Cos(a) * radii[k], Mathf.Sin(a) * radii[k] * .85f, zs[k]));
            }
            for (int k = 0; k < zs.Length - 1; k++) for (int j = 0; j < sides; j++)
            {
                int i = k * sides + j, n = k * sides + (j + 1) % sides;
                tris.AddRange(new[] { i, n, i + sides, n, n + sides, i + sides });
            }
            CreateMesh(label, parent, verts.ToArray(), tris.ToArray(), color);
        }
        private void Wing(string label, Transform parent, Vector2[] xz, float y, float thickness, Color color)
        {
            var verts = new Vector3[xz.Length * 2]; var tris = new List<int>(); int n = xz.Length;
            for (int i = 0; i < n; i++)
            {
                verts[i] = new Vector3(xz[i].x, y + thickness * .5f, xz[i].y);
                verts[i + n] = new Vector3(xz[i].x, y - thickness * .5f, xz[i].y);
            }
            for (int i = 1; i < n - 1; i++) tris.AddRange(new[] { 0, i + 1, i, n, n + i, n + i + 1 });
            for (int i = 0; i < n; i++) { int j = (i + 1) % n; tris.AddRange(new[] { i, i + n, j, j, i + n, j + n }); }
            CreateMesh(label, parent, verts, tris.ToArray(), color);
        }
        private void Fin(string label, Transform parent, Vector2[] yz, float width, Color color)
        {
            var v = new Vector3[yz.Length * 2]; var t = new List<int>(); int n = yz.Length;
            for (int i = 0; i < n; i++) { v[i] = new Vector3(-width * .5f, yz[i].x, yz[i].y); v[i + n] = new Vector3(width * .5f, yz[i].x, yz[i].y); }
            for (int i = 1; i < n - 1; i++) t.AddRange(new[] { 0, i + 1, i, n, n + i, n + i + 1 });
            for (int i = 0; i < n; i++) { int j = (i + 1) % n; t.AddRange(new[] { i, j, i + n, j, j + n, i + n }); }
            CreateMesh(label, parent, v, t.ToArray(), color);
        }
        private void CreateMesh(string label, Transform parent, Vector3[] mathVerts, int[] mathTriangles, Color color)
        {
            var mesh = new Mesh { name = label + " self-authored mesh" };
            // Reflection reverses triangle winding, so compensate when mapping authored RH geometry.
            for (int i = 0; i < mathVerts.Length; i++) mathVerts[i] = EulerMathContract.ToUnity(mathVerts[i]);
            for (int i = 0; i < mathTriangles.Length; i += 3)
            { int swap = mathTriangles[i + 1]; mathTriangles[i + 1] = mathTriangles[i + 2]; mathTriangles[i + 2] = swap; }
            mesh.vertices = mathVerts; mesh.triangles = mathTriangles; mesh.RecalculateNormals(); mesh.RecalculateBounds();
            ownedMeshes.Add(mesh);
            Transform obj = NewObject(label, parent);
            obj.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = obj.gameObject.AddComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, false);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void Ellipsoid(string label, Transform parent, Vector3 mathCenter, Vector3 dimensions, Color color)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Sphere); obj.name = label;
            obj.transform.SetParent(parent, false); obj.transform.localPosition = EulerMathContract.ToUnity(mathCenter);
            obj.transform.localScale = dimensions;
            var collider = obj.GetComponent<Collider>(); if (collider != null) DestroyOwnedObject(collider);
            var renderer = obj.GetComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, false);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void BuildAxes(Transform parent, float length, float radius, float strength)
        {
            BuildArrow(parent, Vector3.zero, Vector3.right * length, Color.Lerp(Color.white, AxisX, strength), radius);
            BuildArrow(parent, Vector3.zero, Vector3.up * length, Color.Lerp(Color.white, AxisY, strength), radius);
            BuildArrow(parent, Vector3.zero, Vector3.forward * length, Color.Lerp(Color.white, AxisZ, strength), radius);
        }
        private void BuildArrow(Transform parent, Vector3 start, Vector3 end, Color color, float radius)
        {
            Vector3 d = (end - start).normalized;
            Segment("Axis shaft", parent, start, end - d * .23f, color, radius);
            const int sides = 20;
            var verts = new Vector3[sides + 2]; var tris = new List<int>();
            Vector3 u = Vector3.Cross(d, Mathf.Abs(d.y) < .9f ? Vector3.up : Vector3.right).normalized;
            Vector3 v = Vector3.Cross(d, u); Vector3 basePoint = end - d * .23f;
            verts[0] = end; verts[sides + 1] = basePoint;
            for (int i = 0; i < sides; i++)
            {
                float a = i * Mathf.PI * 2f / sides;
                verts[i + 1] = basePoint + (u * Mathf.Cos(a) + v * Mathf.Sin(a)) * radius * 3.4f;
            }
            for (int i = 0; i < sides; i++) { int next = (i + 1) % sides + 1; tris.AddRange(new[] { 0, i + 1, next, sides + 1, next, i + 1 }); }
            CreateMesh("Arrow head", parent, verts, tris.ToArray(), color);
        }
        private void Segment(string label, Transform parent, Vector3 start, Vector3 end, Color color, float radius)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder); obj.name = label;
            obj.transform.SetParent(parent, false);
            Vector3 a = EulerMathContract.ToUnity(start), b = EulerMathContract.ToUnity(end);
            obj.transform.localPosition = (a + b) * .5f;
            obj.transform.localRotation = Quaternion.FromToRotation(Vector3.up, (b - a).normalized);
            obj.transform.localScale = new Vector3(radius * 2f, Vector3.Distance(a, b) * .5f, radius * 2f);
            var collider = obj.GetComponent<Collider>(); if (collider != null) DestroyOwnedObject(collider);
            var renderer = obj.GetComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, true);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void BuildRing(Transform parent, Vector3 normal, float radius, Color color, float tubeRadius)
        {
            Vector3 u = Vector3.Cross(normal, Vector3.forward).normalized;
            if (u.sqrMagnitude < .5f) u = Vector3.right;
            Vector3 v = Vector3.Cross(normal, u).normalized;
            const int count = 96;
            for (int i = 0; i < count; i++)
            {
                float a = i * Mathf.PI * 2f / count, b = (i + 1) * Mathf.PI * 2f / count;
                Segment("Ring arc", parent, (u * Mathf.Cos(a) + v * Mathf.Sin(a)) * radius,
                    (u * Mathf.Cos(b) + v * Mathf.Sin(b)) * radius, color, tubeRadius);
            }
        }
        private Material MakeMaterial(Color color, bool unlit)
        {
            bool srp = UsesSrp();
            string cacheKey = ColorUtility.ToHtmlStringRGBA(color) + "-" + unlit + "-" + srp;
            if (materialCache.TryGetValue(cacheKey, out Material existing)) return existing;
            Shader shader = Shader.Find(srp ? (unlit ? "Universal Render Pipeline/Unlit" : "Universal Render Pipeline/Lit")
                : (unlit ? "Unlit/Color" : "Standard"));
            if (shader == null) shader = Shader.Find("Sprites/Default");
            Material material = new Material(shader) { name = "M04 owned " + ColorUtility.ToHtmlStringRGB(color) };
            material.color = color;
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", .22f);
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", .22f);
            if (material.HasProperty("_Metallic")) material.SetFloat("_Metallic", 0f);
            // Procedural surfaces are double-sided for stable authoring and interior visibility.
            if (material.HasProperty("_Cull")) material.SetFloat("_Cull", 0f);
            ownedMaterials.Add(material); materialCache[cacheKey] = material; return material;
        }
        private static Transform NewObject(string name, Transform parent)
        { var obj = new GameObject(name); obj.transform.SetParent(parent, false); return obj.transform; }
        private static void DestroyOwnedObject(UnityEngine.Object obj)
        { if (Application.isPlaying) UnityEngine.Object.Destroy(obj); else UnityEngine.Object.DestroyImmediate(obj); }
        private void ClearOwned()
        {
            var old = transform.Find("Generated lesson geometry"); if (old != null) DestroyOwnedObject(old.gameObject);
            foreach (var mesh in ownedMeshes) if (mesh != null) DestroyOwnedObject(mesh);
            foreach (var material in ownedMaterials) if (material != null) DestroyOwnedObject(material);
            ownedMeshes.Clear(); ownedMaterials.Clear(); AircraftA = null; AircraftB = null;
            materialCache.Clear();
        }

        [Serializable] public class Anchor { public string name; public Vector3 pixelTopLeft; public Vector3 mathWorld; public bool inFrame; }
        [Serializable] public class FrameState
        {
            public string sceneId, mode, stage, handedness = "right", vectorConvention = "column";
            public int frame, width = CaptureWidth, height = CaptureHeight, fps = CaptureFps;
            public float time, normalizedTime;
            public float[] matrixA, matrixB;
            public bool hasEulerParametersA, hasEulerParametersB, hasRotationVectorA, hasRotationVectorB;
            public Vector3 eulerDegreesA, eulerDegreesB, rotationVectorRadiansA, rotationVectorRadiansB;
            public bool normalizationDefinedA, normalizationDefinedB;
            public string presentationTranslation = "Aircraft centers positioned for readable screen layout; matrix fields describe rotation only.";
            public Anchor[] anchors;
        }
        public FrameState GetFrameState(int frame, int totalFrames)
        {
            Evaluate(totalFrames <= 1 ? 0f : frame / (float)(totalFrames - 1));
            var anchors = new List<Anchor>();
            AddAircraftAnchors(anchors, "a", AircraftA); AddAircraftAnchors(anchors, "b", AircraftB);
            Transform visibleWorldA = HasTwoAircraft ? generated.Find("A fixed world axes") : worldAxes;
            if (visibleWorldA != null)
            {
                AddWorldAnchors(anchors, "world", visibleWorldA);
                if (HasTwoAircraft) AddWorldAnchors(anchors, "worldA", visibleWorldA);
            }
            Transform visibleWorldB = HasTwoAircraft ? generated.Find("B fixed world axes") : null;
            if (visibleWorldB != null) AddWorldAnchors(anchors, "worldB", visibleWorldB);
            if (axisAngleGuide != null)
                AddAnchor(anchors, "axisGuide.aTip", axisAngleGuide.TransformPoint(EulerMathContract.ToUnity(Vector3.up * 3.3f)));
            if (alternateAxisGuide != null)
            {
                Vector3 explicitAxis = lessonMode == "nonadd" ? new Vector3(1f, 1f, 0f).normalized : Vector3.down;
                AddAnchor(anchors, "axisGuide.bTip", alternateAxisGuide.TransformPoint(EulerMathContract.ToUnity(explicitAxis * 3.3f)));
            }
            return new FrameState { sceneId = sceneId, mode = lessonMode, stage = StageLabel, frame = frame,
                time = frame / 60f, normalizedTime = normalizedTime, matrixA = Flatten(MathRotationA),
                matrixB = Flatten(MathRotationB), anchors = anchors.ToArray(),
                hasEulerParametersA = hasEulerA, hasEulerParametersB = hasEulerB,
                eulerDegreesA = eulerA, eulerDegreesB = eulerB,
                hasRotationVectorA = hasRotationVectorA, hasRotationVectorB = hasRotationVectorB,
                rotationVectorRadiansA = rotationVectorA, rotationVectorRadiansB = rotationVectorB,
                normalizationDefinedA = hasRotationVectorA && rotationVectorA.sqrMagnitude > 1e-14f,
                normalizationDefinedB = hasRotationVectorB && rotationVectorB.sqrMagnitude > 1e-14f };
        }
        private void AddAircraftAnchors(List<Anchor> anchors, string prefix, Transform aircraft)
        {
            if (aircraft == null || SceneCamera == null) return;
            AddAnchor(anchors, prefix + ".center", aircraft.position);
            AddAnchor(anchors, prefix + ".nose", aircraft.TransformPoint(EulerMathContract.ToUnity(new Vector3(0f, 0f, 2.1f))));
            AddAnchor(anchors, prefix + ".tail", aircraft.TransformPoint(EulerMathContract.ToUnity(new Vector3(0f, .4f, -1.8f))));
            AddAnchor(anchors, prefix + ".wingLeft", aircraft.TransformPoint(EulerMathContract.ToUnity(new Vector3(-2.2f, 0f, -.2f))));
            AddAnchor(anchors, prefix + ".wingRight", aircraft.TransformPoint(EulerMathContract.ToUnity(new Vector3(2.2f, 0f, -.2f))));
            AddAnchor(anchors, prefix + ".bodyX", aircraft.TransformPoint(EulerMathContract.ToUnity(Vector3.right * 2.7f)));
            AddAnchor(anchors, prefix + ".bodyY", aircraft.TransformPoint(EulerMathContract.ToUnity(Vector3.up * 2.7f)));
            AddAnchor(anchors, prefix + ".bodyZ", aircraft.TransformPoint(EulerMathContract.ToUnity(Vector3.forward * 2.7f)));
        }
        private void AddWorldAnchors(List<Anchor> anchors, string prefix, Transform axes)
        {
            AddAnchor(anchors, prefix + ".origin", axes.position);
            AddAnchor(anchors, prefix + ".x", axes.TransformPoint(EulerMathContract.ToUnity(Vector3.right * 2.75f)));
            AddAnchor(anchors, prefix + ".y", axes.TransformPoint(EulerMathContract.ToUnity(Vector3.up * 2.75f)));
            AddAnchor(anchors, prefix + ".z", axes.TransformPoint(EulerMathContract.ToUnity(Vector3.forward * 2.75f)));
        }
        private void AddAnchor(List<Anchor> anchors, string name, Vector3 unityWorld)
        {
            Vector3 v = SceneCamera.WorldToViewportPoint(unityWorld);
            anchors.Add(new Anchor { name = name, pixelTopLeft = new Vector3(v.x * CaptureWidth, (1f - v.y) * CaptureHeight, v.z),
                mathWorld = EulerMathContract.ToMath(unityWorld), inFrame = v.z > 0f && v.x >= 0f && v.x <= 1f && v.y >= 0f && v.y <= 1f });
        }
        private static float[] Flatten(Matrix4x4 m)
        {
            var result = new float[9]; for (int r = 0; r < 3; r++) for (int c = 0; c < 3; c++) result[r * 3 + c] = m[r, c];
            return result;
        }
    }
}
