import {Node} from '@motion-canvas/2d';
import {BBox,createSignal} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {Art,iso,lerp,ramp} from './art';

/** Fictional teaching scenes, never represented as playable Zelda footage. */
export class DesignWorld extends Node {
 readonly chapter=createSignal(0);
 readonly phase=createSignal(0);
 readonly clock=createSignal(0);
 readonly alternative=createSignal(false);
 readonly comparison=createSignal(false);
 protected getCacheBBox(){return new BBox(-780,-490,1560,1000)}
 protected draw(c:CanvasRenderingContext2D){
  const a=new Art(c),i=this.chapter(),p=this.phase(),time=this.clock(),bad=this.alternative(),compare=this.comparison();
  c.save();
  // Camera is the sole changed variable in the two camera-composition pairs.
  if(compare&&bad&&(i===1||i===4)){c.translate(202,8);c.scale(1.25,1.25)}
  if(i===0){
   a.floor('grass');a.path([[-285,98],[-138,98],[-30,20],[140,-30],[262,-122]]);
   a.box(-269,-86,144,143,56,'#c7d2cc','#9cafac','#7c989a');a.arch(-268,-94,1);
   a.tree(-225,184,.65);a.tree(34,-136,.96);a.tree(80,-150,.69);a.tree(265,92,.84);
   a.box(190,-110,187,134,44,'#d8dfcf','#afbfad','#91a99b');a.tower(241,-154,122,44);
   const move=ramp(p,compare?.65:.22,compare?.9:.78);
   a.hero(lerp(-229,-43,move),lerp(80,27,move),time,move>0&&move<1?1:0);
   if(!bad)a.ring(147,-78,ramp(p,.16,.35));
  }else if(i===1){
   a.floor('stone');a.box(-145,-177,364,24,167,'#cdd8df','#9caebc','#7b94a6');
   for(let x=-282;x<2;x+=90)a.box(x,-174,4,29,165,'#e4eaed','#c8d4dc','#b2c3ce');
   a.arch(237,-126,1);a.box(-15,8,73,70,51,'#bacdd7','#7997ae','#547793');a.crystal(-15,8,91);
   a.path([[-245,147],[-15,63],[192,-85]],18,'#d5cdb9');
   a.hero(-237,119,time);a.ring(-15,8,ramp(p,.2,.4));a.ring(237,-126,ramp(p,.53,.72));
  }else if(i===3){
   a.floor('grass');a.tree(-280,-135,1.25);a.tree(-184,-161,.86);a.tree(284,125,.78);
   a.box(-35,-145,174,97,34,'#cbd5c8','#a4b5a8','#859d92');
   a.box(206,-76,98,70,45,'#ceb99a','#ab8e68','#8e765a');a.box(206,-76,110,80,7,'#decbb0','#b69d7b','#a58c6e',45);
   a.box(96,139,69,62,34,'#b9c5c1','#8fa4a1','#718e91');
   const arrive=ramp(p,.2,.43),pickup=ramp(p,.5,.59);
   a.crystal(-85,46,24,1-pickup);a.crystal(94,137,63);a.crystal(204,-76,77);
   a.path([[-238,133],[-119,77]],22);a.hero(lerp(-228,-119,arrive),lerp(124,77,arrive),time,arrive>0&&arrive<1?1:0);
   a.ring(-85,46,(1-pickup)*ramp(p,.07,.17));
  }else if(i===4){
   a.floor('stone');a.box(218,-139,132,132,19,'#d1dce3','#9fb5c3','#7b96aa');
   a.path([[-245,132],[-90,86],[218,-139]],22);a.arch(218,-139,ramp(p,.4,.6));
   a.box(-90,86,80,71,8,'#91abc3','#6b89a7','#526f8d');
   a.box(-90,86,65,56,6,p>.32?P.yellow:P.blueLight,'#b8c2b0','#809585',8);
   const first=ramp(p,.12,.31),last=ramp(p,.66,.94),x=p<.64?lerp(-252,-136,first):lerp(-136,226,last),z=p<.64?lerp(149,90,first):lerp(90,-139,last);
   a.hero(x,z,time,(first>0&&first<1)||(last>0&&last<1)?1:0);
   a.ring(-90,86,1-ramp(p,.58,.68));a.ring(218,-139,ramp(p,.42,.62));
  }else if(i===5){
   a.floor('snow');
   if(!bad)a.plane([[3,-190],[334,-190],[334,192],[3,192]],2,P.blueLight);
   a.tree(-276,-130,.95,true);a.tree(104,-167,1.15,true);a.tree(232,-91,.85,true);a.tree(272,120,.8,true);
   a.box(-282,146,91,75,21,'#dce6ed','#b6cbd8','#99b6ca');
   a.path([[-220,111],[98,45]],21,'#d9e1e5');
   const enter=ramp(p,.16,.5),back=ramp(p,.71,.94),x=p<.69?lerp(-235,99,enter):lerp(99,-190,back);
   a.hero(x,lerp(106,47,Math.max(0,(x+235)/334)),time,(enter>0&&enter<1)||(back>0&&back<1)?1:0);
   if(!bad){
    for(let j=0;j<9;j++){const q=iso(26+j*32,-145+(j*73)%300,50+Math.sin(time*.8+j)*9);a.line([[q[0]-4,q[1]],[q[0]+4,q[1]]],'#8eafc7',2);a.line([[q[0],q[1]-4],[q[0],q[1]+4]],'#8eafc7',2)}
   }
  }else if(i===6){
   a.floor('wood');a.box(-206,-130,166,42,153,'#bbcbce','#8fa5a9','#758f99');
   for(let j=0;j<3;j++){a.box(-240+j*44,-106,25,27,66,'#d1c4a7','#aa9571','#8f815f',25);a.box(-240+j*44,-106,25,27,33,'#acc4d4','#738fa7','#516f8c',104)}
   a.box(4,-55,138,72,55,'#e0cdb0','#b99e7a','#9b805e');
   a.box(4,-55,43,47,8,'#f4efd9','#d6cbb1','#beb599',57);a.crystal(4,-55,95);
   a.arch(247,-101,1);a.path([[-238,145],[-67,57],[144,-49],[247,-101]],18);
   const first=ramp(p,.1,.36),second=ramp(p,.51,.86),x=p<.5?lerp(-235,-67,first):lerp(-67,147,second),z=p<.5?lerp(145,57,first):lerp(57,-51,second);
   a.hero(x,z,time,(first>0&&first<1)||(second>0&&second<1)?1:0);
  }else if(i===7){
   a.floor('grass');a.tree(-270,121,.95);a.tree(-174,-121,.72);
   a.box(205,-122,211,171,70,'#dce4d5','#b7c7b5','#91aa99');
   for(let j=0;j<4;j++)a.box(63+j*30,-38-j*17,43,93,17+j*15,'#d4ddcd','#b0c1ac','#8fa68f');
   a.path([[-259,105],[-106,58],[53,-1]],26);a.arch(-38,-23,1);
   const move=ramp(p,.12,.54);a.hero(lerp(-248,-72,move),lerp(109,4,move),time,move>0&&move<1?1:0);
   c.save();c.globalAlpha*=bad?0:ramp(p,.58,.72);a.tower(235,-135,132,70);a.ring(178,-119,1,70);c.restore();
  }
  c.restore();this.drawChildren(c);
 }
}
