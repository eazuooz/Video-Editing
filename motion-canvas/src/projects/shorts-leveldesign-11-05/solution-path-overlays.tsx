import {Circle, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {Vector2, createSignal, tween, useScene} from '@motion-canvas/core';

export type Point = [number, number];
export type Role = 'term' | 'result' | 'problem';
export type PointLabel = {
  kind: 'point-label'; point: Point; labelCenter: Point; labelWidth: number;
  label: string; role: Role; sourcePanel: string; anchorId: string;
  visibilityReason: 'actual-perspective-point-ray' | 'reviewed-held-surface-only';
};
export type Term = {presentation: 'definition' | 'chip'; english: string; korean: string; meaning: string};
export type OverlayFrame = {
  outputFrame: number;
  sectionId: string;
  packetFingerprint: string;
  physicalInputFingerprint: string;
  nativeFrame: number;
  layout: 'single-player' | 'dual' | 'observer' | 'ab-player' | 'ab-observer';
  modes: string[];
  sourcePanels: string[];
  commands: PointLabel[];
  term?: Term;
  holdReason?: string;
  // Optional explicitly authored stroke reveal; must come from the timed cue.
  guideReveal?: number;
};

export const STYLE = {
  font: 'Noto Sans KR', background: '#000000', text: '#f5f5f5', muted: '#b8b8b8',
  title: '#e8cf83', term: '#73c7c2', result: '#a4c6a0', problem: '#ef8585',
  captionReservedTop: 1527, rightRail: 936, targetFont: 46,
} as const;
const PHYSICAL = '0fdfd4b196c4daa61a9a2ec01982592c60bb476131178d2002ed04229fadee0b';
const NARRATION = '8a35438d9b12131a60a1ec817aaa11d2f4df21b59c2f645dfd69143a71d92a53';
const MODES = ['construction', 'branches-a', 'branches-b', 'templates-a', 'templates-b', 'threats-a', 'threats-b', 'broken-link'];
const hash = (value: string) => /^[0-9a-f]{64}$/.test(value);
const finitePoint = (point: Point) => point.length === 2 && point.every(Number.isFinite);
// Exact final-narration glossary; meaning lines are authored, not auto-scaled.
export const TERM_DEFINITIONS: ReadonlyArray<readonly [string, string, readonly string[]]> = [
  ['Level Chunk', '레벨 조각', ['작은 플레이 상황을 담은 방 규모의 묶음']],
  ['Solution Path', '출구 연결 경로', ['생성기가 입구에서 출구로 이어지게', '준비하는 경로']],
  ['Room Type', '방 연결 유형', ['어느 방향 출입구를 지켜야 하는지', '정하는 구분']],
  ['Room Template', '방 템플릿', ['연결 조건 안에서 고르는 내부 설계안']],
  ['Connectivity', '연결성', ['방과 통로가 서로 이어진 성질']],
  ['Probabilistic Tile', '확률 타일', ['추첨 결과에 따라 배치가 달라지는', '타일 규칙']],
];

export function definitionRows(term: Term): string[] {
  const match = TERM_DEFINITIONS.filter(([en, ko, lines]) =>
    term.english === en && term.korean === ko && term.meaning === lines.join(' '));
  if (term.presentation !== 'definition' || match.length !== 1) {
    throw new Error('Preserve an exact current glossary term and authored meaning');
  }
  return [`${term.english} (${term.korean})`, ...match[0][2]];
}

/** Public typed UI components; actual source geometry is supplied, never simulated here. */
export function objectLabel(command: PointLabel): Node {
  const node = new Node({});
  const color = STYLE[command.role];
  node.add(new Line({points: [command.point, command.labelCenter], stroke: color, lineWidth: 7}));
  node.add(new Circle({position: command.point, size: 38, stroke: color, lineWidth: 9}));
  node.add(new Rect({position: command.labelCenter, width: command.labelWidth, height: 68,
    fill: STYLE.background, stroke: color, lineWidth: 3}));
  node.add(new Txt({position: command.labelCenter, text: command.label, fontFamily: STYLE.font,
    fontSize: STYLE.targetFont, fontWeight: 700, fill: color}));
  return node;
}

export function termDefinition(term: Term): Node {
  const node = new Node({});
  definitionRows(term).forEach((text, i) => node.add(new Txt({
    x: 488, y: 1060 + i * 82, text, fontFamily: STYLE.font, fontSize: 48, fontWeight: i === 0 ? 700 : 500,
    fill: i === 0 ? STYLE.title : STYLE.text,
  })));
  return node;
}

export function termChip(term: Term): Txt {
  return new Txt({x: 488, y: 338, text: `${term.english} (${term.korean})`,
    fontFamily: STYLE.font, fontSize: 40, fontWeight: 700, fill: STYLE.title});
}

export function validateFrame(frame: OverlayFrame, index: number, segmentStartFrame = 0): void {
  if (frame.outputFrame !== segmentStartFrame + index || !frame.sectionId?.trim() || frame.physicalInputFingerprint !== PHYSICAL ||
      !hash(frame.packetFingerprint) || !Number.isInteger(frame.nativeFrame) ||
      frame.nativeFrame < 0 || frame.nativeFrame >= 3120) throw new Error('Current source-bound native frame required');
  if (!['single-player', 'dual', 'observer', 'ab-player', 'ab-observer'].includes(frame.layout)) throw new Error('Unknown layout');
  const ab = frame.layout.startsWith('ab-');
  if (frame.modes.length !== (ab ? 2 : 1) || new Set(frame.modes).size !== frame.modes.length ||
      frame.modes.some(mode => !MODES.includes(mode))) throw new Error('Current distinct mode selection required');
  const cameras = frame.layout === 'dual' ? ['player', 'observer'] :
    frame.layout.includes('observer') ? (ab ? ['observer', 'observer'] : ['observer']) :
      (ab ? ['player', 'player'] : ['player']);
  const keys = cameras.map((camera, i) => `${frame.modes[ab ? i : 0]}/${camera}/${String(frame.nativeFrame).padStart(4, '0')}`);
  if (JSON.stringify(keys) !== JSON.stringify(frame.sourcePanels)) throw new Error('Clear marks on a source/frame/camera cut');
  if (frame.modes.includes('broken-link') && frame.layout !== 'observer' && frame.layout !== 'ab-observer' &&
      frame.nativeFrame >= 2880) throw new Error('Late broken player source is excluded');
  if (frame.commands.length > 2) throw new Error('At most two source-attached labels');
  if (frame.term?.presentation === 'definition') definitionRows(frame.term);
  if (frame.term?.presentation === 'definition' && frame.commands.length) throw new Error('Clear target marks for the definition focus');
  for (const command of frame.commands) {
    if (command.kind !== 'point-label' || !finitePoint(command.point) || !finitePoint(command.labelCenter) ||
        command.point[0] < 48 || command.point[0] >= STYLE.rightRail ||
        command.point[1] < 350 || command.point[1] >= STYLE.captionReservedTop ||
        !frame.sourcePanels.includes(command.sourcePanel) ||
        !['actual-perspective-point-ray', 'reviewed-held-surface-only'].includes(command.visibilityReason) ||
        !['term', 'result', 'problem'].includes(command.role) || !command.label.trim() ||
        !Number.isFinite(command.labelWidth) || command.labelWidth <= 0 || command.labelWidth > 800 ||
        command.labelCenter[0] - command.labelWidth / 2 < 48 ||
        command.labelCenter[0] + command.labelWidth / 2 >= STYLE.rightRail ||
        command.labelCenter[1] - 34 < 350 || command.labelCenter[1] + 34 >= STYLE.captionReservedTop) {
      throw new Error('Measured label/leader conflicts with header, caption or rail');
    }
    if (command.visibilityReason === 'reviewed-held-surface-only' &&
        (!frame.modes.includes('broken-link') || frame.nativeFrame !== 1560 ||
         command.anchorId !== 'closed-port-10-11' || !command.sourcePanel.includes('/observer/'))) throw new Error('Observer surface rule cannot extrapolate');
    if (command.visibilityReason === 'actual-perspective-point-ray' && !command.sourcePanel.includes('/player/')) {
      throw new Error('Observer geometry segment is not a perspective pixel-visibility ray');
    }
  }
  if (frame.guideReveal !== undefined && (!Number.isFinite(frame.guideReveal) || frame.guideReveal < 0 || frame.guideReveal > 1)) {
    throw new Error('Authored reveal must be bounded');
  }
}

/** Transparent overlay only. Pillow owns native images, original cat and fixed captions. */
export default makeScene2D(function* (view) {
  const variables = useScene().variables;
  const mode = variables.get('timingMode', 'unbound-preparation')();
  const total = variables.get('totalFrames', 0)();
  const segmentStart = variables.get('segmentStartFrame', -1)();
  const fps = variables.get('fps', 60)();
  const narration = variables.get('narrationSHA256', '')();
  const voice = variables.get('voiceEvidenceSHA256', '')();
  const asr = variables.get('rawAsrReviewSHA256', '')();
  const timeline = variables.get('timelineSHA256', '')();
  const frames = variables.get<OverlayFrame[]>('frameCues', [])();
  if (mode !== 'actual-pcm-asr-aligned' || !Number.isInteger(total) || total <= 0 ||
      !Number.isInteger(segmentStart) || segmentStart < 0 || fps !== 60 ||
      narration !== NARRATION || !hash(voice) || !hash(asr) || !hash(timeline) || frames.length !== total) {
    throw new Error('Pending actual current PCM/ASR-bound frame cues; no default duration or fake timing');
  }
  if (view.width() !== 1080 || view.height() !== 1920) throw new Error('Exact portrait1080x1920 canvas required');
  frames.forEach((frame, index) => {
    validateFrame(frame, index, segmentStart);
    const prior = frames[index - 1];
    if (prior?.sectionId === frame.sectionId) {
      if (JSON.stringify(prior.modes) !== JSON.stringify(frame.modes) || prior.layout !== frame.layout ||
          ![prior.nativeFrame, prior.nativeFrame + 1].includes(frame.nativeFrame) ||
          (prior.nativeFrame === frame.nativeFrame && !frame.holdReason?.trim())) {
        throw new Error('Within one section preserve native1x or an explicitly labelled explanatory hold');
      }
    }
  });
  view.fill('#00000000');
  const current = createSignal<OverlayFrame>(frames[0]);
  const screen = new Node({position: () => view.size().scale(-.5)});
  view.add(screen);
  const term = () => current().term;
  const definition = new Node({opacity: () => term()?.presentation === 'definition' ? 1 : 0});
  screen.add(definition);
  [0, 1, 2].forEach(i => definition.add(new Txt({x: 488, y: 1060 + i * 82,
    text: () => term()?.presentation === 'definition' ? (definitionRows(term()!)[i] ?? '') : '',
    fontFamily: STYLE.font, fontSize: 48, fontWeight: i === 0 ? 700 : 500,
    fill: i === 0 ? STYLE.title : STYLE.text})));
  screen.add(new Txt({x: 488, y: 338, opacity: () => term()?.presentation === 'chip' ? 1 : 0,
    text: () => `${term()?.english ?? ''} (${term()?.korean ?? ''})`, fontFamily: STYLE.font,
    fontSize: 40, fontWeight: 700, fill: STYLE.title}));
  for (let i = 0; i < 2; i++) {
    const command = () => current().commands[i];
    const point = () => new Vector2(command()?.point ?? [0, 0]);
    const label = () => new Vector2(command()?.labelCenter ?? [0, 0]);
    const color = () => STYLE[command()?.role ?? 'term'];
    const node = new Node({opacity: () => command() ? 1 : 0});
    screen.add(node);
    node.add(new Line({points: () => [point(), label()], stroke: color, lineWidth: 7,
      end: () => current().guideReveal ?? 1}));
    node.add(new Circle({position: point, size: 38, stroke: color, lineWidth: 9}));
    node.add(new Rect({position: label, width: () => command()?.labelWidth ?? 0, height: 68,
      fill: STYLE.background, stroke: color, lineWidth: 3}));
    node.add(new Txt({position: label, text: () => command()?.label ?? '', fontFamily: STYLE.font,
      fontSize: STYLE.targetFont, fontWeight: 700, fill: color}));
  }
  screen.add(new Txt({x: 220, y: 1497, text: '설명을 위한 정지 화면',
    opacity: () => current().holdReason ? 1 : 0, fontFamily: STYLE.font, fontSize: 26, fill: STYLE.muted}));
  // This clock is supplied by the future verified timeline, not inferred from text.
  yield* tween(total / 60, value => current(frames[Math.min(total - 1, Math.floor(value * total))]));
});
