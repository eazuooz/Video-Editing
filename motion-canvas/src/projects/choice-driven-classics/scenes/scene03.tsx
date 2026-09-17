import {Img,Rect,Node,Line,makeScene2D} from '@motion-canvas/2d';
import {all,waitFor,easeInOutCubic} from '@motion-canvas/core';
import screen from '../assets/screen-crime-ko.jpg';
import {page,envelope,heading,label,shots} from './book';
import {BOOK as P} from '../styles';
export default makeScene2D(function* (view) {
  const p=page(view,2,true);
  const ui=new Node({y:-42,scale:.94});p.add(ui);ui.add(new Img({src:screen,width:1600}));
  const selection=new Rect({x:104,y:225,width:620,height:60,stroke:P.ink,lineWidth:2,opacity:0});ui.add(selection);
  const cursor=new Line({points:[[0,0],[0,32],[9,23],[17,39],[24,35],[16,20],[29,20],[0,0]],fill:P.paper,stroke:P.ink,lineWidth:2,position:[565,335],opacity:0});ui.add(cursor);
  const result=new Node({opacity:0});p.add(result);
  heading(result,shots[2].heading,0,-295,58);
  label(result,'선택 결과 개념도 · 검토안',0,-198,26,true);
  label(result,shots[2].metricLabel!,0,-87,36);
  const before=label(result,String(shots[2].before),-165,42,108);
  label(result,'→',0,42,60,true);
  const after=label(result,String(shots[2].after),165,42,108);after.opacity(0);
  label(result,'인물 관계  →  다음 장면  →  결말',0,215,34);
  label(result,'선택 이후 원본 또는 개념도 대체 승인 대기',0,334,24,true);
  yield* envelope(p,13,(function*(){
    yield* waitFor(1);yield* all(cursor.opacity(1,.7),cursor.position([-120,207],2.2,easeInOutCubic));
    yield* selection.opacity(1,.8);yield* waitFor(.8);
    yield* ui.opacity(0,.8);yield* result.opacity(1,.8);
    yield* after.opacity(1,1.2);yield* waitFor(4.6);
  })());
});
