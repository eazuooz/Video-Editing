import {makeScene2D} from '@motion-canvas/2d';
import {useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {guidedTeachingModel,GuidedTeachingRole} from './guided-teaching-model-v74';
import {focusAnalysisModel,FocusAnalysisRole} from './focus-analysis-model-v137';

export interface GuidedSourceClock {
 role:GuidedTeachingRole|FocusAnalysisRole; title:string; frames:number;
 sourceSha256:string; boundSourceSha256:string; wholeAndContextCompared:boolean;
 stages:{fromFrame:number;toFrame:number;progressFrom:number;progressTo:number;anchor:string}[];
}
export function guidedSourceScene(c:GuidedSourceClock){
 if(!c.wholeAndContextCompared||c.sourceSha256!==c.boundSourceSha256)throw Error('Current complete whole/context comparison required');
 let end=0;
 for(const s of c.stages){
  if(!Number.isInteger(s.fromFrame)||!Number.isInteger(s.toFrame)||s.fromFrame<end||s.toFrame<=s.fromFrame||s.toFrame>c.frames||s.progressTo<s.progressFrom||s.progressFrom<0||s.progressTo>1||!s.anchor)throw Error('Invalid directly read word clock');
  end=s.toFrame;
 }
 return makeScene2D(function*(view){
  view.fill(P.background);
  const m=c.role.startsWith('appearance-')?guidedTeachingModel(c.role as GuidedTeachingRole):focusAnalysisModel(c.role as FocusAnalysisRole);
  view.add(m.node);
  view.add(heading('관찰과 검사',c.title,'표시된 결과 → 구별할 조건 → 다음 질문','게임 렌더링 역사 · 마지막 픽셀'));
  const thread=useThread(),start=thread.fixed;
  while(true){
   const f=Math.round((thread.fixed-start)*60);if(f>=c.frames)break;
   let p=0;
   for(const s of c.stages){if(f<s.fromFrame)break;if(f>=s.toFrame)p=s.progressTo;else{p=s.progressFrom+(s.progressTo-s.progressFrom)*(f-s.fromFrame)/(s.toFrame-s.fromFrame);break;}}
   m.reset(p);yield;
  }
 });
}
