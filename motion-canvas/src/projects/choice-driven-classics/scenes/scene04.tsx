import {Img,Node,Line,makeScene2D} from '@motion-canvas/2d';
import {all,waitFor,easeInOutCubic} from '@motion-canvas/core';
import art from '../assets/art-birds.jpg';
import {page,envelope,heading,label,shots} from './book';
import {BOOK as P} from '../styles';
export default makeScene2D(function* (view) {
  const p=page(view,3);
  const picture=new Img({src:art,width:570,x:-545,y:-27});p.add(picture);
  heading(p,shots[3].heading,372,-293,47,830);
  const steps=shots[3].steps!.map((s,i)=>{
    const group=new Node({x:377,y:-118+i*142,opacity:0});p.add(group);
    label(group,s,0,0,i===2?43:38);
    if(i<2)label(group,'↓',0,66,29,true);
    return group;
  });
  label(p,'흑백 펜화로 소설의 감각을 살립니다',370,340,29,true);
  label(p,'삽화 — 정인',-760,378,22,true);
  yield* envelope(p,10,(function*(){
    yield* all(picture.scale(1.02,10,easeInOutCubic),(function*(){
      yield* waitFor(1);yield* steps[0].opacity(1,.8);yield* waitFor(1.2);
      yield* steps[1].opacity(1,.8);yield* waitFor(1.2);yield* steps[2].opacity(1,.8);
      yield* waitFor(4.2);
    })());
  })());
});
