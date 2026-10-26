import configInput from '../../../../projects/shorts-splatoon-ink-readability/production/visual-config.json';
import clausesInput from '../../../../projects/shorts-splatoon-ink-readability/production/clauses.json';

export const SECTION_IDS = ['game', 'pbs', 'boundary', 'flat', 'specular', 'close'] as const;
export type SectionId = typeof SECTION_IDS[number];
export type Point = [number, number];
export type Cue = {startFrame: number; endFrame: number};
export type Section = Cue & {id: SectionId; visualId?: SectionId};
export type Timing = {
  revision: 'ink-readability-v1'; fps: 60; frames: number; previewOnly: false;
  timingInputs: {voiceSha256: string}; sections: Section[]; events: Record<string, Cue>;
  voiceOffsetSeconds: number; tailSecondsMinimum: number; voiceDurationSeconds: number;
};
type Asset = {url: string; sha256: string};
export type FocusKey = {frame: number; x: number; y: number; radiusX: number; radiusY: number};
export type GameCut = Cue & {
  id: 'surface' | 'submerge'; sourceIn: number; sourceOut: number;
  firstFrame: number; frameDirectory: string; pattern: string; digits: number;
  focusReviewed: boolean; focus: FocusKey[]; focusWindow?: Cue;
};
export type Config = {
  revision: 'ink-readability-v1'; inputsReady: true;
  inputs: {timing: Asset; voice: Asset; readback: Asset; captureJob: Asset; captureSuccess: Asset};
  game: {framesPrepared: true; width: number; height: number; fps: 60; sourceSha256: string; cuts: GameCut[]};
  unity: {framesPrepared: true; width: number; height: number; frameDirectory: string; pattern: string; digits: number};
  /** Manual suppression after inspecting occlusion; no fabricated visibility score. */
  hiddenLabels?: {id: string; startFrame: number; endFrame: number}[];
};
export type Label = {
  id: string; target: string; textKo: string; textEn: string; role: string;
  u: number; v: number; x: number; y: number; depth: number;
  inFrontAndInFrame: boolean; targetActive: boolean; occlusionVerified: boolean;
};
export type RecordFrame = {
  frame: number; sectionId: string; visualId: string; stage: 'balanced' | 'shading' | 'specular';
  comparisonNormalized: number; phaseNormalized: number; pictureKind: 'our-implementation';
  appliedState: {shadingStrength: number; specularStrength: number; submergePhase: number};
  termEn?: string; termKo?: string; meaningKo?: string;
  steps: string[]; activeStep: number; labelRequests: Label[];
};
export type Production = {config: Config; timing: Timing; readback: Map<number, RecordFrame>; gameEndFrame: number};
const BASE = '/@fs/D:/Github/VideoEditing/projects/shorts-splatoon-ink-readability/production/';
const SOURCE_SHA = '164a876b17ae78c4fbcbe0c3321d7ff7ae752fa806c68b62c22f9350288baa75';
const sha = (value: unknown): value is string => typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);
const integer = (value: unknown): value is number => Number.isInteger(value);
function check(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Ink readability input guard: ${message}`);
}
function ownUrl(value: string) {
  check(typeof value === 'string' && value.startsWith(BASE) && !value.includes('..') && !/[?#]/.test(value), 'use the own D:/production URL (media through local junction).');
}
async function verified(asset: Asset): Promise<ArrayBuffer> {
  check(asset && sha(asset.sha256), 'all actual input files require SHA256; no provisional/default data.');
  ownUrl(asset.url);
  const response = await fetch(asset.url, {cache: 'no-store'});
  check(response.ok, `missing input ${asset.url}`);
  const bytes = await response.arrayBuffer();
  const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
  check(digest === asset.sha256.toLowerCase(), `changed input hash: ${asset.url}`);
  return bytes;
}
const json = <T,>(bytes: ArrayBuffer): T => JSON.parse(new TextDecoder().decode(bytes)) as T;
function pcmSeconds(bytes: ArrayBuffer) {
  const view = new DataView(bytes);
  const tag = (offset: number) => String.fromCharCode(...new Uint8Array(bytes, offset, 4));
  check(bytes.byteLength >= 44 && tag(0) === 'RIFF' && tag(8) === 'WAVE', 'voice must be actual PCM WAV.');
  let rate = 0, block = 0, data = 0;
  for (let offset = 12; offset + 8 <= bytes.byteLength;) {
    const name = tag(offset), size = view.getUint32(offset + 4, true), start = offset + 8;
    check(start + size <= bytes.byteLength, 'truncated PCM chunk.');
    if (name === 'fmt ') {
      check(size >= 16 && [1, 3, 65534].includes(view.getUint16(start, true)), 'unsupported compressed voice.');
      rate = view.getUint32(start + 4, true); block = view.getUint16(start + 12, true);
    }
    if (name === 'data') data += size;
    offset = start + size + (size % 2);
  }
  check(rate > 0 && block > 0 && data > 0 && data % block === 0, 'invalid PCM length.');
  return data / (rate * block);
}

/** Fetch and hash current bytes once. Typechecking/importing does not fetch or render. */
export async function requireProductionInput(): Promise<Production> {
  const config = configInput as unknown as Config;
  check(config.revision === 'ink-readability-v1' && config.inputsReady === true, 'await final PCM, actual Unity capture and prepared gameplay frames.');
  check(config.game.framesPrepared === true && config.unity.framesPrepared === true, 'frames are not prepared.');
  const [timingBytes, voiceBytes, traceBytes, jobBytes, successBytes] = await Promise.all([
    verified(config.inputs.timing), verified(config.inputs.voice), verified(config.inputs.readback),
    verified(config.inputs.captureJob), verified(config.inputs.captureSuccess),
  ]);
  const timing = json<Timing>(timingBytes);
  check(timing.revision === config.revision && timing.fps === 60 && timing.previewOnly === false &&
    integer(timing.frames) && timing.frames > 0 && timing.timingInputs?.voiceSha256?.toLowerCase() === config.inputs.voice.sha256.toLowerCase(), 'actual timing/revision/voice hash mismatch.');
  const seconds = pcmSeconds(voiceBytes);
  check(timing.voiceOffsetSeconds === 0.2 && timing.tailSecondsMinimum === 0.4 &&
    Math.abs(seconds - timing.voiceDurationSeconds) < 0.0001 &&
    Math.ceil((seconds + timing.voiceOffsetSeconds + timing.tailSecondsMinimum) * 60 - 1e-8) === timing.frames,
    'timeline must match hashed PCM plus the explicit caption/mixer lead and tail.');
  check(Array.isArray(timing.sections) && timing.sections.length === 6, 'require six paragraphs in source order.');
  let next = 0, cueEnd = 0;
  timing.sections.forEach((section, index) => {
    check(section.id === SECTION_IDS[index] && section.startFrame === next && integer(section.endFrame) && section.endFrame > next, `invalid section ${section.id}`);
    check(!section.visualId || SECTION_IDS.includes(section.visualId), 'unknown visualId.');
    for (const clause of clausesInput.clauses.filter(clause => clause.lineIndex === index)) {
      const id = clause.id, cue = timing.events?.[id];
      check(cue && integer(cue.startFrame) && integer(cue.endFrame) && cue.startFrame >= Math.max(cueEnd, section.startFrame) &&
        cue.endFrame > cue.startFrame && cue.endFrame <= section.endFrame, `missing/invalid actual clause ${id}`);
      cueEnd = cue.endFrame;
    }
    next = section.endFrame;
  });
  check(next === timing.frames, 'paragraphs must cover the exact timeline.');
  check(Object.keys(timing.events).length === clausesInput.clauses.length, 'exact display-clause set required.');
  check(config.game.width === 1920 && config.game.height === 1080 && config.game.fps === 60 && config.game.sourceSha256 === SOURCE_SHA, 'require the inspected native FHD charger source.');
  check(config.game.cuts.length === 2, 'require the two selected native-speed opening cuts.');
  next = 0;
  config.game.cuts.forEach((cut, index) => {
    const range = index === 0 ? [66, 68.2] : [70, 72.8];
    check(cut.id === (index === 0 ? 'surface' : 'submerge') && cut.startFrame === next && integer(cut.endFrame) && cut.endFrame > next &&
      cut.sourceIn >= range[0] && cut.sourceOut <= range[1] + 0.0001 &&
      Math.abs((cut.sourceOut - cut.sourceIn) * 60 - (cut.endFrame - cut.startFrame)) < 0.01,
    'native cut length/range mismatch; never freeze, loop, pad or slow footage.');
    check(integer(cut.firstFrame) && cut.firstFrame >= 0 && integer(cut.digits) && cut.digits > 0 && cut.pattern.includes('{frame}'), 'invalid game image numbering.');
    ownUrl(cut.frameDirectory);
    let previousKey = -1;
    if (cut.focus.length) check(cut.focusWindow && integer(cut.focusWindow.startFrame) && integer(cut.focusWindow.endFrame) &&
      cut.focusWindow.startFrame === cut.focus[0].frame && cut.focusWindow.endFrame === cut.focus[cut.focus.length - 1].frame + 1 &&
      cut.focusWindow.startFrame >= cut.startFrame && cut.focusWindow.endFrame <= cut.endFrame,
      'explicit observed focus window required; hide outside it.');
    for (const key of cut.focus) {
      check(cut.focusReviewed === true && integer(key.frame) && key.frame > previousKey && key.frame >= cut.startFrame && key.frame < cut.endFrame &&
        [key.x, key.y, key.radiusX, key.radiusY].every(Number.isFinite) && key.radiusX > 0 && key.radiusY > 0 &&
        key.x >= 0 && key.x <= 1920 && key.y >= 0 && key.y <= 1080, 'unreviewed/invalid footage focus keyframe.');
      previousKey = key.frame;
    }
    next = cut.endFrame;
  });
  const gameEndFrame = next;
  check(gameEndFrame <= 300 && gameEndFrame <= timing.events['p1-3'].startFrame, 'finish actual game before historical prototype discussion; use Unity after the finite cuts.');
  ownUrl(config.unity.frameDirectory);
  check(config.unity.width >= 1080 && config.unity.height >= 1080 && config.unity.pattern.includes('{frame}') && integer(config.unity.digits), 'invalid native Unity capture format.');
  const job = json<{mode: string; revision: string; timingVerified: boolean; pcmSha256: string; startFrame: number; endFrame: number; totalFrames: number; fps: number; writeJpg: boolean}>(jobBytes);
  const success = json<{status: string; width: number; height: number; fps: number; firstFrame: number; endFrameExclusive: number; renderedFrames: number; timingVerified: boolean; jpgWritten: boolean}>(successBytes);
  check(job.mode === 'sequence' && job.revision === config.revision && job.timingVerified === true && job.writeJpg === true &&
    job.pcmSha256.toLowerCase() === config.inputs.voice.sha256.toLowerCase() && job.fps === 60 && job.totalFrames === timing.frames &&
    job.startFrame <= gameEndFrame && job.endFrame === timing.frames, 'capture job is not from the current PCM timeline.');
  check(success.status === 'render-completed-not-reviewed' && success.timingVerified === true && success.jpgWritten === true &&
    success.width === config.unity.width && success.height === config.unity.height && success.fps === 60 &&
    success.firstFrame === job.startFrame && success.endFrameExclusive === job.endFrame && success.renderedFrames === job.endFrame - job.startFrame, 'capture is incomplete or has incompatible dimensions.');
  const readback = new Map<number, RecordFrame>();
  const lines = new TextDecoder().decode(traceBytes).trim().split(/\r?\n/);
  check(lines.length === success.renderedFrames, 'readback length differs from actual completed capture.');
  lines.forEach((line, index) => {
    const record = JSON.parse(line) as RecordFrame;
    check(record.frame === job.startFrame + index && record.pictureKind === 'our-implementation' &&
      ['balanced', 'shading', 'specular'].includes(record.stage), 'missing, reordered or duplicate actual Unity frame.');
    check(record.appliedState && [record.appliedState.shadingStrength, record.appliedState.specularStrength, record.appliedState.submergePhase].every(Number.isFinite), 'actual applied parameters required.');
    check(Array.isArray(record.labelRequests) && record.labelRequests.length <= 3 && Array.isArray(record.steps) && record.steps.length <= 3, 'provide at most three readable target labels/steps.');
    for (const label of record.labelRequests) check([label.u, label.v, label.depth].every(Number.isFinite), 'invalid projected label.');
    readback.set(record.frame, record);
  });
  for (const hidden of config.hiddenLabels ?? []) check(integer(hidden.startFrame) && integer(hidden.endFrame) && hidden.endFrame > hidden.startFrame, 'invalid reviewed label suppression.');
  return {config, timing, readback, gameEndFrame};
}

export function imageUrl(directory: string, pattern: string, digits: number, frame: number) {
  return `${directory.replace(/\/$/, '')}/${pattern.replace('{frame}', String(frame).padStart(digits, '0'))}`;
}
