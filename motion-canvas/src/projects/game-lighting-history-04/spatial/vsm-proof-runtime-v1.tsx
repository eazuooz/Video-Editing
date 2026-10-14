import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {vsmModel} from './vsm-model-v1';
const titles=['가장 가까운 깊이와 화면 표면 비교','넓은 가상 범위와 필요한 표본 밀도','주소·배정·그리는 작업의 분리','가상16주소와 필요한5페이지','카메라 참조 변화와 캐시 무효화','삼각형 교차와 다른 그림자 깊이 표본','정적 재사용과 변경 작업 비교'];
export function vsmProof(i:number){return makeScene2D(function*(view){view.fill(P.background);const m=vsmModel();view.add(m.node);view.add(heading('18v',titles[i],'2.5D 모델 검수용 · 내레이션 시점/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[i*2]);yield*waitFor(.3);yield*m.transition(m.poses[i*2+1],i===4?5:3.4);yield*waitFor(.3);});}
