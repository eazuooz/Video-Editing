import {Node,Rect,Txt} from '@motion-canvas/2d';
import {PAPER} from '../../../styles/research-paper';
import {clearLines,demoBoard,I_VERTICAL,lock} from './tetris-model';

export function tetrisDiagram(parent:Node,p:()=>number,testing:boolean) {
  const lineCount=testing?2:4;
  const initial=demoBoard(lineCount), landed=lock(initial,I_VERTICAL,6,16), cleared=clearLines(landed).board;
  const board=new Node({x:-465,y:35,scale:.88});parent.add(board);
  board.add(<Rect width={322} height={642} fill={PAPER.panel} stroke={PAPER.ink} lineWidth={2} />);
  const state=()=>p()<.60?initial:p()<.78?landed:cleared;
  for(let y=0;y<20;y++)for(let x=0;x<10;x++)board.add(<Rect
    x={(x-4.5)*32} y={(y-9.5)*32} size={30} stroke={PAPER.line} lineWidth={.6}
    fill={()=>state()[y][x]?p()>.60&&p()<.78&&y>=20-lineCount?PAPER.yellow:PAPER.blueLight:PAPER.background} />);
  for(let n=0;n<4;n++)board.add(<Rect x={48} y={()=>(-9.5+Math.min(16,Math.floor(p()/.6*16))+n)*32}
    size={30} fill={PAPER.blue} opacity={()=>p()<.60?1:0} />);
  const notes=testing?[
    'WALL: 벽을 넘는 회전은 거절',
    'OVERLAP: 쌓인 칸과 겹치지 않기',
    'CLEAR: 완성된 줄을 동시에 삭제',
    'END: 종료 상태에서는 이동 금지',
  ]:[
    'BOARD: 10 × 20 배열',
    'MOVE: 다음 좌표의 충돌 검사',
    'LOCK: 내려갈 수 없으면 고정',
    'CLEAR: 완성된 줄 삭제 → 위 줄 이동',
  ];
  notes.forEach((text,i)=>parent.add(<Node x={410} y={-160+i*115}>
    <Rect width={890} height={93} fill={()=>Math.floor(p()*4)===i?PAPER.blueLight:PAPER.panel} />
    <Txt text={text} fontFamily={PAPER.font} fontSize={29} fill={PAPER.ink} />
  </Node>));
  parent.add(<Txt x={410} y={330} text={()=>p()<.6?'블록은 네 칸. 빈 공간으로만 이동.':p()<.78?`가득 찬 ${testing?'두':'네'} 줄을 함께 검사합니다.`:`${lineCount} LINES CLEARED  /  위의 블록도 아래로`} fontFamily={PAPER.font} fontSize={27} fill={PAPER.blue} />);
  parent.add(<Txt x={-465} y={365} text={'테트리스 규칙 학습용 자체 도식'} fontFamily={PAPER.font} fontSize={24} fill={PAPER.muted} />);
  if(testing) {
    // Rejected horizontal rotation at the right edge; do not mutate the board.
    for(let n=0;n<4;n++)board.add(<Rect x={(8+n-4.5)*32} y={-150} size={30} fill={PAPER.red} opacity={()=>p()>.10&&p()<.40?.65:0} />);
    board.add(<Txt text={'회전 거절'} x={0} y={-190} fontFamily={PAPER.font} fontSize={25} fill={PAPER.red} opacity={()=>p()>.10&&p()<.40?1:0} />);
  }
}
