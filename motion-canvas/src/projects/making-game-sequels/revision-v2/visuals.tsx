import {Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

type Timing={duration:number;cues:number[]};
const base='/@fs/D:/Github/VideoEditing/projects/making-game-sequels/production/local/reference-preserving-v2/assets/';
const smooth=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x);};
const txt=(s:string,x:number,y:number,size=46,color:string=D.ink)=><Txt text={s} x={x} y={y} fontSize={size} lineHeight={size*1.35} fontFamily={D.font} fontWeight={600} fill={color}/>;

/** Authored relationship diagrams; screenshots are independent gameplay captures. */
export function* lesson(view:View2D,kind:string,timing:Timing){
 const t=createSignal(0),at=(i:number)=>timing.cues[i]??0;
 const reveal=(i:number)=>()=>smooth((t()-at(i))/.6);
 const add=(children:any,i=0)=>view.add(<Node opacity={reveal(i)}>{children}</Node>);
 const label=(s:string,x:number,y:number,i=0,size=46,color:string=D.ink)=>add(txt(s,x,y,size,color),i);
 const arrow=(points:[number,number][],i=0,color:string=D.teal)=>view.add(<Line points={points} stroke={color} lineWidth={9} endArrow arrowSize={21} end={reveal(i)}/>);
 const shot=(name:string,x:number,y:number,w:number,i=0,h=w*9/16)=>add(<><Img src={base+name+'.png'} x={x} y={y} width={w} height={h}/><Rect x={x} y={y} width={w} height={h} stroke={D.line} lineWidth={2}/></>,i);
 const titles:Record<string,string>={overview:'전편은 재밌었는데, 다음 편은?',foundation:'새 장면보다 먼저 필요한 것',layers:'게임을 움직이는 기반과 그 안의 내용',work:'줄어드는 작업이 어디인지 보기',test:'직접 해 봐야 알 수 있는 재미',teams:'익숙한 플레이 ≠ 같은 제작 출발점',experience:'기대가 경험을 거쳐 돌아옵니다',oatchi:'새 동료가 바꾸는 행동',value:'제작의 이점을 플레이의 가치로',conclusion:'이어 쓸 기반과 다시 할 이유'};
 view.fill(D.background);
 view.add(<>{txt('얌얌코딩  /  속편 만들기',-650,-475,29,D.muted)}{txt(titles[kind],0,-380,57,D.title)}</>);
 const credit=kind==='teams'||kind==='experience'?'기록: LongplayArchive / Spazbo4  ·  Nintendo':['work','layers','foundation'].includes(kind)?'기록: The Geek Joint [Free to Use]  ·  Gran Turismo 7':['overview','value','conclusion'].includes(kind)?'게임: Nintendo · Polyphony Digital / SIE':'게임 화면: Pikmin 4 / Nintendo';
 view.add(txt(credit,480,-475,23,D.muted));
 switch(kind){
 case 'foundation':
  shot('gt-turn',-560,-30,610);
  label('새로 보여 줄 내용',-560,210,0,42,D.green);
  label('영화',-55,-200,0,44,D.title);label('인물 · 설정',340,-200,0,44);label('새 장면',720,-200,1,44,D.green);
  arrow([[490,-200],[600,-200]],1,D.green);
  label('게임',-55,45,2,44,D.title);label('입력에 반응하는 규칙',470,45,2,43,D.teal);
  label('시스템과 제작 도구',470,130,3,39,D.teal);
  arrow([[470,180],[470,225]],3,D.title);
  label('새로운 장소와 도전',470,285,4,44,D.green);break;
 case 'overview':
  shot('pikmin-task',-450,-30,800);shot('gt-turn',450,-30,800,1);
  label('만드는 쪽',-450,-280,0,45,D.teal);label('하는 쪽',450,-280,1,45,D.green);
  label('이어 쓸 기반',-450,245,2,54,D.teal);label('다시 할 이유',450,245,3,54,D.green);
  arrow([[-50,-30],[50,-30]],2,D.title);break;
 case 'layers':
  shot('gt-turn',-470,-25,810);
  label('화면에서 본 자동차와 코스',-470,245,0,37,D.muted);
  [['기반 시스템','조작 · 움직임 · 충돌',D.teal],['제작 도구','코스와 상대를 만들고 수정',D.title],['콘텐츠','구체적인 차 · 코스 · 도전',D.green]].forEach(([a,b,c],i)=>{
   const y=-210+i*200;label(a,460,y,i,49,c);label(b,460,y+65,i,38,D.ink);
   if(i<2)arrow([[460,y+105],[460,y+140]],i+1,c);
  });
  label('개념 구분 · 이 게임의 비공개 내부 구조도가 아닙니다',0,335,0,28,D.muted);break;
 case 'work': {
  shot('gt-turn',595,-170,430);label('가상의 순차 작업 계획',-350,-230,0,43,D.muted);
  const x=-565,unit=106;
  label('새로 마련',-720,-20,0,39);label('기반 개선',-720,170,2,39);
  add(<Rect x={x+6*unit/2} y={-20} width={6*unit} height={78} fill={D.teal}/>,0);
  add(<Rect x={x+6*unit+4*unit/2} y={-20} width={4*unit} height={78} fill={D.green}/>,1);
  label('기반 6개월',x+3*unit,-20,0,41,D.background);label('내용 4개월',x+8*unit,-20,1,41,D.background);label('10개월',720,-20,1,50,D.title);
  add(<Rect x={x+unit} y={170} width={2*unit} height={78} fill={D.teal}/>,2);
  add(<Rect x={x+2*unit+2*unit} y={170} width={4*unit} height={78} fill={D.green}/>,3);
  label('2개월',x+unit,170,2,41,D.background);label('내용 4개월',x+4*unit,170,3,41,D.background);label('6개월',x+7*unit,170,3,50,D.title);
  label('실제 개발 기간이 아닌 설명용 수치 · 변경 범위에 따라 재구축 필요',0,330,4,33,D.muted);break;
 }
 case 'test':
  shot('pikmin-wall',-455,-60,810);shot('pikmin-open',455,-60,810,1);
  label('작업 중: 길을 막은 벽',-455,-310,0,42,D.teal);label('작업 뒤: 열린 길',455,-310,1,42,D.green);
  arrow([[-30,-60],[30,-60]],1,D.title);
  label('작은 실행본',-575,230,2,45);label('직접 조작',0,230,3,45,D.teal);label('느낌과 문제 확인',575,230,4,42,D.green);
  arrow([[-390,230],[-170,230]],3);arrow([[160,230],[350,230]],4,D.green);
  label('프로토타입 (Prototype)',-575,315,2,31,D.muted);label('플레이테스트 (Playtest)',300,315,3,33,D.muted);break;
 case 'teams':
  view.add(<Node opacity={()=>1-reveal(2)()}>{txt('이름은 이어져도',0,-180,54,D.ink)}{txt('개발팀 변경 → 기반 재구축',0,-20,62,D.title)}{txt('플레이의 연속성과 제작 환경의 연속성은 별개',0,165,42,D.muted)}</Node>);
  shot('wiiu-fight',-450,-25,800,2);shot('ultimate-fight',450,-25,800,2);
  label('2014  ·  for Wii U / 3DS',-450,-280,2,42,D.teal);label('2018  ·  Ultimate',450,-280,2,44,D.green);
  arrow([[-35,-25],[35,-25]],2,D.title);
  label('이어지는 개발팀 · 가까운 제작 환경',0,245,2,49,D.title);
  label('두 작품의 개발: 반다이남코 스튜디오 참여',0,325,3,36,D.muted);break;
 case 'experience':
  shot('ultimate-fight',-610,-60,510);
  label('직접 한 경험',-610,130,0,41,D.teal);
  ['기대','플레이','기억','다음 선택'].forEach((s,i)=>{
   const x=-180+i*320;label(s,x,-215,i,46,i===3?D.title:D.ink);
   if(i<3)arrow([[x+82,-215],[x+220,-215]],i+1);
  });
  arrow([[450,-150],[190,35]],2,D.red);arrow([[480,-150],[670,35]],3,D.green);
  label('잘 맞지 않았음',170,100,2,43,D.red);label('더 즐기고 싶음',650,100,3,43,D.green);
  label('완주 여부만으로 만족도를 단정하지 않습니다',160,285,4,36,D.muted);
  label('개념도 · 실제 이용자 조사나 판매 예측이 아닙니다',160,335,4,29,D.muted);break;
 case 'oatchi':
  ['oatchi-before-focus','oatchi-work-focus','oatchi-result-focus'].forEach((s,i)=>{
   const x=(i-1)*580;shot(s,x,-35,545,i,436);label(['항아리 앞의 와치','돌진 (Rush)','파괴 → 물건 등장'][i],x,-290,i,40,[D.teal,D.title,D.green][i]);
   if(i<2)arrow([[x+275,-35],[x+305,-35]],i+1);
  });
  label('추가 기능의 이름보다, 달라진 행동을 보여 주기',0,240,3,47,D.title);
  label('실제 장면에서 확인한 전 상태 → 행동 → 결과',0,315,4,33,D.muted);break;
 case 'value':
  shot('gt-turn',-460,-50,790);shot('oatchi-result',460,-50,790,1);
  label('제작에서 이어 쓸 것',-460,-300,0,46,D.teal);label('플레이에서 달라질 것',460,-300,1,46,D.green);
  arrow([[-35,-50],[35,-50]],2,D.title);
  label('기반 · 도구 · 검증 경험',-460,235,2,41,D.teal);label('조작 · 상황 · 새로운 판단',460,235,3,41,D.green);
  label('작업의 절약이 어떤 플레이 개선으로 이어졌나요?',0,315,4,38,D.title);break;
 default:
  shot('pikmin-task',-600,-75,525);shot('gt-turn',0,-75,525);shot('ultimate-fight',600,-75,525);
  label('무엇을 이어 쓸 수 있나?',-450,195,1,49,D.teal);label('무엇을 다시 해 보고 싶나?',450,195,2,47,D.green);
  arrow([[-50,195],[50,195]],3,D.title);
  label('좋은 출발점 + 충분한 완성도 + 새로 할 이유',0,325,4,43,D.title);
 }
 yield* t(timing.duration,timing.duration,linear);
}
