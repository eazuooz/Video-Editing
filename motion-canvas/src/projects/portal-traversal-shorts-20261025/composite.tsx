import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC'},FONT='Malgun Gothic';
export function composite(topic:string,slug:string,timing:any,native:any){return makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number)=>Math.max(0,Math.min(1,x)),frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001));
 const section=()=>timing.sections.find((s:any)=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections.at(-1),id=()=>section().id,e=()=>t()-section().start,game=()=>section().kind==='game',rec=()=>native.records[frame()];
 const ROOT='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/local/',first=timing.sections.find((s:any)=>s.kind!=='game').startFrame;
 const nativeImage=(alt=false)=>ROOT+'capture-'+timing.captureMode+'/'+(alt?'player':'frames')+'/'+String(game()?first:frame()).padStart(5,'0')+'.jpg';
 const cue=()=>timing.reactions.find((c:any)=>t()>=c.start&&t()<c.end),presence=()=>{const c=cue();return c?clamp((t()-c.start)/.15)*clamp((c.end-t())/.15):0;};
 const is=(...ids:string[])=>ids.includes(id());view.fill('#000');
 const labels:any=topic==='momentum'?{reset:'위치만 이동 · 속도는 0으로',vector:'속도 벡터 = 속력 + 방향',transform:'입구 기준 → 출구 기준',numbers:'같은 속력 · 달라지는 방향',close:'들어오던 움직임까지 연결'}:{camera:'두 문은 서로 떨어져 있다',screen:'출구 쪽 화면을 입구에 그린다',position:'기준점이 경계를 통과하는 순간',half:'몸이 반쯤 걸쳐 있다면?',clip:'각 문 앞쪽의 몸만 남긴다',compare:'하나의 몸 · 두 곳에 나눠 그리기',close:'카메라 + 좌표 변환 + 클리핑'};
 const teaching=new Node({opacity:()=>game()?0:1});view.add(teaching);
 teaching.add(<Txt text={()=>labels[id()]??''} position={[-15,-365]} fontFamily={FONT} fill={C.yellow} fontSize={39} fontWeight={700} zIndex={3}/>);
 if(topic==='momentum'){
  const world=new Node({position:()=>[-20-110*presence(),-45],scale:()=>1-.14*presence()});teaching.add(world);world.add(<Img src={()=>nativeImage()} size={1000}/>);
  teaching.add(<Txt text={()=>is('numbers')?'아래로 6m/s  →  옆으로 6m/s':is('reset')?'속도까지 옮겨야 한다':is('vector')?'길이 = 속력     화살표 = 방향':is('transform')?'Coordinate Transformation · 좌표 변환':'위치와 속도를 함께 옮긴다'} position={[-20,295]} fill={is('reset')?C.red:C.white} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  if(topic==='momentum')teaching.add(<Line points={[[-285,-150],[-285,-70],[-285,20]]} stroke={C.teal} lineWidth={8} endArrow arrowSize={24} opacity={()=>is('vector')?clamp(e()/.6):0}/>);
 }else{
  const large=()=>is('half','clip','compare'),world=new Node({position:()=>[-15-45*presence(),-20],scale:()=>1-.15*presence()});teaching.add(world);
  world.add(<Img src={()=>nativeImage()} size={()=>large()?960:535} position={()=>large()?[0,-20]:[250,0]}/>);
  world.add(<Img src={()=>nativeImage(true)} size={()=>large()?250:535} position={()=>large()?[-290,160]:[-260,0]}/>);
  world.add(<Rect size={()=>large()?250:530} position={()=>large()?[-290,160]:[-260,0]} stroke={C.teal} lineWidth={4}/>);
  world.add(<Txt text="플레이어 화면" position={()=>large()?[-290,15]:[-260,-290]} fill={C.teal} fontFamily={FONT} fontSize={()=>large()?30:36} fontWeight={700}/>);
  world.add(<Txt text="위에서 본 이동" position={[250,-290]} opacity={()=>large()?0:1} fill={C.yellow} fontFamily={FONT} fontSize={36} fontWeight={700}/>);
  teaching.add(<Txt text={()=>is('position')?(rec().crossed?'경계 통과 → 위치·시선 연결':'아직 입구 앞'):is('clip')?'Clipping · 경계 밖을 잘라 그리기':is('half','compare')?'게임 상태는 하나 · 화면용 복사만 추가':is('camera')?'입구와의 거리·각도를 출구에 대응':'같은 시간 · 같은 움직임'} position={[-15,280]} fill={C.white} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
 }
 const gameBox=new Rect({position:[-20,-65],width:1000,height:563,clip:true,opacity:()=>game()?1:0});view.add(gameBox);
 gameBox.add(<Img src={()=>ROOT+'game-frames/'+(game()?id():'game')+'/'+String(game()?frame()-section().startFrame:0).padStart(5,'0')+'.jpg'} width={1000} height={562.5}/>);
 gameBox.add(<Rect position={[0,-248]} width={1000} height={67} fill="#000000A8"/>);gameBox.add(<Txt text="포털" position={[-390,-247]} fill={C.white} fontFamily={FONT} fontSize={35} fontWeight={700}/>);
 // These are editorial focus cues, anchored only during the directly inspected interval.
 const guideTime=()=>topic==='momentum'?e()>.8&&e()<1.4:e()>.8&&e()<1.3;
 gameBox.add(<Circle position={[0,-5]} size={145} stroke={C.green} lineWidth={6} opacity={()=>topic==='momentum'&&game()&&id()==='game'&&guideTime()?1:0}/>);
 gameBox.add(<Line points={[[-240,-100],[75,-115]]} stroke={C.green} lineWidth={7} endArrow arrowSize={22} opacity={()=>topic==='traversal'&&game()&&id()==='game'&&guideTime()?1:0}/>);
 const head=topic==='momentum'?['포털로 떨어진 속도','어디로 갈까?']:['포털에 반쯤 들어가면','몸은 어디에 있을까?'];
 const header=(kind:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="540"><rect width="1080" height="540" fill="black"/><g font-family="Malgun Gothic" font-weight="700"><text x="128" y="128" font-size="37" fill="${C.muted}">얌얌코딩</text><text x="510" y="258" text-anchor="middle" font-size="69" fill="white">${head[0]}</text><text x="510" y="361" text-anchor="middle" font-size="72" fill="${C.yellow}">${head[1]}</text><text x="90" y="490" font-size="28" fill="${C.teal}">${topic==='momentum'?'Velocity Vector · 속도 벡터':'Portal Traversal · 포털 통과'}</text><text x="855" y="490" text-anchor="middle" font-size="28" fill="${C.muted}">${kind}</text></g></svg>`);
 const heads=[header('실제 게임'),header('Unity 구현')];view.add(<Img src={()=>heads[game()?0:1]} width={1080} height={540} position={[0,-690]} zIndex={5}/>);
 const cat=new Rect({width:560,height:860,position:[280,80],clip:true,opacity:presence});view.add(cat);cat.add(<Img src={()=>cue()?.kind==='realize'?realize:relief} width={780} height={780} position={()=>[80+40*(1-presence()),30]}/>);
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});}
