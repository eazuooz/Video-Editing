import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';
import {commonInterval,rayPoint,slabIntervals,triangleHit} from './bvh-math-v1';

// Original, computed educational geometry. This is explanation time, never
// existing-game footage. Final word alignment and all-pixel approval are separate.
export function bvhModel(){
 const node=new Node({});
 const t=createSignal(0),shift=createSignal(0),bounds=createSignal(0),rails=createSignal(0),hierarchy=createSignal(0),miss=createSignal(0),query=createSignal(0),coarse=createSignal(0),cost=createSignal(0);
 const w=depthSpace(()=>26,[-455,80],1),r=depthSpace(()=>0,[490,-5],1);
 const low=():V3=>[2,3,4+shift()],high=():V3=>[6,5,7+shift()/2];
 const intervals=()=>slabIntervals([0,0,0],[1,1,1],low(),high());
 const common=()=>commonInterval(intervals());
 const xyz=(p:V3):V3=>p.map(v=>(v-4)*55) as V3;
 const add=(...n:Node[])=>n.forEach(x=>node.add(x));
 const label=(s:string|(()=>string),x:number,y:number,size=27,color:string=P.ink)=>new Txt({text:s,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const edge=(a:()=>V3,b:()=>V3,color:string|(()=>string),alpha:()=>number=()=>1)=>new Line({points:()=>[w.point(...xyz(a())),w.point(...xyz(b()))],stroke:color,lineWidth:3,opacity:alpha});
 // A translucent projected solid plus all12 true XYZ edges; no drop-shadow card.
 const box=new Node({opacity:()=>bounds()});
 box.add(w.polygon(()=>{const a=xyz(low()),b=xyz(high());return[[a[0],a[1],b[2]],[b[0],a[1],b[2]],[b[0],b[1],b[2]],[a[0],b[1],b[2]]];},'#34454b66'));
 box.add(w.polygon(()=>{const a=xyz(low()),b=xyz(high());return[[a[0],b[1],a[2]],[b[0],b[1],a[2]],[b[0],b[1],b[2]],[a[0],b[1],b[2]]];},'#24323988'));
 box.add(w.polygon(()=>{const a=xyz(low()),b=xyz(high());return[[b[0],a[1],a[2]],[b[0],b[1],a[2]],[b[0],b[1],b[2]],[b[0],a[1],b[2]]];},'#16202699'));
 const corner=(i:number):V3=>low().map((v,a)=>(i>>a)&1?high()[a]:v) as V3;
 for(let i=0;i<8;i++)for(let axis=0;axis<3;axis++)if(!(i&(1<<axis)))box.add(edge(()=>corner(i),()=>corner(i|(1<<axis)),()=>common().hit?P.teal:P.red));
 add(box);
 // Triangle motion stays within the original conservative box. Its actual
 // intersection changes from a hit to a miss while the box still passes.
 const localZ=(z:number)=>low()[2]+(z-4)/3*(high()[2]-low()[2]);
 const triangle=():V3[]=>[[2.2,4.5-.5*miss(),localZ(4.2+1.8*miss())],[5.8,4.5-.5*miss(),localZ(4.2+1.8*miss())],[4,4.5-.5*miss(),localZ(6.8)]];
 const exactTriangle=()=>{const [a,b,c]=triangle();return triangleHit([0,0,0],[1,1,1],a,b,c);};
 const tri=w.polygon(()=>triangle().map(xyz),'#62583d99',P.yellow);tri.opacity(()=>bounds());add(tri);
 const triangleResult=label(()=>exactTriangle()?`삼각형도 교차: t=${exactTriangle()!.t.toFixed(2)}`:'상자 통과 · 이 삼각형은 빗나감',490,60,32,P.yellow);triangleResult.opacity(()=>miss());add(triangleResult);
 const ray=new Line({points:()=>[w.point(...xyz([0,0,0])),w.point(...xyz(rayPoint([0,0,0],[1,1,1],9)))],stroke:P.teal,lineWidth:5,endArrow:true,arrowSize:16,end:()=>Math.min(1,t()/9)});add(ray);
 add(new Circle({position:()=>w.point(...xyz(rayPoint([0,0,0],[1,1,1],t()))),size:22,fill:P.orange,stroke:P.ink,lineWidth:2}));
 const overlap=new Line({points:()=>[w.point(...xyz([common().enter,common().enter,common().enter])),w.point(...xyz([common().exit,common().exit,common().exit]))],stroke:P.yellow,lineWidth:10,opacity:()=>bounds()*Number(common().hit),lineCap:'round'});add(overlap);
 add(label(()=>`p(t) = (0,0,0) + t(1,1,1)    t=${t().toFixed(1)}`,-455,270,27));
 add(label('t는 매개변수 · 단위 방향이 아니므로 미터가 아님',-455,308,23,P.muted));
 const intervalLayer=new Node({opacity:()=>rails()});
 for(let axis=0;axis<3;axis++){
  const color=[P.axisX,P.axisY,P.axisZ][axis],y=-300+axis*280;
  const p=()=>intervals()[axis];
  intervalLayer.add(r.box(0,y,0,470,50,12,P.surfaceSide));
  // Both endpoints and all projected faces follow the computed interval.
  // The z interval contracts from length3 to length1 in the rejection example.
  const x0=()=>-220+p()[0]*47,x1=()=>-220+p()[1]*47;
  intervalLayer.add(r.polygon(()=>[[x0(),y+22,12],[x1(),y+22,12],[x1(),y+22,32],[x0(),y+22,32]],color));
  intervalLayer.add(r.polygon(()=>[[x1(),y-22,12],[x1(),y+22,12],[x1(),y+22,32],[x1(),y-22,32]],color));
  intervalLayer.add(r.polygon(()=>[[x0(),y-22,32],[x1(),y-22,32],[x1(),y+22,32],[x0(),y+22,32]],color));
  intervalLayer.add(label(()=>`${['x','y','z'][axis]} : [${p()[0].toFixed(1)}, ${p()[1].toFixed(1)}]`,490,r.point(0,y,0)[1]-72,28,color));
  for(let k=0;k<=10;k++)intervalLayer.add(r.label(String(k),-220+k*47,y+41,0,19,P.muted));
 }
 intervalLayer.add(label(()=>common().hit?`공통 t ∈ [${common().enter.toFixed(1)}, ${common().exit.toFixed(1)}]`:`공통 구간 없음: ${common().enter.toFixed(1)} > ${common().exit.toFixed(1)}`,490,265,34, P.yellow));
 add(intervalLayer);
 const tree=new Node({opacity:()=>hierarchy(),x:490,y:15});
 const treeBox=(x:number,y:number,c:string)=>{const s=depthSpace(()=>20,[x,y],.72);return s.box(0,0,0,140,70,40,c);};
 tree.add([new Line({points:[[-210,-190],[-210,-95],[-330,-95],[-330,-20]],stroke:P.teal,lineWidth:4}),new Line({points:[[-210,-95],[-50,-95],[-50,-20]],stroke:P.red,lineWidth:4})]);
 tree.add([treeBox(-210,-190,P.surfaceTop),treeBox(-330,-20,P.blueLight),treeBox(-50,-20,'#503239')]);
 tree.add([new Txt({text:'부모 상자',x:-210,y:-245,fill:P.ink,fontFamily:P.font,fontSize:27}),new Txt({text:'방문',x:-330,y:55,fill:P.teal,fontFamily:P.font,fontSize:30}),new Txt({text:'하위 전체 건너뜀',x:-50,y:55,fill:P.red,fontFamily:P.font,fontSize:26})]);
 tree.add([new Line({points:[[-50,65],[-50,105],[50,105]],stroke:P.red,lineWidth:3,lineDash:[9,7]}),new Txt({text:'작은 상자 · 삼각형',x:80,y:140,fill:P.muted,fontFamily:P.font,fontSize:24})]);add(tree);
 const queries=new Node({opacity:()=>query(),x:500,y:-75});
 const qProgress=()=>Math.max(0,Math.min(1,(query()-.3)/.7));
 for(const [i,title,color] of [[0,'closest-hit',P.teal],[1,'any-hit',P.orange]] as const){
  queries.add(new Txt({text:title,x:0,y:i*220-95,fill:color,fontFamily:P.mono,fontSize:31}));
  queries.add(new Line({points:[[-240,i*220], [240,i*220]],stroke:P.line,lineWidth:3,endArrow:true}));
  for(const [tHit,labelT] of [[3,'3'],[7,'7']] as const)queries.add([new Circle({x:-240+tHit*50,y:i*220,size:24,fill:color,opacity:()=>tHit===3?qProgress():1-.7*qProgress()}),new Txt({text:labelT,x:-240+tHit*50,y:i*220+35,fill:P.ink,fontSize:25,fontFamily:P.mono})]);
  queries.add(new Line({points:()=>[[-240,i*220-22],[-240+(i===0?7-4*qProgress():3)*50,i*220-22]],stroke:color,lineWidth:8,end:()=>i===0?1:qProgress()}));
  queries.add(new Txt({text:()=>i===0?`검색 상한 tMax=${(7-4*qProgress()).toFixed(1)}`:qProgress()>.98?'불투명 가림 3 확인 후 종료':'광원 전에 불투명 가림 검사',x:0,y:i*220+80,fontSize:25,fontFamily:P.font,fill:P.ink}));
 }
 queries.add(new Txt({text:'독립 불투명 예 · 광원 tMax=9 · 알파/필터 조건 별도',y:350,fontSize:21,fontFamily:P.font,fill:P.muted}));add(queries);
 const budget=new Node({opacity:()=>cost(),x:450,y:80});
 for(const [i,title,h,c] of [[0,'구조 갱신',90,P.green],[1,'교차 검사',140,P.teal],[2,'재질 셰이딩',110,P.orange]] as const){const b=depthSpace(()=>24,[-240+i*240,25],.8);budget.add([b.box(0,0,0,140,120,h,c),b.label(title,0,135,0,25)]);}
 budget.add(new Txt({text:'세로 크기는 개념 예 · 실제 성능 측정값 아님',y:240,fill:P.muted,fontFamily:P.font,fontSize:23}));add(budget);
 const loose=new Node({opacity:()=>coarse()});
 // This looser conservative box still contains the tight box, but its
 // projected lower edges stay above the ray equation and parameter warning.
 const looseCorner=(i:number):V3=>[i&1?190:-210,i&2?130:-130,i&4?215:-40];
 for(let i=0;i<8;i++)for(let a=0;a<3;a++)if(!(i&(1<<a)))loose.add(new Line({points:()=>[w.point(...looseCorner(i)),w.point(...looseCorner(i|(1<<a)))],stroke:P.muted,lineWidth:2,lineDash:[8,5]}));
 loose.add(label('성긴 경계: 더 많은 후보',490,40,30,P.ink));add(loose);
 const controls={t,shift,bounds,rails,hierarchy,miss,query,coarse,cost};
 const poses:Record<string,number>[]=[
  {t:0,bounds:0},{t:8,bounds:1},
  {t:9,bounds:1,hierarchy:1},{t:9,bounds:1,rails:1},
  {t:9,bounds:1,rails:1,shift:0},{t:9,bounds:1,rails:1,shift:4},
  {t:9,bounds:1,miss:1},{t:9,bounds:1,query:1},
  {t:9,bounds:1,coarse:1},{t:9,bounds:1,cost:1},
 ];
 return{node,controls,poses,reset(p:Record<string,number>){for(const[k,s]of Object.entries(controls))s(p[k]??0);},*transition(p:Record<string,number>,seconds:number){yield*all(...Object.entries(controls).map(([k,s])=>s(p[k]??0,seconds,linear)));}};
}
