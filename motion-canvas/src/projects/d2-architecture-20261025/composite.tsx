import {makeScene2D,Node,Rect,Txt,Img,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {diabloDiagramActor} from '../diablo-tricks-shorts-20261025/composite';
const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',line:'#3E5146'};
const font='Malgun Gothic', clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{x=clamp(x);return x*x*(3-2*x);};
// Two independent drawings make the different visual outputs visible while
// both consume the same position signal. This is not a recovered D2R model.
const detailedActor='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="0 0 300 400"><g stroke="#25322D" stroke-width="7" stroke-linejoin="round"><path d="M111 44Q150 15 189 44L201 107 181 142H119L99 107Z" fill="#B7C8C0"/><path d="M116 77Q150 61 184 77L178 113Q150 130 122 113Z" fill="#293D35"/><path d="M125 86L142 91M158 91L175 86" fill="none" stroke="#F1D591" stroke-width="6"/><path d="M143 32L152 15 161 32 158 111H146Z" fill="#E6EEE7"/><path d="M104 148Q150 126 196 148L190 235H110Z" fill="#8DB5A1"/><path d="M116 158L148 172 184 157 176 208H123Z" fill="#D9E2DC"/><path d="M145 172H158V224H145Z" fill="#E7BA61"/><path d="M78 147Q95 127 113 149L96 205H66Z" fill="#D4E0D7"/><path d="M187 149Q205 128 224 148L233 205H205Z" fill="#D4E0D7"/><path d="M68 201L96 207 91 252H61Z" fill="#8DB5A1"/><path d="M205 205L234 198 241 249H211Z" fill="#8DB5A1"/><path d="M110 231H190L182 280 160 287 150 255 139 287 116 280Z" fill="#4F675A"/><path d="M115 275L141 280 134 339H96L107 320Z" fill="#BACDC0"/><path d="M160 280L185 275 194 321 207 339H166Z" fill="#BACDC0"/><path d="M251 86L264 59 276 87 270 209H251Z" fill="#E0ECE4"/><path d="M238 205H283V216H238Z" fill="#E7BA61"/><path d="M254 216H268V267H254Z" fill="#916A3A"/><path d="M18 186Q49 167 79 186L75 246Q51 273 47 278 24 263 18 246Z" fill="#799A87"/><path d="M29 195L66 195 64 238 48 259 31 239Z" fill="#C8D6CB"/><path d="M47 195V254" fill="none" stroke="#E7BA61"/></g></svg>`);
// Diagrams of state and input semantics, not reconstructed Diablo engine data.
function actor(parent:Node,x:any,y:any,color:string,size=1,src=diabloDiagramActor){
 const n=new Node({position:()=>[typeof x==='function'?x():x,typeof y==='function'?y():y],scale:size});parent.add(n);
 n.add(<Img src={src} size={[110,147]} y={16}/>);
 n.add(<Line points={[[-38,83],[38,83]]} stroke={color} lineWidth={5}/>);
 return n;
}
export function architecture(slug:string,config:any,timing:any){return makeScene2D(function*(view){
 const time=createSignal(0),f=()=>Math.min(timing.frames-1,Math.floor(time()*60+.0001));
 const section=()=>timing.sections.find((s:any)=>f()>=s.startFrame&&f()<s.endFrame)??timing.sections.at(-1);
 const id=()=>section().id,e=()=>time()-section().start,is=(...v:string[])=>v.includes(id()),game=()=>section().kind==='game';
 const cue=(name:string)=>timing.cues?.find((c:any)=>c.id===name);
 const motion=(name:string,duration=1.5)=>{const c=cue(name);return c?smooth((time()-c.start)/Math.max(.3,Math.min(duration,c.end-c.start))):smooth((e()-.7)/duration);};
 const root='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/local/';
 view.fill('#000000');
 view.add(<Txt text="얌얌코딩" x={-344} y={-843} fontFamily={font} fontSize={34} fontWeight={700} fill={C.muted}/>);
 config.head.forEach((t:string,i:number)=>view.add(<Txt text={t} x={-20} y={-705+i*98} fontFamily={font} fontSize={i?70:64} fontWeight={700} fill={i?C.yellow:C.white}/>));
 view.add(<Txt text={()=>game()?'디아블로 II: 레저렉션':'원리 설명 · 자체 도식'} position={[-180,-500]} fontSize={28} fontFamily={font} fill={C.teal}/>);
 const box=new Rect({position:[-15,-30],width:1000,height:563,clip:true,opacity:()=>game()?1:0});view.add(box);
 const sourceCut=()=>section().cuts?.find((cut:any)=>time()>=cut.start&&time()<cut.end);
 box.add(<Img src={()=>root+(timing.frameRoot??'game-frames')+'/'+(game()?id():'game')+'/'+String(game()?Math.max(0,f()-section().startFrame):0).padStart(5,'0')+'.jpg'} width={1000} height={562.5}/>);
 box.add(<Rect position={[0,-247]} size={[1000,68]} fill="#000000BB"/>);
 box.add(<Txt text={()=>config.topic==='renderer'?(sourceCut()?.source?.endsWith('new')?'리마스터 화면':'클래식 화면'):'PC 마우스 조작 화면'} y={-247} fontFamily={font} fontSize={28} fill={C.white}/>);
 if(config.topic==='renderer')box.add(<Rect size={[992,555]} stroke={()=>sourceCut()?.source?.endsWith('new')?C.green:C.teal} lineWidth={7}/>);
 else{
  box.add(<Circle position={[0,-10]} size={[115,155]} stroke={C.green} lineWidth={7}/>);
  box.add(<Line points={[[-240,-135],[-90,-135],[-45,-70]]} stroke={C.green} lineWidth={7} endArrow arrowSize={17}/>);
  box.add(<Txt text="이동하는 캐릭터" position={[-270,-180]} fontFamily={font} fontSize={32} fontWeight={700} fill={C.white} stroke="#000000" lineWidth={8} strokeFirst/>);
 }
 const n=new Node({opacity:()=>game()?0:1,position:[-20,-120]});view.add(n);
 const text=(t:any,x:number,y:number,size=34,color:any=C.white)=>n.add(<Txt text={t} position={[x,y]} fontFamily={font} fontSize={size} fontWeight={700} fill={color}/>);
 if(config.topic==='renderer'){
  const state=()=>is('state')?2+Math.round(motion('p4-1',1.5)):is('close','confirm-explain')?3:2;
  text('게임 상태',0,-300,46,C.yellow);
  text(()=>`위치 x = ${state()}   ·   행동 = 이동`,0,-229,37,C.white);
  n.add(<Line points={[[0,-177],[0,-116],[-251,-116],[-251,-62]]} stroke={C.teal} lineWidth={7} endArrow arrowSize={21}/>);
  n.add(<Line points={[[0,-177],[0,-116],[251,-116],[251,-62]]} stroke={C.teal} lineWidth={7} endArrow arrowSize={21}/>);
  for(const [idx,x] of [-251,251].entries()){
   n.add(<Rect position={[x,137]} size={[450,390]} stroke={C.line} lineWidth={3}/>);
   text(idx?'새 그래픽':'옛 그래픽',x,-22,35,idx?C.green:C.white);
   for(let k=0;k<4;k++)n.add(<Line points={[[x-165+k*110,50],[x-165+k*110,280]]} stroke={C.line} lineWidth={2}/>);
   n.add(<Line points={[[x-195,245],[x+195,245]]} stroke={C.line} lineWidth={3}/>);
   actor(n,()=>x-110+(state()-1)*110,105,idx?C.green:C.teal,1,idx?detailedActor:diabloDiagramActor);
   text(()=>`같은 위치 ${state()}`,x,300,29,idx?C.green:C.teal);
  }
  text(()=>is('jobs')?'계산하는 일과 그리는 일을 나눈다':is('layer')?'기존 동작을 새 모델로 표현한다':is('state')?'위치 한 칸 변경 → 두 화면에 반영':'게임 로직과 렌더링의 분리',0,410,34,C.white);
 }else{
  const mapMode=()=>is('original','commands','confirm','close');
  const maps=new Node({opacity:()=>mapMode()?1:0});n.add(maps);
  const paths=[[[ -165,80],[-80,80],[-80,-90],[150,-90],[150,80]], [[-165,80],[-67,80]]];
  const progress=(side=0)=>is('original')?motion(side?'p2-3':'p2-2',2):is('commands')?(side?motion('p4-3',1.5):1):is('confirm')?motion(side?'p5-3':'p5-2',1.8):1;
  function along(points:number[][],t:number){let lengths=points.slice(1).map((p,i)=>Math.hypot(p[0]-points[i][0],p[1]-points[i][1]));let remaining=t*lengths.reduce((a,b)=>a+b,0);for(let i=0;i<lengths.length;i++){if(remaining<=lengths[i]){let a=points[i],b=points[i+1],u=remaining/lengths[i];return[a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u];}remaining-=lengths[i];}return points.at(-1)!;}
  for(let i=0;i<2;i++){
   const x=i?230:-230;
   maps.add(<Rect position={[x,60]} size={[440,430]} stroke={i?C.teal:C.green} lineWidth={4}/>);
   maps.add(<Txt text={i?'스틱: 방향 지정':'클릭: 목적지 지정'} position={[x,-225]} fontFamily={font} fontSize={31} fill={i?C.teal:C.green} fontWeight={700}/>);
   const map=new Node({position:[x,40]});maps.add(map);
   map.add(<Rect position={[0,80]} size={[90,170]} fill="#53615B"/>);
   map.add(<Txt text="벽" position={[0,80]} fontFamily={font} fontSize={30} fill={C.white}/>);
   map.add(<Circle position={[150,80]} size={44} stroke={C.yellow} lineWidth={6}/>);
   map.add(<Txt text="목표" position={[150,138]} fontFamily={font} fontSize={26} fill={C.yellow}/>);
   map.add(<Line points={paths[i] as any} stroke={i?C.teal:C.green} lineWidth={7} lineDash={i?[]:[12,10]} end={()=>progress(i)} endArrow arrowSize={18}/>);
   const actorPos=()=>along(paths[i],progress(i));actor(map,()=>actorPos()[0],()=>actorPos()[1]-20,i?C.teal:C.green,.47);
   maps.add(<Txt text={()=>i?(progress(i)>.95?'벽에 막힘 → 방향 변경 필요':'오른쪽 방향을 계속 입력'):'목표까지 돌아가는 길 계산'} position={[x,332]} fontFamily={font} fontSize={25} fill={()=>i&&progress(i)>.95?C.red:C.white}/>);
  }
  text(()=>is('original')?'목적지와 이동 방향은 다르다':is('commands')?'패드 이동: 자동 길 찾기를 끈다':'같은 목표 · 서로 다른 조작의 의미',0,-340,37,C.yellow);
  const adapter=new Node({opacity:()=>mapMode()?0:1});n.add(adapter);
  for(const [i,t] of ['스틱 · 버튼','입력 변환 계층','기존 게임 행동'].entries()){
   const y=-225+i*230;
   adapter.add(<Rect position={[0,y]} size={[700,135]} stroke={i===1?C.yellow:C.teal} lineWidth={5}/>);
   adapter.add(<Txt text={t} position={[0,y]} fontFamily={font} fontSize={43} fill={i===1?C.yellow:C.white} fontWeight={700}/>);
   if(i<2)adapter.add(<Line points={[[0,y+75],[0,y+147]]} stroke={C.green} lineWidth={9} endArrow arrowSize={25}/>);
  }
  text('Input Adaptation Layer · 입력 변환 계층',0,418,26,C.muted);
 }
 const reaction=()=>timing.reactions?.find((r:any)=>time()>=r.start&&time()<r.end);
 const presence=()=>{const r=reaction();return r?clamp((time()-r.start)/.2)*clamp((r.end-time())/.2):0;};
 // Reactions appear during the opening/short reveal, not over the comparison test bed.
 const cat=new Rect({size:[560,810],position:[290,180],clip:true,opacity:presence});view.add(cat);
 cat.add(<Img src={()=>reaction()?.kind==='relief'?relief:realize} size={740} position={[75,30]}/>);
 yield view.toPromise();yield* time(timing.durationSeconds,timing.durationSeconds,linear);
});}
