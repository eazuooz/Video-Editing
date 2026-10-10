import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';
import {responseAfterUpdates,wallBlocks,weightedIrradiance} from './ddgi-math-v1';

export function ddgiModel(){
 const node=new Node({}),ray=createSignal(0),camera=createSignal(0),compare=createSignal(0),visibility=createSignal(0),dense=createSignal(0),change=createSignal(0),updates=createSignal(0);
 const q:V3=[-70,-45,20],probes:V3[]=[[-180,-45,85],[180,-45,85]],values=[2,10];
 const label=(text:string|(()=>string),x:number,y:number,size=28,fill:string=P.ink)=>new Txt({text,x,y,fontSize:size,fontFamily:P.font,fill,textAlign:'center'});
 const add=(...nodes:Node[])=>nodes.forEach(n=>node.add(n));
 const corrected=()=>weightedIrradiance(values,probes.map(p=>wallBlocks(q,p)?1-visibility():1))!;
 const panel=(origin:[number,number],aware:boolean)=>{
  const layer=new Node({}),s=depthSpace(()=>28,origin,.93);
  layer.add(s.box(0,0,-12,510,330,12,P.surfaceTop));
  // Draw the far probe, then wall, then foreground receiver/probe. This explicit
  // layer ordering creates occlusion instead of drawing through solid geometry.
  const probe=(p:V3,color:string)=>new Node({children:[s.box(p[0],p[1],p[2],30,30,25,color),s.label(color===P.orange?'B':'A',p[0],p[1],p[2]+55,28,color)]});
  layer.add(probe(probes[1],P.orange));
  for(let i=0;i<2;i++){
   const color=i===0?P.teal:P.orange;
   const blocked=wallBlocks(q,probes[i]);
   const progress=()=>ray()*(aware&&blocked?1-visibility():1);
   // Rays here visualize sample influence at the receiver, not a claim that
   // production DDGI performs exact shadow rays on every probe lookup.
   layer.add(new Line({points:[s.point(...probes[i]),s.point(...q)],stroke:color,lineWidth:4,lineDash:blocked?[8,6]:[],endArrow:true,end:progress,opacity:()=>aware&&blocked?1-.7*visibility():1}));
  }
  layer.add(s.box(0,0,0,22,300,160,P.surfaceFront));
  layer.add(probe(probes[0],P.teal));
  layer.add(s.box(q[0],q[1],0,80,75,20,P.teal));
  const patch=s.polygon(()=>[[q[0]-40,q[1]-37,21],[q[0]+40,q[1]-37,21],[q[0]+40,q[1]+37,21],[q[0]-40,q[1]+37,21]],P.orange);
  patch.opacity(()=>aware?(corrected()-2)/8:.5);layer.add(patch);
  layer.add(s.label('수광점',q[0],q[1]+110,0,26));
  layer.add(label(aware?'가림에 따라 기여 감소':'가림 없이 같은 비중',origin[0],origin[1]-240,31,aware?P.teal:P.orange));
  layer.add(label(()=>`E = ${aware?corrected().toFixed(2):'6.00'}`,origin[0],origin[1]+215,34,aware?P.teal:P.orange));
  layer.add(label(aware?'wA=1 · wB: 1 → 0':'(2 + 10) / 2',origin[0],origin[1]+255,26,P.muted));
  return{layer,s};
 };
 const first=panel([-420,60],false),second=panel([420,60],true);
 add(first.layer);second.layer.opacity(()=>compare());add(second.layer);
 // A camera icon moves along a separate path; the world-space probe positions
 // remain fixed. No implication that screen-space data is being reused.
 const cameraLayer=new Node({opacity:()=>camera()});
 const c=depthSpace(()=>28,[-420,60],.93);
 cameraLayer.add(c.box(()=>-220+camera()*330,230,0,50,45,36,P.green));
 cameraLayer.add(c.label('카메라는 이동 · 프로브는 같은 공간',0,380,0,25,P.green));add(cameraLayer);
 const grid=new Node({opacity:()=>dense()});
 const g=depthSpace(()=>26,[430,40],.75);
 for(let z=0;z<2;z++)for(let y=0;y<2;y++)for(let x=0;x<4;x++){
  grid.add(new Circle({position:g.point(-210+x*140,-100+y*200,z*140),size:18,fill:P.teal,stroke:P.ink,lineWidth:1}));
  if(x<3)grid.add(new Line({points:[g.point(-210+x*140,-100+y*200,z*140),g.point(-70+x*140,-100+y*200,z*140)],stroke:P.line,lineWidth:1}));
 }
 grid.add(label('간격 ↓ · 프로브 수/저장/갱신 ↑',430,265,29,P.teal));
 grid.add(label('격자 그림은 규모 예 · 시간 측정값 아님',430,307,23,P.muted));add(grid);
 const temporal=new Node({opacity:()=>change(),x:435,y:-40});
 const updateCount=()=>Math.floor(updates()+1e-6);
 const response=()=>responseAfterUpdates(2,10,.9,updateCount());
 temporal.add(label('조명이 바뀐 뒤 캐시가 따라오는 과정',0,-180,29,P.yellow));
 const bars=depthSpace(()=>18,[0,0],1);
 temporal.add(bars.box(-120,0,0,110,150,110,P.orange));
 temporal.add(bars.box(140,0,0,110,150,()=>response()*11,P.teal));
 temporal.add(label('새 표본: 10',-120,150,28,P.orange));
 temporal.add(label(()=>`캐시: ${response().toFixed(2)}`,140,150,28,P.teal));
 temporal.add(label(()=>`Enew = 0.9 Eold + 0.1 Esample · 갱신 ${updateCount()}회`,0,220,23));
 temporal.add(label('0.9는 독립 예 · 실제 시간/기본값으로 일반화하지 않음',0,260,22,P.muted));add(temporal);
 add(label('두 프로브 원리 예 · 실제 DDGI는 거리 모멘트·법선·바이어스·8점 보간을 사용',0,350,23,P.muted));
 const controls={ray,camera,compare,visibility,dense,change,updates};
 const poses:Record<string,number>[]=[
  {ray:0},{ray:1},
  {ray:1,camera:0},{ray:1,camera:1},
  {ray:1,compare:1,visibility:0},{ray:1,compare:1,visibility:1},
  {ray:1,dense:0},{ray:1,dense:1},
  {ray:1,change:1,updates:0},{ray:1,change:1,updates:24},
 ];
 return{node,controls,poses,reset(p:Record<string,number>){for(const[k,s]of Object.entries(controls))s(p[k]??0);},*transition(p:Record<string,number>,seconds:number){yield*all(...Object.entries(controls).map(([k,s])=>s(p[k]??0,seconds,linear)));}};
}
