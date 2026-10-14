import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {visibilityModel} from './visibility-model-v1';
const titles=["속성 저장과 표면 ID의 차이","표면 ID에서 원래 기하 데이터로","삼각형 7의 가중치와 UV","표면 경계와 미분/밉 선택","저장 절약과 복원 비용","공식 샘플의 가시성·셰이딩 책임"];
export function visibilityProof(i:number){return makeScene2D(function*(view){view.fill(P.background);const m=visibilityModel();view.add(m.node);view.add(heading('18a',titles[i],'모델 검수용 · 내레이션/실제 샘플 실행/최종 영상 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[i*2]);yield*waitFor(.3);yield*m.transition(m.poses[i*2+1],3.4);yield*waitFor(.3);});}
