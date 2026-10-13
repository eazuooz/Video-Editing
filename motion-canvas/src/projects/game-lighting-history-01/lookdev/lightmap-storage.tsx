import {Circle, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createSignal, linear, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace, heading, V3} from '../../../shared/depth-diagrams';

// A conceptual irradiance bake, not a replica game or actual-footage quota.
// The sample map is deliberately fixed when the lamp moves after the bake.
export default makeScene2D(function* (view) {
  view.fill(P.background);
  const yaw=createSignal(31), bake=createSignal(0), transfer=createSignal(0), lampX=createSignal(-250);
  const phase=createSignal(0);
  const world=depthSpace(yaw,[0,50],1.12);
  const lamp:V3=[-250,-120,180];
  const lower:V3=[-295,-65,12],upper:V3=[-205,5,117];
  function blockHit(p:V3):V3|null{
    let enter=0,leave=1;
    for(let a=0;a<3;a++){
      const d=lamp[a]-p[a];
      if(Math.abs(d)<1e-8){if(p[a]<lower[a]||p[a]>upper[a])return null;continue;}
      const t1=(lower[a]-p[a])/d,t2=(upper[a]-p[a])/d;
      enter=Math.max(enter,Math.min(t1,t2));leave=Math.min(leave,Math.max(t1,t2));
    }
    if(enter>leave || leave<0 || enter>1)return null;
    return p.map((v,a)=>v+(lamp[a]-v)*leave) as V3;
  }
  const samples=Array.from({length:40},(_,i)=>{
    const x=-425+(i%8)*43,y=-144+Math.floor(i/8)*66,p:V3=[x,y,13];
    const dx=lamp[0]-x,dy=lamp[1]-y,dz=lamp[2]-13,r=Math.sqrt(dx*dx+dy*dy+dz*dz);
    const hit=blockHit(p),lit=hit===null,e=Math.min(1,.13+(lit?60000*dz/(r*r*r):0));
    const grey=Math.round(110+e*135),color='#'+[grey,Math.min(255,grey+6),grey].map(n=>n.toString(16).padStart(2,'0')).join('');
    return {p,hit,lit,color,index:i};
  });
  view.add(heading('04 · 1편','빛을 계산한 뒤, 표면에 저장한다','정적 표면의 베이크를 설명하는 개념 도식 · 최종 음성 전 무음 시안','게임 렌더링의 역사'));
  view.add(world.box(-265,0,0,385,355,12,'#dfe8df'));
  view.add(world.box(465,0,0,355,355,12,'#e5eaf1'));
  view.add(world.label('게임 공간',-265,195,0,29));
  view.add(world.label('별도 라이트맵',465,195,0,29));
  for(const s of samples){
    // Step through independent samples; avoid a one-card drop-shadow treatment.
    const verts=()=>{
      const [x,y]=s.p,t=transfer(),ax=313+(s.index%8)*43,ay=-144+Math.floor(s.index/8)*66;
      const X=x+(ax-x)*t,Y=y+(ay-y)*t;
      return [[X-20,Y-30,13],[X+20,Y-30,13],[X+20,Y+30,13],[X-20,Y+30,13]] as V3[];
    };
    const tile=world.polygon(verts,s.color,'#aab4aa');
    tile.opacity(()=>bake()>.02*s.index?1:.12);
    view.add(tile);
  }
  // The occluder sits above the sample plane and hides the tiles behind it.
  view.add(world.box(-250,-30,12,90,70,105,'#7791b5'));
  const rays=samples.filter(s=>[1,6,17,21,32,38].includes(s.index));
  for(const s of rays){
    const end=s.hit??s.p;
    const r=world.path(()=>[[lampX(),lamp[1],lamp[2]],end],s.lit?P.yellow:P.red,()=>Math.min(1,bake()*1.5));
    r.opacity(()=>1-transfer());view.add(r);
  }
  view.add(<Circle position={()=>world.point(lampX(),lamp[1],lamp[2])} size={42} fill={P.yellow} stroke={'#a48825'} lineWidth={3}/>);
  view.add(world.label('광원',()=>lampX()+70,lamp[1],lamp[2],27));
  view.add(<Line points={()=>[world.point(-30,0,75),world.point(235,0,75)]} stroke={P.blue} lineWidth={7} endArrow end={transfer} opacity={transfer}/>);
  view.add(<Txt text={()=>['표면 → 광원 : 가시성 확인','방향 · 거리 · 가림 반영','계산 결과를 텍스처에 저장','움직인 광원 ≠ 저장된 값'][Math.min(3,phase())]} y={327} fontFamily={P.font} fontSize={26} fill={P.muted}/>);
  const captions=[
    '표면의 작은 표본에서 광원까지\n가려지는지 먼저 확인합니다.',
    '가림과 방향·거리를 반영한 값을\n각 표본에 미리 계산합니다.',
    '이 값을 라이트맵에 저장해 두고\n게임 중에는 다시 읽습니다.',
    '광원만 옮겨도 저장된 값은 그대로라\n새 상태에는 다시 계산해야 합니다.',
  ];
  view.add(<Node position={[0,430]}>
    <Rect position={[8,8]} size={[1220,124]} fill={'#355344'}/>
    <Rect size={[1220,124]} fill={'#ffffff'} stroke={'#1a1a1a'} lineWidth={2}/>
    <Txt text={()=>captions[phase()]} fontFamily={P.font} fontSize={48} fontWeight={500} lineHeight={54} fill={'#111111'} textAlign={'center'}/>
  </Node>);
  yield* all(bake(.22,4,linear),yaw(34,4,linear));
  phase(1);yield* bake(1,5,linear);
  phase(2);yield* transfer(1,4,linear);yield* waitFor(1);
  phase(3);yield* all(lampX(-80,4,linear),yaw(39,4,linear));yield* waitFor(2);
});
