// Own captured room frames and independently authored explanation diagrams.
// These are film graphics, not imitated service/editor interfaces.
const fs=require('fs'),path=require('path');
const {createCanvas,loadImage,GlobalFonts}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const P=path.resolve(__dirname,'..'),L=path.join(__dirname,'local/full-video-v1'),A=path.join(L,'assets'),O=path.join(L,'boards');fs.mkdirSync(O,{recursive:true});
GlobalFonts.registerFromPath('C:/Windows/Fonts/NotoSansKR-VF.ttf','Noto Sans KR');
const cv=createCanvas(1920,1080),c=cv.getContext('2d'),im={};
const C={bg:'#0b1311',panel:'#14221e',fg:'#edf1e9',muted:'#afbeb3',gold:'#e1c47d',teal:'#77c8b7',red:'#e99280',line:'#3a5147'};
const rows=JSON.parse(fs.readFileSync(path.join(P,'script/narration.ko.json'))).scenes;
function box(x,y,w,h,col=C.panel,stroke=null){c.fillStyle=col;c.fillRect(x,y,w,h);if(stroke){c.strokeStyle=stroke;c.lineWidth=2;c.strokeRect(x,y,w,h);}}
function text(s,x,y,size=36,color=C.fg,weight=500,align='left'){c.font=`${weight} ${size}px "Noto Sans KR"`;c.textAlign=align;c.textBaseline='middle';c.fillStyle=color;c.fillText(s,x,y);}
function wrap(s,x,y,w,size=32,col=C.muted){c.font=`500 ${size}px "Noto Sans KR"`;let out=[],line='';for(const word of s.split(' ')){const n=line?line+' '+word:word;if(c.measureText(n).width>w&&line){out.push(line);line=word;}else line=n;}if(line)out.push(line);out.forEach((v,i)=>text(v,x,y+i*size*1.55,size,col));return out.length*size*1.55;}
function picture(key,x,y,w,h){const a=im[key];if(!a)return;const sc=Math.min(w/a.width,h/a.height),dw=a.width*sc,dh=a.height*sc;c.drawImage(a,x+(w-dw)/2,y+(h-dh)/2,dw,dh);}
function stroke(x,y,xx,yy,col=C.teal,width=4){c.strokeStyle=col;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(xx,yy);c.stroke();}
function arrow(x,y,xx,yy,col=C.teal){stroke(x,y,xx,yy,col);let a=Math.atan2(yy-y,xx-x);stroke(xx,yy,xx-18*Math.cos(a-.5),yy-18*Math.sin(a-.5),col);stroke(xx,yy,xx-18*Math.cos(a+.5),yy-18*Math.sin(a+.5),col);}
function node(x,y,w,title,sub,color=C.teal){box(x,y,w,124,C.panel,C.line);text(title,x+24,y+37,35,color,650);wrap(sub,x+24,y+88,w-45,26);}
function steps(items,x=1290,y=285,w=490){items.forEach((v,i)=>{text(String(i+1).padStart(2,'0'),x,y+i*143,26,C.teal,650);text(v[0],x+60,y+i*143,35,C.gold,650);wrap(v[1],x+60,y+50+i*143,w-60,28);});}
function base(r,kind='실제 제작 화면 + 작업 원리'){box(0,0,1920,1080,C.bg);text('얌얌코딩  /  AI → PLAYABLE ROOM',76,48,25,C.muted);text(r.title,76,119,51,C.gold,650);text(kind,1844,48,25,C.teal,500,'right');stroke(76,175,1844,175,C.line,2);text('AI로 만드는 3D LOFI 게이밍룸',76,868,26,C.muted);}
function videoSlot(){box(76,216,1120,630,'#080d0b',C.line);}
function two(left,right,labels){picture(left,76,260,850,478);picture(right,994,260,850,478);text(labels[0],501,791,35,C.muted,600,'center');text(labels[1],1419,791,35,C.teal,650,'center');}
const notes={
 1:[['걸어서 앉기','이동 → 정렬 → 앉기'],['소리와 기록','레코드 · 장작 · 메모'],['웹에서 플레이','그림을 실행 가능한 방으로']],
 2:[['이어지는 취향','책 · 식물 · 따뜻한 빛'],['추가하는 깊이','크기 · 접촉 · 조명'],['연결하는 기능','행동 · 소리 · 저장']],
 6:[['실제 생성','Tripo Studio / H3.1'],['입력 방식','자체 이미지 · 추가 텍스트 없음'],['검수 방향','정면 + 옆면 + 뒷면']],
 9:[['캐릭터','생성 55 + 정리 40 + 리깅 20'],['헤드폰','생성 55 + 정리 5'],['실제 사용량','총 175 Studio 크레딧']],
 11:[['가구는 편집 가능하게','의자 · 상판 · 모니터 분리'],['몸에 맞춰 확인','엉덩이 높이 · 발 · 무릎'],['모양 수정의 대안','Blockbench / 이번엔 코드 제작']],
 12:[['표면 규칙','나뭇결 · 천 · 돌의 미세 변화'],['실제 구현','Unity 커스텀 셰이더'],['노드 작업 대안','Material Maker · 미실행 후보']],
 13:[['리깅','뼈와 표면의 연결'],['실제 걷기 · 대기','Tripo 내보내기 모션'],['앉기 · 독서','라이선스 확인한 기존 클립']],
 16:[['이동 거리','클립의 보폭과 경로를 맞춤'],['바닥 접촉','발이 지면 아래로 가지 않게'],['전환 확인','걸음 끝 → 의자 정렬']],
 18:[['같은 독서 클립','몸의 흐름을 먼저 유지'],['책과 손의 접촉','IK 가중치를 천천히 연결'],['일어나기','책 정리 → 손 해제 → 기립']],
 19:[['끝부분의 지연','머리는 먼저 · 머리 끝은 나중'],['길이 제한','연결 길이를 유지'],['몸 주변 보호','머리 · 어깨와 충돌 보정']],
 20:[['식물의 기준점','줄기 아래쪽은 고정'],['느린 흔들림','잎마다 위상과 각도 차이'],['창밖 숲 · 달','직접 만든 2.5D 파노라마']],
 21:[['창가 빛','빛기둥 + 표면 조명'],['벽난로 불','불꽃 · 잔불 · 스파크'],['공간과 같은 소리','별도 장작 음량 조절']],
 22:[['레코드','재생 상태에 맞춰 회전'],['음악','Morning Coffee / HoliznaCC0'],['환경음','Fireplace loop / PaGDev']],
 23:[['PC','로컬 UTF-8 JSON 파일'],['브라우저','같은 주소의 localStorage'],['저장 확인','다시 열어 실제 메모 확인']],
 24:[['기준','끝나는 시각을 저장'],['표시','종료 시각 − 현재 시각'],['탭을 바꿔도','누락된 프레임 수에 의존 안 함']],
 25:[['Codex','코드 · 상태 · 저장 연결'],['Unity 공식 CLI / MCP','씬 생성 · 실행 확인 · 빌드'],['완료 판단','실행 기록과 실제 화면 대조']],
 26:[['실제 Unity 웹 빌드','WebGL 2 + WebAssembly'],['시작 버튼','브라우저 소리 재생 연결'],['플레이 검수','앉기 · 독서 · 저장 · 음량']],
 28:[['디자인','같은 색과 실루엣'],['모델과 움직임','크기 · 텍스처 · 접촉'],['플레이와 저장','조작 · 소리 · 메모']]
};
function draw(r){base(r);const id=+r.id;
 if([4,17,27].includes(id)){two(id===4||id===27?'concept':'old',id===17?'sit':'room',id===17?['초기 큰 의자 · 높은 화면','낮은 등받이 · 차분한 앉기']:['초기 방향을 정한 컨셉 이미지','지금 플레이하는 실제 방']);return;}
 if(id===3){const ts=[['imagegen','캐릭터·소품 원화','실제 사용'],['Tripo','이미지 → 모델·리깅','실제 사용'],['Meshy','모델 생성 대안','비교 후보'],['ComfyUI + Hunyuan3D','노드 기반 생성 대안','비교 후보'],['Blockbench','편집 가능한 모델링','비교 후보'],['Material Maker','재질 제작 대안','비교 후보'],['Mixamo','모션 서비스 대안','비교 후보'],['DeepMotion','영상 → 모션 대안','비교 후보'],['Codex','인터랙션·저장 코드','실제 사용'],['Unity','실행·조명·웹 빌드','실제 사용']];ts.forEach((v,i)=>{const x=76+(i%2)*910,y=215+Math.floor(i/2)*124;box(x,y,858,107);text(v[0],x+22,y+29,31,C.fg,650);text(v[1],x+22,y+76,27,C.muted);text(v[2],x+830,y+29,24,v[2]==='실제 사용'?C.teal:C.gold,600,'right');});return;}
 if(id===5){picture('hero',76,205,550,620);picture('headphones',640,245,540,475);steps([['입력 분리','캐릭터와 소품을 각각'],['몸은 전신이 보이게','손 · 발 · 의상 경계'],['소품은 구조가 보이게','이어컵 · 머리띠 · 두께']]);return;}
 if(id===7){picture('hero',76,230,475,590);node(630,265,500,'Meshy','이미지 → 모델 생성 후보');node(1250,265,580,'ComfyUI + Hunyuan3D','노드 환경 + 생성 모델 후보');arrow(1115,540,1225,540);node(630,600,1200,'이번 방의 실제 경로','자체 참고 이미지 → Tripo Studio → Unity',C.gold);text('이미지 기반 생성과 로컬 노드 작업 중 환경에 맞게 선택',630,790,28,C.muted);return;}
 if(id===8){picture('hero',76,225,600,600);node(750,260,1060,'캐릭터','생성 원본 1,941,784 triangles',C.gold);arrow(1280,410,1280,475);node(750,500,1060,'정리한 메시','9,968 quad faces · 9,428 vertices');text('삼각형 수와 사각형 수는 단위가 다릅니다.',780,700,30,C.muted);text('헤드폰: 1,909,880 triangles → 2,000 triangles',780,776,30,C.teal);return;}
 if(id===10){picture('hero',76,236,620,600);const data=[['Base Color','표면의 기본 색','basecolor'],['Normal','작은 요철 방향','normal'],['Roughness','반사의 퍼짐','roughness'],['Metallic','금속인 부분','metallic']];data.forEach((v,i)=>{const x=780+(i%2)*540,y=235+Math.floor(i/2)*280;box(x,y,490,240);text(v[0],x+18,y+32,32,i===0?C.gold:C.teal,650);picture('hero-'+v[2],x+18,y+64,196,155);wrap(v[1],x+237,y+119,235,29);});text('실제 4K 색 원본 + 함께 제공된 데이터 맵을 연결',780,804,30,C.muted);return;}
 if(id===14){picture('walk',76,245,920,518);node(1060,265,755,'Mixamo','캐릭터 리깅·모션 서비스 대안');node(1060,470,755,'DeepMotion','촬영 영상에서 모션을 얻는 대안');wrap('이번 방은 내보낸 Tripo 모션과 기존 라이선스 클립을 연결했습니다.',1085,680,690,34);return;}
 if(id===15){const ns=[['대기','Idle'],['걷기','Walk'],['정렬','Align'],['앉기','Enter'],['생활','Loop'],['일어나기','Exit']];ns.forEach((v,i)=>{const x=76+i*298;node(x,245,268,v[0],v[1],i===3?C.gold:C.teal);if(i<5)arrow(x+270,307,x+293,307);});picture('walk',76,420,550,310);picture('sit',685,420,550,310);picture('read',1294,420,550,310);text('모션 클립의 끝과 다음 행동의 시작을 연결',960,804,38,C.gold,600,'center');return;}
 if(id===2 && im.pixelRoom){picture('pixelRoom',76,216,1120,630);steps(notes[id]);return;}
 if(id===23 && im.webMemo){two('memo','webMemo',['PC · 로컬 JSON 파일','브라우저 · 같은 주소의 저장 공간']);return;}
 if(id===24 && im.webTimer){picture('webTimer',76,216,1120,630);steps(notes[id]);return;}
 if(id===26 && im.webRoom){picture('webRoom',76,216,1120,630);steps(notes[id]);return;}
 if([6,13].includes(id) && im['tripo-'+(id===6?'model':'animation')]){picture('tripo-'+(id===6?'model':'animation'),76,216,1120,630);steps(notes[id]);return;}
 videoSlot();steps(notes[id]||[['입력','실제 사용한 참고 이미지'],['확인','형태와 크기를 검수'],['적용','같은 방에서 결과 확인']]);
}
(async()=>{for(const f of fs.readdirSync(A))if(/\.(png|jpg)$/i.test(f))im[path.parse(f).name]=await loadImage(path.join(A,f));for(const r of rows){draw(r);fs.writeFileSync(path.join(O,r.id+'.png'),await cv.encode('png'));}console.log('Rendered',rows.length,'full-resolution film graphics');})();
