// Guards the audio sync of the narrated project.
//
// Each narrated scene pins itself to its slot with padTo(), which can only
// stretch a scene -- never trim it. So the one way the video can drift out of
// sync with the narration is a scene whose animation is longer than the segment
// it was given: it overruns, and every later scene inherits the delay. This
// checks that no segment is shorter than the animation assigned to it, and that
// the segments still tile the narration exactly.
//
// Run with: npm run check:narration

import {type BrollWindow, absoluteEnd, absoluteStart, brollFor, timecode} from '../src/broll.ts';
import {
  NARRATION_FPS,
  NARRATION_TOTAL_FRAMES,
  NARRATION_TOTAL_SECONDS,
  SEGMENTS,
  SEGMENT_ORDER,
} from '../src/narration.ts';
import {
  basicConcept,
  celestePair,
  ghostsNGoblins,
  jumpKing,
  mario,
  megamanXDashJump,
  metroid,
  sf2ScrewPiledriver,
  smashJumpSquat,
  smashUltimateSpecial,
} from '../src/scenes/jumpPhysics/profiles.ts';
import {minimumSceneSeconds} from '../src/scenes/jumpPhysics/timing.ts';

// Minimum seconds each narrated scene needs. The profile-driven ones are
// derived from the same helper the scenes use; intro and outro are hand-built,
// so their fixed beats are summed here.
const INTRO_FIXED = 0.8 + 0.5 + 4.2 + 0.6 + 0.5 + 1 + 0.5; // title card, stage fade-in, min jump, fade-out
const OUTRO_FIXED = 0.6 + 3.2 + 2.0 + 0.6 + 0.8; // heading, curve draw, hold, closing, fade-out

const [celesteFull, celesteCut] = celestePair();

// Mirrors the split math in scenes/narrated/celeste.tsx exactly -- if that
// scene's formula changes, this must change with it (and vice versa).
function brollEndOf(window: BrollWindow | undefined): number {
  return window ? window.offset + window.duration : 0;
}
const celesteRawFirstShare =
  SEGMENTS.celeste.duration * (celesteFull.total / (celesteFull.total + celesteCut.total));
const celesteFirstShare = Math.max(
  celesteRawFirstShare,
  brollEndOf(brollFor('celeste')) + 1,
  minimumSceneSeconds(celesteFull),
);

const REQUIRED: Record<string, number> = {
  intro: INTRO_FIXED,
  basic: minimumSceneSeconds(basicConcept()),
  axes: minimumSceneSeconds(megamanXDashJump()[0], false),
  mario: minimumSceneSeconds(mario()),
  metroid: minimumSceneSeconds(metroid()),
  ghosts: minimumSceneSeconds(ghostsNGoblins()),
  sf2: minimumSceneSeconds(sf2ScrewPiledriver()[0], false),
  smashSquat: minimumSceneSeconds(smashJumpSquat()),
  smashUltimate: minimumSceneSeconds(smashUltimateSpecial()),
  jumpKing: minimumSceneSeconds(jumpKing().profile),
  // Two runProfileLeftAnchor calls back to back (see scenes/narrated/celeste.tsx)
  // -- each carries its own header/axes/fade-out overhead, so the segment needs
  // both minimums, not just one.
  celeste: minimumSceneSeconds(celesteFull) + minimumSceneSeconds(celesteCut),
  megaman: minimumSceneSeconds(megamanXDashJump()[0], false),
  outro: OUTRO_FIXED,
};

let failed = false;

console.log(`narration: ${NARRATION_TOTAL_SECONDS.toFixed(3)}s (${NARRATION_TOTAL_FRAMES} frames @ ${NARRATION_FPS}fps)\n`);

let cursor = 0;
let totalFrames = 0;

for (const key of SEGMENT_ORDER) {
  const segment = SEGMENTS[key];
  const required = REQUIRED[key];

  if (Math.abs(segment.start - cursor) > 1e-9) {
    console.error(
      `  ${key}: starts at ${segment.start.toFixed(3)}s but previous segment ended at ${cursor.toFixed(3)}s`,
    );
    failed = true;
  }
  cursor = segment.end;
  totalFrames += segment.frames;

  const headroom = segment.duration - required;
  const ok = headroom >= 0;
  if (!ok) failed = true;
  console.log(
    `  ${ok ? 'ok  ' : 'FAIL'} ${key.padEnd(14)} slot ${segment.duration.toFixed(3)}s  ` +
      `needs >= ${required.toFixed(3)}s  headroom ${headroom.toFixed(3)}s`,
  );

  // A B-roll window runs in parallel with the scene's animation, so if it ended
  // after the animation did it would stretch the scene past its slot -- padTo
  // cannot claw that back, and every later scene would drift. For celeste the
  // window is attached to the *first* of two chained demos (see
  // scenes/narrated/celeste.tsx), so it must fit inside that demo's share, not
  // just the segment as a whole -- checked against the same clamped split math
  // the scene itself uses, so this can't silently drift out of sync with it.
  const broll = brollFor(key);
  if (broll) {
    const endsAt = broll.offset + broll.duration;
    const budget = key === 'celeste' ? celesteFirstShare : segment.duration;
    const brollOk = endsAt <= budget && broll.offset >= 0;
    if (!brollOk) failed = true;
    console.log(
      `       ${brollOk ? '·' : 'FAIL'} b-roll "${broll.clip}" ` +
        `${timecode(absoluteStart(broll))} – ${timecode(absoluteEnd(broll))} ` +
        `(${broll.duration.toFixed(1)}s, ends ${endsAt.toFixed(1)}s into a ${budget.toFixed(1)}s budget)`,
    );
  }
}

const celesteSecondShare = SEGMENTS.celeste.duration - celesteFirstShare;
const celesteSecondOk = celesteSecondShare >= minimumSceneSeconds(celesteCut);
if (!celesteSecondOk) failed = true;
console.log(
  `\n  ${celesteSecondOk ? 'ok  ' : 'FAIL'} celeste split   first ${celesteFirstShare.toFixed(3)}s / ` +
    `second ${celesteSecondShare.toFixed(3)}s  (second needs >= ${minimumSceneSeconds(celesteCut).toFixed(3)}s)`,
);

console.log();

if (totalFrames !== NARRATION_TOTAL_FRAMES) {
  console.error(
    `  scene frames sum to ${totalFrames}, expected ${NARRATION_TOTAL_FRAMES}`,
  );
  failed = true;
}

if (Math.abs(cursor - NARRATION_TOTAL_SECONDS) > 1e-9) {
  console.error(
    `  last segment ends at ${cursor.toFixed(3)}s, expected ${NARRATION_TOTAL_SECONDS.toFixed(3)}s`,
  );
  failed = true;
}

if (failed) {
  console.error('narration sync check FAILED');
  process.exit(1);
}

console.log(`narration sync check passed: ${totalFrames} frames tile the audio exactly.`);
