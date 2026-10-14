import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {seriesSynthesisModel} from './series-synthesis-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=seriesSynthesisModel();view.add(m.node);view.add(heading('conclusion.1',"네 편을 관통하는 질문: 어디에서 어떤 정보를 얻는가",'독립 도식 움직임 검수 · 최종 음성 타이밍/실제 캡처 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[2]);yield*waitFor(.3);yield*m.transition(m.poses[3],3.4);yield*waitFor(.3);});
