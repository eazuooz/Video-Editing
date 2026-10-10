import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {lumenModel} from './lumen-model-v2';
export default makeScene2D(function*(view){view.fill(P.background);const m=lumenModel();view.add(m.node);view.add(heading('17a.5',"표면 추적과 조명 캐시 조회",'실제 리허설에서 발견한 겹침 수정 · 최종 내레이션/게임 자료 아님','게임 렌더링 역사 3편'));m.reset(m.poses[8]);yield*waitFor(.3);yield*m.transition(m.poses[9],3.4);yield*waitFor(.3);});
