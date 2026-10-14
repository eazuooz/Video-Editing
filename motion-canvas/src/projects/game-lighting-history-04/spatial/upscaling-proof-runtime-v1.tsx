import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {upscalingModel} from './upscaling-model-v1';
const titles=["내부 해상도와 복원 출력","TSR과SR의 공통 역할·다른 조건","픽셀 수¼과 전체 시간의 구별","현재 표면과 이전 대응","새로 드러난 영역의 이력 거절","렌더 프레임과 표시 프레임","해상도·렌더·표시·지연의 별도 기록"];
export function upscalingProof(i:number){return makeScene2D(function*(view){view.fill(P.background);const m=upscalingModel();view.add(m.node);view.add(heading('18t',titles[i],'2.5D 모델 검수용 · 실제 내레이션/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[i*2]);yield*waitFor(.3);yield*m.transition(m.poses[i*2+1],3.4);yield*waitFor(.3);});}
