// Original executable prototype, shared by the interactive test page and film.
// Replays call the same state transition as actual keyboard/click input.
export type ChestState={opened:boolean;keys:number;items:number[];message:string;changed:number;openedAt:number};
export function initialState():ChestState{return{opened:false,keys:1,items:[],message:'상자를 찾아 열어보세요',changed:-100,openedAt:-100};}
export function openChest(s:ChestState,t=0):ChestState {
  if(s.opened)return{...s,message:'이미 열린 상자입니다',changed:t};
  if(s.keys===0)return{...s,message:'열쇠가 필요합니다',changed:t};
  if(s.items.length>=4)return{...s,message:'가방이 가득 찼습니다',changed:t};
  return{...s,opened:true,keys:s.keys-1,items:[...s.items,100],message:'보상 +1  ·  가방에 보관했습니다',changed:t,openedAt:t};
}
export const exampleEvents:Record<number,[number,string][]>={
  0:[[3,'no-key'],[5,'open'],[8,'key'],[10,'open'],[15,'open']],
  1:[[3,'key'],[7,'open'],[13,'open']],
  2:[[2,'no-key'],[4,'open'],[7,'full'],[9,'open'],[12,'reset'],[14,'open'],[17,'open']],
  3:[[5,'open'],[13,'open']],
  4:[[3,'open'],[6,'open'],[10,'full'],[13,'open'],[16,'reset'],[18,'open']],
  7:[[9,'key'],[13,'open'],[17,'open']],
  8:[[4,'no-key'],[6,'open'],[10,'key'],[13,'open'],[17,'open']]
};
export function replay(index:number,t:number){
  let s=initialState();
  for(const [at,action] of exampleEvents[index]??[]) {
    if(at>t)break;
    if(action==='open')s=openChest(s,at);
    else if(action==='no-key')s={...initialState(),keys:0,message:'열쇠 없는 상태',changed:at};
    else if(action==='key')s={...s,keys:1,message:'열쇠를 주웠습니다',changed:at};
    else if(action==='full')s={...initialState(),items:[1,2,3,4],message:'가방이 가득 찬 상태',changed:at};
    else s={...initialState(),message:'다시 테스트',changed:at};
  }
  return s;
}
export function drawPrototype(c:CanvasRenderingContext2D,index:number,t:number,manual?:ChestState){
  const s=manual??replay(index,t),smooth=(v:number)=>{v=Math.max(0,Math.min(1,v));return v*v*(3-2*v);};
  c.save();c.fillStyle='#f6f8fb';c.fillRect(0,0,1920,1080);
  const text=(a:string,x:number,y:number,size=30,color='#202020',weight=500)=>{c.fillStyle=color;c.font=`${weight} ${size}px 'Malgun Gothic', sans-serif`;c.fillText(a,x,y);};
  const rect=(x:number,y:number,w:number,h:number,color:string)=>{c.fillStyle=color;c.fillRect(x,y,w,h);};
  const poly=(pts:number[][],color:string)=>{c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();c.fillStyle=color;c.fill();};
  const project=(x:number,z:number,h=0)=>[1090+(x-z)*.82,480+(x+z)*.36-h];
  const cube=(x:number,z:number,w:number,d:number,h:number,colors:string[],lift=0)=>{
    const q=[project(x,z,lift),project(x+w,z,lift),project(x+w,z+d,lift),project(x,z+d,lift)],u=[project(x,z,h+lift),project(x+w,z,h+lift),project(x+w,z+d,h+lift),project(x,z+d,h+lift)];
    poly([q[1],q[2],u[2],u[1]],colors[1]);poly([q[2],q[3],u[3],u[2]],colors[2]);poly(u,colors[0]);
  };
  text(index===2?'규칙을 바꾸고, 직접 확인하기':index===3?'실행과 상태':index===4?'같은 입력을 두 번 보낸다면?':index===7?'발견하기 어려운 배치 → 다시 배치':index===8?'작게 만들고, 다시 실행하기':'상자 하나를 만드는 일',100,112,48,'#202020',700);
  text('PLAY TEST',102,164,22,'#2f5faa',600);
  for(let x=-400;x<400;x+=100)for(let z=-350;z<350;z+=100)cube(x,z,98,98,22,[(x+z)%200===0?'#e4eaf1':'#ecf0f4','#c7d3df','#d6dfe9']);
  cube(220,-210,160,90,80,['#a7b7aa','#869c91','#94aa9e']);
  cube(-280,150,85,100,64,['#b8c0c9','#8b9aab','#9faeba']);
  const move=index===7?smooth((t-7)/3):1,chestX=index===7?210-290*move:-80,chestZ=index===7?-220+195*move:-25;
  const opened=s.opened?smooth((t-s.openedAt)/.7):0;
  cube(chestX,chestZ,170,115,100,['#29456f','#315d94','#507cb1']);
  cube(chestX-4,chestZ-4,178,123,16,['#dbbe66','#b59c4e','#efd88e'],100+opened*65);
  cube(chestX+70,chestZ+118,28,6,32,['#f3da75','#c4ab51','#e7cd7b'],45);
  if(s.opened){const p=project(chestX+85,chestZ+55,220);c.beginPath();c.arc(p[0],p[1]+Math.sin(t*2)*5,18,0,Math.PI*2);c.fillStyle='#edcc5a';c.fill();}
  const walk=smooth(t/6),p=project(-280+170*walk,-30+110*walk,42);
  c.fillStyle='#2f5faa';c.beginPath();c.ellipse(p[0],p[1]+27,25,11,0,0,Math.PI*2);c.fill();rect(p[0]-16,p[1]-20,32,45,'#315d94');c.beginPath();c.arc(p[0],p[1]-32,20,0,Math.PI*2);c.fillStyle='#f3da75';c.fill();
  rect(94,240,530,430,'#fff');text('STATE',124,290,22,'#737373');
  text('열쇠',126,349);text(String(s.keys),494,349,38,'#2f5faa',700);
  text('상자',126,411);text(s.opened?'열림':'닫힘',455,411,32,'#2f5faa',700);
  text('가방',126,473);text(`${s.items.length} / 4`,451,473,32,'#2f5faa',700);
  for(let i=0;i<4;i++){rect(126+i*104,518,88,76,'#edf1f5');if(i<s.items.length){c.beginPath();c.arc(170+i*104,556,19,0,Math.PI*2);c.fillStyle='#e4c866';c.fill();}}
  text(s.message,112,769,34,s.message.includes('필요')||s.message.includes('가득')?'#ad4b31':'#2f5faa',600);
  // Keep all interactive information above the reserved caption zone (y >= 850).
  text('SPACE / 클릭 · 열기     R · 다시 시작',112,824,23,'#737373');
  c.restore();
}
