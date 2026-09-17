import {Node} from '@motion-canvas/2d';
import {BBox, createSignal} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

type Pt=[number,number];
const iso=(x:number,z:number,h=0):Pt=>[(x-z)*.88,(x+z)*.38-h];
const mix=(a:string,b:string,t:number)=>{
 const ca=a.replace('#',''),cb=b.replace('#','');
 return '#'+[0,2,4].map(i=>Math.round(parseInt(ca.slice(i,i+2),16)*(1-t)+parseInt(cb.slice(i,i+2),16)*t).toString(16).padStart(2,'0')).join('');
};

/** Original editable vector diorama. No Nintendo models, textures or game UI.
 * A/B instances share every coordinate; focus changes only color/contrast.
 */
export class OpeningWorld extends Node {
 readonly focus=createSignal(0);
 readonly clock=createSignal(0);
 readonly annotations=createSignal(0);
 protected getCacheBBox(){return new BBox(-590,-450,1180,850);}
 protected draw(c:CanvasRenderingContext2D){
  const f=this.focus(),time=this.clock();
  const quiet=(color:string)=>mix(color,'#e3e7e6',f*.78);
  const poly=(p:Pt[],fill:string,stroke?:string,w=1)=>{c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=w;c.stroke();}};
  const line=(p:Pt[],stroke:string,w=2)=>{c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=stroke;c.lineWidth=w;c.lineCap='round';c.lineJoin='round';c.stroke();};
  const ellipse=(x:number,y:number,rx:number,ry:number,fill:string)=>{c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fillStyle=fill;c.fill();};
  const rect=(x:number,y:number,w:number,h:number,fill:string)=>{c.fillStyle=fill;c.fillRect(x,y,w,h);};
  const plane=(p:Pt[],h:number,fill:string)=>poly(p.map(([x,z])=>iso(x,z,h)),fill);
  const box=(x:number,z:number,w:number,d:number,h:number,top:string,left:string,right:string,base=0)=>{
   const a=iso(x-w/2,z-d/2,base),b=iso(x+w/2,z-d/2,base),e=iso(x+w/2,z+d/2,base),d0=iso(x-w/2,z+d/2,base);
   const up=(p:Pt):Pt=>[p[0],p[1]-h];
   poly([d0,e,up(e),up(d0)],left);poly([e,b,up(b),up(e)],right);poly([up(a),up(b),up(e),up(d0)],top);
  };
  // A light, physical paper model: directional shadows, cut rock faces, clean air.
  ellipse(28,248,390,61,'#f1f3f4');ellipse(25,245,300,40,'#e8ecee');
  const ground:Pt[]=[[-350,-165],[-275,-240],[260,-240],[350,-150],[350,162],[265,240],[-265,240],[-350,155]];
  const edge=ground.map(([x,z])=>iso(x,z));
  for(let i=2;i<8;i++){
   const a=edge[i],b=edge[(i+1)%edge.length];
   poly([a,b,[b[0],b[1]+51],[a[0],a[1]+51]],i<5?'#c4cccd':'#d5dbda');
   line([[a[0],a[1]+25],[b[0],b[1]+25]],'#bac4c5',1);
  }
  poly(edge,'#edf0e8');
  plane([[-350,-165],[-275,-240],[260,-240],[350,-150],[30,-65],[-250,-52]],0,'#e4e9de');
  plane([[-265,240],[265,240],[350,162],[200,115],[-90,150]],0,'#e7ebdf');
  // One fixed path connects the avatar, an interaction object, and the landmark.
  plane([[-260,132],[-206,157],[-123,43],[-24,8],[93,-46],[224,-108],[201,-140],[77,-79],[-47,-27],[-151,13]],1,'#d8d2bd');
  plane([[-245,135],[-222,144],[-135,30],[-32,-5],[85,-64],[215,-126],[209,-132],[81,-72],[-37,-12],[-144,21]],2,'#eee9d8');
  // Low poly ridgeline. This is deliberately not a reconstruction of Hyrule.
  const peak=(x:number,z:number,w:number,h:number)=>{
   const a=iso(x-w,z),b=iso(x+w,z),back=iso(x,z-w*.72),tip=iso(x-w*.12,z-w*.14,h),front=iso(x,z+w*.65);
   poly([a,back,tip],quiet('#b4c6c3'));poly([back,b,tip],quiet('#9fafb0'));
   poly([a,front,tip],quiet('#c5d1c9'));poly([front,b,tip],quiet('#8fa5a3'));
   const snow:Pt[]=[[tip[0]-21,tip[1]+35],tip,[tip[0]+24,tip[1]+41],[tip[0]+5,tip[1]+28],[tip[0]-4,tip[1]+39]];
   poly(snow,'#f8f9f7');
  };
  peak(-250,-143,83,148);peak(-105,-186,85,199);peak(33,-212,65,137);
  // Repeated details are deterministic (no random frame-to-frame flicker).
  for(let i=0;i<38;i++){
   const x=-310+(i*137)%610,z=-120+(i*91)%320;
   if(Math.abs(z+x*.4)<53)continue;
   const p=iso(x,z,1);line([[p[0]-3,p[1]],[p[0]-5,p[1]-7]],quiet('#b9c5ad'),1.4);line([[p[0],p[1]],[p[0]+2,p[1]-5]],quiet('#b9c5ad'),1.4);
  }
  const tree=(x:number,z:number,s:number)=>{
   const p=iso(x,z);c.save();c.translate(...p);c.scale(s,s);
   ellipse(8,4,25,9,'#ccd4cb');rect(-4,-61,8,62,quiet('#8c8b7b'));
   poly([[-33,-34],[0,-104],[33,-34]],quiet('#849b8e'));poly([[0,-104],[33,-34],[0,-34]],quiet('#637f75'));
   poly([[-27,-60],[0,-119],[27,-60]],quiet('#97ad9b'));poly([[0,-119],[27,-60],[0,-60]],quiet('#769284'));c.restore();
  };
  tree(-298,7,1);tree(-239,-32,.8);tree(297,60,.88);tree(260,118,.67);tree(95,193,1.02);
  // Three competing props. Geometry is identical before / after emphasis.
  box(-102,-45,57,45,64,quiet('#789bb4'),quiet('#4e7394'),quiet('#375f81'));
  box(-102,-45,65,52,9,quiet('#a6c1d1'),quiet('#68899f'),quiet('#56768e'),64);
  const p1=iso(-102,-45,75);ellipse(p1[0],p1[1]-12,10,10,quiet('#f3da75'));
  box(68,92,65,46,45,quiet('#789bb4'),quiet('#4e7394'),quiet('#375f81'));
  const p2=iso(68,92,46);poly([[p2[0]-37,p2[1]-9],[p2[0],p2[1]-44],[p2[0]+40,p2[1]-7],[p2[0],p2[1]+11]],quiet('#80a2bb'));
  // Stone lookout: restrained blue and warm light provide the focal contrast.
  const towerX=215,towerZ=-128;
  box(towerX,towerZ,91,75,13,'#a8b9c6','#7c94a5','#627f93');
  box(towerX,towerZ,61,51,162,'#93aec3','#6089a9','#426c8e',13);
  box(towerX,towerZ,85,74,15,'#b3c9d6','#7396ad','#547c97',172);
  const p=iso(towerX,towerZ,13);
  c.save();c.translate(...p);
  poly([[-28,-2],[-5,8],[-5,-69],[-28,-78]],'#233e52');
  poly([[-24,-6],[-9,1],[-9,-65],[-24,-72]],mix('#b7ccca',P.yellow,f));
  line([[-23,-95],[-7,-88]],'#bed0d9',2);line([[-23,-108],[-7,-101]],'#bed0d9',2);
  line([[28,-74],[10,-64]],'#adc4d0',2);line([[28,-89],[10,-79]],'#adc4d0',2);
  line([[3,-187],[3,-239]],'#506f84',3);
  const sway=Math.sin(time*1.2)*3;
  poly([[4,-239],[46,-229+sway],[4,-214]],P.yellow);
  c.restore();
  // Readable silhouette, scarf, satchel, boots: an original channel mascot draft.
  const hero=iso(-219,121,0),breath=Math.sin(time*1.8)*1.15;
  c.save();c.translate(...hero);
  ellipse(7,3,40,13,'#c2ccc4');
  line([[-10,-33],[-13,-8]],'#414b50',14);line([[13,-33],[18,-7]],'#414b50',14);
  ellipse(-15,-5,13,6,'#303c43');ellipse(19,-4,14,6,'#303c43');
  c.translate(0,breath);
  // Walking equipment remains tiny and subordinate to the explanation.
  poly([[-26,-82],[-36,-69],[-29,-30],[-13,-32],[-10,-80]],'#ad9470');
  poly([[-18,-82],[18,-82],[33,-31],[-32,-31]],P.blue);
  poly([[0,-81],[18,-82],[33,-31],[5,-31]],'#254c89');
  line([[-22,-68],[-33,-41]],'#debfa1',10);line([[22,-68],[29,-43]],'#debfa1',10);
  rect(-29,-44,58,6,'#876e4f');rect(-3,-45,9,9,'#dbc39b');
  // Warm paper face and graphic ink hair, not a licensed character likeness.
  ellipse(0,-109,29,31,'#e6ccb0');ellipse(25,-107,7,10,'#e6ccb0');
  poly([[-29,-114],[-25,-133],[-8,-144],[16,-139],[31,-122],[21,-113],[5,-128],[-5,-111],[-13,-121]],'#414d50');
  ellipse(6,-108,2.8,4,'#283d47');ellipse(22,-106,2.5,3.5,'#283d47');
  line([[10,-93],[19,-92]],'#ad7f68',1.6);
  poly([[-21,-87],[14,-84],[21,-75],[-17,-74]],P.yellow);
  poly([[-16,-80],[-50,-90+Math.sin(time*1.2)*2],[-41,-73],[-17,-72]],'#e4c964');
  c.restore();
  // Thin visual connection, not an instruction to draw arrows in the real game.
  c.save();c.globalAlpha=this.annotations();c.setLineDash([6,9]);
  line([iso(-190,101,4),iso(-102,12,4),iso(52,-47,4),iso(173,-110,4)],P.blue,2.5);c.setLineDash([]);
  ellipse(p[0],p[1]+2,48,18,'#2f5faa10');
  c.beginPath();c.ellipse(p[0],p[1]+2,48,18,0,0,Math.PI*2);c.strokeStyle=P.blue;c.lineWidth=2;c.stroke();c.restore();
  this.drawChildren(c);
 }
}
