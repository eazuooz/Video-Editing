import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import data from './narrated-data-v1.json';
import {bvhModel} from './bvh-model-v1';
import {ddgiModel} from './ddgi-model-v1';
import {restirModel} from './restir-model-v1';
const titles=[
['레이의 점과 경계 상자','부모 상자에서 하위 가지 생략','세 축 구간을 공통 t로 비교','[4,5]에서 겹침 없음으로','상자 통과와 삼각형 교차 분리','가장 가까운 표면과 불투명 가림','성긴 상자의 불필요한 후보','교차·셰이딩·갱신의 서로 다른 비용'],
['표면에서 공간의 조사량을 질의','카메라와 프로브의 서로 다른 좌표','벽 너머 빛이 그대로 섞이는 문제','가림에 따라 기여를 줄여 비교','간격·저장·갱신의 교환','새 표본과 캐시의 시간 차이'],
['많은 직접광에서 후보 선택','작은 저장소와 후보 요약','가중치 1과 3의 선택 확률','선택과 최종 조명 추정의 차이','이웃과 과거 후보의 재사용','문이 닫힌 뒤 현재 가시성 검사','표본 선택과 영상 필터링']
];
export function narratedChapter(i:number){return makeScene2D(function*(view){
 const chapter=data.chapters[i],m=[bvhModel,ddgiModel,restirModel][i](),clock=createSignal(0);
 const caption=()=>chapter.cues.find(c=>clock()>=c.from&&clock()<c.to)?.text??'';
 view.fill(P.background);view.add(m.node);if(i===0)m.node.y(15);
 const h=heading(chapter.scene,titles[i][0],['레이 · 경계 · 삼각형','프로브 · 가림 · 갱신','후보 · 요약 · 가시성'][i],'게임 렌더링 역사 3편');view.add(h);
 const title=h.children()[1] as Txt;
 view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 function* motion(){let elapsed=0;for(const p of chapter.paragraphs){
  if(p.from>elapsed)yield*waitFor(p.from-elapsed);
  m.reset(m.poses[p.pair[0]]);title.text(titles[i][p.index]);
  yield*waitFor(Math.max(0,p.move[0]-p.from));
  yield*m.transition(m.poses[p.pair[1]],p.move[1]-p.move[0]);
  yield*waitFor(Math.max(0,p.to-p.move[1]));elapsed=p.to;
 }}
 yield*all(clock(chapter.duration,chapter.duration,linear),motion());
});}
