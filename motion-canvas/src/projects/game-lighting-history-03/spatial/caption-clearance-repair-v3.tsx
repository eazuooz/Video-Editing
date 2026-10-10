import {makeScene2D, Node, Txt} from '@motion-canvas/2d';
import {waitFor, linear, useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import data from './narrated-data-v3.json';
import repair from './caption-clearance-repair-data-v3.json';
import {ddgiModel} from './ddgi-model-v1';
import {restirModel} from './restir-model-v2';
import {cullingModelV2} from './culling-model-v3';
import {pipelineModel} from './pipeline-model-v1';
import {naniteModelV2} from './nanite-model-v2';
import {cacheModel} from './cache-model-v1';
const factories={ddgi:ddgiModel,restir:restirModel,culling:cullingModelV2,pipeline:pipelineModel,nanite:naniteModelV2,cache:cacheModel};

// waitFor deliberately completes up to one frame ahead of fixed playback time.
// Hold the current complete pose until the exact next frame before replacing it.
function* fixedBoundary(frame:number){
 const thread=useThread();
 while(Math.round(thread.fixed*60)<frame)yield;
 thread.time(frame/60);
}
export default makeScene2D(function*(view){
 view.fill(P.background);
 const h=heading('','', '자료 · 확률 · 시간 · 오류의 한계','게임 렌더링 역사 3편');
 view.add(h);const id=h.children()[0] as Txt,title=h.children()[1] as Txt;
 let previous:Node|undefined;
 for(const clip of repair.clips){
  yield*fixedBoundary(clip.repairFromFrame);
  previous?.remove();
  const chapter=data.chapters[clip.chapterIndex],p=chapter.paragraphs[clip.paragraphIndex];
  const m=factories[chapter.model as keyof typeof factories]();
  view.add(m.node);m.node.y(clip.modelShiftY);previous=m.node;
  id.text(`${chapter.scene} · 게임 렌더링 역사 3편`);title.text(chapter.titles[p.index]);
  const from=clip.sourceSampleRange[0]/24000-chapter.sourceFrom;
  const duration=clip.frames/60;
  if(p.move[0]<from-1e-6||p.move[1]>from+duration+1e-6)throw Error('Preserve complete narrated motion');
  m.reset(m.poses[p.pair[0]]);
  yield*waitFor(Math.max(0,p.move[0]-from));
  yield*m.transition(m.poses[p.pair[1]],p.move[1]-p.move[0]);
  yield*waitFor(Math.max(0,duration-(p.move[1]-from)));
  yield*fixedBoundary(clip.repairToFrame);
 }
});
