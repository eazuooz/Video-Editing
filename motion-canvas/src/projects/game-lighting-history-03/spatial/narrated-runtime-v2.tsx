import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import data from './narrated-data-v2.json';
import {bvhModel} from './bvh-model-v1';
import {ddgiModel} from './ddgi-model-v1';
import {restirModel} from './restir-model-v1';
import {naniteModel} from './nanite-model-v1';
import {lumenModel} from './lumen-model-v1';
import {cacheModel} from './cache-model-v1';
const titles=[
 ['레이의 점과 경계 상자','부모 상자에서 하위 가지 생략','세 축 구간을 공통 t로 비교','[4,5]에서 겹침 없음으로','상자 통과와 삼각형 교차 분리','가장 가까운 표면과 불투명 가림','성긴 상자의 불필요한 후보','교차·셰이딩·갱신의 서로 다른 비용'],
 ['표면에서 공간의 조사량을 질의','카메라와 프로브의 서로 다른 좌표','벽 너머 빛이 그대로 섞이는 문제','가림에 따라 기여를 줄여 비교','간격·저장·갱신의 교환','새 표본과 캐시의 시간 차이'],
 ['많은 직접광에서 후보 선택','작은 저장소와 후보 요약','가중치 1과 3의 선택 확률','선택과 최종 조명 추정의 차이','이웃과 과거 후보의 재사용','문이 닫힌 뒤 현재 가시성 검사','표본 선택과 영상 필터링'],
 ['필요한 기하를 선택하고 공급','클러스터·그룹·계층','세계 오차와 화면 오차','거리와 투영 오차의 계산','이웃 경계와 균열','선택과 스트리밍의 차이','기하 처리에서 동적 조명으로'],
 ['추적·저장·최종 질의','화면 추적과 장면 표현','거리장과 삼각형 경로','표면과 캡처 카드','위치 찾기와 캐시 읽기','간접광 변화 비교','기하 공급과 조명 갱신의 연결'],
 ['직접광과 캐시의 변화 속도','새 표면과 오래된 대응','표면 커버리지 확인','얇은 벽과 표본 예산','카메라와 조명 비교 분리','추적·저장·분할 갱신']
];
const topics=['레이 · 경계 · 삼각형','프로브 · 가림 · 갱신','후보 · 요약 · 가시성','기하 · 오차 · 스트리밍','추적 · 표현 · 캐시','동적 조명 · 표면 정보 · 갱신 예산'];
export function narratedChapterV2(i:number){return makeScene2D(function*(view){
 const chapter=data.chapters[i],m=[bvhModel,ddgiModel,restirModel,naniteModel,lumenModel,cacheModel][i](),clock=createSignal(0);
 const caption=()=>chapter.cues.find(c=>clock()>=c.from&&clock()<c.to)?.text??'';
 view.fill(P.background);view.add(m.node);if(i===0)m.node.y(15);
 const h=heading(chapter.scene,titles[i][0],topics[i],'게임 렌더링 역사 3편');view.add(h);const title=h.children()[1] as Txt;
 view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 function* motion(){let elapsed=0;for(const p of chapter.paragraphs){
  if(p.from>elapsed)yield*waitFor(p.from-elapsed);
  m.reset(m.poses[p.pair[0]]);title.text(titles[i][p.index]);
  yield*waitFor(Math.max(0,p.move[0]-p.from));yield*m.transition(m.poses[p.pair[1]],p.move[1]-p.move[0]);
  yield*waitFor(Math.max(0,p.to-p.move[1]));elapsed=p.to;
 }}
 yield*all(clock(chapter.duration,chapter.duration,linear),motion());
});}
