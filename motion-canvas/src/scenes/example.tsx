import {Circle, makeScene2D} from '@motion-canvas/2d';
import {createRef} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const circle = createRef<Circle>();

  view.add(
    <Circle ref={circle} width={140} height={140} fill={'#e13238'} />,
  );

  yield* circle().scale(2, 1).to(1, 1);
});
