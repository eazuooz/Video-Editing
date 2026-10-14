import {Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// Independent projected examples. No sample execution, captured GPU resource,
// universal bit layout or performance measurement is represented here.
export function visibilityModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,24,P.muted));
 const tri=(n:Node,s:ReturnType<typeof depthSpace>,x:number,y:number,z:number,c:string)=>{const pts:V3[]=[[x-150,y+100,z],[x+150,y+100,z],[x-150,y-180,z]];n.add(s.polygon(()=>pts,c));n.add(s.polygon(()=>[[x-150,y+100,z-22],[x+150,y+100,z-22],[x+150,y+100,z],[x-150,y+100,z]],P.surfaceFront));return pts;};
 const a=layer(0),as=depthSpace(()=>16,[0,170],1);
 for(let i=0;i<3;i++){a.add(as.box(-470,-100+i*120,0,400,90,24,[P.teal,P.orange,P.surfaceTop][i]));a.add(as.label(['깊이','법선','재질'][i],-470,-100+i*120,50,30));}
 a.add(as.box(470,40,0,400,260,28,P.teal));a.add(as.label('객체 / 삼각형 ID',470,40,60,29));
 a.add(as.path(()=>[[-210,40,60],[220,40,60]],P.yellow,p));
 a.add([text('속성들을 저장',-470,-200,32,P.muted),text('보인 표면의 신원을 저장',470,-200,32,P.yellow),text('신원 ≠ 조명 결과',0,295,34,P.ink)]);note(a,'저장 선택 비교 · 버퍼 수와 크기는 구현별로 확인');

 const b=layer(1),bs=depthSpace(()=>15,[0,180],1);
 b.add(bs.box(-570,0,0,300,230,35,P.teal));b.add(bs.label('객체 2 / 삼각형 7',-570,0,65,26));tri(b,bs,20,0,40,P.surfaceTop);
 for(const[x,y,t]of[[-130,100,'A'],[170,100,'B'],[-130,-180,'C']]as[number,number,string][]){b.add(bs.box(x,y,40,22,22,()=>25+55*p(),P.orange));b.add(bs.label(t,x,y,145,29,P.orange));}
 b.add(bs.box(570,0,0,310,230,35,P.orange));b.add(bs.label('속성 복원 → 셰이딩',570,0,65,26));
 b.add(bs.path(()=>[[-390,0,75],[-220,0,75]],P.yellow,p));b.add(bs.path(()=>[[230,0,75],[385,0,75]],P.yellow,p));
 b.add(text('ID → 원래 꼭짓점·재질 데이터 → 필요한 속성',0,-200,31,P.yellow));note(b,'메시 데이터 접근과 복원 계산이 뒤 단계의 책임');

 const c=layer(2),cs=depthSpace(()=>10,[-310,165],1.25);tri(c,cs,0,0,50,P.surfaceTop);
 const wa=()=>.2+.3*p(),wb=()=>.3-.2*p(),wc=()=>1-wa()-wb();
 const px=()=>-150*wa()+150*wb()-150*wc(),py=()=>100*wa()+100*wb()-180*wc();
 c.add(cs.box(px,py,50,24,24,65,P.orange));c.add(cs.label('표본',px,py,135,28,P.orange));
 c.add(cs.label('A · UV(0,0)',-150,100,10,27));c.add(cs.label('B · UV(1,0)',150,100,10,27));c.add(cs.label('C · UV(0,1)',-150,-180,90,27));
 c.add(text('삼각형 7의 속성 보간',420,-180,34,P.yellow));c.add(text(()=>`가중치: ${wa().toFixed(2)} / ${wb().toFixed(2)} / ${wc().toFixed(2)}`,420,-90,29));c.add(text(()=>`UV = (${wb().toFixed(2)}, ${wc().toFixed(2)})`,420,10,35,P.teal));c.add(text('wA + wB + wC = 1',420,100,30,P.ink));
 note(c,'숫자는 이미 투영에 맞게 보정된 가중치의 예 · 단순 화면 선형 보간을 일반화하지 않음');

 const d=layer(3),ds=depthSpace(()=>14,[0,155],1);tri(d,ds,-330,0,25,P.teal);tri(d,ds,330,0,25,P.orange);
 d.add(ds.box(-280,30,25,38,38,65,P.teal));d.add(ds.box(290,30,25,38,38,65,P.orange));
 d.add(ds.path(()=>[[-250,30,110],[250,30,110]],P.red,p));d.add(ds.path(()=>[[-420,30,110],[-290,30,110]],P.teal,p));
 d.add(text('이웃 표본이 다른 삼각형이면?',0,-220,34,P.yellow));d.add(text('경계 너머의 UV 차이를 그대로 미분에 사용하지 않기',0,285,30,P.ink));d.add(text('같은 표면의 미분 복원 규칙 확인 → 밉 선택',0,320,29,P.teal));note(d,'텍스처 좌표 복원과 미분 복원은 서로 다른 검수 항목');

 const e=layer(4),es=depthSpace(()=>14,[0,150],1);
 for(const[x,t,col]of[[-530,'ID 쓰기',P.teal],[0,'기하·속성 읽기',P.orange],[530,'복원·재질·조명',P.surfaceTop]]as[number,string,string][]){e.add(es.box(x,0,0,330,230,()=>35+30*p(),col));e.add(es.label(t,x,0,100,28));}
 e.add(es.path(()=>[[-345,0,70],[-190,0,70]],P.yellow,p));e.add(es.path(()=>[[190,0,70],[345,0,70]],P.yellow,p));
 e.add(text('줄어들 수 있는 임시 저장 · 새로 드는 복원/접근 비용',0,-220,32,P.yellow));e.add(text('자료 배치 · 캐시 · 재질 분기 · 멀티샘플링 조건',0,290,31));note(e,'버퍼가 작아졌다는 사실만으로 전체 프레임 성능을 확정하지 않음');

 const f=layer(5),ss=depthSpace(()=>12,[0,160],1);
 for(const[x,t,col]of[[-530,'가시성/ID',P.teal],[0,'원래 기하 데이터',P.surfaceTop],[530,'Compute 셰이딩',P.orange]]as[number,string,string][]){f.add(ss.box(x,0,0,330,230,55,col));f.add(ss.label(t,x,0,110,28));}
 f.add(ss.path(()=>[[-345,0,95],[-190,0,95]],P.yellow,p));f.add(ss.path(()=>[[190,0,95],[345,0,95]],P.yellow,p));
 f.add(text('Microsoft 공식 샘플의 파이프라인 설명',0,-230,34,P.yellow));f.add(text('GDK 2022 호환 기준 ≠ 기술 최초 발명 연도',0,280,31));f.add(text('Forward 전환 · 객체/삼각형 ID 오버레이',0,320,29,P.teal));note(f,'공식 문서 기반 설명 도식 · 실제 샘플 실행/성능 측정 화면 아님');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls:{mode,progress},poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
