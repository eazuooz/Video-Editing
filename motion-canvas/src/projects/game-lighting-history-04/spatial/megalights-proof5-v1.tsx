import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {megalightsModel} from './megalights-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=megalightsModel();view.add(m.node);view.add(heading('21m.6',"메가라이트: 많은 직접광의 표본을 고르는 문제",'독립 도식 움직임 검수 · 최종 음성 타이밍/실제 시연 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[10]);yield*waitFor(.3);yield*m.transition(m.poses[11],3.4);yield*waitFor(.3);});
