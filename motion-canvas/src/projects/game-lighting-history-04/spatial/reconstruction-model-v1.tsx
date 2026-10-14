import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Independent teaching data, not a vendor model, captured image or benchmark.
export function reconstructionModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 const a=layer(0),as=depthSpace(()=>10,[0,130],1);
 for(const[x,name,kind]of[[-570,'적은 표본: 경계 + 노이즈',0],[0,'무조건 평균: 세부 손실',1],[570,'경계를 고려한 복원',2]]as[number,string,number][]){for(let r=0;r<4;r++)for(let c=0;c<4;c++){const edge=c<2,noise=((r*3+c*5)%4-1.5)*14,base=edge?26:100;a.add(as.box(x+(c-1.5)*70,(r-1.5)*70,0,65,65,()=>kind===0?base+noise:kind===1?base+(63-base)*p():base+noise*(1-p()),edge?P.surfaceTop:P.teal));}a.add(text(name,x,290,27,kind===1?P.red:P.ink));}a.add(text('평균은 노이즈와 실제 경계를 함께 섞을 수 있음',0,-230,33,P.yellow));note(a,'높이는 독립 표본 값 도식 · 실제 게임의 디노이저 결과·화질 비교가 아님');
 const b=layer(1),bs=depthSpace(()=>12,[0,150],1);
 for(const[x,t,c]of[[-620,'이전 프레임',P.surfaceTop],[0,'현재 깊이·법선',P.teal],[620,'유효한 역사만',P.orange]]as[number,string,string][]){b.add(bs.box(x,0,0,450,310,35,c));b.add(text(t,x,290,29,c));}
 for(let i=0;i<6;i++){const invalid=i>=4,col=invalid?P.red:P.green;b.add(bs.box(-750+(i%3)*105,-65+Math.floor(i/3)*110,40,82,82,25,col));b.add(bs.box(490+(i%3)*105,-65+Math.floor(i/3)*110,40,82,82,25,col));if(invalid)b.add(<Line points={()=>[bs.point(490+(i%3)*105-30,-65+Math.floor(i/3)*110,80),bs.point(490+(i%3)*105+30,-65+Math.floor(i/3)*110,80)]} stroke={P.red} lineWidth={6} opacity={()=>p()}/>);}
 b.add(bs.path(()=>[[-355,-150,70],[-235,-150,70]],P.yellow,p));b.add(bs.path(()=>[[235,-150,70],[355,-150,70]],P.yellow,p));b.add(text('재투영 후 표면 일치 검사 · 새로 드러난 영역 제외',0,-230,32,P.yellow));note(b,'화면 좌표가 같아도 같은 표면이라고 단정할 수 없음 · 자료별 판단은 실제 통합에 의존');
 const c=layer(2),cs=depthSpace(()=>10,[0,150],1);
 for(const[x,t,col]of[[-570,'희소 레이 결과',P.surfaceTop],[0,'Ray Reconstruction',P.orange],[570,'복원된 출력',P.teal]]as[number,string,string][]){c.add(cs.box(x,0,0,440,300,65,col));c.add(text(t,x,285,28,col));}c.add(cs.path(()=>[[-325,0,100],[-240,0,100]],P.yellow,p));c.add(cs.path(()=>[[240,0,100],[325,0,100]],P.yellow,p));for(let i=0;i<4;i++)c.add(cs.box(-690+i*80,-90,70,35,35,30,P.yellow));c.add(text('2023 · DLSS3.5: 여러 수작업 디노이저를 대체',0,-230,32,P.yellow));note(c,'게임 입력·통합 의존 · 이 상자는 역할 도식이며 내부 신경망 구조의 재현이 아님');
 const d=layer(3),ds=depthSpace(()=>10,[0,140],1);
 for(const[x,t,col]of[[-600,'SR: 출력 해상도',P.teal],[0,'FG: 표시 프레임',P.orange],[600,'RR: 희소 레이 복원',P.green]]as[number,string,string][]){d.add(ds.box(x,0,0,430,300,45,col));d.add(text(t,x,280,27,col));}
 for(let i=0;i<4;i++)d.add(ds.box(-710+(i%2)*140,-70+Math.floor(i/2)*140,50,110,110,()=>10+25*p(),P.surfaceTop));for(let i=0;i<3;i++)d.add(ds.box(-135+i*135,0,50,95,210,()=>i===1?20+30*p():50,i===1?P.orange:P.surfaceTop));for(let i=0;i<6;i++)d.add(ds.box(480+(i%3)*110,-60+Math.floor(i/3)*120,50,70,70,()=>10+30*p(),i%2?P.green:P.surfaceTop));d.add(text('같은 계열 이름 안에서도 입력·출력은 다름',0,-230,34,P.yellow));note(d,'해상도·노이즈·표시 간격의 역할 구분 · 기능을 동일한 패스로 단정하지 않음');
 const e=layer(4),es=depthSpace(()=>10,[0,145],1);for(const[x,t,col]of[[-440,'정지 비교',P.surfaceTop],[440,'움직임 이후 비교',P.teal]]as[number,string,string][]){e.add(es.box(x,0,0,650,340,30,col));for(let i=0;i<5;i++)e.add(es.box(x-190+i*90,-70,35,12,180,25,P.ink));e.add(es.box(()=>x-180+360*p(),75,40,90,85,70,P.orange));e.add(text(t,x,290,31,col));}e.add(text('가는 선 · 작은 글자 · 새로 드러난 표면',0,-230,34,P.yellow));note(e,'원리 도식 · 안정 시간/잔상/흔들림은 실제 같은 카메라의 영상에서 따로 관찰');
 const f=layer(5),fs=depthSpace(()=>10,[0,150],1);for(const[x,t,col]of[[-460,'기능 OFF',P.surfaceTop],[460,'기능 ON',P.teal]]as[number,string,string][]){f.add(fs.box(x,0,0,650,350,50,col));f.add(text(t,x,285,33,col));}for(const[x,t]of[[-500,'카메라'],[0,'내부 해상도'],[500,'노출·조명']]as[number,string][]){f.add(fs.box(x,-270,0,360,90,25,P.surfaceTop));f.add(text(t,x,-150,28,P.yellow));}f.add(fs.path(()=>[[-100,0,90],[100,0,90]],P.orange,p));f.add(text('다른 조건이 섞이면 기능 하나의 효과로 좁힐 수 없음',0,310,28));note(f,'공식 홍보 비교와 동일 조건의 직접 측정은 별도 · 보편적 품질 우위를 약속하지 않음');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();return{node,poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
