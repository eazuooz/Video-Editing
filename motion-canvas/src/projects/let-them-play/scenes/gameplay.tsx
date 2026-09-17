import {Node,Rect,Video,View2D} from '@motion-canvas/2d';
import {PAPER as P} from '../../../styles/research-paper';
import footage from '../../../../../projects/let-them-play/sources/archive64-cuts.json';

const clips=import.meta.glob('../assets/broll-archive64/scene*.mp4',{eager:true,query:'?url',import:'default'}) as Record<string,string>;
// Original files retain sound; the final project mix is the only playback route.
class MixedAudioVideo extends Video {
 protected override video():HTMLVideoElement {
  const video=super.video();video.muted=true;return video;
 }
}
export function showGameplay(view:View2D,index:number){
 const item=footage.clips[index],src=clips['../assets/broll-archive64/scene'+item.scene+'.mp4'];
 if(!src)throw Error('Missing approved gameplay cut: '+item.scene);
 const layer=new Node({});view.add(layer);
 layer.add(<Rect width={1920} height={1080} fill={P.background}/>);
 const video=new MixedAudioVideo({src,width:1920,height:1080});
 layer.add(video);
 return {video,close(){video.pause();layer.remove()}};
}
