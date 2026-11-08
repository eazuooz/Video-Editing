// New user-selected refinements, using real exported pixels and the same game.
const {createCanvas}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
module.exports=function extra(a,row,t,d){
 const {c,C,images,txt,rect,line,arrow,wrap,image,tag,code,sprite,gameView,runtime,cue}=a,p=t/d,id=row.id;
 if(id==='V31'){
  const before=createCanvas(96,132),bc=before.getContext('2d');bc.imageSmoothingEnabled=true;bc.drawImage(images.oldidle,0,0,96,132);
  for(const [x,title,im,col] of [[240,'이전 · 축소 시 픽셀 혼합',before,C.red],[1140,'수정 · 실제 표시 격자',images.nativeidle,C.teal]]){
   image(im,x,235,384,528);tag(title,x-70,215,col);line(x-20,763,x+404,763,col,3);
  }
  arrow(790,490,1030,490,C.yellow);tag('PixelOE → 같은 팔레트',790,390,C.yellow);
  txt('96 × 132  /  32 colors  /  alpha 0·255',960,820,38,C.yellow,true,'center');
  if(p>.65){tag('Nearest Neighbor (최근접 보간)',1050,865,C.teal);}
  return true;
 }
 if(id==='V32'){
  const stride=[38,83],distance=t*62;txt('동일한 실제 이동 거리 → 서로 다른 보행 주기',95,230,39,C.yellow,true);
  stride.forEach((n,i)=>{
   const baseline=505+i*330,x=250+(distance%610)*2,idx=Math.floor((distance/n%1)*8),im=images['nativewalk'+idx];
   line(100,baseline,1810,baseline,C.line,4);c.imageSmoothingEnabled=false;c.drawImage(im,x-96,baseline-250,192,264);
   tag(i?'수정 · 83 px / cycle':'이전 · 38 px / cycle',120,baseline-245,i?C.teal:C.red);
   txt(`자세 ${idx+1} / 8`,1680,baseline-100,32,i?C.teal:C.red,true,'center');
   if(p>.28){const stance=[69,64,53,31.5,27,64,50.5,28][idx],fx=x+(stance-48)*2;line(fx-16,baseline-4,fx+16,baseline-4,C.yellow,5);}
  });
  if(p>.62)tag('이동 거리 / 한 주기의 거리 → 현재 자세',790,865,C.yellow);
  return true;
 }
 if(id==='V33'){
  gameView(80,215,1280,721);tag('같은 게임의 중앙 작업대',100,245,C.teal);
  const labels=['접근 → 몸 낮추기','장부 · 손 · 펜 접촉','몸 고정 · 팔과 펜만 반복'];labels.forEach((s,i)=>wrap(s,1410,300+i*145,450,35,i===Math.min(2,Math.floor(p*3))?C.yellow:C.white));
  if(p>.54){image('ledgerlarge',1410,750,420,150);tag('Pixelbolt · 56 × 20',1410,855,C.teal);}
  return true;
 }
 if(id==='V34'){
  const day=cue(id,'낮에는',d*.3),dark=cue(id,'밤에는',d*.48),night=t<day||t>=dark;runtime.game.weather(night?'night':'sun');gameView(80,215,1280,721);
  txt(night?'밤 · 두 광원을 켬':'낮 · 불을 끔',1420,300,41,C.yellow,true);wrap('불꽃 아래끝 ↔ 심지\n빛의 중심 ↔ 같은 좌표',1420,440,420,36);
  for(const [sx,sy,label]of [[166,43,'랜턴 심지'],[250,127,'촛불 심지']]){
   const x=80+sx/426*1280,y=215+sy/240*721;line(x-14,y,x+14,y,C.yellow,4);line(x,y-14,x,y+14,C.yellow,4);arrow(x+100,y-60,x+15,y-10,C.yellow);tag(label,x+110,y-65,C.yellow);
  }
  tag('2D 빛 표현 · 물리 조도 측정 아님',1410,810,C.muted);return true;
 }
 if(id==='V35'){
  const music=cue(id,'작업실 라디오',d*.16),controls=cue(id,'다음 곡',d*.54);
  if(images.radioUI&&t>=music){
   const ui=images.radioUI,zoom=t>=controls;
   c.imageSmoothingEnabled=true;
   if(zoom)c.drawImage(ui,340,1325,1265,190,100,320,1720,258);
   else c.drawImage(ui,340,1325,1265,445,100,260,1720,605);
   tag('실제 공개 웹페이지 · 라디오',100,220,C.teal);
   if(zoom){['재생 / 일시 정지','다음 곡 · 순서 섞기','음량'].forEach((s,i)=>txt(s,[330,720,1590][i],690,40,C.yellow,true,'center'));arrow(330,650,315,505);arrow(720,650,490,505);arrow(1590,650,1680,505);txt('20곡 → 마지막 곡 뒤 처음으로',960,820,40,C.white,true,'center');}
  }else{gameView(80,215,1270,715);tag('실제 웹 게임 실행',100,245,C.teal);wrap('다섯 행동 · 네 날씨\n더보기에서 직접 플레이',1410,390,450,37,C.yellow)}
  return true;
 }
 return false;
};
