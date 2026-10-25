import {makeScene2D, Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear, Vector2} from '@motion-canvas/core';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';

const C={white:'#FFFFFF',yellow:'#FFD25A',teal:'#73D7CD',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',blue:'#64A8F5',oil:'#DB9C48'},FONT='Malgun Gothic';
const cap=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{x=cap(x);return x*x*(3-2*x);};

/** Authored explanatory diagrams, never recovered commercial-game buffers. */
export function composite(slug:string,cfg:any,timing:any){return makeScene2D(function*(view){
 const t=createSignal(0),frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+0.0001));
 const sec=()=>timing.sections.find((s:any)=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections.at(-1);
 const id=()=>sec().visualId??sec().id,e=()=>t()-sec().start,span=()=>sec().end-sec().start,phase=()=>cap(e()/span());
 const footage=()=>!sec().forceDiagram&&!!cfg.cuts[id()]&&e()<cfg.cuts[id()].maxDuration;
 const gameId=()=>footage()?(sec().frameDirectory??cfg.cuts[id()].frameDirectory??id()):(cfg.cuts.game.frameDirectory??'game');
 const gameFrame=()=>footage()?Math.max(0,Math.min(sec().endFrame-sec().startFrame-1,Math.floor(cfg.cuts[id()].maxDuration*60+1e-8)-1,frame()-sec().startFrame)):0;
 const eventElapsed=(name:string,fallback:number)=>timing.events?.[name]?t()-timing.events[name].startFrame/60:fallback;
 const ROOT='/@fs/D:/Github/VideoEditing/projects/'+slug+'/production/local/';
 const reaction=()=>timing.reactions.find((r:any)=>t()>=r.start&&t()<r.end);
 const catPresence=()=>{const r=reaction();return r?cap((t()-r.start)/.18)*cap((r.end-t())/.2):0;};
 // Noita keeps the grid clear throughout the cat's exit; opacity is not a
 // safe proxy for its occupied area. Restore the grid only after the cat is gone.
 const diagramReserve=()=>{
  if(cfg.topic!=='noita')return catPresence();
  const r=timing.reactions.find((r:any)=>t()>=r.start-.18&&t()<r.end+.22);
  return !r?0:t()<r.start?smooth((t()-r.start+.18)/.18):t()<=r.end?1:1-smooth((t()-r.end)/.22);
 };
 view.fill('#000');
 const diagram=new Node({opacity:()=>footage()?0:1,position:()=>[-25-170*diagramReserve(),-25-140*diagramReserve()],scale:()=>1-.22*diagramReserve()});view.add(diagram);
 const labels:any={material:'색 + 물질의 종류',flow:'이웃한 빈칸을 확인한다',compare:'같은 불 · 주변 물질만 변경',rules:'작은 규칙이 이어지는 세계',chunks:'몸의 기본 구조 = 두 덩어리',constraint:'거리 유지 → 몸의 방향 변화',limbs:'계산한 몸 위에 팔다리와 꼬리',term:'입력과 상태로 자세를 계산',reveal:'밝은 점 + 어두운 점',ratio:'새 색 대신, 점의 비율',shade:'작은 점들이 모이면 명암',motion:'카메라 이동과 패턴의 관계',close:cfg.topic==='noita'?'작은 물질 규칙 → 큰 변화':cfg.topic==='rain'?'연결된 두 덩어리 → 다양한 동작':'두 가지 색 → 풍부한 명암',game:'원리를 확대해 보면'};
 diagram.add(<Txt text={()=>labels[id()]??''} position={()=>[0,-345+82*diagramReserve()]} fill={C.yellow} fontFamily={FONT} fontSize={42} fontWeight={700}/>);

 if(cfg.topic==='noita'){
  const cols=24,rows=13,size=34;
  // Deterministic discrete water model: one particle moves at most one cell per tick.
  const flowStates:number[][]=[];let a=Array(cols*rows).fill(0);
  for(let y=1;y<5;y++)for(let x=9;x<15;x++)a[y*cols+x]=1;
  for(let x=0;x<cols;x++)a[(rows-1)*cols+x]=3;
  for(let y=7;y<10;y++)for(let x=10;x<14;x++)a[y*cols+x]=3;
  flowStates.push(a.slice());
  for(let k=0;k<220;k++){const b=a.slice(),moved=new Set<number>();for(let y=rows-2;y>=0;y--)for(let x=0;x<cols;x++){
   const n=y*cols+x;if(a[n]!==1||moved.has(n))continue;
   const dirs=k%2?[1,-1]:[-1,1];let to=-1;
   if(a[n+cols]===0&&b[n+cols]===0)to=n+cols;
   else for(const dx of dirs){const nx=x+dx;if(nx>0&&nx<cols-1&&a[n+dx]===0&&b[n+dx]===0){to=n+dx;break;}}
   if(to>=0){b[n]=0;b[to]=1;moved.add(to);}
  }a=b;flowStates.push(a.slice());}
  const material=(x:number,y:number)=>{
   if(id()==='flow'){
    const falling=Math.max(0,eventElapsed('flowFallStart',e())),side=eventElapsed('flowSideStart',e());
    const steps=timing.events?(side<0?Math.min(2,Math.floor(falling*5)):2+Math.floor(side*5)):Math.floor(e()*5);
    return flowStates[Math.max(0,Math.min(219,steps))][y*cols+x];
   }
   if(id()==='compare'){
    const right=x>=12,xx=x%12,inside=xx>=3&&xx<=8&&y>=3&&y<=8;
    const burn=eventElapsed('oilIgnition',e()-1),water=eventElapsed('waterReplacement',e());
    if(inside){if(right)return water<0?0:1;const d=Math.abs(xx-3)+Math.abs(y-8);return burn>d*.22?(burn>2.4+d*.22?5:4):2;}
    if(xx===2&&y===8)return right&&water>1.1?0:4;return 0;
   }
   if(y>8)return 3;
   if(x<8&&y>3)return 1;
   if(x>15&&y>3){const d=x-16+y-4;return id()==='rules'&&e()>1+d*.18?(e()>3+d*.18?5:4):2;}
   return 0;
  };
  const colors=['#0C1518',C.blue,C.oil,'#52616B','#FF7440','#AAAFAF'];
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)diagram.add(<Rect position={[(x-(cols-1)/2)*size,(y-(rows-1)/2)*size-15]} size={size-3} radius={2} fill={()=>colors[material(x,y)]}/>);
  diagram.add(<Line points={[[-420,235],[420,235]]} stroke="#52616B" lineWidth={3}/>);
  diagram.add(<Txt text="물은 내려가고, 막히면 옆으로" position={[0,280]} fill={C.white} fontFamily={FONT} fontSize={35} fontWeight={700} opacity={()=>id()==='flow'?1:0}/>);
  for(const [x,plain,compare] of [[-280,'물','기름 · 불이 번짐'],[0,'빈 공간',''],[280,'기름','물 · 불을 막음']] as const)diagram.add(<Txt text={()=>id()==='compare'?compare:plain} position={[x,280]} fill={C.white} fontFamily={FONT} fontSize={id()==='compare'?31:35} fontWeight={700} opacity={()=>id()==='flow'||(id()==='compare'&&x===280&&eventElapsed('waterReplacement',e())<0)?0:1}/>);
  diagram.add(<Line points={[[0,-255],[0,-160]]} stroke={C.teal} lineWidth={7} endArrow arrowSize={22} end={()=>id()==='flow'?smooth(e()/.7):0} opacity={()=>id()==='flow'?1:0}/>);
  diagram.add(<Txt text="우리의 단순화한 물질 격자" position={[0,325]} fill={C.muted} fontFamily={FONT} fontSize={28}/>);
 }

 if(cfg.topic==='rain'){
  const L=192;
  // p3-1: lift the front first, advance over the ledge, then let the rear
  // catch up. p3-2 starts only after that pose, at the real caption anchor.
  const rotationAt=()=>timing.events?.bodyRotation?(timing.events.bodyRotation.startFrame-sec().startFrame)/60:1.85;
  const climb=()=>smooth((e()-2/60)/Math.max(.01,rotationAt()-2/60));
  const climbingFront=():[number,number]=>[145*smooth((climb()-.35)/.30),74-124*smooth(climb()/.35)];
  const climbingRearY=()=>126-52*smooth((climb()-.35)/.30)+( -50-Math.sin(.12)*L-74)*smooth((climb()-.65)/.35);
  const angle=()=>{
   if(id()!=='constraint')return-.28+Math.sin(e()*1.5)*.28;
   if(e()<rotationAt())return Math.asin((climbingFront()[1]-climbingRearY())/L);
   const duration=timing.events?.bodyRotation?(timing.events.bodyRotation.endFrame-timing.events.bodyRotation.startFrame)/60:2.4667;
   return .12+smooth(eventElapsed('bodyRotation',e()-rotationAt())/duration)*.92;
  };
  const front=():[number,number]=>id()==='constraint'?climbingFront():[90+Math.sin(e()*.7)*80,-45-Math.sin(e()*1.2)*30];
  const rear=():[number,number]=>{const f=front();return[f[0]-Math.cos(angle())*L,f[1]-Math.sin(angle())*L];};
  const skin=()=>['limbs','term','close'].includes(id())&&(id()!=='limbs'||eventElapsed('limbsAdded',e())>=0);
  diagram.add(<Line points={[[-430,190],[-20,190],[-20,145],[240,145],[240,190],[430,190]]} stroke="#6D777E" lineWidth={11}/>);
  diagram.add(<Rect position={[145,85]} width={135} height={128} fill="#27343C" stroke="#6D777E" lineWidth={4} opacity={()=>id()==='constraint'?1:0}/>);
  diagram.add(<Line points={()=>[rear(),front()]} stroke={()=>skin()?'#DFEBE4':C.muted} lineWidth={()=>skin()?112:9} lineCap="round"/>);
  const legs=new Node({opacity:()=>skin()?1:0});diagram.add(legs);
  for(let i=0;i<4;i++)legs.add(<Line points={()=>{const b=i<2?front():rear(),sg=i%2?1:-1,z=Math.sin(e()*3+i*1.7);return[[b[0]+sg*24,b[1]+27],[b[0]+sg*38+z*15,b[1]+78],[b[0]+sg*49-z*20,157]];}} stroke={i%2?'#D8E5DD':'#AABAB0'} lineWidth={13} lineCap="round"/>);
  legs.add(<Line points={()=>{const b=rear();return[[b[0]-35,b[1]+24],[b[0]-110,b[1]+48],[b[0]-165,b[1]+30+Math.sin(e()*2)*35]];}} stroke="#D8E5DD" lineWidth={28} lineCap="round"/>);
  diagram.add(<Circle position={rear} size={128} fill={()=>skin()?'#D8E5DD':'#0E242B'} stroke={C.teal} lineWidth={5}/>);
  diagram.add(<Circle position={front} size={142} fill={()=>skin()?'#EAF4EE':'#302B15'} stroke={C.yellow} lineWidth={5}/>);
  for(const dx of [-33,33])diagram.add(<Line points={()=>{const f=front();return[[f[0]+dx-17,f[1]-40],[f[0]+dx,f[1]-105],[f[0]+dx+22,f[1]-40]];}} stroke="#EAF4EE" lineWidth={18} lineJoin="round" opacity={()=>skin()?1:0}/>);
  for(const dx of [-25,25])diagram.add(<Circle position={()=>{const f=front();return[f[0]+dx,f[1]-8];}} size={16} fill="#12202B" opacity={()=>skin()?1:0}/>);
  diagram.add(<Line points={()=>{const f=front(),b=rear(),dx=Math.sin(angle())*145,dy=-Math.cos(angle())*145;return[[b[0]+dx,b[1]+dy],[f[0]+dx,f[1]+dy]];}} stroke={C.green} lineWidth={5} startArrow endArrow arrowSize={17}/>);
  diagram.add(<Txt text="중심 사이 거리 유지" position={[0,220]} fill={C.green} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  diagram.add(<Txt text={()=>id()==='constraint'?(e()<rotationAt()?'앞쪽 상승 → 뒤쪽이 따라옴':'앞쪽이 걸려도 → 뒤쪽이 회전'):skin()?'몸의 상태 → 팔다리 자세 계산':'앞 몸체 + 뒤 몸체'} position={[0,270]} fill={C.white} fontFamily={FONT} fontSize={36} fontWeight={700}/>);
  diagram.add(<Txt text="우리의 두 점 연결 시연" position={[0,325]} fill={C.muted} fontFamily={FONT} fontSize={28}/>);
 }

 if(cfg.topic==='obra'){
  const big=new Node({opacity:()=>['reveal','ratio'].includes(id())?1:0});diagram.add(big);
  const order=[0,10,2,8,5,15,7,13,1,11,3,9,4,14,6,12];
  const bright=()=>id()==='ratio'?(timing.events?(eventElapsed('twelveCells',e())<0?4:12):(phase()<.48?4:12)):8;
  for(let y=0;y<4;y++)for(let x=0;x<4;x++)big.add(<Rect position={[(x-1.5)*118,(y-1.5)*118-30]} size={111} fill={()=>order.indexOf(y*4+x)<bright()?'#EFF3D1':'#19251D'} stroke="#637064" lineWidth={2}/>);
  big.add(<Txt text={()=>`밝은 칸 ${bright()} / 16`} position={[0,270]} fill={C.white} fontFamily={FONT} fontSize={42} fontWeight={700}/>);
  const fine=new Node({opacity:()=>['reveal','ratio'].includes(id())?0:1});diagram.add(fine);
  const nX=48,nY=26,size=17,bayer=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];
  const shift=()=>id()==='motion'?Math.floor(e()*13):0;
  const unstable=()=>timing.events?eventElapsed('patternStable',e())<0:phase()<.5;
  const pixel=(x:number,y:number)=>{
   const xx=(x+(id()==='motion'?Math.sin(e()*.9)*6:0)-23.5)/24,yy=(y-12.5)/13;
   const l=cap(.82-.7*Math.sqrt(xx*xx+yy*yy)+.12*Math.sin((x+y)*.15));
   const dx=id()==='motion'&&unstable()?shift():0;
   return l>(bayer[((y+dx)%4)*4+(x+dx)%4]+.5)/16;
  };
  for(let y=0;y<nY;y++)for(let x=0;x<nX;x++)fine.add(<Rect position={[(x-(nX-1)/2)*size,(y-(nY-1)/2)*size-30]} size={size+.15} fill={()=>pixel(x,y)?'#EFF3D1':'#19251D'}/>);
  fine.add(<Txt text={()=>id()==='motion'?(unstable()?'패턴이 흔들리는 예시':'패턴을 안정시킨 예시'):'점의 밀도 → 눈에 보이는 밝기'} position={[0,270]} fill={()=>id()==='motion'&&unstable()?C.red:C.teal} fontFamily={FONT} fontSize={38} fontWeight={700}/>);
  diagram.add(<Txt text="우리의 디더링 시연" position={[0,325]} fill={C.muted} fontFamily={FONT} fontSize={28}/>);
 }

 const rainCrop=()=>cfg.topic==='rain'&&['game','close'].includes(id());
 const gameHeight=()=>rainCrop()?700:563;
 const game=new Rect({position:[-20,-35],width:1000,height:gameHeight,clip:true,opacity:()=>footage()?1:0});view.add(game);
 game.add(<Img src={()=>ROOT+'game-frames/'+gameId()+'/'+String(gameFrame()).padStart(5,'0')+'.jpg'} width={()=>rainCrop()?2000:1000} height={()=>rainCrop()?1125:562.5} position={()=>rainCrop()?(id()==='game'?[375,-94]:[62.5,-212.5]):[0,0]}/>);
 game.add(<Rect position={()=>[0,-gameHeight()/2+36]} width={1000} height={70} fill="#000000A0"/>);
 game.add(<Txt text={cfg.game} position={()=>[-455,-gameHeight()/2+36]} offset={[-1,0]} fill={C.white} fontFamily={FONT} fontSize={33} fontWeight={700}/>);
 // Editorial focus marks are restricted to the directly inspected source interval.
 if(cfg.topic==='noita'){
  // Hand-checked source coordinates, 1920x1080, source430s + local seconds.
  // The explosion obscures the platform at2.16–2.90s: clear guides then.
  const point=(keys:number[][]):[number,number]=>{
   const next=keys.findIndex(k=>k[0]>e());
   const a=keys[Math.max(0,next<0?keys.length-1:next-1)],b=keys[next<0?keys.length-1:next];
   const u=a===b?0:cap((e()-a[0])/(b[0]-a[0]));
   return[(a[1]+(b[1]-a[1])*u-960)*1000/1920,(a[2]+(b[2]-a[2])*u-540)*1000/1920];
  };
  const cue=(start:number,end:number)=>id()==='game'&&footage()?smooth((e()-start)/.10)*smooth((end-e())/.10):0;
  const fire=()=>point([[.2,1270,353],[.5,1290,353],[1.2,1330,351],[1.45,1360,337]]);
  const fireGuide=new Node({opacity:()=>cue(.2,1.45)});game.add(fireGuide);
  fireGuide.add(<Txt text="타는 나무" position={[50,-187]} fill={C.red} fontFamily={FONT} fontSize={36} fontWeight={700} stroke="#000" lineWidth={6} strokeFirst/>);
  fireGuide.add(<Line points={()=>[[75,-162],fire()]} stroke={C.red} lineWidth={8} endArrow arrowSize={22} end={()=>smooth((e()-.2)/.18)}/>);
  const platform=()=>point([[1.55,795,633],[2,850,625],[2.16,850,625],[2.9,845,625],[3.2,830,630],[3.55,800,625]]);
  const platformGuide=new Node({opacity:()=>Math.max(cue(1.55,2.16),cue(2.9,3.55))});game.add(platformGuide);
  platformGuide.add(<Rect position={platform} size={[180,58]} radius={9} stroke={C.green} lineWidth={8}/>);
  platformGuide.add(<Txt text={()=>e()<2.16?'나무 발판':'발판이 사라진 자리'} position={[-220,-112]} fill={C.green} fontFamily={FONT} fontSize={35} fontWeight={700} stroke="#000" lineWidth={6} strokeFirst/>);
  platformGuide.add(<Line points={()=>{const p=platform();return[[-205,-87],[p[0]-12,p[1]-39]];}} stroke={C.green} lineWidth={8} endArrow arrowSize={22} end={()=>smooth((e()-(e()<2.16?1.55:2.9))/.16)}/>);
 }
 game.add(<Circle position={[-10,0]} size={[130,210]} stroke={C.green} lineWidth={6} opacity={()=>cfg.topic==='rain'&&id()==='game'&&e()>1.5&&e()<2.5?1:0}/>);
 game.add(<Txt text="몸의 움직임" position={[200,90]} fill={C.green} fontFamily={FONT} fontSize={30} fontWeight={700} stroke="#000" lineWidth={5} strokeFirst opacity={()=>cfg.topic==='rain'&&id()==='game'&&e()>1.5&&e()<2.5?1:0}/>);
  const head=(kind:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="540"><rect width="1080" height="540" fill="black"/><g font-family="Malgun Gothic" font-weight="700"><text x="105" y="128" font-size="37" fill="${C.muted}">얌얌코딩</text><text x="510" y="260" text-anchor="middle" font-size="${cfg.topic==='obra'?64:68}" fill="white">${cfg.head[0]}</text><text x="510" y="363" text-anchor="middle" font-size="${cfg.topic==='obra'?62:71}" fill="${C.yellow}">${cfg.head[1]}</text><text x="75" y="478" font-size="29" fill="${C.teal}">${cfg.term}</text><text x="75" y="520" font-size="23" fill="${C.muted}">${cfg.english}</text><text x="880" y="478" text-anchor="middle" font-size="27" fill="${C.muted}">${kind}</text></g></svg>`);
 [head('실제 게임'),head('원리 시연')].forEach((src,i)=>view.add(<Img src={src} size={[1080,540]} position={[0,-690]} zIndex={8} opacity={()=>footage()?(i===0?1:0):(i===1?1:0)}/>));
 const cat=new Rect({size:[560,860],position:[280,110],clip:true,opacity:catPresence});view.add(cat);
 cat.add(<Img src={()=>reaction()?.kind==='relief'?relief:realize} size={780} position={()=>[80+30*(1-catPresence()),30]}/>);
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});}
