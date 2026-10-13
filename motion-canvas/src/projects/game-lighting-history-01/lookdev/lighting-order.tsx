import {Circle,Node,Rect,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading,V3} from '../../../shared/depth-diagrams';

// Same opaque sample and two lights. Conceptual buffer/order demonstration,
// never actual-game quota or a measured universal performance comparison.
export default makeScene2D(function*(view){
 view.fill(P.background);
 const yaw=createSignal(24),stage=createSignal(0),material=createSignal(0),lightA=createSignal(0),lightB=createSignal(0),flow=createSignal(0);
 const left=depthSpace(yaw,[-460,115],.8),right=depthSpace(yaw,[450,115],.8);
 view.add(heading('09b · 1편','같은 조명을, 다른 순서로 계산한다','불투명 표본 하나 · 재질 1회와 광원 2개를 설명하는 교육용 도식','게임 렌더링의 역사'));
 view.add(<Txt x={-450} y={-200} text={'Forward'} fontFamily={P.font} fontSize={36} fontWeight={700} fill={P.ink}/>);
 view.add(<Txt x={450} y={-200} text={'Deferred'} fontFamily={P.font} fontSize={36} fontWeight={700} fill={P.ink}/>);
 const sample:V3=[-185,17.5,46];
 for(const s of [left,right]){
  view.add(s.box(-150,0,0,200,160,12,'#e5eaf1'));
  view.add(s.box(-185,-20,12,85,75,85,'#7791b5'));
  view.add(s.label('불투명 표면',-175,145,0,28));
  for(const [x,color] of [[-300,P.yellow],[10,'#e5a77a']] as [number,string][]){
   view.add(<Circle position={()=>s.point(x,-140,130)} size={34} fill={color} stroke={P.line} lineWidth={2}/>);
  }
 }
 // Right: three physically separated planes store data before lighting.
 const buffer=right.box(130,0,0,190,160,12,'#e5eaf1');view.add(buffer);
 const data=right.polygon(()=>[[45,-65,32],[215,-65,32],[215,65,32],[45,65,32]],'#d3e5d9');data.opacity(material);view.add(data);
 const normals=right.polygon(()=>[[45,-65,78],[215,-65,78],[215,65,78],[45,65,78]],'#b8cce5');normals.opacity(material);view.add(normals);
 const depth=right.polygon(()=>[[45,-65,124],[215,-65,124],[215,65,124],[45,65,124]],'#f3df9b');depth.opacity(material);view.add(depth);
 view.add(right.label('G-buffer',130,140,0,28));
 view.add(<Txt x={490} y={-120} text={'깊이 · 법선 · 재질'} fontFamily={P.font} fontSize={26} fill={P.muted} opacity={material}/>);
 const store=right.path(()=>[sample,[130,0,124]],P.blue,material);view.add(store);
 // Left: material and light evaluation remain together at the sample.
 view.add(left.path(()=>[[-300,-140,130],sample],P.yellow,lightA));
 view.add(left.path(()=>[[10,-140,130],sample],'#cf7e46',lightB));
 // Right: lighting reads the stored visible-sample data.
 view.add(right.path(()=>[[-300,-140,130],[130,0,124]],P.yellow,lightA));
 view.add(right.path(()=>[[10,-140,130],[130,0,124]],'#cf7e46',lightB));
 for(const [s,x] of [[left,-430],[right,470]] as const){
  view.add(s.box(350,35,0,120,100,12,'#dfe8df'));
  view.add(<Circle position={()=>s.point(350,35,23)} size={46} fill={()=>lightB()>.99?'#77a978':lightA()>.99?'#c5b971':'#ffffff'} stroke={P.ink} lineWidth={2}/>);
  view.add(s.label('색 출력',350,120,0,28));
  view.add(s.path(()=>[s===left?sample:[130,0,124],[350,35,23]],P.green,flow));
  view.add(<Txt x={x} y={262} text={()=>stage()<1?'표본 선택':stage()<2?'광원 A 기여 0.25':stage()<3?'0.25 + 0.35 = 0.60':'같은 입력, 같은 최종 기여'} fontFamily={P.font} fontSize={27} fill={P.muted}/>);
 }
 view.add(<Txt y={330} text={()=>stage()<1?'Forward: 재질과 조명 함께  /  Deferred: 표면 정보 먼저 저장':stage()<3?'광원은 두 경로 모두 표면의 방향·재질·가림 정보를 필요로 한다':'G-buffer 저장·대역폭 비용과 투명체·MSAA 제약은 별도 검토'} fontFamily={P.font} fontSize={25} fill={P.muted}/>);
 const captions=[
  '포워드는 표면을 처리하면서\n재질과 조명을 함께 계산합니다.',
  '디퍼드는 보이는 표면의 정보를 저장한 뒤\n광원 단계에서 그 값을 읽습니다.',
  '계산 순서가 달라도 같은 표본에는\n각 광원의 기여를 더합니다.',
  '조명 수와 재질·투명체·대역폭에 따라\n맞는 경로와 비용이 달라집니다.',
 ];
 view.add(<Node position={[0,430]}>
  <Rect position={[8,8]} size={[1340,124]} fill={'#355344'}/>
  <Rect size={[1340,124]} fill={'#ffffff'} stroke={'#1a1a1a'} lineWidth={2}/>
  <Txt text={()=>captions[stage()]} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111111'} textAlign={'center'}/>
 </Node>);
 yield* material(1,3,linear);yield* waitFor(2);
 stage(1);yield* all(lightA(1,3,linear),flow(.5,3,linear));yield* waitFor(2);
 stage(2);yield* all(lightB(1,3,linear),flow(1,3,linear));yield* waitFor(2);
 stage(3);yield* yaw(31,3,linear);yield* waitFor(2-1/60);
});
