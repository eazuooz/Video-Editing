using System;
using System.Linq;
using UnityEngine;

namespace Yamyam.LevelDesign.RhythmRunner
{
    public sealed class RhythmCoursePlayback : MonoBehaviour
    {
        public Transform baselineRunner;
        public Transform delayedRunner;
        public Transform cameraRig;
        public GameObject baselineInput;
        public GameObject delayedInput;
        public GameObject delayedCollision;
        public AudioSource baselineFeedback;

        private RunnerFrame[] baseline;
        private RunnerFrame[] delayed;
        private int nextFrame;
        private float elapsed;

        private void Start()
        {
            Initialize();
        }

        public void Initialize()
        {
            if (baseline != null)
                return;
            baseline = RhythmCourseModel.Simulate(false).ToArray();
            delayed = RhythmCourseModel.Simulate(true).ToArray();
            if (baseline.Length != RhythmCourseModel.DurationFrames || delayed.Length >= baseline.Length)
                throw new InvalidOperationException("Unexpected authored course outcome.");

            if (baselineFeedback)
                baselineFeedback.clip = CreateFeedback();
        }

        private void Update()
        {
            elapsed += Time.unscaledDeltaTime;
            int requested = Mathf.FloorToInt(elapsed * RhythmCourseModel.FramesPerSecond);
            while (nextFrame <= requested && nextFrame < baseline.Length)
                ApplyFrame(nextFrame++, true);
        }

        public void ApplyFrame(int frame, bool playFeedback = false)
        {
            if (baseline == null || frame < 0 || frame >= baseline.Length)
                throw new ArgumentOutOfRangeException(nameof(frame));

            RunnerFrame a = baseline[frame];
            RunnerFrame b = delayed[Math.Min(frame, delayed.Length - 1)];
            Place(baselineRunner, a, 1.55f);
            Place(delayedRunner, b, -1.55f);
            cameraRig.localPosition = new Vector3(a.X + 1, 0, -15);
            baselineInput.SetActive(RecentInput(baseline, frame));
            delayedInput.SetActive(RecentInput(delayed, frame));
            delayedCollision.SetActive(frame >= delayed.Length - 1);

            if (playFeedback && a.Cleared && baselineFeedback && baselineFeedback.clip)
                baselineFeedback.PlayOneShot(baselineFeedback.clip);
        }

        private static bool RecentInput(RunnerFrame[] frames, int frame)
        {
            for (int i = Math.Min(frame, frames.Length - 1); i >= Math.Max(0, frame - 6); i--)
                if (frames[i].JumpInput)
                    return true;
            return false;
        }

        private static void Place(Transform actor, RunnerFrame state, float lane)
        {
            actor.localPosition = new Vector3(state.X, lane + state.Height, 0);
        }

        private static AudioClip CreateFeedback()
        {
            const int rate = 48000;
            var samples = new float[rate / 14];
            for (int i = 0; i < samples.Length; i++)
            {
                float phase = i / (float)(samples.Length - 1);
                float envelope = Mathf.Sin(Mathf.PI * phase);
                samples[i] = 0.12f * envelope * Mathf.Sin(2 * Mathf.PI * 523.25f * i / rate);
            }
            AudioClip clip = AudioClip.Create("Original obstacle-clear tone", samples.Length, 1, rate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
