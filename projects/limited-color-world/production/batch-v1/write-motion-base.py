from pathlib import Path
R=Path('D:/Github/VideoEditing')
common=r'''import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
const P={bg:'#080B0B',ink:'#F5F5F0',yellow:'#F8D66D',teal:'#62D6C5',green:'#91D7A0',red:'#F08083',dim:'#788382',line:'#3D4B49'};
const FONT='Noto Sans KR';
type Pt=[number,number];
export interface Timing{duration:number;cues:number[];title:string;mode:string;labels:string[];images?:string[];summary?:string;}
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>{const q=clamp(v);return q*q*(3-2*q)};
const txt=(t:string,x:number,y:number,s=60,c=P.ink,w=1680)=><Txt text={t} x={x} y={y} fontFamily={FONT} fontWeight={600} fontSize={s} lineHeight={s*1.22} fill={c} width={w} textAlign={'center'} textWrap/>;
export function* lesson(view:View2D,t:Timing){
 view.fill(P.bg);const clock=createSignal(0);const times=t.cues.length?t.cues:[0];
 const reveal=(n:number)=>()=>ease((clock()-(times[Math.min(n,times.length-1)]??0))/.28);
 const step=()=>times.reduce((a,v,i)=>clock()>=v?i:a,0);
 const line=(pts:Pt[],color=P.teal,n=0,arrow=true)=><Line points={pts} stroke={color} lineWidth={8} lineCap={'round'} lineJoin={'round'} endArrow={arrow} arrowSize={20} end={reveal(n)}/>;
 view.add(txt(t.title,0,-424,66,P.yellow));
 const footer=(text:string,color=P.ink)=>view.add(txt(text,0,296,53,color));
 const photo=(i=0,w=1160,h=652,x=0,y=-61)=>t.images?.[i]?<Img src={t.images[i]} width={w} height={h} x={x} y={y}/>:<Rect x={x} y={y} width={w} height={h} stroke={P.line} lineWidth={2}/>;
 const label=(i:number,x:number,y:number,color=P.ink,size=59,w=600)=> <Node opacity={reveal(i)}>{txt(t.labels[i]??'',x,y,size,color,w)}</Node>;
 if(t.mode==='photo'||t.mode==='setting'||t.mode==='overview'||t.mode==='grayscale'){
  if(t.mode==='grayscale'){
   view.add(<><Node opacity={()=>1-reveal(1)()}>{photo(0,1216,684,0,-50)}</Node><Node opacity={reveal(1)}>{photo(1,1216,684,0,-50)}</Node></>);
  }else if(t.mode==='overview'&&t.images?.length>1){
   view.add(<>{t.images.slice(0,3).map((s,i)=><Node opacity={reveal(i)}><Img src={s} width={760} height={427.5} x={i%2?420:-420} y={i===2?65:-90}/>{txt(t.labels[i]??'',i%2?420:-420,205,54,i===1?P.teal:P.ink,760)}</Node>)}</>);
  }else{
   view.add(photo(0,1152,648,0,-65));
   if(t.images?.length&&t.images.length>1)view.add(<Node opacity={reveal(1)}>{photo(1,1152,648,0,-65)}</Node>);
  }
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
 }else if(t.mode==='range'){
  view.add(txt('설명 모형 · 실제 게임 수치가 아닙니다',0,-303,38,P.dim));
  for(let i=0;i<5;i++)view.add(<Rect x={-560+i*280} y={75} width={280} height={125} stroke={P.line} lineWidth={3}/>);
  const playerX=()=>-560+(step()>=2?280:0);
  view.add(<><Circle x={playerX} y={-25} size={85} fill={P.teal}/><Circle x={280} y={-25} size={85} fill={P.red}/><Line points={()=>[[playerX(),-25],[playerX()+560,-25]]} stroke={P.teal} lineWidth={16} endArrow arrowSize={25}/>{txt('공격 범위 2칸',-280,-161,57,P.teal,680)}{txt('상대 거리 3칸',420,-161,57,P.red,680)}</>);
  footer(t.summary??'한 칸 접근 → 공격이 닿는 거리',P.green);
 }else if(t.mode==='delay'){
  view.add(txt('설명 모형 · 실제 CP 반응 시간은 별도입니다',0,-303,38,P.dim));
  view.add(<>{line([[-690,15],[690,15]],P.dim,0,false)}{label(0,-570,-130,P.teal)}{label(1,570,-130,P.green)}
    <Circle x={()=>-600+1200*clamp((clock()-(times[1]??0))/.8)} y={15} size={38} fill={P.yellow}/>{txt('12 프레임 ÷ 60 프레임/초 = 0.2 초',0,160,65,P.yellow)}</>);
  footer(t.summary??'알아챔과 실행 사이에 시간을 둡니다');
 }else if(t.mode==='priority'){
  view.add(<>{label(0,-500,-120,P.teal)}{label(1,500,-120,P.red)}
    {line([[-500,-35],[-150,65]],P.teal,0)}{line([[500,-35],[150,65]],P.red,1)}
    <Node opacity={reveal(2)}><Rect y={145} width={800} height={116} stroke={P.yellow} lineWidth={6}/>{txt(t.labels[2]??'우선순위로 하나를 고릅니다',0,145,59,P.yellow,1100)}</Node></>);
  footer(t.summary??'행동을 바꿀 조건까지 정합니다');
 }else{
  const labels=t.labels.slice(0,4);const n=labels.length;const gap=n>3?440:590;
  view.add(<>{labels.map((s,i)=>{const x=(i-(n-1)/2)*gap;return <Node opacity={reveal(i)}><Circle x={x} y={-60} size={92} stroke={i===n-1?P.green:P.teal} lineWidth={7}/>{txt(String(i+1),x,-60,52,i===n-1?P.green:P.teal)}{txt(s,x,70,58,P.ink,gap-45)}{i<n-1?line([[x+65,-60],[x+gap-65,-60]],P.teal,i+1):null}</Node>})}</>);
  if(t.images?.[0])view.add(<Node opacity={.18}><Img src={t.images[0]} x={0} y={-60} width={1450} height={815.625}/></Node>);
  footer(t.summary??'정보를 읽고 → 판단하고 → 행동합니다',P.yellow);
 }
 yield* clock(t.duration,t.duration,linear);
}
'''
for slug in ['limited-color-world','computer-controlled-players']:
 d=R/'motion-canvas/src/projects'/slug/'batch-v1';d.mkdir(parents=True,exist_ok=True)
 (d/'visuals.tsx').write_text(common,encoding='utf-8')
 (d/'scene.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,{duration:6,cues:[0,1.5,3],title:'시각 설명 · 내부 사전 점검',mode:'flow',labels:['정보','판단','행동']});});\n",encoding='utf-8')
 (d/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './scene?scene';\nexport default makeProject({scenes:[scene]});\n",encoding='utf-8')
 print(slug,'MC base written')
