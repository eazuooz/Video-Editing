using System;
using System.Linq;
using UnityEngine;
using Yamyam.LevelDesign.RhythmRunner;

namespace Yamyam.LevelDesign.RhythmRunnerV2
{
    public sealed class RhythmCoursePlaybackV2 : MonoBehaviour
    {
        public Transform baselineRunner, delayedRunner, cameraRig;
        public Transform baselineModel, delayedModel;
        public AnimationClip walkingClip;
        public GameObject baselineInput, delayedInput, delayedCollision;
        public bool comparison;
        public int currentFrame;
        private RunnerFrame[] baseline, delayed;
        private Vector3 baselineModelPosition, delayedModelPosition, baselineScale, delayedScale;
        private Quaternion baselineRotation, delayedRotation;
        private float elapsed;
        private int nextFrame;

        public void Initialize()
        {
            if (baseline != null) return;
            if (!baselineRunner || !baselineModel || !cameraRig || !walkingClip || !baselineInput)
                throw new InvalidOperationException("The exact articulated runner, camera and input marker are required.");
            if (comparison && (!delayedRunner || !delayedModel || !delayedInput || !delayedCollision))
                throw new InvalidOperationException("The comparison needs both authored lanes.");
            baseline = RhythmCourseModel.Simulate(false).ToArray();
            delayed = RhythmCourseModel.Simulate(true).ToArray();
            if (baseline.Length != 440 || delayed.Length != 392)
                throw new InvalidOperationException("Unexpected fixed authored model outcomes.");
            baselineModelPosition = baselineModel.localPosition;
            baselineRotation = baselineModel.localRotation;
            baselineScale = baselineModel.localScale;
            if (comparison)
            {
                delayedModelPosition = delayedModel.localPosition;
                delayedRotation = delayedModel.localRotation;
                delayedScale = delayedModel.localScale;
            }
        }

        private void Start() { Initialize(); ApplyFrame(0); }
        private void Update()
        {
            elapsed += Time.unscaledDeltaTime;
            int requested = Math.Min(439, Mathf.FloorToInt(elapsed * 60));
            while (nextFrame <= requested) ApplyFrame(nextFrame++);
        }

        public void ApplyFrame(int frame)
        {
            Initialize();
            if (frame < 0 || frame >= 440) throw new ArgumentOutOfRangeException(nameof(frame));
            currentFrame = frame;
            var a = baseline[frame];
            Place(baselineRunner, a, comparison ? 1.5f : 0);
            Pose(baselineModel, frame, baselineModelPosition, baselineRotation, baselineScale);
            baselineInput.SetActive(RecentInput(baseline, frame));
            cameraRig.localPosition = new Vector3(a.X + 3, 0, -15);
            if (!comparison) return;
            int actualDelayedFrame = Math.Min(frame, delayed.Length - 1);
            Place(delayedRunner, delayed[actualDelayedFrame], -1.5f);
            Pose(delayedModel, actualDelayedFrame, delayedModelPosition, delayedRotation, delayedScale);
            delayedInput.SetActive(RecentInput(delayed, frame));
            delayedCollision.SetActive(frame >= delayed.Length - 1);
        }

        private void Pose(Transform model, int frame, Vector3 at, Quaternion rotation, Vector3 scale)
        {
            float time = (frame / 60f) % walkingClip.length;
            walkingClip.SampleAnimation(model.gameObject, time);
            model.localPosition = at;
            model.localRotation = rotation;
            model.localScale = scale;
        }

        private static void Place(Transform actor, RunnerFrame state, float lane)
        {
            actor.localPosition = new Vector3(state.X, lane + state.Height, 0);
        }

        private static bool RecentInput(RunnerFrame[] frames, int frame)
        {
            for (int i = Math.Min(frame, frames.Length - 1); i >= Math.Max(0, frame - 6); i--)
                if (frames[i].JumpInput) return true;
            return false;
        }

        public static float[] FeedbackSamples()
        {
            var samples = new float[3428];
            for (int i = 0; i < samples.Length; i++)
            {
                double envelope = Math.Sin(Math.PI * i / (samples.Length - 1));
                samples[i] = (float)(.12 * envelope * Math.Sin(2 * Math.PI * 523.25 * i / 48000));
            }
            return samples;
        }
    }
}
