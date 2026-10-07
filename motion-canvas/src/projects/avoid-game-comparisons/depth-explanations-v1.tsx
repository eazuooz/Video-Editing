import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={
 '01':['작품 이름만으로 같은 장면이 떠오를까요?','목표 · 행동과 조건 · 다음 행동과의 연결'],
 '03':['같은 이름, 다른 머릿속 장면','가상의 두 청자 · 실제 이용자 조사 결과가 아닙니다'],
 '05':['어디서 → 무엇을 → 어떤 변화까지','공간과 동사를 직접 써서 핵심 행동을 전달합니다'],
 '06-2':['움직임에 공간의 조건을 붙이기','기울어진 길 · 얼음 면 · 주변 지지대'],
 '06-4':['내려가기와 올라가기를 따로 설명','보인 움직임과 아직 확인할 규칙을 구분합니다'],
 '07':['관찰한 사실과 결정할 질문','미정인 규칙을 참고 작품이 대신 약속하게 두지 않습니다'],
 '13-3':['누가 움직이고, 무엇이 달라지는가','캐릭터 이동과 책의 기울기는 다른 변화'],
 '09':['기획을 세 문장으로 설명하기','목표 → 행동과 조건 → 다음 행동과의 연결'],
 '10-2':['편집된 두 컷은 한 번의 추격이 아닙니다','평평한 물 위 이동과 파도 위 이동을 구분'],
 '10-4':['도움 기능의 소개는 별도 조건입니다','기본 난이도나 모든 표시 규칙으로 옮기지 않습니다'],
 '11':['되말하기로 빠진 조건 찾기','작품명 맞히기보다 전달된 행동을 확인합니다'],
 '14-0':['진입 · 전투 · 결과를 따로 말하기','앞선 열쇠 이동만으로 모든 결과를 약속할 수 없습니다'],
 '15-3':['움직임에 공간과 대상을 더하기','물가·용암 위 이동과 적을 향한 발사는 다릅니다'],
 '12-2':['핵심 행동과 조건은 직접 설명하기','기억하는 작품 이름이 전달을 대신하지 않습니다']};
const notes:any={
 '01':['익숙한 작품명에 서로 다른 기억을 채울 수 있습니다','이동의 동사 → 공간과 조건 → 듣는 사람의 질문','목표 · 행동 · 조건을 세 문장에','먼저 노란 지형을 파고 나오는 움직임부터'],
 '03':['상대가 기억한 부분으로 빈칸을 채울 수 있습니다','장애물을 넘는 이동 / 적과의 전투','가상의 설명 연습입니다','비교한다면 어떤 부분인지 이어서 말하기'],
 '05':['공간 · 동사 · 눈에 보이는 변화','추상적인 평가 옆에 구체적인 행동 문장','작품명은 배경 · 핵심 행동은 직접 설명'],
 '07':['진입 표시와 다시 실행할 때의 조건','비용·제한 시간은 우리 기획의 질문','미정인 규칙을 확정된 것처럼 말하지 않기','확인한 조건은 설명 · 미정은 질문으로'],
 '09':['첫 문장: 플레이어가 이루려는 목표','세 번째: 다음 행동과의 연결','예: 다음 발판 → 지형 안 이동 → 지형 밖 공중 이동','개발사의 기획서가 아닌 우리 설명 연습'],
 '11':['처음 무엇을 할지 자기 말로 이야기하기','아무 벽이라면 진입 지점 조건이 빠졌는지','목표와 동작 · 미정 조건을 확인하고 보완']};
