import {Circle, Line, Node, Rect, Txt, Video, View2D} from '@motion-canvas/2d';
import {createSignal, easeInOutCubic, tween, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import manifest from '../../../../../projects/visible-rewards/project.json';
import {STORYBOARD} from '../storyboard';

const clips=import.meta.glob('../assets/gameplay/scene*.mp4',{eager:true,query:'?url',import:'default'}) as Record<string,string>;
class MixedVideo extends Video {
 protected override video():HTMLVideoElement {const el=super.video();el.muted=true;return el;}
}
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const label=(s:string,x:number,y:number,size=34,fill:string=P.ink)=>new Txt({text:s,x,y,fontSize:size,fill,fontFamily:P.font});
function inventory(parent:Node,x:number,y:number,rows:number,active:()=>number) {
 const n=new Node({x,y});parent.add(n);
 for(let i=0;i<rows*6;i++){
  const a=(i%6-2.5)*78,b=(Math.floor(i/6)-(rows-1)/2)*78;
  n.add(<Rect x={a+4} y={b+5} size={66} fill={P.line}/>);
  n.add(<Rect x={a} y={b} size={66} fill={()=>i<active()?P.blueLight:P.background} stroke={P.line} lineWidth={1.5}/>);
  n.add(<Rect x={a} y={b} size={19} rotation={45} fill={P.blue} opacity={()=>clamp(active()-i)}/>);
 }
}
function bag(parent:Node,x:number,y:number,scale=1) {
 const n=new Node({x,y,scale});parent.add(n);
 n.add(<Rect width={110} height={145} x={6} y={8} radius={14} fill={P.line}/>);
 n.add(<Rect width={110} height={145} radius={14} fill={P.blueLight} stroke={P.blue} lineWidth={4}/>);
 n.add(<Rect width={46} height={26} y={-84} radius={7} stroke={P.blue} lineWidth={5}/>);
 n.add(<Rect width={80} height={45} y={25} radius={5} fill={P.background} stroke={P.blue} lineWidth={3}/>);
 n.add(<Line points={[[-50,-30],[50,-30]]} stroke={P.blue} lineWidth={3}/>);
}
function bar(parent:Node,x:number,y:number,w:number,value:()=>number){
 parent.add(<Rect x={x} y={y} width={w} height={38} fill={P.panel} stroke={P.line} lineWidth={1}/>);
 parent.add(<Rect x={()=>x-w/2+w*value()/2} y={y} width={()=>Math.max(.01,w*value())} height={38} fill={P.blue}/>);
}
function arrow(p:Node,x1:number,y1:number,x2:number,y2:number){
 p.add(<Line points={[[x1,y1],[x2,y2]]} stroke={P.blue} lineWidth={4} endArrow arrowSize={15}/>);
}
function world(parent:Node,x:number,y:number,w:number,h:number){
 const n=new Node({x,y});parent.add(n);
 n.add(<Rect width={w} height={h} fill="#f5f7f3" stroke={P.line} lineWidth={1}/>);
 n.add(<Line points={[[-w*.4,h*.25],[-w*.16,h*.06],[w*.1,h*.18],[w*.4,-h*.2]]} stroke="#d6ded0" lineWidth={42}/>);
 for(const [a,b] of [[-.32,-.27],[.29,.25],[.38,-.27],[-.35,.25]]){
  n.add(<Rect x={a*w} y={b*h+19} width={14} height={32} fill={P.muted}/>);
  n.add(<Circle x={a*w} y={b*h-4} size={54} fill="#dae3d5" stroke="#84967b" lineWidth={2}/>);
 }
 n.add(<Circle x={-30} y={32} width={52} height={18} fill="#b9c8b0"/>);
 n.add(<Rect x={-30} y={3} size={[28,40]} fill={P.blue}/>);
 n.add(<Circle x={-30} y={-28} size={27} fill={P.yellow} stroke={P.ink} lineWidth={1}/>);
 return n;
}
// Code-native original diagrams; never pretend these are captured game interfaces.
function diagram(root:Node,index:number,clock:()=>number){
 const p=(delay=0,speed=5)=>()=>easeInOutCubic(clamp((clock()-delay)/speed));
 if(index===0||index===2){
  bag(root,-670,30,1.6);root.add(label('가방 확장',-670,206,32));
  root.add(label('현재',-300,-148,30,P.muted));root.add(label('목표',580,-148,30,P.muted));
  root.add(label('1,700 G',-300,-62,68));root.add(label('2,000 G',580,-62,68));
  bar(root,140,64,1040,()=>.85*p(1,5)());
  root.add(<Rect x={140} y={185} width={480} height={92} fill={P.yellow} opacity={p(4,1)}>
   <Txt text="남은 거리  300 G" fontFamily={P.font} fontSize={42} fontWeight={700} fill={P.ink}/>
  </Rect>);
  root.add(label(index===2?'현재값 + 목표 = 다음 행동의 정보':'막연한 구매가, 가까운 목표가 된다',100,318,34));
 } else if(index===1){
  inventory(root,-475,-10,2,()=>12);root.add(label('챙기고 싶은 것이 더 있다',-475,-208,36));
  root.add(<Rect x={-475} y={184} width={480} height={78} fill={P.panel}><Txt text="버릴까?  돌아갈까?" fontFamily={P.font} fontSize={34} fill={P.ink}/></Rect>);
  arrow(root,-105,0,130,0);bag(root,462,-20,1.5);root.add(label('더 큰 가방',462,160,42));
  root.add(label('하고 싶은 행동을 가능하게',462,226,32,P.blue));
  root.add(label('불편의 반복이 아니라, 원하는 변화',0,334,36));
 } else if(index===3){
  root.add(label('BEFORE',-485,-215,28,P.muted));root.add(label('AFTER',440,-215,28,P.blue));
  root.add(label('12칸',-485,-143,58));root.add(label('24칸',440,-143,58));
  inventory(root,-485,40,2,()=>12);inventory(root,440,65,4,()=>12+9*p(1,7)());
  arrow(root,-145,25,100,25);
  root.add(<Rect y={330} width={1080} height={85} fill={P.yellow}><Txt text="획득 완료 → 이제 더 챙길 수 있다" fontFamily={P.font} fontSize={38} fill={P.ink}/></Rect>);
 } else if(index===4){
  root.add(label('경험치 수집',-620,-105,37));
  for(let i=0;i<5;i++)root.add(<Rect x={()=>-755+i*64+14*p(.4,4)()} y={()=>14-18*Math.sin(p(.4,4)()*Math.PI+i*.3)} size={32} rotation={45} fill={P.blue}/>);
  bar(root,-620,120,360,()=>.48+.52*p(.4,4)());arrow(root,-390,20,-245,20);
  root.add(label('강화 선택',0,-164,38));
  ['공격력','범위','새 무기'].forEach((s,i)=>root.add(<Rect y={-52+i*95} width={320} height={76} fill={()=>i===1&&p(5,1)()>.3?P.yellow:P.panel} stroke={P.line} lineWidth={1}><Txt text={s} fontFamily={P.font} fontSize={32} fill={P.ink}/></Rect>));
  arrow(root,222,20,356,20);root.add(label('플레이의 변화',600,-164,38));
  root.add(<Circle x={600} y={47} size={()=>100+170*p(5,1)()} stroke={P.blue} lineWidth={3} fill={P.blueLight}/>);
  root.add(<Circle x={600} y={47} size={46} fill={P.blue}/>);
  root.add(label('진행은 명확하게 · 발견의 여지는 남기기',0,326,37));
 } else if(index===5){
  const a=world(root,-445,30,770,390),b=world(root,445,30,770,390);
  root.add(label('전부 같은 크기로',-445,-226,38));root.add(label('지금 필요한 것부터',445,-226,38));
  ['재료 9/10','업적 4/5','보석 70','퀘스트 2','EXP 80%','도감 15'].forEach((s,i)=>a.add(<Rect x={i%2===0?-184:184} y={-130+Math.floor(i/2)*125} width={310} height={82} fill={P.background} stroke={P.line} lineWidth={2}><Txt text={s} fontFamily={P.font} fontSize={29} fill={P.ink}/></Rect>));
  bar(b,0,-148,650,()=>.77);
  b.add(<Rect x={170} y={120} width={370} height={68} fill={P.background} stroke={P.line} lineWidth={1}><Txt text="선택한 목표  9 / 10" fontFamily={P.font} fontSize={27} fill={P.ink}/></Rect>);
  root.add(label('항상 필요한 정보 / 필요할 때 확인할 정보',0,323,35));
 } else if(index===6){
  root.add(label('남은 개수',-440,-191,35,P.muted));root.add(label('남은 시도',435,-191,35,P.muted));
  root.add(label('1개',-440,-56,100));root.add(label('?',435,-56,116,P.blue));root.add(label('≠',0,-56,94));
  bar(root,-440,86,580,()=>.9);root.add(label('9 / 10',-440,154,34));
  [0,1,2,3].forEach(i=>root.add(<Circle x={285+i*100} y={89} size={34} stroke={P.blue} lineWidth={2} fill={()=>clock()>3+i?P.blueLight:P.background}/>));
  root.add(<Rect y={281} width={1350} height={104} fill={P.panel}><Txt text="불확실한 시간을 ‘한 번이면 끝’으로 약속하지 않기" fontFamily={P.font} fontSize={36} fill={P.ink}/></Rect>);
 } else {
  ['왜 원할까?','얼마나 남았나?','무엇이 달라지나?'].forEach((s,i)=>{
   root.add(<Rect x={(i-1)*566} y={20} width={510} height={350} fill={i===2?P.blueLight:P.panel} stroke={P.line} lineWidth={1}/>);
   root.add(label('0'+(i+1),(i-1)*566,-82,68,P.blue));root.add(label(s,(i-1)*566,47,37));
   root.add(label(['원하는 행동','목표까지 거리','직접 느끼는 변화'][i],(i-1)*566,123,29,P.muted));
  });root.add(label('그 사이의 플레이도 재미있어야 한다',0,295,43));
 }
}
export function* paperScene(view:View2D,index:number,duration:number){
 const scene=STORYBOARD[index],seconds=manifest.editing.exampleSeconds;view.fill(P.background);
 const src=clips['../assets/gameplay/scene'+scene.id+'.mp4'],shot=new Node({});view.add(shot);
 if(src){const v=new MixedVideo({src,width:1920,height:1080});shot.add(v);yield v;v.play();yield* waitFor(seconds);v.pause();}
 else {shot.add(label('자료화면 준비 중',0,-35,46));shot.add(label(scene.game,0,60,34,P.muted));yield* waitFor(seconds);}
 shot.remove();
 const layout=new Node({});view.add(layout);
 layout.add(<Txt text={'GAME DESIGN  /  '+scene.id} x={-864} y={-471} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.blue}/>);
 layout.add(<Txt text={scene.title} x={-864} y={-386} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>);
 layout.add(<Line points={[[-864,-320],[864,-320]]} stroke={P.line} lineWidth={1.5}/>);
 const note=index===0||index===2?'설명용 가정: 현재 1,700G · 실제 게임 HUD를 재현한 화면이 아닙니다.':index===5?'직접 만든 가상 UI 비교 · 사용자 실험 결과가 아닙니다.':index===6?'가상의 확률 획득 사례 · 특정 게임의 드롭 규칙이 아닙니다.':'개념을 설명하는 자체 제작 도식';
 layout.add(<Txt text={note} x={-864} y={-275} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>);
 const body=new Node({opacity:0});layout.add(body);const time=createSignal(0);diagram(body,index,time);
 layout.add(<Rect y={452} width={1728} height={100} fill={P.panel}><Txt text={scene.takeaway} fontFamily={P.font} fontSize={32} fill={P.ink}/></Rect>);
 // tween emits its closing sample on an additional frame; preserve measured SRT boundaries.
 yield* tween(duration-seconds-1/60,v=>{time(v*(duration-seconds));body.opacity(clamp(v*(duration-seconds)/.35));});
}
