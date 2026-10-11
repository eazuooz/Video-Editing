import {Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

export function seriesSynthesisModel(){
 const node=new Node({}),mode=createSignal(0),p=createSignal(0);
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string,x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 const a=layer(0),as=depthSpace(()=>18,[0,110],1),overview=['그림자 / 가시성','표본 / 재구성','프레임 검사'];
 for(let i=0;i<3;i++){const x=(i-1)*550;a.add(as.box(x,0,0,390,330,60,[P.surfaceTop,P.teal,P.orange][i]));a.add(text(overview[i],x,-230,32,P.yellow));if(i<2)a.add(as.path(()=>[[x+235,0,115],[x+315,0,115]],P.yellow,p));}
 a.add(text('마지막 픽셀은 무엇을 계산하고 무엇을 복원할까?',0,285,32));
 note(a,'먼저 그림자 메모리 배정 → 표본과 복원의 역할 → 실제 자료 검사');

 const b=layer(1),bs=depthSpace(()=>15,[0,115],1),eras=['밝기 숫자','베이크','실시간 그림자','화면 / 격자','레이 / 캐시','복원'];
 for(let i=0;i<6;i++){const x=-650+i*260;b.add(bs.box(x,0,0,180,230,25+i*15,i%2?P.teal:P.surfaceTop));b.add(bs.label(eras[i],x,0,160,26));if(i<5)b.add(bs.path(()=>[[x+110,0,95],[x+150,0,95]],P.orange,p));}
 b.add(text('기술은 한꺼번에 교체되지 않고 함께 사용',0,285,33,P.yellow));
 note(b,'연도 하나로 모든 게임의 구현이 바뀌었다고 해석하지 않음');

 const c=layer(2),cs=depthSpace(()=>18,[0,115],1),data=['밝기','표면 속성','깊이','삼각형 신원','공간의 빛','history'];
 for(let i=0;i<6;i++){const x=-520+(i%3)*520,y=-100+Math.floor(i/3)*230;c.add(cs.box(x,y,0,340,150,40+i*8,i%2?P.teal:P.surfaceTop));c.add(cs.label(data[i],x,y,100,28));c.add(cs.box(x+130,y,50,30,65,()=>15+35*p(),P.orange));}
 c.add(text('1. 무엇을 저장하나?',0,290,36,P.yellow));
 note(c,'서로 다른 정보는 뒤 단계에서 대답할 수 있는 질문도 다름');

 const d=layer(3),ds=depthSpace(()=>18,[0,115],1);
 d.add(ds.box(-540,0,0,330,330,20,P.surfaceTop));
 for(let i=0;i<4;i++)d.add(ds.box((i%2-.5)*100,(Math.floor(i/2)-.5)*100,20,85,85,70,P.teal));
 d.add(ds.polygon(()=>[[420,100,25],[650,100,25],[520,-130,150]],P.orange));
 for(const x of[-540,0,540])d.add(ds.path(()=>[[x,230,45],[x,0,100]],P.yellow,p));
 d.add(text('화면 깊이',-540,-230,32));d.add(text('공간 표현',0,-230,32));d.add(text('삼각형',540,-230,32));
 d.add(text('2. 어디를 검사하나?',0,290,36,P.yellow));
 note(d,'화면 밖 · 가려진 면 · 얇은 구조의 한계는 검사 대상과 연결');

 const e=layer(4),es=depthSpace(()=>18,[0,115],1),reuse=['표본','페이지','캐시','이전 프레임'];
 for(let i=0;i<4;i++){const x=-570+i*380;e.add(es.box(x,0,0,270,280,35,P.surfaceTop));e.add(es.box(x,0,40,100,100,()=>30+80*p(),i%2?P.orange:P.teal));e.add(es.label(reuse[i],x,0,180,30));}
 e.add(text('3. 얼마나 계산하고 어떻게 재사용하나?',0,290,34,P.yellow));
 note(e,'자료·표본·하드웨어·재구성의 선택마다 비용과 오류가 다름');

 const f=layer(5),fs=depthSpace(()=>18,[0,110],1);
 for(const[x,t,col]of[[-550,'저장',P.teal],[0,'검사',P.surfaceTop],[550,'계산 / 재사용',P.orange]]as[number,string,string][]){f.add(fs.box(x,0,0,370,330,80,col));f.add(text(t,x,-230,34,P.yellow));}
 f.add(fs.path(()=>[[-325,0,125],[-225,0,125]],P.yellow,p));f.add(fs.path(()=>[[225,0,125],[325,0,125]],P.yellow,p));
 f.add(text('좋아 보이는 이유와 깨지는 이유를 함께 설명',0,285,32));
 note(f,'기술 이름을 넘어 화면을 만든 자료와 계산의 연결을 확인');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);p(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),p(v.progress,seconds,linear));}};
}
