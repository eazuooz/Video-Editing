import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-normal-map-illusion/production/visual-timing.json';
import data from '../../../../projects/shorts-normal-map-illusion/production/local/capture-data.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'};
const FONT='Malgun Gothic',ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-normal-map-illusion/production/local/';
const SOURCE='/@fs/D:/Github/VideoEditing/unity/VideoEditing/Assets/VideoScenes/shorts-normal-map-illusion/Generated/';
const PREFLIGHT=new URLSearchParams(window.location.search).get('preflight')==='1';
const sparse:any={'hero':'02-wall-on','flat-reveal':'06-wall-edge','shared-normal':'01-wall-off','normal-definition':'05-wall-normals-oblique','pixel-normal':'05-wall-normals-oblique','normal-data':'04-wall-normal-rgb','neutral-purple':'04-wall-normal-rgb','light-facing':'03-wall-light-left','light-sideways':'05-wall-normals-oblique','moving-light':'02-wall-on','knight-source':'07-knight-source','knight-bake':'12-knight-pipeline','knight-light':'10-knight-relit-left','wall-detail':'02-wall-on','same-mesh':'02-wall-on','silhouette':'06-wall-edge','closing':'02-wall-on'};
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
 const sections=timing.sections as any[];
 const section=()=>sections.find(s=>t()>=s.start&&t()<s.end)??sections[sections.length-1];
 const elapsed=()=>t()-section().start,frame=()=>clamp(Math.floor(t()*60+1e-5),0,timing.frames-1);
 const is=(...ids:string[])=>ids.includes(section().id),knight=()=>section().kind.startsWith('knight'),comparison=()=>section().kind==='wall-ab';
 const definition=()=>is('normal-definition','normal-data')&&elapsed()<1.65;
 const record=()=>PREFLIGHT?(data.frames as any[]).find(f=>f.id===sparse[section().id]):(data.frames as any[])[frame()];
 const probe=()=>record()?.probe,point=(p:any)=>new Vector2(((p?.x??540)-540)*1000/1080,((p?.y??540)-540)*1000/1080);
 const reaction=()=>reactionPresence(t);
 view.fill('#000000');
 const world=new Node({position:[-30,0],x:()=>-30-120*reaction(),scale:()=>1-.19*reaction()});view.add(world);
 const picture=new Rect({width:1000,height:1000,clip:true,y:()=>is('knight-bake')?-160:0,opacity:()=>comparison()?0:(definition()?0.25:1)});world.add(picture);
 picture.add(<Img src={()=>PREFLIGHT?ROOT+'capture-preview-v2/'+sparse[section().id]+'.png':ROOT+'capture-full-v1/frames/frame-'+String(frame()).padStart(5,'0')+'.png'} width={1000} height={1000}/>);
 // These leaders reference our actual GPU probe and the real TBN/light directions.
 const normalLabels=new Node({opacity:()=>is('normal-definition','shared-normal','pixel-normal','light-facing','light-sideways')&&!definition()?1:0});world.add(normalLabels);
 for(const [key,text,colour,x,y] of [['geometryNormalScreenEnd','원래 면의 방향',C.white,-275,210],['normalScreenEnd','빛 계산 방향',C.green,-250,275],['lightScreenEnd','광원 쪽 방향',C.yellow,260,210]] as const){
  const visible=()=>key==='geometryNormalScreenEnd'||!is('shared-normal','normal-definition');
  normalLabels.add(<Line points={()=>[[x,y-22],point(probe()?.[key])]} stroke={colour} lineWidth={3} end={()=>visible()?clamp((elapsed()-.15)/.45):0}/>);
  normalLabels.add(<Txt text={key==='geometryNormalScreenEnd'?'원래 면의 방향':text} position={[x,y]} fontFamily={FONT} fontSize={36} fontWeight={700} fill={colour} opacity={()=>visible()?1:0}/>);
 }
 const lightValue=new Node({position:[260,285],opacity:()=>is('light-facing','light-sideways')?1:0});world.add(lightValue);
 lightValue.add(<Rect width={440} height={112} fill="#000000"/>);
 lightValue.add(<Txt text="우리 셰이더 · 직접광 기여" fontFamily={FONT} fontSize={34} fill={C.muted} position={[0,-27]}/>);
 lightValue.add(<Txt text={()=>Math.round((probe()?.gpuNDotL??0)*100)+'%'} fontFamily={FONT} fontSize={52} fontWeight={700} fill={()=>is('light-facing')?C.green:C.red} position={[0,27]}/>);
 const neutral=new Node({opacity:()=>is('neutral-purple')?1:0});world.add(neutral);
 neutral.add(<Circle position={[94,-94]} width={90} height={90} stroke={C.teal} lineWidth={6}/>);
 neutral.add(<Line points={[[94,-50],[94,40],[-220,95]]} stroke={C.teal} lineWidth={4} end={()=>clamp(elapsed()/.45)}/>);
 neutral.add(<Rect width={660} height={250} position={[-50,170]} fill="#000000"/>);
 neutral.add(<Rect width={95} height={95} position={[-235,145]} fill="#8080FF" stroke={C.white} lineWidth={3}/>);
 neutral.add(<Txt text="방향 데이터" fontFamily={FONT} fontSize={34} fill={C.teal} position={[-235,240]}/>);
 neutral.add(<Line points={[[-30,230],[200,230]]} stroke={C.white} lineWidth={4}/>);
 neutral.add(<Line points={[[75,230],[75,110]]} stroke={C.teal} lineWidth={7} endArrow arrowSize={17} end={()=>clamp((elapsed()-.2)/.5)}/>);
 neutral.add(<Line points={[[75,210],[95,210],[95,230]]} stroke={C.white} lineWidth={3}/>);
 neutral.add(<Txt text="수직 방향" fontFamily={FONT} fontSize={36} fontWeight={700} fill={C.teal} position={[75,75]}/>);
 neutral.add(<Txt text="표면" fontFamily={FONT} fontSize={34} fill={C.white} position={[210,255]}/>);
 // Our one-pose bake: the two images are the actual saved colour/normal render outputs.
 const bake=new Node({opacity:()=>is('knight-bake')?1:0});world.add(bake);
 for(let i=0;i<2;i++){
  bake.add(<Rect width={235} height={235} position={[i===0?-125:125,180]} fill="#0D1210" stroke={i===0?C.white:C.teal} lineWidth={3}/>);
  bake.add(<Img src={SOURCE+(i===0?'KnightColour.png':'KnightNormal.png')} width={220} height={220} position={[i===0?-125:125,180]} smoothing={false}/>);
  bake.add(<Txt text={i===0?'색 그림':'노멀 맵'} fontFamily={FONT} fontSize={36} fill={i===0?C.white:C.teal} position={[i===0?-125:125,325]}/>);
 }
 bake.add(<Txt text="3D 모델" fontFamily={FONT} fontSize={36} fill={C.white} position={[-300,-385]}/>);
 bake.add(<Txt text="2D 조명" fontFamily={FONT} fontSize={36} fill={C.green} position={[300,-385]}/>);
 bake.add(<Line points={[[-120,-385],[120,-385]]} stroke={C.teal} lineWidth={5} endArrow arrowSize={15} end={()=>clamp(elapsed()/.5)}/>);
 const ab=new Node({opacity:()=>comparison()?1:0,position:[0,0]});world.add(ab);
 for(let i=0;i<2;i++){
  const pane=new Rect({width:455,height:455,clip:true,position:[i===0?-245:245,0],stroke:i===0?C.white:C.green,lineWidth:4});ab.add(pane);
  pane.add(<Img src={()=>PREFLIGHT||!comparison()?ROOT+'capture-preview-v2/'+(i===0?'01-wall-off':'02-wall-on')+'.png':ROOT+'capture-full-v1/ab-'+(i===0?'off':'on')+'/frame-'+String(frame()).padStart(5,'0')+'.png'} width={455} height={455}/>);
  const corners=()=>((record()?.meshScreenCorners??[]) as any[]).map(p=>new Vector2((p.x-540)*455/1080,(p.y-540)*455/1080));
  pane.add(<Line points={corners} closed={true} stroke={C.yellow} lineWidth={3} opacity={()=>corners().length===4?1:0}/>);
  pane.add(<Line points={()=>corners().length===4?[corners()[0],corners()[2]]:[]} stroke={C.yellow} lineWidth={3} opacity={()=>corners().length===4?1:0} end={()=>clamp(elapsed()/.5)}/>);
  ab.add(<Txt text={i===0?'노멀 맵 끔':'노멀 맵 켬'} fontFamily={FONT} fontSize={38} fontWeight={700} fill={i===0?C.white:C.green} position={[i===0?-245:245,-285]}/>);
  ab.add(<Txt text="삼각형 2개" fontFamily={FONT} fontSize={35} fill={C.yellow} position={[i===0?-245:245,275]}/>);
 }
 ab.add(<Txt text="같은 메시 · 같은 카메라 · 같은 빛" fontFamily={FONT} fontSize={34} fill={C.muted} position={[0,-355]}/>);
 // Fixed claim and both provenance-kind labels survive the scene changes.
 view.add(<Rect width={1080} height={490} position={[0,-715]} fill="#000000"/>);
 view.add(<Txt text="얌얌코딩" fontFamily={FONT} fontSize={37} fontWeight={700} fill={C.muted} position={[-340,-845]}/>);
 view.add(<Txt text="울퉁불퉁한 벽이" fontFamily={FONT} fontSize={77} fontWeight={700} fill={C.white} position={[-30,-730]}/>);
 view.add(<Txt text="사실 평면이라고?" fontFamily={FONT} fontSize={79} fontWeight={700} fill={C.yellow} position={[-30,-625]}/>);
 view.add(<Txt text={()=>t()<(sections.find(s=>s.id==='normal-definition')?.start??0)?'같은 벽 · 같은 메시':t()<(sections.find(s=>s.id==='normal-data')?.start??0)?'Normal · 법선':'Normal Map · 노멀 맵'} fontFamily={FONT} fontSize={34} fontWeight={700} fill={C.teal} position={[-235,-480]}/>);
 view.add(<Txt text={()=>knight()?'우리 재현 · 1프레임':'우리 Unity 구현'} fontFamily={FONT} fontSize={34} fill={C.muted} position={[305,-480]}/>);
 const card=new Node({opacity:()=>definition()?1:0});view.add(card);
 card.add(<Txt text={()=>is('normal-definition')?'Normal':'Normal Map'} fontFamily={FONT} fontSize={47} fill={C.teal} position={[-30,-320]}/>);
 card.add(<Txt text={()=>is('normal-definition')?'법선':'노멀 맵'} fontFamily={FONT} fontSize={60} fontWeight={700} fill={C.yellow} position={[-30,-245]}/>);
 card.add(<Txt text={()=>is('normal-definition')?'표면에서 수직으로 나가는 방향':'픽셀별 표면 방향을 담은 그림'} fontFamily={FONT} fontSize={36} fill={C.white} position={[-30,-165]}/>);
 view.add(<Txt text={()=>is('silhouette','flat-reveal')?'옆에서 보면, 평면':is('knight-source','knight-light')?'데드셀 방식 · 우리 에셋으로 재현':''} fontFamily={FONT} fontSize={36} fontWeight={700} fill={C.yellow} position={[-30,265]}/>);
 view.add(createReactionMascot(t));
 // Final clause/keyword ASS is encoded above all nodes and the mascot.
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
