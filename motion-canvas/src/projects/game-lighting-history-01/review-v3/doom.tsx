import {makeScene2D,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {buildModel,Pose} from '../final/black-models-v2';
import storyboard from '../../../../../projects/game-lighting-history-01/production/animation-storyboard-v4.json';
import data from '../explanation-assets-v1/data.json';
export default makeScene2D(function*(view){
 const chapter=storyboard.scenes.find(s=>s.id==='03')!;
 const action=chapter.paragraphs.find(p=>p.key==='03-p7')!;
 const block=data.chapters.find(c=>c.id==='03')!.blocks.find(b=>b.paragraphKey==='03-p7')!;
 const model=buildModel('sector');model.reset(action.from as Pose);
 view.fill(P.background);view.add(heading('03 · 1편',chapter.title,'','게임 렌더링의 역사'));
 model.node.scale(.88);model.node.y(38);view.add(model.node);
 view.add(<Txt text={action.focus} y={-335} fontFamily={P.font} fontSize={35} fontWeight={600} fill={P.blue}/>);
 view.add(<Txt text={action.expression} y={-285} fontFamily={P.mono} fontSize={29} fill={P.ink}/>);
 view.add(<Txt text={action.limit} y={337} fontFamily={P.font} fontSize={24} fill={P.muted}/>);
 let end=0;
 for(const s of block.actionSteps){yield*waitFor((s.actionStartFrame-end)/60);yield*model.transition(s.to as Pose,s.actionDurationFrames/60);end=s.actionStartFrame+s.actionDurationFrames;}
 yield*waitFor((959-end)/60);
});
