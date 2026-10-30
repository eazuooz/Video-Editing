/** Authored explanatory state; no commercial game's hidden measurements. */
export type Point = [number, number];
export type SectionKind = 'game' | 'unity' | 'diagram';
export type Section = {
  id: string; kind: SectionKind; startFrame: number; endFrame: number;
  start: number; end: number; frameDirectory?: string; firstFrame?: number;
  digits?: number; framePattern?: string; width?: number; height?: number;
  title?: string; diagramType?: 'grid' | 'eud' | 'replay'; unityStage?: number;
  steps?: string[]; activeStep?: number; termVisible?: boolean;
  sourceStart?: number; crop?: {center: Point; width: number};
};
export type Timing = {
  revision: string; previewOnly: boolean; fps: number; frames: number;
  durationSeconds?: number; sections: Section[];
  timingInputs?: {voiceSha256: string};
  events?: Record<string, {startFrame: number; endFrame: number}>;
  reactions?: {start: number; end: number; kind: 'realize' | 'relief' | 'think'}[];
  annotations?: Record<string, Mark[]>;
};
export type Mark = {
  start: number; end: number; label: string;
  labelCenter?: Point;
  role?: 'focus' | 'problem' | 'result'; kind?: 'box' | 'ellipse' | 'arrow';
  keyframes: {at: number; center: Point; size: Point; labelCenter?: Point; visible?: boolean}[];
};
export type Config = {
  slug: string; game: string; head: string[]; term: string; english: string;
  plainMeaning?: string; frameRoot: string; diagramType?: 'grid' | 'eud' | 'replay';
  annotations?: Record<string, Mark[]>;
  catReactions?: Timing['reactions'];
};

export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const smooth = (v: number) => {const t = clamp(v); return t * t * (3 - 2 * t);};
export const lerpPoint = (a: Point, b: Point, t: number): Point => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
export function frameSource(section: Section, globalFrame: number, root: string): string {
  if (!section.frameDirectory) throw new Error('Native/actual frames need an explicit inspected frame directory.');
  const directory = section.frameDirectory.startsWith('/') ? section.frameDirectory : root.replace(/\/$/, '') + '/' + section.frameDirectory;
  const frame = (section.firstFrame ?? 0) + Math.max(0, Math.min(section.endFrame - section.startFrame - 1, globalFrame - section.startFrame));
  return directory.replace(/\/$/, '') + '/' + (section.framePattern ?? '{frame}.jpg').replace('{frame}', String(frame).padStart(section.digits ?? 6, '0'));
}
export function validate(timing: Timing, config: Config) {
  if (timing.revision !== 'tech-ten-v1' || timing.previewOnly !== false || timing.fps !== 60 || timing.frames < 1)
    throw new Error('Render only current final-PCM FHD60 timing.');
  let previous = 0;
  for (const s of timing.sections) {
    if (s.startFrame !== previous || s.endFrame <= s.startFrame || s.endFrame > timing.frames)
      throw new Error('Sections must cover the complete timeline without gaps or overlap.');
    if (Math.abs(s.start - s.startFrame / 60) > 1e-7 || Math.abs(s.end - s.endFrame / 60) > 1e-7)
      throw new Error('Section seconds and native frame indices differ.');
    if (!['game', 'unity', 'diagram'].includes(s.kind)) throw new Error('Unknown picture kind.');
    if (s.kind !== 'diagram' && !s.frameDirectory) throw new Error('Missing actual/native frame sequence.');
    if (s.kind === 'diagram' && !s.diagramType && !config.diagramType) throw new Error('Select one authored mechanism diagram.');
    previous = s.endFrame;
  }
  if (previous !== timing.frames || timing.sections[0]?.kind !== 'game')
    throw new Error('Open on inspected independent game footage and cover every frame.');
  for (const marks of Object.values(timing.annotations ?? config.annotations ?? {})) for (const m of marks) {
    if (!(m.end > m.start) || !m.keyframes.length || m.keyframes.some((k, i) =>
      !Number.isFinite(k.at) || [...k.center, ...k.size].some(x => !Number.isFinite(x))
      || (i > 0 && k.at <= m.keyframes[i - 1].at))) throw new Error('Invalid inspected annotation keyframes.');
  }
}

