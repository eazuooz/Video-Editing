import {Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, usePlayback} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const titles=['많은 보상보다 먼저 정할 것','기능부터 나누는 보상 목록','획득 조건은 한 줄씩 연결하기','강화의 끝과 허용할 조합','수치 밖의 보상도 목적이 필요하다','게임 속 비용과 제작 비용을 나누기','한 줄을 완성한 뒤 목록을 늘리기'];
const notes=['기능 → 조건과 제한 → 필요한 제작 작업','우리의 분류 제안 · 실제 게임의 전체 목록이 아닙니다','시점 · 선행 항목 · 재료 · 실제 사용을 따로 확인','장르와 목표에 맞추는 설계 질문 · 협동 시연을 대전으로 해석하지 않기','겉모양과 행동의 역할을 다른 칸에 기록','플레이어가 지불하는 재료와 개발자가 만드는 작업은 다른 항목','목록의 개수보다 설명할 수 있는 한 보상 행부터'];
const takeaways=['얼리는 탄약과 길을 만드는 탄약부터 실제 행동을 비교합니다.','이름만 늘리기 전에, 빠진 역할과 후보가 필요한 이유를 봅니다.','확인하지 못한 조건은 가정 대신 질문으로 남깁니다.','새 항목을 기존 항목과 함께 쓸 상황도 적어 둡니다.','꾸미기 · 기억 · 새 행동: 필요한 목적을 먼저 정합니다.','숫자로 비용을 단정하기 전에 작업과 담당자를 연결합니다.','한 보상 행을 실제 플레이와 제작 범위 양쪽에서 확인합니다.'];
function text(value:string,x:number,y:number,size=29,color:string=P.ink,weight=500){return <Txt text={value} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={weight} textAlign={'center'}/>;}
function card(x:number,y:number,w:number,h:number,title:string,detail='',color:string=P.blue){return <Node x={x} y={y}>
 <Rect x={11} y={12} width={w} height={h} rotation={-1} fill={'#dfe5e8'}/>
 <Rect width={w} height={h} rotation={-1} fill={'white'} stroke={color} lineWidth={2}/>
 <Rect x={-w/2+10} width={5} height={h-18} fill={color}/>
 {text(title,0,detail?-h*.18:0,30,color,700)}{detail?text(detail,0,h*.25,25,P.muted):null}
 </Node>;}
function arrow(points:[number,number][],color:string=P.blue){return <Line points={points} stroke={color} lineWidth={4} endArrow arrowSize={14}/>;}

