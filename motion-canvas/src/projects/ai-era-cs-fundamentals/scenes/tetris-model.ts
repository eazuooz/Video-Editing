// Deliberately small educational rule set, not the commercial SRS rotation system.
export type Cell = readonly [number, number];
export type Board = number[][];
export const emptyBoard = (w=10,h=20):Board => Array.from({length:h},()=>Array(w).fill(0));
export function fits(board:Board,cells:readonly Cell[],x:number,y:number):boolean {
  return cells.every(([dx,dy])=>{const cx=x+dx,cy=y+dy;return cy>=0&&cy<board.length&&cx>=0&&cx<board[0].length&&board[cy][cx]===0;});
}
export function lock(board:Board,cells:readonly Cell[],x:number,y:number):Board {
  if(!fits(board,cells,x,y)) throw Error('Collision: cannot lock here');
  const copy=board.map(row=>[...row]);cells.forEach(([dx,dy])=>copy[y+dy][x+dx]=1);return copy;
}
export function clearLines(board:Board):{board:Board;cleared:number} {
  const kept=board.filter(row=>!row.every(Boolean)).map(row=>[...row]);
  const cleared=board.length-kept.length;
  return {board:[...emptyBoard(board[0].length,cleared),...kept],cleared};
}
export const I_VERTICAL:readonly Cell[]=[[0,0],[0,1],[0,2],[0,3]];
export function demoBoard(lines=4):Board {
  if(!Number.isInteger(lines)||lines<1||lines>4)throw Error('Demo supports one to four completed rows');
  const board=emptyBoard();
  for(let y=20-lines;y<20;y++)for(let x=0;x<10;x++)if(x!==6)board[y][x]=1;
  board[19-lines][0]=1;board[19-lines][1]=1;
  return board;
}
