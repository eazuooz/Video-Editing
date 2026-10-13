import {Circle,Line,Node,Rect,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';

// One ray, with an explicitly educational linear depth convention.
// This is explanation time and never an engine/gameplay quota substitute.
export default makeScene2D(function*(view){
 view.fill(P.background);
 const yaw=createSignal(21),casterX=createSignal(-250),phase=createSignal(0),ray=createSignal(0),record=createSignal(0),lookup=createSignal(0);
 const space=depthSpace(yaw,[0,85],1.05);
 const lamp:V3=[-420,-130,150],sample:V3=[-95,50,13],receiverDepth=.8;
 function firstHit():{point:V3;depth:number;blocked:boolean}{
  const low=[casterX()-50,-55,12],high=[casterX()+50,15,117];let enter=0,leave=1;
  for(let a=0;a<3;a++){
   const d=sample[a]-lamp[a],lo=(low[a]-lamp[a])/d,hi=(high[a]-lamp[a])/d;
   enter=Math.max(enter,Math.min(lo,hi));leave=Math.min(leave,Math.max(lo,hi));
  }
  const blocked=enter<=leave&&enter>=0&&enter<1,t=blocked?enter:1;
  return {point:lamp.map((v,a)=>v+(sample[a]-v)*t) as V3,depth:t*receiverDepth,blocked};
 }
 view.add(heading('09 · 1편','같은 점을, 광원의 깊이로 비교한다','한 광선의 교육용 선형 깊이 · 최종 음성 전 무음 시안','게임 렌더링의 역사'));
 view.add(space.box(-255,0,0,430,320,12,'#dfe8df'));
 view.add(space.box(400,-65,0,285,270,12,'#e5eaf1'));
 view.add(space.polygon(()=>[[305,-145,13],[495,-145,13],[495,15,13],[305,15,13]],'#f3f5f7'));
 for(let i=0;i<=3;i++){
  view.add(<Line points={()=>[space.point(305+i*190/3,-145,14),space.point(305+i*190/3,15,14)]} stroke={P.line} lineWidth={2}/>);
  view.add(<Line points={()=>[space.point(305,-145+i*160/3,14),space.point(495,-145+i*160/3,14)]} stroke={P.line} lineWidth={2}/>);
 }
 const cell=space.polygon(()=>[[368,-92,15],[432,-92,15],[432,-38,15],[368,-38,15]],P.yellow);
 cell.opacity(record);view.add(cell);
 view.add(space.path(()=>[lamp,firstHit().point],P.yellow,ray));
 const behind=space.path(()=>[firstHit().point,sample],P.red,1,[12,8]);
 behind.opacity(()=>phase()>=2&&firstHit().blocked?1:0);view.add(behind);
 view.add(space.box(casterX,-20,12,100,70,105,'#7791b5'));
 view.add(<Circle position={()=>space.point(...sample)} size={27} fill={()=>phase()>=2?(firstHit().blocked?P.red:P.green):'#ffffff'} stroke={P.ink} lineWidth={2}/>);
 view.add(space.label('검사할 점',sample[0]+35,sample[1]+50,13,26));
 view.add(space.label('깊이 0.80',sample[0]+35,sample[1]+100,13,25));
 const correspondence=space.path(()=>[sample,[70,0,80],[400,-65,25]],P.blue,lookup);
 correspondence.opacity(lookup);view.add(correspondence);
 view.add(<Circle position={()=>space.point(...lamp)} size={40} fill={P.yellow} stroke={'#a48825'} lineWidth={3}/>);
 view.add(space.label('광원',lamp[0]+60,lamp[1],lamp[2],27));
 view.add(space.label('게임 공간',-270,190,0,29));
 view.add(space.label('광원 깊이 맵',400,115,0,29));
 view.add(<Txt text={()=>firstHit().depth.toFixed(2)} position={()=>space.point(400,-65,25)} fill={P.ink} fontFamily={P.font} fontSize={30} fontWeight={700} opacity={record}/>);
 view.add(<Txt text={()=>phase()<2?'한 표본의 첫 번째 깊이를 저장':`수신점 0.80 ${firstHit().blocked?'>':'≤'} 저장값 ${firstHit().depth.toFixed(2)} + bias 0.01`} y={315} fontFamily={P.font} fontSize={30} fill={P.muted}/>);
 const captions=[
  '광원에서 가장 먼저 보이는\n표면의 깊이를 저장합니다.',
  '카메라에 보인 점도\n같은 광원 좌표로 옮깁니다.',
  '저장한 깊이보다 뒤에 있으므로\n이 점은 광원에 가려져 있습니다.',
  '가림 물체가 이동하면 깊이도 갱신해\n새 상태에서 다시 비교합니다.',
 ];
 view.add(<Node position={[0,430]}>
  <Rect position={[8,8]} size={[1220,124]} fill={'#355344'}/>
  <Rect size={[1220,124]} fill={'#ffffff'} stroke={'#1a1a1a'} lineWidth={2}/>
  <Txt text={()=>captions[phase()]} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111111'} textAlign={'center'}/>
 </Node>);
 yield* ray(1,3,linear);yield* record(1,1,linear);yield* waitFor(2);
 phase(1);yield* all(lookup(1,4,linear),yaw(24,4,linear));yield* waitFor(2);
 phase(2);yield* waitFor(6);
 phase(3);yield* all(casterX(-430,4,linear),yaw(29,4,linear));yield* waitFor(2-1/60);
});
