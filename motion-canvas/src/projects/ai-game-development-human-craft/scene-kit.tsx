/// <reference types="vite/client" />
import {View2D,Node,Txt,Rect,Circle,Line,Video,Img} from '@motion-canvas/2d';
import {createSignal,tween,Vector2} from '@motion-canvas/core';
import data from './scene-data.json';
import media from './media.json';
import {CaptionBox} from '../game-dev-career/preview/caption-box';
// Recorded states stay in local output storage, not in Git or hand-written UI.
const captures=import.meta.glob('../../../../shared/output/ai-game-development-human-craft/unity-production/*/*-capture.json',{eager:true,import:'default'});

// All text and graphics use the channel's semantic colors. Black remains quiet;
// the animated path, state or comparison is the focus, not surrounding chrome.
const C={bg:'#000000',ink:'#f5f5f5',yellow:'#e8cf83',teal:'#73c7c2',muted:'#b8b8b8',line:'#39464c',red:'#ef8585',orange:'#f39a4b',panel:'#10181c'};
const font="'Noto Sans KR','Malgun Gothic',sans-serif";
const clamp=(n:number,a=0,b=1)=>Math.max(a,Math.min(b,n));
const smooth=(n:number)=>{n=clamp(n);return n*n*(3-2*n);};
function label(text:any,x:number,y:number,size=38,fill:any=C.ink,width=1600){return new Txt({text,x,y,fontSize:size,fontFamily:font,fontWeight:500,fill,width,textAlign:'center',textWrap:true,lineHeight:size*1.36});}
function arrow(parent:Node,points:any,progress:any,color:any=C.teal,width=7,dash:number[]=[]){const l=new Line({points,stroke:color,lineWidth:width,end:progress,endArrow:true,arrowSize:20,lineDash:dash,radius:24});parent.add(l);return l;}
function dot(parent:Node,x:number,y:number,text:string,active:()=>boolean,fill=C.teal){parent.add(new Circle({x,y,size:200,fill:C.bg,stroke:()=>active()?fill:C.line,lineWidth:5}));parent.add(label(text,x,y,40,()=>active()?C.ink:C.muted,180));}
const fs=(p:string)=>'/@fs/D:/Github/VideoEditing/'+p;

function flow(parent:Node,labels:string[],progress:()=>number,mode:string){
 const n=labels.length;
 const points=labels.map((_,i):[number,number]=>mode==='cycle'?(i===0?[-540,-85]:i===1?[540,-85]:i===2?[540,200]:[-540,200]):mode==='branch'?(i===0?[-520,60]:i===1?[350,-100]:[350,240]):[-640+i*1280/Math.max(1,n-1),70]);
 for(let i=1;i<n;i++){
  const a=points[mode==='branch'?0:i-1],b=points[i];const v=new Vector2(b).sub(new Vector2(a)).normalized;const start=new Vector2(a).add(v.scale(127)),end=new Vector2(b).sub(v.scale(127));
  arrow(parent,[start,end],()=>smooth(progress()-(i-1)),i===n-1?C.yellow:C.teal);
 }
 points.forEach(([x,y],i)=>dot(parent,x,y,labels[i],()=>progress()>=i-.15,i===n-1?C.yellow:C.teal));
 if(mode==='cycle')arrow(parent,[[-650,200],[-765,200],[-765,-85],[-650,-85]],()=>smooth(progress()-2.5),C.orange,6,[12,12]);
}

