import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {representationModel,dynamicRayModel,samplingModel,temporalModel,navigationModel} from './foundation-models-v3';
import data from './foundation-fix-data-v3.json';
const factories={representationModel,dynamicRayModel,samplingModel,temporalModel,navigationModel};
export function foundationProof(i:number){return makeScene2D(function*(view){const d=data[i],m=factories[d.model as keyof typeof factories]();view.fill(P.background);view.add(heading(d.scene+' · 문단 '+d.paragraph,d.title,'자료·확률·시간·오류의 관계','게임 렌더링 역사 3편'));view.add(m.node);m.reset(m.poses[d.mode*2]);view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={d.title+'\n입체·정보·움직임·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);yield*waitFor(.5);yield*m.transition(m.poses[d.mode*2+1],2);yield*waitFor(.5);});}
