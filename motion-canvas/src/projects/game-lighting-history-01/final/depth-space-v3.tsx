import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {DARK as P} from '../../../styles/research-dark';
export type V3=[number,number,number];
export type Value=number|(()=>number);
export const val=(v:Value)=>typeof v==='function'?v():v;
const shade=(c:string,f:number)=>'#'+[1,3,5].map(i=>Math.round(parseInt(c.slice(i,i+2),16)*f).toString(16).padStart(2,'0')).join('');

// Series-scoped XYZ projection. Legacy shared white geometry stays unchanged.
export function depthSpace(yaw:()=>number,origin:[number,number]=[0,80],scale=1){
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{
  const a=yaw()*Math.PI/180,X=val(x),Y=val(y);
  return [origin[0]+scale*(X*Math.cos(a)-Y*Math.sin(a)),origin[1]+scale*((X*Math.sin(a)+Y*Math.cos(a))*.48-val(z))];
 };
 const polygon=(pts:()=>V3[],color:string,stroke:string=P.line)=><Line points={()=>pts().map(p=>point(...p))} closed fill={color} stroke={stroke} lineWidth={1.7} lineJoin={'round'}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>{
  const p=(dx:number,dy:number,dz:number):V3=>[val(x)+dx,val(y)+dy,val(z)+dz];
  return <Node>
   {polygon(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,val(h)),p(-w/2,d/2,val(h))],shade(color,.82))}
   {polygon(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,val(h)),p(w/2,-d/2,val(h))],shade(color,.7))}
   {polygon(()=>[p(-w/2,-d/2,val(h)),p(w/2,-d/2,val(h)),p(w/2,d/2,val(h)),p(-w/2,d/2,val(h))],color)}
  </Node>;
 };
 const shadow=(x:Value,y:Value,w=90,d=50)=>polygon(()=>Array.from({length:32},(_,i)=>[val(x)+20+Math.cos(i*Math.PI/16)*w/2,val(y)+18+Math.sin(i*Math.PI/16)*d/2,1] as V3),'#1b252a','#1b252a');
 const label=(text:string,x:Value,y:Value,z:Value=0,size=29,color:string=P.ink)=><Txt position={()=>point(x,y,z)} text={text} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600} textAlign={'center'}/>;
 // Episode01-only articulated figure. Preserve other productions' shared helper.
 const actor=(x:Value,y:Value,color:string,symbol='★',elevation:Value=22)=>{
  const limb=(a:()=>V3,b:()=>V3,r:number,tint:string)=>{
   const corners=(side:number)=>{const A=a(),B=b(),dx=B[0]-A[0],dz=B[2]-A[2],len=Math.hypot(dx,dz)||1,nx=dz/len*r,nz=-dx/len*r;
    return [[A[0]-nx,A[1]+side*r,A[2]-nz],[B[0]-nx,B[1]+side*r,B[2]-nz],[B[0]+nx,B[1]+side*r,B[2]+nz],[A[0]+nx,A[1]+side*r,A[2]+nz]]as V3[];};
   return <Node>{polygon(()=>corners(-1),shade(tint,.7))}{polygon(()=>corners(1),tint)}{polygon(()=>[corners(-1)[0],corners(-1)[1],corners(1)[1],corners(1)[0]],shade(tint,.82))}</Node>;
  };
  const p=(dx:number,dy:number,dz:number):V3=>[val(x)+dx,val(y)+dy,val(elevation)+dz];
  const gait=()=>Math.sin(val(x)/32);
  const face=(dx:number,dz:number,size:number,tint:string)=><Circle position={()=>point(...p(dx,16,dz))} size={size} fill={tint}/>;
  return <Node>
   {shadow(x,y,70,40)}
   {box(x,()=>val(y)-16,()=>val(elevation)+60,38,20,35,'#38454c')}
   {[-1,1].map(side=><Node>
    {limb(()=>p(side*12,0,53),()=>p(side*12+side*gait()*7,3,28),7,'#344458')}
    {limb(()=>p(side*12+side*gait()*7,3,28),()=>p(side*12+side*gait()*12,6,7),6,'#405267')}
    {box(()=>val(x)+side*12+side*gait()*12,()=>val(y)+12,()=>val(elevation),16,30,9,'#242c34')}
    {box(()=>val(x)+side*12+side*gait()*12,()=>val(y)+14,()=>val(elevation),17,31,2,'#939b9e')}
   </Node>)}
   {polygon(()=>[p(-17,-12,49),p(17,-12,49),p(25,-12,96),p(-25,-12,96)],shade(color,.72))}
   {polygon(()=>[p(17,-12,49),p(17,12,49),p(25,12,96),p(25,-12,96)],shade(color,.8))}
   {polygon(()=>[p(-17,12,49),p(17,12,49),p(25,12,96),p(-25,12,96)],color)}
   {polygon(()=>[p(-25,-12,96),p(25,-12,96),p(25,12,96),p(-25,12,96)],shade(color,1.08))}
   {box(x,()=>val(y)+14,()=>val(elevation)+51,36,5,5,'#252d34')}
   {box(x,()=>val(y)+17,()=>val(elevation)+51,7,3,6,'#b9bdba')}
   <Line points={()=>[point(...p(0,14,57)),point(...p(0,14,94))]} stroke={'#d7dedb'} lineWidth={1.8}/>
   {[-1,1].map(side=><Node>
    {limb(()=>p(side*25,0,90),()=>p(side*32-side*gait()*5,3,70),7,color)}
    {limb(()=>p(side*32-side*gait()*5,3,70),()=>p(side*29-side*gait()*9,10,52),6,shade(color,.9))}
    <Circle position={()=>point(...p(side*29-side*gait()*9,12,49))} size={[11,15]} fill={'#c6a586'} stroke={'#866e5e'} lineWidth={1}/>
    {box(()=>val(x)+side*10,()=>val(y)+15,()=>val(elevation)+70,11,3,11,shade(color,.74))}
   </Node>)}
   {box(x,y,()=>val(elevation)+96,14,16,9,'#b99b7e')}
   <Circle position={()=>point(...p(0,8,115))} size={[32,37]} fill={'#a88a70'} stroke={'#d3b596'} lineWidth={1.5}/>
   <Circle position={()=>point(...p(-2,14,114))} size={[27,31]} fill={'#d3b596'}/>
   {face(-15,115,6,'#b6987b')}{face(14,115,6,'#b6987b')}
   <Line points={()=>[point(...p(-14,15,124)),point(...p(-10,16,132)),point(...p(5,15,132)),point(...p(14,14,125)),point(...p(5,16,127)),point(...p(-5,16,126))]} closed fill={'#343333'} stroke={'#343333'}/>
   {face(-7,117,3,'#20272c')}{face(6,117,3,'#20272c')}
   <Line points={()=>[point(...p(0,18,115)),point(...p(2,19,111)),point(...p(-1,19,110))]} stroke={'#a07963'} lineWidth={1.2}/>
   <Line points={()=>[point(...p(-5,18,106)),point(...p(4,18,106))]} stroke={'#6f4f44'} lineWidth={1.4}/>
   {label(symbol,()=>val(x)+12,()=>val(y)+17,()=>val(elevation)+83,9,'#f4df8a')}
  </Node>;
 };
 const path=(pts:()=>V3[],color:string=P.blue,progress:Value=1,dash:number[]=[])=> <Line points={()=>pts().map(p=>point(...p))} stroke={color} lineWidth={5} endArrow arrowSize={16} end={()=>val(progress)} lineDash={dash} lineJoin={'round'}/>;
 const flag=(x:Value,y:Value,color:string=P.green)=><Node>
  {box(x,y,22,8,8,145,'#818990')}
  {polygon(()=>[[val(x)+4,val(y),163],[val(x)+80,val(y),144],[val(x)+4,val(y),113]],color,color)}
 </Node>;
 return {point,box,shadow,label,actor,path,flag,polygon};
}
export function heading(id:string,title:string,subtitle:string,topic='게임 렌더링의 역사'){return <Node>
 <Txt text={`${id} · ${topic}`} x={-855} y={-465} offset={[-1,0]} fill={P.muted} fontFamily={P.font} fontSize={26}/>
 <Txt text={title} x={-855} y={-390} offset={[-1,0]} fill={P.title} fontFamily={P.font} fontSize={44} fontWeight={700}/>
 <Txt text={subtitle} x={-855} y={-315} offset={[-1,0]} fill={P.muted} fontFamily={P.font} fontSize={29}/>
 </Node>;}