export function markGeometry(mark: Mark | undefined, elapsed: number) {
  if (!mark) return {center: [0, 0] as Point, size: [0, 0] as Point, visible: false, labelCenter: undefined as Point | undefined};
  const next = mark.keyframes.findIndex(k => k.at >= elapsed);
  if (next <= 0) {const key = mark.keyframes[next < 0 ? mark.keyframes.length - 1 : 0]; return {...key, labelCenter: key.labelCenter ?? mark.labelCenter};}
  if (mark.keyframes[next].at === elapsed) {const key = mark.keyframes[next]; return {...key, labelCenter: key.labelCenter ?? mark.labelCenter};}
  const a = mark.keyframes[next - 1], b = mark.keyframes[next];
  const t = clamp((elapsed - a.at) / (b.at - a.at));
  return {center: lerpPoint(a.center, b.center, t), size: lerpPoint(a.size, b.size, t), visible: a.visible,
          labelCenter: a.labelCenter && b.labelCenter ? lerpPoint(a.labelCenter, b.labelCenter, t) : mark.labelCenter};
}

/** Hide occluded targets, targets beyond decoded pixels, or cut off by the crop. */
export function markVisibleInFrame(mark: Mark | undefined, elapsed: number, section: Section) {
  if (!mark || elapsed < mark.start || elapsed >= mark.end || section.kind !== 'game') return false;
  const g = markGeometry(mark, elapsed);
  if (g.visible === false) return false;
  const [w, h] = [section.width ?? 1920, section.height ?? 1080];
  const [x, y] = g.center, [sx, sy] = g.size;
  const left = mark.kind === 'arrow' ? Math.min(x, x - sx) : x - sx / 2;
  const right = mark.kind === 'arrow' ? Math.max(x, x - sx) : x + sx / 2;
  const top = mark.kind === 'arrow' ? Math.min(y, y - sy) : y - sy / 2;
  const bottom = mark.kind === 'arrow' ? Math.max(y, y - sy) : y + sy / 2;
  if (left < 0 || top < 0 || right > w || bottom > h) return false;
  if (section.crop) {
    const halfWidth = section.crop.width / 2, halfHeight = section.crop.width * .4;
    const [cx, cy] = section.crop.center;
    if (left < cx - halfWidth || right > cx + halfWidth || top < cy - halfHeight || bottom > cy + halfHeight) return false;
  }
  return true;
}

// The same diagonal bridge and area are held fixed while sampling cell size changes.
export const walkableCell = (x: number, y: number, cells: number) => Math.abs((x + .5) / cells - (y + .5) / cells) < .20;
export type ReplayCommand = {tick: number; target: Point; label: string; kind: 'start' | 'move' | 'attack'};
export const COMMANDS: ReplayCommand[] = [
  {tick: 0, target: [1, 2], label: '시작', kind: 'start'},
  {tick: 120, target: [5, 2], label: '이동', kind: 'move'},
  {tick: 240, target: [6, 2], label: '공격', kind: 'attack'},
];
export function simulateReplay(tick: number, speed = .045): Point {
  let position: Point = [1, 2], target: Point = [1, 2];
  for (let t = 0; t <= Math.floor(tick); t++) {
    const command = COMMANDS.find(c => c.tick === t); if (command?.kind === 'move') target = command.target;
    const dx = target[0] - position[0], dy = target[1] - position[1], distance = Math.hypot(dx, dy);
    if (distance > 0) position = [position[0] + dx * Math.min(speed, distance) / distance, position[1] + dy * Math.min(speed, distance) / distance];
  }
  return position;
}
export function replayState(tick: number, damage = 30, seed = 7) {
  const position = simulateReplay(tick);
  // Fixed seed is an explicit starting condition of this small teaching model.
  const randomBonus = Math.floor((((seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 5);
  return {position, health: tick >= 240 ? Math.max(0, 100 - damage - randomBonus) : 100,
          attacking: tick >= 240 && tick < 258, seed};
}
