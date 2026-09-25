// Channel-wide membership thank-you outro. See docs/MEMBERSHIP_OUTRO.md.
// Appended as the last scene of every new video (default 10 seconds, BGM only).
import {Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, linear, sequence, waitFor} from '@motion-canvas/core';
import {PAPER} from '../../styles/research-paper';
import roster from './members.json';

export const MEMBERSHIP_OUTRO_SECONDS = 10;

const COLUMNS = 4;
const CARD_W = 390;
const CARD_H = 76;
const GAP_X = 22;
const GAP_Y = 20;
const AREA_TOP = -235;
const AREA_BOTTOM = 470;
const VISIBLE_ROWS = 6;

export function* membershipOutro(view: View2D, seconds = MEMBERSHIP_OUTRO_SECONDS) {
  view.fill(PAPER.background);
  const header = createRef<Node>();
  const grid = createRef<Node>();
  const cards: Rect[] = [];
  const left = -PAPER.width / 2 + PAPER.margin;
  const members = roster.members.map(member => member.handle);
  const rows = Math.ceil(members.length / COLUMNS);
  const gridWidth = COLUMNS * CARD_W + (COLUMNS - 1) * GAP_X;
  const gridHeight = rows * CARD_H + (rows - 1) * GAP_Y;
  // Short lists sit centred under the header; long lists start at the top and crawl.
  const gridTop = rows > VISIBLE_ROWS ? AREA_TOP : Math.max(AREA_TOP, (AREA_TOP + AREA_BOTTOM) / 2 - gridHeight / 2);

  view.add(
    <Node ref={header} opacity={0}>
      <Txt text="MEMBERSHIP" x={left} y={-477} offset={[-1, 0]} fontFamily={PAPER.font}
        fontSize={24} fontWeight={600} letterSpacing={3} fill={PAPER.blue} />
      <Txt text={roster.title} x={left} y={-405} offset={[-1, 0]} fontFamily={PAPER.font}
        fontSize={56} fontWeight={700} fill={PAPER.ink} />
      <Txt text={roster.subtitle} x={left} y={-325} offset={[-1, 0]} fontFamily={PAPER.font}
        fontSize={30} fill={PAPER.muted} />
      <Rect x={0} y={-278} width={PAPER.width - PAPER.margin * 2} height={2} fill={PAPER.line} />
    </Node>,
  );
  view.add(<Node ref={grid} />);
  members.forEach((handle, index) => {
    const column = index % COLUMNS;
    const row = Math.floor(index / COLUMNS);
    const card = (
      <Rect
        x={-gridWidth / 2 + CARD_W / 2 + column * (CARD_W + GAP_X)}
        y={gridTop + CARD_H / 2 + row * (CARD_H + GAP_Y)}
        width={CARD_W} height={CARD_H} fill={PAPER.panel} stroke={PAPER.line} lineWidth={2}
        opacity={0}
      >
        <Rect x={-CARD_W / 2 + 4} width={8} height={CARD_H - 2} fill={PAPER.blue} />
        <Txt text={handle} x={-CARD_W / 2 + 30} offset={[-1, 0]} fontFamily={PAPER.font}
          fontSize={30} fontWeight={500} fill={PAPER.ink} />
      </Rect>
    ) as Rect;
    cards.push(card);
    grid().add(card);
  });

  const step = Math.min(2.4, 0.4 + members.length * 0.08) / Math.max(members.length, 1);
  const revealSeconds = members.length ? (members.length - 1) * step + 0.3 : 0;
  yield* header().opacity(1, 0.4);
  yield* sequence(step, ...cards.map(card => card.opacity(1, 0.3)));
  // Header 0.4s + card reveal + final 0.5s fade; the rest is hold/crawl, so the total equals `seconds`.
  const remaining = seconds - 0.4 - revealSeconds - 0.5;
  if (rows > VISIBLE_ROWS) {
    // Longer lists crawl upward so every handle stays readable inside the frame.
    const travel = (rows - VISIBLE_ROWS) * (CARD_H + GAP_Y);
    yield* grid().y(-travel, Math.max(remaining, 1), linear);
  } else {
    yield* waitFor(Math.max(remaining, 0));
  }
  yield* all(header().opacity(0, 0.5, easeInOutCubic), grid().opacity(0, 0.5, easeInOutCubic));
}
