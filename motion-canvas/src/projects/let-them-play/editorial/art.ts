import {PAPER as P} from '../../../styles/research-paper';
export type Point=[number,number];
export const iso=(x:number,z:number,h=0):Point=>[(x-z)*.88,(x+z)*.38-h];
export const ramp=(t:number,a:number,b:number)=>{const x=Math.max(0,Math.min(1,(t-a)/(b-a)));return x*x*(3-2*x)};
export const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;

/** Small, deterministic vector toolkit shared by the seven new dioramas. */
export class Art {
 constructor(public c:CanvasRenderingContext2D){}
 poly(p:Point[],fill:string,stroke?:string,w=1){const c=this.c;c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=w;c.stroke()}}
 line(p:Point[],stroke:string,w=2){const c=this.c;c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=stroke;c.lineWidth=w;c.lineCap='round';c.lineJoin='round';c.stroke()}
 oval(x:number,y:number,rx:number,ry:number,fill:string){const c=this.c;c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fillStyle=fill;c.fill()}
 rect(x:number,y:number,w:number,h:number,fill:string){this.c.fillStyle=fill;this.c.fillRect(x,y,w,h)}
 plane(p:Point[],h:number,color:string){this.poly(p.map(([x,z])=>iso(x,z,h)),color)}
 box(x:number,z:number,w:number,d:number,h:number,top='#b0c2cc',left='#7f9bab',right='#5f8197',base=0){
  const a=iso(x-w/2,z-d/2,base),b=iso(x+w/2,z-d/2,base),e=iso(x+w/2,z+d/2,base),d0=iso(x-w/2,z+d/2,base),up=(p:Point):Point=>[p[0],p[1]-h];
  this.poly([d0,e,up(e),up(d0)],left);this.poly([e,b,up(b),up(e)],right);this.poly([up(a),up(b),up(e),up(d0)],top);
 }
 floor(kind:'grass'|'stone'|'snow'|'wood'='stone'){
  const colors={grass:['#edf0e5','#cbd3c7','#b7c5b9'],stone:['#e8eef1','#cbd5db','#b0c0ca'],snow:['#edf3f7','#c9d8e2','#adc3d3'],wood:['#eee7d9','#d4c7b0','#b7a791']}[kind];
  this.oval(24,237,407,49,'#f0f3f4');this.oval(19,237,330,34,'#e7edef');
  this.box(0,0,700,440,44,colors[0],colors[1],colors[2],-44);
  if(kind==='stone'||kind==='wood'){
   for(let x=-300;x<350;x+=80)this.line([iso(x,-220,1),iso(x,220,1)],kind==='wood'?'#dcd2bd':'#d5dfe4',1);
   if(kind==='stone')for(let z=-160;z<220;z+=80)this.line([iso(-350,z,1),iso(350,z,1)],'#d5dfe4',1);
  }
 }
 path(p:Point[],width=27,color='#d8d0b9'){const line=p.map(([x,z])=>iso(x,z,1));this.line(line,color,width);this.line(line,'#ebe6d7',width*.43)}
 tree(x:number,z:number,size=1,snow=false){const c=this.c,p=iso(x,z);c.save();c.translate(...p);c.scale(size,size);
  this.oval(7,4,26,9,'#ccd6d0');this.rect(-4,-55,8,56,'#89988a');
  this.poly([[-33,-28],[0,-108],[33,-28]],'#849e90');this.poly([[0,-108],[33,-28],[0,-28]],'#668579');
  this.poly([[-27,-61],[0,-125],[27,-61]],snow?'#f4f7f8':'#9aaf9e');this.poly([[0,-125],[27,-61],[0,-61]],snow?'#d9e5ea':'#7b9787');c.restore();
 }
 arch(x:number,z:number,open=0){
  this.box(x,z,122,94,15,'#ccd8dc','#9bb1bb','#7b97a5');
  this.box(x-40,z,24,44,164,'#d5e0e3','#9ab3c0','#708fa3',15);
  this.box(x+40,z,24,44,164,'#d5e0e3','#9ab3c0','#708fa3',15);
  if(open<.999)this.box(x,z,56,25,139*(1-open),'#a9c0d1','#3c658e','#234f7a',15+139*open);
  this.box(x,z,120,54,22,'#d5e0e3','#9ab3c0','#708fa3',179);
  const p=iso(x,z,217);this.oval(p[0],p[1],7,7,P.yellow);
 }
 tower(x:number,z:number,h=132,base=0){
  this.box(x,z,80,65,12,'#b0c2cc','#7f9bab','#5f8197',base);this.box(x,z,50,43,h,'#93aec3','#6089a9','#426c8e',base+12);this.box(x,z,75,65,12,'#bed0da','#8caaba','#7394a8',base+h+12);
  const p=iso(x,z,base+h+24);this.line([p,[p[0],p[1]-47]],'#54758a',3);this.poly([[p[0],p[1]-47],[p[0]+38,p[1]-35],[p[0],p[1]-24]],P.yellow);
 }
 crystal(x:number,z:number,height=30,alpha=1){this.c.save();this.c.globalAlpha*=alpha;const p=iso(x,z,height);
  this.poly([[p[0]-15,p[1]],[p[0],p[1]-24],[p[0]+15,p[1]],[p[0],p[1]+21]],P.yellow);this.poly([[p[0],p[1]-24],[p[0]+15,p[1]],[p[0],p[1]+21]],'#d7b957');this.c.restore();
 }
 hero(x:number,z:number,time:number,walk=0,base=0){
  const c=this.c,p=iso(x,z,base),step=Math.sin(time*8)*walk;
  c.save();c.translate(...p);this.oval(7,3,38,12,'#bdcbc8');
  this.line([[-10,-33],[-13+step*7,-8]],'#414b50',13);this.line([[13,-33],[18-step*7,-7]],'#414b50',13);
  this.oval(-15+step*7,-5,13,6,'#303c43');this.oval(19-step*7,-4,14,6,'#303c43');
  c.translate(0,Math.sin(time*1.8)*1.15-Math.abs(step)*3);
  this.poly([[-26,-82],[-36,-69],[-29,-30],[-13,-32],[-10,-80]],'#ad9470');
  this.poly([[-18,-82],[18,-82],[33,-31],[-32,-31]],P.blue);this.poly([[0,-81],[18,-82],[33,-31],[5,-31]],'#254c89');
  this.line([[-22,-68],[-33,-41]],'#debfa1',10);this.line([[22,-68],[29,-43]],'#debfa1',10);
  this.rect(-29,-44,58,6,'#876e4f');this.rect(-3,-45,9,9,'#dbc39b');
  this.oval(0,-109,29,31,'#e6ccb0');this.oval(25,-107,7,10,'#e6ccb0');
  this.poly([[-29,-114],[-25,-133],[-8,-144],[16,-139],[31,-122],[21,-113],[5,-128],[-5,-111],[-13,-121]],'#414d50');
  this.oval(6,-108,2.8,4,'#283d47');this.oval(22,-106,2.5,3.5,'#283d47');this.line([[10,-93],[19,-92]],'#ad7f68',1.6);
  this.poly([[-21,-87],[14,-84],[21,-75],[-17,-74]],P.yellow);this.poly([[-16,-80],[-50,-90+Math.sin(time*1.2)*2],[-41,-73],[-17,-72]],'#e4c964');c.restore();
 }
 ring(x:number,z:number,alpha=1,base=0){this.c.save();this.c.globalAlpha*=alpha;const p=iso(x,z,base+3);this.c.beginPath();this.c.ellipse(...p,43,17,0,0,Math.PI*2);this.c.strokeStyle=P.blue;this.c.lineWidth=3;this.c.stroke();this.c.restore()}
}
