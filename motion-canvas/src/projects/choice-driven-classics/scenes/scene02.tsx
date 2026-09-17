import {Img,Rect,makeScene2D} from '@motion-canvas/2d';
import {all,waitFor,easeInOutCubic} from '@motion-canvas/core';
import screen from '../assets/screen-crime-ko.jpg';
import {page,envelope} from './book';
import {BOOK as P} from '../styles';
export default makeScene2D(function* (view) {
  const p=page(view,1,true);
  // Original screenshot is a single unchanged, uniformly scaled image.
  const ui=new Rect({y:-42,width:1600,height:900,scale:.94});p.add(ui);
  ui.add(new Img({src:screen,width:1600}));
  const body=new Rect({x:314,y:-70,width:842,height:360,stroke:P.ink,lineWidth:1.7,opacity:0});
  const choices=new Rect({x:307,y:225,width:844,height:188,stroke:P.ink,lineWidth:1.7,opacity:0});
  ui.add(body);ui.add(choices);
  yield* envelope(p,12,(function*(){
    yield* waitFor(1.6); yield* body.opacity(.8,1);
    yield* waitFor(3.6); yield* body.opacity(0,.8);
    yield* choices.opacity(.8,1);yield* waitFor(3.2);yield* choices.opacity(0,.8);
  })());
});
