import {Node} from '@motion-canvas/2d';
import {BBox,createSignal} from '@motion-canvas/core';

// Editable text, not a raster overlay. Reference treatment: white rectangle,
// thin black outline and a hard forest-green offset shadow, without rounding.
export class CaptionBox extends Node {
  readonly text=createSignal('');
  protected getCacheBBox(){return new BBox(-860,-100,1736,218);}
  protected draw(c:CanvasRenderingContext2D){
    const text=this.text().trim();if(!text)return;
    c.save();c.font="500 48px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
    const lines:string[]=[];let current='';
    for(const word of text.split(/\s+/)){
      const next=current?`${current} ${word}`:word;
      if(current&&c.measureText(next).width>1570){lines.push(current);current=word;}else current=next;
    }
    if(current)lines.push(current);
    const width=Math.ceil(Math.max(...lines.map(line=>c.measureText(line).width)))+44;
    const height=lines.length*62+22;
    c.fillStyle='#073c32';c.fillRect(-width/2+14,-height/2+14,width,height);
    c.fillStyle='#fff';c.fillRect(-width/2,-height/2,width,height);
    c.strokeStyle='#161b18';c.lineWidth=3;c.strokeRect(-width/2,-height/2,width,height);
    c.fillStyle='#080b09';c.textAlign='center';c.textBaseline='middle';
    lines.forEach((line,i)=>c.fillText(line,0,(i-(lines.length-1)/2)*62-1));
    c.restore();this.drawChildren(c);
  }
}
