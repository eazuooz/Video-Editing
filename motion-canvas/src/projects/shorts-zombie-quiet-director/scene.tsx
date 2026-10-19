import {makeScene2D,Img,Node,Txt,Rect,Circle,Line} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-zombie-quiet-director/production/visual-timing.json';
import {makePacingDiagram,makeSoundMigrationDiagram} from './explanation';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC'};
const ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-zombie-quiet-director/production/local/';
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(v:number)=>Math.max(0,Math.min(1,v));
 const s=()=>timing.sections.find(s=>t()>=s.start&&t()<s.end)??timing.sections[timing.sections.length-1];
 const game=()=>s().kind==='game',pz=()=>game()&&('source' in s())&&s().source==='pz';
 const reaction=()=>game()?reactionPresence(t):0;
 const phase=(list:typeof timing.pacingPhases)=>list.find(p=>t()>=p.start&&t()<p.end);
 const pacePhase=()=>s().id==='pacing'?(phase(timing.pacingPhases)?.id??'hidden'):'hidden';
 const soundPhase=()=>s().id==='sound-migration'?(phase(timing.soundPhases)?.id??'hidden'):'hidden';
 const progress=(list:typeof timing.pacingPhases)=>{const p=phase(list);return p?clamp((t()-p.start)/Math.max(.1,p.end-p.start)):0;};
 const frame=()=>Math.max(0,Math.min(Math.round((s().end-s().start)*60)-1,Math.floor((t()-s().start)*60+1e-5)));
 view.fill('#000000');
 const gameGroup=new Node({position:[-30,-70],x:()=>-30-175*reaction(),scale:()=>1-.23*reaction(),opacity:()=>game()?1:0});view.add(gameGroup);
 const pane=new Rect({width:1000,height:750,clip:true});gameGroup.add(pane);
 pane.add(<Img src={()=>ROOT+'frames/'+(game()?s().id:'opening-combat')+'/frame-'+String(game()?frame():0).padStart(4,'0')+'.jpg'} width={1000} height={750}/>);
 // Verified player location in the camera-follow PZ range, never a collider or detector.
 pane.add(<Circle width={95} height={128} position={[0,10]} stroke={C.green} lineWidth={7} opacity={()=>pz()?1:0}/>);
 // Keep the marker key outside the camera/cat transform and below the header.
 view.add(<Rect width={1000} height={44} position={[-30,-445]} fill="#000000" opacity={()=>game()?1:0}/>);
 view.add(<Txt text={()=>s().id==='intensity-events'?'':pz()?'초록 원: 플레이어':game()?'실제 게임 플레이':''} fontFamily="Malgun Gothic" fontSize={31} fill={()=>pz()?C.green:C.muted} position={[-30,-445]}/>);
 // These two independent recordings establish context, not the hidden game state.
 const pacing=makePacingDiagram(t,pacePhase,()=>progress(timing.pacingPhases));view.add(pacing);
 const sound=makeSoundMigrationDiagram(t,soundPhase,()=>progress(timing.soundPhases));view.add(sound);
 view.add(<Txt text={()=>s().id==='pacing'?'페이싱 (Pacing) · 전투와 휴식의 리듬':s().id==='sound-migration'?'메타 이벤트 (Meta Event) · 먼 총성 같은 사건':s().id==='intensity-events'?'AI 디렉터 (AI Director) · 전투 흐름 조절':''} fontFamily="Malgun Gothic" fontSize={33} fill={C.green} position={[-30,-445]}/>);
 view.add(<Txt text={()=>s().id==='remaining-threats'?'남은 적은 계속 공격 · 보스는 예외':s().id==='pz-quiet'?'같은 휴식 신호로 해석할 수 없음':s().id==='l4d-return'?'레포데: 다음 공격의 박자':s().id==='pz-return'?(t()<40.7?'좀보이드: 주변 무리의 이동':'조용함 ≠ 안전 보장'):''} fontFamily="Malgun Gothic" fontSize={38} fontWeight={700} fill={C.yellow} position={[-30,565]}/>);
 // Static brand framing; scene transitions inherit the same title and audio bed.
 view.add(<Rect width={1080} height={490} position={[0,-715]} fill="#000000"/>);
 view.add(<Txt text="얌얌코딩" fontFamily="Malgun Gothic" fontSize={37} fontWeight={700} fill={C.muted} position={[-340,-820]}/>);
 view.add(<Txt text="좀비가 조용해지면" fontFamily="Malgun Gothic" fontSize={74} fontWeight={700} fill={C.white} position={[-30,-700]}/>);
 view.add(<Txt text="안심해도 될까?" fontFamily="Malgun Gothic" fontSize={84} fontWeight={700} fill={C.yellow} position={[-30,-590]}/>);
 view.add(<Txt text={()=>pz()||s().id==='sound-migration'?'PROJECT ZOMBOID':'LEFT 4 DEAD'} fontFamily="Malgun Gothic" fontSize={33} fill={C.muted} position={[-30,-500]}/>);
 view.add(createReactionMascot(t));
 // Credits sit above the fixed two-line caption area and in front of the cat.
 view.add(<Rect width={1040} height={86} position={[-10,292]} fill="#000000" opacity={()=>game()?.88:0}/>);
 view.add(<Txt text={()=>pz()?'녹화 버전 42.5.0 · 조용한 주택가':''} fontFamily="Malgun Gothic" fontSize={28} fill={C.muted} position={[-30,264]}/>);
 view.add(<Txt text={()=>game()?(pz()?'Project Zomboid · Survival Gamer':'Left 4 Dead · GamerSky · CC BY'):''} fontFamily="Malgun Gothic" fontSize={27} fill={C.muted} position={[-30,302]}/>);
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
