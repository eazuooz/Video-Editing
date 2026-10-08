import {Video,View2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import plan from '../../../../../projects/game-math-planes-barycentric/production/timeline.json';
class SilentVideo extends Video {protected override video(){const v=super.video();v.muted=true;return v;}}
export function* playScene(view:View2D,src:string,id:string) {
  view.fill('#ffffff');const video=new SilentVideo({src,width:1920,height:1080});
  view.add(video);yield video;video.play();
  const seconds=id==='intro'?2:id==='outro'?10:plan.scenes.find(s=>s.id===id)!.seconds;
  yield* waitFor(seconds);video.pause();video.remove();
}
