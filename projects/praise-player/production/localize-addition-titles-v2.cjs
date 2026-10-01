// Localize only English chapter headings; voice, subtitle text/timing and video unchanged.
const fs=require('node:fs'),file='projects/praise-player/publishing/youtube-upload-v2.json',r=JSON.parse(fs.readFileSync(file,'utf8'));
const pairs=[['결과와 인정하는 반응 구별하기','Distinguish Outcomes from Acknowledgement'],['동작 가까이에 반응 붙이기','Connect Feedback to the Action'],['어떤 행동을 인정하는가','Identify the Action Being Recognized'],['작은 성공과 큰 마무리의 강도','Small Successes and Larger Completions'],['부분의 성공을 정직하게 다루기','Acknowledge Partial Success Honestly'],['반응과 다음 행동을 함께 보기','Read Feedback Alongside the Next Action']];
for(const [ko,en] of pairs){r.englishMetadata.description=r.englishMetadata.description.replaceAll(ko,en);r.descriptionBody.en=r.descriptionBody.en.replaceAll(ko,en);}
fs.writeFileSync(file,JSON.stringify(r,null,2)+'\n');fs.writeFileSync('projects/praise-player/publishing/upload-description-v2.en.txt',r.englishMetadata.description+'\n');
const f='projects/praise-player/publishing/youtube-v2.en.md';if(fs.existsSync(f)){let t=fs.readFileSync(f,'utf8');for(const [a,b]of pairs)t=t.replaceAll(a,b);fs.writeFileSync(f,t);}
console.log('English chapter headings localized before their Studio publication.');
