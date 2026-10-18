import {makeScene2D,Video,Txt,Rect,Line} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import trace from '../../../../projects/shorts-forgiving-hitbox/production/local/capture-full-v1/trace.json';
import timing from '../../../../projects/shorts-forgiving-hitbox/production/local/visual-timing.json';

// All bounds and health values come from Unity's actual collider queries.
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',muted:'#B8C3BC',forest:'#073C32'};
export default makeScene2D(function*(view){
  const t=createSignal(0);const state=()=>trace.frames[Math.min(1799,Math.floor(t()*60+1e-5))];
  const shown=()=>t()>=timing.revealStart;
  const point=(p:{x:number,y:number})=>new Vector2(p.x-540,p.y-960);
  const outline=(key:'hurt'|'attack')=>{const a=state()[key].map(point);return [...a,a[0]];};
  const progress=()=>Math.max(0,Math.min(1,(t()-timing.revealStart)/.55));
  const activeAttack=()=>{const s=timing.shots.find(s=>s.id===state().shot)!;return t()>=s.attackStart&&t()<s.attackStart+s.attackSeconds&&state().projectile.y>650&&state().projectile.y<1235;};
  view.fill('#000000');
  view.add(<Video src="/@fs/D:/Github/VideoEditing/projects/shorts-forgiving-hitbox/production/local/capture-full-v1/unity-master.mp4" width={1080} height={1920} time={()=>Math.min(t(),29.983333)} />);
  // End the demonstration viewport at the platform, before the fixed captions.
  view.add(<Rect width={1080} height={622} position={[0,649]} fill="#000000" />);
  view.add(<Rect width={1080} height={600} position={[0,-660]} fill="#000000" />);
  view.add(<Txt text="얌얌코딩" fontFamily="Malgun Gothic" fontWeight={700} fontSize={37} fill={C.muted} position={[-340,-820]} />);
  view.add(<Txt text="닿았는데" fontFamily="Malgun Gothic" fontWeight={700} fontSize={88} fill={C.white} position={[-30,-700]} />);
  view.add(<Txt text="왜 안 맞았지?" fontFamily="Malgun Gothic" fontWeight={700} fontSize={88} fill={C.yellow} position={[-30,-590]} />);
  view.add(<Txt text="Unity 직접 시연" fontFamily="Malgun Gothic" fontSize={30} fill={C.muted} position={[-30,-490]} />);
  view.add(<Txt text="체력" fontFamily="Malgun Gothic" fontWeight={700} fontSize={42} fill={C.white} position={[-225,-390]} />);
  view.add(<Rect width={300} height={35} fill="#23392F" stroke={C.white} lineWidth={2} position={[10,-390]} />);
  view.add(<Rect width={()=>300*state().health/100} height={31} fill={()=>state().health===100?C.green:C.red} position={()=>[-140+150*state().health/100,-390]} />);
  view.add(<Txt text={()=>String(state().health)} fontFamily="Malgun Gothic" fontWeight={700} fontSize={46} fill={C.white} position={[220,-390]} />);
  view.add(<Line points={()=>outline('hurt')} stroke={C.green} lineWidth={7} end={progress} opacity={()=>shown()?1:0} />);
  view.add(<Line points={()=>outline('attack')} stroke={C.red} lineWidth={7} opacity={()=>t()>=timing.attackRevealStart&&activeAttack()?1:0} />);
  view.add(<Txt text={'피격 영역\nHurtbox'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={36} lineHeight={44} fill={C.green} position={[-365,-25]} opacity={()=>shown()?1:0} />);
  view.add(<Line points={()=>[new Vector2(-270,-25),new Vector2(Math.min(...state().hurt.map(p=>p.x))-555,-25)]} stroke={C.green} lineWidth={5} endArrow arrowSize={12} opacity={()=>shown()?1:0} />);
  view.add(<Txt text={'공격 영역\nHitbox'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={32} lineHeight={40} fill={C.red} position={[310,-170]} opacity={()=>t()>=timing.attackRevealStart&&activeAttack()?1:0} />);
  view.add(<Line points={()=>[new Vector2(250,-120),new Vector2(Math.max(...state().attack.map(p=>p.x))-530,state().projectile.y-970)]} stroke={C.red} lineWidth={5} endArrow arrowSize={12} opacity={()=>t()>=timing.attackRevealStart&&activeAttack()?1:0} />);
  view.add(<Txt text={()=>state().shot==='03-wide'?'몸 크기로\n설정':state().shot==='05-resolution'?'처음 장면\n느리게 확인':shown()?'조금 작게\n설정':''} fontFamily="Malgun Gothic" fontWeight={700} fontSize={34} lineHeight={43} fill={C.white} position={[-365,170]} />);
  view.add(<Txt text={()=>state().hitApplied?'겹침 → 피해 30':t()>1.65?'겹치지 않음 → 피해 0':''} fontFamily="Malgun Gothic" fontWeight={700} fontSize={38} fill={()=>state().hitApplied?C.red:C.green} position={[-30,-335]} opacity={()=>t()<timing.revealStart?0:1} />);
  // Fixed captions are encoded once after this clean composition.
  view.add(<Txt text={'그림은 스쳐도,\n판정은 겹치지 않았다'} fontFamily="Malgun Gothic" fontWeight={700} fontSize={54} lineHeight={72} fill={C.yellow} position={[-30,420]} opacity={()=>t()>=27?1:0} />);
  yield* t(30,30,linear);
});
