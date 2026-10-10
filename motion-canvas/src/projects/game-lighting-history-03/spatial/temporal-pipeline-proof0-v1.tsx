import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {temporalModel} from './foundation-models-v5';
export default makeScene2D(function*(view){view.fill(P.background);const m=temporalModel();view.add(m.node);view.add(heading('14b.2',"렌더링·재구성·표시의 공간 관계",'측면 투영 수정 검수 · 최종 내레이션 타이밍/실제 게임 자료 아님','게임 렌더링 역사 3편'));m.reset(m.poses[2]);yield*waitFor(.3);yield*m.transition(m.poses[3],3.4);yield*waitFor(.3);});
