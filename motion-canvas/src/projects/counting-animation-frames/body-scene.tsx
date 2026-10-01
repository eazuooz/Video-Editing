import {Video, View2D} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import plan from './production-plan.json';
import g01 from './assets/body-01.mp4';
import g02 from './assets/body-02.mp4';
import g03 from './assets/body-03.mp4';
import g04 from './assets/body-04.mp4';
import g05 from './assets/body-05.mp4';
import g06 from './assets/body-06.mp4';
class MutedVideo extends Video {
  protected override video(){const element=super.video();element.muted=true;return element;}
}
export function* bodyScene(view: View2D, index: number) {
  const scene=plan.scenes[index],video=createRef<Video>();
  view.fill(P.background);
  view.add(<MutedVideo ref={video} src={[g01,g02,g03,g04,g05,g06][index]} width={1920} height={1080}/>);
  // Each independent chapter includes its interleaved actual examples and
  // 2.5D explanations at the same measured narration boundaries as final-v2.
  yield video();video().play();yield* waitFor(scene.seconds);video().pause();
}
