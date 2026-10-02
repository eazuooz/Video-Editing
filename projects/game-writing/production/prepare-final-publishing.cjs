const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),pub=path.join(root,'projects/game-writing/publishing'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),plan=read(path.join(__dirname,'final-v1/plan.json')),m=read(path.join(root,'projects/game-writing/project.json')),draft=read(path.join(pub,'metadata-draft.json'));
const clock=t=>{const n=Math.floor(t);return `${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`;};
const labels={ko:['선택과 순서가 달라도 말이 되는 대본','정보의 주인과 대화 기록','물건 소유와 동료의 부재','선택의 흔적을 남기는 분기 합류','필수 이야기 사실을 다시 얻는 방법','다른 순서로 대사를 실제 실행하기','조건까지 적는 게임 시나리오','멤버쉽가입 감사드립니다.'],en:['Writing for player choice and order','Who knows the fact?','Item ownership and absent companions','Keep consequences when branches rejoin','Recover essential story facts','Run the dialogue in different orders','Write the conditions beside the line','Thank you to our members']};
const starts=[0,...['03','05','07','09','11','12'].map(id=>plan.scenes.find(s=>s.id===id).start),plan.bodyEnd];
for(const lang of ['ko','en']){
 const chapters=starts.map((t,i)=>`${clock(t)} ${labels[lang][i]}`).join('\n'),d=draft.languages[lang];d.description=d.descriptionBody+'\n\n'+chapters+'\n\n'+d.hashtags+'\n\n'+d.channelFooter;
 fs.writeFileSync(path.join(pub,`upload-${lang}.txt`),d.description+'\n');fs.writeFileSync(path.join(pub,`youtube.${lang}.md`),`# ${d.title}\n\n비공개 업로드용 준비본 · 실제 플랫폼 저장/검사는 별도 영수증에 기록 · 공개 예약 없음\n\n${d.description}\n`);
}
draft.preparedAt=new Date().toISOString();draft.status='measured-metadata-prepared-awaiting-real-private-platform-save';draft.chapters={status:'actual-final-plan',times:starts};draft.platformApplied=false;fs.writeFileSync(path.join(pub,'metadata-final.json'),JSON.stringify(draft,null,2)+'\n');
const enfile=path.join(root,m.paths.scriptEn),en=read(enfile);const names={'13':'Speak Again After Asking','14':'Bring the Companion Back','15':'Test the Third Choice','16':'Remember a Completed Event'};for(const s of en.scenes)if(names[s.id])s.title=names[s.id];fs.writeFileSync(enfile,JSON.stringify(en,null,2)+'\n');console.log('KO/EN title, description and eight actual-time chapters prepared; platform not applied.');
