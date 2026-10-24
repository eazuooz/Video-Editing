import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'},FONT='Malgun Gothic';
const topics:any={
 titanfall:{head:['시간여행 버튼의 비밀','사실은 위아래 이동?'],term:'두 시대의 맵 + 순간이동',game:'타이탄폴 2',labels:{reveal:'시간을 바꾼다? 위치를 바꾼다!',stack:'과거와 현재를 위아래로 맞춘다',transfer:'같은 앞뒤 위치, 다른 높이',numbers:'우리 시연: 두 층의 간격 10m',view:'위치가 바뀌어도 시선은 유지',close:'공간 이동이 시간여행이 된다'}},
 superliminal:{head:['멀리 내려놓았더니','진짜 커졌다?'],term:'Forced Perspective · 강제 원근',game:'슈퍼리미널',labels:{reveal:'멀리 옮기는 만큼 크기를 키운다',numbers:'거리 3배 → 실제 크기 3배',view:'보이는 크기와 실제 크기는 다르다',rays:'보이는 표면에 여러 광선을 쏜다',close:'보이는 크기를 퍼즐 규칙으로'}},
 ghost:{head:['불에 안 타는 낙엽','바람으로 고쳤다?'],term:'Updraft · 상승기류',game:'고스트 오브 쓰시마',labels:{problem:'개발 중 문제: 불 속에 떨어지는 낙엽',reveal:'불 위에 상승기류를 만든다',off:'상승기류 OFF',on:'상승기류 ON',compare:'같은 낙엽 · 바꾼 것은 바람뿐',close:'문제가 생기는 조건을 바꾼다'}},
 gears:{head:['동작을 뚝 바꿨는데','왜 자연스러울까?'],term:'Inertialization · 관성화',game:'기어스 오브 워 4',labels:{snap:'갑자기 바꾸면 자세가 튄다',difference:'이전 자세 − 새 자세 = 차이',decay:'남겨 둔 차이를 0으로 줄인다',velocity:'움직이던 속도도 이어 받는다',compare:'이전 동작 대신, 남은 차이를 계산',close:'관성화: 차이를 부드럽게 없앤다'}},
 portal:{head:['포털 안에 또 포털','무한히 그릴까?'],term:'Stencil Buffer · Recursive Rendering',game:'포털',labels:{reveal:'반대편 출구에서 본 장면',mask:'스텐실 버퍼: 그릴 영역을 표시',recursive:'안쪽 포털도 다시 그린다',depth:'같은 장면, 반복 횟수만 바꾸기',limit:'반복에는 한도를 둔다',close:'끝없는 공간도 유한한 계산으로'}},
};
export function composite(topic:string,slug:string,timing:any,native:any){return makeScene2D(function*(view){
 const d=topics[topic],t=createSignal(0),clamp=(x:number)=>Math.max(0,Math.min(1,x));
 const frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001)),rec=()=>native.records[frame()];
 const section=()=>timing.sections.find((s:any)=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections.at(-1),id=()=>section().id,e=()=>t()-section().start,is=(...xs:string[])=>xs.includes(id()),game=()=>section().kind==='game';
 const first=timing.sections.find((s:any)=>s.kind!=='game').startFrame;
 const ROOT='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/local/';
 const nativeImage=(alt=false)=>ROOT+'capture-'+(timing.captureMode??'full-v1')+'/'+(alt?'player':'frames')+'/'+String(game()?first:frame()).padStart(5,'0')+'.jpg';
 const cue=()=>timing.reactions.find((c:any)=>t()>=c.start&&t()<c.end),presence=()=>{const c=cue();return c?clamp((t()-c.start)/.15)*clamp((c.end-t())/.15):0;};
 const point=(p:any)=>new Vector2((p.x-540)*1000/1080,(p.y-540)*1000/1080);
 view.fill('#000');
 const split=()=>topic==='superliminal'&&is('numbers','view','close')||topic==='ghost'&&is('compare');
 const world=new Node({position:()=>[-20-135*presence(),-60],scale:()=>1-.17*presence(),opacity:()=>game()||split()?0:1});view.add(world);
 world.add(<Img src={()=>nativeImage()} size={1000}/>);
 world.add(<Txt text={()=>d.labels[id()]??''} position={[0,-340]} fill={C.yellow} fontFamily={FONT} fontWeight={700} fontSize={40}/>);
 const subtitle=(text:()=>string,y=350,color=C.white,size=38)=>world.add(<Txt text={text} position={[0,y]} fill={color} fontFamily={FONT} fontWeight={600} fontSize={size}/>);
 if(topic==='titanfall'){
  subtitle(()=>is('view')?'카메라 방향을 유지한 전환':is('numbers')?'높이 0m + 10m = 10m':is('transfer')?'버튼 → 높이 차이만큼 순간이동':'같은 좌표에 대응하는 두 공간');
  world.add(<Txt text="과거" position={[-320,-200]} fill={C.teal} fontFamily={FONT} fontSize={40} opacity={()=>is('view')?0:1}/>);
  world.add(<Txt text="현재" position={[-320,130]} fill={C.red} fontFamily={FONT} fontSize={40} opacity={()=>is('view')?0:1}/>);
  world.add(<Circle position={()=>point(rec().focus)} size={90} stroke={C.yellow} lineWidth={5} opacity={()=>is('view')?0:1}/>);
  world.add(<Txt text={()=>is('numbers')?'현재 높이 '+rec().height.toFixed(0)+'m':''} position={[240,230]} fill={C.yellow} fontFamily={FONT} fontSize={38}/>);
 }
 if(topic==='superliminal'){
  subtitle(()=>is('rays')?'광선 = 놓을 수 있는 위치를 찾는 기준':'거리와 크기가 함께 바뀐다',355,C.white,36);
  const comparison=new Node({opacity:()=>split()?1:0});view.add(comparison);
  for(let i=0;i<2;i++){
   let x=i===0?-265:245;
   comparison.add(<Img src={()=>nativeImage(i===0)} size={520} position={[x,-60]}/>);
   comparison.add(<Rect position={[x,-60]} size={510} stroke={i===0?C.white:C.teal} lineWidth={4}/>);
   comparison.add(<Txt text={i===0?'플레이어 시점':'옆에서 본 실제 크기'} position={[x,-370]} fill={i===0?C.white:C.teal} fontFamily={FONT} fontSize={35} fontWeight={700}/>);
  }
  comparison.add(<Txt text={()=>'거리 '+rec().distance.toFixed(1)+'m  /  크기 '+rec().scale.toFixed(1)+'배'} position={[-10,260]} fill={C.yellow} fontFamily={FONT} fontSize={43} fontWeight={700}/>);
 }
 if(topic==='ghost'){
  subtitle(()=>is('off','problem')?'낙엽이 불 쪽으로 내려온다':is('reveal')?'Wind Emitter · 바람을 만드는 장치':is('on')?'위로 밀어, 불 속 진입을 줄인다':'상승기류는 위로 흐르는 바람',355,C.white,35);
  const comparison=new Node({opacity:()=>split()?1:0});view.add(comparison);
  for(let i=0;i<2;i++){
   let x=i===0?-265:245;
   comparison.add(<Img src={()=>nativeImage(i===0&&is('compare'))} size={520} position={[x,-60]}/>);
   comparison.add(<Rect position={[x,-60]} size={510} stroke={i===0?C.red:C.teal} lineWidth={4}/>);
   comparison.add(<Txt text={i===0?'상승기류 OFF':'상승기류 ON'} position={[x,-370]} fill={i===0?C.red:C.teal} fontFamily={FONT} fontSize={38} fontWeight={700}/>);
  }
  comparison.add(<Txt text="같은 낙엽 · 같은 시작 위치" position={[-10,275]} fill={C.yellow} fontFamily={FONT} fontSize={40}/>);
 }
 if(topic==='gears'){
  world.add(<Txt text="바로 전환" position={[-250,-265]} fill={C.red} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  world.add(<Txt text="관성화" position={[245,-265]} fill={C.teal} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  subtitle(()=>is('difference')?'전환 순간: 50° − 20° = 30°':is('decay','velocity')?(e()<1.2?'이전 동작이 움직이는 중':'새 자세 20° + 남은 차이 '+rec().offset.toFixed(1)+'°'):is('compare')?'새 동작 + 저장해 둔 차이':'같은 시작 자세 · 같은 목표 자세');
  world.add(<Line points={()=>[point(rec().focus),point(rec().handB)]} stroke={C.yellow} lineWidth={7} endArrow arrowSize={16} opacity={()=>is('difference','decay','velocity')?1:0}/>);
 }
 if(topic==='portal'){
  subtitle(()=>is('mask')?'표시한 영역 안에 반대편 장면을 그린다':is('depth','close')?'반복 깊이 '+rec().depth+'단계 · 우리 시연의 시점 '+rec().views+'개':is('limit')?'더 깊게 그릴수록 처리할 화면도 늘어난다':'장면 안에 포털이 보이면 한 번 더 그린다',355,C.white,36);
 }
 const gameBox=new Rect({position:[-20,-65],width:1000,height:563,clip:true,opacity:()=>game()?1:0});view.add(gameBox);
 const firstGame=timing.sections.find((s:any)=>s.kind==='game');
 gameBox.add(<Img src={()=>ROOT+(timing.gameFramesDirectory??'game-frames')+'/'+(game()?id():firstGame.id)+'/'+String(game()?frame()-section().startFrame:0).padStart(5,'0')+'.jpg'} width={1000} height={562.5}/>);
 gameBox.add(<Rect position={[0,-248]} width={1000} height={67} fill="#000000A8"/>);
 gameBox.add(<Txt text={d.game} position={[-310,-247]} fill={C.white} fontFamily={FONT} fontSize={35} fontWeight={700}/>);
 // Editorial look-here guides are restricted to inspected, stationary on-screen targets.
 if(topic==='superliminal')gameBox.add(<Circle position={[0,40]} size={160} stroke={C.green} lineWidth={6} opacity={()=>id()==='game'&&e()<1.4?clamp(e()/.15):0}/>);
 if(topic==='portal'){
  // Editorial arrow follows the exposed inner opening at source frames 0,30,60.
  const guide=()=>{const u=clamp(e());return new Vector2(u<.5?100-10*u:95+70*(u-.5),u<.5?-10-110*u:-65-10*(u-.5));};
  gameBox.add(<Line points={()=>[new Vector2(-230,90),guide()]} stroke={C.green} lineWidth={7} endArrow arrowSize={22} opacity={()=>e()<1.05?clamp(e()/.15):0}/>);
  gameBox.add(<Txt text="안쪽 포털" position={[-255,135]} fill={C.white} fontFamily={FONT} fontSize={34} fontWeight={700} opacity={()=>e()<1.05?clamp(e()/.15):0}/>);
 }
 const head=(kind:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="540"><rect width="1080" height="540" fill="black"/><g font-family="Malgun Gothic" font-weight="700"><text x="128" y="128" font-size="37" fill="${C.muted}">얌얌코딩</text><text x="510" y="258" text-anchor="middle" font-size="72" fill="white">${d.head[0]}</text><text x="510" y="361" text-anchor="middle" font-size="74" fill="${C.yellow}">${d.head[1]}</text><text x="90" y="490" font-size="28" fill="${C.teal}">${d.term}</text><text x="855" y="490" text-anchor="middle" font-size="28" font-weight="400" fill="${C.muted}">${kind}</text></g></svg>`);
 const headers=[head('실제 게임'),head('Unity 재현'),head('구조 설명')];
 view.add(<Img src={()=>headers[game()?0:topic==='superliminal'&&is('rays')?2:1]} width={1080} height={540} position={[0,-690]} zIndex={5}/>);
 const cat=new Rect({width:560,height:860,position:[280,80],clip:true,opacity:presence});view.add(cat);
 const bust=new Node({position:()=>[80+40*(1-presence()),30-7*Math.sin(Math.PI*clamp((t()-(cue()?.start??t()))/.5))],scale:()=>1+.035*Math.sin(Math.PI*clamp((t()-(cue()?.start??t()))/.5))});cat.add(bust);
 bust.add(<Img src={()=>cue()?.kind==='realize'?realize:relief} width={780} height={780}/>);
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});}
