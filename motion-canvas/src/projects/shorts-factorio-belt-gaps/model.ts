/**
 * Authored, finite-width teaching model. These are illustrative units, not
 * recovered Factorio positions, item dimensions, CPU timings, or UPS values.
 * x is the LEFT edge of a width-one item on a length-thirteen transport line.
 */
export const BELT_LENGTH = 13;
export const ITEM_WIDTH = 1;
export const INITIAL_POSITIONS = [1, 4, 7, 10] as const;

export const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
export const smooth = (value: number) => {
  const x = clamp01(value);
  return x * x * (3 - 2 * x);
};

/** [input gap, A–B, B–C, C–D, output gap]. Sum(gaps) + 4 widths = 13. */
export function freeGaps(positions: readonly number[]): number[] {
  return [
    positions[0],
    ...positions.slice(1).map((x, i) => x - positions[i] - ITEM_WIDTH),
    BELT_LENGTH - positions[positions.length - 1] - ITEM_WIDTH,
  ];
}

export function translate(positions: readonly number[], distance: number): number[] {
  return positions.map(x => x + distance);
}

/** Two already-touching front items remain packed while the next gap closes. */
export function blockedPositions(reachEnd: number, packFront: number, packNext = 0): number[] {
  const reach = clamp01(reachEnd);
  const front = clamp01(packFront);
  const next = clamp01(packNext);
  return [
    2 + reach + 2 * front + 2 * next,
    5 + reach + 2 * front + 2 * next,
    8 + reach + 2 * front,
    11 + reach,
  ];
}

/** Gap nearest the OUTPUT that still has free space, excluding both endpoints. */
export function lastPositiveInternalGap(positions: readonly number[]): number {
  const gaps = freeGaps(positions);
  for (let i = gaps.length - 2; i > 0; i--) {
    if (gaps[i] > 1e-7) return i;
  }
  return -1;
}
