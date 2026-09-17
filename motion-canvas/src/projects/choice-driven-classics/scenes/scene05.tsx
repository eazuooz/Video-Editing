import {Node,Rect,makeScene2D} from '@motion-canvas/2d';
import {all,waitFor} from '@motion-canvas/core';
import {page,envelope,heading,label,shots} from './book';
import {BOOK as P} from '../styles';
export default makeScene2D(function* (view) {
  const p=page(view,4);
  heading(p,shots[4].heading,0,-305,54);
  label(p,'출간 계획',0,-210,25,true);
  const detail=['첫 30분 체험','작품별 완결판','독자 반응을 바탕으로'];
  const boxes=shots[4].steps!.map((s,i)=>{
    const box=new Rect({x:(i-1)*574,y:-8,width:482,height:236,stroke:P.line,lineWidth:2,opacity:0});p.add(box);
    label(box,s,0,-40,42);label(box,detail[i],0,45,27,true);
    if(i<2)label(p,'→',(i-.5)*574,-8,40,true);
    return box;
  });
  label(p,shots[4].priceQualifier!,0,200,27,true);
  label(p,shots[4].price!,0,275,60);
  label(p,'판매 실적이 아닌 사업 계획입니다',0,365,24,true);
  yield* envelope(p,9,(function*(){
    yield* waitFor(1);yield* boxes[0].opacity(1,.8);yield* waitFor(.6);
    yield* boxes[1].opacity(1,.8);yield* waitFor(.6);yield* boxes[2].opacity(1,.8);yield* waitFor(4.4);
  })());
});
