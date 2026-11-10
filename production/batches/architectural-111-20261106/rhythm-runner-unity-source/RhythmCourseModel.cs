using System;
using System.Collections.Generic;

namespace Yamyam.LevelDesign.RhythmRunner
{
    public readonly struct RunnerFrame
    {
        public readonly int Frame;
        public readonly float X;
        public readonly float Height;
        public readonly bool JumpInput;
        public readonly int ObstacleIndex;
        public readonly bool Cleared;

        public RunnerFrame(int frame, float x, float height, bool jumpInput, int obstacleIndex, bool cleared)
        {
            Frame = frame;
            X = x;
            Height = height;
            JumpInput = jumpInput;
            ObstacleIndex = obstacleIndex;
            Cleared = cleared;
        }
    }

    // A self-authored fixed-speed runner for 13.02, not a model of BIT.TRIP RUNNER.
    public static class RhythmCourseModel
    {
        public const int FramesPerSecond = 60;
        public const int DurationFrames = 440;
        public const float Speed = 4f;
        public const float ObstacleHeight = 0.6f;
        public const int JumpDurationFrames = 54;
        public const int LastObstacleDelayFrames = 34;
        private const float JumpApex = 1.25f;
        private static readonly int[] Inputs = { 60, 150, 240, 330 };
        private static readonly int[] ObstacleCrossings = { 87, 177, 267, 357 };

        public static float ObstacleX(int index, bool delayLastObstacle)
        {
            return Crossing(index, delayLastObstacle) * Speed / FramesPerSecond;
        }

        public static IEnumerable<RunnerFrame> Simulate(bool delayLastObstacle)
        {
            int input = 0;
            int obstacle = 0;
            int lastJump = -JumpDurationFrames;
            for (int frame = 0; frame < DurationFrames; frame++)
            {
                bool pressed = input < Inputs.Length && frame == Inputs[input];
                if (pressed)
                    lastJump = Inputs[input++];

                float phase = (frame - lastJump) / (float)JumpDurationFrames;
                float height = phase < 1 ? 4 * JumpApex * phase * (1 - phase) : 0;
                bool crossing = obstacle < ObstacleCrossings.Length && frame == Crossing(obstacle, delayLastObstacle);
                bool cleared = crossing && height >= ObstacleHeight;
                yield return new RunnerFrame(frame, frame * Speed / FramesPerSecond, height, pressed,
                    crossing ? obstacle : -1, cleared);

                if (crossing && !cleared)
                    yield break;
                if (crossing)
                    obstacle++;
            }
        }

        private static int Crossing(int index, bool delayLastObstacle)
        {
            if (index < 0 || index >= ObstacleCrossings.Length)
                throw new ArgumentOutOfRangeException(nameof(index));
            int delay = delayLastObstacle && index == ObstacleCrossings.Length - 1 ? LastObstacleDelayFrames : 0;
            return ObstacleCrossings[index] + delay;
        }
    }
}
