import {makeScene2D,Node,Img,Txt,Rect,Circle,Line} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC'};
const FONT='Malgun Gothic';
export function makeLesson(topic:string,slug:string,timing:any){return makeScene2D(function*(view){
 const t=createSignal(0),clamp=(v:number)=>Math.max(0,Math.min(1,v));
 const f=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001));
 const section=()=>timing.sections.find((s:any)=>f()>=s.startFrame&&f()<s.endFrame)??timing.sections.at(-1);
 const p=()=>section().paragraph,game=()=>section().kind==='game',frac=()=>clamp((f()-timing.paragraphStarts[p()])/(timing.paragraphStarts[p()+1]-timing.paragraphStarts[p()]));
 const nativePhase=()=>topic==='viewfinder'?([0,.08,.15+.30*frac(),.45+.15*frac(),.60+.30*frac(),.90,.95][p()]??0):(p()===4?frac():p()<4?0:1);
 const ROOT='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/local/';
 const catPresence=()=>p()===6&&section().id==='close'?clamp((t()-section().start)/.25)*clamp((section().end-t())/.25):0;
 view.fill('#000000');
 // The common caption box reserves output y=1289..1483, including its shadow.
 // Keep all teaching labels above it; the closing cat owns the area below it.
 const world=new Node({position:[-20,-10],opacity:()=>!game()&&section().kind!=='diagram'?1:0});view.add(world);
 const nativeImage=new Rect({position:[0,topic==='gravity'?-35:0],size:[1000,topic==='gravity'?560:1000],clip:true});world.add(nativeImage);
 nativeImage.add(<Img src={()=>ROOT+timing.nativeFolder+'/'+String(timing.nativeTimelineAligned?f():Math.round(nativePhase()*(timing.nativeFrames-1))).padStart(5,'0')+'.jpg'} width={1000} height={1000} position={[0,topic==='gravity'?-155:0]}/>);
 if(topic==='viewfinder'){
  const labels=['사진으로 공간을 바꾼다','Mesh · 삼각형으로 만든 표면','노란 경계를 기준으로 나눈다','기존 구조를 자르고 바닥을 넣는다','새 바닥의 충돌 판정까지 연결','한 프레임 안에 많은 메시를 수정','사진이 바꾸는 것은 공간의 구조'];
  world.add(<Txt text={()=>labels[p()]} position={[-5,-405]} fontFamily={FONT} fontSize={37} fontWeight={700} fill={C.yellow}/>);
  world.add(<Rect position={[-10,260]} width={950} height={88} fill="#000000E8" opacity={()=>p()===6?0:1}/>);
  world.add(<Txt text={()=>p()===1?'작은 삼각형들이 하나의 표면이 된다':p()===2?'① 경계 정하기  →  ② 안 / 밖 나누기':p()===3?'③ 메시 절단  →  ④ 새 바닥 삽입':p()===4?'⑤ 충돌 판정  →  공이 통과':'Runtime Mesh Slicing · 런타임 메시 절단'} position={[-15,260]} fontFamily={FONT} fontSize={33} fill={C.white} fontWeight={700} opacity={()=>p()===6?0:1}/>);
  world.add(<Rect position={[-10,-40]} width={800} height={190} fill="#000000DE" opacity={()=>p()===5?1:0}/>);
  world.add(<Txt text={"촬영 · 배치 순간\n메시 수정 + 최적화"} position={[-10,-40]} fontFamily={FONT} fontSize={48} fontWeight={700} fill={C.yellow} opacity={()=>p()===5?1:0}/>);
 }else{
  world.add(<Txt text="같은 행성 · 같은 출발 속도" position={[-10,-400]} fontFamily={FONT} fontSize={42} fill={C.yellow} fontWeight={700}/>);
  world.add(<Txt text="빠르게 약해짐" position={[-250,-340]} fontFamily={FONT} fontSize={34} fill={C.red} fontWeight={700}/>);
  world.add(<Txt text="완만하게 약해짐" position={[225,-340]} fontFamily={FONT} fontSize={34} fill={C.green} fontWeight={700}/>);
  world.add(<Txt text="역제곱: 1 / r²" position={[-250,245]} fontFamily={FONT} fontSize={33} fill={C.red}/>);
  world.add(<Txt text="비교 예시: 1 / r" position={[225,245]} fontFamily={FONT} fontSize={33} fill={C.green}/>);
  world.add(<Txt text="우리 계산 예시 · 게임 내부 수치 아님" position={[-10,295]} fontFamily={FONT} fontSize={27} fill={C.muted}/>);
  world.add(<Line points={[[-250,-220],[-250,-290]]} stroke={C.red} lineWidth={7} endArrow arrowSize={24} opacity={()=>nativePhase()>.26?1:0}/>);
  world.add(<Txt text="계속 멀어짐" position={[-260,-175]} fontFamily={FONT} fontSize={30} fill={C.red} opacity={()=>nativePhase()>.26?1:0}/>);
  world.add(<Txt text="다시 지표면으로" position={[225,-60]} fontFamily={FONT} fontSize={30} fill={C.green} opacity={()=>nativePhase()>.58?1:0}/>);
 }
 const board=new Node({opacity:()=>section().kind==='diagram'?1:0});view.add(board);
 if(topic==='gravity'){
  const inverse=new Node({position:[0,-40],opacity:()=>p()===1?1:0});board.add(inverse);
  inverse.add(<Circle position={[-230,80]} size={220} fill="#27494F" stroke={C.teal} lineWidth={4}/>);
  inverse.add(<Circle position={[-230,80]} size={18} fill={C.white}/>);
  inverse.add(<Line points={[[-230,80],[250,80]]} stroke={C.muted} lineWidth={4}/>);
  inverse.add(<Circle position={()=>[-230+240*(1+clamp(frac()*2)),80]} size={35} fill={C.yellow}/>);
  inverse.add(<Txt text="행성의 중심" position={[-245,205]} fontFamily={FONT} fontSize={30} fill={C.white}/>);
  inverse.add(<Txt text="중심에서 거리 2배" position={[-10,-180]} fontFamily={FONT} fontSize={45} fill={C.yellow} fontWeight={700}/>);
  inverse.add(<Txt text="중력은 1/4" position={[-10,-105]} fontFamily={FONT} fontSize={55} fill={C.green} fontWeight={700} opacity={()=>clamp((frac()-.35)*6)}/>);
  inverse.add(<Txt text="Inverse-square Law · 역제곱 법칙" position={[-10,255]} fontFamily={FONT} fontSize={34} fill={C.teal}/>);
  inverse.add(<Txt text="r → 2r       1 / r² → 1 / (2r)²" position={[-10,305]} fontFamily={FONT} fontSize={34} fill={C.white}/>);
  const scale=new Node({position:[0,-30],opacity:()=>p()===2||p()===3?1:0});board.add(scale);
  scale.add(<Txt text={()=>p()===2?'지구: 점프 높이는 반지름에 비해 작다':'작은 행성: 같은 높이의 비중이 커진다'} position={[-15,-350]} fontFamily={FONT} fontSize={37} fill={C.yellow} fontWeight={700}/>);
  scale.add(<Circle position={[-235,10]} size={370} fill="#27494F" stroke={C.teal} lineWidth={4}/>);
  scale.add(<Circle position={[240,10]} size={130} fill="#27494F" stroke={C.teal} lineWidth={4}/>);
  scale.add(<Circle position={[-235,10]} size={12} fill={C.white}/>);scale.add(<Circle position={[240,10]} size={12} fill={C.white}/>);
  const hop=()=>Math.sin(clamp(frac())*Math.PI)*75;
  scale.add(<Circle position={()=>[-235,-175-hop()]} size={24} fill={C.yellow}/>);
  scale.add(<Circle position={()=>[240,-55-hop()]} size={24} fill={C.yellow}/>);
  scale.add(<Line points={()=>[[-235,10],[-235,-175-hop()]]} stroke={C.yellow} lineWidth={4}/>);
  scale.add(<Line points={()=>[[240,10],[240,-55-hop()]]} stroke={C.yellow} lineWidth={4}/>);
  scale.add(<Txt text="큰 행성" position={[-235,245]} fontFamily={FONT} fontSize={36} fill={C.white}/>);
  scale.add(<Txt text="작은 행성" position={[240,245]} fontFamily={FONT} fontSize={36} fill={C.white}/>);
  scale.add(<Txt text="같은 상승 높이 · 달라지는 상대적 거리" position={[0,300]} fontFamily={FONT} fontSize={33} fill={C.green}/>);
  scale.add(<Txt text="비율을 설명한 도식 · 실제 행성 축척 아님" position={[0,-285]} fontFamily={FONT} fontSize={26} fill={C.muted}/>);
 }
 const footage=new Rect({position:[-20,-40],size:[1000,562.5],clip:true,opacity:()=>game()?1:0});view.add(footage);
 footage.add(<Img src={()=>ROOT+(timing.gameFramesFolder??'game-frames')+'/'+(game()?section().id:'open')+'/'+String(game()?f()-section().startFrame:0).padStart(5,'0')+'.jpg'} width={1000} height={562.5}/>);
 footage.add(<Rect position={[0,-244]} size={[1000,75]} fill="#000000AD"/>);
 footage.add(<Txt text={topic==='viewfinder'?'뷰파인더':'아우터 와일즈'} position={[-330,-244]} fontFamily={FONT} fontSize={34} fill={C.white} fontWeight={700}/>);
 const sourceGuide=new Node({opacity:()=>{const elapsed=t()-section().start;return game()&&section().id==='open'&&(topic==='viewfinder'?elapsed>=3&&elapsed<4.1:elapsed>=.8&&elapsed<2)?1:0;}});footage.add(sourceGuide);
 sourceGuide.add(<Line points={topic==='viewfinder'?[[-360,120],[-180,120],[-65,72]]:[[-200,55],[-385,55]]} stroke={C.green} lineWidth={7} endArrow arrowSize={25}/>);
 sourceGuide.add(<Txt text={topic==='viewfinder'?'사진이 만든 길':'작은 행성의 표면'} position={topic==='viewfinder'?[-265,170]:[-170,110]} fontFamily={FONT} fontSize={31} fill={C.white} stroke="#000000" lineWidth={7} strokeFirst fontWeight={700}/>);
 const headings=topic==='viewfinder'?['종이 사진을 놓았더니','진짜 길이 생겼다?']:['작은 행성에 현실 중력을','그대로 넣으면?'];
 view.add(<Txt text="얌얌코딩" position={[-290,-835]} fontFamily={FONT} fontSize={37} fill={C.muted} fontWeight={700}/>);
 headings.forEach((h,i)=>view.add(<Txt text={h} position={[-20,-710+i*104]} fontFamily={FONT} fontSize={topic==='viewfinder'?67:61} fill={i?C.yellow:C.white} fontWeight={700}/>));
 view.add(<Txt text={topic==='viewfinder'?'Runtime Mesh Slicing · 메시 절단':'Gravity Falloff · 중력 감쇠'} position={[-155,-465]} fontFamily={FONT} fontSize={28} fill={C.teal}/>);
 view.add(<Txt text={()=>game()?'실제 게임':section().kind==='diagram'?'우리 도식':'Unity 구현'} position={[365,-465]} fontFamily={FONT} fontSize={28} fill={C.muted}/>);
 const cat=new Rect({width:560,height:460,position:[280,765],clip:true,opacity:catPresence});view.add(cat);
 cat.add(<Img src={realize} width={560} height={560} position={[20,50]}/>);
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});}
