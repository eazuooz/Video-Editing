import {makeScene2D, Img, Node, Txt, Rect, Line, Circle} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';

// Authored explanatory drawings. These are not recovered game assets or telemetry.
const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',panel:'#101611',line:'#334238'};
const FONT='Malgun Gothic';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const smooth=(n:number)=>{const x=clamp(n);return x*x*(3-2*x);};
const svg=(body:string,w=300,h=400)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`);
const xml=(text:string)=>text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

// A tiny original pixel knight, built from separate layers at a shared origin.
// The styles are independent educational artwork, not replicas of Diablo graphics.
const parts:any={
 head:'<path fill="#24302B" d="M108 23h84v18h18v93h-18v18h-84v-18H90V41h18z"/><path fill="#B9C3BF" d="M111 38h66v15h18v58h-18V98h-66v13H99V53h12z"/><path fill="#E9E4D4" d="M117 100h57v38h-57z"/><path fill="#24302B" d="M124 106h14v9h-14zm29 0h14v9h-14z"/>',
 torso:'<path fill="#27322D" d="M92 145h116v102H92z"/><path fill="COLOR" d="M103 151h94v83h-94z"/><path fill="#FFFFFF55" d="M111 160h31v56h-31z"/><path fill="#504431" d="M98 230h104v17H98z"/><path fill="#FFD25A" d="M141 230h20v17h-20z"/>',
 leftArm:'<path fill="#26322C" d="M59 151h39v91H59z"/><path fill="#9DA9A2" d="M65 157h27v53H65z"/><path fill="#E9D3B1" d="M65 210h27v32H65z"/>',
 rightArm:'<path fill="#26322C" d="M202 151h39v91h-39z"/><path fill="#9DA9A2" d="M208 157h27v53h-27z"/><path fill="#E9D3B1" d="M208 210h27v32h-27z"/>',
 legs:'<path fill="#25312C" d="M104 247h36v93h-48v-21h12zm56 0h36v72h12v21h-48z"/><path fill="#86988F" d="M111 251h22v57h-22zm56 0h22v57h-22z"/>',
 weapon:'<path fill="#26332D" d="M252 90h15v135h-15z"/><path fill="#D8E6E0" d="M252 90l9-19 9 19v112h-18z"/><path fill="#FFD25A" d="M237 199h48v12h-48z"/><path fill="#7C6041" d="M255 211h12v47h-12z"/>',
 shield:'<path fill="#25312C" d="M21 179h55v80l-28 27-27-27z"/><path fill="#8DA79B" d="M28 187h41v68l-21 20-20-20z"/><path fill="#FFD25A" d="M44 194h9v64h-9z"/>'
};
const body=(kind:string)=>svg(kind==='monster'?'<path d="M70 100L44 30 105 62 150 45 195 62 256 30 230 100 235 165 211 198 224 325 196 350 167 280 133 280 104 350 76 325 89 198 65 165z" fill="#6A4544" stroke="#E3AAA2" stroke-width="8"/><path d="M97 118l35 8m36 0 35-8" stroke="#FFD25A" stroke-width="14"/><path d="M117 177l33 15 33-15" fill="none" stroke="#281D1C" stroke-width="10"/>':Object.values(parts).join('').replace('COLOR',C.teal));
// Original educational artwork for sibling explanation scenes, not a game asset.
export const diabloDiagramActor=body('player');

export function diabloComposite(slug:string,config:any,timing:any){return makeScene2D(function*(view){
 const time=createSignal(0);
 const frame=()=>Math.min(timing.frames-1,Math.floor(time()*60+0.0001));
 const section=()=>timing.sections.find((s:any)=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections[timing.sections.length-1];
 const id=()=>section().id,elapsed=()=>time()-section().start;
 const is=(...ids:string[])=>ids.includes(id());
 const game=()=>section().kind==='game';
 const progress=()=>smooth(elapsed()/1.15);
 const cue=(key:string,fallback=0)=>timing.cues?.[key]?.start??section().start+fallback;
 const reaction=()=>timing.reactions?.find((r:any)=>time()>=r.start&&time()<r.end);
 const presence=()=>{const r=reaction();return r?clamp((time()-r.start)/.15)*clamp((r.end-time())/.2):0;};
 const topic=config.topic;
 view.fill('#000000');

 const header=new Node({zIndex:10});view.add(header);
 // One preloaded static header avoids browser text-layout invalidation at seeks.
 const headerSvg=svg(`<g font-family="Malgun Gothic" font-weight="700" dominant-baseline="middle"><text x="134" y="120" font-size="34" fill="${C.muted}">얌얌코딩</text><text x="520" y="260" text-anchor="middle" font-size="65" fill="${C.white}">${xml(config.head[0])}</text><text x="520" y="360" text-anchor="middle" font-size="69" fill="${C.yellow}">${xml(config.head[1])}</text><text x="525" y="490" text-anchor="middle" font-size="26" fill="${C.teal}">${xml(config.term[0]+' · '+config.term[1])}</text></g>`,1080,550);
 header.add(<Img src={headerSvg} size={[1080,550]} position={[0,-685]}/>);
 header.add(<Txt text={()=>game()?'실제 게임':'원리 설명'} position={[390,-416]} fontFamily={FONT} fontSize={26} fill={C.muted}/>);

 const gameBox=new Rect({position:[-15,-50],width:1000,height:563,clip:true,opacity:()=>game()?1:0});view.add(gameBox);
 if(config.footageReady){
   // PCM-bound immutable roots are repository-relative; old previews retain fallback.
   const frameRoot=timing.frameRoot??('projects/'+slug+'/'+config.footageFrameDirectory);
   const root='/@fs/D:/Github/VideoEditing/'+frameRoot.replace(/\\/g,'/').replace(/\/$/,'')+'/';
   gameBox.add(<Img src={()=>root+String(game()?frame():0).padStart(5,'0')+'.jpg'} width={1000} height={562.5}/>);
 }else{
   gameBox.add(<Rect size={[1000,563]} fill={C.panel}/>);
   gameBox.add(<Txt text="실제 게임 장면 · 소스 검수 대기" fontFamily={FONT} fontSize={36} fill={C.muted}/>);
 }
 gameBox.add(<Rect position={[0,-248]} size={[1000,67]} fill="#000000B8"/>);
 gameBox.add(<Txt text={config.gameName} position={[-245,-248]} fontFamily={FONT} fontSize={30} fontWeight={700} fill={C.white}/>);

 // The cat owns the right side only during a reaction. Move the complete mechanism
 // left so no player, enemy, item or equipment part disappears behind the character.
 const teaching=new Node({opacity:()=>game()?0:1,position:()=>[-15-215*presence(),-30-30*presence()],scale:()=>1-.35*presence()});view.add(teaching);
 const labels=new Node({opacity:()=>game()?0:1,position:[-15,-30]});view.add(labels);
 const sub=(text:any,y=300,color:any=C.white,size=34)=>labels.add(<Txt text={text} position={[0,y]} opacity={()=>y>0?1-presence():1} fontFamily={FONT} fontSize={size} fill={color} fontWeight={700}/>);

 if(topic==='ultrawide'){
   const wide=()=>is('view')?smooth((elapsed()-.7)/1.7):is('limit')?1-progress()*.45:is('answer')?.55:1;
   const viewWidth=()=>610+330*wide();
   const outer=new Rect({width:940,height:460,fill:C.panel,stroke:C.line,lineWidth:3,radius:10,clip:true});teaching.add(outer);
   for(let i=-5;i<=5;i++)outer.add(<Line points={[[i*85,-230],[i*85,230]]} stroke="#24332A" lineWidth={2}/>);
   for(let i=-2;i<=2;i++)outer.add(<Line points={[[-470,i*85],[470,i*85]]} stroke="#24332A" lineWidth={2}/>);
   outer.add(<Circle position={[-230,0]} size={690} stroke={C.green} lineWidth={5} lineDash={[15,14]} opacity={()=>is('range')?(time()>=cue('p3-2',.8)?1:0):is('attack','limit','answer')?1:0}/>);
   outer.add(<Img src={body('player')} position={[-235,-25]} width={100} height={134}/>);
   outer.add(<Img src={body('monster')} position={[365,-25]} width={120} height={160}/>);
   const shots=()=>is('attack')?((elapsed()*.9)%1):0;
   outer.add(<Line points={()=>[[-180,-20],[is('attack')?-180+545*shots():-180,-20]]} stroke={C.yellow} lineWidth={7} endArrow arrowSize={18} opacity={()=>is('attack')?1:0}/>);
   outer.add(<Rect position={[365,-130]} size={[112,15]} fill="#2A2120"/>);
   outer.add(<Rect position={()=>[365-(1-(is('attack')?Math.max(.15,1-elapsed()*.11):1))*56,-130]} width={()=>112*(is('attack')?Math.max(.15,1-elapsed()*.11):1)} height={15} fill={C.red}/>);
   outer.add(<Txt text="공격 받음" position={[330,130]} opacity={()=>is('attack')?1:0} fontSize={31} fontFamily={FONT} fill={C.yellow}/>);
   // Opaque view masks hide regions outside the chosen viewport; no object moves.
   outer.add(<Rect position={()=>[-470+(940-viewWidth())/4,0]} width={()=>(940-viewWidth())/2} height={460} fill="#000000F2"/>);
   outer.add(<Rect position={()=>[470-(940-viewWidth())/4,0]} width={()=>(940-viewWidth())/2} height={460} fill="#000000F2"/>);
   outer.add(<Rect width={viewWidth} height={457} stroke={C.teal} lineWidth={6}/>);
   sub(()=>is('limit','answer')?'출시 당시: 19:9 범위로 제한':'화면 폭만 변경 · 캐릭터 위치는 그대로',-285,C.teal,34);
   sub(()=>is('range')?'초록 경계: AI 반응 범위의 설명도':is('attack')?'보이고 공격도 되는데, 반응은 시작되지 않음':is('limit')?'보이는 범위와 전투 규칙을 함께 맞춘다':'2021년 기술 알파에서 발견된 문제',290,is('attack')?C.red:C.white,32);
 }else if(topic==='grass'){
   const clear=()=>is('clear')?smooth((time()-cue('p3-2',.8))/1.15):is('distance','answer')?1:is('compare')?(Math.floor(elapsed()/2)%2):0;
   const patch=new Rect({size:[950,500],fill:'#182219',stroke:C.line,lineWidth:3,radius:10,clip:true});teaching.add(patch);
   patch.add(<Circle position={[0,110]} size={[185,42]} fill="#050A06"/>);
   // Gem stays fixed; plant tips bend outwards. Depth ordering preserves occlusion.
   const gem=new Node({position:[0,30]});patch.add(gem);
   gem.add(<Line points={[[0,-92],[57,-36],[38,66],[-38,66],[-57,-36]]} closed fill="#72DCC7" stroke="#D5FFF0" lineWidth={6}/>);
   gem.add(<Line points={[[-57,-36],[0,-10],[57,-36]]} stroke="#255D4B" lineWidth={5}/>);
   gem.add(<Line points={[[0,-92],[0,-10],[38,66]]} stroke="#D5FFF0" lineWidth={4}/>);
   gem.add(<Line points={[[0,-10],[-38,66]]} stroke="#D5FFF0" lineWidth={4}/>);
   for(let row=0;row<5;row++)for(let col=0;col<17;col++){
     const x=-440+col*55+(row%2)*12,y=-120+row*88;
     const influence=Math.max(0,1-Math.hypot(x,y-70)/260);
     const side=x>=0?1:-1;
     const color=['#426A3C','#588145','#35582D'][Math.abs(col+row*2)%3];
     patch.add(<Line points={()=>[[x-9,y+70],[x-7+side*clear()*influence*210,y-38],[x+12,y+70]]} closed fill={color} stroke="#85A86A" lineWidth={2}/>);
   }
   // Foreground tufts make the readability problem visible at mobile size.
   // Their roots stay fixed below the item; their tips bend away from its centre.
   for(let k=-3;k<=3;k++){
     const x=k*25,side=k<0?-1:1;
     patch.add(<Line points={()=>[[x-17,145],[x*.35+side*clear()*220,-75],[x+17,145]]} closed fill={k%2?'#537C40':'#426A3C'} stroke="#85A86A" lineWidth={2}/>);
   }
   patch.add(<Circle position={[0,30]} size={270} stroke={C.green} lineWidth={5} lineDash={[12,12]} opacity={()=>is('distance')?1:0}/>);
   patch.add(<Line points={()=>[[65,30],[65+clear()*180,30]]} stroke={C.yellow} endArrow lineWidth={7} arrowSize={20} opacity={()=>is('distance')?1:0}/>);
   sub(()=>clear()>.5?'같은 아이템 · 주변 풀이 비켜난 상태':'같은 아이템 · 풀에 가려진 상태',-300,()=>clear()>.5?C.green:C.red,36);
   sub(()=>is('distance')?'아이템은 고정 · 가까운 풀의 모양만 변경':is('compare')?'식생 변위 · Vegetation Displacement':'전리품의 윤곽이 읽혀야 한다',320,C.white,34);
 }else{
   const exploded=()=>is('parts')?progress():is('swap')?1:is('sync')?1-progress():0;
   const swapped=()=>is('swap')?time()>cue('p3-2',1.1)+.4:is('sync','combine','answer');
   const walking=()=>is('sync','combine','answer');
   const phase=()=>Math.floor(time()*5)%4;
   const spriteRoot=new Node({scale:1,position:[0,-30]});teaching.add(spriteRoot);
   const offsets:any={head:[0,-85],torso:[0,0],leftArm:[-105,-5],rightArm:[105,-5],legs:[0,100],weapon:[130,30],shield:[-130,30]};
   const names:any={head:'머리',torso:'몸통',leftArm:'왼팔',rightArm:'오른팔',legs:'다리',weapon:'무기',shield:'방패'};
   for(const key of ['legs','leftArm','rightArm','torso','head','weapon','shield']){
     const img=new Img({src:()=>svg(parts[key].replace('COLOR',swapped()?C.yellow:C.teal)),size:[300,400],position:()=>{const o=offsets[key];const stride=walking()?[-6,0,6,0][phase()]:0;return [o[0]*exploded()+(key==='weapon'||key==='rightArm'?stride:key==='leftArm'||key==='shield'?-stride:0),o[1]*exploded()+(walking()&&['head','torso'].includes(key)?Math.abs(stride)*.4:0)];}});spriteRoot.add(img);
     const anchor:any={head:[0,-108],torso:[0,76],leftArm:[-175,64],rightArm:[175,64],legs:[0,265],weapon:[240,145],shield:[-240,145]};
     spriteRoot.add(<Rect position={anchor[key]} size={[110,40]} fill="#000000E8" radius={4} opacity={()=>exploded()>.8?1:0}/>);
     spriteRoot.add(<Txt text={names[key]} position={anchor[key]} opacity={()=>exploded()>.8?1:0} fontFamily={FONT} fontSize={30} fontWeight={700} fill={key==='torso'?C.yellow:C.white}/>);
   }
   sub(()=>is('swap')?'갑옷만 바꿔도 새로운 외형':is('sync')?'같은 자세 · 같은 시점 · 맞는 겹침 순서':is('combine')?'부품을 재사용해서 조합을 늘린다':'한 캐릭터를 부위별 그림으로',-355,C.teal,35);
   sub(()=>walking()?'동작 단계 '+String(phase()+1)+' / 4 · 자체 설명 캐릭터':'머리 + 몸통 + 양팔 + 다리 + 장비',320,C.white,30);
 }

 const cat=new Rect({width:500,height:820,position:[340,100],clip:true,opacity:presence});view.add(cat);
 cat.add(<Img src={()=>reaction()?.kind==='relief'?relief:realize} size={760} position={[75,25]}/>);
 // Captions are composited from the actual PCM-derived clause cues in the final pass.
 yield view.toPromise();
 // Resolve browser text layout before exporting the first requested frame.
 header.children().forEach(node=>{if(node instanceof Txt)node.size();});
 yield new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())));
 yield* time(timing.durationSeconds,timing.durationSeconds,linear);
});}
