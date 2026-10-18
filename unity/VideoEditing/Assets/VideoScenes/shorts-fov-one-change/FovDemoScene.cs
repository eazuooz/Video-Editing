using System;
using System.Collections.Generic;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace YamyamCoding.Shorts.FovOneChange
{
    /// <summary>Original procedural teaching assets. Nothing moves: only the camera's horizontal FOV varies.</summary>
    [DisallowMultipleComponent]
    public sealed class FovDemoScene : MonoBehaviour
    {
        public Camera sceneCamera;
        public Transform centerCar, leftCar, rightCar;
        public const int Width = 1920, Height = 1080;
        private readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        private Mesh pineMesh;

        [ContextMenu("Build original FOV teaching scene")]
        public void BuildWorld()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
                DestroyImmediate(transform.GetChild(i).gameObject);
            materials.Clear(); pineMesh = ConeMesh("Shared original pine branch mesh");
            var cameraObject = new GameObject("Fixed camera — only horizontal FOV changes");
            cameraObject.transform.SetParent(transform, false);
            sceneCamera = cameraObject.AddComponent<Camera>();
            sceneCamera.transform.SetPositionAndRotation(new Vector3(0, 1.5f, 0), Quaternion.identity);
            sceneCamera.aspect = Width / (float)Height;
            sceneCamera.nearClipPlane = .1f; sceneCamera.farClipPlane = 180f;
            sceneCamera.clearFlags = CameraClearFlags.SolidColor;
            sceneCamera.backgroundColor = new Color32(8, 11, 9, 255);
            sceneCamera.allowHDR = false; sceneCamera.allowMSAA = true;
            sceneCamera.useOcclusionCulling = false;

            Material asphalt = Material("Road asphalt", 65, 72, 75);
            Material paint = Material("Road markings", 227, 225, 207);
            Material grass = Material("Ground muted green", 99, 122, 96);
            Material curb = Material("Road curb", 152, 157, 151);
            Cube("Ground", transform, new Vector3(0, -.19f, 70), new Vector3(180, .12f, 180), grass);
            Cube("Three lane road", transform, new Vector3(0, -.07f, 70), new Vector3(32, .12f, 160), asphalt);
            foreach (float x in new[] { -16.1f, 16.1f })
                Cube("Raised roadside curb", transform, new Vector3(x, .035f, 70), new Vector3(.24f, .12f, 160), curb);
            foreach (float x in new[] { -13.5f, -4.5f, 4.5f, 13.5f })
                for (int z = 5; z < 140; z += 7)
                    Cube("Fixed lane dash", transform, new Vector3(x, .003f, z), new Vector3(.16f, .018f, 3.4f), paint);
            for (int z = 18; z <= 130; z += 13)
                foreach (int side in new[] { -1, 1 }) Tree(new Vector3(side * 19f, 0, z), z % 3 * .25f + 1f);

            centerCar = Car("center", new Vector3(0, 0, 10), Material("Center car warm yellow", 241, 178, 45));
            leftCar = Car("left", new Vector3(-9, 0, 11), Material("Left car blue", 63, 133, 191));
            rightCar = Car("right", new Vector3(9, 0, 11), Material("Right car green", 85, 161, 117));

            var lightObject = new GameObject("Fixed directional key light");
            lightObject.transform.SetParent(transform, false);
            lightObject.transform.rotation = Quaternion.Euler(43, -29, 0);
            Light key = lightObject.AddComponent<Light>(); key.type = LightType.Directional;
            key.intensity = 1.25f; key.color = new Color(1f, .97f, .9f);
            key.shadows = LightShadows.Soft; key.shadowStrength = .7f;
            key.shadowBias = .035f; key.shadowNormalBias = .2f;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.54f, .61f, .65f);
            RenderSettings.ambientEquatorColor = new Color(.4f, .44f, .45f);
            RenderSettings.ambientGroundColor = new Color(.25f, .28f, .23f);
            RenderSettings.fog = false; RenderSettings.reflectionIntensity = .3f;
            SetHorizontalFov(60);
        }

        public void SetHorizontalFov(float horizontalDegrees)
        {
            if (sceneCamera == null) throw new InvalidOperationException("BuildWorld must run before capture.");
            sceneCamera.fieldOfView = Camera.HorizontalToVerticalFieldOfView(horizontalDegrees, Width / (float)Height);
        }

        private Transform Car(string id, Vector3 position, Material body)
        {
            var root = new GameObject("Car " + id).transform;
            root.SetParent(transform, false); root.localPosition = position;
            Material tire = Material("Rubber tires", 25, 29, 31);
            Material rim = Material("Wheel rims", 153, 165, 173, .65f, .35f);
            Material glass = Material("Opaque stable window glass", 37, 67, 82, .2f, .55f);
            Material dark = Material("Grille and seals", 37, 42, 45);
            Material lamp = Material("Headlights", 248, 244, 213, .1f, .4f);
            Material red = Material("Rear lamps", 191, 46, 36, .1f, .3f);
            Material plate = Material("License plate", 222, 226, 219);
            Cube("Lower sill", root, new Vector3(0, .48f, 0), new Vector3(2.1f, .25f, 4.12f), dark);
            MeshObject(id + " shaped body", root, BodyMesh(id + " body mesh"), body);
            Cube("Front hood", root, new Vector3(0, .97f, -1.36f), new Vector3(1.96f, .14f, 1.28f), body);
            Cube("Rear trunk", root, new Vector3(0, 1f, 1.45f), new Vector3(1.96f, .14f, 1.02f), body);
            MeshObject(id + " cabin", root, CabinMesh(id + " cabin mesh"), body);
            Quad(id + " windshield", root, new[] { new Vector3(-.84f, 1.02f, -.99f), new Vector3(.84f, 1.02f, -.99f), new Vector3(.7f, 1.57f, -.59f), new Vector3(-.7f, 1.57f, -.59f) }, glass);
            Quad(id + " rear window", root, new[] { new Vector3(.84f, 1.02f, .99f), new Vector3(-.84f, 1.02f, .99f), new Vector3(-.7f, 1.57f, .59f), new Vector3(.7f, 1.57f, .59f) }, glass);
            foreach (int side in new[] { -1, 1 })
            {
                Quad(id + " side window " + side, root, new[] {
                    new Vector3(side*.914f, 1.03f, -.87f), new Vector3(side*.914f, 1.03f, .87f),
                    new Vector3(side*.744f, 1.55f, .53f), new Vector3(side*.744f, 1.55f, -.53f) }, glass);
                Cube("Window center pillar", root, new Vector3(side*.83f, 1.29f, .02f), new Vector3(.035f, .51f, .065f), dark);
                Cube("Mirror stem", root, new Vector3(side*1.05f, 1.13f, -.68f), new Vector3(.16f, .055f, .08f), dark);
                Cube("Side mirror", root, new Vector3(side*1.13f, 1.15f, -.68f), new Vector3(.16f, .14f, .25f), body);
                Cube("Door handle", root, new Vector3(side*1.071f, .94f, .3f), new Vector3(.025f, .045f, .24f), rim);
                foreach (float z in new[] { -1.34f, 1.31f })
                {
                    GameObject wheel = Primitive("Four-wheel tire", PrimitiveType.Cylinder, root, new Vector3(side*1.02f, .4f, z), new Vector3(.68f, .13f, .68f), tire);
                    wheel.transform.localRotation = Quaternion.Euler(0, 0, 90);
                    GameObject hub = Primitive("Wheel rim", PrimitiveType.Cylinder, root, new Vector3(side*1.159f, .4f, z), new Vector3(.43f, .027f, .43f), rim);
                    hub.transform.localRotation = Quaternion.Euler(0, 0, 90);
                    for (int spoke = 0; spoke < 5; spoke++)
                    {
                        GameObject part = Cube("Wheel spoke", root, new Vector3(side*1.19f, .4f, z), new Vector3(.024f, .35f, .04f), dark);
                        part.transform.localRotation = Quaternion.Euler(spoke*36, 0, 0);
                    }
                }
                Cube("Front headlight", root, new Vector3(side*.76f, .84f, -2.12f), new Vector3(.48f, .18f, .045f), lamp);
                Cube("Rear red light", root, new Vector3(side*.77f, .84f, 2.12f), new Vector3(.45f, .17f, .045f), red);
            }
            Cube("Front bumper", root, new Vector3(0, .52f, -2.17f), new Vector3(2.08f, .15f, .16f), dark);
            Cube("Rear bumper", root, new Vector3(0, .52f, 2.17f), new Vector3(2.08f, .15f, .16f), dark);
            Cube("Grille", root, new Vector3(0, .72f, -2.13f), new Vector3(1.18f, .22f, .045f), dark);
            for (int i = -3; i <= 3; i++) Cube("Grille slat", root, new Vector3(i*.15f, .72f, -2.16f), new Vector3(.025f, .17f, .025f), rim);
            Cube("Front license plate", root, new Vector3(0, .48f, -2.258f), new Vector3(.46f, .13f, .02f), plate);
            return root;
        }

        private void Tree(Vector3 position, float scale)
        {
            Transform root = new GameObject("Fixed roadside pine").transform;
            root.SetParent(transform, false); root.localPosition = position; root.localScale = Vector3.one*scale;
            Primitive("Pine trunk", PrimitiveType.Cylinder, root, new Vector3(0, .9f, 0), new Vector3(.23f, .9f, .23f), Material("Tree bark", 105, 83, 62));
            Material green = Material("Pine needles", 57, 94, 74);
            for (int layer = 0; layer < 3; layer++)
            {
                GameObject cone = MeshObject("Pine branch crown", root, pineMesh, green);
                cone.transform.localPosition = new Vector3(0, 1.3f+layer*.9f, 0);
                cone.transform.localScale = new Vector3(1.45f-layer*.28f, 2.1f-layer*.22f, 1.45f-layer*.28f);
            }
        }

        private Material Material(string name, byte r, byte g, byte b, float metal = 0f, float smooth = .22f)
        {
            if (materials.TryGetValue(name, out Material existing)) return existing;
            Shader shader = Shader.Find("Standard");
            if (shader == null) throw new InvalidOperationException("Built-in Standard shader is required.");
            var material = new Material(shader) { name = name, color = new Color32(r, g, b, 255) };
            material.SetFloat("_Metallic", metal); material.SetFloat("_Glossiness", smooth);
            materials.Add(name, material); return material;
        }
        private static GameObject Cube(string name, Transform parent, Vector3 position, Vector3 scale, Material material)
        { return Primitive(name, PrimitiveType.Cube, parent, position, scale, material); }
        private static GameObject Primitive(string name, PrimitiveType kind, Transform parent, Vector3 position, Vector3 scale, Material material)
        {
            GameObject item = GameObject.CreatePrimitive(kind); item.name = name;
            item.transform.SetParent(parent, false); item.transform.localPosition = position; item.transform.localScale = scale;
            item.GetComponent<Renderer>().sharedMaterial = material;
            Collider collider = item.GetComponent<Collider>(); if (collider != null) DestroyImmediate(collider);
            return item;
        }
        private static GameObject MeshObject(string name, Transform parent, Mesh mesh, Material material)
        {
            var item = new GameObject(name); item.transform.SetParent(parent, false);
            item.AddComponent<MeshFilter>().sharedMesh = mesh; item.AddComponent<MeshRenderer>().sharedMaterial = material; return item;
        }
        private static void Quad(string name, Transform parent, Vector3[] points, Material material)
        {
            // Duplicate reverse-face vertices so recalculated normals do not
            // cancel, while both sides remain stable in the built-in renderer.
            var vertices = new Vector3[8]; Array.Copy(points,vertices,4); Array.Copy(points,0,vertices,4,4);
            var mesh = new Mesh { name = name + " mesh", vertices = vertices, triangles = new[] { 0, 1, 2, 0, 2, 3, 6, 5, 4, 7, 6, 4 } };
            mesh.RecalculateNormals(); mesh.RecalculateBounds(); MeshObject(name, parent, mesh, material);
        }
        private static Mesh BodyMesh(string name)
        {
            return BoxProfile(name, new[] {
                new Vector3(-.98f,.45f,-2.1f), new Vector3(.98f,.45f,-2.1f), new Vector3(1.07f,.45f,2.1f), new Vector3(-1.07f,.45f,2.1f),
                new Vector3(-.96f,.96f,-2.02f), new Vector3(.96f,.96f,-2.02f), new Vector3(1.02f,.98f,2.02f), new Vector3(-1.02f,.98f,2.02f) });
        }
        private static Mesh CabinMesh(string name)
        {
            return BoxProfile(name, new[] {
                new Vector3(-.91f,.98f,-1f), new Vector3(.91f,.98f,-1f), new Vector3(.91f,.98f,1f), new Vector3(-.91f,.98f,1f),
                new Vector3(-.73f,1.63f,-.56f), new Vector3(.73f,1.63f,-.56f), new Vector3(.73f,1.63f,.56f), new Vector3(-.73f,1.63f,.56f) });
        }
        private static Mesh BoxProfile(string name, Vector3[] corners)
        {
            int[][] faces = { new[]{0,3,2,1}, new[]{4,5,6,7}, new[]{0,1,5,4}, new[]{1,2,6,5}, new[]{2,3,7,6}, new[]{3,0,4,7} };
            var vertices = new List<Vector3>(); var triangles = new List<int>();
            foreach (int[] face in faces)
            {
                int first = vertices.Count; foreach (int i in face) vertices.Add(corners[i]);
                triangles.AddRange(new[]{first,first+2,first+1,first,first+3,first+2});
            }
            var mesh = new Mesh { name = name }; mesh.SetVertices(vertices); mesh.SetTriangles(triangles, 0); mesh.RecalculateNormals(); mesh.RecalculateBounds(); return mesh;
        }
        private static Mesh ConeMesh(string name)
        {
            const int sides = 16; var vertices = new List<Vector3>(); var triangles = new List<int>();
            for (int i = 0; i < sides; i++)
            {
                float a = i*Mathf.PI*2/sides, b = (i+1)*Mathf.PI*2/sides;
                int start = vertices.Count; vertices.Add(new Vector3(Mathf.Cos(a),0,Mathf.Sin(a)));
                vertices.Add(new Vector3(0,1,0)); vertices.Add(new Vector3(Mathf.Cos(b),0,Mathf.Sin(b)));
                triangles.AddRange(new[]{start,start+1,start+2});
            }
            var mesh = new Mesh { name = name }; mesh.SetVertices(vertices); mesh.SetTriangles(triangles,0); mesh.RecalculateNormals(); mesh.RecalculateBounds(); return mesh;
        }

        public string TransformSignature()
        {
            var text = new StringBuilder();
            foreach (Transform item in GetComponentsInChildren<Transform>(true))
            {
                text.Append(item.name).Append('|');
                foreach (float f in new[] { item.localPosition.x,item.localPosition.y,item.localPosition.z,item.localRotation.x,item.localRotation.y,item.localRotation.z,item.localRotation.w,item.localScale.x,item.localScale.y,item.localScale.z })
                    text.Append(f.ToString("R", CultureInfo.InvariantCulture)).Append(',');
                text.Append(';');
            }
            using (SHA256 algorithm = SHA256.Create())
                return BitConverter.ToString(algorithm.ComputeHash(Encoding.UTF8.GetBytes(text.ToString()))).Replace("-", "").ToLowerInvariant();
        }
    }
}
