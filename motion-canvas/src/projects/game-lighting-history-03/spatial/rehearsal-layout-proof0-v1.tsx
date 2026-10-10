import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {restirModel} from './restir-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=restirModel();view.add(m.node);view.add(heading('15b.4',"보정 입력과 화살표의 분리",'실제 리허설에서 발견한 겹침 수정 · 최종 내레이션/게임 자료 아님','게임 렌더링 역사 3편'));m.reset(m.poses[6]);yield*waitFor(.3);yield*m.transition(m.poses[7],3.4);yield*waitFor(.3);});
