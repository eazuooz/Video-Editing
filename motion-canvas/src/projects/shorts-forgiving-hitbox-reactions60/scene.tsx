import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import trace from '../../../../projects/shorts-forgiving-hitbox/production/local/capture-full-v1/trace.json';
import footage from '../../../../projects/shorts-forgiving-hitbox/production/source-fairness-60s.json';
import timing from '../../../../projects/shorts-forgiving-hitbox/production/local/fairness-60s/visual-timing.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',forest:'#073C32'};
const ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-forgiving-hitbox/production/local/';
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number,a:number,b:number)=>Math.min(b,Math.max(a,x));
 const section=()=>timing.sections.find(s=>t()>=s.start&&t()<s.end)??timing.sections[timing.sections.length-1];
 const isGame=()=>['celeste','code','return-game'].includes(section().id);
 const reaction=()=>reactionPresence(t);
 const code=()=>section().id==='code';
 const codeProgress=()=>code()?clamp((t()-section().start-3.46)/.9,0,1):0;
 const unityTime=()=>{
  const s=section();if(s.kind==='unity')return clamp(s.sourceStart+(t()-s.start)*(s.rate??0),s.sourceStart,s.sourceEnd);
  return 4;
 };
 const state=()=>trace.frames[clamp(Math.floor(unityTime()*60+1e-5),0,1799)];
 const green=()=>!isGame()&&t()>=timing.revealStart;
 const red=()=>{const u=unityTime(),s=state();const sh=trace.frames.find(f=>f.shot===s.shot)!;return green()&&t()>=timing.termsStart&&s.projectile.y>650&&s.projectile.y<1235&&Math.abs(s.projectile.x)<1200&&u>=0;};
 const point=(p:{x:number,y:number})=>new Vector2(p.x-540,p.y-960);
 const outline=(key:'hurt'|'attack')=>{const a=state()[key].map(point);return [...a,a[0]];};
 const sourceTime=()=>{const s=section();return s.kind==='game'?clamp(s.sourceStart+t()-s.start,s.sourceStart,s.sourceEnd):99.5;};
 // Exact original-frame selection matches the inspected anchor stills. Avoid HTMLVideo seek lag.
 const gameFrame=()=>clamp(Math.ceil(sourceTime()*30000/1001-1e-7)-2776,0,329);
 const anchors=footage.editorialTracking.anchors;
 const anchor=()=>{
  const st=sourceTime();let a=anchors[0],b=anchors[anchors.length-1];
  for(let i=0;i<anchors.length-1;i++)if(st>=anchors[i].sourceSeconds&&st<=anchors[i+1].sourceSeconds){a=anchors[i];b=anchors[i+1];break;}
  if(!a.targetCenter||!b.targetCenter)return null;
  const p=clamp((st-a.sourceSeconds)/Math.max(.0001,b.sourceSeconds-a.sourceSeconds),0,1);
  return new Vector2(a.targetCenter[0]*(1-p)+b.targetCenter[0]*p,a.targetCenter[1]*(1-p)+b.targetCenter[1]*p);
 };
 // Keep the editorial crop continuous across a dash flash; the marker itself stays hidden.
 const validAnchors=anchors.filter(a=>a.targetCenter!==null);
 const cropAnchor=()=>{
  const st=sourceTime();let a=validAnchors[0],b=validAnchors[validAnchors.length-1];
  for(let i=0;i<validAnchors.length-1;i++)if(st>=validAnchors[i].sourceSeconds&&st<=validAnchors[i+1].sourceSeconds){a=validAnchors[i];b=validAnchors[i+1];break;}
  if(st>=validAnchors[validAnchors.length-1].sourceSeconds)a=b=validAnchors[validAnchors.length-1];
  const p=clamp((st-a.sourceSeconds)/Math.max(.0001,b.sourceSeconds-a.sourceSeconds),0,1);
  return new Vector2(a.targetCenter![0]*(1-p)+b.targetCenter![0]*p,a.targetCenter![1]*(1-p)+b.targetCenter![1]*p);
 };
 const scale=5/6,gameCenter=()=>{const p=cropAnchor();return new Vector2(clamp(p.x,540,1380),clamp(p.y,432,648));};
 const toGame=(p:Vector2)=>p.sub(gameCenter()).scale(scale);
 const markVisible=()=>isGame()&&!code()&&anchor()!==null&&!footage.editorialTracking.hideIntervals.some(i=>sourceTime()>=i.startSeconds&&sourceTime()<=i.endSeconds);
 view.fill('#000000');
 const unityDemo=new Node({x:()=>-200*reaction(),scale:()=>1-.25*reaction()});view.add(unityDemo);
 unityDemo.add(<Img src={()=>ROOT+'fairness-60s/footage/unity-frames/frame-'+String(state().frame).padStart(4,'0')+'.png'} width={1080} height={1920} opacity={()=>isGame()?0:1}/>);
 view.add(<Rect width={1080} height={600} position={[0,-660]} fill="#000000" opacity={()=>isGame()?0:1}/>);
 view.add(<Rect width={1080} height={622} position={[0,649]} fill="#000000"/>);
 const gamePane=new Rect({width:900,height:720,position:[-70,-30],clip:true,opacity:()=>isGame()?1:0});view.add(gamePane);
 gamePane.add(<Img src={()=>ROOT+'fairness-60s/footage/frames/frame-'+String(gameFrame()).padStart(4,'0')+'.png'} width={1600} height={900} smoothing={false} position={()=>new Vector2(960,540).sub(gameCenter()).scale(scale)}/>);
 gamePane.add(<Circle width={114} height={114} position={()=>toGame(anchor()??new Vector2(0,0))} stroke={C.green} lineWidth={7} opacity={()=>markVisible()?1:0}/>);
 // This ring identifies the visible character. It is not an inferred collider.
 view.add(<Txt text="초록 원: 캐릭터 위치" fontFamily="Malgun Gothic" fontSize={30} fill={C.green} position={[-70,-430]} opacity={()=>isGame()&&!code()?1:0}/>);
 view.add(<Rect width={1080} height={510} position={[0,-705]} fill="#000000"/>);
 view.add(<Txt text="얌얌코딩" fontFamily="Malgun Gothic" fontWeight={700} fontSize={37} fill={C.muted} position={[-340,-820]}/>);
 view.add(<Txt text="닿았는데 안 맞는" fontFamily="Malgun Gothic" fontWeight={700} fontSize={74} fill={C.white} position={[-30,-700]}/>);
 view.add(<Txt text="게임의 작은 봐주기" fontFamily="Malgun Gothic" fontWeight={700} fontSize={74} fill={C.yellow} position={[-30,-590]}/>);
 view.add(<Txt text={()=>code()?'공개 코드로 보는 판정':isGame()?'실제 게임 플레이':'Unity 직접 시연'} fontFamily="Malgun Gothic" fontSize={30} fill={C.muted} position={()=>isGame()?[-30,-490]:[-30,-515]}/>);
 view.add(<Txt text="체력" fontFamily="Malgun Gothic" fontWeight={700} fontSize={42} fill={C.white} position={[-225,-390]} opacity={()=>isGame()?0:1}/>);
 view.add(<Rect width={300} height={35} fill="#23392F" stroke={C.white} lineWidth={2} position={[10,-390]} opacity={()=>isGame()?0:1}/>);
 view.add(<Rect width={()=>300*state().health/100} height={31} fill={()=>state().health===100?C.green:C.red} position={()=>[-140+150*state().health/100,-390]} opacity={()=>isGame()?0:1}/>);
 view.add(<Txt text={()=>String(state().health)} fontFamily="Malgun Gothic" fontWeight={700} fontSize={46} fill={C.white} position={[220,-390]} opacity={()=>isGame()?0:1}/>);
 unityDemo.add(<Line points={()=>outline('hurt')} stroke={C.green} lineWidth={7} end={()=>clamp((t()-timing.revealStart)/.55,0,1)} opacity={()=>green()?1:0}/>);
 unityDemo.add(<Line points={()=>outline('attack')} stroke={C.red} lineWidth={7} opacity={()=>red()?1:0}/>);
 unityDemo.add(<Txt text={'피격 영역\nHurtbox'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={36} lineHeight={44} fill={C.green} position={[-365,-25]} opacity={()=>green()?1:0}/>);
 unityDemo.add(<Line points={()=>[new Vector2(-270,-25),new Vector2(Math.min(...state().hurt.map(p=>p.x))-555,-25)]} stroke={C.green} lineWidth={5} endArrow arrowSize={12} opacity={()=>green()?1:0}/>);
 unityDemo.add(<Txt text={'공격 영역\nHitbox'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={32} lineHeight={40} fill={C.red} position={()=>[310-74*reaction(),-170-240*reaction()]} opacity={()=>red()?1:0}/>);
 unityDemo.add(<Line points={()=>[new Vector2(250-10*reaction(),-120-225*reaction()),new Vector2(Math.max(...state().attack.map(p=>p.x))-530,state().projectile.y-970)]} stroke={C.red} lineWidth={5} endArrow arrowSize={12} opacity={()=>red()?1:0}/>);
 // Keep the result above HP, inside the opaque header rather than the projectile path.
 view.add(<Txt text={()=>section().id==='attacker'?'공격한 쪽: “왜 안 맞아?”':section().id==='survivor'?'살아남은 쪽: “잘 피했다!”':section().id==='resolution'?'겉은 스쳐도, 판정은 안 겹침':state().hitApplied?'겹침 → 피해 30':'겹치지 않음 → 피해 0'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={()=>section().id==='attacker'||section().id==='survivor'?42:38} fill={()=>section().id==='attacker'||state().hitApplied?C.red:C.green} position={[-30,-445]} opacity={()=>isGame()||t()<3?0:1}/>);
 unityDemo.add(<Txt text={()=>section().id==='wide'?'몸 크기로\n설정':section().id==='resolution'?'처음 장면\n다시 확인':section().id==='limit'?'여기서 더\n줄인다면?':green()?'조금 작게\n설정':''} fontFamily="Malgun Gothic" fontWeight={700} fontSize={34} lineHeight={43} fill={C.white} position={[-365,170]} opacity={()=>isGame()?0:1}/>);
 // A separate public-code diagram; no guessed bounds are placed on gameplay.
 const diagram=new Rect({width:900,height:720,position:[-70,-30],fill:'#000000',opacity:()=>code() ? .96 : 0});view.add(diagram);
 diagram.add(<Txt text="공개 코드 · 기본 상태" fontFamily="Malgun Gothic" fontWeight={700} fontSize={38} fill={C.yellow} position={[0,-265]}/>);
 diagram.add(<Txt text="이동 충돌 영역" fontFamily="Malgun Gothic" fontWeight={700} fontSize={36} fill={C.white} position={[-220,-185]}/>);
 diagram.add(<Txt text="피격 영역" fontFamily="Malgun Gothic" fontWeight={700} fontSize={36} fill={C.green} position={[220,-185]}/>);
 // 28 native pixels represent one source pixel in this code-based diagram.
 // The two bounds share the same fixed top; only the lower two rows are removed.
 diagram.add(<Txt text="1칸 = 1픽셀" fontFamily="Malgun Gothic" fontSize={32} fill={C.muted} position={[0,-315]}/>);
 for(const centerX of [-220,220]){
  const color=centerX<0?C.white:C.muted;
  for(let i=1;i<8;i++)diagram.add(<Line points={[[centerX-112+i*28,-138],[centerX-112+i*28,170]]} stroke={color} lineWidth={1.5} opacity={.16}/>);
  for(let i=1;i<11;i++)diagram.add(<Line points={[[centerX-112,-138+i*28],[centerX+112,-138+i*28]]} stroke={color} lineWidth={1.5} opacity={.16}/>);
 }
 diagram.add(<Rect width={224} height={()=>56*codeProgress()} position={()=>[220,170-28*codeProgress()]} fill="#FFD25A24" stroke={C.yellow} lineWidth={3} opacity={()=>codeProgress()>0?1:0}/>);
 diagram.add(<Rect width={224} height={308} position={[-220,16]} stroke={C.white} lineWidth={7}/>);
 diagram.add(<Rect width={224} height={308} position={[220,16]} stroke={C.muted} lineWidth={3} lineDash={[12,9]}/>);
 diagram.add(<Rect width={224} height={()=>308-56*codeProgress()} position={()=>[220,16-28*codeProgress()]} stroke={C.green} lineWidth={8}/>);
 diagram.add(<Txt text="8 × 11" fontFamily="Malgun Gothic" fontWeight={700} fontSize={48} fill={C.white} position={[-220,15]}/>);
 diagram.add(<Txt text={()=>codeProgress()>.8?'8 × 9':'8 × 11'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={48} fill={C.green} position={[220,-12]}/>);
 diagram.add(<Line points={[[350,170],[350,114]]} stroke={C.yellow} lineWidth={5} endArrow arrowSize={12} opacity={()=>codeProgress()>=1?1:0}/>);
 diagram.add(<Txt text="아래쪽 2픽셀 차이" fontFamily="Malgun Gothic" fontWeight={700} fontSize={38} fill={C.yellow} position={[0,226]} opacity={()=>codeProgress()>=1?1:0}/>);
 diagram.add(<Txt text="공개 코드 재구성 · 실측 아님" fontFamily="Malgun Gothic" fontSize={32} fill={C.muted} position={[0,278]}/>);
 // The credit stays above both the code diagram and the fixed caption box.
 view.add(<Rect width={900} height={44} position={[-70,300]} fill="#000000" opacity={()=>isGame()?1:0}/>);
 view.add(<Txt text="Celeste · UltraPita · CC BY" fontFamily="Malgun Gothic" fontSize={27} fill={C.muted} position={[-70,300]} opacity={()=>isGame()?1:0}/>);
 // A compact condition/result strip, wholly outside the fixed caption box.
 // It shows real Unity state; the arrow to health completes only after a hit.
 const stripShown=()=>['terms','wide','narrow'].includes(section().id)&&(section().id!=='terms'||t()>=timing.termsStart+2.7);
 const stripStart=()=>section().id==='terms'?timing.termsStart+2.7:section().start;
 const stripEntry=()=>clamp((t()-stripStart())/.22,0,1);
 const hitFrames=new Map<string,number>();
 for(const f of trace.frames)if(f.hitApplied&&!hitFrames.has(f.shot))hitFrames.set(f.shot,f.frame);
 const hitTrace=()=>state().hitApplied?clamp((state().frame-(hitFrames.get(state().shot)??state().frame)+1)/8,0,1):0;
 const strip=new Node({position:[-30,645],opacity:()=>stripShown()?stripEntry():0});
 view.add(strip);
 strip.add(<Txt text="공격 영역" fontFamily="Malgun Gothic" fontWeight={700} fontSize={34} fill={C.red} position={[-310,-26]}/>);
 strip.add(<Txt text="피격 영역" fontFamily="Malgun Gothic" fontWeight={700} fontSize={34} fill={C.green} position={[0,-26]}/>);
 strip.add(<Txt text="체력" fontFamily="Malgun Gothic" fontWeight={700} fontSize={34} fill={C.white} position={[300,-26]}/>);
 strip.add(<Line points={[[-212,-26],[-126,-26]]} stroke={C.red} lineWidth={4} endArrow arrowSize={11} end={()=>clamp((t()-stripStart())/.32,0,1)}/>);
 strip.add(<Line points={[[122,-26],[224,-26]]} stroke={C.muted} lineWidth={3} lineDash={[7,7]} endArrow arrowSize={10} opacity={.42}/>);
 strip.add(<Line points={[[122,-26],[224,-26]]} stroke={C.red} lineWidth={5} endArrow arrowSize={11} end={hitTrace}/>);
 strip.add(<Txt text={()=>state().overlapping?`현재 겹침 · 체력 100 → ${state().health}`:state().hitApplied?`겹침 발생 · 체력 100 → ${state().health}`:`겹치지 않음 · 체력 ${state().health} 유지`} fontFamily="Malgun Gothic" fontWeight={700} fontSize={32} fill={()=>state().hitApplied?C.red:C.green} position={[0,40]}/>);
 // Four finite reactions; original footage selection, PCM and 60s clock remain intact.
 view.add(createReactionMascot(t));
 yield* t(60,60,linear);
});
