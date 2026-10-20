// Transparent overlay layer for steam-next-fest-ai-flood (chips, labels, cards,
// drawn strokes). Rendered as a PNG sequence and composited over our own
// browser recordings by projects/steam-next-fest-ai-flood/production/render-edit.py.
import {makeProject} from '@motion-canvas/core';
import s01 from './scenes/s01?scene';
import s02 from './scenes/s02?scene';
import s03 from './scenes/s03?scene';
import s04 from './scenes/s04?scene';
import s05 from './scenes/s05?scene';
import s06 from './scenes/s06?scene';
import s07 from './scenes/s07?scene';

export default makeProject({
  name: 'steam-next-fest-ai-flood-overlay',
  scenes: [s01, s02, s03, s04, s05, s06, s07],
});
