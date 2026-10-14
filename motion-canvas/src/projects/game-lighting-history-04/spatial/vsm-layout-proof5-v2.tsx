import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {vsmModel} from './vsm-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=vsmModel();view.add(m.node);view.add(heading('18v','SMRT: 표본과 제목의 공간 분리','수정 구간 모델 검수 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[10]);yield*waitFor(.3);yield*m.transition(m.poses[11],3.4);yield*waitFor(.3);});
