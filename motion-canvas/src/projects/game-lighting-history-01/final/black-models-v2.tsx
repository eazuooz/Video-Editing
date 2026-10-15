import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,Color,createSignal,linear,SimpleSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from './depth-space-v3';

// Original educational geometry; every output from this module is explanation.
// Native engine footage is inserted separately and is never counted twice.
export type Pose=Record<string,number>;
export type ModelKind='store'|'visibility'|'sector'|'bake'|'filter'|'tile'|'volume'|'normal'|'depth'|'cascade'|'pipeline'|'ao';
const defaults:Record<ModelKind,Pose>={
 store:{lamp:-300,saved:0,flow:0,read:0},
 visibility:{front:0,raster:0,angle:0,ray:0,blocked:0,directions:0,rayKind:0},
 sector:{actor:-330,code:0,axis:0,distance:1,lamp:-300,version:1993},
 bake:{detail:1,bake:1,transfer:0,grid:4,read:0,bounce:0,lamp:-250,material:0,actor:-350},
 filter:{u:.25,v:.5,stretch:1,mip:0,blend:0},
 tile:{bin:0,era:0,transfer:0,out:0,hidden:1,list:0,glass:0},
 volume:{lamp:-410,ray:0,extend:0,cameraInside:0,receiverY:0},
 normal:{angle:0,geometry:0,basis:1,probe:0,actor:250,direct:1},
 depth:{record:1,lookup:0,stored:.33,grid:8,bias:0,filter:0,pcf:0,search:0,moment:0,virtual:0},
 cascade:{split:0,maps:1,coverage:20,sample:-330,receive:1},
 pipeline:{path:0,stored:1,channels:0,a:0,b:0,lights:1,glass:0,feature:0},
 ao:{amount:1,radius:75,filter:0,thin:0,era:2007,direct:1,shift:0},
};
const text=(value:string|(()=>string),x=0,y=260,size=28,color:string=P.ink)=><Txt text={value} x={x} y={y} fill={color} fontFamily={P.font} fontSize={size} textAlign={'center'}/>;
const mono=(value:()=>string,x=0,y=255,size=28)=><Txt text={value} x={x} y={y} fill={P.ink} fontFamily={P.mono} fontSize={size} textAlign={'center'}/>;
const sat=(x:number)=>Math.min(1,Math.max(0,x));

