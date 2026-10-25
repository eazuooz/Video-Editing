import {makeScene2D, Node, Rect, Txt, Img, Line, Circle} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-d2r-renderer-logic-separation/production/layered-comparison-v2.json';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {diabloDiagramActor} from '../diablo-tricks-shorts-20261025/composite';

const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',line:'#3E5146'};
const font='Malgun Gothic';
const clamp=(n:number)=>Math.min(1,Math.max(0,n));
const smooth=(n:number)=>{n=clamp(n);return n*n*(3-2*n);};
// Our drawing, not a recovered game model. Two presentation layers consume
// one position signal. Their spatial separation is an explanatory diagram.
const modern='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="0 0 300 400"><g stroke="#25322D" stroke-width="7" stroke-linejoin="round"><path d="M111 44Q150 15 189 44L201 107 181 142H119L99 107Z" fill="#B7C8C0"/><path d="M116 77Q150 61 184 77L178 113Q150 130 122 113Z" fill="#293D35"/><path d="M125 86L142 91M158 91L175 86" fill="none" stroke="#F1D591" stroke-width="6"/><path d="M143 32L152 15 161 32 158 111H146Z" fill="#E6EEE7"/><path d="M104 148Q150 126 196 148L190 235H110Z" fill="#8DB5A1"/><path d="M116 158L148 172 184 157 176 208H123Z" fill="#D9E2DC"/><path d="M145 172H158V224H145Z" fill="#E7BA61"/><path d="M78 147Q95 127 113 149L96 205H66Z" fill="#D4E0D7"/><path d="M187 149Q205 128 224 148L233 205H205Z" fill="#D4E0D7"/><path d="M68 201L96 207 91 252H61Z" fill="#8DB5A1"/><path d="M205 205L234 198 241 249H211Z" fill="#8DB5A1"/><path d="M110 231H190L182 280 160 287 150 255 139 287 116 280Z" fill="#4F675A"/><path d="M115 275L141 280 134 339H96L107 320Z" fill="#BACDC0"/><path d="M160 280L185 275 194 321 207 339H166Z" fill="#BACDC0"/><path d="M251 86L264 59 276 87 270 209H251Z" fill="#E0ECE4"/><path d="M238 205H283V216H238Z" fill="#E7BA61"/><path d="M254 216H268V267H254Z" fill="#916A3A"/><path d="M18 186Q49 167 79 186L75 246Q51 273 47 278 24 263 18 246Z" fill="#799A87"/><path d="M29 195L66 195 64 238 48 259 31 239Z" fill="#C8D6CB"/></g></svg>`);

