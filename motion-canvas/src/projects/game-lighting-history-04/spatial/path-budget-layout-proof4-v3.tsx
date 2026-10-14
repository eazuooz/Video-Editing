import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {pathBudgetModel} from './path-budget-model-v3';
export default makeScene2D(function*(view){view.fill(P.background);const m=pathBudgetModel();view.add(m.node);view.add(heading('19','같은 방향을 평가하는 MIS','수정 구간 모델 검수 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[8]);yield*waitFor(.3);yield*m.transition(m.poses[9],3.4);yield*waitFor(.3);});
