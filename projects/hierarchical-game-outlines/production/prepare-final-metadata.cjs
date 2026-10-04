const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),dir=path.resolve(__dirname,'../publishing');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');
const plan=read(path.join(__dirname,'final-v1/plan.json')),draft=read(path.join(dir,'metadata-draft.json')),en=read(path.join(dir,'../script/narration.en.json'));
const clock=t=>{let n=Math.floor(t);return `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;};
const languages={};
for(const language of ['ko','en']){
 const chapters=plan.scenes.map((s,i)=>(i?'': '00:00 ').length?`00:00 ${language==='ko'?s.title:en.scenes[i].title}`:`${clock(s.start)} ${language==='ko'?s.title:en.scenes[i].title}`);
 chapters.push(`${clock(plan.bodyEnd)} ${language==='ko'?'멤버쉽 후원 감사':'Membership thanks'}`);
 const original=draft.descriptions[language],pos=original.indexOf('🎮');if(pos<0)throw Error('Preserved footer marker absent');
 const body=original.slice(0,pos).trim()+`\n\n${language==='ko'?'챕터':'Chapters'}\n${chapters.join('\n')}`;
 languages[language]={title:draft.titles[language],descriptionBody:body,description:body+'\n\n'+original.slice(pos),chapters};
 write(path.join(dir,`youtube.${language}.md`),`# ${draft.titles[language]}\n\n${languages[language].description}\n`);
}
const meta={revision:'final-v1',preparedAt:new Date().toISOString(),privacyStatus:'private',scheduled:false,languages,
 chapterSource:'projects/hierarchical-game-outlines/production/final-v1/plan.json',chapterSourceSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'final-v1/plan.json'))).digest('hex'),seconds:plan.seconds,bodyEnd:plan.bodyEnd,
 finalRenderedQA:'technical-QA-passed-human-listening-pending',platformUpload:'pending',sourceCreditPolicy:'Public source blocks omitted per user; internal source/rights evidence retained.'};
write(path.join(dir,'metadata-final.json'),meta);console.log('Actual measured KO/EN chapters added above preserved channel introductions. Upload pending.');
