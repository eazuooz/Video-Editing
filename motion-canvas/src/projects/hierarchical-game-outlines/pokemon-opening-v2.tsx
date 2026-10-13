import {Node,Txt,Line} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './pokemon-opening-plan-v2.json';
const smooth=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x);};

// An authored planning illustration. No developer document, extracted reference
// slide, game screenshot, or unmeasured catch formula is represented here.
export function* referenceExplanation(view:any,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Timing mismatch');
 const t=createSignal(0),s=depthSpace(()=>5,[id==='01'?-100:-170,55],.83);
 const group=new Node({});view.fill(P.background);
 const text=(v:string,x:number,y:number,col=P.ink,size=31)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 if(id==='01'){
  view.add(heading('01','원하는 규칙을 바로 찾을 수 있나요?','포켓몬 초기작을 소재로 만든 설명용 메모','계층형 아웃라인'));
  group.add(s.box(0,20,0,1450,1260,24,'#edf1f3'));
  const labels=['지도에서 이동하기','몬스터볼을 쓸 수 있는 조건','전투에서 기술 고르기','포획 성공 뒤의 처리','이동할 지역 이름','포획 실패 뒤의 처리'];
  labels.forEach((v,i)=>{
   const y=-500+i*195,isBall=[1,3,5].includes(i),u=()=>smooth((t()-row.paragraphStarts[1]/60-i*.08)/.6);
   group.add(s.box(-30,y,27,1190,155,12,isBall?'#f4e4ce':'#ffffff'));
   group.add(s.label(v,-30,y,40,34,isBall?P.red:P.ink));
   if(isBall)group.add(<Node opacity={u}>{s.path(()=>[[620,y-70,45],[620,y+65,45]],P.red,1)}{s.label('관련 규칙',820,y,69,26,P.red)}</Node>);
  });
  view.add(group);
 }else if(id==='01a'){
  view.add(heading('01a','기획 메모를 같은 가지로 묶기','설명용 예시 · 실제 개발사의 원본 기획서가 아닙니다','계층형 아웃라인'));
  group.add(s.box(0,0,0,1350,1330,24,'#edf1f3'));
  const hierarchy=[
   ['게임 규칙',0,-570],['탐험',1,-395],['이동 · 지역',2,-220],['전투',1,-45],
   ['기술 선택',2,130],['아이템 사용',2,305],['몬스터볼',3,480]
  ];
  const reveal=()=>smooth((t()-row.paragraphStarts[1]/60)/1.1);
  const focus=()=>smooth((t()-row.paragraphStarts[2]/60)/1.2);
  hierarchy.forEach((r:any,i)=>{
   const x=()=>-455+r[1]*195*reveal(),y=r[2],active=i===0||i>=3;
   group.add(<Node opacity={()=>active?1:1-.62*focus()}>
    {s.box(x,y,28,440,140,11,i===0?'#e7ead2':i===6?'#f4e4ce':'#ffffff')}
    {s.label(r[0],x,y,40,34,i===6?P.red:P.ink)}
   </Node>);
  });
  // Indentation is the primary readable relationship; short child leaders are
  // explicitly illustrative, not a claim about internal game-code structure.
  view.add(group);
  const call=new Node({opacity:focus});view.add(call);
  call.add(text('몬스터볼 규칙',615,-30,P.red,35));
  call.add(text('사용 조건',615,55,P.ink,31));
  call.add(text('처리 결과',615,122,P.ink,31));
  call.add(text('함께 찾고 · 함께 수정',615,227,P.green,29));
  call.add(<Line points={[[465,260],[765,260]]} stroke={P.green} lineWidth={3}/>);
 }
 yield* t(frames/60,frames/60,linear);
}
