const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),dir=path.resolve(__dirname,'../publishing');
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'final-v1/plan.json'),'utf8'));
const projectPath=path.join(root,'projects/picking-sides/project.json'),project=JSON.parse(fs.readFileSync(projectPath,'utf8'));
const time=t=>{const s=Math.floor(t);return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');};
const ko=['도입: 누구를 보고 있나요?','대상·이유·상황을 나누기','외형과 색으로 같은 대상 다시 찾기','색 하나에 맡기지 않는 식별 정보','한 명을 고른 뒤 손과 몸 따라가기','응원할 이유와 보상을 구분하기','발판·톱날·도로에서 위험 읽기','대상과 중요한 순간 연결하기','카메라가 바뀌어도 관심 이어가기','선택을 강요하지 않는 관전','낙하와 경기 결과를 구분하기','관전 화면을 점검하는 네 질문'];
const en=['Introduction: who are you watching?','Separate identity, interest and situation','Find the same player by shape and color','Do not rely on color alone','Choose one player and follow their movement','Reasons to root are different from rewards','Read risk from platforms, saws and roads','Connect the player to the important moment','Follow your player as the framing changes','Let viewers watch without forcing a choice','Distinguish a fall from the match result','Four questions for a spectator screen'];
const chapters=language=>[...plan.scenes.map((s,i)=>(i===0?'00:00':time(s.start))+' '+(language==='ko'?ko[i]:en[i])),time(plan.bodyEnd)+' '+(language==='ko'?'멤버쉽 후원 감사':'Membership thanks')].join('\n');
const titles={ko:'관전과 응원 대상의 게임 디자인: 왜 남의 플레이도 재미있을까?',en:'Spectator Game Design: Why Do We Root for Other Players?'};
const body={ko:`남의 게임을 보고도 한 캐릭터를 응원하게 되는 이유는 무엇일까요? 관전 화면의 게임 디자인을 대상 식별, 관심의 이유, 위험과 결과의 연결로 나누어 살펴봅니다.

Ultimate Chicken Horse와 Gang Beasts의 실제 플레이에서 외형·색·손·발판·카메라 구도를 관찰하고, 2.5D 설명으로 관전 화면을 점검하는 네 질문을 정리합니다. 서로 다른 발췌와 초기 버전의 장면은 별도 시도로 구분하며, 보이지 않은 전체 승패나 관전 재미의 실험 결과를 단정하지 않습니다.

챕터
${chapters('ko')}

#게임디자인 #게임개발 #게임기획 #관전`,en:`Why do we start rooting for one character while watching someone else's game? This video breaks spectator game design into identifying a player, finding a reason to care, and reading risk and results.

We observe real Ultimate Chicken Horse and Gang Beasts gameplay: character shapes and colors, hands, platforms, and changing camera framing. White 2.5D explanations connect these examples to four questions for a spectator screen. Separate excerpts and early builds are identified as separate attempts; we do not infer an unseen match winner or claim a measured improvement in enjoyment.

Chapters
${chapters('en')}

#GameDesign #GameDevelopment #SpectatorGames`};
const meta={revision:'final-v1',preparedAt:new Date().toISOString(),privacyStatus:'private',scheduled:false,languages:Object.fromEntries(['ko','en'].map(l=>[l,{title:titles[l],description:body[l]}])),chapterSource:'projects/picking-sides/production/final-v1/plan.json',seconds:plan.seconds,bodyEnd:plan.bodyEnd,topicKeywords:['관전','응원 대상','게임 디자인','spectator game design'],sourceCreditPolicy:'Public credits omitted per request; internal sources/rights retained.'};
fs.writeFileSync(path.join(dir,'metadata-final.json'),JSON.stringify(meta,null,2)+'\n');
for(const l of ['ko','en'])fs.writeFileSync(path.join(dir,`youtube.${l}.md`),`# ${titles[l]}\n\n${body[l]}\n`);
project.titles=titles;fs.writeFileSync(projectPath,JSON.stringify(project,null,2)+'\n');
console.log('Accurate bilingual titles, chapters and descriptions prepared; platform upload remains pending.');
