import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {naniteModel} from './nanite-model-v1';
import {lumenModel} from './lumen-model-v1';
const titles=[
 ['필요한 기하 표현 선택','클러스터 · 그룹 · 단순화 · 재분할','거리와 화면에서의 오차','거리 2배 · 투영 오차 ½','이웃 경계와 균열 방지','선택과 메모리 공급의 차이','기하 공급과 조명 갱신'],
 ['추적 · 저장 · 최종 질의','화면에서 장면 표현으로','거리장과 삼각형 경로','메시 표면과 캡처 카드','표면 위치와 조명 조회','간접광 변화 비교','Nanite와 Lumen의 지원 관계']
];
export function engineProof(kind:number,i:number){return makeScene2D(function*(view){
 const m=[naniteModel,lumenModel][kind]();view.fill(P.background);
 view.add(heading(`${kind===0?'16a':'17a'} · 문단 ${i+1}`,titles[kind][i],kind===0?'원본 기하 · 표현 선택 · 공급':'화면 · 장면 · 표면 캐시','게임 렌더링 역사 3편'));
 view.add(m.node);m.reset(m.poses[i*2]);
 view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={titles[kind][i]+'\n입체·가림·움직임·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 yield*waitFor(.5);yield*m.transition(m.poses[i*2+1],2);yield*waitFor(.5);
});}
