import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';

export interface Cue {id:string;scene:string;purpose:string;title:string;labels:string[];frames:number;sourceImage:string;variant:number;startFrame:number;endFrame:number;globalStartFrame:number;globalEndFrame:number;pictureKind:string;stageCueTimes?:number[];metrics?:{control:number;wait:number;total:number;share:string}|null;}
type Point=[number,number];
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const text=(s:string,x:number,y:number,size=48,color:string=P.ink,width=760)=><Txt text={s} x={x} y={y} fontFamily={P.font} fontWeight={600} fontSize={size} fill={color} width={width} textWrap textAlign={'center'} lineHeight={size*1.25}/>;

/** Pictures are inspected screenshots; moving figures are explicitly editorial models. */
export function* explain(view:View2D,c:Cue){
 const clock=createSignal(0), duration=c.frames/60;
 const stageTime=Math.min(1.6,duration/3);
 const progress=(i:number)=>()=>clamp((clock()-(c.stageCueTimes?.[i]??i*stageTime))/.45);
 const stage=()=>Math.min(2,Math.floor(clock()/stageTime));
 const root=new Node({});view.add(root);view.fill(P.background);
 const draw=(pts:Point[],color:string=P.teal,i=0,arrow=true)=><Line points={pts} stroke={color} lineWidth={8} lineCap={'round'} lineJoin={'round'} endArrow={arrow} arrowSize={20} end={progress(i)}/>;
 const label=(i:number,y:number,color:string=P.ink)=><Node opacity={progress(i)}>{text(c.labels[i]??'',455,y,48,color,790)}</Node>;
 root.add(<>{text(c.title,0,-423,c.title.length>31?54:64,P.yellow,1740)}
  <Img src={c.sourceImage.replace('/@fs/C:/Users/1/.codex/video-production/design-finish-six-20261026/', '/@fs/D:/Github/VideoEditing/projects/').replace('/batch-v1/', '/production/local/batch-v1/')} x={-460} y={-66} width={860} height={483.75}/>
  {text('게임 화면',-460,213,36,P.muted,850)}
  {text('원리 도식',455,c.purpose==='wash'?-350:-315,36,P.muted,790)}
 </>);
 const flow=()=>{
  root.add(<>{c.labels.map((s,i)=><Node opacity={progress(i)}>
   <Circle x={140} y={-190+i*180} size={70} stroke={i===2?P.green:P.teal} lineWidth={6}/>
   {text(String(i+1),140,-190+i*180,40,i===2?P.green:P.teal,90)}
   {text(s,500,-190+i*180,50,i===2?P.green:P.ink,620)}
   {i<2?draw([[140,-142+i*180],[140,-70+i*180]],P.teal,i+1):null}
  </Node>)}</>);
 };
 if(c.purpose==='timeline-before'||c.purpose==='timeline-after'){
  const after=c.purpose==='timeline-after';const waiting=()=>20-(after?10*progress(1)():0);
  root.add(<>
   {text('설명용 가정 · 초',455,-233,40,P.muted,790)}
   <Rect opacity={after?1:progress(0)} x={328} y={-80} width={480} height={112} fill={P.teal}/>
   <Rect opacity={after?1:progress(1)} x={()=>568+waiting()*6} y={-80} width={()=>waiting()*12} height={112} fill={P.red}/>
   <Node opacity={after?1:progress(0)}>{text('조작 40초',328,-80,46,P.background,470)}</Node>
   <Txt opacity={after?1:progress(1)} text={()=>`대기 ${Math.round(waiting())}초`} x={()=>568+waiting()*6} y={55} fontFamily={P.font} fontSize={42} fill={P.red}/>
   <Node opacity={progress(2)}>{text(after?'40 ÷ 50 = 80%':'40 ÷ 60 = 2/3',455,190,64,P.yellow,790)}</Node>
   <Line opacity={after?1:progress(1)} points={()=>[[88,-9],[88,15],[568+waiting()*12,15],[568+waiting()*12,-9]]} stroke={P.line} lineWidth={3}/>
  </>);
 }else if(['intent','choice','opportunity','alternatives','comparison'].includes(c.purpose)){
  root.add(<>{label(0,-225,P.teal)}{label(1,5,P.green)}
   {draw([[455,-170],[455,-70]],P.teal,1,false)}
   <Circle x={455} y={-106} size={17} fill={P.yellow}/>
   {draw([[455,64],[455,138]],P.green,2)}{label(2,213,P.yellow)}</>);
 }else if(['route','instructions'].includes(c.purpose)){
  root.add(<>{draw([[140,160],[360,40],[550,-130],[790,-190]],P.line,0,false)}
   {draw([[360,40],[560,160],[790,200]],P.line,0,false)}
   <Circle x={140} y={160} size={38} fill={P.teal}/>
   <Circle x={()=>140+410*progress(1)()} y={()=>160-290*progress(1)()} size={34} fill={P.yellow}/>
   {draw([[140,160],[360,40],[550,-130]],P.green,1)}
   {text(c.labels[0],455,-252,44,P.ink)}
   <Node opacity={progress(2)}>{text(c.labels[2],455,285,46,P.green)}</Node></>);
 }else if(c.purpose==='steering'){
  root.add(<><Line points={[[210,220],[210,-225],[680,-225],[680,220]]} stroke={P.line} lineWidth={5}/>
   {draw([[440,170],[580,20],[650,-80]],P.red,0,false)}
   {draw([[650,-80],[540,-130],[445,-210]],P.green,1)}
   <Circle x={()=>440+210*progress(0)()-205*progress(1)()} y={()=>170-250*progress(0)()-130*progress(1)()} size={40} fill={P.yellow}/>
   {text('코스 경계',455,280,42,P.muted)}
   <Node opacity={progress(2)}>{text('이탈 방향을 안쪽으로 보조',455,-288,46,P.green)}</Node></>);
 }else if(['acceleration','burden','handoff','onboarding','menu-control'].includes(c.purpose)){
  root.add(<>{c.labels.map((s,i)=><Node opacity={progress(i)}>
   <Rect x={145} y={-190+i*175} width={80} height={80} radius={12} stroke={i===0?P.teal:P.green} lineWidth={5}/>
   {text(i===0?'입력':String(i+1),145,-190+i*175,32,P.ink,100)}
   {draw([[205,-190+i*175],[300,-190+i*175]],i===0?P.teal:P.green,i)}
   {text(s,570,-190+i*175,48,P.ink,530)}
  </Node>)}</>);
 }else if(c.purpose==='distance'||c.purpose==='feedback'){
  root.add(<><Line points={[[120,40],[810,40]]} stroke={P.line} lineWidth={4}/>
   <Circle x={260} y={-40} size={90} stroke={P.teal} lineWidth={7}/>
   <Circle x={()=>700-160*progress(1)()} y={-40} size={90} stroke={P.red} lineWidth={7}/>
   {draw([[320,-40],[490,-40]],P.teal,1)}
   {label(0,-220,P.teal)}{label(1,140,P.ink)}{label(2,270,P.green)}</>);
 }else if(c.purpose==='turbo'){
  root.add(<>{c.labels.map((s,i)=><Node opacity={progress(i)}>
   <Rect x={180+i*230} y={65-i*55} width={130} height={130+i*110} fill={[P.teal,P.yellow,P.green][i]}/>
   {text(s,180+i*230,250,41,P.ink,230)}
  </Node>)}</>);
 }else if(c.purpose==='calendar'||c.purpose==='commitment'){
  root.add(<>{text('300시간',455,-215,85,P.yellow)}
   {Array.from({length:30},(_,i)=><Rect x={185+(i%10)*60} y={-76+Math.floor(i/10)*62} size={38} fill={()=>i<Math.floor(progress(1)()*30)?P.teal:P.panel}/>)}
   <Node opacity={progress(2)}>{text(c.purpose==='calendar'?'÷ 하루 1시간 = 300일':'재미를 알기 전의 약속',455,220,52,P.ink)}</Node>
   {text('설명용 가정',455,310,35,P.muted)}</>);
 }else if(c.purpose==='wash'){
  root.add(<><Rect x={455} y={-30} width={650} height={340} fill={P.teal}/>
   <Rect x={()=>455+325*progress(1)()} y={-30} width={()=>650*(1-progress(1)())} height={340} fill={P.panel}/>
   <Line points={()=>[[120+650*progress(1)(),-245],[130+650*progress(1)(),145]]} stroke={P.ink} lineWidth={10}/>
   {label(0,-285)}{label(2,242,P.green)}</>);
 }else if(c.purpose==='phone'){
  root.add(<><Rect x={455} y={-20} width={285} height={440} radius={28} stroke={P.ink} lineWidth={6}/>
   {c.labels.map((s,i)=><Node opacity={progress(i)}><Line points={[[350,-155+i*120],[560,-155+i*120]]} stroke={[P.teal,P.yellow,P.green][i]} lineWidth={24}/></Node>)}
   <Txt text={()=>c.labels[stage()]} x={455} y={282} fontFamily={P.font} fontSize={46} fill={P.ink} width={780} textWrap textAlign={'center'}/></>);
 }else if(c.purpose==='damage'){
  root.add(<>{text('설명 모형 · 실제 수치 아님',455,-250,37,P.muted)}
   <Circle x={()=>220+440*progress(2)()} y={()=>15-90*progress(2)()} size={90} stroke={P.yellow} lineWidth={8}/>
   {draw([[220,40],[770,-80]],P.teal,2)}
   {label(0,-160)}{label(1,180,P.red)}{label(2,290,P.green)}</>);
 }else flow();
 yield* clock(duration,duration,linear);root.remove();
}
