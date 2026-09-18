import {Circle, Line, Node, Rect, Txt, Video, View2D} from '@motion-canvas/2d';
import {createSignal, tween, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import edit from '../../../../../projects/gpt-astra-showcase/planning/edit-plan.json';

const examples=import.meta.glob('../assets/examples/scene*.mp4',{eager:true,query:'?url',import:'default'}) as Record<string,string>;
class ReviewVideo extends Video {protected override video(){const v=super.video();v.muted=true;return v;}}

// Original isometric editorial objects, not a recreation of an external UI.
function block(parent:Node,x:number,y:number,w:number,h:number,d:number,color:string,label=''){
  const node=new Node({x,y}); parent.add(node);
  node.add(<Line points={[[-w/2,-h],[w/2,-h],[w/2+d,-h-d],[-w/2+d,-h-d]]} closed fill={'#eef3f9'} stroke={P.line} lineWidth={2}/>);
  node.add(<Line points={[[w/2,-h],[w/2+d,-h-d],[w/2+d,-d],[w/2,0]]} closed fill={'#bdcce1'} stroke={P.line} lineWidth={2}/>);
  node.add(<Rect x={0} y={-h/2} width={w} height={h} fill={color} stroke={P.ink} lineWidth={2}/>);
  if(label)node.add(<Txt text={label} y={-h/2} fontFamily={P.font} fontSize={40} fontWeight={700} fill={P.ink}/>);
  return node;
}
function platform(parent:Node){
  parent.add(<Line points={[[-180,35],[0,115],[180,35],[0,-45]]} closed fill={'#e6eaf0'} stroke={P.line} lineWidth={2}/>);
  parent.add(<Line points={[[-180,18],[0,98],[180,18],[0,-62]]} closed fill={'#f8fafc'} stroke={P.line} lineWidth={2}/>);
}
function glyph(parent:Node,kind:string,column:number,time:()=>number){
  const color=column===2?P.yellow:P.blueLight;
  if(kind==='world'||kind==='integration'){
    block(parent,-60,10,72,70+column*25,22,color);
    block(parent,37,30,68,110-column*12,22,'#ffffff');
    block(parent,7,65,95,35,18,P.yellow);
    parent.add(<Circle x={()=>18+Math.sin(time())*45} y={62} size={17} fill={P.blue}/>);
  }else if(kind==='inspection'){
    block(parent,0,30,125,142,25,color,column===1?'앞':column===0?'색':'뒤');
    parent.add(<Circle x={()=>Math.cos(time()*1.3)*105} y={()=>-40+Math.sin(time()*1.3)*24} size={20} fill={column===1?'#c43b3b':P.blue}/>);
  }else if(kind==='shader'){
    parent.add(<Circle x={0} y={-25} size={150} fill={column===2?'#92b4d8':'#dfeaf5'} stroke={P.ink} lineWidth={2}/>);
    parent.add(<Line points={[[-58,-80],[-20,-25],[-58,26]]} stroke={P.blue} lineWidth={18}/>);
    parent.add(<Circle x={37} y={-51} size={35} fill={'#ffffff'}/>);
    block(parent,0,64,140,27,18,color);
  }else if(kind==='interaction'){
    if(column===1){block(parent,-25,-22,47,49,15,P.yellow);block(parent,-25,39,65,63,18,P.blueLight);}
    else block(parent,-10,38,145,133,20,color,column===0?'불':'휴식');
  }else{
    block(parent,-14,41,150,135,25,color,kind==='intro'?['8','11','GO'][column]:kind==='outro'?'?':['01','02','03'][column]);
    for(let j=0;j<3;j++)parent.add(<Rect x={-17} y={56+j*10} width={96-j*12} height={4} fill={P.blue}/>);
  }
}

export function* explanation(view:View2D,index:number,seconds:number){
  const scene=edit.scenes[index],clock=createSignal(0),root=new Node({opacity:0}); view.add(root);view.fill(P.background);
  root.add(<Txt text={scene.title} y={-402} width={1740} textAlign={'center'} fontFamily={P.font} fontSize={62} fontWeight={700} fill={P.ink}/>);
  root.add(<Txt text={scene.takeaway} y={-287} width={1730} textAlign={'center'} fontFamily={P.font} fontSize={34} fill={P.blue}/>);
  const labels=scene.steps;
  for(let i=0;i<3;i++){
    const x=(i-1)*530,unit=new Node({x,y:()=>50+Math.sin(clock()*.7+i)*6,opacity:()=>Math.min(1,Math.max(0,(clock()-i*.6)/.5))});
    root.add(unit);platform(unit);glyph(unit,scene.kind,i,clock);
    unit.add(<Txt text={labels[i]} y={201} width={480} textAlign={'center'} fontFamily={P.font} fontSize={32} fontWeight={600} fill={P.ink}/>);
  }
  const rail=new Line({points:[[-715,357],[715,357]],stroke:P.line,lineWidth:2});root.add(rail);
  root.add(<Circle x={()=>-715+1430*Math.min(1,clock()/Math.max(1,seconds-.5))} y={357} size={15} fill={P.blue}/>);
  yield* tween(seconds-1/60,p=>{clock(p*seconds);root.opacity(Math.min(1,p*seconds/.45));});root.remove();
}
export function* showcaseScene(view:View2D,index:number){
  const scene=edit.scenes[index],example=scene.cuts.reduce((n,c)=>n+c.out-c.in,0);view.fill(P.background);
  if(example>0){
    const src=examples[`../assets/examples/scene${scene.id}.mp4`];
    if(!src)throw new Error(`Prepare rights-pending review clips first: scene${scene.id}`);
    const video=new ReviewVideo({src,width:1920,height:1080});view.add(video);yield video;video.play();yield* waitFor(example);video.pause();video.remove();
  }
  // Video loading yields one frame; graphic-only intro/outro do not.
  yield* explanation(view,index,scene.duration-example+(example===0?1/60:0));
}
