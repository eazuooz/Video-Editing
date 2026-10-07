import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {PAPER as P} from '../styles/research-paper';
export type V3=[number,number,number];
export type Value=number|(()=>number);
export const val=(v:Value)=>typeof v==='function'?v():v;
const shade=(c:string,f:number)=>'#'+[1,3,5].map(i=>Math.round(parseInt(c.slice(i,i+2),16)*f).toString(16).padStart(2,'0')).join('');
// Orthographic projection of real XYZ geometry. Z is elevation, not a pasted shadow.
export function depthSpace(yaw:()=>number,origin:[number,number]=[0,80],scale=1){
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{
  const a=yaw()*Math.PI/180,X=val(x),Y=val(y);
  return [origin[0]+scale*(X*Math.cos(a)-Y*Math.sin(a)),origin[1]+scale*((X*Math.sin(a)+Y*Math.cos(a))*.48-val(z))];
 };
 const polygon=(pts:()=>V3[],color:string,stroke:string=P.line)=> <Line points={()=>pts().map(p=>point(...p))} closed fill={color} stroke={stroke} lineWidth={1.7} lineJoin={'round'}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:number,color:string)=>{
  const p=(dx:number,dy:number,dz:number):V3=>[val(x)+dx,val(y)+dy,val(z)+dz];
  return <Node>
   {polygon(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(color,.82))}
   {polygon(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(color,.7))}
   {polygon(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],color)}
  </Node>;
 };
 const shadow=(x:Value,y:Value,w=90,d=50)=>polygon(()=>Array.from({length:32},(_,i)=>[val(x)+20+Math.cos(i*Math.PI/16)*w/2,val(y)+18+Math.sin(i*Math.PI/16)*d/2,1] as V3),'#dce2e5','#dce2e5');
 const label=(text:string,x:Value,y:Value,z:Value=0,size=29,color:string=P.ink)=> <Txt position={()=>point(x,y,z)} text={text} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600} textAlign={'center'}/>;
 const actor=(x:Value,y:Value,color:string,symbol='★',elevation:Value=22)=> <Node>
  {shadow(x,y)}
  {box(x,y,elevation,54,42,64,color)}
  {box(x,y,()=>val(elevation)+64,65,48,49,'#f3ecdd')}
  {label(symbol,x,()=>val(y)+27,()=>val(elevation)+41,27,'#ffffff')}
  {label('• •',x,()=>val(y)+25,()=>val(elevation)+92,21,P.ink)}
 </Node>;
 const path=(pts:()=>V3[],color:string=P.blue,progress:Value=1,dash:number[]=[])=> <Line points={()=>pts().map(p=>point(...p))} stroke={color} lineWidth={5} endArrow arrowSize={16} end={()=>val(progress)} lineDash={dash} lineJoin={'round'}/>;
 const flag=(x:Value,y:Value,color:string=P.green)=> <Node>
  {box(x,y,22,8,8,145,'#818990')}
  {polygon(()=>[[val(x)+4,val(y),163],[val(x)+80,val(y),144],[val(x)+4,val(y),113]],color,color)}
 </Node>;
 return {point,box,shadow,label,actor,path,flag,polygon};
}
export function heading(id:string,title:string,subtitle:string,topic='관전과 응원 대상'){return <Node>
 <Txt text={`${id} · ${topic}`} x={-855} y={-465} offset={[-1,0]} fill={P.muted} fontFamily={P.font} fontSize={26}/>
 <Txt text={title} x={-855} y={-390} offset={[-1,0]} fill={P.ink} fontFamily={P.font} fontSize={44} fontWeight={700}/>
 <Txt text={subtitle} x={-855} y={-315} offset={[-1,0]} fill={P.muted} fontFamily={P.font} fontSize={29}/>
 </Node>;}
