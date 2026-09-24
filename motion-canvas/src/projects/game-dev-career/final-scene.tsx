import {Circle,Line,Node,Rect,Txt,Video,View2D} from '@motion-canvas/2d';
import {createSignal,tween,useScene} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import {ChestWorld,ramp} from './preview/chest-world';
import {CaptionBox} from './preview/caption-box';
import board from '../../../../projects/game-dev-career/planning/storyboard.v1.json';
import manifest from '../../../../projects/game-dev-career/project.json';
import timing from './timing.generated.json';
import footage01 from './assets/examples-v3/01.mp4';
import footage02 from './assets/examples-v3/02.mp4';
import footage03 from './assets/examples-v3/03.mp4';
import footage04 from './assets/examples-v3/04.mp4';
import footage05 from './assets/examples-v3/05.mp4';
import footage06 from './assets/examples-v3/06.mp4';
import footage07 from './assets/examples-v3/07.mp4';
import footage08 from './assets/examples-v3/08.mp4';
import footage09 from './assets/examples-v3/09.mp4';
const footage=[footage01,footage02,footage03,footage04,footage05,footage06,footage07,footage08,footage09];
class MutedVideo extends Video {protected video(){const v=super.video();v.muted=true;v.volume=0;return v;}}

// One independently editable scene per approved script chapter.
export function* finalScene(view:View2D,index:number,captions=true){
  const scene=timing.scenes[index],s=board.scenes[index],duration=scene.frames/60;
  const overrides:Record<string,number>=manifest.editing.exampleSecondsByScene;
  const example=overrides[scene.id]??manifest.editing.exampleSeconds,time=createSignal(0);
  const local=()=>Math.max(0,time()-example),phase=()=>local()/(duration-example);
  const active=()=>Math.min(2,Math.floor(phase()*3));
  view.fill(P.background);
  const explanation=new Node({opacity:()=>ramp(time(),example-.25,example+.25)});view.add(explanation);
  explanation.add(<>
    <Line points={[[-848,-433],[-802,-433]]} stroke={P.blue} lineWidth={5}/>
    <Txt x={-779} y={-433} offset={[-1,0]} text={s.role} fontFamily={P.font} fontSize={23} fontWeight={600} letterSpacing={2} fill={P.blue}/>
    <Txt x={-846} y={-292} offset={[-1,0]} text={s.headline} fontFamily={P.font} fontSize={56} lineHeight={76} fontWeight={700} fill={P.ink}/>
  </>);
  const world=new ChestWorld({x:440,y:85,scale:()=>.74+.04*ramp(phase(),.1,.9)});
  world.clock(time);world.phase(phase);world.chapter([0,0,1,2,3,4,5,0,5][index]);explanation.add(world);
  const cueAt=(part:string,fallback:number)=>scene.cues.find(c=>c.ko.includes(part))?.start??fallback;
  if(index===4){
    const gray=cueAt('실루엣',duration*.58),small=cueAt('실제 게임 화면',duration*.76);
    world.grayscale(()=>ramp(time(),gray,gray+.5)*(1-ramp(time(),small,small+.5)));
    world.scale(()=>.78-.34*ramp(time(),small,small+2));
  }
  if(index===5){
    const bad=cueAt('크기와 방향',duration*.58),good=cueAt('작은 소품',duration*.78);
    world.badPivot(()=>ramp(time(),bad,bad+.5)*(1-ramp(time(),good,good+.5)));
    world.phase(()=>time()<bad?Math.min(.53,phase()*.9):.6+.35*ramp(time(),bad,duration-2));
  }
  if(index===3){
    explanation.add(<>
      <Rect x={-500} y={50} width={700} height={278} fill={P.panel}/>
      <Txt x={-810} y={-58} offset={[-1,0]} text={'플레이어 입력'} fontFamily={P.font} fontSize={31} fontWeight={600} fill={()=>active()===0?P.blue:P.ink}/>
      <Txt x={-810} y={34} offset={[-1,0]} text={'게임 규칙과 상태'} fontFamily={P.font} fontSize={31} fontWeight={600} fill={()=>active()===1?P.blue:P.ink}/>
      <Txt x={-810} y={126} offset={[-1,0]} text={'화면과 사운드 결과'} fontFamily={P.font} fontSize={31} fontWeight={600} fill={()=>active()===2?P.blue:P.ink}/>
      <Txt x={-840} y={250} offset={[-1,0]} text={'구현 · 도구 · 디버깅'} fontFamily={P.font} fontSize={29} fill={P.blue}/>
    </>);
  }else if(index===6){
    const groups=[
      ['기획','게임플레이 · 시스템 · 레벨 · UI/UX'],
      ['프로그래밍','게임플레이 · 엔진 · 그래픽 · 서버 · 도구'],
      ['아트','콘셉트 · 캐릭터 · 배경 · 애니메이션 · VFX'],
    ];
    groups.forEach((group,i)=>explanation.add(<Node x={-510} y={-42+i*108}>
      <Rect width={690} height={88} fill={()=>active()===i?P.blueLight:P.panel} stroke={()=>active()===i?P.blue:P.line} lineWidth={1.5}/>
      <Txt x={-310} text={group[0]} fontFamily={P.font} fontSize={28} fontWeight={700} fill={P.blue}/>
      <Txt x={-205} offset={[-1,0]} text={group[1]} fontFamily={P.font} fontSize={25} fontWeight={500} fill={P.ink}/>
    </Node>));
  }else if(index===2){
    ['무엇을 하게 할까?','어떤 규칙으로 작동할까?','플레이해보니 재미있는가?'].forEach((text,i)=>explanation.add(<Node x={-511} y={-29+i*107}>
      <Rect width={664} height={77} fill={()=>active()===i?P.blueLight:P.panel} stroke={()=>active()===i?P.blue:P.line} lineWidth={1.5}/>
      <Txt text={text} fontFamily={P.font} fontSize={31} fontWeight={600} fill={P.ink}/>
    </Node>));
  }else if(index===1){
    ['기획 · 경험과 규칙','프로그래밍 · 기능과 도구','2D · 콘셉트와 정보','3D · 공간과 움직임'].forEach((text,i)=>explanation.add(new Txt({text,x:-565,y:-40+i*87,fontSize:32,fontFamily:P.font,fontWeight:600,fill:()=>i===Math.min(3,Math.floor(phase()*4))?P.blue:P.muted})));
  }else{
    s.labels.forEach((text,i)=>explanation.add(<Node y={-30+i*102}>
      <Line points={[[-837,-20],[-837,20]]} stroke={()=>active()===i?P.blue:P.line} lineWidth={4}/>
      <Txt x={-810} offset={[-1,0]} text={text} fontFamily={P.font} fontSize={35} fontWeight={600} fill={()=>active()===i?P.blue:P.muted}/>
    </Node>));
  }
  const exampleRoot=new Node({opacity:()=>1-ramp(time(),example-.25,example+.25)});view.add(exampleRoot);
  // Actual licensed development / gameplay excerpts precede our own explanation.
  // Source audio is in the continuous mix; individual video nodes remain muted.
  // Decode only real 30fps source frames, not 60 distinct seeks per second.
  const video=new MutedVideo({src:footage[index],width:1920,height:1080,time:()=>Math.min(Math.floor((time()+1e-6)*30)/30,example-1/30)});
  exampleRoot.add(video);
  yield video;
  if(captions&&useScene().variables.get('captions',true)()){const cap=new CaptionBox({y:manifest.editing.captionStyle.centerYPx});cap.text(()=>scene.cues.find(c=>time()>=c.start&&time()<c.end)?.ko??'');view.add(cap);}
  // One signal drives footage, procedural geometry and the measured captions.
  yield* tween(duration-1/60,p=>time(p*(duration-1/60)));
  video?.pause();
}
