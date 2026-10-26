/**
 * Authored sample schedule. These are not measured Cuphead positions, input
 * polling, physics ticks, clean sprite assets or benchmark results.
 */
export const DISPLAY_FPS = 60;
export const POSITION_UNITS_PER_SECOND = 240;
export type Rate = 24 | 60;
export type PoseKey = 'A' | 'B' | 'C';
export const POSE_KEYS: readonly PoseKey[] = ['A', 'B', 'C'];

export const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
export const smooth = (value: number) => {
  const p = clamp01(value);
  return p * p * (3 - 2 * p);
};

export function sampleAt(displayFrame: number, poseRate: Rate = 24, positionRate: Rate = 60) {
  if (!Number.isInteger(displayFrame) || displayFrame < 0)
    throw new Error('Display frame must be a nonnegative integer.');
  const poseSample = Math.floor(displayFrame * poseRate / DISPLAY_FPS);
  const positionSample = Math.floor(displayFrame * positionRate / DISPLAY_FPS);
  return {
    displayFrame,
    timeSeconds: displayFrame / DISPLAY_FPS,
    poseSample,
    // A/B/C are three inspected drawing EXAMPLES, not a recovered run cycle.
    poseKey: POSE_KEYS[poseSample % POSE_KEYS.length],
    positionSample,
    position: POSITION_UNITS_PER_SECOND * positionSample / positionRate,
  };
}

export function recentThreeFrames(currentFrame: number): [number, number, number] {
  const first = Math.max(0, currentFrame - 2);
  return [first, first + 1, first + 2];
}

export function poseHoldLengths(poseRate: Rate = 24, seconds = 1): number[] {
  const count = DISPLAY_FPS * seconds;
  const holds: number[] = [];
  let previous = -1;
  for (let n = 0; n < count; n++) {
    const sample = sampleAt(n, poseRate);
    if (sample.poseSample === previous) holds[holds.length - 1]++;
    else {holds.push(1); previous = sample.poseSample;}
  }
  return holds;
}

export const displayedNumber = (value: number) => Number.isInteger(value)
  ? String(value) : value.toFixed(1);

/** Six consecutive60Hz display samples, expanded for reading only in our diagram. */
export const EXPANDED_LAST_FRAME = 5;
export function expandedFrame(progress: number): number {
  return Math.min(EXPANDED_LAST_FRAME, Math.floor(clamp01(progress) * (EXPANDED_LAST_FRAME + 1)));
}

export function expandedState(progress: number, positionRate: Rate = 60) {
  const displayFrame = expandedFrame(progress);
  const current = sampleAt(displayFrame, 24, positionRate);
  const previous = sampleAt(Math.max(0, displayFrame - 1), 24, positionRate);
  return {
    current, previous,
    poseChanged: displayFrame === 0 || current.poseSample !== previous.poseSample,
    positionChanged: displayFrame > 0 && current.position !== previous.position,
    // These enlarged0..5-frame positions are not observed Cuphead pixels,
    // physics or input ticks. Both rows share the exact same route scale.
    routeProgress: current.position / sampleAt(EXPANDED_LAST_FRAME, 24, 60).position,
    previousRouteProgress: previous.position / sampleAt(EXPANDED_LAST_FRAME, 24, 60).position,
  };
}
