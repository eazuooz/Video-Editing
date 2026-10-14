import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {transparencyModel} from './transparency-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=transparencyModel();view.add(m.node);view.add(heading('21a.6','투명도: 순서와 층별 출력','수정 모델의 실제 움직임 검수 · 최종 영상/내레이션 타이밍 아님','게임 렌더링 역사 4편'));m.reset(m.poses[10]);yield*waitFor(.3);yield*m.transition(m.poses[11],3.4);yield*waitFor(.3);});
