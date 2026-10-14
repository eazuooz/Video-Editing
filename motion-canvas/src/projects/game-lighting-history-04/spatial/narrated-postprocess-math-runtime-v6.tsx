import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {createSignal,useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {vsmModel} from './vsm-model-v2';
import {upscalingModel} from './upscaling-model-v2';
import {visibilityModel} from './visibility-model-v1';
import {mobileModel} from './mobile-model-v1';
import {pathBudgetModel} from './path-budget-model-v3';
import {reconstructionModel} from './reconstruction-model-v2';
import {megalightsModel} from './megalights-model-v1';
import {transparencyModel} from './transparency-model-v3';
import {dlssLatestModel} from './dlss-latest-model-v1';
import {postprocessModel} from './postprocess-model-v4';
import {frameInspectionModel} from './frame-inspection-model-v1';
import {seriesSynthesisModel} from './series-synthesis-model-v1';
import {prerequisiteModel,PrerequisiteId} from './additive-prerequisite-model-v1';

const factories={vsm:vsmModel,upscaling:upscalingModel,visibility:visibilityModel,mobile:mobileModel,pathBudget:pathBudgetModel,reconstruction:reconstructionModel,megalights:megalightsModel,transparency:transparencyModel,dlssLatest:dlssLatestModel,postprocess:postprocessModel,frameInspection:frameInspectionModel,seriesSynthesis:seriesSynthesisModel};
export interface NarratedStage {fromFrame:number;toFrame:number;progressFrom:number;progressTo:number;anchor:string;wordTimesDirectlyReviewed:boolean}
export interface NarratedParagraph {fromFrame:number;toFrame:number;mode:number;title:string;stages:NarratedStage[]}
export interface NarratedCaption {fromFrame:number;toFrame:number;text:string}
export interface NarratedScene04 {
 id:string;model:keyof typeof factories|'prerequisite';prerequisiteId?:PrerequisiteId;
 frames:number;currentAudioSha256:string;boundAudioSha256:string;
 allWholeAndIndependentContextTextCompared:boolean;
 captionWordTimesDirectlyReviewed:boolean;renderCaptions?:boolean;paragraphs:NarratedParagraph[];cues:NarratedCaption[];
}

// Data must be measured and directly reviewed before scene creation. This is
// a prepared renderer, not an approval of silent model proofs or final pixels.
export function narratedScene04(chapter:NarratedScene04){
 if(!chapter.allWholeAndIndependentContextTextCompared||!chapter.captionWordTimesDirectlyReviewed||chapter.currentAudioSha256!==chapter.boundAudioSha256)throw Error('Current whole/context audio and word timing review required');
 if(!Number.isInteger(chapter.frames)||chapter.frames<1||!chapter.paragraphs.length||!chapter.cues.length)throw Error('Measured integer scene frames and complete captions required');
 let priorEnd=0;
 for(const cue of chapter.cues){
  if(!Number.isInteger(cue.fromFrame)||!Number.isInteger(cue.toFrame)||cue.fromFrame<priorEnd||cue.toFrame<=cue.fromFrame||cue.toFrame>chapter.frames||cue.text.split('\n').length>2)throw Error('Caption frame bounds/wrapping invalid');
  priorEnd=cue.toFrame;
 }
 let paragraphEnd=0;
 for(const paragraph of chapter.paragraphs){
  if(!Number.isInteger(paragraph.fromFrame)||!Number.isInteger(paragraph.toFrame)||paragraph.fromFrame<paragraphEnd||paragraph.toFrame<=paragraph.fromFrame||paragraph.toFrame>chapter.frames||!paragraph.stages.length)throw Error('Paragraph frame bounds invalid');
  let previous=paragraph.fromFrame;
  for(const stage of paragraph.stages){
   if(!stage.wordTimesDirectlyReviewed||!stage.anchor||!Number.isInteger(stage.fromFrame)||!Number.isInteger(stage.toFrame)||stage.fromFrame<previous||stage.toFrame<=stage.fromFrame||stage.toFrame>paragraph.toFrame||!Number.isFinite(stage.progressFrom)||!Number.isFinite(stage.progressTo)||stage.progressFrom<0||stage.progressTo>1||stage.progressTo<stage.progressFrom)throw Error('Narration motion anchor invalid');
   previous=stage.toFrame;
  }
  paragraphEnd=paragraph.toFrame;
 }
 return makeScene2D(function*(view){
  const clock=createSignal(0),m=chapter.model==='prerequisite'?null:factories[chapter.model]();
  const prerequisite=chapter.model==='prerequisite'&&chapter.prerequisiteId?prerequisiteModel(chapter.prerequisiteId):null;
  if(!m&&!prerequisite)throw Error('Independent explanation model missing');
  view.fill(P.background);view.add((m??prerequisite)!.node);
  if(prerequisite)prerequisite.node.y(-20);
  const h=heading(chapter.id,chapter.paragraphs[0].title,'같은 자료 · 계산 과정 · 결과와 한계','게임 렌더링 역사 4편');view.add(h);const title=h.children()[1] as Txt;
  const caption=()=>{const frame=Math.round(clock());return chapter.cues.find(c=>frame>=c.fromFrame&&frame<c.toFrame)?.text??'';};
  if(chapter.renderCaptions===true)view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
  function reset(mode:number,progress:number){if(m)m.reset({mode,progress});else prerequisite!.reset(progress);}
  // One integer presentation clock drives every model and caption. Nested
  // all()/join() termination previously left an extra scene-boundary frame.
  // The preserved v1 proofs remain historical; clean sources use this driver.
  const thread=useThread(),startTime=thread.fixed;
  while(true){
   const frame=Math.round((thread.fixed-startTime)*60);
   if(frame>=chapter.frames)break;
   clock(frame);
   const preceding=chapter.paragraphs.filter(p=>p.fromFrame<=frame);
   const paragraph=chapter.paragraphs.find(p=>frame>=p.fromFrame&&frame<p.toFrame)
    ??preceding[preceding.length-1]
    ??chapter.paragraphs[0];
   let progress=0;
   for(const stage of paragraph.stages){
    if(frame<stage.fromFrame)break;
    if(frame>=stage.toFrame)progress=stage.progressTo;
    else{progress=stage.progressFrom+(stage.progressTo-stage.progressFrom)*(frame-stage.fromFrame)/(stage.toFrame-stage.fromFrame);break;}
   }
   title.text(paragraph.title);reset(paragraph.mode,progress);
   yield;
  }
 });
}
