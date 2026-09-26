import {Video,View2D} from '@motion-canvas/2d';
import {createRef,waitFor} from '@motion-canvas/core';
import {diagramScene} from './diagram';
import plan from './plan.json';
class MutedVideo extends Video {
  protected override video(){const element=super.video();element.muted=true;return element;}
}
export function* fullScene(view:View2D,index:number,clip:string){
  const s=plan.scenes[index],video=createRef<Video>();
  view.add(<MutedVideo ref={video} src={clip} width={1920} height={1080}/>);
  yield video();video().play();yield* waitFor(s.gameSeconds);video().pause();video().remove();
  yield* diagramScene(view,index,s.diagramSeconds);
}
