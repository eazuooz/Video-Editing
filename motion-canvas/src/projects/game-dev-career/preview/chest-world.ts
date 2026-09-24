import {Node} from '@motion-canvas/2d';
import {BBox, createSignal} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

type V = [number,number,number];
type Face = {points:V[];color:string;edge?:string};
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const ramp=(t:number,a:number,b:number)=>{const p=clamp((t-a)/(b-a));return p*p*(3-2*p);};

// Original procedural 2.5D illustration. Lid vertices rotate about a physical
// hinge; the orbit and wireframe reveal the same geometry used in shaded views.
export class ChestWorld extends Node {
  readonly clock=createSignal(0);
  readonly phase=createSignal(0);
  readonly chapter=createSignal(0);
  // Default zero preserves the already-approved preview; the full episode can
  // compare a wrong centre pivot with the actual hinge without changing it.
  readonly badPivot=createSignal(0);
  readonly grayscale=createSignal(0);
  protected getCacheBBox(){return new BBox(-700,-620,1400,1100);}
  protected draw(c:CanvasRenderingContext2D){
    const p=this.phase(),t=this.clock(),chapter=this.chapter();
    const yaw=chapter===4?-.38+1.16*ramp(p,.06,.76):.06*Math.sin(t*.22);
    const rotate=([x,y,z]:V):V=>[x*Math.cos(yaw)-z*Math.sin(yaw),y,x*Math.sin(yaw)+z*Math.cos(yaw)];
    const project=(v:V):[number,number]=>{const [x,y,z]=rotate(v);return[(x-z)*.88,(x+z)*.42-y];};
    const poly=(points:[number,number][],fill:string|null,stroke?:string,width=1.5)=>{
      c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();
      if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}
    };
    const line=(points:[number,number][],stroke:string,width=2)=>{c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=stroke;c.lineWidth=width;c.stroke();};
    const circle=(x:number,y:number,r:number,fill:string,stroke?:string,w=2)=>{c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=w;c.stroke();}};
    c.save();c.scale(1.45,1.45);c.translate(0,62);
    const faces:Face[]=[];
    const box=(x:number,y:number,z:number,w:number,h:number,d:number,colors:string[],transform?:(v:V)=>V)=>{
      let v:V[]=[[-w/2,0,-d/2],[w/2,0,-d/2],[w/2,0,d/2],[-w/2,0,d/2],[-w/2,h,-d/2],[w/2,h,-d/2],[w/2,h,d/2],[-w/2,h,d/2]].map(q=>[q[0]+x,q[1]+y,q[2]+z] as V);
      if(transform)v=v.map(transform);
      [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]].forEach((indices,i)=>faces.push({points:indices.map(i=>v[i]),color:colors[i%colors.length]}));
    };
    const palette=['#20416f','#315d94','#4d78b0','#648cc0','#99b4d4'];
    const gold=['#bca249','#d0b559','#e8cc70','#edda95','#f3e4b6'];
    const sketch=chapter===3?1-ramp(p,.47,.7):0;
    const wire=chapter===4?ramp(p,.22,.3)*(1-ramp(p,.48,.57)):0;
    const float=chapter===3?26*(1-ramp(p,.22,.47)):0;
    let open=chapter===0?ramp(p,.4,.75):chapter===1?ramp(p,.61,.78):chapter===2?ramp(p,.18,.37):chapter===4?ramp(p,.6,.82):chapter===5?.88:0;
    const ground:V[]=[[-250,-8,-200],[250,-8,-200],[250,-8,200],[-250,-8,200]];
    poly(ground.map(project),'#edf1f5');
    poly([[-250,-8,200],[250,-8,200],[250,-35,200],[-250,-35,200]].map(v=>project(v as V)),'#d4dce5');
    poly([[250,-8,-200],[250,-8,200],[250,-35,200],[250,-35,-200]].map(v=>project(v as V)),'#c3cedb');
    c.save();c.globalAlpha=.55;
    for(let q=-200;q<=200;q+=50){line([project([q,-7,-200]),project([q,-7,200])],'#d0d9e3',.8);line([project([-250,-7,q]),project([250,-7,q])],'#d0d9e3',.8);}c.restore();
    c.save();const shadow=project([20,0,15]);c.translate(...shadow);c.scale(1,.42);circle(0,0,153,'#c1cbd8');c.restore();
    box(0,5,0,246,118,164,palette);
    // Dark inner cavity and a slim rim are exposed when the lid opens.
    box(0,124,0,250,8,168,gold);
    faces.push({points:[[-107,133,-67],[107,133,-67],[107,133,67],[-107,133,67]],color:'#193657'});
    [-76,76].forEach(x=>box(x,7,84,18,116,6,gold));
    [-66,-22,22,66].forEach(z=>box(124,10,z,2,105,2,['#7d9abd']));
    box(0,73,87,27,37,8,gold);
    const pivotZ=-84*(1-this.badPivot());
    const lidTransform=([x,y,z]:V):V=>{const a=open*1.18,dy=y-134,dz=z-pivotZ;return[x,134+dy*Math.cos(a)+dz*Math.sin(a)+float,pivotZ+dz*Math.cos(a)-dy*Math.sin(a)];};
    box(0,134,0,258,27,177,palette,lidTransform);
    [-79,79].forEach(x=>box(x,161,0,20,5,180,gold,lidTransform));
    faces.sort((a,b)=>{
      const depth=(f:Face)=>f.points.reduce((s,v)=>{const q=rotate(v);return s+q[0]+q[2]+q[1]*.85;},0)/f.points.length;
      return depth(a)-depth(b);
    });
    faces.forEach(f=>{const pts=f.points.map(project);let color=f.color;
      if(this.grayscale()>0){const hex=parseInt(color.slice(1),16),r=hex>>16,g=(hex>>8)&255,b=hex&255,y=.2126*r+.7152*g+.0722*b,a=this.grayscale();color=`rgb(${Math.round(r+(y-r)*a)},${Math.round(g+(y-g)*a)},${Math.round(b+(y-b)*a)})`;}
      poly(pts,sketch>.9||wire>.9?'#f7f9fc':color,(sketch>.1||wire>.1)?P.blue:undefined,(sketch>.1||wire>.1)?1.2:.5);});
    if(sketch>.01){
      c.save();c.globalAlpha=sketch*.5;c.setLineDash([6,6]);
      [[[-190,0,84],[250,0,84]],[[-129,0,-170],[-129,0,210]],[[0,0,0],[0,245,0]]].forEach(points=>line(points.map(v=>project(v as V)),P.blue,1));c.restore();
    }
    // Simple loose highlight strokes, not an emissive/neon effect.
    if(chapter===0||chapter===5){
      const lift=ramp(p,.45,.78),q=project([0,172+lift*62,0]);
      c.save();c.globalAlpha=lift;circle(q[0],q[1],22,P.yellow,'#bba048',2);
      line([[q[0],q[1]-12],[q[0],q[1]+12]],'#fff8d9',3);
      for(let k=0;k<3;k++){const a=(k-1)*.48;line([[q[0]+Math.sin(a)*44,q[1]-Math.cos(a)*44],[q[0]+Math.sin(a)*57,q[1]-Math.cos(a)*57]],'#d4b654',2);}c.restore();
    }
    if(chapter===1){
      const key=ramp(p,.25,.4)*(1-ramp(p,.55,.67));c.save();c.globalAlpha=key;
      const q=project([-180,95,-10]);circle(q[0],q[1],16,P.yellow,'#bda44c',3);circle(q[0],q[1],6,'#fff');
      line([[q[0]+14,q[1]],[q[0]+62,q[1]]],'#bda44c',8);line([[q[0]+45,q[1]],[q[0]+45,q[1]+13]],'#bda44c',7);
      c.restore();
    }
    if(chapter===2){
      const q=project([5,0,210]);
      for(let k=0;k<4;k++){const x=q[0]+k*50-75;poly([[x-20,q[1]-20],[x+20,q[1]-20],[x+20,q[1]+20],[x-20,q[1]+20]],'#fff',P.line,1.5);}
      const travel=ramp(p,.32,.48),start=project([0,190,0]);
      const x=start[0]+(q[0]-75-start[0])*travel,y=start[1]+(q[1]-start[1])*travel-Math.sin(travel*Math.PI)*65;
      circle(x,y,12,P.yellow,'#bda44c',2);
      if(p>.68){c.save();c.globalAlpha=ramp(p,.68,.76);const last=q[0]+75;line([[last-7,q[1]],[last-1,q[1]+7],[last+10,q[1]-8]],P.blue,3);c.restore();}
    }
    if(chapter===4&&p>.54){
      const h=project([135,134,pivotZ]);c.save();c.globalAlpha=ramp(p,.54,.63);
      circle(h[0],h[1],7,P.yellow,P.ink,1);line([[h[0]+10,h[1]-5],[h[0]+90,h[1]-50]],P.blue,1.5);
      c.font="600 20px 'Malgun Gothic', sans-serif";c.fillStyle=P.blue;c.textAlign='center';c.fillText(this.badPivot()>.5?'잘못된 축':'회전축',h[0]+88,h[1]-64);
      c.restore();
    }
    c.restore();this.drawChildren(c);
  }
}
