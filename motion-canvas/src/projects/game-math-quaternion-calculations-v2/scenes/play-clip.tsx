import {Video,View2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import plan from '../../../../../projects/game-math-quaternion-calculations-v2/production/timeline.json';
import captions from '../caption-layout.json';
class SilentVideo extends Video {protected override video(){const v=super.video();v.muted=true;return v;}}
export function* playScene(view:View2D,src:string,id:string) {
  view.fill('#ffffff');const video=new SilentVideo({src,width:1920,height:1080});
  view.add(video);yield video;video.play();
  const slot=plan.scenes.find(s=>s.id===id);
  const seconds=id==='intro'?2:id==='outro'?10:slot!.seconds;
  let elapsed=0;
  for(const cue of captions.filter(c=>c.scene===id)){
    const start=cue.start-slot!.start,end=cue.end-slot!.start;
    yield* waitFor(Math.max(0,start-elapsed));
    const [x,y,w,h]=cue.box;const layer=new Node({});
    layer.add(new Rect({x:x+w/2-960+14,y:y+h/2-540+14,width:w,height:h,fill:'#073c32',radius:0}));
    layer.add(new Rect({x:x+w/2-960,y:y+h/2-540,width:w,height:h,fill:'#161b18',radius:0}));
    layer.add(new Rect({x:x+w/2-960,y:y+h/2-540,width:w-6,height:h-6,fill:'#ffffff',radius:0}));
    layer.add(new Txt({x:0,y:430,text:cue.text,fontFamily:'Malgun Gothic',fontSize:48,lineHeight:62,fill:'#090b08',textAlign:'center'}));
    view.add(layer);yield* waitFor(Math.max(0,end-start));layer.remove();elapsed=end;
  }
  yield* waitFor(Math.max(0,seconds-elapsed));video.pause();video.remove();
}
