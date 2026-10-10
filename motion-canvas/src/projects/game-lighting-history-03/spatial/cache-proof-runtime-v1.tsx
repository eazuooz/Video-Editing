import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {cacheModel} from './cache-model-v1';
const titles=['직접광과 캐시의 변화 속도','새 표면과 오래된 대응','표면 커버리지 확인','얇은 벽과 표본 예산','카메라와 조명 비교 분리','추적·저장·분할 갱신'];
export function cacheProof(i:number){return makeScene2D(function*(view){
 const m=cacheModel();view.fill(P.background);
 view.add(heading(`17b · 문단 ${i+1}`,titles[i],'동적 조명 · 표면 정보 · 갱신 예산','게임 렌더링 역사 3편'));
 view.add(m.node);m.reset(m.poses[i*2]);
 view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={titles[i]+'\n입체·가림·움직임·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 yield*waitFor(.5);yield*m.transition(m.poses[i*2+1],2);yield*waitFor(.5);
});}
