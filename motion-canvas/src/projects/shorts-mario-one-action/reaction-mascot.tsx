import {Img, Node, Rect} from '@motion-canvas/2d';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';

type ReactionKind = 'puzzled' | 'relief' | 'realize' | 'understood';
type ReactionCue = {start: number; end: number; kind: ReactionKind};

import timing from '../../../../projects/shorts-mario-one-action/production/visual-timing.json';
export const reactionCues = timing.reactions as readonly ReactionCue[];

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const easeOut = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
const once = (elapsed: number, start: number, seconds: number) =>
  Math.sin(Math.PI * clamp01((elapsed - start) / seconds));

export function reactionPresence(clock: () => number): number {
  const c = reactionCues.find(c => clock() >= c.start && clock() < c.end);
  if (!c) return 0;
  return easeOut((clock() - c.start) / .12) * easeOut((c.end - clock()) / .15);
}

export function createReactionMascot(clock: () => number): Rect {
  const cue = () => reactionCues.find(c => clock() >= c.start && clock() < c.end);
  const elapsed = () => Math.max(0, clock() - (cue()?.start ?? clock()));
  const kind = () => cue()?.kind ?? 'puzzled';
  const alpha = () => reactionPresence(clock);
  const lift = () => {
    if (kind() === 'relief') return -8 * once(elapsed(), .12, .50);
    if (kind() === 'realize') return -4 * once(elapsed(), .12, .36);
    if (kind() === 'understood') return -3 * once(elapsed(), .12, .36);
    return 0;
  };
  const rotation = () => {
    const e = elapsed();
    if (kind() === 'puzzled') {
      return -6 * easeOut(e / .24) + 11 * easeOut((e - .24) / .24)
        - 5 * easeOut((e - .48) / .24);
    }
    return (kind() === 'realize' ? 4.5 : 3) * once(e, .12, .36);
  };
  const size = () => 1 + (kind() === 'realize' ? .05 : .035)
    * once(elapsed(), .12, kind() === 'relief' ? .50 : .36);

  // Reference-sized lower-right bust:780px square, center(900,1070).
  // The right silhouette exits the canvas; fixed captions composite in front.
  // Native clip x540..1100/y610..1470; the Unity group yields the left gutter.
  const bounds = new Rect({width: 560, height: 860, position: [280, 80],
    clip: true, opacity: alpha});
  const actor = new Node({
    x: () => 80 + 40 * (1 - easeOut(elapsed() / .12)),
    y: () => 30 + lift(), rotation, scale: size,
  });
  actor.add(<Img
    src={() => kind() === 'puzzled' ? puzzled : kind() === 'realize' ? realize : relief}
    width={780} height={780} smoothing={true}
  />);
  bounds.add(actor);
  return bounds;
}