// Each explanation has an independent entrypoint. Proportional timing is
// restricted to the explicitly silent lookdev project; finals require ASR ends.
export function* rewardConcept(view:View2D,index:number,duration:number,paragraphEnds?:number[]){
 const playback=usePlayback(),startFrame=playback.frame;
 function* until(seconds:number){const end=startFrame+Math.round(seconds*playback.fps);while(playback.frame<end)yield;}
 const count=index===0?4:3;
 const ends=paragraphEnds??Array.from({length:count},(_,i)=>duration*(i+1)/count);
 if(index<0||index>6||duration<7||ends.length!==count||ends.some((t,i)=>t<=(ends[i-1]??0))||Math.abs(ends[ends.length-1]-duration)>1/60)throw Error('Current independent paragraph timing required');
 const base=createRef<Node>(),second=createRef<Node>(),third=createRef<Node>(),summary=createRef<Node>();
 const moved=createRef<Node>(),mark=createRef<Rect>();
 view.fill(P.background);
 view.add(<>
  <Txt text={`보상 기획  ·  ${index+1} / 7`} x={-850} y={-469} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
  <Txt text={titles[index]} x={-850} y={-392} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>
  <Txt text={notes[index]} x={-850} y={-316} offset={[-1,0]} fontFamily={P.font} fontSize={26} fill={P.muted}/>
  <Node ref={base} opacity={0} y={18}/><Node ref={second} opacity={0}/><Node ref={third} opacity={0}/>
  <Node ref={summary} y={300} opacity={0}><Rect x={10} y={11} width={1650} height={74} fill={'#dae6df'}/><Rect width={1650} height={74} fill={'white'} stroke={P.green} lineWidth={2}/>{text(takeaways[index],0,0,28,P.ink,600)}</Node>
 </>);
 if(index===0){
  base().add(<>{card(0,-175,1320,102,'보상을 늘리기 전에 무엇을 정할까?')}{text('아이템 이름만 길어진 목록',0,-48,29,P.muted)}</>);
  second().add(<>{card(-540,80,430,105,'기능','바뀌는 행동')}{card(0,80,430,105,'조건 · 제한','획득과 조합')}{card(540,80,430,105,'작업','만들고 검수할 것')}{arrow([[-290,80],[-250,80]])}{arrow([[250,80],[290,80]])}</>);
  third().add(<>{card(0,212,1340,66,'시청 후: 한 보상 행에 기능 · 조건 · 작업을 함께 적기','',P.green)}</>);
 }else if(index===1){
  base().add(<>{card(-590,-80,370,250,'이름만 적은 목록','항목 A · B · C',P.muted)}{arrow([[-370,-80],[-300,-80]],P.line)}</>);
  second().add(<>{card(-100,-130,340,150,'더 강해지기','성장의 폭')}{card(295,-130,340,150,'새 선택 열기','가능한 행동')}{card(690,-130,300,150,'표현 · 모으기','목적 확인')}{text('이름 → 얻은 뒤 달라지는 역할',280,10,30,P.blue,700)}</>);
  third().add(<>{card(290,136,1100,108,'아직 없는 장식과 기념품','우리 기획 후보 · 필요한 이유부터 확인',P.green)}</>);
 }else if(index===2){
  base().add(<>{card(-570,-150,390,100,'언제 얻는가?','획득 시점')}{card(-100,-150,390,100,'무엇이 먼저인가?','선행 연구')}{arrow([[-362,-150],[-305,-150]],P.blue)}</>);
  second().add(<>{card(370,-150,390,100,'무엇을 만드는가?','필요 재료')}{card(370,55,390,100,'어떻게 쓰는가?','실제 사용')}{arrow([[125,-150],[145,-150]])}{arrow([[370,-92],[370,-5]])}{card(-380,65,740,110,'우회 경로와 재료 시점','앞 단계 없이 얻을 수 있는가?',P.green)}</>);
  third().add(<>{card(0,213,1380,65,'미확인 조건 → 우리 게임에서 결정할 질문','',P.red)}</>);
 }else if(index===3){
  base().add(<>{card(-440,-132,710,145,'성장이 중심','강해지는 폭을 계획')}{card(440,-132,710,145,'대등한 경쟁이 중심','누적 강화가 목표를 깨는가?',P.red)}</>);
  second().add(<>{card(-535,65,410,105,'상한','얼마나 늘리는가?')}{card(0,65,410,105,'동시 사용','함께 쓰는가?')}{card(535,65,410,105,'교체','무엇을 포기하는가?')}{arrow([[-440,-48],[-535,7]],P.blue)}{arrow([[440,-48],[535,7]],P.red)}</>);
  third().add(<>{text('새 보상 + 기존 항목 → 조합을 확인 → 수치 조정 / 선택의 교환',0,215,29,P.green,600)}</>);
 }else if(index===4){
  base().add(<>{card(-550,-150,430,110,'표현','개성을 드러낸다')}{card(0,-150,430,110,'기억','플레이를 남긴다')}{card(550,-150,430,110,'새 역할','생산 · 이동을 연다')}</>);
  second().add(<>{text('외형',-590,15,29,P.muted,700)}{card(-110,20,650,92,'의상 · 가면이 바뀐다')}{text('기능',-590,143,29,P.muted,700)}{card(-110,148,650,92,'생산 · 이동이 달라진다','',P.green)}<Node ref={moved} x={580} y={84}>{card(0,0,420,185,'따로 적기','외형 ≠ 같은 기능',P.green)}</Node></>);
  third().add(<Rect ref={mark} x={-110} y={84} width={684} height={236} stroke={P.green} lineWidth={4}/>);
 }else if(index===5){
  base().add(<>{card(-560,-117,520,225,'게임 안의 재료','플레이어가 지불하는 조건')}{arrow([[-260,-117],[-190,-117]],P.line)}{card(290,-157,1120,90,'개발 쪽의 작업','이미지 · 동작 · 검수 범위')}</>);
  second().add(<>{card(-30,15,305,94,'아이콘 · 그림')}{card(305,15,305,94,'동작 · 효과')}{card(640,15,305,94,'안내 · 검수')}{arrow([[290,-99],[290,-40]],P.blue)}</>);
  third().add(<>{card(260,166,1160,100,'기존 자료 / 새 작업을 나누기','작업과 담당자 · 빠진 조건부터 확인',P.green)}</>);
 }else{
  base().add(<>{text('보상 한 행',0,-222,31,P.blue,700)}{card(-620,-89,350,130,'기능','바뀌는 행동')}{card(-205,-89,350,130,'조건','언제 · 무엇이 먼저')}{card(210,-89,350,130,'제한','허용할 조합')}{card(625,-89,350,130,'작업','제작과 검수')}</>);
  second().add(<>{text('빈칸이 많으면 조건부터 · 같은 역할뿐이면 다른 목적도 검토',0,40,29,P.red,600)}<Rect x={-205} y={-89} width={374} height={154} stroke={P.red} lineWidth={4}/></>);
  third().add(<>{card(-450,181,620,106,'실제 플레이에서 확인','행동과 조건')}{card(450,181,620,106,'제작 범위에서 확인','필요한 작업',P.green)}{arrow([[0,76],[-450,76],[-450,119]],P.blue)}{arrow([[0,76],[450,76],[450,119]],P.green)}</>);
 }
 yield*all(base().opacity(1,.55),base().y(0,.55,easeInOutCubic));
 yield*until(ends[0]);
 yield*all(second().opacity(1,.6),second().y(-5,.6,easeInOutCubic));
 yield*until(ends[1]);
 if(index===4)yield*all(moved().x(590,.55,easeInOutCubic),third().opacity(1,.55));
 else yield*all(third().opacity(1,.55),third().y(-4,.55,easeInOutCubic));
 if(index===0)yield*until(ends[2]);
 yield*summary().opacity(1,.45);
 yield*until(duration);
}
