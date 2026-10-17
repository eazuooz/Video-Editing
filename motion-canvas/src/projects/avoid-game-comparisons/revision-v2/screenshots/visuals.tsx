import {Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../../styles/research-dark';

const base='/@fs/D:/Github/VideoEditing/projects/avoid-game-comparisons/production/local/reference-preserving-v2/screenshots-v1/assets/';
const smooth=(n:number)=>{const v=Math.max(0,Math.min(1,n));return v*v*(3-2*v);};
const txt=(s:string,x:number,y:number,size=46,color:string=D.ink)=><Txt text={s} x={x} y={y} fontSize={size} lineHeight={size*1.3} fontWeight={600} fontFamily={D.font} fill={color}/>;
type Timing={duration:number;cues:number[]};

/** Actual recorded frames support independently authored explanations, not measured game telemetry. */
export function* screenshots(view:View2D,kind:string,timing:Timing){
 const t=createSignal(0),reveal=(time:number)=>()=>smooth((t()-time)/.55);
 const at=(n:number)=>timing.cues[n]??0;
 const title:Record<string,string>={pitch:'머릿속 게임을 함께 만들 게임으로',conditions:'방향을 빼면, 다른 규칙이 됩니다',rewrite:'이름을 지우고, 플레이를 남기기',retell:'상대의 말로 돌아온 행동을 확인하기',shared:'같은 부분과 다른 부분을 나누기',conclusion:'비교 뒤에도 게임의 매력이 남도록'};
 const add=(children:any,time=0)=>view.add(<Node opacity={reveal(time)}>{children}</Node>);
 const arrow=(a:[number,number],b:[number,number],time:number,color:string=D.teal)=>view.add(<Line points={[a,b]} stroke={color} lineWidth={9} endArrow arrowSize={21} end={reveal(time)}/>);
 const shot=(id:string,x:number,y:number,w:number,time=0)=>add(<><Img src={base+id+'.png'} x={x} y={y} width={w} height={w*9/16}/><Rect x={x} y={y} width={w} height={w*9/16} stroke={D.line} lineWidth={2}/></>,time);
 // Source-space coordinates are from directly inspected full-resolution stills.
 const box=(x:number,y:number,w:number,rect:[number,number,number,number],time:number,color:string=D.title)=>{
  const [sx,sy,sw,sh]=rect,k=w/1920;
  add(<Rect x={x+(sx+sw/2-960)*k} y={y+(sy+sh/2-540)*k} width={sw*k} height={sh*k} stroke={color} lineWidth={7}/>,time);
 };
 const credit=(nes=false)=>view.add(txt(nes?'기록: Gameplay Project · CC BY  |  게임: Nintendo':'기록: LongplayArchive / Spazbo4  |  게임: Nintendo',510,-475,24,D.muted));
 view.fill(D.background);
 view.add(<>{txt('얌얌코딩  /  게임 설명법',-640,-475,29,D.muted)}{txt(title[kind],0,-380,58,D.title)}</>);
 switch(kind){
  case 'pitch':
   shot('capture',-450,-20,820);
   add(txt('구체적인 플레이를 떠올려 보기',-450,-290,40,D.teal));
   add(txt('플레이 장면을 말로 옮기는 예시',-450,255,33,D.muted));
   add(<>{txt('무엇을 만들까',470,-200,53,D.ink)}{txt('플레이어가 하는 행동',470,-125,40,D.muted)}</>,at(1));
   add(<>{txt('왜 함께 만들까',470,35,53,D.title)}{txt('이 게임을 선택할 이유',470,110,40,D.muted)}</>,at(2));
   arrow([-10,-20],[70,-20],at(3));
   add(txt('피치 (Pitch)  ·  핵심 매력과 방향',450,275,40,D.green),at(3));
   credit();break;
  case 'conditions':
   shot('pull',-450,-45,800);shot('moon',450,-45,800,at(3));
   add(txt('행동: 당겼다가 놓기',-450,-300,44,D.teal));
   box(-450,-45,800,[780,410,355,410],at(1),D.teal);
   box(-450,-45,800,[805,2,300,330],at(1),D.green);
   arrow([-450,-72],[-450,-190],at(1),D.green);
   add(txt('조건: 부술 벽을 향해',-450,220,42,D.green),at(1));
   add(txt('방향을 빼면 다른 설명',0,295,43,D.red),at(2));
   add(txt('결과: 벽 파괴 → 파워문',450,-300,43,D.title),at(3));
   arrow([-30,-45],[30,-45],at(3),D.title);
   box(450,-45,800,[860,270,200,260],at(3),D.title);
   add(txt('실제 장면에서 확인한 결과',450,220,38,D.muted),at(3));
   credit();break;
  case 'rewrite': {
   const imageX=-460,imageY=-30,w=850;
   view.add(<Node opacity={()=>1-reveal(at(1))()}><Img src={base+'moon.png'} x={imageX} y={imageY} width={w}/></Node>);
   view.add(<Node opacity={()=>reveal(at(1))()*(1-reveal(at(2))())}><Img src={base+'pull.png'} x={imageX} y={imageY} width={w}/></Node>);
   view.add(<Node opacity={reveal(at(2))}><Img src={base+'break.png'} x={imageX} y={imageY} width={w}/></Node>);
   view.add(<Rect x={imageX} y={imageY} width={w} height={w*9/16} stroke={D.line} lineWidth={2}/>);
   const rows=[['01  목표','벽 너머의 파워문 얻기',D.title],['02  행동','멍멍이를 당겼다가 놓기',D.teal],['03  조건과 결과','벽을 향해 발사 → 벽 파괴',D.green]];
   rows.forEach(([a,b,color],i)=>{
    const y=-225+i*185;
    view.add(<Node opacity={()=>.28+.72*reveal(at(i))()}>{txt(a,460,y,46,color)}{txt(b,460,y+70,44)}<Line points={[[65,y+117],[850,y+117]]} stroke={D.line} lineWidth={2}/></Node>);
    add(<Line points={[[30,y+25],[65,y+25]]} stroke={color} lineWidth={9}/>,at(i));
   });
   add(txt('목표 → 행동 → 조건에 따른 결과',-460,265,39,D.title),at(0));
   add(txt('기획에는 조작 입력·실패 처리도 덧붙입니다',450,300,33,D.muted),at(4));
   credit();break;
  }
  case 'retell':
   add(txt('“처음 무엇을 하고, 다음에 무엇이 바뀌나요?”',0,-290,46,D.title),at(1));
   shot('capture',-450,-35,790);shot('break',450,-35,790);
   add(<>{txt('조종 대상이 바뀜',-450,215,43,D.teal)}{txt('벽이 무너짐',450,215,43,D.green)}</>,at(3));
   arrow([-30,-35],[30,-35],at(3),D.green);
   add(txt('“점프해서 벽을 넘어요”',0,275,43,D.red),at(2));
   view.add(<Line points={[[-260,275],[260,275]]} stroke={D.red} lineWidth={5} end={reveal(at(3))}/>);
   view.add(txt('가상 대화 · 이해도를 측정한 결과가 아닙니다',0,330,27,D.muted));credit();break;
  case 'shared':
   shot('side-jump',-470,-25,830);add(txt('참고할 범위: 옆에서 보는 시점',-470,-295,41,D.teal));
   box(-470,-25,830,[860,280,120,160],at(0),D.teal);
   add(txt('다르게 설계할 목표',460,-210,48,D.green),at(1));
   add(txt('끝까지 달리기',460,-80,49,D.muted),at(2));
   view.add(<Line points={[[270,-80],[650,-80]]} stroke={D.red} lineWidth={5} end={reveal(at(3))}/>);
   arrow([460,-30],[460,45],at(3),D.green);
   add(txt('흩어진 물건 모으기',460,110,49,D.green),at(3));
   add(txt('가상의 새 게임 기획',460,205,36,D.title),at(3));
   add(txt('실제 마리오의 규칙을 바꿨다는 뜻은 아닙니다',0,295,37,D.muted),at(4));
   credit(true);break;
  default:
   ['moon','pull','break'].forEach((id,i)=>{
    const x=-570+i*570;shot(id,x,-70,530);
    add(txt(['목표','행동','조건과 결과'][i],x,-280,48,[D.title,D.teal,D.green][i]));
    add(txt(['파워문 얻기','당겼다가 놓기','벽을 향해 → 벽 파괴'][i],x,130,i===2?35:39));
   });
   arrow([-292,-70],[-265,-70],at(1));arrow([278,-70],[305,-70],at(2));
   add(txt('상대의 말로 같은 플레이가 돌아오나요?',0,245,48,D.title),at(2));
   add(txt('비교는 돕고, 게임의 매력은 직접 말하기',0,305,38,D.green),at(4));
   credit();
 }
 yield* t(timing.duration,timing.duration,linear);
}
