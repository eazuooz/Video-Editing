// Full-length transparent overlay for steam-next-fest-ai-flood: term chip (top-left),
// current-picture label (top-right), evidence cards over a dimmed recording, and
// drawn-over-footage strokes (rects/circles/arrows/text) anchored to the recorded
// screen. Durations come from timing.json (measured narration); content from
// spec.json (technical/content explainer grammar, docs/VIDEO_VISUAL_STYLE.md).
import {Circle, Layout, Line, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, waitFor, easeOutCubic, Reference, ThreadGenerator} from '@motion-canvas/core';
import {DARK} from '../../styles/research-dark';
import timing from './timing.json';
import spec from './spec.json';

const FONT = "'Malgun Gothic', 'Segoe UI', sans-serif";
const W = 1920, H = 1080;
const X = (x: number) => x - W / 2; // screen (0,0 top-left) -> scene (centre origin)
const Y = (y: number) => y - H / 2;
type El = Record<string, any>;
const ROLE: Record<string, string> = {title: DARK.title, yellow: DARK.title, teal: DARK.teal, blue: DARK.teal, orange: DARK.orange, red: DARK.red, green: DARK.green, ink: DARK.ink, muted: DARK.muted};
const color = (c?: string) => (c && ROLE[c]) || c || DARK.title;
const LIST_KINDS = ['bars', 'timeline', 'flow', 'status', 'grid'];

function animSeconds(e: El): number {
  if (e.type === 'dim') return 0.35;
  if (e.type === 'card') return 0.35 + (e.kind === 'dots' ? Math.ceil((e.filled ?? 0) / 4) * 0.08 : 0) + (LIST_KINDS.includes(e.kind) ? (e.lines?.length ?? 0) * (e.stepSeconds ?? 0.45) : 0);
  if (e.type === 'rect' || e.type === 'circle') return e.draw ?? 0.6;
  if (e.type === 'line' || e.type === 'arrow') return e.draw ?? 0.7;
  if (e.type === 'text' || e.type === 'badge') return 0.3;
  if (e.type === 'chip') return 0.3;
  if (e.type === 'label' || e.type === 'clear-chip') return 0.25;
  return 0;
}

