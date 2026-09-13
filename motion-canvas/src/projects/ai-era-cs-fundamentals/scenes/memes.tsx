import {Circle,Line,Node,Rect,Txt} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import references from '../../../../../projects/ai-era-cs-fundamentals/sources/meme-references.json';

const text=(s:string|(()=>string),x=0,y=0,size=42,color:string=P.ink)=><Txt text={s} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} />;
function person(x:number,y:number,question=false) {
  return <Node x={x} y={y}>
    <Circle y={-90} size={110} stroke={P.ink} lineWidth={5} fill={P.background} />
    <Circle x={-18} y={-94} size={7} fill={P.ink} /><Circle x={18} y={-94} size={7} fill={P.ink} />
    <Line points={[[-15,-65],[15,-65]]} stroke={P.ink} lineWidth={4} />
    <Line points={[[0,-35],[0,110],[-65,200],[0,110],[65,200]]} stroke={P.ink} lineWidth={6} />
    <Line points={[[-105,55],[0,0],[105,55]]} stroke={P.ink} lineWidth={6} />
    {question&&text('?',125,-130,65,P.blue)}
  </Node>;
}
// Overlay lives within the explanation time; it never shifts narration or SRT.
export function* memeAside(parent:Node,index:number,duration:number) {
  const p=createSignal(0),m=references.memes[index];
  const root=new Rect({width:1920,height:1080,fill:P.background});parent.add(root);
  root.add(<>
    <Txt text={`${m.scene} · 잠깐, 이 상황`} x={-864} y={-470} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted} />
    <Txt text={m.caption} x={-864} y={-390} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={600} fill={P.ink} />
    <Rect y={425} width={1728} height={86} fill={P.panel} stroke={P.ink} lineWidth={1.5}>
      {text('익숙한 난처함을 잠깐 웃고, 해결할 조건으로 돌아갑니다.',0,0,30)}
    </Rect>
  </>);
  const art=new Node({y:5,scale:()=>1+Math.min(1,p()*8)*.02});root.add(art);
  switch(m.visual) {
    case 'news':
      art.add(person(-420,15,true));
      ['안 쓰면 뒤처진다','쓰면 실력이 안 는다','그래서 켜요, 꺼요?'].forEach((s,i)=>art.add(<Rect x={370} y={-170+i*170} width={670} height={125} fill={i===2?P.blueLight:P.panel}>{text(s,0,0,40)}</Rect>));break;
    case 'chart':
      art.add(<><Line points={[[-590,-200],[-590,225],[650,225]]} stroke={P.ink} lineWidth={3} />
        <Line points={[[-500,-140],[-200,-40],[100,30],[570,180]]} stroke={P.blue} lineWidth={11} endArrow end={()=>Math.min(1,p()*2)} />
        {text('일정',-680,-200,32)}{text('30일 → 15일',100,-170,67)}{text('검증한 코드: 0줄',150,315,36,P.muted)}</>);break;
    case 'loop':
      ['에러 A','수정','에러 B'].forEach((s,i)=>art.add(<Node x={(i-1)*540}><Rect width={390} height={160} fill={i===1?P.panel:P.blueLight} />{text(s,0,0,54)}{i<2&&text('→',270,0,70)}</Node>));
      art.add(<>{text('↶',0,220,150,P.blue)}{text('처음 뵙겠습니다. 또 뵙네요.',0,-195,39,P.muted)}</>);break;
    case 'math':
      art.add(person(0,20,true));['O(n log n)','TCP / UDP','SELECT …','stack? queue?','0(n)? O(n)?'].forEach((s,i)=>art.add(text(s,[-520,470,-500,500,0][i],[-170,-175,120,120,285][i],38,i%2?P.muted:P.blue)));break;
    case 'servers':
      art.add(<>{text('memo.txt',-600,0,56)}{text('→',-350,0,75)}</>);
      for(let i=0;i<6;i++)art.add(<Rect x={-70+(i%3)*270} y={-110+Math.floor(i/3)*200} width={215} height={145} fill={P.panel} stroke={P.line} lineWidth={2} opacity={()=>p()>i*.08?1:0}>{text(`서버 ${i+1}`,0,0,33)}</Rect>);break;
    case 'loading':
      art.add(person(-525,40,true));art.add(<Rect x={240} width={900} height={370} fill={P.panel} stroke={P.line} lineWidth={2}>{text('def solve():',0,-100,50)}{text(()=>p()%0.35<.2?'|':'',-180,20,80,P.blue)}{text('생각 불러오는 중…',0,115,35,P.muted)}</Rect>);break;
    case 'blocks':
      for(let i=0;i<21;i++)art.add(<Rect x={-430+(i%7)*100} y={190-Math.floor(i/7)*100} size={94} fill={i%3?P.blueLight:P.blue} opacity={()=>p()>.025*i?1:0} />);
      art.add(<>{text('충돌  ·  회전  ·  고정  ·  줄 삭제',0,-220,47)}{text('쉬워 보였던 일의 실제 목록',0,315,35,P.muted)}</>);break;
    case 'button':
      art.add(person(-480,20,true));art.add(<><Rect x={290} width={620} height={260} fill={P.panel} stroke={P.line} lineWidth={2} />
        <Circle x={290} size={()=>165+Math.sin(p()*30)*5} fill={P.blueLight} stroke={P.red} lineWidth={5}/>{text('회전',290,0,54)}{text('벽 옆에서  ×  100',290,230,41,P.red)}</>);break;
    case 'wallet':
      art.add(<><Rect x={-430} width={420} height={250} fill={P.panel} stroke={P.ink} lineWidth={4}>{text('내 지갑',0,0,53)}</Rect>{text('API / 구독료',450,-200,43)}{text('첫 월급: 아직',-430,230,37,P.muted)}</>);
      for(let i=0;i<4;i++)art.add(<Circle x={()=>-80+((p()+i*.2)%1)*740} y={i%2?35:-35} size={75} fill={P.yellow} stroke={P.ink} lineWidth={1}>{text('₩',0,0,36)}</Circle>);break;
    case 'boulder':
      art.add(<><Line points={[[-700,240],[630,-230]]} stroke={P.ink} lineWidth={5} />
        <Circle x={()=>-230+Math.sin(p()*Math.PI)*400} y={()=>-38-Math.sin(p()*Math.PI)*140} size={190} fill={P.panel} stroke={P.blue} lineWidth={5}>{text('99%',0,0,51)}</Circle>
        {text('오늘도 거의 다 됐습니다',230,285,42,P.muted)}</>);break;
    case 'pointing':
      art.add(<>{person(-420,20,true)}{person(420,20,true)}{text('선배',-420,-230,40)}{text('취준생',420,-230,40)}{text('↔',0,30,100,P.blue)}{text('고생 자랑 말고, 작은 기능부터',0,310,42)}</>);break;
    default:
      art.add(<><Circle size={230} fill={P.blueLight} stroke={P.blue} lineWidth={5}>{text('✓',0,0,130,P.blue)}</Circle>{text('작은 기능 하나 완료',0,220,51)}{text('+1',370,-140,90,P.blue)}</>);
  }
  yield* tween(duration,v=>{p(v);root.opacity(v>.88?(1-v)/.12:1);});root.remove();
}
