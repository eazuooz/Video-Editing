import {makeScene2D,Video,Txt,Rect,Line,Circle,Node} from '@motion-canvas/2d';
import {createSignal,tween,Vector2} from '@motion-canvas/core';
import {CaptionBox} from '../../game-dev-career/preview/caption-box';
import capture from '../../../../../shared/output/ai-game-development-human-craft/unity-sample/capture.json';

const C={yellow:'#e8cf83',teal:'#73c7c2',red:'#ef8585',ink:'#f5f5f5',muted:'#b8b8b8'};
const font="'Noto Sans KR', 'Malgun Gothic', sans-serif";
export default makeScene2D(function*(view){
 view.fill('#000');
 const t=createSignal(0),second=()=>t()>=11,local=()=>second()?t()-11:t();
 const state=()=>capture.timeline[Math.min(1559,Math.floor(t()*60))];
 const color=()=>state().result==='purchased'?C.teal:state().result==='insufficient-gold'?C.red:C.yellow;
 const phase=()=>t()<11?'01  정상 구매':t()<22?'02  골드 부족':'03  개발자가 정할 조건';
 const text=(text:any,x:number,y:number,size=32,fill:any=C.ink,weight=500)=>new Txt({text,x,y,fontSize:size,fontFamily:font,fill,fontWeight:weight});
 view.add(text('AI와 게임 개발  /  Unity 애니메이션 시안',-540,-479,25,C.muted));
 view.add(text('자체 제작 엔진 시연 · 설명용 수치',605,-479,24,C.muted));
 view.add(text(()=>t()<22?'같은 구매 요청, 다른 결과':'작동하는 코드에서 완성된 기능으로',0,-397,57,C.yellow,700));
 view.add(text(()=>t()<22?'캐릭터 동작과 실제 구매 조건을 함께 확인합니다.':'무엇을 허용하고, 무엇을 막을지 정해야 합니다.',0,-326,30));
 view.add(new Line({points:[[-850,-280],[850,-280]],stroke:'#343b3f',lineWidth:2}));
 view.add(<Video src="/@fs/D:/Github/VideoEditing/shared/output/ai-game-development-human-craft/unity-sample/unity-shop-v1.mp4"
   x={-300} y={30} width={1200} height={675} time={()=>t()} />);
 view.add(text(phase,-570,-242,31,()=>t()>=22?C.yellow:color(),700));
 view.add(text('물약 가격  30 G',-310,253,32,C.yellow,700));
 // Camera viewport anchors are exported by Unity per frame; this video has no crop.
 const hero=()=>new Vector2(-900+state().heroX/1920*1200,-307.5+state().heroY/1080*675);
 const target=()=>new Vector2(-900+state().potionX/1920*1200,-307.5+state().potionY/1080*675);
 const visible=()=>local()>=4.35&&local()<7.5;
 const progress=()=>Math.max(0,Math.min(1,(local()-4.6)/1));
 const arrow=new Line({points:()=>{const h=hero(),p=target();return [h.add([0,-80]),h.add([0,-150]),p.add([0,-150]),p.add([0,-35])];},stroke:color,lineWidth:7,radius:22,endArrow:true,arrowSize:17,end:progress,opacity:()=>visible()?1:0});view.add(arrow);
 view.add(new Circle({position:()=>target(),size:()=>state().result==='purchased'?60:68,stroke:color,lineWidth:4,opacity:()=>visible()&&progress()>=1?1:0}));
 view.add(text(()=>local()<3.6?'상점으로 이동':local()<4.6?'물약 선택':state().result==='purchased'?'구매 완료':state().result==='insufficient-gold'?'구매 거절':'구매 요청',35,-195,30,color,700));
 // Right panel always displays the executed C# state, not an animation counter.
 view.add(new Rect({x:632,y:15,width:430,height:532,fill:'#0e171b',stroke:color,lineWidth:2,radius:18}));
 view.add(text('구매 상태',632,-192,30,C.muted));
 view.add(text(()=>`${state().gold} G`,632,-107,72,color,700));
 view.add(text('남은 골드',632,-46,28,C.muted));
 view.add(new Line({points:[[465,7],[800,7]],stroke:'#364447',lineWidth:2}));
 view.add(text(()=>`아이템  ${state().inventory} 개`,632,60,39,C.ink,700));
 view.add(text(()=>state().result==='purchased'?'100 − 30 = 70':state().result==='insufficient-gold'?'20 < 30  →  거절':'가격과 잔액 확인',632,134,28,color));
 view.add(text(()=>state().result==='purchased'?'골드 차감 + 아이템 지급':state().result==='insufficient-gold'?'골드·아이템 모두 유지':'골드 ≥ 30 일 때만 구매',632,199,24,C.muted));
 const takeaway=new Rect({x:-300,y:335,width:1110,height:80,fill:'#102520',stroke:C.teal,lineWidth:2,radius:10,opacity:()=>t()>=22?1:0});view.add(takeaway);takeaway.add(text('조건 확인  →  구매 처리  →  결과 검증',0,0,34,C.teal,700));
 const caption=new CaptionBox({y:430});view.add(caption);
 caption.text(()=>t()<3.2?'게임 속 상점을 예로 들어 보겠습니다.':t()<6?'AI에게 골드로 아이템을 구매하는 기능을 만들어 달라고 요청했습니다.':t()<9?'버튼을 누르면 골드가 줄고 아이템이 들어옵니다.':t()<11?'한 번 눌러 봤을 때는 잘 작동합니다.':t()<16.6?'그런데 골드가 부족하면 어떻게 될까요?':t()<22?'구매를 거절하고, 골드와 아이템을 그대로 유지해야 합니다.':'바로 여기서 개발자의 이해가 필요합니다.');
 yield* tween(26,v=>t(v*26));
});