export function* overlayScene(view: View2D, sceneId: string) {
  const segments = (timing as any).segments.filter((s: any) => s.scene === sceneId);
  const elements: Record<string, El[]> = (spec as any).segments;
  const chip = createRef<Rect>(); const chipTerm = createRef<Txt>(); const chipSub = createRef<Txt>();
  const label = createRef<Txt>(); const labelBg = createRef<Rect>();
  const transient = createRef<Layout>();
  view.add(
    <>
      <Layout ref={transient} />
      <Rect ref={chip} x={X(96)} y={Y(64)} offset={[-1, -1]} fill={DARK.panel} opacity={0} radius={8} padding={[10, 18, 10, 14]} layout direction={'row'} alignItems={'center'} gap={14}>
        <Rect width={6} height={44} fill={DARK.title} radius={3} />
        <Layout direction={'column'} gap={2}>
          <Txt ref={chipTerm} fontFamily={FONT} fontSize={30} fontWeight={700} fill={DARK.ink} text={''} />
          <Txt ref={chipSub} fontFamily={FONT} fontSize={22} fill={DARK.muted} text={''} />
        </Layout>
      </Rect>
      <Rect ref={labelBg} x={X(1824)} y={Y(64)} offset={[1, -1]} fill={'rgba(0,0,0,0.55)'} opacity={0} radius={6} padding={[8, 14, 8, 14]} layout>
        <Txt ref={label} fontFamily={FONT} fontSize={26} fill={DARK.ink} text={''} />
      </Rect>
    </>,
  );

  for (const seg of segments) {
    const seconds = seg.frames / 60;
    const els: El[] = elements[seg.id] || [];
    const budget = els.reduce((t, e) => t + animSeconds(e), 0);
    // A new segment with its own dim/card/text clears what a previous persisted segment left behind.
    if (transient().children().length && els.some(e => ['dim', 'card', 'text', 'rect', 'circle', 'line', 'arrow'].includes(e.type))) {
      yield* transient().opacity(0, 0.25); transient().removeChildren(); transient().opacity(1);
    }
    for (const el of els) {
      if (el.type === 'chip') { chipTerm().text(el.term); chipSub().text(el.sub || ''); yield* chip().opacity(1, 0.3); }
      else if (el.type === 'label') { label().text(el.text); yield* labelBg().opacity(1, 0.25); }
      else if (el.type === 'clear-chip') { yield* chip().opacity(0, 0.25); }
      else if (el.type === 'dim') { const r = createRef<Rect>(); transient().add(<Rect ref={r} width={W} height={H} fill={'#000000'} opacity={0} />); yield* r().opacity(el.alpha ?? 0.62, 0.35); }
      else if (el.type === 'card') {
        const r = createRef<Rect>(); transient().add(card(r, el));
        yield* all(r().opacity(1, 0.35), r().scale(1, 0.35, easeOutCubic));
        if (el.kind === 'dots') yield* fillDots(r, el);
        if (LIST_KINDS.includes(el.kind)) yield* revealRows(r, el.stepSeconds ?? 0.45);
      }
      else if (el.type === 'rect' && el.w > 0) {
        const r = createRef<Rect>(); transient().add(<Rect ref={r} x={X(el.x + el.w / 2)} y={Y(el.y + el.h / 2)} width={el.w} height={el.h} stroke={color(el.color)} lineWidth={el.lineWidth ?? 10} radius={el.radius ?? 10} end={0} />);
        if (el.label) transient().add(tag(el.x, el.y - 14, el.label, color(el.color)));
        yield* r().end(1, el.draw ?? 0.6, easeOutCubic);
      }
      else if (el.type === 'circle') {
        const r = createRef<Circle>(); transient().add(<Circle ref={r} x={X(el.x)} y={Y(el.y)} size={el.r * 2} stroke={color(el.color)} lineWidth={el.lineWidth ?? 10} end={0} />);
        if (el.label) transient().add(tag(el.x + el.r + 12, el.y - 22, el.label, color(el.color)));
        yield* r().end(1, el.draw ?? 0.6, easeOutCubic);
      }
      else if (el.type === 'line' || el.type === 'arrow') {
        const r = createRef<Line>();
        transient().add(<Line ref={r} points={el.points.map((p: number[]) => [X(p[0]), Y(p[1])])} stroke={color(el.color)} lineWidth={el.lineWidth ?? 10} endArrow={el.type === 'arrow'} arrowSize={26} radius={12} end={0} lineCap={'round'} />);
        if (el.label) { const p = el.points[el.points.length - 1]; transient().add(tag(p[0] + 16, p[1] - 24, el.label, color(el.color))); }
        yield* r().end(1, el.draw ?? 0.7, easeOutCubic);
      }
      else if (el.type === 'text') {
        const r = createRef<Txt>();
        transient().add(<Txt ref={r} x={X(el.x)} y={Y(el.y)} offset={[-1, -1]} fontFamily={FONT} fontSize={el.size ?? 44} fontWeight={700} fill={color(el.color)} text={el.text} opacity={0} shadowColor={'rgba(0,0,0,0.9)'} shadowBlur={0} shadowOffset={[3, 3]} />);
        yield* r().opacity(1, 0.3);
      }
      else if (el.type === 'badge') {
        const r = createRef<Rect>();
        transient().add(<Rect ref={r} x={X(el.x ?? 1824)} y={Y(el.y ?? 130)} offset={[1, -1]} fill={DARK.orange} radius={6} padding={[6, 14, 6, 14]} layout opacity={0}><Txt fontFamily={FONT} fontSize={26} fontWeight={700} fill={'#000000'} text={el.text ?? '우리 전망'} /></Rect>);
        yield* r().opacity(1, 0.3);
      }
    }
    const remaining = Math.max(0.05, seconds - budget);
    const persist = els.some(e => e.persist);
    if (persist || transient().children().length === 0) { yield* waitFor(remaining); }
    else {
      yield* waitFor(Math.max(0.05, remaining - 0.3));
      yield* transient().opacity(0, 0.3); transient().removeChildren(); transient().opacity(1);
    }
  }
}

function tag(x: number, y: number, text: string, fill: string) {
  return <Rect x={X(x)} y={Y(y)} offset={[-1, 1]} fill={'rgba(0,0,0,0.72)'} radius={6} padding={[4, 12, 4, 12]} layout><Txt fontFamily={FONT} fontSize={36} fontWeight={700} fill={fill} text={text} /></Rect>;
}

function row(children: any, extra: Record<string, any> = {}) {
  return <Layout direction={'row'} gap={16} alignItems={'center'} opacity={0} {...extra}>{children}</Layout>;
}

