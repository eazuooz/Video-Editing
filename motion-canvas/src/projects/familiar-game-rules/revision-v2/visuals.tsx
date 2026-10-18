import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

export interface Timing {duration:number; cues?:number[]; title?:string; credit?:string;}
type Point = [number,number];
const ASSETS='/@fs/D:/Github/VideoEditing/output/familiar-game-rules/preproduction-assets/';
const clamp=(value:number)=>Math.max(0,Math.min(1,value));
const smooth=(value:number)=>{const x=clamp(value);return x*x*(3-2*x);};
const text=(value:string,x:number,y:number,size=48,color:string=D.ink)=><Txt text={value} x={x} y={y} fontSize={size} lineHeight={size*1.28} fill={color} fontWeight={600} fontFamily={D.font}/>;

/**
 * Independently authored explanation scenes. All image files are inspected,
 * rights-recorded gameplay/menu evidence supplied by the production plan.
 * Input diagrams are illustrations, not captured inputs or measured game data.
 * Content ends above MC y=340; fixed captions at MC y=430 are never relocated.
 * timing.cues contains measured paragraph starts, in scene-local seconds.
 */
export function* lesson(view:View2D,kind:string,timing:Timing){
 const t=createSignal(0),duration=timing.duration;
 // Short look-development scenes compress their reveal/response durations
 // along with the supplied cues. Normal measured lesson scenes retain1x.
 const motionScale=Math.min(1,duration/8);
 const fallback=[0,.18,.36,.54,.72,.88];
 const at=(index:number)=>timing.cues?.[index]??duration*(fallback[Math.min(index,fallback.length-1)]??0);
 const reveal=(index:number,delay=0,length=.55)=>()=>smooth((t()-at(index)-delay*motionScale)/(length*motionScale));
 const interval=(index:number,endIndex?:number)=>()=>reveal(index)()*(endIndex===undefined?1:1-smooth((t()-at(endIndex))/(.4*motionScale)));
 const add=(index:number,children:any,delay=0)=>view.add(<Node opacity={reveal(index,delay)}>{children}</Node>);
 const during=(index:number,endIndex:number|undefined,children:any)=>view.add(<Node opacity={interval(index,endIndex)}>{children}</Node>);
 const label=(value:string,x:number,y:number,index:number,color:string=D.ink,size=48,delay=0)=>add(index,text(value,x,y,size,color),delay);
 const trace=(points:Point[]|(()=>Point[]),index:number,color:string=D.teal,delay=0,parent:Node|View2D=view)=>parent.add(<Line points={points} stroke={color} lineWidth={9} endArrow arrowSize={22} end={reveal(index,delay,.85)} lineCap={'round'} lineJoin={'round'}/>);
 const diagramNode=(value:string,x:number,y:number,index:number,color:string=D.teal,width=260,delay=0)=>add(index,<><Rect x={x} y={y} width={width} height={96} stroke={color} lineWidth={5} fill={D.background}/>{text(value,x,y,45,color)}</>,delay);
 const image=(file:string,x:number,y:number,width:number,caption:string,captionColor:string=D.ink)=>{
  const height=width*9/16;
  // Preserve each inspected source's aspect ratio inside the unchanged16:9
  // viewport. Caption positions follow the viewport, not the contained image.
  const sourceRatio=file==='atomic-run.png'?4/3:file==='acc-remap.png'?1600/1020:16/9;
  const containedWidth=Math.min(width,height*sourceRatio),containedHeight=containedWidth/sourceRatio;
  return <><Rect x={x} y={y} width={width} height={height} fill={D.background}/><Img src={ASSETS+file} x={x} y={y} width={containedWidth} height={containedHeight}/><Rect x={x} y={y} width={width+4} height={height+4} stroke={D.line} lineWidth={2}/>{text(caption,x,y+height/2+41,37,captionColor)}</>;
 };
 const note=(value:string,index:number,color:string=D.muted,size=36)=>label(value,0,315,index,color,size);
 const titles:Record<string,string>={
  overview:'처음인데, 손이 먼저 움직이는 이유',fps:'다른 게임에서도 이어지는 조작',controller:'두 게임의 기본 조작을 나란히 보기',world:'같은 조작으로, 다른 경험을 만들기',
  newcomer:'아는 만큼 줄이고, 모르는 곳은 돕기',standard:'널리 쓰이며 익숙해진 약속',remap:'행동은 두고, 입력의 연결을 바꾸기',
  preference:'기본 배치와 플레이어의 선택',analog:'방향은 같아도, 입력의 크기는 다릅니다',limits:'연결 변경과 기능 보존은 다릅니다',
  unusual:'낯선 연결도 하나의 경험이 됩니다',conclusion:'남길 익숙함과 배울 새로움',
 };
 if(!(kind in titles))throw Error(`Unknown familiar-game-rules explanation: ${kind}`);
 view.fill(D.background);
 view.add(<>{text('얌얌코딩  /  익숙한 게임 조작',-585,-482,29,D.muted)}{text(timing.title??titles[kind],0,-393,58,D.title)}</>);
 if(timing.credit)view.add(<Txt text={timing.credit} x={560} y={-482} width={700} textAlign={'right'} textWrap fontSize={23} lineHeight={29} fontWeight={500} fontFamily={D.font} fill={D.muted}/>);

 switch(kind){
  case 'overview': {
   during(0,2,<>{image('rage-reticle.png',-440,-39,790,'RAGE 2')}{image('apex-reticle.png',440,-39,790,'Apex Legends')}</>);
   during(1,2,text('이미 배운 이동 · 조준 · 발사',0,301,47,D.teal));
   during(2,3,<>
    {text('익숙한 약속',-580,-105,54,D.teal)}{text('바꿀 수 있는 연결',0,-105,50,D.ink)}{text('장치가 주는 정보',580,-105,48,D.green)}
    <Line points={[[-400,-105],[-205,-105]]} stroke={D.teal} lineWidth={9} endArrow arrowSize={22} end={reveal(2,.25,.85)}/>
    <Line points={[[215,-105],[385,-105]]} stroke={D.green} lineWidth={9} endArrow arrowSize={22} end={reveal(2,1.1,.85)}/>
    {text('무엇을 남기고, 무엇을 새로 설계할까요?',0,130,54,D.title)}
   </>);
   during(3,undefined,<>{image('rage-reticle.png',-440,-39,790,'바라보고 · 움직이고')}{image('apex-reticle.png',440,-39,790,'대상을 겨누고 · 발사')}</>);
   break;
  }
  case 'fps': {
   view.add(<>{text('일인칭 슈팅 게임  /  First-Person Shooter · FPS',0,-302,37,D.muted)}{image('rage-reticle.png',-440,-31,790,'RAGE 2')}{image('apex-reticle.png',440,-31,790,'Apex Legends')}</>);
   during(0,2,text('플레이어 자신의 시점에서 공간과 대상을 봅니다',0,307,39,D.ink));
   during(2,3,<>
    {text('이동',-550,304,48,D.teal)}{text('조준',0,304,48,D.ink)}{text('발사',550,304,48,D.green)}
    <Line points={[[-410,304],[-140,304]]} stroke={D.teal} lineWidth={7} endArrow arrowSize={18} end={reveal(2,0,.85)}/>
    <Line points={[[140,304],[410,304]]} stroke={D.green} lineWidth={7} endArrow arrowSize={18} end={reveal(2,.85,.85)}/>
   </>);
   during(3,4,text('공통된 역할 ≠ 모든 기기의 같은 버튼',0,307,43,D.title));
   during(4,undefined,text('익숙한 역할을 남기면, 새로운 판단에 집중할 수 있습니다',0,307,37,D.green));
   break;
  }
  case 'controller': {
   // Left: independently captured FHD RAGE2 Xbox default-controller menu.
   // Right: four EA-documented Apex defaults, not an invented settings capture.
   // No callout is placed at an unverified point inside the original menu.
   add(0,image('rage-controller.png',-470,-45,900,'RAGE 2 · Xbox 기본 배치'));
   label('Apex Legends',450,-285,0,D.title,47);
   label('EA 공식 기본 배치',450,-231,0,D.muted,32);
   const rows=[['Left Stick','이동'],['Right Stick','시점'],['LT','조준'],['RT','발사']];
   rows.forEach(([input,action],index)=>{
    const y=-132+index*116,color=index<2?D.teal:D.green;
    const delay=index*Math.max(.25,duration*.12);
    add(0,text(input,210,y,40,color),delay);
    trace([[365,y],[568,y]],0,color,delay+.15);
    add(0,<>{text(action,710,y,51,color)}<Line points={[[638,y+43],[782,y+43]]} stroke={color} lineWidth={4}/></>,delay+1);
   });
   note('Xbox 기본 배치의 네 기능만 비교',0,D.muted,36);
   break;
  }
  case 'world': {
   add(0,image('rage-reticle.png',-440,-28,790,'세계와 분위기',D.teal));
   add(1,image('apex-team.png',440,-28,790,'팀과 상대의 위치',D.green));
   during(0,2,text('입력이 같아도, 들어갈 세계는 달라집니다',0,305,43,D.ink));
   during(2,4,text('적의 위치 · 지킬 대상 · 능력을 쓸 순간',0,305,43,D.title));
   during(4,undefined,text('그 조작을 처음 만나는 사람은 어떨까요?',0,305,45,D.green));
   break;
  }
  case 'newcomer': {
   add(0,image('apex-reticle.png',-445,-35,800,'행동과 화면의 반응을 함께 보기'));
   diagramNode('처음 하는 사람',445,-195,0,D.teal,540);
   trace([[445,-132],[445,-67]],0,D.teal,.25);
   label('행동과 결과부터',445,-17,0,D.teal,49,1.1);
   diagramNode('이미 아는 사람',445,119,1,D.green,540);
   trace([[445,182],[445,228]],1,D.green,.25);
   label('달라진 규칙부터',445,277,1,D.green,46,1.1);
   // The actual fire/ammunition clips remain separately reviewed gameplay;
   // no invented number or cursor location is superimposed on this still.
   during(3,5,text('새 기능은 무엇이 일어나는지도 설명합니다',-435,307,31,D.muted));
   during(5,undefined,<Rect x={445} y={-17} width={590} height={84} stroke={D.title} lineWidth={4}/>);
   break;
  }
  case 'standard': {
   label('사실상의 표준  /  de facto standard',0,-300,0,D.title,43);
   const u=()=>smooth((t()-at(1)-.85*motionScale)/(1.35*motionScale));
   // Recognizable mouse and pointer silhouettes are authored illustrations.
   const mouse=<Node x={()=>-570+70*u()} y={-48}>
    <Rect width={142} height={208} radius={65} stroke={D.ink} lineWidth={7} fill={D.background}/>
    <Line points={[[0,-104],[0,-20]]} stroke={D.ink} lineWidth={5}/>
    <Line points={[[-66,-18],[66,-18]]} stroke={D.ink} lineWidth={5}/>
    <Rect x={0} y={-56} width={18} height={35} radius={7} stroke={D.teal} lineWidth={4}/>
   </Node>;
   add(1,<>{mouse}{text('마우스를 움직임',-530,155,46,D.teal)}</>);
   trace([[-385,-40],[-180,-40],[125,-40]],1,D.teal);
   add(1,<Node opacity={reveal(1,.85)}><Rect x={475} y={-45} width={490} height={300} stroke={D.line} lineWidth={4}/><Line points={()=>[[340+135*u(),-130],[340+135*u(),5],[375+135*u(),-26],[406+135*u(),32],[432+135*u(),18],[401+135*u(),-38],[443+135*u(),-42]]} closed fill={D.ink} stroke={D.background} lineWidth={3}/>{text('포인터 위치가 바뀜',475,155,43,D.green)}</Node>);
   during(2,3,<>{text('인간–컴퓨터 상호작용 (HCI)',0,263,43,D.title)}{text('Human–Computer Interaction',0,316,32,D.muted)}</>);
   during(3,undefined,text('널리 쓰인 방식에도, 개인이 바꿀 여지는 필요합니다',0,296,41,D.green));
   break;
  }
  case 'remap': {
   const menuSwitch=()=>at(0)+Math.max(.02,(at(1)-at(0))*.52);
   const beforeSwitch=()=>t()<menuSwitch()?1:0;
   const afterSwitch=()=>t()>=menuSwitch()?1:0;
   view.add(<Node opacity={()=>t()>=at(0)&&t()<at(1)?1:0}>
    <Node opacity={beforeSwitch}>{image('sf6-remap.png',-440,-33,790,'Street Fighter 6')}{image('tales-remap.png',440,-33,790,'Tales of Arise')}</Node>
    <Node opacity={afterSwitch}>{image('acc-remap.png',0,-50,880,'Assetto Corsa Competizione')}</Node>
   </Node>);
   during(1,undefined,<>{image('sf6-remap.png',-455,-24,760,'실제 설정 메뉴')}{text('버튼 리매핑  /  Button Remapping',0,-303,37,D.muted)}{text('가상 입력 연결',440,-233,44,D.title)}</>);
   const changed=()=>reveal(2,0,.85)();
   add(1,<>
    <Circle x={220} y={-108} width={104} height={104} stroke={D.teal} lineWidth={6}/>{text('A',220,-108,58,D.teal)}
    <Rect x={690} y={-108} width={210} height={106} stroke={()=>changed()>.96?D.green:D.teal} lineWidth={6}/>{text('점프',690,-108,49,D.ink)}
    <Line points={[[290,-108],[565,-108]]} stroke={D.teal} lineWidth={9} endArrow arrowSize={22} end={reveal(1,.2,.85)} opacity={()=>1-changed()}/>
   </>);
   add(2,<>
    <Circle x={220} y={78} width={104} height={104} stroke={D.green} lineWidth={6}/>{text('B',220,78,58,D.green)}
    <Line points={[[290,78],[430,78],[565,-108]]} stroke={D.green} lineWidth={9} endArrow arrowSize={22} end={reveal(2,0,.85)}/>
   </>);
   const repaired=()=>reveal(3,1.8,.45)();
   add(3,<>
    <Rect x={470} y={238} width={610} height={96} stroke={()=>repaired()>.95?D.green:D.red} lineWidth={5}/>
    <Txt text={()=>repaired()>.95?'실행 B  ·  안내 B':'실행 B  ·  안내 A'} x={470} y={238} fontSize={45} fontFamily={D.font} fontWeight={600} fill={()=>repaired()>.95?D.green:D.red}/>
    <Line points={[[470,137],[470,177]]} stroke={D.green} lineWidth={7} endArrow arrowSize={17} end={reveal(3,1,.8)}/>
   </>);
   note('설명용 A/B 배치 · 표시된 게임의 기본 버튼 배치가 아닙니다',1,D.muted,31);
   break;
  }
  case 'preference': {
   add(0,image('sf6-remap.png',-455,-24,760,'기본 배치와 선택 가능한 설정'));
   label('같은 행동, 다른 손의 습관',435,-220,0,D.title,43);
   diagramNode('제작자의 기본 배치',440,-83,0,D.teal,620);
   trace([[440,-15],[440,44]],1,D.green);
   diagramNode('플레이어의 선택',440,106,1,D.green,620,.85);
   during(2,3,text('동시 행동 · 바뀐 화면 안내 확인',440,257,37,D.ink));
   during(3,undefined,text('버튼 위치보다, 정보가 다르다면?',440,257,37,D.title));
   break;
  }
  case 'analog': {
   during(0,1,<>{text('슈퍼 스매시브라더스 얼티밋  /  Super Smash Bros. Ultimate',0,-303,35,D.muted)}{image('smash-walk.png',-440,-35,790,'걷는 장면')}{image('smash-run.png',440,-35,790,'달리는 장면')}</>);
   during(1,5,<>
    {text('방향 패드 (D-pad)',-455,-240,45,D.teal)}{text('아날로그 스틱 (Analog Stick)',450,-240,43,D.green)}
    <Line points={[[-495,-127],[-415,-127],[-415,-67],[-355,-67],[-355,13],[-415,13],[-415,73],[-495,73],[-495,13],[-555,13],[-555,-67],[-495,-67]]} closed stroke={D.ink} fill={D.background} lineWidth={7}/>
    <Rect x={-385} y={-27} width={55} height={67} fill={D.teal} opacity={reveal(1,.8)}/>
    <Circle x={450} y={-27} width={225} height={225} stroke={D.line} lineWidth={6}/>
    <Line points={[[450,-27],[550,-27]]} stroke={D.green} lineWidth={7} endArrow arrowSize={17} end={reveal(2,0,.85)}/>
   </>);
   const phase=()=>clamp((t()-at(2))/Math.max(.08,at(3)-at(2)));
   const value=()=>phase()<.2?0:phase()<.45?.25:phase()<.75?.75:1;
   during(1,5,<>
    <Circle x={()=>450+100*value()} y={-27} width={86} height={86} fill={D.background} stroke={D.green} lineWidth={7}/>
    {text('0  또는  1',-455,154,61,D.teal)}
    <Txt text={()=>t()<at(2)?'여러 중간값':value().toFixed(value()===0||value()===1?0:2)} x={450} y={154} fontSize={61} fontFamily={D.font} fontWeight={600} fill={D.green}/>
   </>);
   during(2,5,<>{text('0    0.25    0.75    1',450,215,40,D.ink)}{text('설명용 선형 환산: 최대 기울임 거리 = 1',0,270,35,D.title)}{text('실제 컨트롤러·게임의 측정값이나 속도·판정 기준이 아닙니다',0,315,30,D.muted)}</>);
   during(5,undefined,<>
    {text('대난투 스매시브라더스 X (Brawl)',0,-265,43,D.title)}
    <Rect x={-440} y={-47} width={540} height={145} radius={26} stroke={D.ink} fill={D.background} lineWidth={7}/>
    <Line points={[[-655,-47],[-565,-47]]} stroke={D.ink} lineWidth={13}/><Line points={[[-610,-92],[-610,-2]]} stroke={D.ink} lineWidth={13}/>
    <Circle x={-320} y={-47} width={54} height={54} stroke={D.ink} lineWidth={4}/>{text('1',-320,-47,29)}
    <Circle x={-222} y={-47} width={54} height={54} stroke={D.ink} lineWidth={4}/>{text('2',-222,-47,29)}
    {text('Wii 리모컨 가로 잡기 지원',-440,122,36,D.ink)}
    <Line points={[[-130,-47],[140,-47]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(5,.3,.85)}/>
    <Node opacity={reveal(5,1.15)}>{text('장치 이름보다',485,-95,45,D.muted)}{text('필요한 입력 정보',485,12,49,D.green)}</Node>
    {text('시리즈의 모든 작품이 디지털 방향 입력을 막은 것은 아닙니다',0,295,35,D.muted)}
   </>);
   break;
  }
  case 'limits': {
   add(0,image('smash-run.png',-455,-30,780,'필요한 입력이 남아 있나요?'));
   label('단순 버튼 재설정',450,-230,0,D.title,45);
   diagramNode('0 / 1',205,-70,0,D.teal,200);
   trace([[325,-70],[525,-70]],0,D.teal,.2);
   diagramNode('기울임 크기?',690,-70,0,D.red,260,1.05);
   during(0,1,text('단순 재설정으로\n중간값이 생기지는 않습니다',450,70,33,D.red));
   during(1,undefined,<>{text('별도 대안의 설계',450,65,43,D.green)}{text('보조 버튼  /  속도 선택',450,143,39,D.ink)}</>);
   during(2,3,text('같은 행동과 판단을 직접 확인',450,263,39,D.green));
   during(3,undefined,text('그렇다면, 낯선 조작은 모두 지워야 할까요?',0,309,40,D.title));
   break;
  }
  case 'unusual': {
   add(0,image('atomic-run.png',-455,-25,760,'Chelnov / Atomic Runner · 실제 플레이'));
   label('가상 입력 연결 비교',450,-237,1,D.title,44);
   const swapped=()=>reveal(2,0,.9)();
   add(1,<>
    <Rect x={200} y={-105} width={226} height={98} stroke={D.teal} lineWidth={5}/>{text('이동 입력',200,-105,39,D.teal)}
    <Rect x={200} y={95} width={226} height={98} stroke={D.green} lineWidth={5}/>{text('공격 입력',200,95,39,D.green)}
    <Rect x={710} y={-105} width={196} height={98} stroke={()=>reveal(2,.35,.9)()>.97?D.green:D.teal} lineWidth={5}/>{text('이동',710,-105,46)}
    <Rect x={710} y={95} width={196} height={98} stroke={()=>swapped()>.97?D.teal:D.green} lineWidth={5}/>{text('공격',710,95,46)}
    <Line points={[[335,-105],[590,-105]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(1,.1,.85)} opacity={()=>1-swapped()}/>
    <Line points={[[335,95],[590,95]]} stroke={D.green} lineWidth={8} endArrow arrowSize={20} end={reveal(1,.5,.85)} opacity={()=>1-swapped()}/>
   </>);
   add(2,<>
    <Line points={[[335,-105],[405,-105],[540,95],[590,95]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(2,0,.9)}/>
    <Line points={[[335,95],[405,95],[540,-105],[590,-105]]} stroke={D.green} lineWidth={8} endArrow arrowSize={20} end={reveal(2,.35,.9)}/>
   </>);
   during(1,3,text('실제 게임의 기본 조작이 아닙니다',450,225,35,D.muted));
   during(3,4,<>{text('설계 실수',235,234,42,D.red)}{text('의도한 도전',655,234,42,D.green)}</>);
   during(4,undefined,<>{text('익히는 재미',235,234,42,D.green)}{text('처음의 부담',655,234,42,D.red)}</>);
   note('가상 연결 비교 · 실제 버튼 입력을 측정한 화면이 아닙니다',1,D.muted,33);
   break;
  }
  case 'conclusion': {
   add(0,image('sf6-remap.png',-440,-40,790,'남길 익숙함',D.teal));
   add(2,image('atomic-run.png',440,-40,790,'배울 새로움',D.green));
   during(1,3,text('연결 · 화면 안내 · 필요한 입력 정보를 함께 확인',0,302,39,D.ink));
   during(3,undefined,text('처음인데 손에 익었던 게임, 무엇이었나요?',0,302,45,D.title));
   break;
  }
 }
 yield* t(duration,duration,linear);
}
