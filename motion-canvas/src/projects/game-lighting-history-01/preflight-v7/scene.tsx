import {makeScene2D,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {buildModel} from '../final/black-models-v2';
import {DARK as P} from '../../../styles/research-dark';
import {CaptionBox} from '../../game-dev-career/preview/caption-box';
export default makeScene2D(function*(view){
 view.fill(P.background);
 view.add(<Txt text={'저장한 빛을 이동하는 물체가 읽는 과정'} y={-390} fontSize={44} fill={P.title} fontFamily={P.font}/>);
 view.add(<Txt text={'표면 표본과 공간 표본의 위치를 구별합니다'} y={-320} fontSize={31} fill={P.ink} fontFamily={P.font}/>);
 const caption=new CaptionBox({y:430,zIndex:100});view.add(caption);
 const a=buildModel('bake');a.node.scale(.88);a.node.y(0);view.add(a.node);
 a.reset({read:1,actor:-350});caption.text('움직이는 캐릭터는 벽의 같은 위치에 붙어 있지 않죠.');
 yield*waitFor(.5);yield*a.transition({actor:-150},3);yield*waitFor(.5);a.node.remove();
 const b=buildModel('normal');b.node.scale(.88);b.node.y(0);view.add(b.node);
 b.reset({probe:1,actor:250});caption.text('표면의 텍셀 격자와 공간에 놓인 표본 점은 저장 위치부터 다릅니다.');
 yield*waitFor(.5);yield*b.transition({actor:-160},3);yield*waitFor(.5);
});
