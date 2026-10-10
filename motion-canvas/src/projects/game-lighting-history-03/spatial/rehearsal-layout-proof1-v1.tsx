import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {cullingModelV2} from './culling-model-v3';
export default makeScene2D(function*(view){view.fill(P.background);const m=cullingModelV2();view.add(m.node);view.add(heading('16aa.4',"깊이 요약 조건 두 줄의 간격",'실제 리허설에서 발견한 겹침 수정 · 최종 내레이션/게임 자료 아님','게임 렌더링 역사 3편'));m.reset(m.poses[6]);yield*waitFor(.3);yield*m.transition(m.poses[7],3.4);yield*waitFor(.3);});
