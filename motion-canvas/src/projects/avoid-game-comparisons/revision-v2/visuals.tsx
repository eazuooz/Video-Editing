import {Circle, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

export interface Timing {duration:number; cues?:number[]; title?:string;}
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const smooth=(v:number)=>{const x=clamp(v);return x*x*(3-2*x);};
const text=(s:string,x:number,y:number,size=48,color:string=D.ink)=><Txt text={s} x={x} y={y} fontSize={size} lineHeight={size*1.35} fill={color} fontWeight={600} fontFamily={D.font}/>;

/** Editorial concept diagrams. Arrows express relationships, never measured game data. */
export function* lesson(view:View2D,kind:string,timing:Timing){
 const t=createSignal(0),duration=timing.duration;
 const at=(i:number)=>timing.cues?.[i]??duration*[0,.18,.38,.58,.78][i];
 const appear=(i:number,delay=0)=>()=>smooth((t()-at(i)-delay)/.55);
 const show=(i:number,children:any,delay=0)=>view.add(<Node opacity={appear(i,delay)}>{children}</Node>);
 const arrow=(points:[number,number][],i:number,color:string=D.teal)=>view.add(<Line points={points} stroke={color} lineWidth={9} endArrow arrowSize={22} end={appear(i)}/>);
 const rule=(y:number)=>view.add(<Line points={[[-820,y],[820,y]]} stroke={D.line} lineWidth={2}/>);
 const label=(s:string,x:number,y:number,i:number,color:string=D.ink,size=48)=>show(i,text(s,x,y,size,color));
 const titles:Record<string,string>={overview:'“마리오 같은 게임”이면 통할까요?',familiar:'익숙한 이름이 불러오는 행동',pitch:'머릿속 게임을 함께 만들 게임으로',difference:'왜 이 게임을 선택해야 할까?',exception:'비교가 도움이 되는 범위',nes:'옆으로 이어진 길과 점프',odyssey:'조종 대상이 바뀌면, 행동도 바뀝니다',conditions:'방향을 빼면, 다른 규칙이 됩니다',rewrite:'이름을 지우고, 플레이를 남기기',retell:'상대의 말로 돌아온 행동을 확인하기',shared:'같은 부분과 다른 부분을 나누기',conclusion:'비교 뒤에도 게임의 매력이 남도록'};
 view.fill(D.background);
 view.add(<>{text('얌얌코딩  /  게임 설명법',-640,-475,29,D.muted)}{text(timing.title??titles[kind],0,-370,58,D.title)}</>);
 switch(kind){
  case 'overview':
   label('마리오 같은 게임',0,-190,0,D.ink,66);
   arrow([[-80,-120],[-470,10]],1);arrow([[80,-120],[470,10]],2);
   label('옆으로 이동 · 점프',-470,100,1,D.teal,48);label('공간 탐색 · 능력 활용',470,100,2,D.green,48);
   show(3,<>{text('같은 이름',-330,270,48,D.muted)}{text('같은 상상?',340,270,60,D.title)}</>);arrow([[-150,270],[120,270]],3,D.title);break;
  case 'familiar':
   label('“마리오”',0,-200,0,D.title,78);
   ['옆에서 보는 시점','발판 사이 점프','길 끝을 향해 진행'].forEach((s,i)=>{arrow([[0,-120],[(i-1)*570,20]],i+1);label(s,(i-1)*570,105,i+1,D.ink,45);});
   label('이름이 설명하는 것: 이미 알고 있는 경험',0,275,4,D.muted,43);break;
  case 'pitch':
   label('내 머릿속',-580,-190,0,D.teal,49);label('함께 만들 사람',580,-190,1,D.green,49);
   show(0,<Circle x={-580} y={-10} width={170} height={170} stroke={D.teal} lineWidth={6}/>);
   show(1,<Circle x={580} y={-10} width={170} height={170} stroke={D.green} lineWidth={6}/>);
   label('선명한 플레이',-580,145,0,D.ink,44);label('아직 보이지 않음',580,145,1,D.muted,44);
   arrow([[-465,-10],[-190,-10]],3);label('피치 (Pitch)',0,-10,3,D.title,48);arrow([[190,-10],[465,-10]],3,D.green);
   show(2,<>{text('무엇을 만들까',-410,285,46)}{text('왜 만들 가치가 있을까',390,285,46,D.title)}</>);break;
  case 'difference':
   label('“비슷하다”',-480,-155,0,D.muted,68);arrow([[-170,-155],[135,-155]],1,D.red);
   label('기존 게임을 하면 되지 않을까?',420,-155,1,D.red,42);
   rule(-50);label('이 게임에서만 할 행동',-450,65,2,D.teal,47);arrow([[-100,65],[115,65]],3,D.green);label('달라지는 경험',460,65,3,D.green,51);
   label('설명 연습 · 눈앞의 행동과 결과를 말로 옮기기',0,270,4,D.muted,38);break;
  case 'exception':
   label('공통 경험을 빠르게 불러오기',0,-190,0,D.teal,57);
   show(1,<>{text('후속작',-550,-20,54,D.title)}{text('이어지는 조작과 재미',290,-20,52)}</>);arrow([[-350,-20],[-100,-20]],1);
   rule(90);label('상대가 떠올린 연상',-450,175,2,D.ink,44);label('설명을 이름에 맡기기',450,175,3,D.red,44);
   label('비교를 빼고 나면, 어떤 매력이 남나요?',0,300,4,D.title,45);break;
  case 'nes':
   label('진행 방향',-640,-190,0,D.muted,42);
   view.add(<Line points={[[-790,100],[-390,100],[-390,20],[-130,20]]} stroke={D.teal} lineWidth={10}/>);
   view.add(<Line points={[[140,-60],[420,-60],[420,100],[790,100]]} stroke={D.teal} lineWidth={10}/>);
   arrow([[-650,45],[-450,-100],[-250,-35]],1,D.title);arrow([[-140,-35],[20,-210],[230,-110]],2,D.title);
   label('발판 높이',-350,220,1,D.ink,45);label('빈 공간',70,220,2,D.red,45);label('도착할 곳',570,220,3,D.green,45);
   label('실제 플레이에서 본 시점·목표의 관계도',0,315,4,D.muted,32);break;
  case 'odyssey':
   label('캐피로 캡처 (Capture)',0,-200,0,D.title,61);
   arrow([[-100,-130],[-480,-10]],1);arrow([[100,-130],[480,-10]],2);
   label('개구리',-480,55,1,D.teal,58);label('티라노사우루스',480,55,2,D.green,52);
   label('높은 점프',-480,165,1,D.ink,47);label('몸으로 돌 부수기',480,165,2,D.ink,47);
   label('어떤 대상을 쓸까? → 어떤 길이 열릴까?',0,305,3,D.title,46);break;
  case 'conditions': {
   label('같은 행동: 당겼다가 놓기',0,-210,0,D.ink,52);
   show(0,<><Circle x={-610} y={55} width={110} height={110} stroke={D.teal} lineWidth={7}/><Line points={[[-680,55],[-805,55]]} stroke={D.muted} lineWidth={6}/><Rect x={520} y={45} width={100} height={310} stroke={D.green} lineWidth={7}/>{text('부술 벽',520,255,44,D.green)}</>);
   arrow([[-530,55],[430,55]],1,D.green);label('벽을 향해',-40,120,1,D.green,48);
   arrow([[-530,20],[-260,-55],[300,-55]],2,D.red);label('방향을 정하지 않으면?',40,-120,2,D.red,40);
   show(3,<Rect x={520} y={45} width={130} height={340} stroke={D.title} lineWidth={3}/>);
   label('관찰한 결과: 벽에 충돌 → 벽 파괴 → 파워문',0,330,4,D.title,42);break;
  }
  case 'rewrite':
   ['목표','행동','조건 → 결과'].forEach((s,i)=>{label(String(i+1).padStart(2,'0'),-780,-170+i*165,i,D.muted,40);label(s,-550,-170+i*165,i,[D.title,D.teal,D.green][i],48);rule(-95+i*165);});
   label('벽 너머의 파워문 얻기',270,-170,0,D.ink,53);
   label('멍멍이를 당겼다가 놓기',270,-5,1,D.ink,53);
   label('벽을 향해 발사 → 접근 가능',270,160,2,D.ink,48);
   label('실제 기획에는 입력·실패 처리 등 필요한 규칙을 더합니다',0,330,4,D.muted,34);break;
  case 'retell':
   label('“이해했어요?”',-500,-210,0,D.muted,51);label('“처음 무엇을 하나요?”',400,-210,1,D.title,51);
   show(2,<>{text('돌아온 답',-690,-40,40,D.muted)}{text('점프해서 벽을 넘어요',130,-40,54,D.red)}<Line points={[[-260,-40],[630,-40]]} stroke={D.red} lineWidth={5} end={appear(3)}/></>);
   label('캡처 → 당겨서 발사 → 벽 파괴',100,140,3,D.green,54);
   label('가상 대화 · 빠진 행동을 찾아 다시 연결하기',0,310,4,D.muted,38);break;
  case 'shared':
   label('비교할 부분',-570,-190,0,D.muted,43);label('다르게 설계할 부분',450,-190,1,D.muted,43);
   label('옆에서 보는 시점',-500,-30,0,D.teal,53);label('목표와 완료 조건',470,-30,1,D.green,53);
   view.add(<Line points={[[0,-250],[0,200]]} stroke={D.line} lineWidth={3}/>);
   label('끝까지 달리기',370,100,2,D.muted,44);show(3,<Line points={[[100,100],[640,100]]} stroke={D.red} lineWidth={5}/>);
   label('흩어진 물건 모으기',470,205,3,D.green,49);
   label('가상 기획 예시 · 실제 마리오 규칙의 변경을 뜻하지 않습니다',0,330,4,D.muted,33);break;
  default:
   label('이름 없이도 설명할 수 있나요?',0,-190,0,D.title,60);
   ['목표','행동','조건과 결과','다시 말해 보기'].forEach((s,i)=>{const x=-660+i*440;label(s,x,20,i,D.ink,i===3?40:48);if(i<3)arrow([[x+(i===2?190:130),20],[x+(i===2?260:290),20]],i+1,D.teal);});
   label('비교는 설명을 돕고, 내 게임의 매력은 직접 말합니다',0,250,4,D.green,46);
 }
 yield* t(duration,duration,linear);
}
