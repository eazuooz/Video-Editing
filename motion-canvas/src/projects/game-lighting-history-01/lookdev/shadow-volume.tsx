import {Circle,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(25),phase=createSignal(0),extend=createSignal(0),receiverY=createSignal(0);
 const w=depthSpace(yaw,[0,0],.9),lamp:V3=[-410,-70,180],receiverX=50;
 const near:V3[]=[[-190,-65,30],[-190,65,30],[-190,65,165],[-190,-65,165]];
 const far=()=>near.map(p=>p.map((v,i)=>v+(v-lamp[i])*extend()*1.3)as V3);
 function blocked(){const t=(-190-lamp[0])/(receiverX-lamp[0]),y=lamp[1]+(receiverY()-lamp[1])*t,z=lamp[2]+(25-lamp[2])*t;return Math.abs(y)<=65&&z>=30&&z<=165;}
 view.add(heading('07 · 2001 시연 / 2004 출시','실루엣 뒤에, 빛이 못 가는 공간을 만든다','교육용 평면 가림체와 닫힌 볼륨 · 실제 id 코드는 경계 면과 caps를 별도 처리','게임 렌더링의 역사'));
 view.add(w.box(-60,40,0,900,450,12,'#e5eaf1'));
 for(let i=0;i<4;i++){const j=(i+1)%4;view.add(w.polygon(()=>[near[i],near[j],far()[j],far()[i]],'#c43b3b22','#c43b3b88'));view.add(w.path(()=>[near[i],far()[i]],P.red,extend));}
 view.add(w.polygon(far,'#c43b3b18','#c43b3b88'));
 view.add(w.polygon(()=>near,'#7791b5'));
 view.add(<Circle position={()=>w.point(...lamp)} size={42} fill={P.yellow}/>);
 view.add(w.path(()=>[lamp,[-190,0,90]],P.yellow));
 // X=50 is inside the completed finite cap at X=96, unlike the rejected v1 X=250.
 view.add(<Circle position={()=>w.point(receiverX,receiverY(),25)} size={30} fill={()=>phase()<2?'white':blocked()?P.red:P.green} stroke={P.ink} lineWidth={2}/>);
 view.add(<Txt x={430} y={-40} text={'검사할 표면점'} fontFamily={P.font} fontSize={26} fill={P.ink}/>);
 view.add(w.path(()=>[[390,-120,25],[receiverX,receiverY(),25]],P.muted));
 view.add(w.label('가림체',-190,110,130,27));
 view.add(<Txt y={272} text={()=>phase()<2?'광원에서 본 경계 → 뒤쪽으로 연장':`같은 광원에 가려짐: ${blocked()?'예':'아니오'}`} fontFamily={P.font} fontSize={30} fill={P.ink}/>);
 view.add(note(()=>['물체의 윤곽과 법선맵이 바꾸는 작은 표면 방향은 구별한다','평면의 경계를 광원 반대쪽으로 늘린 단순 볼륨','화면 표본과 볼륨의 관계를 stencil로 판별하는 원리','가림 밖으로 이동하면 해당 광원의 직접 기여를 받을 수 있다'][phase()]));
 const cues=['움직이는 조명과 물체에는\n새 상태의 직접광과 그림자가 필요합니다.','섀도 볼륨은 광원에서 본 경계를\n뒤로 이어 그늘의 공간을 구성합니다.','스텐실로 화면 표본과 그 공간의 관계를 검사해\n해당 광원의 기여를 막습니다.','가림 밖에서는 그 빛을 받을 수 있지만\n반사와 색 번짐까지 해결한 것은 아닙니다.'];view.add(caption(()=>cues[phase()]));
 yield*waitFor(6);phase(1);yield*extend(1,5,linear);yield*waitFor(1);phase(2);yield*waitFor(6);phase(3);yield*all(receiverY(-160,4,linear),yaw(33,4,linear));yield*waitFor(2);
});
