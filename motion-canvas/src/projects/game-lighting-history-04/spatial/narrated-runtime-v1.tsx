import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
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
import {postprocessModel} from './postprocess-model-v3';
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
 captionWordTimesDirectlyReviewed:boolean;paragraphs:NarratedParagraph[];cues:NarratedCaption[];
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
  view.add(<Node y={430} opacity={()=>caption()?1:0}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={caption} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
  function reset(mode:number,progress:number){if(m)m.reset({mode,progress});else prerequisite!.reset(progress);}
  function* motion(){let elapsed=0;
   for(const paragraph of chapter.paragraphs){
    yield*waitFor((paragraph.fromFrame-elapsed)/60);title.text(paragraph.title);reset(paragraph.mode,0);elapsed=paragraph.fromFrame;
    for(const stage of paragraph.stages){
     yield*waitFor((stage.fromFrame-elapsed)/60);reset(paragraph.mode,stage.progressFrom);
     if(m)yield*m.transition({mode:paragraph.mode,progress:stage.progressTo},(stage.toFrame-stage.fromFrame)/60);
     else yield*prerequisite!.transition(stage.progressTo,(stage.toFrame-stage.fromFrame)/60);
     elapsed=stage.toFrame;
    }
    yield*waitFor((paragraph.toFrame-elapsed)/60);elapsed=paragraph.toFrame;
   }
   yield*waitFor((chapter.frames-elapsed)/60);
  }
  yield*all(clock(chapter.frames,chapter.frames/60,linear),motion());
 });
}
