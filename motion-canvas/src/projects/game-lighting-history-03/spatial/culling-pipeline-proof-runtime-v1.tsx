import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {cullingModel} from './culling-model-v1';
import {pipelineModel} from './pipeline-model-v1';
const titles=[["시야 밖과 가림의 구별","시야 안에 있지만 벽 뒤에 가림","가능한 얼리 깊이 검사","보수적인 계층 깊이 요약","현재 가림과 과거 깊이","레이 질의와 렌더 제출"],["메시 묶음의 처리","셰이딩 빈도와 픽셀 수","2×2 평가 공유","가상 페이지와 상주 메모리","수요 피드백과 데이터 도착","서로 다른 작업 자원"]];
export function workProof(model:number,i:number){return makeScene2D(function*(view){const m=model?pipelineModel():cullingModel();view.fill(P.background);view.add(heading((model?'16ab':'16aa')+' · 문단 '+(i+1),titles[model][i],'가시성 · 기하 · 빈도 · 메모리','게임 렌더링 역사 3편'));view.add(m.node);m.reset(m.poses[i*2]);view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={titles[model][i]+'\n입체·가림·움직임·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);yield*waitFor(.5);yield*m.transition(m.poses[i*2+1],2);yield*waitFor(.5);});}
