import {makeScene2D,Video} from '@motion-canvas/2d';
import {createRef,waitFor} from '@motion-canvas/core';
import {windowScene} from '../scenes/window-scene';
import timing from './timing.json';
import clip from './assets/forza.mp4';
class MutedVideo extends Video {
  protected override video():HTMLVideoElement {const element=super.video();element.muted=true;return element;}
}
export default makeScene2D(function*(view){
  const video=createRef<Video>();
  view.add(<MutedVideo ref={video} src={clip} width={1920} height={1080}/>);
  yield video();
  video().play();yield* waitFor(timing.gameplaySeconds);video().pause();video().remove();
  yield* windowScene(view,0,timing.seconds-timing.gameplaySeconds,false);
});
