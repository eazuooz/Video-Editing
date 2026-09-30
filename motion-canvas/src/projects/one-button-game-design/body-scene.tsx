import {Video, View2D} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import plan from './production-plan.json';
import g01 from './assets/game-01.mp4';
import g02 from './assets/game-02.mp4';
import g03 from './assets/game-03.mp4';
import g04 from './assets/game-04.mp4';
import g05 from './assets/game-05.mp4';
import g06 from './assets/game-06.mp4';
import g07 from './assets/game-07.mp4';
import {diagramScene} from './diagram';
class MutedVideo extends Video {
  protected override video(){const element=super.video();element.muted=true;return element;}
}
export function* bodyScene(view: View2D, index: number) {
  const scene=plan.scenes[index],video=createRef<Video>();
  view.fill(P.background);
  view.add(<MutedVideo ref={video} src={[g01,g02,g03,g04,g05,g06,g07][index]} width={1920} height={1080}/>);
  yield video();video().play();yield* waitFor(scene.gameSeconds);video().pause();
  view.removeChildren();
  yield* diagramScene(view,index,scene.diagramSeconds);
}
