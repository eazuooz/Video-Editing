import {makeScene2D,Txt} from '@motion-canvas/2d';
import {waitFor,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import data from './narrated-data-v3.json';
import selected from './retained-clean-data-v1.json';
import {bvhModel} from './bvh-model-v1';
import {ddgiModel} from './ddgi-model-v1';
import {restirModel} from './restir-model-v2';
import {naniteModel} from './nanite-model-v1';
import {lumenModel} from './lumen-model-v2';
import {cacheModel} from './cache-model-v1';
import {navigationModel,representationModel,dynamicRayModel,samplingModel,temporalModel} from './foundation-models-v5';
import {cullingModelV2} from './culling-model-v3';
import {pipelineModel} from './pipeline-model-v1';
const factories={navigation:navigationModel,representation:representationModel,bvh:bvhModel,dynamicRay:dynamicRayModel,sampling:samplingModel,temporal:temporalModel,ddgi:ddgiModel,restir:restirModel,culling:cullingModelV2,pipeline:pipelineModel,nanite:naniteModel,lumen:lumenModel,cache:cacheModel};

// Render only the47 complete retained explanation paragraphs, with the same
// ASR-word-anchored poses and motion. Captions are burned once after native
// interleaving, so both the clean master and final fixed-caption master remain
// available. This file does not adopt a timeline or approve any final pixels.
export function retainedCleanChapterV1(i:number){return makeScene2D(function*(view){
 const chapter=data.chapters[i],m=factories[chapter.model as keyof typeof factories]();
 const clips=selected.clips.filter(x=>x.chapterIndex===i);
 view.fill(P.background);view.add(m.node);if(chapter.model==='bvh')m.node.y(15);
 const h=heading(chapter.scene,chapter.titles[0],'자료 · 확률 · 시간 · 오류의 한계','게임 렌더링 역사 3편');view.add(h);const title=h.children()[1] as Txt;
 for(const clip of clips){
  const p=chapter.paragraphs[clip.paragraphIndex];
  const from=clip.sourceSampleRange[0]/24000-chapter.sourceFrom;
  const duration=clip.frames/60;
  if(p.move[0]<from-1e-6||p.move[1]>from+duration+1e-6)throw Error('Complete narration-timed motion required');
  m.reset(m.poses[p.pair[0]]);title.text(chapter.titles[p.index]);
  let elapsed=0;
  if('earlyRay' in p&&p.earlyRay&&'controls' in m&&'t' in m.controls){
   const ray=p.earlyRay;
   yield*waitFor(Math.max(0,ray.from-from));
   yield*m.controls.t(8,ray.to-ray.from,linear);elapsed=ray.to-from;
  }
  yield*waitFor(Math.max(0,p.move[0]-from-elapsed));
  yield*m.transition(m.poses[p.pair[1]],p.move[1]-p.move[0]);
  yield*waitFor(Math.max(0,duration-(p.move[1]-from)));
 }
});}
