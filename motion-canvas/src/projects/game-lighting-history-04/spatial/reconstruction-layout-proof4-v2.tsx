import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {reconstructionModel} from './reconstruction-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=reconstructionModel();view.add(m.node);view.add(heading('20.5','레이 재구성: 역할과 유효한 역사','수정 모델의 실제 움직임 검수 · 최종 영상/내레이션 타이밍 아님','게임 렌더링 역사 4편'));m.reset(m.poses[8]);yield*waitFor(.3);yield*m.transition(m.poses[9],3.4);yield*waitFor(.3);});
