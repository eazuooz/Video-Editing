import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {postprocessModel} from './postprocess-model-v3';
export default makeScene2D(function*(view){view.fill(P.background);const m=postprocessModel();view.add(m.node);view.add(heading('22p.4','후처리: 입력 단위와 카메라 기준 구별','문구·높이 수정 검수 · 최종 내레이션/실제 게임 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[6]);yield*waitFor(.3);yield*m.transition(m.poses[7],3.4);yield*waitFor(.3);});
