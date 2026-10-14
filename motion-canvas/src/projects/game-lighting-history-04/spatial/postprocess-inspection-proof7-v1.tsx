import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {frameInspectionModel} from './frame-inspection-model-v1';
export default makeScene2D(function*(view){view.fill(P.background);const m=frameInspectionModel();view.add(m.node);view.add(heading('22r.1',"프레임 검사: 기술 이름 대신 실제 자원을 따라가기",'독립 도식 움직임 검수 · 최종 음성 타이밍/실제 캡처 자료 아님','게임 렌더링 역사 4편'));m.reset(m.poses[0]);yield*waitFor(.3);yield*m.transition(m.poses[1],3.4);yield*waitFor(.3);});
