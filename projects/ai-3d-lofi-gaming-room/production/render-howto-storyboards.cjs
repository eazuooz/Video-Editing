// Authored instructional cards beside actual input images and game captures.
// These cards never imitate a service UI or claim unrun alternatives were used.
const fs=require('fs'),path=require('path');
const {createCanvas,loadImage,GlobalFonts}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const P=path.resolve(__dirname,'..'),L=path.join(__dirname,'local/full-video-v5'),A=path.join(L,'assets'),O=path.join(L,'boards');fs.mkdirSync(O,{recursive:true});
GlobalFonts.registerFromPath('C:/Windows/Fonts/NotoSansKR-VF.ttf','Noto Sans KR');
const rows=JSON.parse(fs.readFileSync(path.join(P,'script/narration.ko.json'))).scenes;
const recipes=JSON.parse(fs.readFileSync(path.join(P,'script/tutorial-v5.json'))).scenes;
const cv=createCanvas(1920,1080),c=cv.getContext('2d'),im={};
const C={bg:'#0b1311',panel:'#14221e',fg:'#edf1e9',muted:'#afbeb3',gold:'#e1c47d',teal:'#77c8b7',red:'#e99280',line:'#3a5147'};
function box(x,y,w,h,col=C.panel){c.fillStyle=col;c.fillRect(x,y,w,h);}
function text(s,x,y,size=32,color=C.fg,weight=500,align='left'){c.font=`${weight} ${size}px "Noto Sans KR"`;c.textAlign=align;c.textBaseline='middle';c.fillStyle=color;c.fillText(s,x,y);}
function wrap(s,x,y,w,size=30,col=C.fg){c.font=`500 ${size}px "Noto Sans KR"`;let out=[],line='';for(const word of s.split(' ')){const n=line?line+' '+word:word;if(c.measureText(n).width>w&&line){out.push(line);line=word;}else line=n;}if(line)out.push(line);out.forEach((v,i)=>text(v,x,y+i*size*1.5,size,col));return out.length*size*1.5;}
function pic(key,x,y,w,h){const a=im[key];if(!a)return;let s=Math.min(w/a.width,h/a.height);c.drawImage(a,x+(w-a.width*s)/2,y+(h-a.height*s)/2,a.width*s,a.height*s);}
function stroke(x,y,xx,yy,col=C.line){c.strokeStyle=col;c.lineWidth=3;c.beginPath();c.moveTo(x,y);c.lineTo(xx,yy);c.stroke();}
function arrow(x,y,xx,yy){stroke(x,y,xx,yy,C.teal);stroke(xx,yy,xx-14,yy-8,C.teal);stroke(xx,yy,xx-14,yy+8,C.teal);}
const settings={
 1:['이미지: 기준 디자인','모델: Tripo 생성·정리','게임: Codex + Unity'],
 6:['이미지 업로드 · Image to 3D','H3.1 · 캐릭터·소품 분리','앞 · 옆 · 뒤를 돌려 확인'],
 8:['Retopo · Quad / 목표 10K','관찰 결과 · 9,968 quad faces','실루엣 · 손가락 · 관절 확인'],
 9:['FBX · PBR 텍스처 · 동작','원본 / 게임용 결과 폴더 분리','계정의 실행 전 차감량 확인'],
 11:['소파·테이블 입력을 분리','Tripo 생성 → 게임용 메시','미터 단위 · 몸과 가구 접촉'],
 12:['나뭇결은 길이 방향으로','천은 무광 · 요철은 약하게','재질 결과를 같은 조명에서 확인'],
 13:['Tripo · Walk / Idle','Unity Rig · Humanoid','KayKit Sit + EmacEArt 휴식'],
 16:['기존 걷기 클립 사용','Root Motion → 경로 이동','발 접촉 · 회전 속도 확인'],
 17:['접근 → 정렬 → 앉기','클립 속도 0.36 · 점진 보정','골반 · 발 · 키보드 손 확인'],
 18:['휴식 몸 + 독서 팔 Avatar Mask','등은 소파 · 발은 테이블','책·손목·팔꿈치 간격 확인'],
 19:['머리 뿌리 고정 · 영역 마스크','끝부분의 지연 · 길이 제한','머리 · 어깨와 충돌 보정'],
 20:['줄기 아래 고정 · 잎별 위상','숲 · 달 · 별을 레이어로','낮·밤과 실내 조명 연동'],
 29:['창문 영역에만 비·물방울','배경 → 비 → 창틀','날씨 상태를 UI·효과가 공유'],
 21:['불꽃 · 잔불 · 불티','주변의 따뜻한 빛과 연동','별도 장작 음량 · 같은 위치'],
 22:['CC0 완전한 음원 열 곡','선택 / 이전 / 다음 / 순환','재생 상태 → 레코드 회전'],
 30:['CC0 사진 → 배경 정리 이미지','Tripo H3.1 → Triangle 20K','4K 텍스처 · 몸통 호흡 · 작은 꼬리'],
 23:['한글 · 줄바꿈 · 자동 저장','입력 중 게임 단축키 분리','같은 주소에서 새로고침 확인'],
 24:['종료 시각 − 현재 시각','일시정지 / 재개 / 시간 선택','탭 전환 후 실제 시간 확인'],
 26:['같은 Unity 버전 · Web 모듈','빌드 씬 지정 · 시작 후 오디오','HTTP 실행 · 독서·저장 확인'],
 28:['1  기준 그림 만들기','2  모델과 동작 준비하기','3  AI 코드 + 엔진으로 연결']
};
function base(r){box(0,0,1920,1080,C.bg);text('얌얌코딩  /  AI 도구로 같은 게임 만들기',76,48,25,C.muted);text(r.title,76,119,49,C.gold,650);stroke(76,175,1844,175);text('입력 · 요청문 · 설정 · 결과를 연결하기',76,868,26,C.muted);}
function steps(id){const a=settings[id]||[];a.forEach((s,i)=>{text(String(i+1).padStart(2,'0'),1245,278+i*183,25,C.teal,650);wrap(s,1301,278+i*183,518,32,i===0?C.gold:C.fg);});}
function node(x,y,w,title,sub){box(x,y,w,146);text(title,x+22,y+40,34,C.gold,650);wrap(sub,x+22,y+94,w-44,27,C.muted);}
function request(title,lines){box(1005,239,839,557);text('따라 만들기 요청문',1030,271,27,C.teal,650);text(title,1030,326,33,C.gold,650);let y=387;for(const line of lines){y+=wrap(line,1030,y,777,31,C.fg)+25;}}
function draw(r){base(r);const id=+r.id,recipe=recipes.find(s=>s.id===r.id);
 if(id===2){const a=[['ChatGPT 이미지 생성','캐릭터·소품 입력 그림','기본 경로'],['Tripo Studio / H3.1','3D 모델 · 정리 · 리깅','기본 경로'],['Codex','기능별 요청 → 구현 코드','기본 경로'],['Unity 6 URP','조명 · 동작 · 웹 실행','기본 경로'],['Meshy','이미지 → 3D 생성','모델 대안'],['ComfyUI + Hunyuan3D','노드 환경 + 생성 모델','모델 대안'],['Blockbench','분리된 가구 형상 편집','편집 대안'],['Material Maker','노드 기반 표면 제작','재질 대안'],['Mixamo','기존 리깅·모션 서비스','동작 대안'],['DeepMotion','전신 영상 → 동작','동작 대안']];a.forEach((v,i)=>{let x=76+i%2*910,y=215+Math.floor(i/2)*124;box(x,y,858,107);text(v[0],x+22,y+29,31,C.fg,650);text(v[1],x+22,y+76,27,C.muted);text(v[2],x+830,y+29,23,i<4?C.teal:C.gold,600,'right');});return;}
 if(id===3){pic('concept',76,235,860,540);request('방의 용도와 배치',[ '따뜻한 목재 · 청록색 캐릭터','아이맥 한 대 · 편안한 독서 자리','창밖 숲과 달 · 걸어갈 통로','고정된 대각선 카메라 · 방 전체']);return;}
 if(id===11){pic('sofa-input',76,240,1120,335);pic('table-input',76,585,1120,245);steps(id);return;}
 if(id===4){pic('hero',76,205,850,620);request('같은 캐릭터의 기준 그림',['갈색 머리 · 청록색 재킷','전신 중립 A-pose','팔은 몸통에서 분리 · 손발 노출','단순 배경 · 균일한 조명']);return;}
 if(id===5){pic('headphones',76,220,850,590);request('헤드폰 한 개만 만들기',['무광 어두운 이어컵 · 청록색 장식','연결된 패딩 머리띠 · 실제 두께','전체 윤곽이 보이는 3/4 시점','로고 · 받침대 · 다른 물건 제외']);return;}
 if(id===7){pic('hero',76,235,560,560);node(715,244,1129,'Meshy · Image to 3D','이미지 업로드 → 모델 생성 → 내보내기');node(715,448,1129,'ComfyUI + Hunyuan3D','Image → Shape model → Texture model → Export');node(715,652,1129,'선택 기준','같은 입력과 목표 엔진 · 뼈대 · 재질 형식');return;}
 if(id===8){pic('hero',76,235,1120,600);steps(id);text('게임용 메시 설정과 실제 관찰값',76,224,27,C.teal);return;}
 if(id===9){node(76,245,530,'FBX','캐릭터 · 뼈대 · 게임용 메시');node(695,245,530,'PBR maps','색 · 노멀 · 거칠기 · 금속성');node(1314,245,530,'Animation','기존 동작 클립과 Avatar');arrow(607,318,675,318);arrow(1226,318,1294,318);pic('hero',90,445,500,350);pic('headphones',660,445,500,350);node(1230,460,614,'이번 실행 기록','캐릭터 115 + 헤드폰 60\n합계 175 Studio 크레딧');text('출력 묶음 · 파일 탐색기를 흉내 낸 UI가 아닙니다.',76,817,26,C.muted);return;}
 if(id===10){pic('hero',76,236,620,600);const d=[['Base Color','표면의 기본 색','basecolor'],['Normal','작은 요철 방향','normal'],['Roughness','반사의 퍼짐','roughness'],['Metallic','금속인 영역','metallic']];d.forEach((v,i)=>{let x=780+i%2*540,y=235+Math.floor(i/2)*280;box(x,y,490,240);text(v[0],x+18,y+32,32,C.gold,650);pic('hero-'+v[2],x+18,y+64,196,155);wrap(v[1],x+235,y+119,240,29);});text('URP Smoothness는 Roughness와 반대 방향의 값',780,805,29,C.teal);return;}
 if(id===14){pic('walk',76,245,920,518);node(1060,265,755,'Mixamo','기존 동작을 찾아 리깅·재생');node(1060,470,755,'DeepMotion','가려지지 않은 전신 영상에서 모션 추출');wrap('클립 확보 → 정상 속도 관찰 → 같은 Avatar에 연결',1085,680,700,32);return;}
 if(id===15){['Walk','Align','Enter','Loop','Exit'].forEach((s,i)=>{let x=76+i*356;node(x,235,310,s,['이동','방향 맞춤','앉기 · 눕기','생활 동작','정리 · 기립'][i]);if(i<4)arrow(x+315,308,x+348,308);});pic('walk',76,420,550,310);pic('sit',685,420,550,310);pic('read',1294,420,550,310);text('새 입력은 안전한 전환을 마친 뒤 이어서 실행',960,802,37,C.gold,650,'center');return;}
 if(id===25){node(76,245,470,'Codex','무엇을 만들지 요청');node(650,245,530,'Unity CLI / MCP','프로젝트의 도구 호출');node(1284,245,560,'Unity Editor','씬 · 재생 · 상태 · 빌드');arrow(550,317,620,317);arrow(1186,317,1255,317);box(1005,465,839,292);text('요청 전에 범위 지정',1030,505,30,C.teal,650);wrap('프로젝트 경로와 작업할 새 씬',1030,574,777,31);wrap('기존 씬·에셋 보존',1030,639,777,31);wrap('구현 → 실행 → 상태 확인',1030,704,777,31,C.gold);box(76,465,820,292);text('명령 예시 · 설치된 Unity CLI 기준',102,506,29,C.teal);wrap('unity mcp --project-path <UnityProject>',102,572,740,29);wrap('AI의 도구 연결 → Unity에서 결과 확인',102,665,740,30,C.gold);return;}
 if(id===31){pic('concept',76,242,520,400);pic('hero',650,238,520,410);pic('webRoom',1224,242,620,400);text('입력 그림 + 디자인 요청',76,708,31,C.gold,650);text('모델 + 재질 + 기존 동작',650,708,31,C.gold,650);text('기능별 Codex 요청문',1224,708,31,C.gold,650);text('위키에서 요청문 · 설정 · 확인할 결과를 함께 보기',960,809,33,C.teal,650,'center');return;}
 if(id===27){pic('concept',76,260,850,478);pic('room',994,260,850,478);text('입력 · 디자인 기준 그림',501,791,33,C.muted,600,'center');text('결과 · 조작과 저장이 연결된 방',1419,791,33,C.teal,650,'center');return;}
 if(id===23||id===24||id===26){pic(id===23?'webMemo':id===24?'webTimer':'webRoom',76,216,1120,630);steps(id);return;}
 if(id===30){pic('cat-photo',76,258,520,490);pic('cat-input',646,258,550,490);text('CC0 실제 수면 사진',76,793,29,C.gold);text('이미지 AI로 배경 정리',646,793,29,C.teal);steps(id);return;}
 if(id===6||id===13){pic(id===6?'tripo-model':'tripo-animation',76,216,1120,630);steps(id);return;}
 box(76,216,1120,630,'#080d0b');steps(id);text(recipe.tool,1245,814,25,C.teal,650);
}
(async()=>{for(const f of fs.readdirSync(A))if(/\.(png|jpg)$/i.test(f))im[path.parse(f).name]=await loadImage(path.join(A,f));for(const r of rows){draw(r);fs.writeFileSync(path.join(O,r.id+'.png'),await cv.encode('png'));}console.log('Rendered',rows.length,'AI-tool tutorial boards');})();