export function* depthExplanation(view:View2D,inputId:string,frames:number){
 const row=plan.rows.find(r=>r.id===inputId);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');const id=inputId.replace('-original-white-explanation','').replace('-white-comparison','');
 const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d),move=()=>smooth(t()/Math.min(4,frames/60));
 const phase=()=>{let p=0;starts.forEach((v,i)=>{if(t()>=v)p=i;});return p;};const s=depthSpace(()=>20+7*move(),[0,90],.76),g=new Node({});view.fill(P.background);view.add(heading(id,titles[id][0],titles[id][1],'게임 기획 설명'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const island=(x:number,col='#e2eadb')=>s.box(x,0,0,430,370,45,col);
 const portal=(x:number,y:number)=> <Node>{s.box(x,y,45,140,35,220,'#d1dfca')}{s.box(x,y-22,65,90,20,160,'#eff4ec')}{s.path(()=>[[x-80,y,45],[x+80,y,45]],P.green)}</Node>;
 if(id==='01'||id==='09'){
  [-570,0,570].forEach((x,i)=>{g.add(island(x));g.add(text(['목표','행동 · 조건','다음 행동'][i],x,-165,P.ink,32));if(i<2)g.add(s.path(()=>[[x+245,0,80],[x+325,0,80]],P.blue,()=>u(i+1)));});g.add(s.flag(-570,0));g.add(s.actor(()=>-80+160*move(),0,P.blue));g.add(s.box(570,0,45,180,160,80,'#d3dfe9'));g.add(text(id==='01'?'동사로 풀기 → 조건 구분 → 빠진 질문 찾기':'도달하기 → 파고 이동하기 → 밖으로 나와 이어가기',0,315,P.blue,30));
 }else if(id==='03'){
  g.add(island(-450));g.add(island(460));g.add(s.actor(-620,60,P.blue));g.add(s.actor(650,60,P.green));g.add(s.box(-330,0,45,140,140,100,'#e0cbb7'));g.add(s.path(()=>[[-620,0,75],[-450,-80,150],[-220,0,75]],P.blue,()=>u(1)));g.add(s.box(330,0,45,100,100,110,'#d5b5a8'));g.add(s.path(()=>[[590,0,120],[380,0,120]],P.red,()=>u(1)));g.add(<Node>{text('장애물을 넘는 이동',-450,-165,P.blue,32)}{text('적을 상대하는 전투',460,-165,P.red,32)}{text('가상의 청자 · 설명 연습',0,315,P.muted,29)}</Node>);
 }else if(id==='05'){
  g.add(s.box(-440,0,0,650,470,45,'#e5ddd2'));g.add(s.box(480,0,0,500,390,45,'#dce6f0'));g.add(portal(-210,-60));g.add(s.actor(()=>-630+410*move(),80,P.blue));g.add(s.path(()=>[[-180,-50,75],[240,-50,75]],P.green,()=>u(1)));g.add(s.actor(480,0,P.green,'●',45));g.add(<Node>{text('책상',-450,-165,P.ink,33)}{text('진입 지점 → 인쇄면 안',420,-165,P.green,32)}{text('어디서 · 다가가서 · 안으로 들어간다',0,315,P.blue,31)}</Node>);
 }else if(id==='06-2'){
  g.add(s.box(0,0,0,1400,430,45,'#e4e9ef'));g.add(s.polygon(()=>[[-650,-100,45],[650,-100,135],[650,100,135],[-650,100,45]],'#d3e4ef'));g.add(s.actor(()=>-550+700*move(),0,P.blue,'●',()=>60+50*move()));for(const x of [-650,650])g.add(s.box(x,-130,0,50,50,170,'#c3a582'));g.add(text('기울기와 얼음 면이라는 공간의 조건',0,315,P.blue,32));
 }else if(id==='06-4'){
  g.add(s.box(0,0,0,600,500,35,'#e6ded3'));g.add(s.box(0,0,35,400,320,140,'#e4edf3'));g.add(s.box(0,0,175,420,340,22,'#f1f6fa'));g.add(s.actor(0,-50,P.blue,'●',()=>210-120*Math.sin(Math.PI*move())));g.add(s.path(()=>[[-300,0,240],[-300,0,80]],P.blue,move));g.add(s.path(()=>[[310,0,80],[310,0,240]],P.green,move));g.add(<Node>{text('하강',-460,50,P.blue,33)}{text('상승',450,50,P.green,33)}{text('비행 제한·연료 규칙은 이 관찰만으로 확정하지 않습니다',0,315,P.muted,28)}</Node>);
 }else if(id==='07'||id==='10-4'){
  g.add(island(-450,'#dce6f0'));g.add(island(460,'#f0e3d6'));g.add(portal(-450,0));g.add(s.box(460,0,45,160,160,120,'#ece5dc'));g.add(s.label('?',460,0,210,55,P.red));g.add(<Node>{text(id==='07'?'시연에서 보인 사실':'도움 기능 소개',-450,-165,P.blue,32)}{text(id==='07'?'우리 기획에서 결정할 질문':'기본 규칙은 별도 확인',460,-165,P.red,31)}{text(id==='07'?'진입 알림 · 재실행 시점 · 비용 · 제한':'기본 난이도·모든 진입 표시로 일반화하지 않기',0,315,P.ink,29)}</Node>);
 }else if(id==='13-3'){
  g.add(island(-450));g.add(s.actor(()=>-580+240*move(),0,P.blue));g.add(s.path(()=>[[-650,0,65],[-220,0,65]],P.blue,move));g.add(s.box(470,0,0,570,460,45,'#ebe1d6'));g.add(s.polygon(()=>[[200,-100,55+55*move()],[750,-100,110-55*move()],[750,100,110-55*move()],[200,100,55+55*move()]],'#edf1e8'));g.add(s.box(()=>350+210*move(),0,125,80,50,30,'#dac574'));g.add(<Node>{text('캐릭터가 걷는다',-450,-165,P.blue,32)}{text('책이 기울고 열쇠가 움직인다',470,-165,'#94712e',29)}{text('움직이는 주체와 변화 · 정확한 입력은 별도 확인',0,315,P.muted,28)}</Node>);
 }else if(id==='10-2'){
  for(const [i,x] of [-460,460].entries()){g.add(island(x,'#dae8f2'));g.add(s.box(()=>x-80+160*move(),0,()=>50+i*35*Math.sin(Math.PI*move()),190,110,45,'#d5c4aa'));g.add(text(i?'파도 위의 이동 컷':'평평한 물 위의 이동 컷',x,-165,P.blue,31));}g.add(text('서로 다른 편집 컷 · 연속 결과를 자동으로 연결하지 않기',0,315,P.muted,29));
 }else if(id==='11'){
  g.add(island(-450));g.add(island(460));g.add(s.box(-450,0,45,300,40,230,'#dce6f0'));g.add(portal(460,0));g.add(<Node>{text('아무 벽에나 들어간다?',-450,-165,P.red,31)}{text('진입 지점을 조건으로 말했는가?',460,-165,P.green,29)}{text('목표와 동작 · 아직 정할 조건을 듣는 사람의 말로 확인',0,315,P.ink,28)}</Node>);
 }else if(id==='14-0'){
  [-570,0,570].forEach(x=>g.add(island(x)));g.add(portal(-570,0));g.add(s.actor(0,0,P.blue));g.add(s.path(()=>[[-130,0,110],[100,0,110]],P.red,move));g.add(s.box(570,0,45,190,140,90,'#d6b39a'));g.add(s.box(570,-35,()=>135+100*move(),190,140,25,'#bc8b72'));g.add(s.box(570,0,()=>140+100*move(),90,12,110,'#e7e0ce'));g.add(<Node>{text('진입 이동',-570,-165,P.green,32)}{text('안에서 전투',0,-165,P.blue,32)}{text('상자와 카드 변화',570,-165,'#94712e',32)}{text('다른 행동과 결과 · 연결 조건은 별도로 확인',0,315,P.muted,29)}</Node>);
 }else if(id==='15-3'){
  g.add(island(-450,'#dce8f2'));g.add(island(460,'#edddd3'));g.add(s.actor(()=>-560+230*move(),0,P.blue));g.add(s.actor(550,0,P.green));g.add(s.path(()=>[[450,0,110],[200,0,110]],P.red,move));g.add(<Node>{text('물가·용암 위로 이동',-450,-165,P.blue,31)}{text('적을 향해 발사',460,-165,P.red,31)}{text('공간과 대상이 다르면 설명도 나누기',0,315,P.ink,31)}</Node>);
 }else{
  [-570,0,570].forEach(x=>g.add(island(x)));g.add(s.flag(-570,0));g.add(s.actor(()=>-80+160*move(),0,P.blue));g.add(s.box(570,0,45,180,160,80,'#dce6f0'));g.add(<Node>{text('목표',-570,-165,P.ink,32)}{text('가능한 행동 · 조건',0,-165,P.blue,32)}{text('다음 행동의 연결',570,-165,P.green,32)}{text('직접 쓴 문장 + 듣는 사람의 되말하기',0,315,P.ink,31)}</Node>);
 }
 view.add(<Txt text={()=>notes[id]?.[Math.min(phase(),notes[id].length-1)]||'설명용 공간 도식 · 보인 행동과 미정인 조건을 나누기'} y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);yield* t(frames/60,frames/60,linear);
}
