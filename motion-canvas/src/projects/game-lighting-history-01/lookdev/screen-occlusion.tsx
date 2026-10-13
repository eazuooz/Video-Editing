import {Circle,Line,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
// Toy height-field/depth comparison: explanation, not a replica SSAO shader.
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(24),phase=createSignal(0),radius=createSignal(75),amount=createSignal(0),shift=createSignal(0);
 const w=depthSpace(yaw,[0,150],1.04),p:V3=[-100,80,15];
 const q=(i:number):V3=>{const a=2*Math.PI*i/8;return [p[0]+Math.cos(a)*radius(),p[1]+Math.sin(a)*radius(),p[2]+35];};
 const valid=(i:number)=>q(i)[0]+shift()<110;
 const hit=(i:number)=>valid(i)&&q(i)[0]>=-40&&q(i)[0]<=40&&q(i)[1]>=-80&&q(i)[1]<=80;
 const count=()=>Array.from({length:8},(_,i)=>Number(valid(i))).reduce<number>((n,v)=>n+v,0);
 const A=()=>count()?1-Array.from({length:8},(_,i)=>Number(hit(i))).reduce<number>((n,v)=>n+v,0)/count():null;
 view.add(heading('10 · SSAO','화면에 남은 깊이로, 가까운 가림을 어림한다','화면 정보의 한계 · 교육용 8표본, 동일 가중 근사 · 실제 엔진 식은 다름','게임 렌더링의 역사'));
 view.add(w.box(-130,0,0,480,380,12,'#e5eaf1'));
 view.add(w.box(0,0,12,80,160,100,'#7791b5'));
 for(let i=0;i<8;i++){
  view.add(new Line({points:()=>[w.point(...p),w.point(...q(i))],stroke:()=>!valid(i)?'#a4abb0':hit(i)?P.red:P.green,lineWidth:5,endArrow:true,end:amount}));
  view.add(<Circle position={()=>w.point(...q(i))} size={18} fill={()=>!valid(i)?'#a4abb0':hit(i)?P.red:P.green} opacity={amount}/>);
 }
 view.add(<Circle position={()=>w.point(...p)} size={28} fill={P.yellow} stroke={P.ink} lineWidth={2}/>);
 const screen=depthSpace(()=>28,[600,125],.85);view.add(screen.box(0,0,0,200,250,16,'#e5eaf1'));
 for(let i=0;i<25;i++)view.add(screen.box(-80+i%5*40,-100+Math.floor(i/5)*50,16,35,45,4,i%5>=3&&Math.floor(i/5)<=2?'#7b898d':'#d9e3e7'));
 view.add(screen.label('현재 화면 깊이',0,190,0,29));
 view.add(<Txt y={268} text={()=>`유효 표본 ${count()}/8 · A = 1 − occluded/N = ${A()?.toFixed(2)??'정보 없음'} · 반경 ${Math.round(radius())}`} fontFamily={P.mono} fontSize={28} fill={P.ink}/>);
 view.add(note(()=>['표면 주변 표본을 현재 화면의 깊이와 비교하는 근사','예제의 높이 비교는 가시성 근사; 광원의 섀도 맵이 아니다','반경 확대는 더 먼 정보와 잘못된 연결·halo 문제를 함께 만든다','회색은 화면 밖/정보 없음; 보이지 않는 전체 장면을 복원하지 못한다'][phase()]));
 const cues=['에스에스에이오는 화면 깊이의 주변 표본으로\n가까운 가림을 근사합니다.','구석과 접촉 주변의 환경광을 줄여\n표면의 접촉감을 보완합니다.','반경을 크게 잡으면 범위가 넓어지지만\n노이즈와 잘못된 번짐도 다뤄야 합니다.','화면 밖과 가려진 표면을 모르므로\n광원 그림자나 전역조명의 대체물은 아닙니다.'];view.add(caption(()=>cues[phase()]));
 yield*amount(1,5,linear);yield*waitFor(1);phase(1);yield*radius(120,5,linear);yield*waitFor(1);phase(2);yield*radius(220,5,linear);yield*waitFor(1);phase(3);yield*all(shift(200,4,linear),yaw(32,4,linear));yield*waitFor(2);
});
