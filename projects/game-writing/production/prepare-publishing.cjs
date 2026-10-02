// Local editorial drafts only. No platform writes and no fabricated chapter timestamps.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../..'),base='projects/game-writing';
const manifest=JSON.parse(fs.readFileSync(path.join(root,base+'/project.json'),'utf8'));
const defaults=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/youtube-defaults.json'),'utf8'));
assert.equal(defaults.defaultPrivacyStatus,'private');assert.equal(defaults.description.includePublicSourceCredits,false);
const koFooter=fs.readFileSync(path.join(root,defaults.description.channelDefaultSnapshot),'utf8').split('📚 수업 노트')[0].trim();
const priorEnglish=fs.readFileSync(path.join(root,'projects/responsive-game-feedback/publishing/upload-description-v2.en.txt'),'utf8');
const enFooter=priorEnglish.slice(priorEnglish.indexOf('🎮 Build games with real programming skills.')).trim();
const body={
 ko:'게임 시나리오와 분기 대사는 플레이어의 선택과 방문 순서가 달라져도 실제 상황과 맞아야 합니다. 정보의 주인, 이야기 물건의 소유자, 동료의 부재, 선택 뒤의 합류와 놓친 설명을 어떻게 다룰지 실제 화면과 자체 이야기 게임으로 살펴봅니다.\n\n디비니티: 오리지널 신 2의 공식 대화·게임 마스터 제작 시연에서 보이는 작업을 관찰하고, 직접 만든 「항구의 봉인」에서 다른 순서와 소유 상태를 실행합니다. 흰 2.5D 설명 사이마다 행동과 결과를 연결하며, 화면에 보이지 않는 내부 구현을 단정하지 않습니다. 대사의 옆에 “이 말이 참이려면 무엇이 먼저 일어나야 할까?”를 함께 적어 보세요.\n\n자체 상태 검증은 플레이와 대사의 모순을 찾는 기술 검증입니다. 이야기의 재미와 이해·감정은 사람의 플레이 검토가 필요합니다. 한국어 내레이션과 수동 한국어·영어 자막을 제공합니다.',
 en:'Game stories and branching dialogue should remain coherent when players choose a different order or response. Explore who knows a fact, who currently holds a story item, what changes when a companion leaves, what survives after branches rejoin, and how players can recover essential information.\n\nObserve visible dialogue and Game Master authoring actions in official Divinity: Original Sin 2 demonstrations. Then try different orders and ownership states in our original playable prototype, The Harbor Seal. Real actions and results appear between white 2.5D explanations. These short source clips do not establish hidden implementation details. Add one question beside each line: “What must happen first for this statement to be true?”\n\nThe prototype checks technical consistency between play and dialogue. People still need to review comprehension, emotion and enjoyment. Korean narration with manually prepared Korean and English subtitles.'
};
const tags={ko:'#게임시나리오 #게임기획 #게임디자인 #게임개발',en:'#GameWriting #NarrativeDesign #GameDesign #GameDevelopment'};
const draft={preparedAt:new Date().toISOString(),status:'draft-awaiting-measured-chapters-and-final-video',privacy:'private',publicSchedule:false,thumbnail:base+'/publishing/thumbnail.png',languages:{},chapters:{status:'pending-measured-scene-starts',times:null},subtitles:{method:'manual-file-upload',status:'pending-final-KO-EN-output'},platformApplied:false,internalRightsRecord:base+'/sources/SOURCES.md'};
for(const language of ['ko','en']){
 const footer=language==='ko'?koFooter:enFooter;
 for(const link of [defaults.coaching.url,defaults.membershipUrl,'https://discord.gg/wZuqe7fqkR'])assert(footer.includes(link),'Retain approved channel link '+link);
 assert(!footer.includes('여기에-GitHub-주소')&&!footer.includes('노션 또는 강의 자료 링크'));
 draft.languages[language]={title:manifest.titles[language],descriptionBody:body[language],hashtags:tags[language],channelFooter:footer};
 const md=['# YouTube 게시 정보 — '+(language==='ko'?'한국어':'English'),'','내부 준비 상태: 최종 음성·영상과 실측 챕터를 기다리는 초안. 플랫폼 적용 없음. 공개·예약 없음.','', '## 제목','',manifest.titles[language],'','## 설명','',body[language],'',tags[language],'',footer,'','## 챕터 작성 상태','','실측 타임라인 확정 후 장면 시작과 마지막 10초 회원 엔딩을 함께 반영한다. 임시 00:00 챕터나 내부 권리 기록은 공개 설명에 넣지 않는다.',''];
 fs.writeFileSync(path.join(root,base+'/publishing/youtube.'+language+'.md'),md.join('\n'));
}
fs.writeFileSync(path.join(root,base+'/publishing/metadata-draft.json'),JSON.stringify(draft,null,2)+'\n');
console.log('KO/EN metadata drafted with coaching, Discord and membership links; chapters/platform application remain pending.');
