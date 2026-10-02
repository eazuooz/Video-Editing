// Original narrative sandbox. Facts, ownership and consequences are executable.
(function(factory) {
  const api=factory();
  if(typeof module!=='undefined') module.exports=api;
  else globalThis.HarborStory=api;
})(function(){
  const create=()=>({started:false,introRead:false,noteKnown:false,sharedRule:false,
    sealOwner:null,companionPresent:true,route:null,rations:1,minutes:0,
    gateOpen:false,arrived:false,dialogue:null,events:[],lastLineId:null});
  const line=(s,id,text,choices=[])=>{s.lastLineId=id;s.dialogue={id,text,choices};return s;};
  function guard(s){
    const route=s.route==='feed'?'길의 동물에게 먹이를 주었군요.':s.route==='detour'?'우회로로 오셨군요.':s.route==='drive'?'길을 막던 동물을 물러나게 했군요.':'항구에 오신 것을 환영합니다.';
    const access=s.sealOwner==='player'||(s.sealOwner==='companion'&&s.companionPresent);
    const choices=[];
    if(!s.sharedRule) choices.push(s.noteKnown?['share-rule','게시판의 통행 규칙을 읽었어요.']:s.introRead?['confirm-known-rule','관리인의 증표를 구하러 갈게요.']:['ask-rule','무엇이 필요한가요?']);
    if(access)choices.push(['present-seal',s.sealOwner==='player'?'내 증표를 보여 준다.':'동료가 증표를 보여 준다.']);
    else choices.push(['ask-seal','증표를 어디서 가져오나요?']);
    choices.push(['close','대화를 마친다.']);
    if(s.gateOpen)return line(s,'guard.already-open','증표를 받았습니다. 항구 안으로 들어가세요.',[['enter-harbor','항구에 들어간다.'],['close','대화를 마친다.']]);
    // A shorter greeting does not assert that the guard knows what the player read.
    const greeting=s.sharedRule?'통행 규칙은 이미 이야기했지요.':(s.noteKnown||s.introRead)?'무슨 일로 오셨나요?':'항구에는 관리인의 증표가 필요합니다.';
    return line(s,s.sharedRule?'guard.rule-shared':'guard.first',`${route} ${greeting}`,choices);
  }
  function act(input,action){
    const s=JSON.parse(JSON.stringify(input)),before=JSON.parse(JSON.stringify(input));
    let accepted=true;
    switch(action){
      case 'start-read':s.started=true;s.introRead=true;line(s,'intro.read','폭풍 뒤 항구가 닫혔습니다. 관리인의 증표가 있으면 문지기가 통행을 허락합니다.',[['close','출발한다.']]);break;
      case 'start-skip':s.started=true;line(s,'intro.skipped','항구 마을에 도착했습니다.',[['close','둘러본다.']]);break;
      case 'read-note':s.noteKnown=true;line(s,'note.rule','항구 통행 안내: 관리인의 증표를 문지기에게 보여 주세요. 증표는 등대 보관함에 있습니다.',[['close','안내를 닫는다.']]);break;
      case 'talk-guard':guard(s);break;
      case 'ask-rule':s.sharedRule=true;line(s,'guard.explains','관리인의 증표를 보여 주면 통과할 수 있습니다. 등대 보관함에서 찾아 주세요.',[['close','알겠습니다.']]);break;
      case 'share-rule':if(!s.noteKnown){accepted=false;break;}s.sharedRule=true;line(s,'guard.acknowledges','규칙을 읽었군요. 증표를 가져오면 확인하겠습니다.',[['close','알겠습니다.']]);break;
      case 'confirm-known-rule':if(!s.introRead){accepted=false;break;}s.sharedRule=true;line(s,'guard.known-confirmed','좋습니다. 증표를 찾으면 다시 들러 주세요.',[['close','증표를 찾으러 간다.']]);break;
      case 'ask-seal':line(s,'guard.seal-source',s.sealOwner==='companion'?'증표를 가진 동료와 함께 오거나, 동료에게서 다시 받아 주세요.':'등대 보관함을 확인해 주세요.',[['close','확인하러 간다.']]);break;
      case 'take-seal':if(s.sealOwner!==null){accepted=false;break;}s.sealOwner='player';line(s,'seal.acquired','등대 보관함에서 관리인의 증표를 받았습니다.',[['close','가져간다.']]);break;
      case 'give-companion':if(s.sealOwner!=='player'||!s.companionPresent){accepted=false;break;}s.sealOwner='companion';line(s,'companion.holds','동료: 내가 증표를 맡아 둘게. 함께 가서 보여 주자.',[['close','부탁한다.']]);break;
      case 'rest-companion':s.companionPresent=false;line(s,'companion.rests','동료: 잠시 등대에서 쉬고 있을게.',[['close','혼자 출발한다.']]);break;
      case 'call-companion':s.companionPresent=true;line(s,'companion.returns','동료가 다시 합류했습니다.',[['close','함께 간다.']]);break;
      case 'recover-seal':if(s.sealOwner!=='companion'){accepted=false;break;}s.sealOwner='player';line(s,'seal.recovered','등대에 돌아가 동료에게서 증표를 다시 받았습니다.',[['close','증표를 챙긴다.']]);break;
      case 'road':if(s.route){line(s,'road.resolved','이미 길을 통과했습니다.',[['close','계속 간다.']]);break;}line(s,'road.choice','작은 동물이 항구 길을 막고 있습니다. 어떻게 지나갈까요?',[['feed','먹이를 준다.'],['detour','우회로로 간다.'],['drive','침착하게 물러나게 한다.']]);break;
      case 'feed':if(s.route||s.rations<1){accepted=false;break;}s.route='feed';s.rations-=1;s.minutes+=1;line(s,'road.fed','먹이를 받아 든 동물이 비켜났습니다. 식량 하나를 사용했습니다.',[['close','항구로 간다.']]);break;
      case 'detour':if(s.route){accepted=false;break;}s.route='detour';s.minutes+=3;line(s,'road.detoured','해안 우회로를 걸었습니다. 식량은 남았고 시간이 더 걸렸습니다.',[['close','항구로 간다.']]);break;
      case 'drive':if(s.route){accepted=false;break;}s.route='drive';s.minutes+=1;line(s,'road.driven','천천히 다가가자 동물이 길을 비켜 주었습니다.',[['close','항구로 간다.']]);break;
      case 'present-seal':if(s.sealOwner!=='player'&&!(s.sealOwner==='companion'&&s.companionPresent)){accepted=false;break;}s.sealOwner='guard';s.gateOpen=true;line(s,'guard.seal-accepted','증표를 확인했습니다. 항구 문을 열겠습니다.',[['enter-harbor','항구에 들어간다.'],['close','대화를 마친다.']]);break;
      case 'enter-harbor':if(!s.gateOpen){accepted=false;break;}s.arrived=true;line(s,'harbor.arrived','항구에 들어왔습니다. 지나온 선택은 기록에 남습니다.',[['close','마을을 돌아본다.']]);break;
      case 'close':s.dialogue=null;break;
      default:accepted=false;
    }
    if(!accepted)return {...before,events:[...before.events,{action,accepted:false,lineId:before.lastLineId}]};
    const keys=['introRead','noteKnown','sharedRule','sealOwner','companionPresent','route','rations','minutes','gateOpen','arrived'];
    const changed=Object.fromEntries(keys.filter(k=>before[k]!==s[k]).map(k=>[k,{from:before[k],to:s[k]}]));
    s.events.push({action,accepted:true,lineId:s.lastLineId,changed});
    return s;
  }
  return {create,act,guard};
});
