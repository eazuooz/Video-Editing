import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {restirModel} from './restir-model-v1';
const titles=['많은 직접광에서 후보 선택','작은 저장소와 후보 요약','가중치 1과 3의 선택 확률','선택과 최종 조명 추정의 차이','이웃과 과거 후보의 재사용','문이 닫힌 뒤 현재 가시성 검사','표본 선택과 영상 필터링'];
export function restirProof(i:number){return makeScene2D(function*(view){
 const m=restirModel();view.fill(P.background);view.add(heading(`15b · 문단 ${i+1}`,titles[i],'후보 · 요약 · 가시성 · 필터','게임 렌더링 역사 3편'));
 view.add(m.node);m.reset(m.poses[i*2]);
 view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={titles[i]+'\n입체·계산·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 yield*waitFor(.5);yield*m.transition(m.poses[i*2+1],2);yield*waitFor(.5);
});}
