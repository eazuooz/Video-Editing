/** Pure timeline/file selection for compositing. No renderer, filesystem or clock side effects. */
export const SECTIONS = ['game', 'sheet', 'collision', 'uv', 'stamp', 'patch', 'orbit'] as const;
export type SectionId = typeof SECTIONS[number];
export const CUES = [
  'p1-1', 'p1-2', 'p2-1', 'p2-2', 'p2-3', 'p3-1', 'p3-2', 'p3-3',
  'p4-1', 'p4-2', 'p4-3', 'p4-4', 'p5-1', 'p5-2', 'p5-3', 'p5-4',
  'p6-1', 'p6-2', 'p7-1', 'p7-2', 'p7-3',
] as const;
export type CueId = typeof CUES[number];
export type Point = [number, number];
export type Cue = {startFrame: number; endFrame: number};
export type Section = Cue & {id: SectionId};
export type GameplayWindow = Cue & {cut: 'floor' | 'wall'; sourceFrameOffset?: number};
export type Timing = {
  revision: 'surface-ink-v1'; fps: 60; frames: number; previewOnly: false;
  voiceDurationSeconds: number; voiceOffsetSeconds?: number;
  timingInputs: {voiceSha256: string; narrationSha256?: string; clausesSha256?: string};
  sections: Section[]; events: Record<CueId, Cue>;
  /** Explicit final-timeline windows, never inferred from paragraph length. */
  gameplayWindows: GameplayWindow[];
};
export type Sequence = Cue & {
  directory: string; root?: string; pattern?: string; digits?: number; firstFrame?: number;
  indexBasis: 'absolute-final-frame' | 'sequence-relative';
};
export type Focus = {time: number; x: number; y: number; radiusX: number; radiusY: number};
export type Cut = {
  directory: string; root?: string; pattern?: string; digits?: number; firstFrame?: number;
  frameCount: number; sourceStartSeconds: number; sourceEndSeconds: number;
  sourceSha256: string; nativeDimensions: [1920, 1080]; fps: 60;
  inspected: boolean; focus?: Focus[];
};
export type Config = {
  revision: 'surface-ink-v1'; framesPrepared: boolean; frameRoot: string;
  unityImagePlacement: {size: [648, 1152]; center: [540, 860]; preserveAspect: true};
  gameplayCuts: Record<'floor' | 'wall', Cut>;
  unityFrames: {
    root: string; width: 1080; height: 1920; fps: 60;
    captured: boolean; voiceSha256: string | null; sequences: Sequence[];
  };
  compositing: {
    anchorsReviewed: boolean;
    anchors: {sheet: Point; wall: Point; floor: Point; impact: Point; seam: Point};
    uvReadout: {u: number | null; v: number | null; runtimeVerified: boolean; evidencePath: string | null};
  };
};
export const clamp01 = (n: number) => Math.max(0, Math.min(1, n));
export const smooth = (n: number) => {const p = clamp01(n); return p * p * (3 - 2 * p);};
export const validFrame = (n: number) => Number.isInteger(n) && n >= 0;
const hash = (value: unknown) => typeof value === 'string' && /^[0-9a-f]{64}$/i.test(value);
const registeredRoot = (root: string) => /^\/@fs\/D:\/Github\/VideoEditing\/projects\/shorts-splatoon-surface-ink\/production\/local\//i.test(root.replace(/\\/g, '/'));

export function sectionAt(timing: Timing, frame: number): Section {
  if (!validFrame(frame) || frame >= timing.frames) throw new Error('Frame outside exact final timeline.');
  const section = timing.sections.find(s => frame >= s.startFrame && frame < s.endFrame);
  if (!section) throw new Error('No contiguous section for final frame.');
  return section;
}

export function gameplayAt(timing: Timing, frame: number) {
  return timing.gameplayWindows.find(w => frame >= w.startFrame && frame < w.endFrame);
}

export function sequenceAt(config: Config, frame: number) {
  return config.unityFrames.sequences.find(s => frame >= s.startFrame && frame < s.endFrame);
}

export function fileUrl(root: string, directory: string, frame: number, pattern = '{frame}.jpg', digits = 6) {
  if (!validFrame(frame)) throw new Error('Image sequence index must be a nonnegative integer.');
  const name = pattern.replace('{frame}', String(frame).padStart(digits, '0'));
  return root.replace(/\/$/, '') + '/' + directory.replace(/^\/+|\/+$/g, '') + '/' + name;
}

