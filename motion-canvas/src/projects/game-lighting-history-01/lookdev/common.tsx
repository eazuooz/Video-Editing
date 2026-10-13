import {Node,Rect,Txt} from '@motion-canvas/2d';
import {PAPER as P} from '../../../styles/research-paper';
export function caption(text:()=>string){return <Node position={[0,430]}>
 <Rect position={[8,8]} size={[1460,124]} fill={'#355344'}/>
 <Rect size={[1460,124]} fill={'white'} stroke={'#111111'} lineWidth={2}/>
 <Txt text={text} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111111'} textAlign={'center'}/>
</Node>;}
export function note(text:()=>string){return <Txt y={330} text={text} fontFamily={P.font} fontSize={26} fill={P.muted}/>;}
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));
