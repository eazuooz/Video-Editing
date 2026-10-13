import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './reference-reel-plan-v1.json';
const smooth=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x);};
const titles:any={
 '01':['생각을 찾을 수 있는 구조','큰 묶음 → 필요한 가지 → 읽는 사람의 문서'],
 '02':['큰 항목 아래에 작은 항목','계층은 중요도 순위가 아니라 포함 관계입니다'],
 '03':['같은 층과 한 단계 아래','설정 → 소리 → 음악 · 효과음 · 목소리'],
 '04':['캐릭터에서 기술의 세부로','캐릭터 → 필살기 → 기술 → 입력 · 동작 · 결과'],
 '05':['접기 · 순서 이동 · 단계 변경','보이는 범위, 읽는 순서, 소속은 서로 다른 작업입니다'],
 '06':['워드에서 아웃라인 시작하기','데스크톱 Word: 보기 → 개요 · 아래는 설명용 도식입니다'],
 '07':['작업 메모에서 전달 문서로','같은 내용도 읽는 사람에 맞춰 표현을 다듬습니다'],
 '08':['작은 목록 하나부터','제목만 읽고도 원하는 설명을 찾아갈 수 있나요?']};
const notes:any={
 '01':['흩어진 메모를 묶습니다','필요한 부분만 펼칩니다','읽는 사람의 순서로 정리합니다'],
 '02':['부모: 묶음의 범위','자식: 그 안의 세부 항목','같은 질문에 답하는 항목끼리 나란히'],
 '03':['들여쓰기가 포함 관계를 보여 줍니다','소리와 밝기는 같은 층','효과음은 소리의 세부 항목'],
 '04':['설명용 문서 · 실제 개발사 기획서가 아닙니다','같은 기술의 입력 · 동작 · 결과','이름만 바꾸지 말고 설명의 소속을 확인'],
 '05':['접어도 내용은 남습니다','제목과 자식이 함께 이동합니다','단계 변경은 부모를 바꾸는 일입니다'],
 '06':['글자 크기와 문서 단계는 다릅니다','큰 제목과 작은 제목에 단계 지정','표시 단계로 전체와 세부를 오갑니다'],
 '07':['질문이 남아 있는 작업 메모','결정된 내용을 읽는 순서로 연결','다른 사람에게 필요한 설명을 분명하게'],
 '08':['큰 제목과 관련 항목을 묶기','한 가지를 펼쳤다가 다시 접기','찾을 수 있고 고칠 수 있는 구조']};
