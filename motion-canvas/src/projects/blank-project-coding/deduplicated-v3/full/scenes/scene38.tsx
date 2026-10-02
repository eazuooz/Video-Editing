import {makeScene2D,Video} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import clip0 from '../../../../../../../projects/blank-project-coding/revisions/deduplicated-v3/cuts/091a.mp4?url';
import clip1 from '../../../../../../../projects/blank-project-coding/revisions/deduplicated-v3/cuts/091b.mp4?url';
import clip2 from '../../../../../../../projects/blank-project-coding/revisions/deduplicated-v3/cuts/091c.mp4?url';
import clip3 from '../../../../../../../projects/blank-project-coding/revisions/original-restored-v2/cuts/092.mp4?url';
export default makeScene2D(function*(view){{const v=new Video({src:clip0,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(329/60+1e-7);v.pause();v.remove();}
{const v=new Video({src:clip1,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(220/60+1e-7);v.pause();v.remove();}
{const v=new Video({src:clip2,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(435/60+1e-7);v.pause();v.remove();}
{const v=new Video({src:clip3,width:1920,height:1080});view.add(v);(v as any).video().muted=true;v.play();yield*waitFor(341/60+1e-7);v.pause();v.remove();}});
