const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base='projects/deconstruct-analyze-rebuild',work=path.join(__dirname,'final-v2');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const subset='https://subsetgames.com/faq.html#youtube', noita='https://www.noitagame.com/press/index.html';
const sources={
 breach:{file:'shared/assets/deconstruct-analyze-rebuild/raw/breach-official-steam.mp4',url:'https://store.steampowered.com/app/590380/Into_the_Breach/',label:'Into the Breach · Subset Games · 공식 게임 장면',labelX:720,labelY:25,rights:subset},
 ftl:{file:'shared/assets/deconstruct-analyze-rebuild/raw/ftl-official-steam.mp4',url:'https://store.steampowered.com/app/212680/FTL_Faster_Than_Light/',label:'FTL: Faster Than Light · Subset Games · 공식 게임 장면',labelX:950,labelY:12,captionCenterX:620,captionCenterY:855,rights:subset},
};
for(let n=1;n<=3;n++)sources['noita'+n]={file:`shared/assets/deconstruct-analyze-rebuild/raw/noita-steam-${n}.mp4`,url:'https://store.steampowered.com/app/881100/Noita/',label:'Noita · Nolla Games · 공식 게임 장면',labelX:550,labelY:25,rights:noita};
for(const r of read(`${base}/sources/breach-advanced-actions.json`).files)sources[r.key]={file:r.file,url:r.sourceArchive,label:'Into the Breach · Subset Games · 공식 프레스킷 게임 장면',labelX:400,labelY:10,rights:subset,nativeTimedSinglePass:true,originalGif:r.originalGif};
const group=(endAtLine,windows,claim,focus,pptConnection)=>({endAtLine,windows,claim,visibleAction:focus,viewerFocus:focus,pptConnection,normalSpeed:true,loop:false});
const chapters=[
 {originalScene:'01',insertion:'after all original scene01 picture and speech',groups:[
  group(3,[['breach',10,17.5],['breach-squad-arachnophile-combo',.05,7.45]],'기능 이름보다 보호할 대상·공격 방향·옮길 위치를 관찰한다.','공격 예고와 목표 셀, 선택한 기체와 전후 위치','원래 기능→판단→결과 도식의 실제 선택 장면'),
  group(6,[['noita2',2,16.7]],'발사 이후의 물질과 이동 경로까지 관찰한다.','발사/파괴와 액체가 흘러 나간 뒤 남는 공간','공격 기능의 목록을 실제 행동 결과로 분해'),
  group(9,[['noita3',34,47.7],['noita3',21.1,24.866666666666667]],'보이는 효과와 플레이어가 결정한 정보·결과를 나눠 적는다.','조준과 발사, 이동, 장면의 결과','같은 버튼도 상황에 따라 다른 판단이라는 원래 설명')
 ]},
 {originalScene:'02',insertion:'after all original scene02 picture and speech',groups:[
  group(3,[['breach-squad-cataclysm-combo',.05,10.25],['breach-squad-arachnophile-combo',7.5,14.95]],'한 번의 이동·공격과 밀려난 적의 새 위치를 따로 본다.','커서와 방향 표식, 공격 전후의 대상 셀','원래 정보→입력→결과의 관찰 기록'),
  group(5,[['noita2',19.9,28.9],['noita3',69.45,73.86666666666667]],'전체 탐험 대신 한 번의 발사체가 바꾼 구간을 본다.','발사 방향, 물질 변화와 다음 이동 공간','큰 기능 이름을 관찰 가능한 단위로 줄인다'),
  group(7,[['ftl',1.5,18.9]],'한 함선의 방·승무원·전력 중 돌볼 상태 하나를 고른다.','선체의 방과 승무원, 하단 전력/시스템 상태','기능 이름 대신 결정 순간을 자른다'),
  group(9,[['breach-squad-bombermechs-combo',.05,10.0]],'게임마다 정해진 길이가 아니라 정보와 결과가 이어진 행동을 고른다.','플레이어의 선택과 이어진 기체/적의 변화','원래 행동 단위 관찰 기록의 마무리')
 ]},
 {originalScene:'03',insertion:'after all original scene03 picture and speech',groups:[
  group(4,[['noita2',29.5,41.5],['noita3',50,56.3]],'지형이 변했다는 관찰과 새 길이 좋아서라는 가설은 다르다.','지형·물질 변화와 이어지는 이동','원래 조건을 적고 한 변수를 검증하는 도식'),
  group(6,[['ftl',19,35]],'상태가 많다는 사실과 동시에 돌볼 일이 몰입을 만든다는 가설을 구분한다.','서로 다른 방/피해/전력 변화','재미의 이유를 관찰 사실로 단정하지 않기'),
  group(9,[['breach-squad-misteaters-combo',.05,11.1],['breach',17.6,26.9]],'소개 컷은 관찰과 질문의 출발점이며 내부 코드·마음의 증거가 아니다.','셀을 선택하고 그 뒤의 상태를 읽는 실제 연속 동작','자체 테스트로 질문을 옮겨 확인하자는 원래 설명')
 ]},
 {originalScene:'04',insertion:'after all original scene04 picture and speech',groups:[
  group(4,[['ftl',52.5,57.8],['ftl',64.6,73],['ftl',1.5,35]],'서로 다른 전투를 연결해도 통제된 비교는 아니다.','함선/적/방 상태가 함께 달라지는 두 전투','원래 발판 폭/재시도 조건 하나만 비교한 실험과 대비'),
  group(6,[['breach-squad-bombermechs-combo',10.1,19.7],['breach-squad-misteaters-combo',11.2,16.2]],'앞의 자체 비교에서는 나머지를 유지해 바꾼 조건을 본다; 현재 상용 컷을 통제 실험이라고 주장하지 않는다.','선택 뒤 연속적으로 바뀌는 실제 셀 상태','원래 점프/재시도 PPT를 보존한 뒤 복수 변수가 있는 상용 사례와 연결'),
  group(9,[['noita2',41.7,54],['noita3',57,63.9]],'주변 물질이 많은 실제 사례에서 작은 실험에 남길 조건을 고른다.','전기/액체/불과 지형의 변화','사례로 질문을 찾고 작은 테스트로 확인한다')
 ]},
 {originalScene:'05',insertion:'after all original scene05 picture and speech',groups:[
  group(2,[['breach-squad-heatsinkers-combo',.05,8.95],['breach',42,50.5]],'겉모양보다 다음에 영향을 받을 위치를 읽는 판단을 고른다.','방향 예고·셀 선택과 그 뒤의 위치','원래 점프/문/신호로 다른 규칙을 묶는 설명'),
  group(6,[['noita3',43.8,47.8],['noita3',26.5,27.9],['noita3',77,85.43333333333334],['noita2',54.1,57.7]],'다른 게임의 규칙을 동일시하지 않고 행동 전 결과를 예상하는 판단을 옮긴다.','발사 뒤 남을 길과 이동 위치','판단을 다른 상황의 문/빛 테스트로 재조립'),
  group(7,[['ftl',58.1,64.5]],'제한된 도움을 어느 상태에 먼저 보낼지의 선택으로 바꿔 볼 수 있다.','방 상태와 사건 선택창, 다음 행동 선택','우선순위라는 판단을 자체 다른 규칙으로 재구성'),
  group(9,[['noita3',95,102.5],['breach-weapon-bounceshot',.05,5.15]],'그림과 이름을 빌리지 않아도 규칙을 실험하고 재미는 사람에게 확인한다.','발사·대상·남은 결과의 서로 다른 상용 행동','원래 재조립 후 사람의 판단을 확인한다는 설명')
 ]},
 {originalScene:'06',insertion:'after all original scene06 picture and speech; fresh recap follows at measured time',groups:[
  group(2,[['breach',50.6,54],['breach-squad-heatsinkers-combo',.05,8.95],['breach-squad-cataclysm-combo',.05,10.25],['breach-enemy-combo',.05,3.7]],'공격 방향을 읽고 고른 위치를 설계 기록에 남긴다.','예상 방향과 실제 공격/결과','원래 플레이 기록의 정보→선택→결과'),
  group(3,[['noita3',12,17.266666666666666]],'행동 뒤 주변 변화와 다음 이동에 남은 것을 기록한다.','설원에서 실제 캐릭터의 이동과 주변 지형/날씨','행동 후 상태를 관찰 기록으로 남긴다'),
  group(4,[['ftl',1.5,38.9],['ftl',52.5,57.8],['ftl',64.6,73]],'여러 상태 중 먼저 돌보고 싶은 것을 적는다.','방·승무원·피해 상태 중 플레이어의 다음 선택','관찰을 검증할 조건으로 바꾸는 순서'),
  group(9,[['breach-squad-misteaters-combo',.05,16.2],['breach-squad-bombermechs-combo',.05,19.7],['breach',10,26.9],['breach',42,54],['breach-enemy-combo',.05,3.7],['breach-combat-volcanofall',0,3.02],['ftl',1.5,35],['ftl',52.5,57.8],['ftl',64.6,73]],'질문과 실제 플레이 답을 다른 기록으로 남기고 놓친 정보를 찾는다.','선택·실행·결과가 이어지는 아직 사용하지 않은 실제 동작','마지막에는 원래 기록 도식의 짧은 추가 2.5D 요약으로 연결')
 ]}
];
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),role:'original explanation preserved; one additional spoken game-observation scene after every chapter',originalUpload:'reng7uTFE7s',sources,chapters,captionPolicy:'FTL uses a smaller lower-left box above weapon/power HUD; other sources use approved bottom boxed captions. Every rendered cue/cut still requires direct review.',sourceConstraints:'No source title/end cards, no reused interval, no artificial slow-down. Press GIF footage plays at native timing once. Chapter claims are observations/questions, not internal-code or controlled-commercial-test claims.'};
fs.writeFileSync(path.join(work,'example-map.json'),JSON.stringify(record,null,2)+'\n');
console.log('New action/claim/PPT mapping saved; exact cuts follow current-hash speech approval.');
