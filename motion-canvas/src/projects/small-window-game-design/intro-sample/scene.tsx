import {makeScene2D,Node} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER} from '../../../styles/research-paper';

// Editable pixel-art reinterpretation of the channel's thumbnail chicken.
// No crop/repainting of the raster thumbnail or generated character asset.
const pixels=[
 '        KK  KK      ',
 '       KPPKKPPK     ',
 '       KPPPPPPK     ',
 '      KPPPKKKKK     ',
 '      KPKKWWWWWK    ',
 '      KWWWWWWWWWK   ',
 '      KWWWWKWKWWK   ',
 '     KWWWWWKWKWWKKK ',
 ' KK  KWWWWWWWWWKYYK ',
 'KWWKKWWWWWRWWWWKYYK ',
 ' KWWWWWWWWWWWWWWKK  ',
 '  KWWWWWWWWWWWWWK   ',
 '  KWWWSWWWWWWWWWK   ',
 '   KWWWSSWWWWWWK    ',
 '    KWWWWWWWWWK     ',
 '     KKKKKKKKK      ',
 '      KYK  KYK      ',
 '     KYYK KYYK      ',
 '     KKK  KKK       ',
];
const palette:Record<string,string>={K:'#111111',P:'#f695ab',W:'#ffffff',S:'#dedede',Y:'#ffdb1a',R:'#ff9da5'};
const smooth=(x:number)=>{const q=Math.max(0,Math.min(1,x));return 1-Math.pow(1-q,3);};
class Intro extends Node{
 constructor(private clock:()=>number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),open=smooth((t-.12)/.55),w=460+1080*open,show=smooth((t-.40)/.38),yellow='#ffdc16';
  c.save();c.fillStyle=yellow;c.fillRect(-960,-540,1920,22);
  c.strokeStyle='#161616';c.lineWidth=8;c.strokeRect(-w/2,-215,w,430);
  c.fillStyle=yellow;c.fillRect(-w/2+4,-211,w-8,18);
  c.save();c.beginPath();c.rect(-w/2+18,-180,w-36,360);c.clip();c.globalAlpha=show;
  c.fillStyle=PAPER.ink;c.textAlign='center';c.textBaseline='middle';
  c.font="900 116px 'Malgun Gothic'";c.fillText('얌얌코딩',-342,7+(1-show)*24);
  c.fillRect(-52,-45,5,110);
  c.fillStyle=yellow;c.fillRect(23,57,665*show,25);
  c.fillStyle=PAPER.ink;c.font="700 68px 'Malgun Gothic'";c.fillText('게임 기획·디자인',348,6+(1-show)*24);
  c.restore();
  // The chicken follows the expanding edge, taking two small steps.
  const moving=Math.min(1,t/.85),bob=t<.85?-Math.abs(Math.sin(moving*Math.PI*2))*18:0;
  const px=Math.round((w/2-35)/10)*10,py=163+bob,unit=10;
  c.save();c.translate(px,py);c.imageSmoothingEnabled=false;
  for(let y=0;y<pixels.length;y++)for(let x=0;x<pixels[y].length;x++){const color=palette[pixels[y][x]];if(color){c.fillStyle=color;c.fillRect((x-10)*unit,(y-9)*unit,unit,unit);}}
  // Wing on the frame edge makes the pulling gesture explicit.
  c.fillStyle='#111';c.fillRect(-62,-25,54,28);c.fillStyle='#fff';c.fillRect(-53,-17,38,12);
  c.restore();
  if(t>.65&&t<1.15){c.globalAlpha=Math.sin((t-.65)/.5*Math.PI);c.fillStyle=yellow;c.fillRect(px+85,py-105,12,34);c.save();c.translate(px+125,py-65);c.rotate(.7);c.fillRect(0,0,12,32);c.restore();}
  c.restore();this.drawChildren(c);
 }
}
export default makeScene2D(function*(view){view.fill(PAPER.background);const clock=createSignal(0);view.add(new Intro(()=>clock()));yield* tween(2,p=>clock(p*2));});
