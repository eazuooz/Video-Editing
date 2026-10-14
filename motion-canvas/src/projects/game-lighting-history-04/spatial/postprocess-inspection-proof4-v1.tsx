import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {postprocessModel} from './postprocess-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=postprocessModel();view.add(m.node);view.add(heading('22p.4',"마지막 색: 노출, 톤 매핑과 후처리",'독립 도식 움직임 검수 · 최종 음성 타이밍/실제 캡처 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[6]);yield*waitFor(.3);yield*m.transition(m.poses[7],3.4);yield*waitFor(.3);});
