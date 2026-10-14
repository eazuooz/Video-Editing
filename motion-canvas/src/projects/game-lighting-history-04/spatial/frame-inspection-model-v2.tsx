import {Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Resource relationships and numeric examples only; never imitate a recorded RenderDoc UI.
export function frameInspectionModel(){
 const node=new Node({}),mode=createSignal(0),p=createSignal(0);
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 const a=layer(0),as=depthSpace(()=>16,[0,100],1);
 for(const[x,t,col]of[[-540,'생성 명령',P.orange],[0,'자원',P.teal],[540,'소비 명령',P.surfaceTop]]as[number,string,string][]){a.add(as.box(x,0,0,360,280,65,col));a.add(text(t,x,-230,33,P.yellow));}
 a.add(as.path(()=>[[-325,0,105],[-215,0,105]],P.orange,p));a.add(as.path(()=>[[215,0,105],[325,0,105]],P.teal,p));
 a.add(text('한 프레임에서 명령 ↔ 자료의 연결을 추적',0,285,32));
 note(a,'엔진 이름만으로 구조를 확정하지 않기 · 실제 프레임 캡처와 구별한 역할도');

 const b=layer(1),bs=depthSpace(()=>16,[0,100],1);
 for(const x of[-540,0,540])b.add(bs.box(x,0,0,350,290,20,P.surfaceTop));
 b.add(bs.box(-590,-40,25,70,90,65,P.orange));b.add(bs.path(()=>[[-590,-40,105],[-340,-40,105]],P.red,p));
 for(let i=0;i<4;i++)b.add(new Node({opacity:()=>i===2?.3+.7*p():1,children:[bs.box((i%2-.5)*120,(Math.floor(i/2)-.5)*110,25,100,90,35,i===2?P.orange:P.teal)]}));
 for(let i=0;i<3;i++)b.add(bs.box(450+i*85,-60+i*70,25+i*25,65,65,35,[P.orange,P.teal,P.green][i]));
 b.add(text('화면 밖 반사?',-540,-230,32,P.yellow));b.add(text('페이지 갱신?',0,-230,32,P.yellow));b.add(text('G-buffer 속성?',540,-230,32,P.yellow));
 b.add(text('먼저 질문 → 볼 자원과 이벤트 선택',0,285,32));
 note(b,'상태를 임의로 단정하지 않고 실제 입력과 출력에서 확인할 질문을 정함');

 const c=layer(2),cs=depthSpace(()=>16,[0,100],1),conds=['엔진 / API','렌더 경로','내부 / 출력 해상도','카메라','기능 설정','노출 / 캐시'];
 for(let i=0;i<6;i++){const x=-520+(i%3)*520,y=-120+Math.floor(i/3)*230;c.add(cs.box(x,y,0,350,150,35,P.surfaceTop));c.add(cs.label(conds[i],x,y,90,27));c.add(cs.box(x+155,y,45,30,60,()=>20+35*p(),P.teal));}
 c.add(text('같은 조건을 먼저 잠그고 한 변수씩 비교',0,285,32,P.yellow));
 note(c,'조건표는 측정 전에 기록 · 다른 API와 다른 해상도의 차이를 기능 하나의 효과로 단정하지 않음');

 const d=layer(3),ds=depthSpace(()=>18,[0,120],1);
 const counts=[4,2,1],xs=[-530,0,530];
 for(let k=0;k<3;k++){
  const n=counts[k],step=280/n;d.add(ds.box(xs[k],0,0,330,330,15,P.surfaceTop));
  for(let j=0;j<n;j++)for(let i=0;i<n;i++)d.add(ds.box(xs[k]+(i-(n-1)/2)*step,(j-(n-1)/2)*step,()=>20+k*30*p(),step-5,step-5,15,P.teal));
  d.add(text('mip '+k+' · '+n+'×'+n,xs[k],-230,30,P.yellow));
 }
 d.add(text('크기 · 형식 · 배열 층 · 밉 수준',0,285,33));
 note(d,'밉의 단순 수치 예 · 층/깊이/큐브면 선택과 해상도 변경을 구별');

 const e=layer(4),es=depthSpace(()=>18,[0,100],1),zs=[1,2,10,100];
 for(let i=0;i<4;i++){
  const x=-600+i*400,dep=100/99-100/(99*zs[i]);
  e.add(es.box(x,0,0,250,280,20,P.surfaceTop));
  e.add(new Node({opacity:()=>.25+.75*(1-p()),children:[es.box(x-55,0,20,60,110,170*dep,P.teal)]}));
  e.add(new Node({opacity:p,children:[es.box(x+55,0,20,60,110,170*(1-dep),P.orange)]}));
  e.add(text('z = '+zs[i],x,-230,30,P.yellow));
  e.add(text('d='+dep.toFixed(3)+'\n1−d='+(1-dep).toFixed(3),x,275,27));
 }
 e.add(text('near=1, far=100 · d=100/99−100/(99z)',0,-275,30,P.teal));
 note(e,'유한한 [0,1] 투영의 독립 예 · 역방향과 부동소수점 형식의 관계는 별도 확인');

 const f=layer(5),fs=depthSpace(()=>18,[0,125],1);
 f.add(fs.box(-420,0,0,420,320,35,P.surfaceTop));f.add(fs.path(()=>[[-420,0,35],[-420,0,220]],P.teal,p));
 f.add(fs.box(430,0,0,420,320,35,'#8080ff'));
 f.add(text('법선 n = (0,0,1)',-420,-230,33,P.yellow));f.add(text('표시 RGB = (n+1)/2',430,-230,33,P.yellow));
 f.add(text('(0.5, 0.5, 1.0) ≠ 표면의 albedo',0,285,32));
 note(f,'일반적인 법선 시각화 예 · 실제 G-buffer의 압축/채널 배치는 엔진 문서와 대조');

 const g=layer(6),gs=depthSpace(()=>18,[0,105],1);
 g.add(gs.box(-500,80,0,420,330,20,P.surfaceTop));g.add(gs.box(500,0,0,420,330,20,P.teal));
 g.add(gs.box(-500,80,25,45,45,45,P.orange));g.add(gs.box(430,-70,25,70,70,65,P.orange));
 g.add(gs.path(()=>[[-500,80,95],[160,-20,155],[430,-70,95]],P.yellow,p));
 g.add(text('표면 위치',-500,-230,33,P.yellow));g.add(text('광원 공간의 깊이',500,-230,33,P.yellow));
 g.add(text('lightMatrix × position → 깊이 비교',0,285,32));
 note(g,'변환과 비교를 구별 · bias / 캐스케이드 / 가상 페이지 선택은 실제 소비 패스에서 확인');

 const h=layer(7),hs=depthSpace(()=>18,[0,110],1);
 h.add(hs.box(-340,0,0,620,420,20,P.surfaceTop));h.add(hs.box(-500,100,25,80,80,45,P.teal));
 h.add(hs.box(570,-120,0,180,200,65,P.orange));h.add(hs.box(570,180,0,180,130,80,P.green));
 h.add(hs.path(()=>[[-500,100,75],[-40,-40,75]],P.teal,p));h.add(hs.path(()=>[[-40,-40,75],[570,-120,100]],P.orange,p));h.add(hs.path(()=>[[-40,-40,75],[570,180,115]],P.green,p));
 h.add(text('화면 깊이의 경계',-350,-230,33,P.yellow));h.add(text('대체 추적 / 프로브',520,-230,31,P.yellow));
 h.add(text('SSR 결과와 실패 지점의 대체 입력을 따로 추적',0,285,31));
 note(h,'지원하는 실제 경로에서 선택 관계 확인 · 모든 반사가 동일한 추적으로 만들어졌다고 단정하지 않음');

 const i=layer(8),is=depthSpace(()=>18,[0,125],1);
 for(let z=0;z<2;z++)for(let y=0;y<2;y++)for(let x=0;x<3;x++)i.add(new Node({opacity:()=>.35+.4*p(),children:[is.box(-600+x*105,-80+y*100,z*95,90,85,80,P.teal)]}));
 i.add(is.path(()=>[[-660,200,80],[-315,-120,160]],P.orange,p));
 for(const[x,t]of[[120,.8],[520,.5]]as[number,number][]){i.add(is.box(x,0,0,200,260,()=>30+150*t, P.orange));i.add(text('T = '+t,x,-230,32,P.yellow));}
 i.add(text('누적 T = 0.8 × 0.5 = 0.4',340,285,31));
 note(i,'T *= exp(−σ Δx) · 공간의 밀도/조명과 시선 방향의 투과율 누적을 구별하는 수치 예');

 const j=layer(9),js=depthSpace(()=>18,[0,115],1);
 for(const[x,t]of[[-480,'이전 프레임 읽기'],[480,'현재 입력 / 다음 기록']]as[number,string][]){j.add(js.box(x,0,0,550,340,20,P.surfaceTop));j.add(text(t,x,-230,31,P.yellow));}
 j.add(new Node({opacity:.4,children:[js.box(-480,0,25,90,90,90,P.orange)]}));j.add(js.box(()=>340+280*p(),0,25,90,90,90,P.teal));
 j.add(js.path(()=>[[-145,0,145],[145,0,145]],P.orange,p));
 j.add(text('움직임 · 깊이 · 가림 변화로 history 검증',0,285,31));
 note(j,'한 캡처에 없는 이전 조건은 해석 범위로 남김 · 모든 과거 표본을 그대로 재사용하지 않음');

 const k=layer(10),ks=depthSpace(()=>16,[0,110],1);
 for(const[x,t,col]of[[-550,'톤 매핑 전 HDR',P.orange],[0,'복원 / 변환',P.teal],[550,'표시 색 + UI',P.surfaceTop]]as[number,string,string][]){k.add(ks.box(x,0,0,360,300,60,col));k.add(text(t,x,-230,30,P.yellow));}
 k.add(ks.box(620,70,65,180,50,30,P.ink));k.add(ks.path(()=>[[-335,0,105],[-215,0,105]],P.orange,p));k.add(ks.path(()=>[[215,0,105],[335,0,105]],P.teal,p));
 k.add(text('실제 자원에서 전후를 비교 · 순서는 엔진별 확인',0,285,31));
 note(k,'역할 연결도이며 공통 파이프라인 명세가 아님 · 준비된 도식을 캡처 결과로 표시하지 않음');

 const l=layer(11),ls=depthSpace(()=>18,[0,115],1);
 l.add(ls.box(-540,0,0,290,300,70,P.orange));l.add(ls.box(0,0,0,360,300,55,P.teal));
 for(const[y,t]of[[-170,'소비 A'],[170,'소비 B']]as[number,string][]){l.add(ls.box(540,y,0,290,190,55,P.surfaceTop));l.add(ls.label(t,540,y,115,30));l.add(ls.path(()=>[[210,0,125],[360,y,125]],P.teal,p));}
 l.add(ls.path(()=>[[-360,0,125],[-210,0,125]],P.orange,p));l.add(text('생성',-540,-230,34,P.yellow));l.add(text('공유 자원',0,-230,34,P.yellow));
 l.add(text('출력의 생성자 → 둘 이상의 소비자',0,285,32));
 note(l,'사용 관계를 추적해 역할 확인 · 이름만 다르다고 독립 자료라고 가정하지 않음');

 const m=layer(12),ms=depthSpace(()=>18,[0,115],1);
 for(const[x,t,col]of[[-440,'구조 검사 캡처',P.surfaceTop],[440,'동일 조건 반복 측정',P.teal]]as[number,string,string][]){m.add(ms.box(x,0,0,570,340,25,col));m.add(text(t,x,-230,33,P.yellow));}
 for(let q=0;q<3;q++)m.add(ms.box(-600+q*145,0,30,100,220,45+q*12,P.orange));
 for(let q=0;q<5;q++)m.add(ms.box(245+q*95,0,30,65,220,()=>50+15*(q%2)+10*p(),P.orange));
 m.add(text('캡처 비용과 실제 패스 성능을 섞지 않기',0,285,32));
 note(m,'막대 높이는 역할 구분용 · 측정값이나 GPU 프로파일러 화면을 재현한 것이 아님');

 const n=layer(13),ns=depthSpace(()=>16,[0,130],1),samples=[8,10,9,11,8,10];
 n.add(ns.box(0,0,0,1500,380,20,P.surfaceTop));
 for(let q=0;q<6;q++){const x=-600+q*240;n.add(new Node({opacity:()=>Math.max(0,Math.min(1,p()*6-q)),children:[ns.box(x,0,20,100,170,samples[q]*12,P.teal)]}));n.add(text(samples[q]+' ms',x,250,28));}
 n.add(text('예시 N=6 · 평균 9.33 ms · 범위 8~11 ms',0,-230,33,P.yellow));
 n.add(text('같은 높이 단위 · 0 ms 기준에서 비교',0,-185,25,P.muted));
 n.add(text('평균과 실행 횟수, 변동을 함께 보고',0,305,32));
 note(n,'가상 수치 예 · 실제 측정에서는 준비/로딩/캐시/카메라 조건과 제외 구간을 기록');

 const o=layer(14),os=depthSpace(()=>18,[0,115],1);
 for(const[x,t,col]of[[-460,'화면 관찰',P.orange],[460,'구현 확인 근거',P.teal]]as[number,string,string][]){o.add(os.box(x,0,0,590,350,25,col));o.add(text(t,x,-230,34,P.yellow));}
 o.add(os.box(-500,0,30,160,180,65,P.surfaceTop));o.add(os.path(()=>[[-500,0,125],[-320,0,125]],P.yellow,p));
 o.add(os.box(380,0,30,160,180,65,P.surfaceTop));o.add(os.box(600,0,30,100,180,65,P.surfaceTop));o.add(os.path(()=>[[480,0,135],[530,0,135]],P.yellow,p));
 o.add(text('보인 변화와 원인을 확인한 범위를 나누어 기록',0,285,31));
 note(o,'최종 이미지 하나만으로 내부 구현·성능·정확성을 증명하지 않음');
 const poses=Array.from({length:15},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);p(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),p(v.progress,seconds,linear));}};
}
