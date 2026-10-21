import {makeScene2D,Img,Node,Txt,Rect,Line} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-normal-map-illusion/production/visual-timing.json';
import data from '../../../../projects/shorts-normal-map-illusion/production/local/capture-data-v3.json';
import frozenSpriteProof from '../../../../projects/shorts-normal-map-illusion/production/local/capture-preview-v3/preview-readback.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
import {createNormalGrid} from './normal-grid';
import {createNormalRGB,RGBPhase} from './normal-rgb';
import {createDeadCellsGameplay} from './dead-cells-gameplay';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'};
const FONT='Malgun Gothic',ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-normal-map-illusion/production/local/';
const SOURCE='/@fs/D:/Github/VideoEditing/unity/VideoEditing/Assets/VideoScenes/shorts-normal-map-illusion/Generated/';
const PREFLIGHT=new URLSearchParams(window.location.search).get('preflight')==='1';
const sparse:any={'hero':'grid-on','flat-reveal':'wall-edge','shared-normal':'grid-off','normal-definition':'grid-off','grid-flat':'grid-off','pixel-normal':'grid-on','normal-data':'normal-rgb','rgb-signed':'normal-rgb','rgb-encoding':'normal-rgb','neutral-purple':'normal-rgb','light-facing':'grid-on-light-left','light-sideways':'grid-on','moving-light':'grid-on','knight-source':'knight-light-left','knight-bake':'knight-light-left','knight-light':'knight-light-left','wall-detail':'grid-on','same-mesh':'grid-on','silhouette':'wall-edge','closing':'grid-on'};
const PREVIEW=(data as any).previewDirectory??'capture-preview-grid-v2-grid-rgb',CAPTURE=(data as any).captureDirectory??PREVIEW;
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
 const sections=timing.sections as any[];
 const frame=()=>clamp(Math.floor(t()*60+1e-5),0,timing.frames-1);
 // The captured integer frame owns the cut. Floating time can fall one ULP
 // before a cue and must never request an A/B file outside that native state.
 const section=()=>!PREFLIGHT&&(data as any).mode==='full'?(sections.find(s=>s.id===(data.frames as any[])[frame()]?.id)??sections[sections.length-1]):(sections.find(s=>t()>=s.start&&t()<s.end)??sections[sections.length-1]);
 const elapsed=()=>t()-section().start;
 const is=(...ids:string[])=>ids.includes(section().id),knight=()=>section().kind.startsWith('knight'),game=()=>section().kind==='game',comparison=()=>section().kind==='wall-ab';
 const definition=()=>is('normal-definition','normal-data')&&elapsed()<1.65;
 const sparseRecord=()=>section().kind==='knight-source'?(frozenSpriteProof.frames as any[]).find(f=>f.id==='07-knight-source'):section().kind==='knight-pipeline'?(frozenSpriteProof.frames as any[]).find(f=>f.id==='12-knight-pipeline'):(data.frames as any[]).find(f=>f.id===sparse[section().id]);
 const record=()=>PREFLIGHT||(data as any).mode!=='full'?sparseRecord():(data.frames as any[])[frame()];
 const previewPicture=()=>section().kind==='knight-source'?ROOT+'capture-preview-v3/07-knight-source.png':section().kind==='knight-pipeline'?ROOT+'capture-preview-v3/12-knight-pipeline.png':ROOT+PREVIEW+'/'+(sparse[section().id]??'grid-on')+'.png';
 const probe=()=>record()?.probe,spatialScale=()=>record()?.gridRenderedNative ? .78 : 1,point=(p:any)=>new Vector2(((p?.x??540)-540)*1000/1080*spatialScale(),((p?.y??540)-540)*1000/1080*spatialScale());
 const reaction=()=>reactionPresence(t);
 view.fill('#000000');
 const world=new Node({y:()=>is('shared-normal','normal-definition','grid-flat','pixel-normal')?-35:0,x:()=>-30-120*reaction(),scale:()=>1-.19*reaction()});view.add(world);
 const picture=new Rect({width:1000,height:1000,clip:true,y:()=>is('knight-bake')?-160:0,opacity:()=>comparison()||game()?0:(definition()?0.25:1)});world.add(picture);
 picture.add(<Img src={()=>game()?ROOT+PREVIEW+'/grid-on.png':PREFLIGHT||(data as any).mode!=='full'?previewPicture():ROOT+(record()?.nativeFrameDirectory??CAPTURE)+'/frames/frame-'+String(frame()).padStart(5,'0')+'.png'} width={1000} height={1000} scale={spatialScale}/>);
 world.add(createNormalGrid({record,elapsed,enabled:()=>!definition()&&is('shared-normal','normal-definition','grid-flat','pixel-normal'),point}));
 const rgbPhase=():RGBPhase=>is('rgb-signed')?'signed':is('rgb-encoding')?'packing':is('neutral-purple')?'neutral':'none';
 const rgbStep=()=>Math.max(0,(section().events??[]).filter((event:any)=>frame()>=event.startFrame).length-1);
 world.add(createNormalRGB({phase:rgbPhase,elapsed,step:rgbStep}));
 const rgbChannels=new Node({opacity:()=>is('normal-data')?1:0});world.add(rgbChannels);
 rgbChannels.add(<Rect width={920} height={85} position={[0,255]} fill="#000000"/>);
 for(const [x,text,colour] of [[-300,'R = 빨강',C.red],[0,'G = 초록',C.green],[300,'B = 파랑','#8AB6F0']] as const)rgbChannels.add(<Txt text={text} position={[x,255]} fontFamily={FONT} fontSize={37} fontWeight={700} fill={colour}/>);
 world.add(createDeadCellsGameplay({enabled:game,localFrame:()=>Math.max(0,frame()-(game()?section().startFrame:0)),sourceSeconds:()=>game()?section().sourceStart+elapsed():30}));
 // These leaders reference our actual GPU probe and the real TBN/light directions.
 const normalLabels=new Node({opacity:()=>is('light-facing','light-sideways')?1:0});world.add(normalLabels);
 for(const [key,text,colour,x,y] of [['geometryNormalScreenEnd','원래 면의 방향',C.white,-275,175],['normalScreenEnd','빛 계산 방향',C.green,-250,240],['lightScreenEnd','광원 쪽 방향',C.yellow,260,175]] as const){
  const visible=()=>key==='geometryNormalScreenEnd'||!is('shared-normal','normal-definition');
  normalLabels.add(<Line points={()=>[[x,y-22],point(probe()?.[key])]} stroke={colour} lineWidth={3} end={()=>visible()?clamp((elapsed()-.15)/.45):0}/>);
  normalLabels.add(<Txt text={key==='geometryNormalScreenEnd'?'원래 면의 방향':text} position={[x,y]} fontFamily={FONT} fontSize={36} fontWeight={700} fill={colour} opacity={()=>visible()?1:0}/>);
 }
 const lightValue=new Node({position:[260,250],opacity:()=>is('light-facing','light-sideways')?1:0});world.add(lightValue);
 lightValue.add(<Rect width={440} height={112} fill="#000000"/>);
 lightValue.add(<Txt text="이 빛을 받는 정도" fontFamily={FONT} fontSize={34} fill={C.muted} position={[0,-27]}/>);
 lightValue.add(<Txt text={()=>Math.round((probe()?.gpuNDotL??0)*100)+'%'} fontFamily={FONT} fontSize={52} fontWeight={700} fill={()=>is('light-facing')?C.green:C.red} position={[0,27]}/>);
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
  pane.add(<Img src={()=>PREFLIGHT||(data as any).mode!=='full'||!comparison()?ROOT+PREVIEW+'/'+(i===0?'grid-off':'grid-on')+'.png':ROOT+CAPTURE+'/ab-'+(i===0?'off':'on')+'/frame-'+String(frame()).padStart(5,'0')+'.png'} width={455} height={455}/>);
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
 view.add(<Txt text={()=>game()?'데드셀 · 실제 플레이':t()<(sections.find(s=>s.id==='normal-definition')?.start??0)?'같은 벽 · 같은 메시':t()<(sections.find(s=>s.id==='normal-data')?.start??0)?'Normal · 법선':'Normal Map · 노멀 맵'} fontFamily={FONT} fontSize={34} fontWeight={700} fill={C.teal} position={[-235,-480]}/>);
 view.add(<Txt text={()=>game()?'실제 게임 화면':knight()?'우리 재현 · 1프레임':'우리 Unity 구현'} fontFamily={FONT} fontSize={34} fill={C.muted} position={[305,-480]}/>);
 const card=new Node({opacity:()=>definition()?1:0});view.add(card);
 card.add(<Txt text={()=>is('normal-definition')?'Normal':'Normal Map'} fontFamily={FONT} fontSize={47} fill={C.teal} position={[-30,-320]}/>);
 card.add(<Txt text={()=>is('normal-definition')?'법선':'노멀 맵'} fontFamily={FONT} fontSize={60} fontWeight={700} fill={C.yellow} position={[-30,-245]}/>);
 card.add(<Txt text={()=>is('normal-definition')?'표면에서 수직으로 나가는 방향':'픽셀별 표면 방향을 담은 그림'} fontFamily={FONT} fontSize={36} fill={C.white} position={[-30,-165]}/>);
 view.add(<Txt text={()=>is('silhouette')?'옆에서 보면, 평면':is('knight-source','knight-light')?'데드셀 방식 · 우리 에셋으로 재현':''} fontFamily={FONT} fontSize={36} fontWeight={700} fill={C.yellow} position={[-30,265]}/>);
 view.add(createReactionMascot(t));
 // Final clause/keyword ASS is encoded above all nodes and the mascot.
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
