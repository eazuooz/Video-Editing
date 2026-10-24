import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-interior-mapping-window/production/visual-timing.json';
import native from '../../../../projects/shorts-interior-mapping-window/production/local/capture-full/readback.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'};
const FONT='Malgun Gothic',ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-interior-mapping-window/production/local/';
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number)=>Math.min(1,Math.max(0,x));
 const frame=()=>Math.min(timing.frames-1,Math.floor(t()*60+.0001)),rec=()=>native.records[frame()] as any;
 const section=()=>timing.sections.find(s=>frame()>=s.startFrame&&frame()<s.endFrame)??timing.sections.at(-1)!,id=()=>section().id,e=()=>t()-section().start;
 const is=(...ids:string[])=>ids.includes(id()),q=timing.cueStarts as Record<string,number>,presence=()=>reactionPresence(t);
 const image=()=>ROOT+'capture-full/frames/'+String(frame()).padStart(5,'0')+'.jpg';
 const flat=()=>ROOT+'capture-full/flat/'+String(frame()).padStart(5,'0')+'.jpg';
 const point=(p:any)=>new Vector2((p.x-540)*1000/1080,(p.y-540)*1000/1080);
 view.fill('#000');
 const world=new Node({position:()=>[-20-135*presence(),-50],scale:()=>1-.17*presence()});view.add(world);
 world.add(<Img src={image} size={1000} opacity={()=>is('game','compare')?0:1}/>);
 const game=new Rect({position:[-20,-70],width:1000,height:810,clip:true,opacity:()=>is('game')?1:0});view.add(game);
 game.add(<Img src={()=>ROOT+'game-frames/'+String(Math.min(frame(),timing.sections[0].endFrame-1)).padStart(5,'0')+'.jpg'} width={1920} height={810}/>);
 // A restrained look-here mark highlights visible windows, not hidden geometry.
 game.add(<Rect position={()=>[-300-100*(e()-2),30]} width={100} height={260} stroke={C.green} lineWidth={6} radius={12} opacity={()=>e()>=2&&e()<3.1?Math.min(clamp((e()-2)/.12),clamp((3.1-e())/.12)):0}/>);
 game.add(<Txt text="심시티 · 창문을 보세요" position={[-110,-300]} fill={C.yellow} fontFamily={FONT} fontSize={43} fontWeight={700}/>);
 const labels:any={hero:'평면에 그린 방의 깊이',plane:'옆에서 보면 평면 하나',pixelIntro:'픽셀 = 화면의 작은 한 점',ray:'카메라에서 창문 픽셀로',room:'창문 뒤에 방을 가정한다',sample:'먼저 닿는 벽의 무늬를 읽는다',move:'카메라 이동 → 보이는 벽 변화',pixels:'화면의 각 픽셀에서 계산',close:'모델 대신, 보이는 깊이를 계산'};
 world.add(<Txt text={()=>is('game','compare')?'':labels[id()]} position={[-5,-315]} fill={C.yellow} fontFamily={FONT} fontSize={43} fontWeight={700}/>);
 world.add(<Txt text={()=>is('plane')?'우리 창문 메시 · 삼각형 2개':is('move')?'바꾸는 것은 카메라 위치뿐':is('pixels')?'방의 입체 메시 추가: 0개':is('close')?'가구도 벽에 그려진 무늬':''} position={[-5,355]} fill={C.white} fontFamily={FONT} fontSize={37}/>);
 const diagram=new Node({opacity:()=>is('ray','room','sample')?1:0});world.add(diagram);
 const attach=(key:string,label:string,colour:string,dx:number,dy:number)=>{
  const p=()=>point(rec()[key]);
  diagram.add(<Line points={()=>[p(),p().add(new Vector2(dx,dy))]} stroke={colour} lineWidth={4} opacity={()=>key==='screenHit'&&is('ray')?0:1}/>);
  diagram.add(<Txt text={label} position={()=>p().add(new Vector2(dx,dy+24))} fill={colour} fontFamily={FONT} fontSize={35} fontWeight={700} opacity={()=>key==='screenHit'&&is('ray')?0:1}/>);
 };
 attach('screenViewer','카메라',C.teal,-50,60);attach('screenEntry','창문 픽셀',C.white,-100,100);attach('screenHit','교차점',C.yellow,35,-65);
 diagram.add(<Txt text="선과 상자 = 계산을 보여주는 안내선" position={[-5,330]} fill={C.muted} fontFamily={FONT} fontSize={30}/>);
 diagram.add(<Line points={()=>[point(rec().screenHit).add(new Vector2(0,25)),point(rec().screenEntry).add(new Vector2(0,25))]} stroke={C.teal} lineWidth={6} endArrow arrowSize={18} end={()=>clamp((t()-q['p5-2'])/.8)} opacity={()=>is('sample')&&t()>=q['p5-2']?1:0}/>);
 const steps=['시선','닿는 벽','색 읽기'];
 for(let i=0;i<3;i++)diagram.add(<Txt text={(i+1)+'. '+steps[i]} position={[-285+i*285,-235]} fill={()=>i===(is('sample')?2:is('room')?1:0)?C.yellow:C.muted} fontFamily={FONT} fontSize={38}/>);
 const compare=new Node({opacity:()=>is('compare')?1:0});view.add(compare);
 for(let i=0;i<2;i++){
  const x=i===0?-265:245;
  compare.add(<Img src={()=>is('compare')?(i===0?flat():image()):image()} size={520} position={[x,-70]}/>);
  compare.add(<Rect position={[x,-70]} size={510} stroke={i===0?C.red:C.teal} lineWidth={4}/>);
  compare.add(<Txt text={i===0?'고정된 방 사진':'인테리어 매핑'} position={[x,-370]} fontFamily={FONT} fontSize={40} fill={i===0?C.red:C.teal} fontWeight={700}/>);
 }
 compare.add(<Txt text="같은 카메라 이동 · 같은 창문 메시" position={[-10,260]} fill={C.white} fontFamily={FONT} fontSize={38}/>);
 // Pixel sampling grid is an editorial overlay; it makes repetition explicit.
 for(let i=0;i<9;i++)for(let j=0;j<5;j++)world.add(<Circle position={[-300+i*75,-165+j*75]} size={9} fill={C.yellow} opacity={()=>is('pixels','pixelIntro')?clamp(e()*2-(i+j)*.1)*.85:0}/>);
 const header=(term:string,kind:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="540"><rect width="1080" height="540" fill="black"/><g font-family="Malgun Gothic" font-weight="700"><text x="128" y="128" font-size="37" fill="${C.muted}">얌얌코딩</text><text x="510" y="258" text-anchor="middle" font-size="77" fill="white">게임 속 창문 안에</text><text x="510" y="361" text-anchor="middle" font-size="77" fill="${C.yellow}">방이 없다고?</text><text x="100" y="490" font-size="31" fill="${C.teal}">${term}</text><text x="760" y="490" font-size="30" font-weight="400" fill="${C.muted}">${kind}</text></g></svg>`);
 const headers=[header('많은 창문, 방도 전부 만들까?','실제 게임'),header('Interior Mapping · 인테리어 매핑','Unity 구현'),header('Interior Mapping · 인테리어 매핑','구조 설명')];
 view.add(<Img src={()=>headers[is('game')?0:is('ray','room','sample','plane')?2:1]} width={1080} height={540} position={[0,-690]} zIndex={5}/>);
 view.add(createReactionMascot(t));
 yield view.toPromise();yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
