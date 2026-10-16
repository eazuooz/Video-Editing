import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, usePlayback} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';
import trophy from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/trophies-01.jpg';
import trophyModel from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/trophies-02.jpg';
import stickerEmpty from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/stickers-03.jpg';
import stickerFull from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/stickers-05.jpg';
import stickerEffects from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/stickers-07.jpg';
import coinStart from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/coin-launcher-03.jpg';
import coinHit from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/coin-launcher-05.jpg';
import coinResult from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/coin-launcher-09.jpg';
import myMusic from '../../../../../projects/game-reward-planning/production/local/reference-preserving-v2/official/music-01.jpg';

export type LessonKind='overview'|'growth'|'powerLoss'|'training'|'unlock'|'trophyCost'|'stickers'|'costMath'|'spiritRules'|'coins'|'music'|'checklist'|'progress'|'worksheet';
export interface LessonTiming {duration:number; cues?:number[];}
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>{const a=clamp(x);return a*a*(3-2*a);};
const txt=(text:string,x:number,y:number,size=44,color:string=D.ink)=> <Txt text={text} x={x} y={y} fontFamily={D.font} fontSize={size} lineHeight={size*1.3} fill={color} fontWeight={600}/>;

/** Independent editorial diagrams. No detector output or measured game stats. */
export function* lesson(view:View2D,kind:LessonKind,timing:LessonTiming){
  const clock=createSignal(0),duration=timing.duration;
  if(!(duration>0))throw new Error(`Missing measured duration for ${kind}`);
  const cue=(n:number)=>timing.cues?.[n]??duration*[0,.2,.4,.6,.8][n];
  const reveal=(n:number)=>()=>ease((clock()-cue(n))/.55);
  const stage=(n:number)=>()=>clock()>=cue(n)?1:0;
  const headers:Record<LessonKind,string>={overview:'보상을 받으면, 무엇이 달라질까?',growth:'공격력 증가와 피해량 증가는 다릅니다',powerLoss:'얻은 힘을 잃을 수 있다는 긴장감',training:'바로 대결하려는데, 육성부터 필요하다면?',unlock:'새로운 선택지를 여는 보상',trophyCost:'작은 수집품 하나에도, 여러 작업이 필요합니다',stickers:'수집의 즐거움을 다른 형식으로',costMath:'만들 수 있는 양부터 계산하기',spiritRules:'스피릿: 능력치의 바탕 + 추가 효과',coins:'코인은 사용 행동과 결과로 이어져야 합니다',music:'얻는 즐거움과, 기다리는 불편',checklist:'완료한 일이 다음 목표를 열어 줍니다',progress:'진행도·완료·지급을 구분하기',worksheet:'보상 한 줄을 먼저 완성하기'};
  view.fill(D.background);
  view.add(<>
    <Txt text={'얌얌코딩  /  게임 보상 기획'} x={-850} y={-478} offset={[-1,0]} fontFamily={D.font} fontSize={28} fill={D.muted}/>
    <Txt text={headers[kind]} x={-850} y={-386} offset={[-1,0]} fontFamily={D.font} fontSize={58} fontWeight={700} fill={D.title}/>
  </>);
  function captionNote(s:string){view.add(txt(s,0,318,30,D.muted));}
  function official(){captionNote('Nintendo · Smash Bros. DOJO!!  |  공식 공개 정지 자료를 설명에 사용');}
  function block(label:string,x:number,y:number,index:number,color:string=D.title,width=400){
    view.add(<Node opacity={reveal(index)}><Rect x={x} y={y} width={width} height={150} stroke={color} lineWidth={5}/>{txt(label,x,y,43,color)}</Node>);
  }
  function arrow(points:[number,number][],index:number,color:string=D.teal){view.add(<Line points={points} stroke={color} lineWidth={8} endArrow arrowSize={19} end={reveal(index)}/>);}
  switch(kind){
    case 'overview':
      block('무엇을 했나',-590,-40,0);block('무엇을 얻나',0,-40,1);block('무엇이 달라지나',590,-40,2);
      arrow([[-370,-40],[-225,-40]],1);arrow([[225,-40],[370,-40]],2);
      view.add(<Node opacity={reveal(3)}>{txt('새로운 선택   ·   수집   ·   감상   ·   다음 목표',0,190,46)}</Node>);
      break;
    case 'growth':
      captionNote('설명용 수치 · 실제 게임의 공격력·피해량을 측정한 결과가 아닙니다');
      view.add(<>{txt('공격력',0,-240,40,D.muted)}{txt('10',-440,-60,140)}<Node opacity={reveal(1)}>{txt('12',440,-60,140,D.title)}</Node></>);
      arrow([[-250,-60],[240,-60]],1);
      view.add(<Node opacity={reveal(2)}>{txt('(12 − 10) ÷ 10 × 100 = 20%',0,130,62,D.title)}</Node>);
      view.add(<Node opacity={reveal(3)}>{txt('피해량에는 방어력·별도 계산식도 영향을 줍니다',0,238,40,D.ink)}</Node>);
      break;
    case 'powerLoss':
      captionNote('봄버맨의 보상·손실 관계 설명 · 특정 버전의 정확한 상태·수치가 아닙니다');
      block('얻기 전',-590,-40,0,D.muted);block('강화된 상태',0,-40,1,D.green);block('실패 뒤의 상태',590,-40,3,D.red);
      arrow([[-370,-40],[-225,-40]],1);arrow([[225,-40],[370,-40]],3,D.red);
      view.add(<Node opacity={reveal(2)}>{txt('지금 가진 힘을 유지하고 싶다',0,180,52,D.title)}</Node>);
      break;
    case 'training':
      captionNote('필수 육성은 비교를 위한 가정 · 실제 기본 대전의 규칙이 아닙니다');
      block('파이터 선택',-560,-140,0);block('대결 시작',560,-140,1,D.green);arrow([[-330,-140],[330,-140]],1);
      view.add(<Node opacity={reveal(2)}>{txt('필수 육성 조건을 넣는다면',0,60,42,D.red)}</Node>);
      block('오래 육성하기',0,195,2,D.red,480);arrow([[-560,-50],[-560,195],[-265,195]],2,D.red);arrow([[265,195],[560,195],[560,-50]],3,D.red);
      break;
    case 'unlock':
      block('사용할 수 없음',-590,-40,0,D.muted);block('조건 달성',0,-40,1,D.green);block('새 파이터 선택',590,-40,2,D.title);
      arrow([[-370,-40],[-225,-40]],1);arrow([[225,-40],[370,-40]],2);
      view.add(<Node opacity={reveal(3)}>{txt('해금 (Unlock): 잠긴 항목을 사용할 수 있게 열기',0,190,44)}</Node>);
      break;
    case 'trophyCost':
      view.add(<><Img src={trophyModel} x={-450} y={-70} height={460} opacity={()=>1-stage(1)()}/><Img src={trophy} x={-450} y={-70} height={460} opacity={stage(1)}/></>);
      ['모델 제작·정리','감상 화면','설명문 준비','검수'].forEach((v,i)=>view.add(<Node opacity={reveal(i)}>{txt(v,460,-200+i*125,48,i===3?D.green:D.ink)}<Line points={[[210,-150+i*125],[720,-150+i*125]]} stroke={D.line} lineWidth={2}/></Node>));
      official();break;
    case 'stickers':
      view.add(<>
        <Img src={stickerEmpty} height={460} x={-470} y={-55}/>
        <Img src={stickerFull} height={460} x={470} y={-55} opacity={()=>1-stage(3)()}/>
        <Img src={stickerEffects} height={460} x={470} y={-55} opacity={stage(3)}/>
        {txt('붙이기 전',-470,230,44,D.muted)}<Node opacity={reveal(1)}>{txt('그림 수집 + 모드 안의 강화',470,230,42,D.green)}</Node>
      </>);arrow([[-110,-55],[100,-55]],1);official();break;
    case 'costMath':
      captionNote('독립적인 제작 계획 예시 · Nintendo의 실제 제작 시간·예산이 아닙니다');
      view.add(<>{txt('개별 제작',-620,-240,38,D.muted)}{txt('10개 × 2시간',-620,-100,57)}{txt('공통 화면',0,-240,38,D.muted)}{txt('6시간',0,-100,62)}{txt('별도 검수',620,-240,38,D.muted)}{txt('3시간',620,-100,62)}</>);
      view.add(<Node opacity={reveal(1)}>{txt('20 + 6 + 3 = 29시간',0,80,76,D.title)}</Node>);
      view.add(<Node opacity={reveal(2)}>{txt('총 시간 = 개수 × 개별 시간 + 공통 작업 + 검수',0,202,42)}</Node>);
      view.add(<Node opacity={reveal(3)}>{txt('항목별 시간이 다르면: 개별 시간을 각각 계산해 합산',0,270,34,D.muted)}</Node>);
      break;
    case 'spiritRules':
      captionNote('스피릿 규칙을 사용하는 모드의 설명 · 기본 대전 전체의 필수 육성이 아닙니다');
      block('어택커 스피릿\nPrimary Spirit',-470,-80,0,D.title,650);
      block('서포터 스피릿\nSupport Spirit',470,-80,1,D.teal,650);
      view.add(<><Node opacity={reveal(0)}>{txt('공격력·방어력의 바탕',-470,130,42)}</Node><Node opacity={reveal(1)}>{txt('슬롯에 넣어 추가 효과',470,130,42)}</Node></>);
      arrow([[125,-80],[-125,-80]],2);
      break;
    case 'coins':
      view.add(<>
        <Img src={coinStart} height={460} x={-450} y={-40} opacity={()=>1-stage(1)()}/>
        <Img src={coinHit} height={460} x={-450} y={-40} opacity={()=>stage(1)()*(1-stage(3)())}/>
        <Img src={coinResult} height={460} x={-450} y={-40} opacity={stage(3)}/>
      </>);
      ['보유한 코인','탄환으로 사용','피규어·스티커 획득'].forEach((v,i)=>{block(v,460,-210+i*185,i,D.title,650);if(i<2)arrow([[460,-130+i*185],[460,-105+i*185]],i+1);});
      // Different official stills are not a continuous balance measurement.
      view.add(txt('각 화면은 별도 상태 · 숫자 변화량을 비교하지 않습니다',-400,240,28,D.muted));official();break;
    case 'music':
      view.add(<><Img src={myMusic} height={460} x={-440} y={-90}/>{txt('곡별 재생 비중을 고르는 화면',-440,230,38,D.muted)}</>);
      block('해금 전\n바로 들을 수 없음',460,-190,0,D.red,650);block('해금 후\n감상·선택의 폭이 늘어남',460,110,2,D.green,650);
      arrow([[460,-100],[460,20]],2);official();break;
    case 'checklist':
    case 'progress': {
      const isProgress=kind==='progress';
      captionNote('독립적인 설명용 과제판 · 실제 커비의 조건·수치·보상과 다릅니다');
      [0,1,2].forEach(r=>[0,1,2].forEach(c=>{
        const center=r===1&&c===1,next=r===1&&c===2,x=-470+(c-1)*250,y=-35+(r-1)*155;
        view.add(<Node><Rect x={x} y={y} width={202} height={132} lineWidth={center||next?6:2} stroke={()=>center?(isProgress||stage(1)()?D.green:D.title):next&&(isProgress||stage(2)())?D.teal:D.line}/>
        <Txt x={x} y={y} text={()=>center?(isProgress||stage(1)()?'완료':'첫 완주'):next&&(isProgress||stage(2)())?'코인 3개':'?'} fontFamily={D.font} fontSize={center||next?37:44} fill={()=>center?(isProgress||stage(1)()?D.green:D.title):next?D.teal:D.muted}/></Node>);
      }));
      if(!isProgress)arrow([[-360,-35],[-330,-35]],2);
      view.add(<>
        <Txt x={475} y={-210} text={()=>isProgress?'현재 진행도':stage(2)()?'새로 보이는 목표':'현재 목표'} fontFamily={D.font} fontSize={40} fill={D.title}/>
        <Txt x={475} y={-110} text={()=>isProgress||stage(2)()?'코인 세 개 모으기':'첫 코스를 완주하기'} fontFamily={D.font} fontSize={48} fill={D.ink}/>
        <Txt x={475} y={0} text={()=>isProgress?(stage(1)()?'1 / 3개':'0 / 3개'):stage(2)()?'힌트 공개 ≠ 조건 완료':stage(1)()?'조건 달성 → 새 음악':'조건을 아직 달성하지 않음'} fontFamily={D.font} fontSize={40} fill={D.green}/>
      </>);
      if(isProgress){
        view.add(<Node opacity={reveal(2)}>{txt('보상 지급 조건',475,120,38,D.title)}{txt('조건 완료 + 아직 지급하지 않음',475,190,34)}{txt('완료 화면을 다시 열어도 추가 지급 없음',475,257,31,D.muted)}</Node>);
      }else view.add(<Node opacity={reveal(3)}>{txt('해낸 일 → 다음에 해 볼 일',475,170,42,D.teal)}</Node>);
      break;
    }
    case 'worksheet': {
      const rows=[['달라지는 것','새 음악을 다시 감상할 수 있다'],['획득 조건','설명용: 첫 코스 완주'],['필요한 작업','음원·권리 확인·감상 화면·저장'],['잠금의 불편','얻기 전에는 바로 듣지 못한다'],['검증할 결과','완료 → 한 번 지급 → 감상 가능']];
      rows.forEach(([a,b],i)=>view.add(<Node opacity={reveal(Math.min(i,4))}>
        <Txt text={a} x={-790} y={-230+i*111} offset={[-1,0]} fontFamily={D.font} fontSize={42} fill={D.title}/>
        <Txt text={b} x={-320} y={-230+i*111} offset={[-1,0]} fontFamily={D.font} fontSize={42} fill={D.ink}/>
        <Line points={[[-800,-178+i*111],[800,-178+i*111]]} stroke={D.line} lineWidth={2}/>
      </Node>));break;
    }
  }
  const playback=usePlayback(),start=playback.frame,frames=Math.round(duration*60);
  while(playback.frame-start<frames){clock((playback.frame-start)/60);yield;}
}
