import {makeScene2D} from '@motion-canvas/2d';
import {useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {part1TransferModel,Part1TransferRole} from './part1-transfer-model-v225';
import {part1HistoryContract} from './part1-history-contract-v225';
import {part1ObservationContract,Part1ObservationRole} from './part1-observation-contract-v225';

export type Part1SpatialRole=Part1TransferRole|'history-silhouette'|'history-thin-blade'|Part1ObservationRole;
export interface Part1ReviewedClock {
 id:string;role:Part1SpatialRole;title:string;frames:number;
 sourceSha256:string;boundSourceSha256:string;sourceSampleRange:[number,number];
 wholeAndContextCompared:boolean;
 stages:{fromFrame:number;toFrame:number;progressFrom:number;progressTo:number;anchor:string}[];
}

// Only a clock bound to the current complete speech may instantiate this scene.
// Explanatory excerpts remain explanation time; they never extend a game loop.
export function part1ReviewedSourceScene(c:Part1ReviewedClock){
 if(!c.wholeAndContextCompared||c.sourceSha256!==c.boundSourceSha256||!Number.isInteger(c.frames)||c.frames<=0||c.sourceSampleRange[1]<=c.sourceSampleRange[0])throw Error('Current complete speech and exact sample binding required');
 let end=0;
 for(const s of c.stages){
  if(!Number.isInteger(s.fromFrame)||!Number.isInteger(s.toFrame)||s.fromFrame<end||s.toFrame<=s.fromFrame||s.toFrame>c.frames||s.progressTo<s.progressFrom||s.progressFrom<0||s.progressTo>1||!s.anchor)throw Error('Invalid directly read word clock');
  end=s.toFrame;
 }
 return makeScene2D(function*(view){
  view.fill(P.background);
  const transfer=['horizon-comparison-before','outer-comparison-before','cyber-comparison-before','fortnite-comparison-before','four-game-transfer-conclusion'].includes(c.role);
  const m=transfer?part1TransferModel(c.role as Part1TransferRole):c.role.startsWith('history-')?part1HistoryContract(c.role==='history-silhouette'?'silhouette':'thin-blade'):part1ObservationContract(c.role as Part1ObservationRole);
  view.add(m.node);
  if(transfer)view.add(heading('자료의 역할',c.title,'같은 기준을 유지하며 입력과 결과를 구별','게임 렌더링 역사 · 그림자 / 복원 / 모바일'));
  const thread=useThread(),start=thread.fixed;
  while(true){
   const f=Math.round((thread.fixed-start)*60);if(f>=c.frames)break;
   let p=0;
   for(const s of c.stages){if(f<s.fromFrame)break;if(f>=s.toFrame)p=s.progressTo;else{p=s.progressFrom+(s.progressTo-s.progressFrom)*(f-s.fromFrame)/(s.toFrame-s.fromFrame);break;}}
   m.reset(p);yield;
  }
 });
}
