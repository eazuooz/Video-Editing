import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {transparencyModel} from './transparency-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=transparencyModel();view.add(m.node);view.add(heading('21a.7',"투명도와 머리카락: 가장 앞의 표면만으로 부족한 경우",'독립 도식의 움직임 검수 · 최종 내레이션 타이밍/실제 게임 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[12]);yield*waitFor(.3);yield*m.transition(m.poses[13],3.4);yield*waitFor(.3);});
