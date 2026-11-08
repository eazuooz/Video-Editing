// The game source is the frozen public v6; screenshots are actual browser evidence.
module.exports=function(a,row,t,d){
 const {c,C,images,txt,rect,line,arrow,wrap,image,tag,code,sprite,gameView,runtime,cue}=a,id=row.id,p=t/d;
 if(['01','30'].includes(id)){
  gameView(80,210,1280,720);tag('실제 웹 게임 실행 · 최신 완성본',100,243,C.teal);
  const labels=id==='01'?['같은 캐릭터 유지','픽셀과 배경 정리','동작과 게임 연결']:['디자인 일관성','격자 · 색 · 투명도','게임 속 가독성'];
  labels.forEach((s,i)=>txt(s,1410,340+i*145,37,i===Math.min(2,Math.floor(p*3))?C.yellow:C.white,true));return true;
 }
 if(id==='02'){
  ['생성','정리','검수'].forEach((s,i)=>txt(s,345+i*615,250,50,C.yellow,true,'center'));
  image('turnaround',90,320,500,450,false);sprite('walk-right',t,780,325,300,412);gameView(1320,365,500,282);arrow(590,530,710,530);arrow(1180,530,1300,530);
  ['디자인 후보','픽셀 · 색 · 알파','실제 방에서 동작 확인'].forEach((s,i)=>txt(s,345+i*615,810,32,C.white,false,'center'));return true;
 }
 if(id==='15'){
  image('roomFinal',90,235,1160,653);sprite('map-read',t,580,440,235,324);if(t>cue(id,'배경 레이어에서는',d*.8)){rect(80,205,1220,700,C.bg);image('roomFinal',90,235,1160,653)}
  const reveal=Math.min(1,t/5);line(375,250,375,850,C.yellow,3);line(960,250,960,850,C.yellow,3);arrow(350,560,120,560,C.teal,reveal);arrow(985,560,1220,560,C.teal,reveal);
  wrap('배경을 넓혀도\n구도 · 사물 비율 유지',1350,330,460,41,C.yellow);wrap('최종 배경은 별도 레이어\n책상과 캐릭터를 독립 배치',1350,570,460,33,C.white);tag('확장 · 분리 원리 도식 / 실제 최종 배경',100,225,C.muted);return true;
 }
 if(id==='16'){
  gameView(80,230,1190,670);wrap('캐릭터 96 × 132\n방 426 × 240',1340,300,480,41,C.yellow);wrap('같은 픽셀 규격\n같은 카메라와 비율',1340,490,480,37,C.teal);image('deskFinal',1360,680,420,167);tag('독립 가구 · 실제 출력',1350,865,C.white);return true;
 }
 if(id==='R21'){
  if(p<.58){image('pixeloecompare',80,240,1760,580);tag('배경 초안 · 실제 PixelOE 처리 비교',100,220,C.teal);code(['target_size: 426 × 240','patch_size: 4 / colors: 64'],110,790,860);}
  else{image('roomFinal',80,245,1160,653);image('deskFinal',1350,420,430,171);wrap('같은 426 × 240 격자\n최종 배경과 가구를 분리',1350,280,470,36,C.yellow);wrap('추가 편집 후\n기존 팔레트로 정리',1350,680,470,34,C.white);tag('초안 후 실제 수정 결과',100,220,C.teal)}return true;
 }
 if(id==='V33'){
  gameView(80,215,1280,721);tag('실제 게임 · 전경 중앙 작업대',100,245,C.teal);
  ['접근 → 몸 낮추기','상판 위 장부 · 손 · 펜','책상 앞부분이 다리를 가림'].forEach((s,i)=>wrap(s,1410,300+i*145,440,35,i===Math.min(2,Math.floor(p*3))?C.yellow:C.white));
  if(p>.62){const x=80+213/426*1280,y=215+181/240*721;line(x-130,y,x+130,y,C.yellow,4);image('ledgerlarge',1410,730,330,118);tag('앞부분 → 다리 앞',1410,875,C.yellow)}return true;
 }
 if(id==='V34'){
  const day=cue(id,'낮에는',d*.3),dark=cue(id,'밤에는',d*.48),night=t<day||t>=dark;runtime.game.weather(night?'night':'sun');gameView(80,215,1280,721);
  txt(night?'밤 · 두 광원을 켬':'낮 · 불을 끔',1420,300,41,C.yellow,true);wrap('불꽃 아래끝 ↔ 심지\n빛의 중심 ↔ 같은 좌표',1420,440,420,36);
  for(const [sx,sy,label]of [[166,43,'랜턴 심지'],[250,162,'촛불 심지']]){const x=80+sx/426*1280,y=215+sy/240*721;line(x-14,y,x+14,y,C.yellow,4);line(x,y-14,x,y+14,C.yellow,4);arrow(x+100,y-60,x+15,y-10,C.yellow);tag(label,x+110,y-65,C.yellow)}wrap('2D 빛 표현\n물리 조도 측정 아님',1410,790,430,28,C.muted);return true;
 }
 if(id==='V35'){
  const music=cue(id,'작업실 라디오',d*.16),controls=cue(id,'다음 곡',d*.54);
  if(t<music){gameView(80,215,1270,715);wrap('다섯 행동 · 네 날씨\n현재 공개 게임에서 실행',1410,390,450,37,C.yellow);return true}
  const next=t>=controls,im=next?images.radioPlaylist:images.radioUI;if(!im)throw Error('Actual browser UI evidence missing');
  c.imageSmoothingEnabled=true;
  if(next){c.drawImage(im,1245,332,370,185,170,290,1110,555);wrap('다음 곡\n순서 섞기\n음량 조절',1400,360,420,42,C.yellow);txt('20곡 → 마지막 곡 뒤 처음으로',960,885,34,C.white,true,'center')}
  else{c.drawImage(im,398,324,1224,690,80,215,1270,715);wrap('화면 안에서 재생\n게임과 함께 듣는 라디오',1410,390,430,38,C.yellow)}
  tag('실제 공개 웹페이지 캡처 · 라디오',100,220,C.teal);
  return true;
 }
 if(id==='W36'){
  if(!images.memoSaved)throw Error('Actual memo evidence missing');c.imageSmoothingEnabled=true;c.drawImage(images.memoSaved,398,44,1224,690,80,265,1020,575);c.drawImage(images.memoSaved,1305,370,305,350,1190,245,550,630);tag('실제 브라우저 캡처 · 저장한 메모',110,220,C.teal);
  const label=p<.33?'최대 500자 입력':p<.66?'저장 → 현재 브라우저에 보관':'기기 간 자동 전송 없음';txt(label,590,880,38,p<.66?C.yellow:C.teal,true,'center');return true;
 }
 return require('../room-v3/render_extra.cjs')(a,row,t,d);
};
