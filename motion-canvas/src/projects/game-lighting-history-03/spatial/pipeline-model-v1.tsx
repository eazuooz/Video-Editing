import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Independent grids show work categories, never a measured engine speedup.
export function pipelineModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const text=(t:string|(()=>string),x:number,y:number,size=29,color:string=P.ink)=>new Txt({text:t,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const grid=(n:Node,s:ReturnType<typeof depthSpace>,count:number,spacing:number)=>{for(let j=0;j<count;j++)for(let i=0;i<count;i++)n.add(s.box((i-(count-1)/2)*spacing,(j-(count-1)/2)*spacing,0,spacing-5,spacing-5,14,P.surfaceTop));};
 const m0=layer(0),s0=depthSpace(()=>22,[0,110],.95);
 for(let group=0;group<4;group++){
  const x=-360+group*240,n=new Node({opacity:()=>group===3?1-progress()*.8:1});
  n.add(s0.box(x,0,0,190,170,18,group===3?P.muted:P.surfaceTop));
  for(let k=0;k<3;k++)n.add(s0.polygon(()=>[[x-70+k*50,-55,24],[x-25+k*50,-55,24],[x-48+k*50,55,50]],group===3?P.muted:P.teal));
  n.add(s0.label(`묶음${group+1}`,x,0,95,27));m0.add(n);
 }
 m0.add(text('메시 작업 묶음 → 정점·프리미티브 출력',0,-195,34,P.teal));
 m0.add(text('가시성에 따라 묶음의 작업 조절',0,310,30,P.yellow));
 m0.add(text('메시 처리와 간접광 계산은 서로 다른 작업',0,355,26,P.muted));

 const m1=layer(1),s1=depthSpace(()=>22,[0,100],1);grid(m1,s1,4,100);
 for(let j=0;j<4;j++)for(let i=0;i<4;i++)m1.add(new Circle({position:s1.point((i-1.5)*100,(j-1.5)*100,27),size:18,fill:P.orange,opacity:()=>1-progress()}));
 for(let j=0;j<2;j++)for(let i=0;i<2;i++)m1.add(new Circle({position:s1.point((i-.5)*200,(j-.5)*200,27),size:24,fill:P.teal,opacity:progress}));
 m1.add(text('같은16픽셀 · 셰이딩 빈도만 비교',0,-195,34,P.teal));
 m1.add(text(()=>progress()<.5?'주황: 픽셀마다16평가':'청록: 2×2 묶음별4평가',0,305,31,P.yellow));
 m1.add(text('출력 격자는 그대로 · 점은 독립 평가 위치 도식',0,350,25,P.muted));

 const m2=layer(2),s2=depthSpace(()=>22,[0,105],1.4);grid(m2,s2,2,130);
 for(let j=0;j<2;j++)for(let i=0;i<2;i++){const x=(i-.5)*130,y=(j-.5)*130;m2.add(s2.path(()=>[[0,0,75],[x,y,25]],P.teal,progress));}
 m2.add(new Circle({position:s2.point(0,0,75),size:26,fill:P.orange}));
 m2.add(text('2×2 픽셀 · 한 평가 결과 공유',0,-195,34,P.teal));
 m2.add(text('평가 수를 줄여도 전체 프레임이4배 빨라지는 것은 아님',0,310,28,P.yellow));
 m2.add(text('기기 지원 · 보간 · 미분 · 깊이와 커버리지 조건은 별도',0,355,25,P.muted));

 const wanted=[9,10,17,18,27],m3=layer(3),s3=depthSpace(()=>22,[-390,100],.7),ram=depthSpace(()=>22,[430,125],.9);
 for(let j=0;j<8;j++)for(let i=0;i<8;i++){const id=j*8+i;m3.add(s3.box((i-3.5)*72,(j-3.5)*72,0,66,66,12,wanted.includes(id)?P.orange:P.surfaceTop));}
 for(let i=0;i<5;i++)m3.add(new Node({opacity:()=>progress()>i/5?1:.2,children:[ram.box((i%3-1)*115,(Math.floor(i/3)-.5)*115,0,103,103,25,P.teal),ram.label(String(wanted[i]),(i%3-1)*115,(Math.floor(i/3)-.5)*115,44,26)]}));
 m3.add(text('가상 주소: 큰 텍스처',-390,-195,31,P.orange));m3.add(text('상주 메모리: 필요한 페이지',430,-195,31,P.teal));
 m3.add(text('64페이지 중5개 수요를 보여주는 독립 예',0,315,29,P.yellow));
 m3.add(text('페이지 관리와 내용 생성은 다른 일 · 학습으로 만든 텍스처가 아님',0,360,24,P.muted));

 const m4=layer(4),d=depthSpace(()=>22,[-410,110],1),r=depthSpace(()=>22,[410,110],1);grid(m4,d,2,135);grid(m4,r,2,135);
 for(let j=0;j<2;j++)for(let i=0;i<2;i++){const id=j*2+i,x=(i-.5)*135,y=(j-.5)*135;
  m4.add(d.box(x,y,15,125,125,18,P.orange));
  m4.add(new Node({opacity:()=>progress()>(id+.5)/4?1:0,children:[r.box(x,y,15,125,125,18,P.teal)]}));
 }
 m4.add(text('피드백: 요구된 영역',-410,-195,31,P.orange));m4.add(text('스트리밍: 도착한 데이터',410,-195,31,P.teal));
 m4.add(text(()=>`요구4개 · 이 예의 도착${Math.min(4,Math.floor(progress()*4+.5))}개`,0,310,31,P.yellow));
 m4.add(text('수요 파악 ≠ 즉시 상주 · 지연/메모리/대체 밉을 따로 확인',0,355,25,P.muted));

 const m5=layer(5),a=depthSpace(()=>22,[-540,105],.85),b=depthSpace(()=>22,[0,105],.85),c=depthSpace(()=>22,[540,105],.85);
 for(const ss of[a,b,c])m5.add(ss.box(0,0,0,330,260,15,P.surfaceTop));
 for(let k=0;k<3;k++)m5.add(a.polygon(()=>[[-120+k*85,-70,20],[-45+k*85,-70,20],[-85+k*85,80,90]],P.teal));
 for(let j=0;j<2;j++)for(let i=0;i<2;i++)m5.add(new Circle({position:b.point((i-.5)*140,(j-.5)*140,40),size:26,fill:P.orange}));
 for(let k=0;k<3;k++)m5.add(new Node({opacity:()=>k===2?1-progress()*.8:1,children:[c.box(-100+k*100,0,16,86,100,35,P.green)]}));
 m5.add(text('기하 묶음',-540,-195,31,P.teal));m5.add(text('셰이딩 빈도',0,-195,31,P.orange));m5.add(text('텍스처 페이지',540,-195,31,P.green));
 m5.add(text('서로 다른 자원을 줄이는 선택',0,310,33,P.yellow));
 m5.add(text('Nanite · VRS · DLSS를 하나의 해상도 기능으로 합치지 않기',0,355,25,P.muted));
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
