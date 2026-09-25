import {Node} from '@motion-canvas/2d';
import {BBox,createSignal} from '@motion-canvas/core';
export class LectureCaption extends Node {
  readonly text=createSignal('');
  protected getCacheBBox(){return new BBox(-850,-85,1720,185);}
  protected draw(c:CanvasRenderingContext2D){
    const text=this.text().trim();if(!text)return;
    c.save();c.font="500 44px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
    const lines:string[]=[];let line='';
    for(const word of text.split(/\s+/)){
      const next=line?`${line} ${word}`:word;
      if(line&&c.measureText(next).width>1540){lines.push(line);line=word;}else line=next;
    }
    if(line)lines.push(line);
    const w=Math.ceil(Math.max(...lines.map(l=>c.measureText(l).width)))+44,h=lines.length*58+22;
    c.fillStyle='#073c32';c.fillRect(-w/2+14,-h/2+14,w,h);
    c.fillStyle='#fff';c.fillRect(-w/2,-h/2,w,h);
    c.strokeStyle='#161b18';c.lineWidth=3;c.strokeRect(-w/2,-h/2,w,h);
    c.fillStyle='#080b09';c.textAlign='center';c.textBaseline='middle';
    lines.forEach((l,i)=>c.fillText(l,0,(i-(lines.length-1)/2)*58));c.restore();this.drawChildren(c);
  }
}
