import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {mobileModel} from './mobile-model-v1';
const titles=["타일 하드웨어와 패스 순서","같은 타일 이름·다른 책임","G-buffer를 타일 안에서 소비","외부 메모리가 필요한 조건","투명 효과의 별도 경로","조건에 따른 파이프라인 선택"];
export function mobileProof(i:number){return makeScene2D(function*(view){view.fill(P.background);const m=mobileModel();view.add(m.node);view.add(heading('18m',titles[i],'모델 검수용 · 실제 기기 캡처/성능 측정/내레이션 승인 아님','게임 렌더링 역사 4편'));m.reset(m.poses[i*2]);yield*waitFor(.3);yield*m.transition(m.poses[i*2+1],3.4);yield*waitFor(.3);});}
