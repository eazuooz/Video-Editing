import {makeScene2D, Video} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import clip from '../assets/original-05.mp4';
class MutedVideo extends Video {protected override video(){const element=super.video();element.muted=true;return element;}}
export default makeScene2D(function*(view){const video=createRef<Video>();view.add(<MutedVideo ref={video} src={clip} width={1920} height={1080}/>);yield video();video().play();yield* waitFor(34.4);video().pause();});
