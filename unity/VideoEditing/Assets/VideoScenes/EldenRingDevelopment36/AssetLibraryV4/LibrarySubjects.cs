using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        [Serializable] public sealed class LibraryBinding
        {
            public string role, assetPath, guid;
            public GameObject prefab;
        }

        public LibraryBinding[] library;
        readonly HashSet<string> assetRoles = new HashSet<string>();
        readonly Dictionary<Material, Material> materialAdapters = new Dictionary<Material, Material>();
        readonly List<Actor> actors = new List<Actor>();
        public string[] UsedLibraryRoles => assetRoles.OrderBy(role => role).ToArray();

        sealed class Actor
        {
            public Transform root, driver;
            public GameObject body;
            public Vector3 lastPosition, origin;
            public float lastTime = -1;
        }

        LibraryBinding Get(string role)
        {
            var binding = Array.Find(library, value => value.role == role);
            if (binding == null) throw new InvalidOperationException($"Unbound shared role: {role}");
            assetRoles.Add(role);
            return binding;
        }

        GameObject Attach(string role, Transform target, Vector3 fit, bool ground, float yaw = 0, bool poseActor = false)
        {
            var binding = Get(role);
            if (!binding.prefab) throw new InvalidOperationException($"Missing shared prefab: {role}");
            var anchor = new GameObject(binding.prefab.name + " reference").transform;
            anchor.SetParent(target, false);
            var instance = Instantiate(binding.prefab, anchor);
            instance.name = binding.prefab.name;
            foreach (var collider in instance.GetComponentsInChildren<Collider>(true)) collider.enabled = false;
            foreach (var audio in instance.GetComponentsInChildren<AudioSource>(true)) audio.enabled = false;
            foreach (var camera in instance.GetComponentsInChildren<Camera>(true)) camera.enabled = false;
            foreach (var animator in instance.GetComponentsInChildren<Animator>(true)) animator.enabled = false;
            instance.transform.localPosition = Vector3.zero;
            instance.transform.localRotation *= Quaternion.Euler(0, yaw, 0);
            if (poseActor) BakeActor(instance);
            var renderers = instance.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) throw new InvalidOperationException($"Shared prefab has no visible renderer: {role}");
            foreach (var lod in instance.GetComponentsInChildren<LODGroup>()) lod.ForceLOD(0);
            Bounds? combined = null;
            foreach (var renderer in renderers.Where(item => item.enabled))
            {
                Bounds box = renderer.localBounds;
                for (int i = 0; i < 8; i++)
                {
                    Vector3 edge = new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1);
                    var point = anchor.InverseTransformPoint(renderer.transform.TransformPoint(box.center + Vector3.Scale(box.extents, edge)));
                    if (!combined.HasValue) combined = new Bounds(point, Vector3.zero);
                    else { var updated = combined.Value; updated.Encapsulate(point); combined = updated; }
                }
                renderer.sharedMaterials = renderer.sharedMaterials.Select(CompatibleMaterial).ToArray();
            }
            if (!combined.HasValue) throw new InvalidOperationException($"No enabled shared renderers for {role}");
            var bounds = combined.Value;
            Vector3 size = bounds.size;
            float scale = Mathf.Min(fit.x / Mathf.Max(size.x, .01f), fit.y / Mathf.Max(size.y, .01f),
                                    fit.z / Mathf.Max(size.z, .01f));
            var pivot = bounds.center;
            if (ground) pivot.y = bounds.min.y;
            anchor.localScale = Vector3.one * scale;
            anchor.localPosition = -pivot * scale;
            return instance;
        }

        Material CompatibleMaterial(Material source)
        {
            if (!source) return Paint(Paper);
            var shaderName = source.shader ? source.shader.name : "";
            bool srp = GraphicsSettings.currentRenderPipeline;
            bool wrong = !source.shader || !source.shader.isSupported || shaderName == "Hidden/InternalErrorShader" ||
                (srp && shaderName.StartsWith("Standard", StringComparison.Ordinal)) ||
                (!srp && (shaderName.Contains("Universal Render Pipeline") || shaderName.Contains("Shader Graph")));
            if (!wrong) return source;
            if (materialAdapters.TryGetValue(source, out var adapted)) return adapted;
            adapted = new Material(Shader.Find(srp ? "Universal Render Pipeline/Lit" : "Standard"));
            var color = source.HasProperty("_BaseColor") ? source.GetColor("_BaseColor") :
                source.HasProperty("_Color") ? source.GetColor("_Color") : Paper;
            adapted.color = color;
            adapted.mainTexture = source.HasProperty("_BaseMap") ? source.GetTexture("_BaseMap") :
                source.HasProperty("_MainTex") ? source.GetTexture("_MainTex") : null;
            if (source.HasProperty("_BumpMap") && source.GetTexture("_BumpMap"))
            {
                adapted.SetTexture("_BumpMap", source.GetTexture("_BumpMap"));
                adapted.EnableKeyword("_NORMALMAP");
            }
            materialAdapters.Add(source, adapted);
            owned.Add(adapted);
            return adapted;
        }

        void AddLibraryActor(Transform root, string name, Color color)
        {
            bool partner = name.Contains("Joining") || name.Contains("Explorer B") || name.Contains("Gate approach") ||
                           name.Contains("Responding") || name.Contains("Player target");
            var body = Attach(partner && episode != 14 ? "partner" : "villager", root, V(1.42f, 1.54f, 1.18f), true, 180, true);
            var handle = new GameObject("Right sleeve").transform;
            handle.SetParent(root, false);
            handle.localPosition = V(.25f, .78f, -.03f);
            var actor = new Actor {root = root, body = body, driver = handle,
                lastPosition = root.position, origin = body.transform.localPosition};
            actors.Add(actor);
            var ring = Ring("Actor identifier", root.localPosition, .38f, color);
            ring.SetParent(root, false);
            ring.localPosition = V(0, .035f, 0);
            if ((episode == 14 || episode == 24 || episode == 35) && !partner)
            {
                var gear = new GameObject("Shield mount").transform;
                gear.SetParent(root, false);
                gear.localPosition = V(-.30f, .66f, -.14f);
                Attach("shield", gear, V(.42f, .51f, .28f), false);
            }
        }

        static Transform FindBone(Transform[] bones, string suffix) =>
            bones.FirstOrDefault(t => t.name.EndsWith(suffix, StringComparison.Ordinal));

        static void AimBone(Transform bone, Vector3 aim)
        {
            if (!bone || bone.childCount == 0) return;
            Vector3 direction = bone.GetChild(0).position - bone.position;
            if (direction.sqrMagnitude > .000001f)
                bone.rotation = Quaternion.FromToRotation(direction, aim) * bone.rotation;
        }

        void BakeActor(GameObject body)
        {
            var bones = body.GetComponentsInChildren<Transform>(true);
            AimBone(FindBone(bones, "upper_arm.R"), body.transform.TransformDirection(V(.27f, -.91f, -.16f)));
            AimBone(FindBone(bones, "upper_arm.L"), body.transform.TransformDirection(V(-.24f, -.93f, -.07f)));
            foreach (var skin in body.GetComponentsInChildren<SkinnedMeshRenderer>())
            {
                var mesh = new Mesh {name = skin.name + " capture pose"};
                skin.BakeMesh(mesh, false);
                if (mesh.vertexCount == 0) throw new InvalidOperationException($"Empty imported mesh: {skin.name}");
                owned.Add(mesh);
                var part = new GameObject(skin.name + " pose");
                part.transform.SetParent(skin.transform, false);
                part.AddComponent<MeshFilter>().sharedMesh = mesh;
                part.AddComponent<MeshRenderer>().sharedMaterials = skin.sharedMaterials;
                skin.enabled = false;
            }
        }

        void PlayLibraryActors(float time)
        {
            foreach (var actor in actors)
            {
                Vector3 shift = actor.root.position - actor.lastPosition;
                bool moving = time > actor.lastTime && new Vector2(shift.x, shift.z).sqrMagnitude > .000002f;
                bool combat = episode == 14 || episode == 26 || episode == 32 || episode == 35;
                var body = actor.body.transform;
                if (moving && !combat)
                {
                    float facing = Mathf.Atan2(shift.x, shift.z) * Mathf.Rad2Deg;
                    body.localRotation = Quaternion.Euler(0, facing, 0);
                }
                body.localPosition = actor.origin + Vector3.up * (moving ? .075f * Mathf.Abs(Mathf.Sin(time * 10)) : 0);
                if (combat)
                {
                    float pose = Quaternion.Angle(Quaternion.identity, actor.driver.localRotation);
                    body.localRotation = Quaternion.Euler(pose * .076f, 180 - pose * .17f, 0);
                }
                actor.lastPosition = actor.root.position;
                actor.lastTime = time;
            }
        }

        void DressPrimitive(Transform primitive, string name)
        {
            string role = null;
            switch (name)
            {
                case "Trunk": role = "tree"; break;
                case "Mountain silhouette": case "Cave back": case "Cave side": case "Repeated silhouette in front of goal":
                    role = "cliff"; break;
                case "Raised step": case "Step": case "Reconstructed surface marker":
                    role = "rock"; break;
                case "Individually positioned bloom": case "Procedurally placed plant":
                    role = "grass"; break;
                case "Training blade": case "Light tool":
                    role = "sword"; break;
                case "Heavy tool": role = "axe"; break;
                case "Gate left wall": case "Gate right wall": case "Local facade":
                    role = "tower"; break;
                case "Walkable west": case "Walkable east": case "Sidewalk alternative": case "Upper passage":
                    role = "bridge"; break;
                case "Workstation": role = "bench"; break;
                case "Work handoff": case "Common render test objects": case "Completed example task":
                    role = "crate"; break;
                case "Ray target": role = "rock"; break;
                case "Receiving surface": role = "paving"; break;
            }
            if (role == null) return;
            Attach(role, primitive, Vector3.one, false);
            primitive.GetComponent<Renderer>().enabled = false;
        }

        void AddSupportingAssets()
        {
            // These shots keep their authored geometry for the calculation itself.
            // A shared asset grounds each abstract comparison in the subject it represents.
            if (episode == 3)
                Attach("villager", Group("Library face reference", V(0, 0, 1.45f)), V(.82f, 1.76f, .8f), true, 180, true);
            if (episode == 7)
                Attach("rock", Group("Natural step reference", V(0, .06f, 2.65f)), V(1.12f, .91f, .9f), true);
            if (episode == 8)
                Attach("sword", Group("Weapon model context", V(-2.96f, .04f, 1.85f)), V(1.4f, 1.93f, .82f), true);
            if (episode == 12)
                Attach("tower", Group("Recorded viewpoint on the world map", V(2, .14f, 1.72f)), V(.86f, 1.42f, .86f), true);
            if (episode == 30)
                Attach("paving", Group("Movement distance reference", V(0, .04f, 2.03f)), V(7.85f, .72f, 1.6f), true);
            if (episode == 34)
                Attach("chest", Group("Progress reward example", V(-3.68f, .04f, 2.3f)), V(1.35f, .93f, 1.21f), true);
            if (assetRoles.Count == 0)
                throw new InvalidOperationException($"No library asset in lesson {episode}-{shot}");
        }
    }
}
