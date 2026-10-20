import {makeScene2D} from '@motion-canvas/2d';
import {lesson} from './visuals';
export default makeScene2D(function*(view) {
  yield* lesson(view, {kind: 'permissions', title: '무료라는 말과 허락은 다릅니다', duration: 8, currentPicture: '해설용 도식'});
});
