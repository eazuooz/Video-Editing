import {Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const title = createRef<Txt>();

  view.fill('#0b1020');
  view.add(
    <Rect width={1920} height={1080} fill={'#0b1020'}>
      <Txt
        ref={title}
        text={'{{TITLE_KO}}'}
        fontFamily={'Pretendard, Noto Sans KR, sans-serif'}
        fontWeight={800}
        fontSize={88}
        fill={'#ffffff'}
        opacity={0}
      />
    </Rect>,
  );

  yield* title().opacity(1, 0.6);
  yield* waitFor(2.4);
  yield* title().opacity(0, 0.4);
});
