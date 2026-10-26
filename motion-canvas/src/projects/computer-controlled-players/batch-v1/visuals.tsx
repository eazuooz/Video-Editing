import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';
const P={bg:D.background,ink:D.ink,yellow:D.yellow,teal:D.teal,green:D.green,red:D.red,dim:D.muted,line:D.line};
const FONT=D.font;
type Pt=[number,number];
export interface Timing{duration:number;cues:number[];title:string;mode:string;labels:string[];images?:string[];summary?:string;}
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>{const q=clamp(v);return q*q*(3-2*q)};
const txt=(t:string,x:number,y:number,s=60,c:string=P.ink,w=1680)=><Txt text={t} x={x} y={y} fontFamily={FONT} fontWeight={600} fontSize={s} lineHeight={s*1.22} fill={c} width={w} textAlign={'center'} textWrap/>;
export function* lesson(view:View2D,t:Timing){
 view.fill(P.bg);const clock=createSignal(0);const times=t.cues.length?t.cues:[0];
 const reveal=(n:number)=>()=>ease((clock()-(times[Math.min(n,times.length-1)]??0))/.28);
 const step=()=>times.reduce((a,v,i)=>clock()>=v?i:a,0);
 const line=(pts:Pt[],color:string=P.teal,n=0,arrow=true)=><Line points={pts} stroke={color} lineWidth={8} lineCap={'round'} lineJoin={'round'} endArrow={arrow} arrowSize={20} end={reveal(n)}/>;
 if(t.mode==='evidenceFreeze'){
  view.add(<><Img src={t.images?.[0]} x={0} y={-64} width={1408} height={792}/>{txt('가까운 주먹 · 명중 결과 정지 분석',0,-500,42,P.yellow)}</>);
  yield* clock(t.duration,t.duration,linear);return;
 }
 view.add(txt(t.title,0,-424,66,P.yellow));
 const footer=(text:string,color:string=P.ink)=>view.add(txt(text,0,280,56,color));
 const photo=(i=0,w=1160,h=652,x=0,y=-61)=>t.images?.[i]?<Img src={t.images[i]} width={w} height={h} x={x} y={y}/>:<Rect x={x} y={y} width={w} height={h} stroke={P.line} lineWidth={2}/>;
 const label=(i:number,x:number,y:number,color:string=P.ink,size=59,w=600)=> <Node opacity={reveal(i)}>{txt(t.labels[i]??'',x,y,size,color,w)}</Node>;
 if(t.mode==='photo'||t.mode==='setting'||t.mode==='overview'||t.mode==='grayscale'){
  if(t.mode==='grayscale'){
   view.add(<><Node opacity={()=>1-reveal(1)()}>{photo(0,1104,621,0,-65)}</Node><Node opacity={reveal(1)}>{photo(1,1104,621,0,-65)}</Node></>);
  }else if(t.mode==='overview'&&(t.images?.length??0)>1){
   view.add(<>{t.images!.slice(0,3).map((s,i)=><Node opacity={reveal(i)}><Img src={s} width={760} height={427.5} x={i%2?420:-420} y={i===2?65:-90}/>{txt(t.labels[i]??'',i%2?420:-420,205,54,i===1?P.teal:P.ink,760)}</Node>)}</>);
  }else{
   view.add(photo(0,1104,621,0,-65));
   if(t.images?.length&&t.images.length>1)view.add(<Node opacity={reveal(1)}>{photo(1,1104,621,0,-65)}</Node>);
  }
  if(t.mode==='setting')view.add(<><Rect x={-280} y={-171} width={480} height={58} stroke={P.green} lineWidth={8}/>{txt('필터 유형 선택',-350,-283,48,P.green,670)}</>);
  footer(t.summary??t.labels[t.labels.length-1]??'');
 }else if(t.mode==='color'||t.mode==='lightness'||t.mode==='patterns'||t.mode==='theme'){
  const xs=[-480,0,480];
  view.add(<>{xs.map((x,i)=><Node><Rect x={x} y={-30} width={240} height={240} radius={16} fill={()=>{
   if(t.mode==='lightness')return i===0?'#46594F':i===1?(step()>=1?'#D3DDD3':'#536853'):'#141B17';
   if(t.mode==='theme')return step()>=1?['#BF6977','#6C8B73','#746D89'][i]:['#EE899C','#64CBA9','#D5B064'][i];
   return step()>=1&&t.mode==='color'?'#A3A078':['#EE899C','#73D4AB','#D5B064'][i];
  }} stroke={P.ink} lineWidth={4}/>
  {t.mode==='patterns'?<Node opacity={reveal(1)}>{i===0?<Circle x={x} y={-30} size={104} stroke={P.bg} lineWidth={12}/>:i===1?<Line points={[[x,-95],[x-65,30],[x+65,30]]} closed stroke={P.bg} lineWidth={12}/>:<>{[-50,0,50].map(q=><Line points={[[x-70,-30+q],[x+70,-30+q]]} stroke={P.bg} lineWidth={12}/>)}</>}</Node>:null}
  {txt(t.labels[i]??['종류 A','종류 B','배경'][i],x,161,57,P.ink,430)}</Node>)}</>);
  footer(t.summary??'색 차이 외에도 구별할 단서를 남깁니다',P.teal);
 }else if(t.mode==='background'){
  view.add(<><Rect width={1210} height={430} x={0} y={-55} fill={'#18271F'}/><Rect width={230} height={230} x={0} y={-55} fill={()=>step()>=1?'#18271F':'#A0C391'} stroke={()=>step()>=2?P.ink:'#18271F'} lineWidth={()=>step()>=2?8:0}/>{txt('어두운 배경',0,217,54,P.ink)}{label(0,0,-304,P.teal)}</>);
  footer(t.summary??'대상끼리의 차이와 배경에서의 분리를 함께 봅니다');
 }else if(t.mode==='controls'){
  const state=()=>clock()<(times[0]??0)+.8?0:clock()<(times[2]??t.duration)?1:2;
  view.add(txt('조작 상태를 설명하는 모형',0,-306,40,P.dim));
  view.add(<>{txt('입력 방향',-520,-180,58,P.teal)}{txt('이동 해석',520,-180,58,P.green)}
   <Line points={()=>state()>=2?[[-320,-30],[-720,-30]]:[[-720,-30],[-320,-30]]} stroke={P.teal} lineWidth={14} endArrow arrowSize={30}/>
   <Line points={()=>state()===1?[[720,-30],[320,-30]]:[[320,-30],[720,-30]]} stroke={()=>state()===1?P.red:P.green} lineWidth={14} endArrow arrowSize={30}/>
   <Node opacity={reveal(1)}>{txt('방향 반전',0,80,64,P.red)}</Node><Node opacity={reveal(2)}>{txt('새 상태를 반영해 다시 판단',0,194,58,P.green)}</Node></>);
  footer(t.summary??'짧은 혼란 뒤, 달라진 상태를 반영합니다');
 }else if(t.mode==='range'){
  view.add(txt('설명 모형 · 실제 게임 수치가 아닙니다',0,-303,38,P.dim));
  for(let i=0;i<5;i++)view.add(<Rect x={-560+i*280} y={75} width={280} height={125} stroke={P.line} lineWidth={3}/>);
  const advance=()=>step()>=(times.length>=4?3:2);
  const playerX=()=>-560+(advance()?280:0);
  view.add(<><Circle x={playerX} y={-25} size={85} fill={P.teal}/><Circle x={280} y={-25} size={85} fill={P.red}/><Line points={()=>[[playerX(),-25],[playerX()+560,-25]]} stroke={P.teal} lineWidth={16} endArrow arrowSize={25}/>{txt('공격 범위 2칸',-280,-161,57,P.teal,680)}<Txt text={()=>advance()?'상대 거리 2칸':'상대 거리 3칸'} x={420} y={-161} fontFamily={FONT} fontSize={57} fontWeight={600} fill={P.red}/></>);
  footer(t.summary??'한 칸 접근 → 공격이 닿는 거리',P.green);
 }else if(t.mode==='delay'){
  view.add(txt('설명 모형 · 실제 CP 반응 시간은 별도입니다',0,-303,38,P.dim));
  view.add(<>{line([[-690,15],[690,15]],P.dim,0,false)}{label(0,-570,-130,P.teal)}{label(1,570,-130,P.green)}
    <Circle x={()=>-600+1200*clamp((clock()-(times[1]??0))/.2)} y={15} size={38} fill={P.yellow}/>{txt('12 프레임 ÷ 60 프레임/초 = 0.2 초',0,160,65,P.yellow)}</>);
  footer(t.summary??'알아챔과 실행 사이에 시간을 둡니다');
 }else if(t.mode==='priority'){
  const conflictCase=times.length>=4;
  view.add(<>{label(0,-500,-120,P.teal)}{label(1,500,-120,P.red)}
    {line([[-500,-35],[-150,65]],P.teal,0)}{line([[500,-35],[150,65]],P.red,1)}
    {conflictCase?<>
      <Node opacity={()=>reveal(2)()*(1-reveal(3)())}><Line points={[[-24,12],[24,60]]} stroke={P.red} lineWidth={10}/><Line points={[[-24,60],[24,12]]} stroke={P.red} lineWidth={10}/>{txt('동시에 켜짐 · 판단 충돌',0,145,59,P.red,1200)}</Node>
      <Node opacity={reveal(3)}><Rect y={145} width={1080} height={116} stroke={P.yellow} lineWidth={6}/>{txt('상황에 맞춘 우선순위 결정',0,145,59,P.yellow,1100)}</Node>
    </>:<Node opacity={reveal(2)}><Rect y={145} width={1000} height={116} stroke={P.yellow} lineWidth={6}/>{txt(t.labels[2]??'상황을 읽는 판단',0,145,59,P.yellow,1100)}</Node>}</>);
  footer(t.summary??'행동을 바꿀 조건까지 정합니다');
 }else{
  const labels=t.labels.slice(0,4);const n=labels.length;const gap=n>3?440:590;
  view.add(<>{labels.map((s,i)=>{const x=(i-(n-1)/2)*gap;return <Node opacity={reveal(i)}><Circle x={x} y={-60} size={92} stroke={i===n-1?P.green:P.teal} lineWidth={7}/>{txt(String(i+1),x,-60,52,i===n-1?P.green:P.teal)}{txt(s,x,70,58,P.ink,gap-45)}{i<n-1?line([[x+65,-60],[x+gap-65,-60]],P.teal,i+1):null}</Node>})}</>);

  footer(t.summary??'정보를 읽고 → 판단하고 → 행동합니다',P.yellow);
 }
 yield* clock(t.duration,t.duration,linear);
}
