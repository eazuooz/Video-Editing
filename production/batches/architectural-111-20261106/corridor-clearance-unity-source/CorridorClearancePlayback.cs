using System;
using UnityEngine;

namespace Yamyam.LevelDesign.CorridorClearance
{
    public sealed class CorridorClearancePlayback : MonoBehaviour
    {
        public const float BodyRadius = 0.30f;
        public const float CameraRadius = 0.14f;
        public const float CameraOffsetX = 0.66f;
        public const float CameraTrail = 0.41f;
        public const float CameraHeight = 1.35f;
        public const float WallStart = 2.00f;
        public const float WallEnd = 3.20f;
        public const float SampleZ = 2.78f;

        [Serializable]
        public sealed class Lane
        {
            public Transform origin;
            public BoxCollider leftWall;
            public BoxCollider rightWall;
            public Transform body;
            public Transform desiredCameraMarker;
            public Transform resolvedCameraMarker;
            public Camera playerCamera;

            public bool BodyBlocked { get; private set; }
            public bool DesiredCameraBlocked { get; private set; }
            public bool ResolvedCameraBlocked { get; private set; }

            public void Apply(float forward)
            {
                Vector3 center = origin.TransformPoint(new Vector3(0, 0.90f, forward));
                Vector3 desired = origin.TransformPoint(new Vector3(CameraOffsetX, CameraHeight, forward - CameraTrail));
                Vector3 resolved = desired;

                BodyBlocked = Overlaps(leftWall, center, BodyRadius) || Overlaps(rightWall, center, BodyRadius);
                DesiredCameraBlocked = Overlaps(rightWall, desired, CameraRadius);
                if (DesiredCameraBlocked)
                    resolved.x = rightWall.bounds.min.x - CameraRadius - 0.005f;
                ResolvedCameraBlocked = Overlaps(leftWall, resolved, CameraRadius) ||
                                        Overlaps(rightWall, resolved, CameraRadius);

                body.position = center;
                desiredCameraMarker.position = desired;
                resolvedCameraMarker.position = resolved;
                resolvedCameraMarker.gameObject.SetActive(DesiredCameraBlocked);
                playerCamera.transform.position = resolved;
            }

            private static bool Overlaps(BoxCollider wall, Vector3 point, float radius)
            {
                return (wall.ClosestPoint(point) - point).sqrMagnitude < radius * radius;
            }
        }

        public Lane narrow;
        public Lane wide;

        private float elapsed;

        public void Apply(float forward)
        {
            narrow.Apply(forward);
            wide.Apply(forward);
        }

        private void OnEnable()
        {
            elapsed = 0;
            Apply(0.6f);
        }

        private void Update()
        {
            elapsed += Time.deltaTime;
            Apply(Mathf.Min(0.6f + elapsed * 0.8f, 4.15f));
        }
    }
}
