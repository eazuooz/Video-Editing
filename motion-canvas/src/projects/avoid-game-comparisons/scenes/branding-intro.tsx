import {makeScene2D,Img,Node,Txt,Rect} from '@motion-canvas/2d';
import {createSignal,usePlayback} from '@motion-canvas/core';
import {PAPER} from '../../../styles/research-paper';
import cats from '../../../../../shared/assets/branding/yamyamcoding-cats-original.png';

const ease=(n:number)=>{const q=Math.max(0,Math.min(1,n));return 1-Math.pow(1-q,3);};
// User-provided logo, unmodified. Only the layout/scale/opacity is animated.
export default makeScene2D(function*(view){
  view.fill(PAPER.background);const clock=createSignal(0);
  const open=()=>ease((clock()-.10)/.55),show=()=>ease((clock()-.32)/.33);
  view.add(<Rect width={1920} height={22} y={-529} fill={'#ffdc16'}/>);
  view.add(<Rect x={()=>-505+505*open()} width={()=>480+1060*open()} height={520} stroke={'#161616'} lineWidth={7}/>);
  view.add(<Rect x={()=>-505+505*open()} width={()=>472+1060*open()} height={16} y={-248} fill={'#ffdc16'}/>);
  view.add(<Img src={cats} width={400} height={400} x={-500} y={()=>16*(1-ease(clock()/.4))} scale={()=>.92+.08*ease(clock()/.45)} opacity={()=>ease(clock()/.22)}/>);
  view.add(<Node opacity={show} y={()=>18*(1-show())}>
    <Rect width={3} height={242} x={-236} fill={'#d6d2c9'}/>
    <Txt text={'얌얌코딩'} x={240} y={-66} fontFamily={PAPER.font} fontSize={116} fontWeight={900} fill={'#111111'}/>
    <Rect x={240} y={100} width={()=>570*show()} height={23} fill={'#ffdc16'}/>
    <Txt text={'게임 기획·디자인'} x={240} y={68} fontFamily={PAPER.font} fontSize={64} fontWeight={700} fill={'#202020'}/>
  </Node>);
  const playback=usePlayback(),start=playback.frame;
  while(playback.frame-start<120){clock((playback.frame-start)/60);yield;}
  clock(2);
});
