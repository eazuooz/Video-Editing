import {Line,Node,Rect,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createRef,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
export default makeScene2D(function*(view){
 const left=createRef<Node>(),right=createRef<Node>(),limits=createRef<Node>();view.fill(P.background);
 const card=(title:string,detail:string,color:string)=><><Rect width={720} height={235} x={11} y={12} rotation={-1} fill={'#dfe5e8'}/><Rect width={720} height={235} rotation={-1} fill={'white'} stroke={color} lineWidth={2}/><Txt text={title} y={-63} fontFamily={P.font} fontSize={37} fontWeight={700} fill={color}/><Txt text={detail} y={42} fontFamily={P.font} fontSize={29} lineHeight={44} fill={P.ink} textAlign={'center'}/></>;
 view.add(<><Txt text={'관찰한 물약 화면의 상태'} x={-850} y={-392} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/><Txt text={'선택 변화와 남아 있는 안내를 따로 읽습니다'} x={-850} y={-316} offset={[-1,0]} fontFamily={P.font} fontSize={28} fill={P.muted}/>
 <Node ref={left} x={-440} y={-50} opacity={0}>{card('선택한 항목','약한 회복 물약 → 다음 물약',P.blue)}</Node>
 <Node ref={right} x={440} y={-50} opacity={0}>{card('동시에 남은 안내','완료 표시\n재료가 부족하다는 문구',P.red)}</Node>
 <Line points={[[-68,-50],[68,-50]]} stroke={P.line} lineWidth={4} endArrow arrowSize={14}/>
 <Node ref={limits} y={232} opacity={0}><Rect x={11} y={12} width={1630} height={100} fill={'#dfe5e8'}/><Rect width={1630} height={100} fill={'white'} stroke={P.green} lineWidth={2}/><Txt text={'정상적인 지불 · 획득 과정은 이 편집만으로 확정하지 않습니다'} fontFamily={P.font} fontSize={31} fill={P.green} fontWeight={600}/></Node></>);
 yield*all(left().opacity(1,.35),left().y(-58,.35));yield*waitFor(1.45);yield*all(right().opacity(1,.4),right().y(-58,.4));yield*waitFor(1.8);yield*limits().opacity(1,.4);yield*waitFor(1.6);
});
