import {makeScene2D,Video} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
// Preview uses the unchanged approved2s branding; final assembly packet-copies it.
export default makeScene2D(function*(view){
 const t=createSignal(0);view.fill('#000');
 view.add(new Video({src:'/@fs/D:/Github/VideoEditing/shared/output/motion-canvas/yamyam-intro-sample-v2-visual.mp4',width:1920,height:1080,time:t}));
 yield* tween(2,v=>t(v*2));
});
