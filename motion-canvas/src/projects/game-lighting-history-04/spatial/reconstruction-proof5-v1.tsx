import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {reconstructionModel} from './reconstruction-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=reconstructionModel();view.add(m.node);view.add(heading('20.6',"레이 재구성: 노이즈 제거와 업스케일링의 역할",'독립 도식의 움직임 검수 · 최종 내레이션 타이밍/실제 게임 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[10]);yield*waitFor(.3);yield*m.transition(m.poses[11],3.4);yield*waitFor(.3);});