export function visualAt(timing: Timing, config: Config, frame: number) {
  const game = gameplayAt(timing, frame);
  if (game) {
    const cut = config.gameplayCuts[game.cut];
    const index = (cut.firstFrame ?? 0) + (game.sourceFrameOffset ?? 0) + frame - game.startFrame;
    return {kind: 'gameplay' as const, cut: game.cut, index,
      sourceSeconds: cut.sourceStartSeconds + ((game.sourceFrameOffset ?? 0) + frame - game.startFrame) / 60,
      path: fileUrl(cut.root ?? config.frameRoot, cut.directory, index, cut.pattern, cut.digits)};
  }
  const sequence = sequenceAt(config, frame);
  if (!sequence) throw new Error(`No explicit Unity capture mapping for absolute timeline frame ${frame}.`);
  const index = sequence.indexBasis === 'absolute-final-frame'
    ? frame : (sequence.firstFrame ?? 0) + frame - sequence.startFrame;
  return {kind: 'unity' as const, cut: undefined, index, sourceSeconds: undefined,
    path: fileUrl(sequence.root ?? config.unityFrames.root, sequence.directory,
      index, sequence.pattern, sequence.digits)};
}

export function cueProgress(timing: Timing, frame: number, first: CueId, last: CueId = first) {
  const a = timing.events[first].startFrame;
  const b = timing.events[last].endFrame;
  return clamp01((frame - a) / Math.max(1, b - a - 1));
}

export function focusAt(keys: Focus[], sourceSecondsFromCutStart: number) {
  const t = sourceSecondsFromCutStart;
  if (!keys.length || t < keys[0].time || t > keys[keys.length - 1].time) return undefined;
  const next = keys.findIndex(k => k.time >= t);
  if (next <= 0) return keys[0];
  const a = keys[next - 1], b = keys[next];
  const p = clamp01((t - a.time) / (b.time - a.time));
  return {time: t, x: a.x + (b.x - a.x) * p, y: a.y + (b.y - a.y) * p,
    radiusX: a.radiusX + (b.radiusX - a.radiusX) * p,
    radiusY: a.radiusY + (b.radiusY - a.radiusY) * p};
}

