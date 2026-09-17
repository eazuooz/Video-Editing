import {Img,makeScene2D} from '@motion-canvas/2d';
import {easeInOutCubic} from '@motion-canvas/core';
import art from '../assets/art-finished.jpg';
import {page,envelope,heading,label,shots} from './book';
export default makeScene2D(function* (view) {
  const p=page(view,5);
  const picture=new Img({src:art,height:792,x:-493,y:-28});p.add(picture);
  heading(p,shots[5].heading,425,-95,60,810);
  label(p,'첫 30분 데모부터 시작합니다',405,239,34);
  label(p,'개발 계획 · 아직 출시되지 않았습니다',421,309,24,true);
  yield* envelope(p,8,picture.scale(1.018,8,easeInOutCubic));
});
