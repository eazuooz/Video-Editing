import type {PoseKey} from './model';

export type SectionId = 'game' | 'frames' | 'source-rates' | 'pose24' | 'position24' | 'close';
export type Cue = {startFrame: number; endFrame: number};
export type Section = {
  id: SectionId; visualId?: SectionId; startFrame: number; endFrame: number;
  start?: number; end?: number; forceDiagram?: boolean; frameDirectory?: string;
};
export type Timing = {
  revision: 'animation-tick-v1'; fps: 60; frames: number; previewOnly: false;
  durationSeconds?: number; timingInputs: {voiceSha256: string};
  sections: Section[]; events: Record<string, Cue>;
  reactions?: {start: number; end: number; kind: 'puzzled' | 'realize' | 'relief'}[];
};
export type Cut = {
  frameDirectory: string; maxDuration: number; firstFrame?: number;
  pattern?: string; digits?: number;
  /** Editorial target keyframes in native1920×1080 source coordinates. */
  focus?: {time: number; x: number; y: number; radiusX: number; radiusY: number}[];
};
export type Config = {
  game: 'Cuphead'; frameRoot: string;
  framesPrepared: boolean;
  cuts: Partial<Record<SectionId, Cut>>;
  poseImages: Record<PoseKey, string>;
};

export const SECTION_IDS: readonly SectionId[] = [
  'game', 'frames', 'source-rates', 'pose24', 'position24', 'close',
];
const CUE_IDS = [
  'p1-1', 'p1-2', 'p2-1', 'p2-2', 'p2-3', 'p2-4', 'p3-1', 'p3-2',
  'p4-1', 'p4-2', 'p4-3', 'p4-4', 'p5-1', 'p5-2', 'p5-3', 'p5-4',
  'p6-1', 'p6-2', 'p6-3',
] as const;

/**
 * Deliberately no synthetic/default timeline. Vite discovers these files only
 * after actual current-voice timing and inspected source frames are prepared.
 * Importing/typechecking this project never starts a render or a dev server.
 */
const timingModules = import.meta.glob(
  '../../../../projects/shorts-cuphead-animation-tick/production/visual-timing.json',
  {eager: true, import: 'default'},
);
const configModules = import.meta.glob(
  '../../../../projects/shorts-cuphead-animation-tick/production/visual-config.json',
  {eager: true, import: 'default'},
);

export function validateProductionInput(timingValue: unknown, configValue: unknown): {
  timing: Timing; config: Config;
} {
  const t = timingValue as Timing | undefined;
  const c = configValue as Config | undefined;
  if (!t || !c)
    throw new Error('Cuphead awaits actual-PCM visual-timing.json and inspected visual-config.json; no provisional render is permitted.');
  if (t.revision !== 'animation-tick-v1' || t.fps !== 60 || t.previewOnly !== false ||
      !Number.isInteger(t.frames) || t.frames < 1 ||
      !/^[a-f0-9]{64}$/i.test(t.timingInputs?.voiceSha256 ?? ''))
    throw new Error('Require current animation-tick-v1 actual voice hash, fps60 and final PCM-derived timing.');
  if (!Array.isArray(t.sections) || t.sections.length !== SECTION_IDS.length)
    throw new Error('Require the six narration-linked sections in their teaching order.');
  let nextFrame = 0;
  for (let i = 0; i < t.sections.length; i++) {
    const s = t.sections[i];
    if (s.id !== SECTION_IDS[i] || s.startFrame !== nextFrame ||
        !Number.isInteger(s.startFrame) || !Number.isInteger(s.endFrame) ||
        s.endFrame <= s.startFrame)
      throw new Error(`Invalid or discontinuous Cuphead section ${s.id}.`);
    nextFrame = s.endFrame;
  }
  if (nextFrame !== t.frames) throw new Error('Cuphead sections must cover the exact current PCM duration.');
  let previousCueEnd = 0;
  for (const id of CUE_IDS) {
    const cue = t.events?.[id];
    const paragraph = Number(id.match(/^p(\d)-/)?.[1]) - 1;
    const ownSection = t.sections[paragraph];
    if (!cue || !Number.isInteger(cue.startFrame) || !Number.isInteger(cue.endFrame) ||
        cue.startFrame < previousCueEnd || cue.endFrame <= cue.startFrame || cue.endFrame > t.frames ||
        cue.startFrame < ownSection.startFrame || cue.endFrame > ownSection.endFrame)
      throw new Error(`Missing/invalid actual speech cue ${id}.`);
    previousCueEnd = cue.endFrame;
  }
  if (c.game !== 'Cuphead' || c.framesPrepared !== true || !c.frameRoot || !c.cuts?.game || t.sections[0].forceDiagram ||
      !['A', 'B', 'C'].every(k => c.poseImages?.[k as PoseKey]))
    throw new Error('Require inspected Cuphead frame root and three provenance-linked analysis images.');
  for (const [id, cut] of Object.entries(c.cuts ?? {})) {
    if (!SECTION_IDS.includes(id as SectionId) || !cut || !cut.frameDirectory ||
        !(cut.maxDuration > 0) || !Number.isFinite(cut.maxDuration))
      throw new Error(`Invalid source cut ${id}.`);
    let previous = -1;
    for (const key of cut.focus ?? []) {
      if (![key.time, key.x, key.y, key.radiusX, key.radiusY].every(Number.isFinite) ||
          key.time <= previous || key.time < 0 || key.time > cut.maxDuration ||
          key.x < 0 || key.x > 1920 || key.y < 0 || key.y > 1080 ||
          key.radiusX <= 0 || key.radiusY <= 0)
        throw new Error(`Invalid inspected source focus keyframe in ${id}.`);
      previous = key.time;
    }
  }
  return {timing: t, config: c};
}

export function requireProductionInput() {
  return validateProductionInput(Object.values(timingModules)[0], Object.values(configModules)[0]);
}
