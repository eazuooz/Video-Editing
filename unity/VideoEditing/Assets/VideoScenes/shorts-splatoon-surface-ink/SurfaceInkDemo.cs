using System;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace Yamyam.Video.SurfaceInk
{
    // An independently authored, deliberately small flat-surface example.
    // This is not Nintendo source or a claim about a shipped Splatoon shader.
    public sealed class SurfaceInkDemo : MonoBehaviour
    {
        [Range(0, 5)] public int stage;
        [Range(0, 1)] public float progress;
        public bool joinedPatches = true;
        public Camera lessonCamera;
        public Material paintMaterial;
        public Transform generatedRoot;
        public MeshRenderer floorRenderer, wallRenderer, sheetRenderer;
        public LineRenderer impactGuide, mappingGuide;
        public Transform contactMarker;
        [NonSerialized] public Vector2 lastUV;
        [NonSerialized] public Vector3 lastHit;
        [NonSerialized] public Vector2 wallUV;
        [NonSerialized] public Vector3 wallHit;
        [NonSerialized] public bool wallPaintHasHit;
        Texture2D floorPaint, wallPaint;
        Color[] floorPixels, wallPixels;
        Material floorMat, wallMat, sheetMat;
        const int Size = 512;
        int preparedStage = -1;
        int resetOperations, stampOperations, pairedTextureUploadOperations;
        static readonly Rect[] AdjacentPatches = { new Rect(0, 0, .5f, 1), new Rect(.5f, 0, .5f, 1) };
        static readonly Color Ink = new Color(0.05f, 0.66f, 0.80f, 1);
        static readonly Color InkOther = new Color(1, 0.43f, 0.08f, 1);

        [Serializable]
        public sealed class PaintTextureEvidence
        {
            public string floorSHA256, wallSHA256;
            public string floorTextureEntityId, wallTextureEntityId;
            public int resetOperations, stampOperations, pairedTextureUploadOperations;
            public bool sheetAndWallShareTexture;
            public string evidenceKind = "CPU Texture2D raw bytes after explicit Upload/Apply; not a GPU readback or Nintendo implementation";
        }

        // Read-only CPU evidence for our actual allocated/updated Texture2D data.
        // Hashing a final JPG cannot prove paint persistence while the camera moves.
        public PaintTextureEvidence CapturePaintEvidence()
        {
            Initialize();
            return new PaintTextureEvidence
            {
                floorSHA256 = TextureSHA256(floorPaint), wallSHA256 = TextureSHA256(wallPaint),
                floorTextureEntityId = floorPaint.GetEntityId().ToString(), wallTextureEntityId = wallPaint.GetEntityId().ToString(),
                resetOperations = resetOperations, stampOperations = stampOperations,
                pairedTextureUploadOperations = pairedTextureUploadOperations,
                sheetAndWallShareTexture = sheetMat.GetTexture("_PaintTex") == wallPaint &&
                                          wallMat.GetTexture("_PaintTex") == wallPaint,
            };
        }

        static string TextureSHA256(Texture2D texture)
        {
            using (var digest = SHA256.Create())
            {
                byte[] hash = digest.ComputeHash(texture.GetRawTextureData());
                var result = new StringBuilder(hash.Length * 2);
                foreach (byte value in hash) result.Append(value.ToString("x2"));
                return result.ToString();
            }
        }

        public static Vector2 SurfaceUV(Vector3 hit, Vector3 origin, Vector3 u, Vector3 v, Vector2 size)
        {
            if (size.x <= 0 || size.y <= 0 || Mathf.Abs(Vector3.Dot(u.normalized, v.normalized)) > 0.001f)
                throw new ArgumentException("Positive size and orthogonal surface axes required.");
            var offset = hit - origin;
            return new Vector2(Vector3.Dot(offset, u.normalized) / size.x,
                               Vector3.Dot(offset, v.normalized) / size.y);
        }

        public void Initialize()
        {
            if (wallPaint != null) return;
            if (!floorRenderer || !wallRenderer || !sheetRenderer || !lessonCamera || !paintMaterial)
                throw new InvalidOperationException("Build and assign the lesson stage first.");
            floorPaint = NewTexture("Floor paint: actual persistent image");
            wallPaint = NewTexture("Wall paint: actual persistent image");
            floorPixels = new Color[Size * Size]; wallPixels = new Color[Size * Size];
            floorMat = new Material(paintMaterial); wallMat = new Material(paintMaterial);
            sheetMat = new Material(paintMaterial);
            floorMat.SetTexture("_PaintTex", floorPaint); wallMat.SetTexture("_PaintTex", wallPaint);
            // The sheet and wall sample the same texture object, not two illustrations.
            sheetMat.SetTexture("_PaintTex", wallPaint); sheetMat.SetFloat("_FlatView", 1);
            floorRenderer.sharedMaterial = floorMat; wallRenderer.sharedMaterial = wallMat;
            sheetRenderer.sharedMaterial = sheetMat;
            ResetPaint();
        }

        static Texture2D NewTexture(string name)
        {
            return new Texture2D(Size, Size, TextureFormat.RGBA32, false, true)
            { name = name, filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp };
        }

        public void ResetPaint()
        {
            resetOperations++;
            wallPaintHasHit = false;
            Array.Clear(floorPixels, 0, floorPixels.Length);
            Array.Clear(wallPixels, 0, wallPixels.Length);
            Upload();
        }

        public bool Shoot(Vector3 origin, Vector3 target, Color color, float radius, bool join)
        {
            Physics.SyncTransforms();
            Vector3 delta = target - origin;
            if (!Physics.Raycast(origin, delta.normalized, out RaycastHit hit, delta.magnitude + .1f))
                return false;
            bool wall = hit.collider.gameObject == wallRenderer.gameObject;
            bool floor = hit.collider.gameObject == floorRenderer.gameObject;
            if (!wall && !floor) return false;
            Vector3 corner = wall ? new Vector3(-2, 0, 2) : new Vector3(-2, 0, -2);
            Vector3 axisV = wall ? Vector3.up : Vector3.forward;
            lastUV = SurfaceUV(hit.point, corner, Vector3.right, axisV, new Vector2(4, 4));
            lastHit = hit.point;
            if (lastUV.x < 0 || lastUV.x > 1 || lastUV.y < 0 || lastUV.y > 1) return false;
            Stamp(wall ? wallPixels : floorPixels, lastUV, radius, color, join);
            stampOperations++;
            if (wall) { wallUV = lastUV; wallHit = hit.point; wallPaintHasHit = true; }
            Upload();
            if (contactMarker) contactMarker.position = hit.point + hit.normal * .025f;
            if (impactGuide) { impactGuide.SetPosition(0, origin); impactGuide.SetPosition(1, hit.point); }
            return true;
        }

        static void Stamp(Color[] pixels, Vector2 uv, float radius, Color color, bool join)
        {
            int hitPatch = uv.x < .5f ? 0 : 1;
            int minX = Mathf.Max(0, Mathf.FloorToInt((uv.x - radius * 1.25f) * Size));
            int maxX = Mathf.Min(Size - 1, Mathf.CeilToInt((uv.x + radius * 1.25f) * Size));
            int minY = Mathf.Max(0, Mathf.FloorToInt((uv.y - radius * 1.25f) * Size));
            int maxY = Mathf.Min(Size - 1, Mathf.CeilToInt((uv.y + radius * 1.25f) * Size));
            for (int y = minY; y <= maxY; y++) for (int x = minX; x <= maxX; x++)
            {
                Vector2 texelUV = new Vector2((x + .5f) / Size, (y + .5f) / Size);
                // Both coplanar patches map into adjacent regions of one image.
                // Joined mode updates either region intersected by the same stamp.
                bool inHitPatch = AdjacentPatches[hitPatch].Contains(texelUV);
                bool inNeighbour = AdjacentPatches[1 - hitPatch].Contains(texelUV);
                if (!inHitPatch && !(join && inNeighbour)) continue;
                Vector2 d = texelUV - uv;
                float angle = Mathf.Atan2(d.y, d.x);
                float edge = radius * (1 + .12f * Mathf.Sin(5 * angle) + .06f * Mathf.Cos(9 * angle));
                float alpha = Mathf.Clamp01((edge - d.magnitude) * Size);
                if (alpha <= 0) continue;
                int i = y * Size + x;
                Color old = pixels[i];
                float outA = alpha + old.a * (1 - alpha);
                Vector3 rgb = (new Vector3(color.r, color.g, color.b) * alpha +
                               new Vector3(old.r, old.g, old.b) * old.a * (1 - alpha)) / outA;
                pixels[i] = new Color(rgb.x, rgb.y, rgb.z, outA);
            }
        }

        void Upload()
        {
            pairedTextureUploadOperations++;
            floorPaint.SetPixels(floorPixels); floorPaint.Apply(false, false);
            wallPaint.SetPixels(wallPixels); wallPaint.Apply(false, false);
        }

        // Capture calls this with speech-derived progress. No invented final duration.
        public void ApplyFrame(int selectedStage, float normalizedProgress, bool joined = true,
            float collisionHitAt = .65f, float stampEndAt = 1, float floorAt = 0)
        {
            Initialize(); stage = selectedStage; progress = Mathf.Clamp01(normalizedProgress);
            joinedPatches = joined;
            bool paintThisFrame = stage != 5 || preparedStage != 5;
            if (paintThisFrame) ResetPaint();
            sheetRenderer.gameObject.SetActive(stage <= 4);
            wallMat.SetFloat("_ShowSeam", stage == 4 ? 1 : 0);
            sheetMat.SetFloat("_ShowSeam", stage == 4 ? 1 : 0);
            impactGuide.enabled = stage == 1 || stage == 2;
            mappingGuide.enabled = stage == 2 || stage == 3;
            contactMarker.gameObject.SetActive(stage <= 4);
            Vector3 origin = new Vector3(0, 1.6f, -3);
            Vector3 wallTarget = new Vector3(stage == 4 ? -.08f : 0, 2, 2);
            collisionHitAt = Mathf.Clamp(collisionHitAt, .001f, 1);
            stampEndAt = Mathf.Clamp(stampEndAt, .001f, 1);
            floorAt = Mathf.Clamp01(floorAt);
            bool reachedSurface = stage != 1 || progress >= collisionHitAt;
            float minimumStampScale = stampEndAt < .999f ? .15f : .02f;
            float stampRadius = stage == 3 ? .17f * Mathf.SmoothStep(minimumStampScale, 1,
                Mathf.Clamp01(progress / stampEndAt)) : .17f;
            if (reachedSurface && paintThisFrame) Shoot(origin, wallTarget, Ink, stampRadius, stage != 4 || joined);
            else if (!reachedSurface)
            {
                impactGuide.SetPosition(0, origin);
                impactGuide.SetPosition(1, Vector3.Lerp(origin, wallTarget, progress / collisionHitAt));
                contactMarker.gameObject.SetActive(false);
            }
            if (paintThisFrame && (stage == 5 || (stage == 3 && progress >= floorAt)))
                Shoot(new Vector3(-1, 3, -1), new Vector3(-1, 0, -.5f), InkOther, .15f, true);
            // Keep the UV illustration tied to the wall hit, not the later floor hit.
            Vector3 wallPoint = wallTarget;
            // This is an explanatory coordinate connector, not another physical
            // collision ray. Route it just in front of the opaque checker sheet
            // so its center endpoint is not hidden behind that representation.
            var sheetBounds = sheetRenderer.GetComponent<MeshFilter>().sharedMesh.bounds;
            Vector3 front = sheetRenderer.transform.TransformDirection(Vector3.back).normalized * .04f;
            Vector3 sheetPoint = sheetRenderer.transform.TransformPoint(sheetBounds.center) + front;
            Vector3 elbow = sheetRenderer.transform.TransformPoint(sheetBounds.center +
                Vector3.down * (sheetBounds.extents.y + .16f)) + front;
            Vector3 connectorStart = wallPoint + Vector3.back * .025f;
            float connectorProgress = stage == 2 ? progress : 1;
            Vector3 middle = connectorProgress < .5f ?
                Vector3.Lerp(connectorStart, elbow, connectorProgress * 2) : elbow;
            Vector3 end = connectorProgress < .5f ? middle :
                Vector3.Lerp(elbow, sheetPoint, (connectorProgress - .5f) * 2);
            mappingGuide.positionCount = 3;
            mappingGuide.SetPosition(0, connectorStart);
            mappingGuide.SetPosition(1, middle);
            mappingGuide.SetPosition(2, end);
            if (stage == 3) contactMarker.position = wallPoint + Vector3.back * .025f;
            float angle = stage == 5 ? Mathf.Lerp(-22, 22, progress) : -16;
            lessonCamera.transform.position = Quaternion.Euler(0, angle, 0) * new Vector3(0, 6.5f, -15);
            lessonCamera.transform.LookAt(new Vector3(0, 3, 1));
            preparedStage = stage;
        }

        void OnDestroy()
        {
            Release(floorPaint); Release(wallPaint); Release(floorMat); Release(wallMat); Release(sheetMat);
        }
        static void Release(UnityEngine.Object o)
        {
            if (!o) return;
            if (Application.isPlaying) Destroy(o); else DestroyImmediate(o);
        }
    }
}
