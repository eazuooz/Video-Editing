import {makeScene2D,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import storyboard from '../../../../../projects/game-lighting-history-01/production/animation-storyboard-v4.json';
import {buildModel,ModelKind,Pose} from '../final/black-models-v2';
import data from './data.json';

export function explanationAssetScene(id:string){return makeScene2D(function*(view){
 const timing=data.chapters.find(c=>c.id===id);
 if(!timing||data.scope!=='independent-explanation-assets-only'||!data.all26VoiceWindowsCompared||data.paragraphs!==108)throw new Error('Speech-timed asset input missing');
 const chapter=storyboard.scenes.find(s=>s.id===id);
 if(!chapter)throw new Error('Independent scene not found');
 const byKey=new Map(chapter.paragraphs.map(p=>[p.key,p]));
 const keys=Array.from(new Set(chapter.paragraphs.map(p=>p.model)))as ModelKind[];
 const models=new Map(keys.map(k=>[k,buildModel(k)]));
 const title=createSignal(''),focus=createSignal(''),equation=createSignal(''),limit=createSignal('');
 view.fill(P.background);
 view.add(heading(`${id} · 1편`,chapter.title,'','게임 렌더링의 역사'));
 for(const [kind,model]of models){model.node.opacity(0);model.node.scale(kind==='volume'?.74:.88);model.node.y(kind==='volume'?5:38);view.add(model.node);}
 view.add(<Txt text={focus} y={-335} fontFamily={P.font} fontSize={35} fontWeight={600} fill={P.blue}/>);
 view.add(<Txt text={equation} y={-285} fontFamily={P.mono} fontSize={29} fill={P.ink}/>);
 view.add(<Txt text={limit} y={337} fontFamily={P.font} fontSize={24} fill={P.muted}/>);
 // Captions are added once to the final clean/native composition, using current
 // measured whole-episode KO cues at (960,970). No duplicate baked captions here.
 let previous:ReturnType<typeof buildModel>|null=null,total=0;
 for(const block of timing.blocks){
  const action=byKey.get(block.paragraphKey);
  if(!action||!Number.isInteger(block.frames)||block.frames<=0||block.pcmEndFrame-block.pcmStartFrame!==block.frames)throw new Error('Invalid measured explanation block');
  const current=models.get(action.model as ModelKind)!;
  current.reset(action.from as unknown as Pose);focus(action.focus);equation(action.expression);limit(action.limit);
  const duration=block.frames/60;
  const steps=block.actionSteps;
  if(!steps.length)throw new Error('Reviewed speech-triggered action timing is missing');
  let lastEnd=0;
  for(const step of steps){
   if(!Number.isInteger(step.actionStartFrame)||!Number.isInteger(step.actionDurationFrames)||step.actionStartFrame<lastEnd||step.actionDurationFrames<1||step.actionStartFrame+step.actionDurationFrames>block.frames||!step.spokenTrigger||!Object.keys(step.to).length||Object.values(step.to).some(v=>!Number.isFinite(v)))throw new Error('Invalid or overlapping speech action step');
   lastEnd=step.actionStartFrame+step.actionDurationFrames;
  }
  const reveal=previous!==current?Math.min(.3,steps[0].actionStartFrame/60):0;
  if(reveal){if(previous)yield*all(previous.node.opacity(0,reveal),current.node.opacity(1,reveal));else yield*current.node.opacity(1,reveal);}
  else {if(previous&&previous!==current)previous.node.opacity(0);current.node.opacity(1);}
  // The reviewed word trigger controls the motion onset. Do not move an angle
  // before the narrator reaches the angle comparison, or stretch a20s lookdev.
  let elapsed=reveal;
  for(const step of steps){
   yield*waitFor(Math.max(0,step.actionStartFrame/60-elapsed));
   yield*current.transition(step.to as unknown as Pose,step.actionDurationFrames/60);
   elapsed=(step.actionStartFrame+step.actionDurationFrames)/60;
  }
  yield*waitFor(Math.max(0,duration-elapsed));
  previous=current;total+=block.frames;
 }
 if(total!==timing.frames)throw new Error('Explanation frame total drift');
});}
