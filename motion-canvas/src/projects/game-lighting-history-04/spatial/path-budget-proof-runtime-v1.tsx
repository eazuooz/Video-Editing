import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {pathBudgetModel} from './path-budget-model-v1';
const titles=['2023: 경로 추적 기술 프리뷰','카메라에서 이어지는 표본 경로','방향 선택과 확률 보정','같은 기대값을 추정하는 두 분포','광원·재질 전략의 MIS 가중치','생존 확률의 역수로 보정','경로 종료의 비용과 오류','독립 표본과 제곱근 관계','배정·재사용·재구성을 연결'];
export function pathBudgetProof(i:number){return makeScene2D(function*(view){view.fill(P.background);const m=pathBudgetModel();view.add(m.node);view.add(heading('19',titles[i],'2.5D 모델 검수 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[i*2]);yield*waitFor(.3);yield*m.transition(m.poses[i*2+1],3.4);yield*waitFor(.3);});}
