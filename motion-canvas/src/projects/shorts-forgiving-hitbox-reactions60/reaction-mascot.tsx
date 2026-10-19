import {Img, Node, Rect} from '@motion-canvas/2d';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';

type ReactionKind = 'puzzled' | 'relief' | 'realize' | 'understood';
type ReactionCue = {start: number; end: number; kind: ReactionKind};

// All cues follow the existing locked narration. No new scene or audio clock.
export const reactionCues: readonly ReactionCue[] = [
  {start: 1.05, end: 2.55, kind: 'puzzled'},
  {start: 4.97, end: 6.70, kind: 'relief'},
  {start: 40.28, end: 41.92, kind: 'realize'},
  {start: 58.37, end: 59.65, kind: 'understood'},
];

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const easeOut = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
const once = (elapsed: number, start: number, seconds: number) =>
  Math.sin(Math.PI * clamp01((elapsed - start) / seconds));

export function createReactionMascot(clock: () => number): Rect {
  const cue = () => reactionCues.find(c => clock() >= c.start && clock() < c.end);
  const elapsed = () => Math.max(0, clock() - (cue()?.start ?? clock()));
  const kind = () => cue()?.kind ?? 'puzzled';
  const alpha = () => {
    const c = cue();
    if (!c) return 0;
    return easeOut(elapsed() / .12) * easeOut((c.end - clock()) / .15);
  };
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

  // Native dock: center(170,765), hard maximum bounds x70..270/y665..865.
  // It clears the HP/result, hero, Hurtbox label and the fixed caption box.
  const bounds = new Rect({width: 200, height: 200, position: [-370, -195],
    clip: true, opacity: alpha});
  const actor = new Node({
    x: () => -24 * (1 - easeOut(elapsed() / .12)),
    y: lift, rotation, scale: size,
  });
  actor.add(<Img
    src={() => kind() === 'puzzled' ? puzzled : kind() === 'realize' ? realize : relief}
    width={174} height={174} smoothing={true}
  />);
  bounds.add(actor);
  return bounds;
}
