import {makeProject} from '@motion-canvas/core';

import main from './scenes/main?scene';

export default makeProject({
  name: '{{SLUG}}',
  scenes: [main],
});
