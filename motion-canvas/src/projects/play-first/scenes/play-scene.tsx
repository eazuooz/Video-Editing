// Shared scene runner for play-first: 2.5D diorama beats keyed to narration lines, with one
// Super Mario Odyssey example window (project.json.editing.exampleSeconds) over the line that describes it.
// Timing comes from storyboard.generated.json (scripts/build-play-first-storyboard.cjs).
import {Node, Txt, Video, View2D} from '@motion-canvas/2d';
import {all, tween, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {CaptionBox} from '../../game-dev-career/preview/caption-box';
import board from '../storyboard.generated.json';
import {captionMode} from '../caption-mode';
import {PlayWorld} from './play-world';

// The final mix carries the source sound; the editor video element stays muted.
class MutedVideo extends Video {
  protected override video(): HTMLVideoElement {
    const element = super.video();
    element.muted = true;
    return element;
  }
}

/** One diorama beat: shown from narration line `line`, drawing PlayWorld(chapter, beat). */
export type Panel = {line: number; beat: number; heading: string};
export interface SceneSpec {
  index: number;
  chapter: string;
  title: string;
  clip: string;
  /** Describes the clip for reviewers; not drawn (examples play full-frame). */
  exampleLabel: string;
  panels: Panel[];
}

const FADE = 0.3;
// 2026-09-25 user: examples play full-frame, with no label or frame.
const VIDEO_W = 1920, VIDEO_H = 1080;

function txt(text: string, x: number, y: number, size: number, fill: string, weight: number): Txt {
  return (<Txt text={text} x={x} y={y} fontFamily={P.font} fontSize={size} fontWeight={weight} fill={fill} offset={[-1, 0]} />) as Txt;
}

function* captionTrack(caption: CaptionBox, cues: {start: number; end: number; text: string}[]) {
  let now = 0;
  for (const cue of cues) {
    if (cue.start > now) yield* waitFor(cue.start - now);
    caption.text(cue.text);
    yield* waitFor(Math.max(cue.end - Math.max(cue.start, now), 0));
    caption.text('');
    now = cue.end;
  }
}

export function* playScene(view: View2D, spec: SceneSpec) {
  const s = board.scenes[spec.index];
  view.fill(P.background);
  const graphics = new Node({});
  view.add(graphics);
  graphics.add(txt(spec.chapter, -864, -477, 25, P.blue, 600));
  graphics.add(txt(spec.title, -864, -405, 52, P.ink, 700));
  const layer = new Node({});
  graphics.add(layer);
  const example = new Node({opacity: 0});
  view.add(example);
  const caption = new CaptionBox({y: 430});
  if (captionMode.on) view.add(caption);

  // Beats whose line falls inside the example window wait until it ends; only the latest is kept.
  const exStart = s.exampleStart, exEnd = s.exampleEnd;
  const lastUsable = s.duration - 1.5;
  const events: {t: number; panel: Panel}[] = [];
  for (const panel of spec.panels) {
    let t = panel.line === 0 ? 0 : s.lineStarts[panel.line];
    if (t >= exStart && t < exEnd) t = exEnd;
    if (t > lastUsable) continue;
    const same = events.findIndex(event => Math.abs(event.t - t) < 0.01);
    if (same >= 0) events.splice(same, 1);
    events.push({t, panel});
  }
  events.sort((a, b) => a.t - b.t);

  function* body() {
    let now = 0;
    let current: Node | null = null;
    let world: PlayWorld | null = null;
    let exampleDone = false;
    // Waiting keeps the current diorama alive: its clock advances with scene time.
    const hold = function* (seconds: number) {
      if (seconds <= 0) return;
      if (world) {
        const w = world, from = w.clock();
        yield* tween(seconds, v => w.clock(from + v * seconds));
      } else {
        yield* waitFor(seconds);
      }
      now += seconds;
    };
    const show = function* (panel: Panel) {
      const next = new Node({opacity: 0});
      const nextWorld = new PlayWorld({});
      nextWorld.chapter(spec.index);
      nextWorld.beat(panel.beat);
      next.add(nextWorld);
      next.add(txt(panel.heading, -864, -325, 32, P.blue, 600));
      layer.add(next);
      const previous = current;
      current = next;
      world = nextWorld;
      yield* all(next.opacity(1, FADE), previous ? previous.opacity(0, FADE) : waitFor(0),
        tween(FADE, v => nextWorld.clock(v * FADE)));
      previous?.remove();
      now += FADE;
    };
    const runExample = function* () {
      const video = new MutedVideo({src: spec.clip, width: VIDEO_W, height: VIDEO_H});
      example.add(video);
      yield video;
      video.play();
      yield* all(example.opacity(1, FADE), graphics.opacity(0, FADE));
      yield* waitFor(exEnd - exStart - 2 * FADE);
      yield* all(example.opacity(0, FADE), graphics.opacity(1, FADE));
      video.pause();
      example.removeChildren();
      now = exEnd;
      exampleDone = true;
    };
    for (const event of events) {
      if (!exampleDone && event.t >= exEnd) {
        yield* hold(exStart - now);
        yield* runExample();
      }
      yield* hold(event.t - now);
      yield* show(event.panel);
    }
    if (!exampleDone) {
      yield* hold(exStart - now);
      yield* runExample();
    }
    yield* hold(s.duration - now);
  }

  if (captionMode.on) yield* all(body(), captionTrack(caption, s.captions));
  else yield* body();
}