export function buildModel(kind:ModelKind){
 const node=new Node({});
 const signals:Record<string,SimpleSignal<number>>={};
 for(const [key,v]of Object.entries(defaults[kind]))signals[key]=createSignal(v);
 const n=(key:string)=>{if(!signals[key])throw new Error(`Unknown ${kind} pose ${key}`);return signals[key]();};
 const w=depthSpace(()=>26,[0,75],1.02);
 const add=(...children:Node[])=>children.forEach(c=>node.add(c));
 const dot=(p:()=>V3,color:string|(()=>string|Color),size=25)=>new Circle({position:()=>w.point(...p()),size,fill:color,stroke:P.ink,lineWidth:2});
 if(kind==='store'){
  add(w.box(-410,0,0,260,280,18,'#34454b'),w.box(-410,0,18,90,80,110,'#3d6675'));
  add(dot(()=>[n('lamp'),-120,180],P.yellow,42));
  add(w.path(()=>[[n('lamp'),-120,180],[-410,35,20]],P.yellow));
  add(w.box(0,0,0,250,280,18,'#62583d'));
  for(let i=0;i<12;i++){
   const cell=w.box(-78+i%3*78,-98+Math.floor(i/3)*64,18,70,56,6,i%4===0?'#374640':'#5c573e');
   cell.opacity(()=>n('saved')>.07*i?1:.1);add(cell);
  }
  add(w.path(()=>[[-250,0,95],[-135,0,95]],P.blue,()=>n('saved')));
  add(w.box(410,0,0,260,280,18,'#30463b'));
  add(w.path(()=>[[140,0,95],[260,0,95]],P.green,()=>Math.max(n('read'),n('flow'))));
  add(w.label('표면과 광원',-410,205,0),w.label('저장 데이터',0,205,0),w.label('조회 · 갱신',410,205,0));
  add(mono(()=>`광원 위치 ${Math.round(n('lamp'))} / 저장된 격자는 광원 이동만으로 바뀌지 않는다`,0,305,26));
 }
 if(kind==='visibility'){
  const back:V3[]=[[-470,35,20],[-200,35,20],[-330,35,230]];
  const front=()=>[[-490,-60-70*n('front'),20],[-230,-60-70*n('front'),20],[-350,-60-70*n('front'),230]]as V3[];
  add(w.polygon(()=>back,'#805640'),w.polygon(front,'#3d6675'));
  const p:V3=[-330,-60,105];
  const light=():V3=>[p[0]+190*Math.sin(n('angle')*Math.PI/180),p[1],p[2]+190*Math.cos(n('angle')*Math.PI/180)];
  add(w.path(()=>[p,[p[0],p[1],p[2]+170]],P.ink),w.path(()=>[light(),p],P.yellow,()=>n('ray')));
  const occluder=w.box(-330,-60,180,110,60,20,'#40515b');occluder.opacity(()=>n('blocked'));add(occluder);
  add(dot(light,P.yellow,35));
  add(w.box(420,0,0,260,270,18,'#34454b'));
  for(let i=0;i<25;i++){
   const cell=w.box(315+i%5*50,-105+Math.floor(i/5)*50,18,44,44,5,i===12?'#3d6675':'#26343b');cell.opacity(()=>i===12?1:.3+.7*n('raster'));add(cell);
  }
  for(let i=0;i<5;i++){
   const ray=w.path(()=>[p,[p[0]+120*Math.cos(i*Math.PI/5),p[1]+90*Math.sin(i*Math.PI/5),p[2]+80]],P.blue);ray.opacity(()=>n('directions'));add(ray);
  }
  add(w.path(()=>[[-160,0,100],[265,0,100]],P.blue,()=>n('front')));
  add(w.label('겹친 삼각형',-340,200,0),w.label('화면 표본',420,200,0));
  add(mono(()=>`단위 n·l = ${Math.cos(n('angle')*Math.PI/180).toFixed(2)} / V = ${n('blocked')>.5?'0':'1'} / ${['camera','shadow','reflection'][Math.round(n('rayKind'))]}`,0,305,26));
 }
 if(kind==='sector'){
  const s=depthSpace(()=>26,[-150,50],.95);
  for(const [x,color]of [[-350,'#35483f'],[-30,'#4b5748']]as const)add(s.box(x,0,0,320,300,15,color),s.box(x,-140,15,320,14,145,color));
  for(const y of [-115,115])add(s.box(-190,y,15,14,70,145,'#3b4c46'));
  add(s.box(125,0,15,14,300,145,'#4b5748'));
  const horizontal=s.polygon(()=>[[-510,-140,15],[-190,-140,15],[-190,-140,160],[-510,-140,160]],'#35483f')as Line;
  const vertical=s.polygon(()=>[[125,-150,15],[125,150,15],[125,150,160],[125,-150,160]],'#4b5748')as Line;
  horizontal.fill(()=>Color.lerp('#35483f','#2b3c33',n('axis')));vertical.fill(()=>Color.lerp('#4b5748','#636349',n('axis')));add(horizontal);
  // The rear-wall color overlay belongs behind the person in the room.
  // Retain the right foreground wall after the person for genuine occlusion.
  add(s.actor(()=>n('actor'),40,P.green,'●',15),vertical);
  const distancePoint=new Circle({position:()=>s.point(-350+45*(n('distance')-1),80,20),size:24,fill:P.blue});add(distancePoint);
  add(s.label('구역 A: 96',-350,205,0),s.label('구역 B: 160',-30,205,0));
  add(mono(()=>`lightnum = (${n('actor')<-190?96:160} >> 4) + extra`,390,-50,30));
  add(text(()=>n('axis')>.5?'수평 벽 −1 / 수직 벽 +1':'구역 기준 밝기 → 색상표',390,25,29,P.blue));
  add(text(()=>`투영 scale 조회: ${n('distance').toFixed(1)} / 자료 버전 ${n('version')<2008.5?'1993':'2024'}`,390,105,26));
  const code=new Txt({x:390,y:180,text:'sector → shift → extra → axis → clamp',fontFamily:P.mono,fontSize:24,fill:P.green,opacity:()=>n('code')});add(code);
  const lamp=dot(()=>[n('lamp'),-110,190],P.yellow);lamp.opacity(()=>n('lamp')>-250?1:0);add(lamp);
 }
 if(kind==='bake'){
  const lamp=():V3=>[n('lamp'),-120,180];
  add(w.box(-300,0,0,410,330,12,'#3a493e'),w.box(400,0,0,330,330,12,'#34454b'));
  const initialLamp:V3=[-250,-120,180],low=[-295,-65,12],high=[-205,5,117];
  const hit=(p:V3)=>{
   let enter=0,leave=1;for(let axis=0;axis<3;axis++){const d=initialLamp[axis]-p[axis];if(Math.abs(d)<1e-8){if(p[axis]<low[axis]||p[axis]>high[axis])return false;continue;}const a=(low[axis]-p[axis])/d,b=(high[axis]-p[axis])/d;enter=Math.max(enter,Math.min(a,b));leave=Math.min(leave,Math.max(a,b));}return enter<=leave&&leave>=0&&enter<=1;
  };
  for(let i=0;i<64;i++){
   const count=()=>Math.max(4,Math.min(8,Math.round(n('grid'))));
   const at=():V3=>[-300-168+(i%8+.5)*336/count(),-160+(Math.floor(i/8)+.5)*320/count(),13];
   const quad=(side:boolean)=>{const p=at(),t=n('transfer'),X=p[0]+(400+(p[0]+300)*.82-p[0])*t,Y=p[1],dx=160/count(),dy=152/count();return side?[[X-dx,Y+dy,13],[X+dx,Y+dy,13],[X+dx,Y+dy,20],[X-dx,Y+dy,20]]as V3[]:[[X-dx,Y-dy,20],[X+dx,Y-dy,20],[X+dx,Y+dy,20],[X-dx,Y+dy,20]]as V3[];};
   const tile=w.polygon(()=>quad(false),'#5c573e','#68796f')as Line;
   tile.fill(()=>hit(at())?'#263b3e':'#5c573e');
   const active=()=>i%8<count()&&Math.floor(i/8)<count();
   tile.opacity(()=>!active()?0:n('bake')>(Math.floor(i/8)*count()+i%8)/(count()*count())?1:.1);
   const side=w.polygon(()=>quad(true),'#414934');side.opacity(()=>tile.opacity());add(side,tile);
   if(i%13===0){const ray=w.path(()=>[initialLamp,at()],P.yellow,()=>n('bake'))as Line;ray.stroke(()=>hit(at())?P.red:P.yellow);ray.opacity(()=>active()?1-n('transfer'):0);add(ray);}
  }
  add(w.box(-250,-30,12,90,70,105,'#3d6675'),dot(lamp,P.yellow,40));
  add(w.label('미리 계산하는 공간',-300,210,0),w.label('별도 조명 텍스처',400,210,0));
  // Base-colour detail is a separate finer signal, never generated by lightmap density.
  for(let i=0;i<48;i++){
   const x=255+i%8*40,y=50+Math.floor(i/8)*16,part=w.polygon(()=>[[x-18,y-7,25],[x+18,y-7,25],[x+18,y+7,25],[x-18,y+7,25]],'#3d6675')as Line;
   part.fill(()=>i%2?Color.lerp('#3d6675','#87554d',n('material')):Color.lerp('#3a4d60','#80654e',n('material')));part.opacity(()=>n('detail'));add(part);
  }
  const bounce=w.path(()=>[initialLamp,[-350,-145,80],[-390,80,20]],P.green,()=>n('bounce'));add(bounce);
  const actor=w.actor(()=>n('actor'),100,P.green,'●',14);actor.opacity(()=>n('read'));add(actor);
  add(w.path(()=>[[400,0,50],[0,90,50]],P.blue,()=>n('read')));
  add(mono(()=>`무늬 정보 ${n('detail').toFixed(1)} / 조명 밀도 예 ${Math.round(n('grid'))} / 재질 수정 ${n('material').toFixed(1)}`,0,305,26));
 }
 if(kind==='filter'){
  for(const [level,x,count,z]of [[0,-420,8,0],[1,-40,4,40],[2,300,2,80]]as const){
   add(w.box(x,0,z,280,280,12,'#34454b'));
   const width=250/count;
   for(let i=0;i<count*count;i++)add(w.box(x-125+width/2+i%count*width,-125+width/2+Math.floor(i/count)*width,z+12,width-2,width-2,4,level===0?(i%count+Math.floor(i/count))%2?'#42653c':'#5c573e':'#485c3b'));
   const selected=w.box(x,0,z+18,285,285,4,'#62583d');selected.opacity(()=>Math.max(0,1-Math.abs(n('mip')-level))*.23);add(selected);
   add(w.label(`MIP ${level}`,x,195,z,29));
  }
  const footprint=w.polygon(()=>{const x=-435.625+n('u')*31.25,y=-15.625+n('v')*31.25;return [[x-22*n('stretch'),y-22,22],[x+22*n('stretch'),y-22,22],[x+22*n('stretch'),y+22,22],[x-22*n('stretch'),y+22,22]]as V3[];},'#f3da7570',P.red);add(footprint);
  for(const [x,y]of [[-435.625,-15.625],[-404.375,-15.625],[-435.625,15.625],[-404.375,15.625]])add(dot(()=>[x,y,25],P.blue,9));
  add(dot(()=>[-435.625+n('u')*31.25,-15.625+n('v')*31.25,25],P.red,16));
  const weighted=()=>n('u')*(1-n('v'))+(1-n('u'))*n('v');
  add(new Circle({x:650,y:35,size:90,fill:()=>Color.lerp(Color.lerp('#5c573e','#42653c',weighted()),'#485c3b',n('blend')),stroke:P.ink,lineWidth:2}));
  add(text('필터 결과',650,110,26));
  add(mono(()=>`w = [${[(1-n('u'))*(1-n('v')),n('u')*(1-n('v')),(1-n('u'))*n('v'),n('u')*n('v')].map(v=>v.toFixed(3)).join(', ')}]`,0,260,26));
  add(text(()=>`읽는 MIP ${n('mip').toFixed(1)} / 레벨 보간 ${n('blend').toFixed(2)} / 발자국 비 ${n('stretch').toFixed(1)}`,0,308,25,P.muted));
 }
 if(kind==='tile'){
  add(w.box(-430,0,0,290,280,14,'#34454b'));
  for(let i=0;i<16;i++){const tile=w.box(-535+i%4*70,-105+Math.floor(i/4)*70,14,66,66,4,i===6?'#62583d':'#33444d');tile.opacity(()=>i===6?1:.5+.5*n('bin'));add(tile);}
  add(w.polygon(()=>[[-530,-50,22],[-320,-50,22],[-430,95,22]],'#3d6675'));
  add(w.box(0,0,0,270,250,30,'#425460'),w.box(0,0,30,190,175,20,'#62583d'));
  const back=w.box(0,0,60,135,115,15,'#805640');back.opacity(()=>n('hidden'));add(back,w.box(0,0,100,135,115,15,'#3d6675'));
  const glass=w.polygon(()=>[[-70,-70,155],[70,-70,155],[70,70,155],[-70,70,155]],'#547a9670');glass.opacity(()=>n('glass'));add(glass);
  add(w.path(()=>[[-260,0,65],[-150,0,85]],P.blue,()=>n('transfer')),w.path(()=>[[150,0,85],[290,0,65]],P.green,()=>n('out')));
  add(w.box(430,0,0,270,250,15,'#30463b'));const out=w.box(430,0,15,130,115,12,'#3d6675');out.opacity(()=>n('out'));add(out);
  add(w.label('타일별 분류',-430,195,0),w.label('칩 내부 작업 집합',0,195,0),w.label('결과 저장',430,195,0));
  for(let i=0;i<3;i++){
   const triangle=w.polygon(()=>{const from=[[-76+i*68,-110,180],[-26+i*68,-110,180],[-51+i*68,-110,220]]as V3[],to=[[-475+i*40,-45+i*30,22],[-425+i*40,-45+i*30,22],[-450+i*40,0+i*30,22]]as V3[];return from.map((p,j)=>p.map((v,k)=>v+(to[j][k]-v)*n('bin'))as V3);},'#3d6675');triangle.opacity(()=>1-n('list'));add(triangle);
   const light=dot(()=>[-51+i*68,-110,200],P.yellow,24);light.opacity(()=>n('list'));add(light);
  }
  add(mono(()=>`${n('list')<.5?'triangle bins: geometry visibility':'light lists: software light selection'} / ${n('era')<.5?'구조':'1990년대 계보'}`,0,305,26));
 }
 if(kind==='volume'){
  const near:V3[]=[[-190,-65,30],[-190,65,30],[-190,65,165],[-190,-65,165]];
  const lamp=():V3=>[n('lamp'),-70,180];
  const far=()=>near.map(p=>p.map((v,j)=>v+(v-lamp()[j])*n('extend')*1.3)as V3);
  add(w.box(-60,40,0,900,450,12,'#34454b'));
  for(let i=0;i<4;i++){const j=(i+1)%4;add(w.polygon(()=>[near[i],near[j],far()[j],far()[i]],'#c43b3b20','#c43b3b90'),w.path(()=>[near[i],far()[i]],P.red,()=>n('extend')));}
  add(w.polygon(far,'#c43b3b18','#c43b3b90'),w.polygon(()=>near,'#3d6675'),dot(lamp,P.yellow,40));
  add(w.path(()=>[lamp(),[-190,0,90]],P.yellow,()=>n('ray')));
  const blocked=()=>{const L=lamp(),t=(-190-L[0])/(50-L[0]),y=L[1]+(n('receiverY')-L[1])*t,z=L[2]+(25-L[2])*t;return Math.abs(y)<=65&&z>=30&&z<=165;};
  add(dot(()=>[50,n('receiverY'),25],()=>blocked()?P.red:P.green,30));
  add(w.label('수광점',50,()=>n('receiverY')+70,25,27));
  const camera=():V3=>[390-360*n('cameraInside'),0,60];
  // Test against the same closed convex geometry that is drawn, rather than
  // deciding camera-inside status from the animation slider alone.
  const cameraIsInside=()=>{if(n('extend')<.05)return false;const f=far(),faces=[near,f,...near.map((p,i)=>[p,near[(i+1)%4],f[(i+1)%4],f[i]])];const centre=near.concat(f).reduce((sum,p)=>sum.map((v,j)=>v+p[j]/8)as V3,[0,0,0]as V3);return faces.every(face=>{const a=face[0],u=face[1].map((v,j)=>v-a[j]),v=face[2].map((v,j)=>v-a[j]),normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],dotAt=(p:V3)=>normal.reduce((sum,value,j)=>sum+value*(p[j]-a[j]),0);return dotAt(centre)*dotAt(camera())>=-1e-6;});};
  add(dot(camera,P.ink,24));
  add(w.path(()=>[camera(),[50,n('receiverY'),25]],P.muted));
  add(mono(()=>`닫힌 볼륨 / 광원 가림: ${blocked()?'예':'아니오'} / 카메라 ${n('extend')<.05?'체적 구성 전':cameraIsInside()?'안쪽':'바깥쪽'}`,0,305,26));
 }
 if(kind==='normal'){
  const origin:V3=[-360,0,20],basis:V3[]=[[Math.sqrt(2/3),0,1/Math.sqrt(3)],[-Math.sqrt(1/6),Math.sqrt(.5),1/Math.sqrt(3)],[-Math.sqrt(1/6),-Math.sqrt(.5),1/Math.sqrt(3)]];
  const normal=():V3=>[Math.sin(n('angle')*Math.PI/180),0,Math.cos(n('angle')*Math.PI/180)];
  const weights=()=>basis.map(b=>Math.max(0,b.reduce((sum,v,j)=>sum+v*normal()[j],0)));
  add(w.box(-360,0,0,270,260,18,'#34454b'));
  for(let i=0;i<3;i++){const color=[P.red,P.green,P.blue][i],ray=w.path(()=>[origin,basis[i].map((v,j)=>origin[j]+v*155)as V3],color);ray.opacity(()=>n('basis'));add(ray);}
  add(w.path(()=>[origin,normal().map((v,j)=>origin[j]+v*180)as V3],P.ink));
  const directLight=dot(()=>[-300,-110,210],P.yellow,30);directLight.opacity(()=>n('direct'));add(directLight);
  add(w.box(-20,0,0,145,140,18,'#3a493e'),dot(()=>[-20,0,35],()=>`rgb(${weights().map(v=>Math.round(Math.min(1,v)*255)).join(',')})`,85));
  // Actual displaced top faces change silhouette, unlike normal-only arrows.
  for(let i=0;i<4;i++){
   const x=230+i*48,h=()=>18+Math.sin(i*Math.PI/3)*60*n('geometry');
   add(w.polygon(()=>[[x-22,-50,0],[x-22,50,0],[x-22,50,h()],[x-22,-50,18]],'#42627d'));
   add(w.polygon(()=>[[x-22,50,0],[x+22,50,0],[x+22,50,h()],[x-22,50,h()]],'#3d607b'));
   add(w.polygon(()=>[[x-22,-50,18],[x+22,-50,18],[x+22,50,h()],[x-22,50,h()]],'#43647d'));
  }
  const probeColors=[P.blue,P.green,'#ad793e'];
  for(const [i,x]of [200,400,600].entries()){const probe=dot(()=>[x,120,145],probeColors[i],24);probe.opacity(()=>n('probe'));add(probe);}
  const actor=w.actor(()=>n('actor'),120,P.green,'●',18);actor.opacity(()=>n('probe'));add(actor);
  const received=dot(()=>[n('actor'),120,145],()=>n('actor')<400?Color.lerp(probeColors[0],probeColors[1],sat((n('actor')-200)/200)):Color.lerp(probeColors[1],probeColors[2],sat((n('actor')-400)/200)),34);received.opacity(()=>n('probe'));add(received);
  add(mono(()=>`w = (${weights().map(v=>v.toFixed(2)).join(', ')}) / direct=${n('direct').toFixed(1)} / geometry=${n('geometry').toFixed(1)}`,0,270,25));
 }
 if(kind==='depth'){
  const lamp:V3=[-480,-100,190],sample:V3=[-60,60,20];
  const point=(depth:number):V3=>lamp.map((v,j)=>v+(sample[j]-v)*depth/.8)as V3;
  add(w.box(-250,0,0,500,340,12,'#3a493e'),w.box(440,0,0,270,270,12,'#34454b'));
  for(let i=0;i<64;i++){
   const count=()=>Math.max(4,Math.min(8,Math.round(n('grid')))),p=()=>{const step=250/count(),x=315+(i%8+.5)*step,y=-125+(Math.floor(i/8)+.5)*step;return [[x-step*.45,y-step*.45,18],[x+step*.45,y-step*.45,18],[x+step*.45,y+step*.45,18],[x-step*.45,y+step*.45,18]]as V3[];};
   const cell=w.polygon(p,i===9?'#62583d':'#33444d');cell.opacity(()=>i%8<count()&&Math.floor(i/8)<count()?n('record'):0);add(cell);
  }
  add(dot(()=>lamp,P.yellow,40),dot(()=>sample,()=>.8>n('stored')+n('bias')?P.red:P.green,28));
  const caster=()=>point(n('stored'));
  add(w.box(()=>caster()[0],()=>caster()[1],()=>caster()[2],55,55,65,'#3d6675'));
  add(w.path(()=>[lamp,point(Math.min(.8,n('stored')))],P.yellow,()=>n('record')));
  add(w.path(()=>[sample,[440,0,35]],P.blue,()=>n('lookup')));
  const biasGap=w.polygon(()=>{const shift=n('bias')*700;return [[-60+shift,20,14],[20+shift,20,14],[20+shift,110,14],[-60+shift,110,14]]as V3[];},'#48595b');biasGap.opacity(()=>n('bias')>0?.6:0);add(biasGap);
  const results=[1,0,1,0],revealed=()=>Math.min(4,Math.max(0,Math.floor(n('filter')*4+1e-6)));
  for(let i=0;i<4;i++){
   const pass=results[i],visible=()=>revealed()>i?1:0,test=new Circle({x:-280+i*90,y:220,size:37,fill:pass?P.green:P.red,opacity:visible});const digit=text(String(pass),-280+i*90,220,25,'#ffffff');digit.opacity(visible);add(test,digit);
  }
  const filtered=new Circle({x:625,y:220,size:45,fill:Color.lerp('#ffffff',P.green,.5),stroke:P.ink,lineWidth:2,opacity:()=>sat(n('pcf')/.5)});add(filtered);
  // Blocker-search footprint and moment buffers are separate educational
  // operations. Stored moment values below come from the shown .33/.90 pair.
  const kernel=w.polygon(()=>{const r=30+100*n('search');return [[-250-r,-r,14],[-250+r,-r,14],[-250+r,r,14],[-250-r,r,14]]as V3[];},'#62583d40',P.yellow);kernel.opacity(()=>n('search'));add(kernel);
  for(const [i,value]of [.615,.45945].entries()){const x=130+i*170,h=()=>15+value*150*sat((n('moment')-.4)/.6),bar=new Node({});bar.add([w.polygon(()=>[[x-42,-102,15],[x+42,-102,15],[x+42,-18,h()],[x-42,-18,h()]],i?P.blue:P.green),w.polygon(()=>[[x-42,-18,15],[x+42,-18,15],[x+42,-18,h()],[x-42,-18,h()]],i?'#3d607b':'#394c41')]);bar.opacity(()=>n('moment'));add(bar);const label=text(i?'E[z²] = .45945':'E[z] = .615',90+i*220,-95,23);label.opacity(()=>n('moment'));add(label);}
  for(let i=0;i<16;i++){const page=w.box(320+i%4*63,-95+Math.floor(i/4)*63,28,56,56,8,i===5?P.yellow:'#43647d');page.opacity(()=>n('virtual')>i/16?.85:0);add(page);}
  add(w.label('검사점 0.80',sample[0],sample[1]+80,20,26),w.label('광원 깊이',440,145,0,28));
  add(text(()=>n('stored').toFixed(2),440,-40,40));
  add(mono(()=>{const count=revealed();return count?`PCF ${count}회 [${results.slice(0,count).join(',')}] / 판정 평균 ${(results.slice(0,count).reduce((a,b)=>a+b,0)/count).toFixed(2)}`:`0.80 ${.8>n('stored')+n('bias')?'>':'≤'} ${n('stored').toFixed(2)} + bias ${n('bias').toFixed(2)}`;},0,280,26));
  add(text(()=>n('virtual')>.5?'Variance ≠ Virtual':n('moment')>.5?'모멘트 E[z], E[z²] / blocker search는 별도':`조명 표본 밀도 예: ${Math.round(n('grid'))}`,0,310,25,P.muted));
 }
 if(kind==='cascade'){
  const s=depthSpace(()=>23,[-120,0],.87),bounds=[-470,-310,-70,280],colors=['#547a96','#44673d','#62583d'];
  add(s.box(-50,0,0,780,530,14,'#34454b'));
  for(let i=0;i<3;i++){
   const quad=(x:number):V3[]=>{const r=35+(x+470)*.24;return [[x,-r,18],[x,r,18],[x,r,180],[x,-r,180]];};
   const q=s.polygon(()=>quad(bounds[i+1]),colors[i]+'66',colors[i]);q.opacity(()=>n('split'));add(q);
   for(let j=0;j<4;j++){const p=s.polygon(()=>[quad(bounds[i])[j],quad(bounds[i])[(j+1)%4],quad(bounds[i+1])[(j+1)%4],quad(bounds[i+1])[j]],colors[i]+'20',colors[i]);p.opacity(()=>n('split'));add(p);}
   const y=-270+i*150,map=s.box(700,y,0,145,130,12,colors[i]);map.opacity(()=>n('maps')>i?1:.12);add(map);
   const path=s.path(()=>[[bounds[i+1],0,120],[610,y,30]],colors[i]);path.opacity(()=>n('maps')>i?1:0);add(path);
  }
  for(let i=0;i<3;i++)add(s.label(`${[20,80,200][i]}m / 2048`,850,-270+i*150,0,24));
  // A world-space texel footprint grows with coverage at fixed map resolution.
  const footprint=s.polygon(()=>{const width=20+n('coverage')*.6;return [[-200-width/2,-70-width/2,20],[-200+width/2,-70-width/2,20],[-200+width/2,-70+width/2,20],[-200-width/2,-70+width/2,20]]as V3[];},'#cf7e4655',P.red);add(footprint);
  const receiverShadow=s.polygon(()=>[[100,-70,16],[250,-70,16],[250,70,16],[100,70,16]],'#3f515c');receiverShadow.opacity(()=>n('receive')*.75);add(receiverShadow);
  const cascadeColor=()=>{const x=n('sample');if(x<-320)return new Color(P.blue);if(x<-300)return Color.lerp(P.blue,P.green,(x+320)/20);if(x<-80)return new Color(P.green);if(x<-60)return Color.lerp(P.green,P.yellow,(x+80)/20);return new Color(P.yellow);};
  add(new Circle({position:()=>s.point(n('sample'),25,20),size:26,fill:cascadeColor,stroke:P.ink,lineWidth:2}));
  for(let i=0;i<3;i++){const lookup=s.path(()=>[[n('sample'),25,20],[700,-270+i*150,25]],colors[i]);lookup.opacity(()=>n('split')*Number((n('sample')<-310?0:n('sample')<-70?1:2)===i));add(lookup);}
  add(s.label('카메라',-480,120,100,25));
  add(mono(()=>`${n('coverage').toFixed(0)}m / 2048 = ${(n('coverage')/2048).toFixed(4)}m/texel / maps=${Math.round(n('maps'))}`,0,260,26));
  add(text(()=>`수신 예제 ${n('receive')>.5?'켜짐':'꺼짐'} / 도식은 엔진 설정 측정이 아님`,0,310,25,P.muted));
 }
 if(kind==='pipeline'){
  const left=depthSpace(()=>24,[-450,80],.74),right=depthSpace(()=>24,[420,80],.74);
  for(const s of [left,right]){
   add(s.box(-140,0,0,210,240,14,'#34454b'));
   for(let i=0;i<4;i++)add(s.box(-200+i%2*95,-65+Math.floor(i/2)*105,14,75,75,50,'#3d6675'));
   for(let i=0;i<3;i++){const light=new Circle({position:()=>s.point(-300+i*145,-175,180),size:28,fill:[P.yellow,'#805640',P.blue][i],opacity:()=>n('lights')>i?1:.1});add(light);}
   for(let i=0;i<2;i++){const glass=s.polygon(()=>[[-250,-140-i*25,140],[-25,-140-i*25,140],[-25,-140-i*25,25],[-250,-140-i*25,25]],'#547a9655',P.blue);glass.opacity(()=>n('glass')>i?1:0);add(glass);}
   add(s.box(350,0,0,120,130,14,'#30463b'));
   add(s.label('색 출력',350,120,0,27));
  }
  for(let i=0;i<3;i++){const plane=right.box(()=>110+(i-1)*70*n('channels'),0,()=>30+i*(45+20*n('channels')),135,160,12,['#30463b','#43647d','#62583d'][i]);plane.opacity(()=>n('stored'));add(plane);}
  add(left.path(()=>[[-300,-175,180],[-150,0,70]],P.yellow),left.path(()=>[[-155,-175,180],[-150,0,70]],'#cf7e46'),left.path(()=>[[-150,0,70],[350,0,30]],P.green));
  const store=right.path(()=>[[-150,0,70],[110,0,150]],P.blue,()=>n('stored'));add(store);
  add(right.path(()=>[[-300,-175,180],[110,0,150]],P.yellow),right.path(()=>[[110,0,150],[350,0,30]],P.green));
  const leftFocus=left.polygon(()=>[[-320,-205,0],[430,-205,0],[430,160,0],[-320,160,0]],'#62583d25',P.yellow);leftFocus.opacity(()=>n('path')===2?.65:1-sat(n('path')));
  const rightFocus=right.polygon(()=>[[-320,-205,0],[430,-205,0],[430,160,0],[-320,160,0]],'#43647d25',P.blue);rightFocus.opacity(()=>sat(n('path')));add(leftFocus,rightFocus);
  const contribution=new Circle({x:0,y:170,size:65,fill:()=>Color.lerp('#3a4d60','#62583d',sat(n('a')+n('b'))),stroke:P.ink,lineWidth:2});add(contribution);
  add(text('Forward',-440,-245,34),text('Deferred',460,-245,34));
  add(text(()=>n('channels')>.5?'BaseColor · Normal · Roughness':'표면 정보 먼저 저장',475,-195,25,P.muted));
  const featureGate=left.polygon(()=>[[50,-60,200],[230,-60,200],[230,-60,255],[50,-60,255]],'#805640',P.red);featureGate.opacity(()=>n('feature'));add(featureGate);const gateLabel=text('기능별 지원 확인',-345,195,25,P.red);gateLabel.opacity(()=>n('feature'));add(gateLabel);
  add(mono(()=>`${n('a').toFixed(2)} + ${n('b').toFixed(2)} = ${(n('a')+n('b')).toFixed(2)} / ${['Forward','Deferred','혼합 경로'][Math.round(n('path'))]}`,0,260,28));
  add(text(()=>n('feature')>.5?'구현의 기능 제한 ≠ 수학적 불가능':'불투명·투명·MSAA·버퍼 대역폭의 비용을 함께 비교',0,310,25,P.muted));
 }
 if(kind==='ao'){
  const p:V3=[-110,80,15],q=(i:number):V3=>{const a=2*Math.PI*i/8;return [p[0]+Math.cos(a)*n('radius'),p[1]+Math.sin(a)*n('radius'),p[2]+35];};
  const valid=(i:number)=>q(i)[0]+n('shift')<110;
  const hit=(i:number)=>valid(i)&&q(i)[0]>=-40&&q(i)[0]<=40&&q(i)[1]>=-80&&q(i)[1]<=80;
  add(w.box(-130,0,0,480,380,12,'#34454b'),w.box(0,0,12,80,160,100,'#3d6675'));
  for(let i=0;i<8;i++){
   add(new Line({points:()=>[w.point(...p),w.point(...q(i))],stroke:()=>!valid(i)?P.muted:hit(i)?P.red:P.green,lineWidth:5,endArrow:true,end:()=>n('amount')}));
   const sample=dot(()=>q(i),()=>!valid(i)?P.muted:hit(i)?P.red:P.green,18);sample.opacity(()=>n('amount'));add(sample);
  }
  add(dot(()=>p,P.yellow,28));
  const thin=w.box(310,10,12,18,160,110,'#3d6675'),wall=w.box(420,80,12,100,18,140,'#3a493e');thin.opacity(()=>n('thin'));wall.opacity(()=>n('thin'));add(thin,wall);
  for(let i=0;i<6;i++){
   const shade=w.polygon(()=>[[-80+i*18,65,14],[-63+i*18,65,14],[-63+i*18,125,14],[-80+i*18,125,14]],'#394c41');
   shade.opacity(()=>n('amount')*((i%2?.55:.12)*(1-n('filter'))+.28*n('filter')));add(shade);
  }
  const directLight=dot(()=>[480,-90,200],P.yellow,30),directRay=w.path(()=>[[480,-90,200],[400,80,20]],P.yellow);directLight.opacity(()=>n('direct'));directRay.opacity(()=>n('direct'));add(directLight,directRay);
  add(w.label('앞면 깊이 ≠ 두께',390,170,0,25));
  add(mono(()=>{const count=Array.from({length:8},(_,i)=>Number(valid(i))).reduce((a,b)=>a+b,0),blocked=Array.from({length:8},(_,i)=>Number(hit(i))).reduce((a,b)=>a+b,0);return `유효 ${count}/8 / A=${count?(1-blocked/count).toFixed(2):'정보 없음'} / 반경 ${Math.round(n('radius'))}`;},0,280,26));
  add(text(()=>`${n('era')<2012?'2007':'2017'} 구현 맥락 / filter=${n('filter').toFixed(1)} / direct=${n('direct').toFixed(1)}`,0,310,25,P.muted));
 }
 return {node,keys:Object.keys(signals),reset(pose:Pose={}){for(const [k,v]of Object.entries(defaults[kind]))signals[k](v);for(const [k,v]of Object.entries(pose)){if(!signals[k])throw new Error(`Unsupported ${kind}.${k}`);signals[k](v);}},*transition(pose:Pose,duration:number){for(const key of Object.keys(pose))if(!signals[key])throw new Error(`Unsupported ${kind}.${key}`);yield* all(...Object.entries(pose).map(([key,v])=>signals[key](v,duration,linear)));}};
}
