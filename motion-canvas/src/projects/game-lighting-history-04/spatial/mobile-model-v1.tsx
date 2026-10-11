import {Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// Engine-document-based explanatory geometry; no captured mobile frame or timing claim.
export function mobileModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,24,P.muted));
 const a=layer(0),s=depthSpace(()=>12,[0,165],1);
 for(let r=0;r<3;r++)for(let c=0;c<4;c++){const selected=r===1&&c===2;a.add(s.box(-590+c*105,-120+r*105,0,94,94,selected?()=>25+50*p():15,selected?P.orange:P.surfaceTop));}
 a.add(s.label('타일 기반 GPU',-440,205,60,32,P.yellow));a.add(s.box(110,0,0,250,220,45,P.teal));a.add(s.label('내부 메모리',110,0,95,29));
 a.add(s.path(()=>[[-300,0,75],[-35,0,75]],P.orange,p));
 for(const[x,t,col]of[[470,'재질 / G-buffer',P.surfaceTop],[760,'조명',P.teal]]as[number,string,string][]){a.add(s.box(x,0,0,245,220,45,col));a.add(s.label(t,x,0,95,27));}
 a.add(s.path(()=>[[610,0,85],[625,0,85]],P.yellow,p));
 a.add(text('하드웨어: 작은 영역을 가까운 메모리에서',-380,-215,29,P.orange));a.add(text('파이프라인: 어떤 자료를 언제 계산할까?',435,-215,29,P.yellow));note(a,'하드웨어의 저장 방식과 셰이딩 패스 순서는 별개의 선택');

 const b=layer(1),bs=depthSpace(()=>8,[0,190],1);
 const labels=[['타일 GPU / Forward',-410,-110,P.teal],['타일 GPU / Deferred',410,-110,P.orange],['Forward+ 조명 목록',-410,140,P.surfaceTop],['하드웨어 타일 저장',410,140,P.surfaceTop]]as[string,number,number,string][];
 for(const[t,x,y,col]of labels){b.add(bs.box(x,y,0,660,170,50,col));b.add(bs.label(t,x,y,95,29));}
 b.add(bs.path(()=>[[-65,140,100],[65,140,100]],P.red,p));b.add(text('목록의 타일 ≠ 하드웨어 내부 저장',0,315,31,P.yellow));note(b,'같은 화면 분할 용어라도 역할·수명·저장 위치를 따로 확인');

 const c=layer(2),cs=depthSpace(()=>15,[0,165],1);
 c.add(cs.box(-130,0,0,970,460,20,P.surfaceFront));c.add(cs.label('GPU 타일 메모리',-130,-190,65,34,P.yellow));
 for(const[x,t,col]of[[-440,'기하 패스',P.surfaceTop],[-130,'G-buffer',P.orange],[180,'조명 패스',P.teal]]as[number,string,string][]){c.add(cs.box(x,0,22,265,220,45,col));c.add(cs.label(t,x,0,105,29));}
 c.add(cs.path(()=>[[-285,0,105],[-285+50*p(),0,105]],P.yellow));c.add(cs.path(()=>[[25,0,105],[25+50*p(),0,105]],P.yellow));
 c.add(cs.box(650,0,0,380,320,35,P.surfaceTop));c.add(cs.label('외부 메모리',650,0,85,30));c.add(cs.path(()=>[[650,130,90],[180,130,90]],P.muted,()=>1-p(),[12,10]));
 c.add(text('지원 경로: 중간 속성을 타일 안에서 소비',0,-235,33,P.yellow));c.add(text('중간 자료의 외부 쓰기 → 다시 읽기 감소',0,295,30,P.teal));note(c,'최종 색 출력까지 외부 메모리를 전혀 쓰지 않는다는 의미는 아님');

 const d=layer(3),ds=depthSpace(()=>12,[0,180],1);
 d.add(ds.box(-520,0,0,470,350,45,P.teal));d.add(ds.label('타일의 중간 자료',-520,0,100,29));d.add(ds.box(520,0,0,470,350,45,P.orange));d.add(ds.label('저장 / 외부 읽기',520,0,100,29));
 d.add(ds.path(()=>[[-255,0,100],[255,0,100]],P.orange,p));
 for(const[x,t]of[[-500,'API / 기기'],[0,'패스 연결'],[500,'메모리 지원']]as[number,string][]){d.add(ds.box(x,-350,0,360,100,35,P.surfaceTop));d.add(ds.label(t,x,-350,75,26));}
 d.add(text(()=>p()<.5?'지원되는 타일 내부 소비':'패스 분리·저장 요구: 외부 대역폭 사용 가능',0,295,31,P.yellow));note(d,'iOS·Vulkan subpass·GLES 확장 및 기기 지원은 실제 대상에서 확인');

 const e=layer(4),es=depthSpace(()=>15,[0,190],1);
 e.add(es.box(-570,0,0,400,360,40,P.surfaceTop));e.add(es.label('불투명 표면',-570,0,95,30));
 e.add(es.box(-30,-105,20,350,160,35,P.teal));e.add(es.label('불투명 G-buffer',-30,-105,100,27));
 e.add(es.path(()=>[[-345,-80,100],[-220,-80,100]],P.teal,p));
 const layers=new Node({});e.add(layers);for(const[z,col]of[[20,P.blue],[100,P.red],[180,P.teal]]as[number,string][]){const n=new Node({opacity:.6});n.add(es.box(580,0,z,330,230,20,col));layers.add(n);}
 e.add(es.label('여러 투명 층',580,0,270,31));e.add(es.path(()=>[[195,140,100],[380,140,100]],P.orange,p));e.add(text('투명 효과: 별도 Forward 경로',250,295,32,P.orange));note(e,'한 불투명 표본의 속성만으로 뒤의 여러 투명 기여를 복원할 수 없음');

 const f=layer(5),ss=depthSpace(()=>8,[0,165],1);
 for(const[x,t,col]of[[-540,'Forward',P.teal],[540,'Deferred',P.orange]]as[number,string,string][]){f.add(ss.box(x,0,0,480,350,60,col));f.add(ss.label(t,x,0,125,34));}
 for(const[y,t]of[[-150,'재질 · 광원'],[0,'투명 효과'],[150,'대역폭 · 기기']]as[number,string][]){f.add(ss.box(0,y,0,370,95,35,P.surfaceTop));f.add(ss.label(t,0,y,75,28));}
 f.add(ss.path(()=>[[-200,0,100],[-285,0,100]],P.teal,p));f.add(ss.path(()=>[[200,0,100],[285,0,100]],P.orange,p));f.add(text('같은 엔진 안에서도 경로가 공존',0,295,33,P.yellow));note(f,'승자/패자 순위 대신 대상 기기와 실제 패스·재질·메모리 조건으로 비교');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
