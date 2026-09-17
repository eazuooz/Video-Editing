import {Node} from '@motion-canvas/2d';
import {BBox, createSignal} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {Art, iso, lerp, ramp, Point} from '../../let-them-play/editorial/art';

// Original animated teaching dioramas. These are not captured game interfaces.
// X/Z objects share one isometric ground plane, height, cast shadows and depth order.
export class RewardWorld extends Node {
  readonly chapter = createSignal(0);
  readonly clock = createSignal(0);
  readonly span = createSignal(30);
  protected getCacheBBox() {return new BBox(-960, -500, 1920, 1000);}
  protected draw(c: CanvasRenderingContext2D) {
    const t=this.clock(), p=Math.min(1,t/this.span()), i=this.chapter(), a=new Art(c);
    c.save();
    // A gentle physical dolly; unlike slide transitions, the action continues throughout.
    c.translate(-18+36*ramp(p,0,1), 68-14*ramp(p,0,1));
    c.scale(1.30+.06*ramp(p,.05,.9),1.30+.06*ramp(p,.05,.9));
    const fade=(alpha:number,f:()=>void)=>{c.save();c.globalAlpha*=Math.max(0,Math.min(1,alpha));f();c.restore();};
    const text=(s:string,x:number,z:number,h=0,size=22,color:string=P.ink)=>{
      const q=iso(x,z,h); c.font=`600 ${size}px 'Malgun Gothic',sans-serif`;c.fillStyle=color;c.textAlign='center';c.fillText(s,...q);
    };
    const tree=(x:number,z:number,s=1)=>a.tree(x,z,s);
    const coin=(x:number,z:number,h=17,alpha=1)=>fade(alpha,()=>{
      const q=iso(x,z,h);a.oval(q[0]+2,q[1]+3,11,14,'#b69b44');a.oval(q[0],q[1],11,14,P.yellow);
      a.line([[q[0],q[1]-6],[q[0],q[1]+6]],'#fff8d6',2);
    });
    const bag=(x:number,z:number,base=0,s=1)=>{
      const q=iso(x,z,base);c.save();c.translate(...q);c.scale(s,s);
      a.oval(5,3,35,12,'#c7cecb');a.poly([[-29,-72],[18,-72],[31,-57],[31,-8],[-18,-1],[-32,-13]],'#b39770');
      a.poly([[18,-72],[31,-57],[31,-8],[18,-19]],'#826b4f');a.poly([[-29,-72],[18,-72],[18,-19],[-29,-14]],'#d3b68a');
      a.line([[-17,-72],[-17,-86],[4,-87],[10,-73]],'#75654f',5);a.poly([[-22,-43],[11,-45],[11,-24],[-22,-22]],'#ecdbc0');
      a.line([[-28,-61],[18,-61]],'#836f54',3);c.restore();
    };
    const shop=(x:number,z:number)=>{
      a.box(x,z,158,112,127,'#f2ead7','#dfd5be','#b4b19b');
      a.box(x,z,184,133,15,'#a7b8ae','#7b948b','#627e75',127);
      a.box(x,z-42,151,36,52,'#b9cabe','#8ca69a','#738f82',140);
      a.box(x+23,z+59,54,5,86,'#7c98a8','#708a94','#5f7887',1);
      a.box(x-45,z+59,41,7,36,'#bdd5da','#9bbdc7','#769ba9',59);
      const q=iso(x,z+69,115);a.rect(q[0]-63,q[1]-20,126,29,'#fbf8ed');
      c.font="700 16px 'Segoe UI',sans-serif";c.textAlign='center';c.fillStyle='#526b61';c.fillText('GENERAL STORE',q[0],q[1]);
      bag(x-80,z+76,34,.72);
    };
    const ore=(x:number,z:number,alpha=1,h=10)=>fade(alpha,()=>{a.box(x,z,23,22,25,'#d9e8ee','#8eaebf','#658aa4',h);});
    const chest=(x:number,z:number,open=0)=>{
      a.box(x,z,82,62,40,'#d7bd8e','#ac926c','#886e4d');
      a.box(x,z,88,67,9,'#efd99f','#c5ac76','#9f875a',43+open*26);
      const q=iso(x,z+34,29);a.rect(q[0]-4,q[1]-6,8,13,P.yellow);
    };
    const grid=(x:number,z:number,rows:number,filled:number,alpha=1)=>fade(alpha,()=>{
      for(let r=0;r<rows;r++)for(let k=0;k<6;k++){
        const xx=x+(k-2.5)*34,zz=z+(r-(rows-1)/2)*34;
        a.box(xx,zz,30,30,6,'#f9fbfc','#d9e1e5','#bccbd1',12);
        if(r*6+k<filled)a.box(xx,zz,14,14,18,P.blueLight,'#9cb6ce',P.blue,18);
      }
    });
    const foot=(pts:Point[],alpha=1)=>fade(alpha,()=>a.path(pts,21));
    const sword=(x:number,z:number,h=90,alpha=1)=>fade(alpha,()=>{
      const q=iso(x,z,h);c.save();c.translate(...q);c.rotate(-.23);
      a.poly([[-8,6],[-12,-68],[0,-93],[12,-68],[8,6]],'#d9e6ec');
      a.poly([[0,-93],[12,-68],[8,6],[0,6]],'#7696aa');a.line([[-23,7],[23,7]],'#ac8f43',7);a.line([[0,12],[0,41]],'#526e80',9);c.restore();
    });

    if(i===0||i===2){
      a.floor('grass');foot([[-265,128],[-116,108],[48,57],[164,-9]]);
      if(i===0){tree(-266,-125,.9);tree(-151,-156,.7);}shop(186,-104);tree(303,110,.7);
      const travel=ramp(p,.12,.78),x=lerp(-255,54,travel),z=lerp(130,25,travel);
      const spots:Point[]=[[-158,99],[-56,68],[46,27]];
      spots.forEach(([cx,cz],k)=>{const at=.28+k*.19;coin(cx,cz,25+Math.sin(t*1.7+k)*4,1-ramp(p,at,at+.07));
        fade(ramp(p,at,at+.05)*(1-ramp(p,at+.08,at+.2)),()=>text('+100',cx,cz,165+(p-at)*100,25,'#846c28'));});
      a.hero(x,z,t,travel>0&&travel<1?1:0);
      a.ring(103,-25,.45+.2*Math.sin(t));
      // The exact same hypothetical values as the approved narration; not a game HUD.
      text('2,000 G',186,-104,228,29);text('가방 확장',186,-104,270,21,P.muted);
      if(i===2){
        const q=iso(-160,-99,60);a.line([[q[0]-65,q[1]],[q[0]+65,q[1]]],P.blue,4);
        text('현재 1,700',-165,-98,81,23);text('목표까지 300',-165,-98,119,24,P.blue);
      }
    }else if(i===1){
      a.floor('stone');a.box(-190,-139,170,100,55,'#d0dadd','#acbdc5','#8d9eab');
      for(let k=0;k<5;k++)a.box(-260+k*39,-169,38,32,35+k%2*14,'#bfcbd0','#9aabb6','#8196a4',55);
      chest(240,-113);bag(223,-123,66,1.2);foot([[-246,137],[-77,50],[184,-44]]);
      const move=ramp(p,.08,.32);a.hero(lerp(-252,-107,move),lerp(129,60,move),t,move>0&&move<1?1:0);
      ore(-50,65);ore(22,59);ore(-1,126);grid(-117,163,2,12);
      const reject=ramp(p,.38,.46)*(1-ramp(p,.56,.67));
      ore(lerp(-50,-100,reject),lerp(65,135,reject),1,10+Math.sin(reject*Math.PI)*35);
      fade(ramp(p,.45,.55),()=>{a.ring(237,-119,.65);text('더 챙기고 싶다',228,-114,212,25,P.blue);});
      fade(ramp(p,.68,.8),()=>foot([[-80,59],[26,31],[175,-42]]));
    }else if(i===3){
      a.floor('wood');shop(225,-144);tree(-281,-143,.8);foot([[-260,79],[-60,71],[179,-63]]);
      const expanded=ramp(p,.2,.38),collect=ramp(p,.43,.89);
      grid(-62,56,2,12);grid(-62,130,2,Math.floor(collect*9),expanded);
      bag(46,-101,0,1+expanded*.42);a.ring(46,-101,.7*expanded);
      [0,1,2].forEach(k=>{const q=ramp(p,.48+k*.12,.58+k*.12);ore(lerp(-215+k*14,-62+k*34,q),lerp(147,151,q),1,15+Math.sin(q*Math.PI)*85);});
      a.hero(-239,61,t,.25);text(expanded<.5?'12칸':'24칸',-67,-11,115,40,P.blue);
    }else if(i===4){
      a.floor('grass');tree(-258,-163,.87);tree(265,-150,.85);tree(290,149,.8);a.box(156,-109,90,83,25,'#d7decf','#b3c3a9','#94a98d');
      const collect=ramp(p,.05,.38),choice=ramp(p,.45,.54),power=ramp(p,.58,.69);
      for(let k=0;k<10;k++){
        const angle=k*Math.PI*.2,q=ramp(p,.04+k*.025,.16+k*.025);
        a.crystal(Math.cos(angle)*190*(1-q),Math.sin(angle)*140*(1-q),20+Math.sin(t*2+k)*3,1-q);
      }
      a.hero(0,0,t,.25);
      c.save();c.globalAlpha=power*.6;const q=iso(0,0,4);c.beginPath();c.ellipse(...q,75+70*power,32+30*power,0,0,Math.PI*2);c.strokeStyle=P.blue;c.lineWidth=4;c.stroke();c.restore();
      [0,1,2].forEach(k=>fade(ramp(p,.38,.45)*(1-ramp(p,.54,.62)),()=>{
        a.box(-130+k*130,-95,94,50,70,k===1?P.yellow:'#e1e8ec','#b5c6d3','#809bad',30+Math.sin(t+k)*3);
        if(k===1)sword(0,-95,118);else a.crystal(-130+k*130,-95,115);
      }));
      for(let k=0;k<3;k++){const angle=t*.9+k*2.094;sword(Math.cos(angle)*134,Math.sin(angle)*81,75,power);}
      text(choice>.8?'선택 → 공격의 변화':collect>.9?'다음 강화는?':'경험치 수집',0,-150,155,29,P.blue);
    }else if(i===5){
      a.floor('grass');foot([[-259,147],[-58,39],[215,-102]]);tree(-245,-146,.8);shop(239,-137);
      const move=ramp(p,.15,.9);a.hero(lerp(-260,70,move),lerp(151,24,move),t,1);
      const clean=ramp(p,.4,.6);
      ['재료','업적','도감','퀘스트','재화','장비'].forEach((s,k)=>fade(1-clean,()=>{
        const q=iso(-225+(k%3)*200,15+Math.floor(k/3)*128,116+Math.sin(t+k)*8);
        a.poly([[q[0]-62,q[1]-24],[q[0]+62,q[1]-24],[q[0]+62,q[1]+15],[q[0]-62,q[1]+15]],'#edf2f5',P.line);
        c.font="22px 'Malgun Gothic'";c.fillStyle=P.muted;c.textAlign='center';c.fillText(s,q[0],q[1]+2);
      }));
      fade(clean,()=>{a.ring(149,-39,.8);bag(141,-40,72,.85);text('지금 원하는 목표',135,-41,174,24,P.blue);});
    }else if(i===6){
      a.floor('stone');foot([[-259,134],[-64,35],[180,-104]]);a.box(192,-113,110,94,29,'#d9dfd4','#b7c3b1','#98ac95');chest(192,-113, .2+.1*Math.sin(t));
      const walk=ramp(p,.1,.38);a.hero(lerp(-255,-91,walk),lerp(134,47,walk),t,walk>0&&walk<1?1:0);
      [0,1,2,3].forEach(k=>fade(ramp(p,.3+k*.12,.39+k*.12),()=>{
        const x=-61+k*69,z=35-k*39;a.ring(x,z,.5);text('?',x,z,60+Math.sin(t+k)*7,35,P.blue);
      }));
      text('9 / 10',-300,-85,39,41);text('남은 소재 1개',-300,-85,90,24,P.muted);
      text('시도 횟수는 미확정',192,-113,190,27,P.blue);
      // Never fill to 10 automatically: a random drop is not a promise of one more attempt.
    }else if(i===8){
      a.floor('stone');tree(-270,-161,.8);a.box(206,-130,133,104,67,'#b9c7ce','#8ca1ae','#698696');
      a.box(208,-132,78,50,22,'#bac9d3','#8297a6','#587a91',67);sword(207,-130,192,.4+.6*ramp(p,.62,.82));
      foot([[-238,132],[-71,36],[126,-80]]);
      for(let k=0;k<3;k++){a.box(-230+k*75,-86,51,46,28,'#dce4e6','#b0c4ca','#7f9eaa');ore(-230+k*75,-86,k<2?1:ramp(p,.5,.66),37);}
      const go=ramp(p,.12,.4),back=ramp(p,.55,.84);
      a.hero(p<.5?lerp(-198,-25,go):lerp(-25,136,back),p<.5?lerp(118,42,go):lerp(42,-71,back),t,1);
      text('목표 장비',207,-130,296,29,P.blue);
      text('필요 소재를 확인',-146,-88,95,24);a.ring(133,-69,.6*ramp(p,.62,.8));
    }else{
      a.floor('grass');tree(287,144,.76);shop(244,-122);chest(-191,-111);
      foot([[-244,134],[-84,56],[81,-22],[165,-68]]);
      const move=ramp(p,.07,.9);a.hero(lerp(-247,152,move),lerp(137,-57,move),t,1);
      const stops:Point[]=[[-191,109],[-47,39],[95,-22]];
      stops.forEach(([x,z],k)=>{a.ring(x,z,.25+.5*ramp(p,.12+k*.25,.2+k*.25));if(k===0)bag(x,z,72,.65);if(k===1)coin(x,z,80);if(k===2)sword(x,z,96);});
      text('원하는 변화',-211,104,176,22);text('목표까지 거리',-42,29,179,22);text('다음 행동',115,-33,193,22);
    }
    c.restore();this.drawChildren(c);
  }
}
