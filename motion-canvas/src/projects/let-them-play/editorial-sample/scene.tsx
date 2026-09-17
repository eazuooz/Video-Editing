import {makeScene2D,Node,Txt,Line,Rect,Circle} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {OpeningWorld} from './world';

const smooth=(t:number,a:number,b:number)=>{const p=Math.max(0,Math.min(1,(t-a)/(b-a)));return p*p*(3-2*p);};
const blend=(a:number,b:number,t:number)=>a+(b-a)*t;
export default makeScene2D(function*(view){
 view.fill(P.background);
 const t=createSignal(0),introOut=()=>1-smooth(t(),18.7,19.1),focus=()=>smooth(t(),9,11.4);
 const editorial=new Node({opacity:()=>smooth(t(),0,.5)*introOut()});view.add(editorial);
 // Editorial asymmetry: large words on the left, one unboxed visual on the right.
 editorial.add(<>
  <Txt x={-852} y={-394} offset={[-1,0]} text={'카메라와 시선 설계'} fill={P.blue} fontFamily={P.font} fontSize={30} fontWeight={600}/>
  <Txt x={-856} y={-283} offset={[-1,0]} text={'넓은 화면,\n분명한 첫 시선.'} fontFamily={P.font} fontSize={62} fontWeight={700} lineHeight={86} fill={P.ink}/>
  <Line points={[[-850,-150],[-782,-150]]} stroke={P.blue} lineWidth={5}/>
 </>);
 const words=['크기','대비','여백'],notes=['먼저 보이는 크기','구분되는 명암','시선이 머물 공간'];
 words.forEach((word,i)=>{
  const on=()=>smooth(t(),9+i*1.7,10+i*1.7);
  editorial.add(<>
   <Circle x={-839} y={-50+i*100} size={10} fill={()=>on()>.5?P.blue:P.line}/>
   <Txt x={-807} y={-50+i*100} offset={[-1,0]} text={word} fontFamily={P.font} fontWeight={600} fontSize={36} fill={()=>on()>.5?P.blue:P.ink}/>
   <Txt x={-688} y={-47+i*100} offset={[-1,0]} text={notes[i]} fontFamily={P.font} fontSize={27} fill={P.muted}/>
  </>);
 });
 const world=new OpeningWorld({x:322,y:136,scale:()=>blend(.98,1.02,smooth(t(),0,19))});
 editorial.add(world);world.focus(focus);world.clock(t);world.annotations(()=>smooth(t(),13,15));
 // Live, editable type. No labels baked into a raster illustration.
 const marker=new Node({x:631,y:-168,opacity:()=>smooth(t(),11.1,12)});editorial.add(marker);
 marker.add(<>
  <Line points={[[0,14],[0,51],[-35,79]]} stroke={P.blue} lineWidth={2}/>
  <Circle x={-35} y={79} size={7} fill={P.blue}/>
  <Rect y={-14} width={216} height={53} fill={P.background}/>
  <Txt y={-14} text={'첫 관심 대상'} fontFamily={P.font} fontSize={29} fontWeight={600} fill={P.blue}/>
 </>);
 editorial.add(<>
  <Txt x={-852} y={334} offset={[-1,0]} text={()=>t()<9?'모두 강조하면':'강조할 하나를 정하고,'} fontFamily={P.font} fontSize={31} fill={P.ink}/>
  <Txt x={-852} y={382} offset={[-1,0]} text={()=>t()<9?'먼저 볼 곳이 흐려집니다.':'나머지는 한 걸음 물러나게.'} fontFamily={P.font} fontSize={31} fill={()=>t()<9?P.muted:P.blue} fontWeight={600}/>
 </>);
 // Side-by-side comparison uses exactly the same world twice, with no camera,
 // target-count or terrain changes. This makes contrast the sole variable.
 // Sequential fades avoid ghosted overlapping type during the transition.
 const comparison=new Node({opacity:()=>smooth(t(),19.1,19.5)});view.add(comparison);
 comparison.add(<>
  <Txt x={-852} y={-399} offset={[-1,0]} text={'같은 장면, 다른 시선의 순서.'} fontFamily={P.font} fontSize={59} fontWeight={700} fill={P.ink}/>
  <Txt x={-851} y={-318} offset={[-1,0]} text={'지형과 대상은 그대로 · 강조만 바꿔봅니다'} fontFamily={P.font} fontSize={29} fill={P.muted}/>
  <Line points={[[0,-217],[0,294]]} stroke={P.line} lineWidth={1}/>
 </>);
 const left=new OpeningWorld({x:-440,y:110,scale:.75}),right=new OpeningWorld({x:440,y:110,scale:.75});
 comparison.add(left);comparison.add(right);left.focus(0);right.focus(()=>smooth(t(),23,25));left.clock(t);right.clock(t);
 for(const [i,x] of [-440,440].entries()){
  comparison.add(<>
   <Line points={[[x-390,-215],[x-342,-215]]} stroke={i?P.blue:P.ink} lineWidth={4}/>
   <Txt x={x-315} y={-215} offset={[-1,0]} text={i?'첫 대상에 집중':'강조가 분산된 화면'} fontFamily={P.font} fontSize={34} fontWeight={600} fill={i?P.blue:P.ink}/>
  </>);
 }
 const takeaway=new Node({y:395,opacity:()=>smooth(t(),29.5,30.5)});comparison.add(takeaway);
 takeaway.add(<>
  <Line points={[[-500,-49],[500,-49]]} stroke={P.line} lineWidth={1}/>
  <Txt y={0} text={'강조하지 않을 곳도, 디자인합니다.'} fontFamily={P.font} fontWeight={600} fontSize={41} fill={P.ink}/>
  <Line points={[[91,29],[512,29]]} stroke={P.yellow} lineWidth={8} opacity={.75}/>
 </>);
 // End on the last occupied frame; avoid floating point rounding to 2383.
 yield* tween(2381/60,p=>t(p*39.7));
});