function sourceScene(view:View2D,s:any,t:()=>number,p:()=>number){
 const src=s.source;
 view.add(label(src.name,-75,-215,42,C.ink));
 view.add(label(src.date,0,-157,26,C.muted));
 view.add(new Line({points:[[-770,-105],[770,-105]],stroke:C.yellow,lineWidth:3}));
 view.add(label(src.statement,0,-15,48,C.ink,1590));
 const g=new Node({y:90,scale:.85});view.add(g);flow(g,s.labels,()=>clamp(t()/Math.max(1,s.duration-3))*3,'flow');
 view.add(label(src.note,0,285,32,C.yellow));
 view.add(label(src.url,0,340,23,C.muted));
 if(s.id==='04'||s.id==='10'){
  const begin=s.id==='10'?s.paragraphs[1].start:0;
  const evidence=new Node({opacity:()=>t()>=begin&&t()<begin+8?1:0});view.add(evidence);
  evidence.add(new Rect({x:0,y:15,width:1800,height:620,fill:C.bg}));
  if(s.id==='04'){
   const crop=new Rect({x:0,y:-70,width:1518,height:396,clip:true});evidence.add(crop);
   crop.add(new Img({src:fs('shared/output/ai-game-development-human-craft/source-review/epic-announcement.png'),width:1518,height:855.6,y:229.8}));
   evidence.add(label('실제 공식 공지 · 2026.06.22',0,220,35,C.muted));
  }else evidence.add(new Img({src:fs('shared/output/ai-game-development-human-craft/source-review/unity-spark.png'),width:1050,height:592,x:0,y:-20}));
  evidence.add(label(src.note,0,300,33,C.yellow));
 }
}

function compareScene(view:View2D,s:any,t:()=>number){
 const rows=[{y:-80,name:'사람',labels:['노드 배치','연결의 흐름','동작 이해']},{y:200,name:'AI 도구',labels:['프로젝트 읽기','기능 호출','결과 검사']}];
 rows.forEach((r,j)=>{view.add(label(r.name,-780,r.y,35,j?C.yellow:C.teal,260));r.labels.forEach((x,i)=>{const xx=-390+i*490;view.add(new Rect({x:xx,y:r.y,width:380,height:110,stroke:j?C.yellow:C.teal,lineWidth:3,radius:8}));view.add(label(x,xx,r.y,40,C.ink,360));if(i)arrow(view,[[xx-295,r.y],[xx-205,r.y]],()=>smooth((t()-j*7-i*2)/2),j?C.yellow:C.teal);});});
}

function timelineScene(view:View2D,s:any,t:()=>number){
 const n=s.labels.length;
 view.add(new Line({points:[[-755,90],[755,90]],stroke:C.line,lineWidth:5}));
 s.labels.forEach((x:string,i:number)=>{const pos=-650+i*1300/(n-1);const on=()=>t()>=s.duration*i/(n+1);view.add(new Circle({x:pos,y:90,size:26,fill:()=>on()?C.yellow:C.line}));view.add(label(x,pos,i%2?-30:215,43,()=>on()?C.ink:C.muted,350));view.add(new Line({points:[[pos,90],[pos,i%2?15:160]],stroke:()=>on()?C.yellow:C.line,lineWidth:3}));});
 if(s.id==='11')view.add(label('Pinstripe  ·  Neversong  ·  Twisted Tower',0,-170,40,C.teal));
 if(s.id==='12')view.add(label('직접 만든 결과가 움직이고, 소리가 나는 순간',0,-170,46,C.teal));
 if(s.id==='24')view.add(label('Halo       /       The Elder Scrolls',0,-170,48,C.teal));
}

function roadScene(view:View2D,s:any,t:()=>number){
 view.add(new Rect({x:0,y:65,width:1710,height:235,fill:C.panel}));
 view.add(new Line({points:[[-850,65],[850,65]],stroke:C.muted,lineWidth:4,lineDash:[38,32]}));
 const car=new Node({x:()=>-680+1050*clamp(t()/Math.max(1,s.duration*.55)),y:125});view.add(car);
 car.add(new Rect({width:145,height:60,fill:C.teal,radius:15}));car.add(new Rect({x:0,y:-37,width:87,height:43,fill:C.teal,radius:9}));car.add(new Rect({x:0,y:-38,width:60,height:28,fill:C.bg}));[-43,43].forEach(x=>car.add(new Circle({x,y:32,size:31,fill:C.bg,stroke:C.ink,lineWidth:4})));
 view.add(new Line({points:[[480,-100],[480,185]],stroke:C.muted,lineWidth:8}));view.add(new Rect({x:480,y:-115,size:104,rotation:45,fill:C.red,radius:10}));view.add(label('정지',480,-115,33,C.bg,100));
 s.labels.forEach((x:string,i:number)=>view.add(label(x,-590+i*590,295,42,i===1?C.yellow:C.ink,500)));
}

