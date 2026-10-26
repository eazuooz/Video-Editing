using System;
using UnityEngine;

namespace YamyamCoding.Shorts.SplatoonInkReadability
{
    /// <summary>
    /// One editable, deterministic teaching scene. Inspector values are OUR
    /// implementation parameters, never measured or reverse-engineered game data.
    /// No automatic playback, capture, render-target allocation or project changes.
    /// </summary>
    [ExecuteAlways]
    public sealed class InkReadabilityDemo : MonoBehaviour
    {
        public Renderer[] inkSurfaces;
        public Transform diver;
        public Transform ripple;
        public Transform[] droplets;
        public Camera lessonCamera;
        public Vector3 diverStart = new Vector3(0.8f, 0.45f, -0.6f);
        public Vector3 fixedLightDirection = new Vector3(0.65f, 0.32f, -0.69f);
        [Tooltip("Use the fixed floor/view reflection direction at the submerge ring in every comparison.")]
        public bool aimFixedLightAtSplash = true;

        [Range(0, 1)] public float shadingStrength = 1;
        [Range(0, 4)] public float specularStrength = 0.3f;
        [Range(0, 1)] public float submergePhase = 0.62f;
        [TextArea] public string sourceKind = "우리 Unity 모형 — Nintendo 셰이더 복원이 아님";

        private MaterialPropertyBlock block;

        [Serializable]
        public struct State
        {
            public string sourceKind;
            public float shadingStrength;
            public float specularStrength;
            public float submergePhase;
            public Vector3 lightDirection;
            public Vector3 cameraPosition;
            public Vector3 cameraEulerAngles;
            public Vector3 diverPosition;
        }

        public State ReadState()
        {
            return new State
            {
                sourceKind = "our-implementation, not commercial-game measurements",
                shadingStrength = shadingStrength,
                specularStrength = specularStrength,
                submergePhase = submergePhase,
                lightDirection = fixedLightDirection.normalized,
                cameraPosition = lessonCamera ? lessonCamera.transform.position : Vector3.zero,
                cameraEulerAngles = lessonCamera ? lessonCamera.transform.eulerAngles : Vector3.zero,
                diverPosition = diver ? diver.position : Vector3.zero,
            };
        }

        // Compare these at identical submergePhase, geometry, light and camera.
        // Call the two families separately; restoring the shared baseline is
        // explicit, rather than silently changing two variables inside one A/B.
        public void SetShadingComparison(float amount, float phase)
        {
            shadingStrength = Mathf.Lerp(1, 0, Mathf.Clamp01(amount));
            specularStrength = 0.3f;
            submergePhase = Mathf.Clamp01(phase);
            Apply();
        }

        public void SetSpecularComparison(float amount, float phase)
        {
            shadingStrength = 0.55f;
            specularStrength = Mathf.Lerp(0.3f, 3.5f, Mathf.Clamp01(amount));
            submergePhase = Mathf.Clamp01(phase);
            Apply();
        }

        public void SetBalancedIllustration(float phase)
        {
            shadingStrength = 0.55f;
            specularStrength = 0.3f;
            submergePhase = Mathf.Clamp01(phase);
            Apply();
        }

        public void Apply()
        {
            if (aimFixedLightAtSplash && lessonCamera)
            {
                // Solve the actual mirror direction of the unchanged floor:
                // L = reflect(-V, N). N is the floor's macroscopic normal;
                // its existing raised mesh supplies the local rough highlights.
                // The anchor is fixed, not the animated diver/droplets. This
                // never depends on stage, comparison amount or submerge phase.
                Vector3 anchor = transform.TransformPoint(new Vector3(diverStart.x, 0.09f, diverStart.z));
                Vector3 view = (lessonCamera.transform.position - anchor).normalized;
                fixedLightDirection = Vector3.Reflect(-view, transform.up).normalized;
            }
            if (block == null) block = new MaterialPropertyBlock();
            if (inkSurfaces != null)
            {
                foreach (Renderer surface in inkSurfaces)
                {
                    if (!surface) continue;
                    surface.GetPropertyBlock(block);
                    block.SetFloat("_ShadingStrength", shadingStrength);
                    block.SetFloat("_SpecularStrength", specularStrength);
                    block.SetVector("_LightDirection", fixedLightDirection.normalized);
                    surface.SetPropertyBlock(block);
                }
            }
            // The mannequin, ring and droplets are identical in both A/B states.
            // No enemy AI, game collision, ink-paint attachment or Nintendo asset.
            float descent = Smooth(Mathf.InverseLerp(0.15f, 0.75f, submergePhase));
            if (diver) diver.localPosition = diverStart + Vector3.down * (2.0f * descent);
            float splash = Mathf.Clamp01((submergePhase - 0.45f) / 0.5f);
            bool splashVisible = splash > 0 && splash < 1;
            if (ripple)
            {
                ripple.gameObject.SetActive(splashVisible);
                ripple.localPosition = new Vector3(diverStart.x, 0.09f, diverStart.z);
                ripple.localScale = new Vector3(1 + 2 * splash, 1, 1 + 2 * splash);
            }
            if (droplets == null) return;
            for (int i = 0; i < droplets.Length; i++)
            {
                Transform drop = droplets[i];
                if (!drop) continue;
                drop.gameObject.SetActive(splashVisible);
                float angle = i * Mathf.PI * 2 / Mathf.Max(1, droplets.Length);
                float radius = 0.1f + splash * (0.7f + 0.06f * (i % 3));
                float height = 0.09f + Mathf.Sin(splash * Mathf.PI) * (0.35f + 0.07f * (i % 3));
                drop.localPosition = new Vector3(diverStart.x + Mathf.Cos(angle) * radius,
                    height, diverStart.z + Mathf.Sin(angle) * radius);
                drop.localScale = Vector3.one * (0.07f * Mathf.Sqrt(1 - splash));
            }
        }

        private static float Smooth(float value)
        {
            return value * value * (3 - 2 * value);
        }

        private void OnEnable() { Apply(); }
        private void OnValidate() { Apply(); }
    }
}