export function* referenceExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Current timing mismatch');
 const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=1.4)=>smooth((t()-(starts[p]||0))/d);
 const phase=()=>{let p=0;starts.forEach((s,i)=>{if(t()>=s)p=i;});return p;};
 const s=depthSpace(()=>17+5*u(1),[0,90],.67),g=new Node({});view.fill(P.background);view.add(heading(id,titles[id][0],titles[id][1],'계층형 아웃라인'));view.add(g);
 const txt=(v:string,x:number,y:number,col=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const sheet=(name:string,x:number|(()=>number),y:number|(()=>number),z:number|(()=>number),col='#dce6f0',w=320)=><Node>{s.box(x,y,z,w,145,25,col)}{s.label(name,x,y,()=> (typeof z==='function'?z():z)+83,29)}</Node>;
 const edge=(a:V3,b:V3,col=P.blue,progress:number|(()=>number)=1)=>s.path(()=>[a,b],col,progress);
 g.add(s.box(0,40,0,1650,780,22,'#eef1f3'));
 if(id==='01'||id==='02'||id==='08'){
  const names=id==='02'?['소리','리플레이','기록']:id==='08'?['영상 주제','시청자 질문','세부 설명']:['메뉴의 묶음','글의 단계','전달할 문서'];
  g.add(sheet(id==='02'?'보관함':id==='08'?'채널 기획':'생각의 아웃라인',0,-290,180,'#dce8d8',480));
  names.forEach((name,i)=>{let x=[-550,0,550][i];g.add(<Node opacity={()=>smooth(t()/.9-i*.35)}>{edge([0,-240,170],[x,-20,90])}{sheet(name,x,-20,90,'#dce6f0',360)}</Node>);});
  const opened=()=>id==='08'?u(1)*(1-u(2)):u(1);
  if(id!=='02')g.add(<Node opacity={opened}>{edge([0,40,90],[0,290,25],P.green)}{sheet(id==='08'?'예시 · 설명 · 결과':'필요한 세부 내용',0,290,25,'#e5eadb',430)}</Node>);
 }else if(id==='03'){
  g.add(sheet('설정',-520,-240,150,'#dce8d8',330));
  ['소리','밝기','언어'].forEach((v,i)=>{let y=-240+i*225;g.add(edge([-330,-200,130],[-70,y,90]));g.add(sheet(v,60,y,90,'#dce6f0',260));});
  ['음악','효과음','목소리'].forEach((v,i)=>{let y=-210+i*230;g.add(<Node opacity={()=>u(1)}>{edge([190,-200,100],[580,y,25],i===1?P.red:P.green)}{sheet(v,640,y,25,i===1?'#f0ddd4':'#e5eadb',260)}</Node>);});
 }else if(id==='04'){
  [['캐릭터',-650,-220,180],['필살기',-170,-80,110],['개별 기술',310,40,70]].forEach((r:any,i)=>{g.add(sheet(r[0],r[1],r[2],r[3],i===0?'#dce8d8':'#dce6f0',330));if(i<2)g.add(edge([r[1]+160,r[2],r[3]],[r[1]+470,r[2]+140,r[3]-60]));});
  ['입력 방법','동작','결과'].forEach((v,i)=>g.add(<Node opacity={()=>u(1)}>{sheet(v,-420+i*470,320,25,['#e5eadb','#ebe1d6','#dce6f0'][i],340)}</Node>));
 }else if(id==='05'){
  const measured=row as typeof row & {foldAt?:number;expandAt?:number;moveAt?:number;levelAt?:number};
  const fold=()=>smooth((t()-(measured.foldAt??.2))/.6)*(1-smooth((t()-(measured.expandAt??Math.max(1.8,(starts[1]||3)-1.2)))/.7));
  const move=()=>smooth((t()-(measured.moveAt??starts[1]))/1.4),level=()=>smooth((t()-(measured.levelAt??starts[2]))/1.4);
  const x=()=>-430+760*move(),y=()=>-90+90*level();
  g.add(sheet('캐릭터',-550,-290,200,'#dce8d8',410));g.add(sheet('공통 규칙',520,-290,200,'#ebe1d6',410));g.add(sheet('필살기',x,y,105,'#dce6f0',330));
  g.add(<Node opacity={()=>1-level()}>{s.path(()=>[[-370,-240,180],[x()+210,y()-30,115]],P.blue)}</Node>);
  g.add(<Node opacity={()=>1-fold()}>{sheet('기술 A · 입력',x,()=>y()+200,45,'#e5eadb',360)}{sheet('기술 A · 결과',x,()=>y()+360,25,'#ebe1d6',360)}{s.path(()=>[[x()+220,y()+40,90],[x()+220,y()+160,40]],P.green)}</Node>);
  g.add(<Node opacity={()=>fold()}>{s.box(x,()=>y()+20,65,330,145,15,'#d7e1e8')}{txt('내용 보존',100,280,P.green,31)}</Node>);
  g.add(<Node opacity={()=>level()}>{s.path(()=>[[520,-240,180],[x()+220,y()-30,95]],P.red)}{txt('새 부모 아래의 뜻을 확인',0,315,P.red,30)}</Node>);
 }else if(id==='06'){
  g.add(sheet('보기',-540,-240,170,'#dce8d8'));g.add(edge([-350,-210,150],[0,-170,110]));g.add(sheet('개요',0,-170,110,'#dce6f0'));g.add(edge([180,-140,100],[550,-90,60]));g.add(sheet('단계 지정',550,-90,60,'#e5eadb'));
  ['1  캐릭터','2    필살기','3      개별 기술'].forEach((v,i)=>g.add(<Node opacity={()=>u(1)*(1-(i>0?u(2):0)*.7)}>{sheet(v,-220+i*140,80+i*170,45-i*10,'#e8edf1',560)}</Node>));
 }else if(id==='07'){
  g.add(sheet('작업 메모',-510,-250,180,'#ebe1d6',450));g.add(sheet('전달 문서',520,-250,180,'#dce8d8',450));
  ['입력은?','어떤 동작?','결과는?'].forEach((v,i)=>g.add(sheet(v,-550,10+i*180,85-i*25,'#f0ddd4',340)));
  ['입력 방법','동작 설명','관찰할 결과'].forEach((v,i)=>g.add(<Node opacity={()=>u(1)}>{sheet(v,520,10+i*180,85-i*25,'#dce6f0',370)}</Node>));
  g.add(s.path(()=>[[-300,20,100],[280,20,100]],P.green,()=>u(1)));
 }
 view.add(<Txt text={()=>notes[id][Math.min(2,phase())]} x={350} y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={25}/>);
 yield* t(frames/60,frames/60,linear);
}
