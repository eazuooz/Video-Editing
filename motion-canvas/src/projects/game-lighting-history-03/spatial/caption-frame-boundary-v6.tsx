import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {createSignal,waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {captionAtFrame} from '../../game-lighting-history-shared/caption-frame-time';
import data from './narrated-data-v3.json';
import proof from './caption-frame-boundary-data-v6.json';
export default makeScene2D(function*(view){const sample=createSignal(0),s=()=>proof.samples[sample()],c=()=>data.chapters[s().chapter],caption=()=>captionAtFrame(c().cues,c().timelineFrom,s().localFrame/60);view.fill(P.background);view.add(<Txt y={-320} text={()=>s().scene+' · local frame '+s().localFrame+' · global frame '+s().globalFrame} fontFamily={P.font} fontSize={42} fill={P.ink}/>);view.add(<Txt y={-180} text={'자막 경계만 검수 · 전체 설명 영상 승인 아님'} fontFamily={P.font} fontSize={32} fill={P.title}/>);view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);for(let i=0;i<proof.samples.length;i++){sample(i);yield*waitFor(.1);}});