function horizonScene(view:View2D,s:any,t:()=>number){
 view.add(label('현재 확인된 기능',-530,-110,45,C.teal,600));view.add(label('앞으로의 발전',530,-110,45,C.yellow,600));
 view.add(new Line({points:[[0,-210],[0,260]],stroke:C.line,lineWidth:3}));
 arrow(view,[[-530,90],[-120,90]],()=>smooth(t()/3),C.teal);
 arrow(view,[[120,90],[600,90]],()=>smooth((t()-4)/4),C.yellow,7,[14,12]);
 view.add(label('조율과 검증',-530,185,43,C.ink,600));view.add(label('더 복잡한 제품',530,185,43,C.ink,600));
 view.add(label('전망을 현재의 성능으로 단정하지 않습니다.',0,300,35,C.muted));
}

const unityStart:{[key:string]:number}={'02':2,'06':2,'08':2,'09':5,'14':1,'17':2,'18':0,'20':4,'23':1,'25':5,'26':1,'28':0};
function unityScene(view:View2D,s:any,t:()=>number,p:()=>number){
 const m=(media as any).unity[s.id];const start=s.paragraphs[unityStart[s.id]||0]?.start||0;
 const local=()=>{
  const end=(m?.frames||1)/60-1/60;
  if(s.id==='17'){
   const phase=t()>=s.paragraphs[6].start?2:t()>=s.paragraphs[5].start?1:0;
   const begin=s.paragraphs[phase===2?6:phase===1?5:2].start;
   return clamp(phase*12+clamp(t()-begin,0,12-1/60),0,end);
  }
  return clamp(t()-start,0,end);
 };
 const captured:any=m?(captures as any)['../../../../'+m.capture]:null;
 const state=()=>{
  const f=Math.floor(local()*60),list=captured?.timeline||[];
  return (m?.video?list[Math.min(list.length-1,f)]:[...list].reverse().find((r:any)=>r.frame<=f))||{gold:100,items:0,result:'waiting',scenario:'normal-purchase'};
 };
 const shop=['09','17','18','23','25','28'].includes(s.id);
 const x=shop?-280:0,y=s.id==='20'?40:-10,w=shop?1230:1200,h=w*1080/1920;
 const canvas=s.id==='06'?new Rect({y:-10,width:1600,height:560,clip:true}):view;if(canvas!==view)view.add(canvas);
 const mw=s.id==='06'?1920:w,mh=s.id==='06'?1080:h;
 if(m?.video)canvas.add(new Video({src:fs(m.video),x,y:canvas===view?y:0,width:mw,height:mh,time:local}));
 else if(m?.posters?.length)canvas.add(new Img({src:()=>fs(([...m.posters].reverse().find((r:any)=>r.frame<=Math.floor(local()*60))||m.posters[0]).path),x,y:canvas===view?y:0,width:mw,height:mh}));
 else {view.add(new Rect({x,y,width:w,height:h,stroke:C.line,lineWidth:2}));view.add(label('Unity 장면 제작 중',x,y,50,C.muted,w));}
 view.add(label(s.note,0,s.id==='20'?-300:-280,26,C.muted));
 if(shop){
  const hue=()=>['insufficient-gold','inventory-full'].includes(state().result)?C.red:C.teal;
  view.add(new Line({points:[[405,-190],[405,260]],stroke:C.line,lineWidth:2}));
  view.add(label(()=>s.id==='09'?(state().scenario==='numeric-feedback'?'수치만 표시':'반응과 보상 연출'):s.id==='23'?(local()<(m?.frames||1)/120?'따뜻한 조명':'차가운 조명'):state().scenario==='insufficient-gold'?'골드 부족':state().scenario==='inventory-full'?'가방 가득':state().scenario==='same-request-retried'?'같은 요청 재전송':state().scenario==='two-distinct-purchases'?'서로 다른 구매':'정상 구매',650,-180,34,C.yellow,435));
  view.add(label(()=>`${state().gold} G`,650,-67,76,hue,430));
  view.add(label(()=>`물약 ${state().items} / 3`,650,37,47,C.ink,430));
  const names:any={'waiting':'요청 전','purchased':'구매 완료','duplicate-ignored':'같은 요청 무시','insufficient-gold':'구매 거절','inventory-full':'구매 거절'};
  view.add(label(()=>names[state().result]||state().result,650,135,40,hue,430));
  view.add(label('물약 가격 30 G',650,230,30,C.muted,430));
  if(s.id==='18')view.add(label(()=>`도착 ${state().requestDeliveries||0}회 / 처리 ${state().acceptedRequests||0}회`,650,300,26,C.muted,440));
  if(s.id==='09')view.add(label(()=>state().scenario==='animated-feedback'?'동작 · 보상 이동 · 효과음':'골드와 물약 수치',-280,310,33,C.teal,1150));
  if(s.id==='25'||s.id==='28')view.add(label(()=>p()<s.paragraphs.length/2?'조건을 이해하고, 빠진 것을 찾는다':'표현을 선택하고, 경험을 다듬는다',-280,310,37,C.yellow,1150));
  if(s.id==='18'){
   const show=()=>p()>=1;const panel=new Node({opacity:()=>show()?1:0});view.add(panel);
   panel.add(new Rect({x:-280,y:20,width:1210,height:560,fill:'#000000e8'}));panel.add(label('저장과 네트워크는 별도로 실행 검증',-280,-130,46,C.yellow,1150));panel.add(label('재접속  →  상태 비교  →  실패 복구',-280,0,44,C.ink,1150));panel.add(label('이 상점 시연은 메모리 내 요청 처리만 구현했습니다.',-280,140,30,C.muted,1100));
  }
 }else if(s.id==='20'){
  const lt=()=>local();view.add(label('즉시 반응',-230,-230,38,C.teal,440));view.add(label('18프레임 뒤 반응',230,-230,38,C.yellow,460));
  view.add(new Line({points:[[-600,145],[600,145]],stroke:C.line,lineWidth:3}));
  view.add(label(()=>lt()<3?'입력 대기':lt()<3.3?'동일한 입력 · 오른쪽은 아직 대기':'반응 차이 = 0.30초',0,290,43,()=>lt()>=3&&lt()<3.3?C.yellow:C.ink));
  view.add(new Circle({x:0,y:-170,size:34,fill:()=>lt()>=3?C.yellow:C.line}));
 }else if(s.id==='06'){
  view.add(label('펼친 UV 좌표',-270,290,42,C.ink,500));view.add(label('모델 표면',240,290,42,C.ink,500));
  arrow(view,[[-80,60],[120,60]],()=>smooth((t()-start)/2),C.yellow);
 }else if(s.id==='02'||s.id==='14'){
  const names:any={'approaching-door':'문에 접근','locked-key-required':'열쇠가 필요합니다','key-collected':'열쇠 획득','door-open':'문 열림'};
  view.add(label(()=>names[state().result]||'조건 → 입력 → 결과',0,290,45,C.yellow));
 }else if(s.id==='08'){
  view.add(label(()=>p()<3?'다리 · 등받이 · 좌판의 세부 구조':'재료와 표현, 실제 완성도를 함께 본다',0,305,39,C.teal));
 }else if(s.id==='26'){
  view.add(label(()=>local()<1?'위치 맞추기':local()<5?'나사를 조인다':'안착하면 멈춘다',0,300,45,C.yellow));
 }
 if(s.id==='28'){
  const outro=new Node({opacity:()=>p()>=6?1:0});view.add(outro);outro.add(new Rect({x:0,y:20,width:1800,height:620,fill:C.bg}));outro.add(label('여러분의 경험을 댓글로 남겨 주세요.',0,-110,58,C.yellow));outro.add(label('얌얌코딩 · 프로그래밍 과외',0,55,45,C.ink));outro.add(label('설명란의 과외 링크에서 확인할 수 있습니다.',0,150,34,C.muted));
 }
}

