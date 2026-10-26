/**
 * Authored lookup-table illustration, not extracted Teardown code or profiling.
 * Palette/index limits come from Dennis Gustafsson's 2020-12-03 account.
 * IDs, cell grid, colors and RGB-distance metric below are teaching examples.
 */
export type RGB = readonly [number, number, number];
export type Material = {index: number; name: string; rgb: RGB; tint: number};
export const PALETTE_LIMIT = 255;
export const ORIGINAL = 3;
export const VARIANT_IDS = [9, 11, 13, 15] as const;
export const ORIGINAL_RGB: RGB = [111, 67, 53];
export const YELLOW_RGB: RGB = [255, 213, 43];
export const clamp01 = (n: number) => Math.max(0, Math.min(1, n));
export const smooth = (n: number) => {const t = clamp01(n); return t * t * (3 - 2 * t);};
export const hex = (rgb: RGB) => '#' + rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
export const luminance = (rgb: RGB) => rgb.map(n => {
  const c = n / 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4;
}).reduce((sum,n,i) => sum + n * [.2126,.7152,.0722][i], 0);
export const materialTextColor = (rgb: RGB) => luminance(rgb) > .179 ? '#000000' : '#ffffff';
export const blend = (a: RGB, b: RGB, t: number): RGB => a.map((v, i) => v + (b[i] - v) * clamp01(t)) as unknown as RGB;
export const ORIGINAL_MATERIAL: Material = {index: ORIGINAL, name: '벽돌', rgb: ORIGINAL_RGB, tint: 0};
export const VARIANTS: Material[] = VARIANT_IDS.map((index, i) => ({
  // Illustration-only spacing: make the first yellow change readable on mobile.
  // These blends are not measured game tint values or equal simulation steps.
  index, name: `노랑 ${i + 1}`, rgb: blend(ORIGINAL_RGB, YELLOW_RGB, [.45, .65, .82, 1][i]), tint: i + 1,
}));
export const FULL_PALETTE = [ORIGINAL_MATERIAL, ...VARIANTS];
// Same silhouette for every tint. Only the stored index changes.
export const GRID_COLUMNS = 4;
export const GRID_ROWS = 3;
export const CELLS: readonly (readonly [number, number])[] = Array.from({length: GRID_COLUMNS * GRID_ROWS}, (_, i) => [i % GRID_COLUMNS, Math.floor(i / GRID_COLUMNS)] as const);
export const targetForStep = (step: number): Material => FULL_PALETTE[Math.max(0, Math.min(4, Math.round(step)))];
export function squaredDistance(a: RGB, b: RGB): number {
  return a.reduce((sum, value, i) => sum + (value - b[i]) ** 2, 0);
}
export function closestIndex(target: RGB, available: readonly Material[]): number {
  if (!available.length) throw new Error('A nonempty palette is required');
  return available.reduce((best, m) => squaredDistance(m.rgb, target) < squaredDistance(best.rgb, target) ? m : best).index;
}
/** A full table can advance all four steps. A constrained table may repeat an index. */
export function yellowVariant(original: number, step: number, available: readonly Material[] = FULL_PALETTE): number {
  const material = FULL_PALETTE.find(m => m.index === original);
  if (!material) throw new Error(`Unknown illustration index ${original}`);
  return closestIndex(targetForStep(material.tint + step).rgb, available);
}
export function gridIndices(step: number, sweep: number): number[] {
  const target = yellowVariant(ORIGINAL, step);
  // Begin with the cell beside the lookup arrow, then include its neighbours.
  return CELLS.map(([x]) => (GRID_COLUMNS - x - .5) / GRID_COLUMNS <= clamp01(sweep) ? target : ORIGINAL);
}
export const BROWN_FALLBACK: Material = {index: 7, name: '기존 갈색', rgb: [171, 128, 62], tint: 0};
export const LIMITED_PALETTE = [ORIGINAL_MATERIAL, BROWN_FALLBACK];
export const fallbackIndex = (hasRoom: boolean) => yellowVariant(ORIGINAL, 4, hasRoom ? FULL_PALETTE : LIMITED_PALETTE);
export const unchangedIndex = () => yellowVariant(ORIGINAL, 4, [ORIGINAL_MATERIAL]);
export const slotsPerOriginal = (tints = 2, steps = 4) => 1 + tints * steps;
export const maxOriginalsWithoutMixedTints = () => Math.floor(PALETTE_LIMIT / slotsPerOriginal());

