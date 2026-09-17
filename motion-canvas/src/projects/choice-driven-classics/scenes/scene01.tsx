import {Img,makeScene2D,Rect} from '@motion-canvas/2d';
import {easeInOutCubic} from '@motion-canvas/core';
import art from '../assets/art-hands.jpg';
import {page,heading,label,envelope,shots} from './book';
import {BOOK as P} from '../styles';
export default makeScene2D(function* (view) {
  const p=page(view,0);
  const frame=new Rect({x:-366,y:-35,width:990,height:748,clip:true});
  const picture=new Img({src:art,width:990}); frame.add(picture); p.add(frame);
  heading(p,shots[0].heading,535,-110,62,600);
  label(p,'읽는 사람에서',465,120,30,true);
  label(p,'선택하는 주인공으로',513,178,34);
  label(p,'삽화 — 정인',-772,378,22,true);
  yield* envelope(p,8,picture.scale(1.025,8,easeInOutCubic));
});
