// The full narrated video: the Qwen3-TTS narration track plus one scene per
// narration segment, each running for exactly its slot in the audio (see
// src/narration.ts, generated from the narration's measured line timings).
//
// Scene order and durations here must stay in the same order as
// SEGMENT_ORDER -- Motion Canvas plays scenes back to back, so each scene's
// length is what places the next one against the audio.

import {makeProject} from '@motion-canvas/core';

// Imported from within src/ (a synced copy -- see
// qwen3-tts/build_motion_canvas_timing.py) rather than from
// ../../shared/output/ directly: Vite serves out-of-root files via a
// /@fs/<absolute-path> URL, and @motion-canvas/ffmpeg's exporter naively
// strips only the leading "/" from that URL before handing it to ffmpeg as a
// file path, leaving a bogus "@fs/D:/..." argument that ffmpeg can't open
// ("Invalid argument"). That crash is fatal to the whole Vite dev process
// (not just the render), which is why rendering silently died even before
// showing a progress bar. Importing from inside src/ produces a plain
// "/src/..." URL with no /@fs/ prefix, which resolves correctly.
import narrationAudio from './assets/narration/jump-physics-qwen3-balanced.wav';

import axes from './scenes/narrated/axes?scene';
import basic from './scenes/narrated/basic?scene';
import celeste from './scenes/narrated/celeste?scene';
import ghosts from './scenes/narrated/ghosts?scene';
import intro from './scenes/narrated/intro?scene';
import jumpKing from './scenes/narrated/jumpKing?scene';
import mario from './scenes/narrated/mario?scene';
import megaman from './scenes/narrated/megaman?scene';
import metroid from './scenes/narrated/metroid?scene';
import outro from './scenes/narrated/outro?scene';
import sf2 from './scenes/narrated/sf2?scene';
import smashSquat from './scenes/narrated/smashSquat?scene';
import smashUltimate from './scenes/narrated/smashUltimate?scene';

export default makeProject({
  name: 'jump-physics-narrated',
  audio: narrationAudio,
  scenes: [
    intro,
    basic,
    axes,
    mario,
    metroid,
    ghosts,
    sf2,
    smashSquat,
    smashUltimate,
    jumpKing,
    celeste,
    megaman,
    outro,
  ],
});
