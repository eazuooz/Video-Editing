import {makeScene2D,Node,Txt} from '@motion-canvas/2d';
import {createSignal,useThread} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,heading,V3} from '../../game-lighting-history-shared/depth-space';

// The complete last sentence is retained, with exact selected PCM binding in plan.
export default makeScene2D(function*(view){
 view.fill(P.background);
 const p=createSignal(0),world=depthSpace(()=>18+10*p(),[0,35],1),motion=()=>Math.max(0,Math.min(1,(p()-.28)/.48));
 view.add(heading('자료 → 관찰','표면 자료를 실제 움직임에 연결','형태는 이어지고, 밝은 무늬는 시점에 따라 달라집니다','게임 렌더링 역사 · 모바일 관찰'));
 const platform=(x:number)=><Node>{world.box(x,0,0,510,290,30,P.surfaceTop)}{world.box(x,0,30,110,100,145,P.teal)}</Node>;
 view.add(<Node>
  {platform(-390)}
  {platform(400)}
  {world.label('물체의 형태',-390,0,220,34,P.ink)}
  {world.label('움직이는 화면',400,0,220,34,P.ink)}
  {world.polygon(()=>{const x=350+120*motion();return [[x-65,-95,31],[x+65,-95,31],[x+65,95,31],[x-65,95,31]] as V3[];},P.orange,P.orange)}
  {world.box(400,0,30,110,100,145,P.teal)}
  {world.path(()=>[[-230,-30,100],[30,-30,100],[240,-30,100]],P.red,()=>Math.max(0,Math.min(1,(p()-.58)/.36)))}
  {world.label('형태 자료',-390,165,20,30,P.teal)}
  {world.label('빛의 결과',400,165,20,30,P.orange)}
  <Txt text={'설명용 모형 · 실제 시연의 내부 구현을 증명하지 않습니다'} y={327} fill={P.muted} fontFamily={P.font} fontSize={26}/>
 </Node>);
 const thread=useThread(),start=thread.fixed;
 while(true){const frame=Math.round((thread.fixed-start)*60);if(frame>=252)break;p(frame/251);yield;}
});