function footageScene(view:View2D,s:any,t:()=>number,p:()=>number){
 const start=s.paragraphs[s.id==='16'?5:1].start;const clips=(media as any).footage[s.id]||[];
 let offset=0;clips.forEach((m:any)=>{const begin=offset;offset+=m.duration;const last=m===clips[clips.length-1];view.add(new Video({src:fs(m.path),x:0,y:10,width:1640,height:922.5,time:()=>clamp(t()-start-begin,0,m.duration-1/60),opacity:()=>t()-start>=begin&&(last||t()-start<begin+m.duration)?1:0}));});
 view.add(new Rect({x:0,y:350,width:1920,height:70,fill:'#000000ee'}));view.add(label(s.note,0,345,26,C.muted));
 const early=new Node({opacity:()=>t()<start?1:0});view.add(early);early.add(new Rect({x:0,y:20,width:1800,height:600,fill:C.bg}));flow(early,s.labels,()=>clamp(t()/Math.max(1,start))*3,'flow');
 if(s.id==='16')view.add(label('스플래툰 방식의 잉크 개발 실험 · Nintendo 게임 본편이 아닙니다.',0,-280,25,C.muted));
 if(s.id==='22')view.add(label('2020년 Classic 녹화 · 형태와 색의 선택을 관찰합니다.',0,-280,26,C.muted));
 if(!clips.length)view.add(label('소스 클립 준비 중',0,15,50,C.muted));
}

