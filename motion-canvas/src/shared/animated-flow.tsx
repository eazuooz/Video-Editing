import {Circle, Line, Node, Txt} from '@motion-canvas/2d';
import {all, createSignal, easeInOutCubic, Vector2} from '@motion-canvas/core';
import {DARK} from '../styles/research-dark';

export type Point = [number, number];

/** A relationship, not a measured velocity vector. Caller supplies its meaning. */
export function flowArrow(parent: Node, points: () => Point[], color: string = DARK.yellow) {
  const progress = createSignal(0);
  const root = new Node({});
  const guide = new Line({points, radius: 64, stroke: '#394247', lineWidth: 4, lineDash: [9, 11]});
  const active = new Line({points, radius: 64, stroke: color, lineWidth: 7, end: progress, endArrow: true, arrowSize: 18});
  const token = new Circle({size: 17, fill: color, opacity: 0, position: () => active.getPointAtPercentage(progress()).position});
  root.add([guide, active, token]); parent.add(root);
  return {root, guide, active, token, progress,
    *trace(seconds = .7) {
      token.opacity(1);
      yield* progress(1, seconds, easeInOutCubic);
      yield* token.opacity(0, .15);
    },
    *verify(seconds = .25) {
      yield* all(active.stroke(DARK.teal, seconds), guide.opacity(.3, seconds));
    },
  };
}

export function flowNode(parent: Node, title: string, icon: string, position: Point, status = '대기') {
  const root = new Node({position});
  const ring = new Circle({size: 144, fill: '#080c0e', stroke: '#566066', lineWidth: 4});
  const glyph = new Txt({text: icon, fontFamily: DARK.mono, fontSize: 45, fill: DARK.ink});
  const name = new Txt({text: title, y: 108, fill: DARK.ink, fontFamily: DARK.font, fontWeight: 600, fontSize: 33});
  const state = new Txt({text: status, y: 151, fill: DARK.muted, fontFamily: DARK.font, fontSize: 25});
  root.add([ring, glyph, name, state]); parent.add(root);
  return {root, ring, glyph, name, state,
    anchor(): Vector2 {return root.position();},
    *focus(label: string, color: string = DARK.yellow) {
      state.text(label); state.fill(color);
      yield* all(ring.stroke(color, .2), ring.lineWidth(7, .2));
      yield* ring.lineWidth(4, .15);
    },
  };
}