export function validateProductionInput(timingValue: unknown, configValue: unknown) {
  const t = timingValue as Timing | undefined;
  const c = configValue as Config | undefined;
  if (!t || !c) throw new Error('SurfaceInk requires actual-PCM visual-timing.json and prepared capture config; no provisional render.');
  if (t.revision !== 'surface-ink-v1' || t.fps !== 60 || t.previewOnly !== false ||
      !validFrame(t.frames) || t.frames < 1 || !hash(t.timingInputs?.voiceSha256) ||
      !(t.voiceDurationSeconds > 0) || !Number.isFinite(t.voiceDurationSeconds))
    throw new Error('Require surface-ink-v1 exact PCM hash/duration, final frame count and fps60.');
  if (t.timingInputs.narrationSha256 && t.timingInputs.narrationSha256 !== 'e58065ae39d65647f0ebf1402643499422570e1a4ca3bb90a6c2e3e5abe66b00')
    throw new Error('SurfaceInk canonical narration hash differs.');
  if (t.timingInputs.clausesSha256 && t.timingInputs.clausesSha256 !== '7911f7dc0ad620b797279815758e06331bbb7548f489b9249a7f0075bab35e03')
    throw new Error('SurfaceInk canonical21-clause hash differs.');
  if (!Array.isArray(t.sections) || t.sections.length !== 7) throw new Error('Require seven ordered contiguous narration sections.');
  let end = 0;
  for (let i = 0; i < SECTIONS.length; i++) {
    const s = t.sections[i];
    if (s.id !== SECTIONS[i] || s.startFrame !== end || !validFrame(s.endFrame) || s.endFrame <= s.startFrame)
      throw new Error(`Invalid/gapped SurfaceInk section ${s.id}.`);
    end = s.endFrame;
  }
  if (end !== t.frames) throw new Error('Sections must cover the exact final PCM-derived timeline.');
  if (!t.events || Object.keys(t.events).length !== CUES.length) throw new Error('Require all and only21 actual speech events.');
  let previous = 0;
  for (const id of CUES) {
    const cue = t.events[id];
    const section = t.sections[Number(id.match(/^p(\d)-/)?.[1]) - 1];
    if (!cue || !validFrame(cue.startFrame) || !validFrame(cue.endFrame) ||
        cue.startFrame < previous || cue.endFrame <= cue.startFrame ||
        cue.startFrame < section.startFrame || cue.endFrame > section.endFrame)
      throw new Error(`Invalid/missing measured clause ${id}.`);
    previous = cue.endFrame;
  }
  if (c.revision !== 'surface-ink-v1' || c.framesPrepared !== true || !registeredRoot(c.frameRoot) ||
      c.unityImagePlacement?.size?.join(',') !== '648,1152' ||
      c.unityImagePlacement?.center?.join(',') !== '540,860' || c.unityImagePlacement.preserveAspect !== true ||
      c.unityFrames?.captured !== true || c.unityFrames.width !== 1080 || c.unityFrames.height !== 1920 ||
      c.unityFrames.fps !== 60 || c.unityFrames.voiceSha256 !== t.timingInputs.voiceSha256 ||
      !registeredRoot(c.unityFrames.root) || !Array.isArray(c.unityFrames.sequences))
    throw new Error('Require current-voice-bound real Unity captures and the preserved648x1152 placement via D: junction URLs.');
  if (!c.compositing?.anchorsReviewed || !c.compositing.uvReadout.runtimeVerified ||
      !c.compositing.uvReadout.evidencePath ||
      ![c.compositing.uvReadout.u, c.compositing.uvReadout.v].every(n => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 1))
    throw new Error('Actual capture anchor review and our Unity UV readout evidence are still required.');
  if (Math.abs(c.compositing.uvReadout.u! - .5) > .001 || Math.abs(c.compositing.uvReadout.v! - .5) > .001)
    throw new Error('Actual example must match the narrated wall-center UV(0.5,0.5); do not relabel another hit.');
  for (const point of Object.values(c.compositing.anchors)) {
    if (!Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite) ||
        point[0] < 0 || point[0] > 1080 || point[1] < 440 || point[1] >= 1290)
      throw new Error('A reviewed full-resolution surface anchor is outside the explanatory safe region.');
  }
  const sourceHashes = {
    floor: '0c9bcb99f0344e7023d82446fe82012239a97b1aa40a03348781a096c7b57ccd',
    wall: '164a876b17ae78c4fbcbe0c3321d7ff7ae752fa806c68b62c22f9350288baa75',
  };
  for (const key of ['floor', 'wall'] as const) {
    const cut = c.gameplayCuts?.[key];
    const bounds = key === 'floor' ? [62.4, 66.3] : [68.5, 71.5];
    if (!cut || !cut.inspected || cut.sourceSha256 !== sourceHashes[key] || cut.fps !== 60 ||
        cut.nativeDimensions?.join(',') !== '1920,1080' || !cut.directory ||
        cut.sourceStartSeconds !== bounds[0] || cut.sourceEndSeconds !== bounds[1] ||
        !validFrame(cut.frameCount) || cut.frameCount !== Math.round((bounds[1] - bounds[0]) * 60) ||
        (cut.root !== undefined && !registeredRoot(cut.root)))
      throw new Error(`Native inspected source/cut ${key} changed or was not prepared.`);
    let previousTime = -1;
    for (const k of cut.focus ?? []) {
      if (![k.time, k.x, k.y, k.radiusX, k.radiusY].every(Number.isFinite) ||
          k.time <= previousTime || k.time < 0 || k.time > cut.frameCount / 60 ||
          k.x < 0 || k.x > 1920 || k.y < 0 || k.y > 1080 || k.radiusX <= 0 || k.radiusY <= 0)
        throw new Error('Invalid inspected editorial target keyframe.');
      previousTime = k.time;
    }
  }
  if (!Array.isArray(t.gameplayWindows) || t.gameplayWindows.length !== 2 ||
      t.gameplayWindows[0]?.cut !== 'floor' || t.gameplayWindows[1]?.cut !== 'wall' ||
      t.gameplayWindows[0]?.startFrame !== 0)
    throw new Error('Opening needs two explicitly timed native windows: floor, then wall; no loops.');
  let previousEnd = 0;
  for (const w of t.gameplayWindows) {
    const cut = c.gameplayCuts[w.cut];
    if (!validFrame(w.startFrame) || !validFrame(w.endFrame) || w.startFrame < previousEnd ||
        w.endFrame <= w.startFrame || w.endFrame > t.sections[0].endFrame ||
        !validFrame(w.sourceFrameOffset ?? 0) ||
        (w.sourceFrameOffset ?? 0) + w.endFrame - w.startFrame > cut.frameCount)
      throw new Error('Opening cut exceeds inspected source or first paragraph; never hold/loop to fill speech.');
    previousEnd = w.endFrame;
  }
  previousEnd = 0;
  for (const s of c.unityFrames.sequences) {
    if (!validFrame(s.startFrame) || !validFrame(s.endFrame) || s.startFrame < previousEnd ||
        s.endFrame <= s.startFrame || s.endFrame > t.frames || !s.directory ||
        !['absolute-final-frame', 'sequence-relative'].includes(s.indexBasis) ||
        !validFrame(s.firstFrame ?? 0) || (s.root !== undefined && !registeredRoot(s.root)))
      throw new Error('Invalid explicit Unity capture-to-timeline sequence mapping.');
    previousEnd = s.endFrame;
  }
  for (let frame = 0; frame < t.frames; frame++) {
    if (!gameplayAt(t, frame) && !sequenceAt(c, frame))
      throw new Error(`Unity capture mapping missing at absolute timeline frame ${frame}.`);
  }
  return {timing: t, config: c};
}
