import {makeScene2D} from '@motion-canvas/2d';
import {useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {physicalFramingModel,FramingRole} from './physical-framing-model-v57';

export interface FramingClock {
 role:FramingRole; title:string; frames:number; sourceSha256:string;
 boundSourceSha256:string; allWholeAndContextTextsCompared:boolean;
 stages:{fromFrame:number;toFrame:number;progressFrom:number;progressTo:number;anchor:string}[];
}
// Clean explanation source. The final fixed caption layer is added from the
// same measured cues. This source rendering does not approve human listening.
export function physicalFramingScene(c:FramingClock){
 if(!c.allWholeAndContextTextsCompared||c.sourceSha256!==c.boundSourceSha256)throw Error('Hash-bound whole/context text review required');
 let end=0;
 for(const s of c.stages){
  if(!Number.isInteger(s.fromFrame)||!Number.isInteger(s.toFrame)||s.fromFrame<end||s.toFrame<=s.fromFrame||s.toFrame>c.frames||!s.anchor||s.progressFrom<0||s.progressTo>1||s.progressTo<s.progressFrom)throw Error('Reviewed integer word clock invalid');
  end=s.toFrame;
 }
 return makeScene2D(function*(view){
  view.fill(P.background);const m=physicalFramingModel(c.role);view.add(m.node);
  view.add(heading(c.role.split('-')[0].replace('part','회차 '),c.title,'관찰할 대상 → 계산의 책임 → 다음 질문','게임 렌더링 역사 · 마지막 픽셀'));
  const thread=useThread(),start=thread.fixed;
  while(true){
   const f=Math.round((thread.fixed-start)*60);if(f>=c.frames)break;
   let p=0;
   for(const s of c.stages){if(f<s.fromFrame)break;if(f>=s.toFrame)p=s.progressTo;else{p=s.progressFrom+(s.progressTo-s.progressFrom)*(f-s.fromFrame)/(s.toFrame-s.fromFrame);break;}}
   m.reset(p);yield;
  }
 });
}