export function* lesson(view:View2D,index:number){
 const s=data.scenes[index],t=createSignal(0);
 const paragraph=()=>{let i=s.paragraphs.findIndex(p=>t()>=p.start&&t()<p.end);return i<0?(t()>=s.paragraphs.at(-1)!.end?s.paragraphs.length-1:0):i;};
 view.fill(C.bg);
 const mode=s.mode;
 if(mode==='unity')unityScene(view,s,t,paragraph);
 else if(mode==='source')sourceScene(view,s,t,paragraph);
 else if(mode==='compare')compareScene(view,s,t);
 else if(mode==='timeline')timelineScene(view,s,t);
 else if(mode==='road')roadScene(view,s,t);
 else if(mode==='horizon')horizonScene(view,s,t);
 else if(mode==='footage')footageScene(view,s,t,paragraph);
 else{flow(view,s.labels,()=>clamp(t()/Math.max(1,s.duration-5))*s.labels.length,mode);view.add(label(s.note,0,320,32,C.muted));}
 if(mode==='footage')view.add(new Rect({x:0,y:-432,width:1920,height:216,fill:'#000000ed'}));
 view.add(label('얌얌코딩  /  게임과 개발',-590,-486,25,C.muted,650));
 view.add(label('AI 시대, 개발자의 실력',610,-486,25,C.muted,650));
 view.add(label(s.heading,0,-385,61,C.yellow,1770));
 // QA page only; final clean frames never carry a subtitle overlay.
 if(typeof window!=='undefined'&&new URLSearchParams(window.location.search).get('captions')==='1'){
  const caption=new CaptionBox({y:430});view.add(caption);
  caption.text(()=>{const line=s.paragraphs[paragraph()];const pieces=line.text.match(/.{1,52}(?:\s|$)/g)||[line.text];const i=Math.min(pieces.length-1,Math.floor(clamp((t()-line.start)/(line.end-line.start))*pieces.length));return pieces[i];});
 }
 yield* tween(s.duration,v=>t(v*s.duration));
}
