import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-flow-map-river/production/visual-timing.json';
import native from '../../../../projects/shorts-flow-map-river/production/local/capture-full/readback.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
import rHalf from './labels/r-half.svg';
import rFull from './labels/r-full.svg';
import gHalf from './labels/g-half.svg';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'};
const FONT='Malgun Gothic',ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-flow-map-river/production/local/';
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(v:number)=>Math.min(1,Math.max(0,v));const sections=timing.sections as any[];
 const frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001)),record=()=>native.records[frame()] as any;
 const section=()=>sections.find(s=>frame()>=s.startFrame&&frame()<s.endFrame)??sections.at(-1),id=()=>section().id,e=()=>t()-section().start;
 const is=(...ids:string[])=>ids.includes(id()),presence=()=>reactionPresence(t),point=(p:any)=>new Vector2((p.x-540)*1040/1080,(p.y-540)*1040/1080);
 view.fill('#000');
 const world=new Node({position:()=>[-25-145*presence(),-35],scale:()=>1-.18*presence()});view.add(world);
 world.add(<Img src={()=>ROOT+'capture-full/frames/'+String(frame()).padStart(5,'0')+'.jpg'} width={1040} height={1040} opacity={()=>is('decode')?.22:1}/>);
 const field=new Node({opacity:()=>is('arrows','map','flow','move','update')?clamp(e()/.45):0});world.add(field);
 for(let i=0;i<84;i++)field.add(<Line points={()=>{const a=record()?.arrows?.[i];return a?[point(a.a),point(a.b)]:[];}} stroke={()=>is('map')?'#173B36':is('move')?C.red:C.yellow} lineWidth={4} endArrow arrowSize={11} end={()=>clamp(e()*3-i*.009)} opacity={()=>record()?.arrows?.[i]?1:0}/>);
 const focus=new Node({opacity:()=>is('uniform')?clamp(e()/.35):0});world.add(focus);
 focus.add(<Line points={[[-400,-15],[370,-15]]} stroke={C.red} lineWidth={7} endArrow arrowSize={22} end={()=>clamp(e()/.8)}/>);
 const modeLabels:any={hero:'물결이 바위를 돌아간다',uniform:'한 방향으로만 이동',arrows:'위치마다 다른 방향',map:'색 = 움직일 방향',decode:'색에 저장된 방향 읽기',flow:'그림을 읽는 위치가 이동',stretch:'계속 늘리면 → 왜곡',reset:'하나만 되감으면 → 튐',blend:'두 무늬를 번갈아 섞기',move:'바위만 이동 · 지도는 그대로',update:'방향 지도도 함께 수정',close:'보이는 흐름을 설계한다'};
 world.add(<Txt text={()=>modeLabels[id()]} position={[-15,-290]} fill={()=>is('uniform','stretch','reset','move')?C.red:C.yellow} fontFamily={FONT} fontSize={45} fontWeight={700}/>);
 world.add(<Txt text={()=>is('map')?'빨강(R) = 가로 · 초록(G) = 세로':is('arrows')?'격자 화살표 = 지도에서 읽은 방향':is('flow')?'같은 방향 데이터 → 화살표와 물결':is('move')?'옛 위치를 피하는 흐름':is('update')?'새 위치에 맞춘 흐름':''} position={[-15,255]} fill={C.white} fontFamily={FONT} fontSize={37}/>);
 // Worked RG example. The values are explicitly illustrative, never game telemetry.
 const decode=new Node({opacity:()=>is('decode')?1:0});world.add(decode);
 const right=()=>t()>=(timing.cueStarts as any)['p3-5'];
 decode.add(<Txt text="우리 맵의 저장 예시" position={[-15,-175]} fill={C.white} fontSize={37} fontFamily={FONT}/>);
 for(let i=0;i<2;i++){
  const x=i===0?-235:215,col=i===0?C.red:C.green;
  decode.add(<Rect position={[x,-80]} width={380} height={90} fill="#141A17" stroke={col} lineWidth={3}/>);
  decode.add(<Img src={()=>i===0?(right()?rFull:rHalf):gHalf} position={[x,-80]} height={42}/>);
 }
 decode.add(<Txt text="저장값 × 2 − 1 = 방향 성분" position={[-15,30]} fontSize={40} fill={C.white} fontFamily={FONT}/>);
 decode.add(<Txt text={()=>right()?'(1, 0)  오른쪽':'(0, 0)  정지'} position={[-15,120]} fontSize={57} fontWeight={700} fill={C.yellow} fontFamily={FONT}/>);
 decode.add(<Line points={[[-180,225],[180,225]]} stroke={C.yellow} lineWidth={9} endArrow arrowSize={24} opacity={()=>right()?1:0}/>);
 // Two phase bars directly visualize the shader's actual reset/blend clock.
 const phases=new Node({opacity:()=>is('reset','blend')?1:0,position:[-10,230]});world.add(phases);
 for(let i=0;i<2;i++){
  const y=i*80,ph=()=>((record()?.clock??0)*.3+i*.5)%1;
  phases.add(<Txt text={i===0?'무늬 A':'무늬 B'} position={[-350,y]} fontSize={35} fontFamily={FONT} fill={i===0?C.teal:C.yellow} opacity={()=>i===0||is('blend')?1:0}/>);
  phases.add(<Line points={[[-210,y],[330,y]]} lineWidth={8} stroke="#34423D" opacity={()=>i===0||is('blend')?1:0}/>);
  phases.add(<Circle position={()=>[-210+540*ph(),y]} size={25} fill={i===0?C.teal:C.yellow} opacity={()=>i===0||is('blend')?1:0}/>);
 }
 // A single vector header avoids stale DOM text bounds during exact-frame seeks.
 const header=(term:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="540" viewBox="0 0 1080 540"><rect width="1080" height="540" fill="black"/><g font-family="Malgun Gothic" font-weight="700"><text x="128" y="128" font-size="37" fill="${C.muted}">얌얌코딩</text><text x="510" y="258" text-anchor="middle" font-size="77" fill="white">게임 속 강물은</text><text x="510" y="361" text-anchor="middle" font-size="70" fill="${C.yellow}">어떻게 바위를 피할까?</text><text x="125" y="492" font-size="34" fill="${C.teal}">${term}</text><text x="720" y="492" font-size="34" font-weight="400" fill="${C.muted}">우리 Unity 구현</text></g></svg>`);
 const headers=[header('물결의 움직임'),header('Flow Map · 플로 맵')];
 view.add(<Img src={()=>headers[t()<(timing.cueStarts as any)['p3-1']?0:1]} width={1080} height={540} position={[0,-690]} zIndex={5}/>);
 view.add(createReactionMascot(t));
 yield view.toPromise();
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
