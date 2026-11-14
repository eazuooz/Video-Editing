using UnityEngine;

namespace Yamyam.LevelDesign.ApertureV1
{
    // An authored comparison, not a reconstruction or a photometric measurement.
    public sealed class ApertureDirectionPlaybackV1 : MonoBehaviour
    {
        public const int Frames = 960;
        public const int Fps = 60;
        public static readonly Vector3 Source = new Vector3(0f, 2.5f, -3f);
        public Light finiteSpot;
        public LineRenderer editorialCenterRay;
        public Transform sourceArrow;
        public TextMesh stateLabel;
        public Camera playerCamera;
        public Camera sectionCamera;
        public float currentSlope;
        public bool autoPlay;

        private void Update()
        {
            if (autoPlay) ApplyFrame(Mathf.Min(Frames - 1, Mathf.FloorToInt(Time.timeSinceLevelLoad * Fps)));
        }

        public void ApplyFrame(int frame)
        {
            frame = Mathf.Clamp(frame, 0, Frames - 1);
            // Monotonic direction change; geometry, source position and light settings stay fixed.
            currentSlope = Mathf.Lerp(-.24f, -.10f, frame / (float)(Frames - 1));
            Vector3 direction = new Vector3(0f, currentSlope, 1f).normalized;
            finiteSpot.transform.position = Source;
            finiteSpot.transform.rotation = Quaternion.LookRotation(direction, Vector3.up);
            sourceArrow.position = Source;
            sourceArrow.rotation = Quaternion.LookRotation(direction, Vector3.up);
            Physics.SyncTransforms();
            Vector3 endpoint = Source + direction * 25f;
            string firstSurface = "No solid surface";
            RaycastHit hit;
            if (Physics.Raycast(Source, direction, out hit, 25f, ~0, QueryTriggerInteraction.Ignore))
            {
                endpoint = hit.point;
                firstSurface = hit.collider.gameObject.name;
            }
            editorialCenterRay.positionCount = 2;
            editorialCenterRay.SetPosition(0, Source);
            editorialCenterRay.SetPosition(1, endpoint);
            stateLabel.text = "첫 접촉 / First contact: " + firstSurface +
                "\n선은 중심 경로 안내 · 밝기는 Unity 조명 출력";
        }
    }
}