function card(ref: Reference<Rect>, el: El) {
  const kind = el.kind || 'text'; const accent = color(el.accent || (kind === 'number' ? 'teal' : 'title'));
  const width = el.width ?? 1570; const inner = width - 96; const lines: string[] = el.lines || [];
  let body: any = null;
  if (kind === 'number') body = <Txt fontFamily={FONT} fontSize={el.bigSize ?? 150} fontWeight={700} fill={accent} text={el.big} />;
  if (kind === 'quote') body = <Layout direction={'row'} gap={24}><Rect width={8} fill={accent} radius={4} /><Layout direction={'column'} gap={10}>{lines.map(l => <Txt fontFamily={FONT} fontSize={34} fill={DARK.ink} text={l} textWrap width={inner - 40} />)}</Layout></Layout>;
  if (kind === 'text') body = <Layout direction={'column'} gap={10}>{lines.map(l => <Txt fontFamily={FONT} fontSize={36} fill={DARK.ink} text={l} textWrap width={inner} />)}</Layout>;
  if (kind === 'bars') body = <Layout direction={'column'} gap={12}>{lines.map(l => { const [name, v, max, c] = l.split('|'); const w = Math.max(8, Math.round(880 * Number(v.replace(/[^0-9.]/g, '')) / Number(max))); return row([<Txt fontFamily={FONT} fontSize={30} fill={DARK.ink} text={name} width={420} />, <Rect height={34} width={w} fill={color(c || 'teal')} radius={6} />, <Txt fontFamily={FONT} fontSize={30} fontWeight={700} fill={color(c || 'teal')} text={v} />]); })}</Layout>;
  if (kind === 'dots') body = <Layout direction={'row'} wrap={'wrap'} width={inner} gap={10}>{Array.from({length: 100}, (_, i) => <Circle size={28} fill={i < (el.filled ?? 0) ? accent : DARK.line} opacity={i < (el.filled ?? 0) ? 0 : 0.45} />)}</Layout>;
  if (kind === 'timeline') body = <Layout direction={'row'} justifyContent={'space-between'} width={inner}>{lines.map(l => { const [when, what] = l.split('|'); return <Layout direction={'column'} alignItems={'center'} gap={8} opacity={0} width={Math.floor(inner / lines.length) - 12}><Circle size={22} fill={accent} /><Txt fontFamily={FONT} fontSize={30} fontWeight={700} fill={accent} text={when} /><Txt fontFamily={FONT} fontSize={28} fill={DARK.ink} text={what} textAlign={'center'} textWrap width={Math.floor(inner / lines.length) - 24} /></Layout>; })}</Layout>;
  if (kind === 'flow') body = <Layout direction={'row'} gap={18} alignItems={'center'} wrap={'wrap'} width={inner}>{lines.map((l, i) => { const [what, sub, c] = l.split('|'); return row([i > 0 ? <Txt fontFamily={FONT} fontSize={40} fill={DARK.muted} text={'→'} /> : null, <Rect fill={DARK.surfaceFront} stroke={color(c || 'teal')} lineWidth={3} radius={10} padding={[10, 18, 10, 18]} layout direction={'column'} gap={4}><Txt fontFamily={FONT} fontSize={30} fontWeight={700} fill={DARK.ink} text={what} />{sub ? <Txt fontFamily={FONT} fontSize={24} fill={DARK.muted} text={sub} /> : null}</Rect>]); })}</Layout>;
  if (kind === 'status') body = <Layout direction={'column'} gap={12}>{lines.map(l => { const [what, state] = l.split('|'); const ok = state === 'ok'; return row([<Txt fontFamily={FONT} fontSize={36} fontWeight={700} fill={ok ? DARK.green : DARK.red} text={ok ? '✓' : '✗'} />, <Txt fontFamily={FONT} fontSize={32} fill={DARK.ink} text={what} textWrap width={inner - 60} />]); })}</Layout>;
  if (kind === 'grid') body = <Layout direction={'row'} wrap={'wrap'} gap={18} width={inner}>{lines.map(l => { const [head, text, c] = l.split('|'); return <Rect width={(inner - 18) / 2} fill={DARK.surfaceFront} stroke={color(c || 'teal')} lineWidth={3} radius={12} padding={[16, 20, 16, 20]} layout direction={'column'} gap={6} opacity={0}><Txt fontFamily={FONT} fontSize={32} fontWeight={700} fill={color(c || 'teal')} text={head} /><Txt fontFamily={FONT} fontSize={28} fill={DARK.ink} text={text} textWrap width={(inner - 18) / 2 - 40} /></Rect>; })}</Layout>;
  return (
    <Rect ref={ref} x={X(960)} y={Y(el.y ?? 500)} width={width} fill={DARK.panel} radius={16} stroke={DARK.line} lineWidth={2} opacity={0} scale={0.96} padding={[36, 48, 36, 48]} layout direction={'column'} gap={18} clip>
      {el.badge ? <Rect fill={DARK.orange} radius={6} padding={[4, 12, 4, 12]} layout><Txt fontFamily={FONT} fontSize={24} fontWeight={700} fill={'#000000'} text={el.badge} /></Rect> : null}
      {el.title ? <Txt fontFamily={FONT} fontSize={44} fontWeight={700} fill={accent} text={el.title} textWrap width={inner} /> : null}
      {body}
      {el.note ? <Txt fontFamily={FONT} fontSize={26} fill={DARK.muted} text={el.note} textWrap width={inner} /> : null}
      {el.source ? <Txt fontFamily={FONT} fontSize={24} fill={DARK.muted} text={'출처 · ' + el.source} textWrap width={inner} /> : null}
    </Rect>
  );
}

function* fillDots(ref: Reference<Rect>, el: El): ThreadGenerator {
  const dots = (ref().findAll((n: any) => n instanceof Circle) as Circle[]).slice(0, el.filled ?? 0);
  for (let i = 0; i < dots.length; i += 4) { yield* all(...dots.slice(i, i + 4).map(d => d.opacity(1, 0.08))); }
}
function* revealRows(ref: Reference<Rect>, step: number): ThreadGenerator {
  const items = ref().findAll((n: any) => n instanceof Layout && n.opacity() === 0 && n !== ref()) as Layout[];
  for (const it of items) { yield* it.opacity(1, step); }
}
