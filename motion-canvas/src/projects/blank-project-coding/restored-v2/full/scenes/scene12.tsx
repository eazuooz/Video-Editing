import {makeScene2D,Video} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import clip0 from '../../../../../../../projects/blank-project-coding/revisions/original-restored-v2/cuts/028.mp4?url';
import clip1 from '../../../../../../../projects/blank-project-coding/revisions/original-restored-v2/cuts/029.mp4?url';
import clip2 from '../../../../../../../projects/blank-project-coding/revisions/original-restored-v2/cuts/030.mp4?url';
export default makeScene2D(function*(view){{const v=new Video({src:clip0,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(228/60+1e-7);v.pause();v.remove();}
{const v=new Video({src:clip1,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(240/60+1e-7);v.pause();v.remove();}
{const v=new Video({src:clip2,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(425/60+1e-7);v.pause();v.remove();}});