export default makeScene2D(function*(view){
 const t=createSignal(0);
 const frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001));
 const section=()=>timing.sections.find(s=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections[timing.sections.length-1];
 const id=()=>section().id;
 const game=()=>section().kind==='game';
 const is=(...ids:string[])=>ids.includes(id());
 const step=()=>is('state')?smooth((t()-21.4)/1.5):is('confirm-explain','close')?1:0;
 const stateX=()=>step()>.5?3:2;
 const planeX=()=>-61.875+step()*148.75;
 const projection=()=>is('jobs')?smooth((t()-9.4667)/.75):1;
 const upperReveal=()=>is('layer')?.28+.72*smooth((t()-14.9167)/.7):1;
 const root='/@fs/D:/Github/VideoEditing/projects/shorts-d2r-renderer-logic-separation/production/local/'+timing.frameRoot;
 view.fill('#000000');
 const label=(parent:Node,text:any,x:number,y:number,size=36,color:any=C.white)=>parent.add(<Txt text={text} position={[x-540,y-960]} fontFamily={font} fontSize={size} fontWeight={700} fill={color}/>);

 // Fixed header is copied from the approved raster at final encode, unchanged.
 label(view,'얌얌코딩',196,117,34,C.muted);
 label(view,'그래픽을 바꿨는데',520,255,64);
 label(view,'전투는 그대로?',520,353,70,C.yellow);

 const footage=new Node({opacity:()=>game()?1:0});view.add(footage);
 label(footage,'디아블로 II: 레저렉션 · 동일 시점 비교',540,466,32,C.white);
 for(let i=0;i<2;i++){
   const y=i?1100:680;
   const panel=new Rect({position:[0,y-960],size:[960,360],clip:true});footage.add(panel);
   panel.add(<Img src={()=>`${root}/${id()==='confirm'?'barracks':'tristram'}-${i?'old':'new'}/${String(game()?Math.max(0,frame()-section().startFrame):0).padStart(5,'0')}.jpg`} size={[960,360]}/>);
   panel.add(<Rect size={[954,354]} stroke={i?C.teal:C.green} lineWidth={6}/>);
   panel.add(<Rect position={[-300,-145]} size={[340,58]} fill="#000000DD"/>);
   panel.add(<Txt text={i?'아래 · 클래식':'위 · 레저렉션'} position={[-300,-145]} fontFamily={font} fontSize={32} fontWeight={700} fill={i?C.teal:C.green}/>);
 }
 label(footage,'같은 장면 · 같은 순간',540,890,35,C.yellow);

 const diagram=new Node({opacity:()=>game()?0:1});view.add(diagram);
 label(diagram,'원리 설명 · 표시 계층을 펼친 도식',540,466,31,C.muted);
 const common=new Node({position:[145-540,875-960]});diagram.add(common);
 common.add(<Rect size={[230,300]} stroke={()=>is('jobs')&&t()<9.4667?C.yellow:C.teal} lineWidth={5} fill="#08110D"/>);
 for(const [text,y,size,color] of [['공통 상태',-100,36,C.yellow],['게임 로직',-49,31,C.white],['위치 · 공격',6,29,C.white]] as const){
   common.add(<Txt text={text} y={y} fontFamily={font} fontSize={size} fontWeight={700} fill={color}/>);
 }
 common.add(<Txt text={()=>`x = ${stateX()}`} y={64} fontFamily={font} fontSize={45} fontWeight={700} fill={C.teal}/>);
 common.add(<Txt text="예시 위치" y={115} fontFamily={font} fontSize={25} fill={C.muted}/>);

 // Both arrows carry the same conceptual state. No claim that the production
 // game renders both views on every frame, or stores two physical worlds.
 for(let i=0;i<2;i++){
   const y=i?1080:690;
   const col=i?C.teal:C.green;
   diagram.add(<Line points={[[260-540,875-960],[302-540,875-960],[302-540,y-960],[355-540,y-960]]} stroke={col} lineWidth={7} endArrow arrowSize={18} end={projection}/>);
   const n=new Node({position:[670-540,y-960],opacity:()=>i?1:upperReveal()});diagram.add(n);
   n.add(<Txt text={i?'아래 · 클래식 표시':'위 · 레저렉션 표시'} y={-175} fontFamily={font} fontSize={40} fontWeight={700} fill={col}/>);
   n.add(<Txt text={i?'스프라이트':'새 3D 모델'} y={-124} fontFamily={font} fontSize={30} fill={C.white}/>);
   const floor=[[-285,75],[-205,-35],[260,-35],[310,75]] as [number,number][];
   n.add(<Line points={floor} closed fill={i?'#0C2522':'#13271D'} stroke={col} lineWidth={4}/>);
   for(let k=0;k<=4;k++){
     n.add(<Line points={[[-285+k*148.75,75],[-205+k*116.25,-35]]} stroke={C.line} lineWidth={2}/>);
     if(k<4)n.add(<Txt text={String(k+1)} position={[-210.625+k*148.75,108]} fontFamily={font} fontSize={30} fill={C.muted}/>);
   }
   n.add(<Line points={[[-245,20],[285,20]]} stroke={C.line} lineWidth={2}/>);
   n.add(<Line points={()=>[[planeX()-45,60],[planeX()+50,60]]} stroke={C.yellow} lineWidth={7}/>);
   // Different drawings use exactly the same frame's position signal.
   n.add(<Img src={i?diabloDiagramActor:modern} size={[127.5,170]} position={()=>[planeX(),-20]}/>);
   const change=()=>is('state')?clamp((t()-21.4)/.25)*clamp((26.4-t())/.4):0;
   n.add(<Line points={[[-61.875,148],[86.875,148]]} stroke={C.yellow} lineWidth={6} endArrow arrowSize={18} opacity={change} end={()=>step()}/>);
 }
 label(diagram,()=>is('jobs')?'① 계산 → ② 화면에 그리기':is('state')?'한 칸 이동 → 두 표시가 함께 이동':is('layer')?'하나의 게임 상태 → 두 가지 모습':'게임 로직과 렌더링의 분리',540,1258,32,C.yellow);
 label(diagram,()=>is('close')?'Game Logic / Rendering':is('state')?'공유한 위치 값으로 같은 동작을 표시':'',540,1510,31,C.muted);

 // Late reaction below all teaching marks and below the fixed caption band.
 const cat=new Rect({position:[290,775],size:[560,480],clip:true,opacity:()=>clamp((t()-40.15)/.22)*clamp((43.55-t())/.22)});view.add(cat);
 cat.add(<Img src={relief} size={520} position={[0,45]}/>);
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
