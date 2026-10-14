import {makeScene2D,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {prerequisiteIds,prerequisiteTitles,prerequisiteModel} from './additive-prerequisite-model-v1';

// Independent proof clock. No narration is attached and no final duration is
// approved here. The reserved box exercises the fixed two-line caption zone.
export function prerequisiteProof(i:number){return makeScene2D(function*(view){
 view.fill(P.background);
 const m=prerequisiteModel(prerequisiteIds[i]);m.node.y(-20);view.add(m.node);
 view.add(heading(`추가${i+1}`,prerequisiteTitles[i],'선행 개념·숫자 예 · 실제 음성에 맞춘 최종 타이밍은 별도','게임 렌더링 역사4편'));
 view.add(<Rect y={430} width={1500} height={134} radius={0} fill={'#ffffff'} stroke={'#121212'} lineWidth={2} shadowColor={'#164b35'} shadowBlur={0} shadowOffset={[9,9]}><Txt text={'아래 가운데 두 줄 자막 영역을 고정합니다.\n이 장면은 움직임·구도 검수용 무음 초안입니다.'} fontFamily={P.font} fontSize={48} lineHeight={58} fill={'#000000'} textAlign={'center'}/></Rect>);
 m.reset(0);yield*waitFor(.4);yield*m.transition(1,8);yield*waitFor(.4);
});}
