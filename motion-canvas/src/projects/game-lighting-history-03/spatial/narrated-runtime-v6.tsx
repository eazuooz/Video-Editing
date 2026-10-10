import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import data from './narrated-data-v3.json';
import {captionAtFrame} from '../../game-lighting-history-shared/caption-frame-time';
import {bvhModel} from './bvh-model-v1';
import {ddgiModel} from './ddgi-model-v1';
import {restirModel} from './restir-model-v1';
import {naniteModel} from './nanite-model-v1';
import {lumenModel} from './lumen-model-v1';
import {cacheModel} from './cache-model-v1';
import {navigationModel,representationModel,dynamicRayModel,samplingModel,temporalModel} from './foundation-models-v4';
import {cullingModelV2} from './culling-model-v2';
import {pipelineModel} from './pipeline-model-v1';
const factories={navigation:navigationModel,representation:representationModel,bvh:bvhModel,dynamicRay:dynamicRayModel,sampling:samplingModel,temporal:temporalModel,ddgi:ddgiModel,restir:restirModel,culling:cullingModelV2,pipeline:pipelineModel,nanite:naniteModel,lumen:lumenModel,cache:cacheModel};
export function narratedChapterV6(i:number){return makeScene2D(function*(view){
 const chapter=data.chapters[i],m=factories[chapter.model as keyof typeof factories](),clock=createSignal(0);
 const caption=()=>captionAtFrame(chapter.cues,chapter.timelineFrom,clock());
 view.fill(P.background);view.add(m.node);if(chapter.model==='bvh')m.node.y(15);
 const h=heading(chapter.scene,chapter.titles[0],'자료 · 확률 · 시간 · 오류의 한계','게임 렌더링 역사 3편');view.add(h);const title=h.children()[1] as Txt;
 view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 function* motion(){let elapsed=0;for(const p of chapter.paragraphs){
  if(p.from>elapsed)yield*waitFor(p.from-elapsed);
  m.reset(m.poses[p.pair[0]]);title.text(chapter.titles[p.index]);
  let current=p.from;
  if('earlyRay' in p&&p.earlyRay&&'controls' in m&&'t' in m.controls){
   const ray=p.earlyRay;yield*waitFor(ray.from-current);
   yield*m.controls.t(8,ray.to-ray.from,linear);current=ray.to;
  }
  yield*waitFor(Math.max(0,p.move[0]-current));
  yield*m.transition(m.poses[p.pair[1]],p.move[1]-p.move[0]);
  yield*waitFor(Math.max(0,p.to-p.move[1]));elapsed=p.to;
 }}
 yield*all(clock(chapter.duration,chapter.duration,linear),motion());
 yield*waitFor(Math.max(0,chapter.sequenceDuration-chapter.duration));
});}
