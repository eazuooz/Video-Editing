import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {upscalingModel} from './upscaling-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=upscalingModel();view.add(m.node);view.add(heading('18t','인접 렌더 프레임 사이의 생성','수정 구간 모델 검수 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[10]);yield*waitFor(.3);yield*m.transition(m.poses[11],3.4);yield*waitFor(.3);});
