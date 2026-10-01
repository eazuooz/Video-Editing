// Adapt the additive editor; never re-run a completed video or its synthesis.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'projects/praise-player/production');
for(const file of ['build-expansion-v2.cjs','render-recap-v2.cjs','review-expanded-sources.py','run-expansion-v2.cjs','run-expansion-render-v2.cjs','verify-expanded-v2.py','caption-expanded-v2.cjs','finalize-expansion-v2.cjs']){
 const target=path.join(__dirname,file);if(fs.existsSync(target))throw Error('Resume existing engine '+file);
 let source=fs.readFileSync(path.join(base,file),'utf8').replaceAll('praise-player','responsive-game-feedback').replaceAll('PRAISE_','RESPONSIVE_').replaceAll("['sports','ringfit']","['desk','alyx']").replaceAll('성공 피드백 — 원본 설명 보존·실제 행동 해설 확장본','입력 응답 — 원본 설명 보존·실제 행동 해설 확장본').replaceAll('original paired defense tests','original input-state tests');
 if(file==='build-expansion-v2.cjs'){
  const a=source.indexOf('   // Protect native input rows'),b=source.indexOf('   scene.cuts.push(c);',a);
  if(a<0||b<0)throw Error('Source-specific placement marker changed');
  source=source.slice(0,a)+`   if(w.key==='oni'){
    // Top-center whitespace avoids native resource, build, job and crew panels.
    c.captionCenterX=970;c.captionCenterY=165;c.captionMaxWidth=1300;
    c.protectedRegions=[[0,300,1920,1080],[0,0,1920,75]];
   }
`+source.slice(b);
  source=source.replace('fps=60,scale=1920:1080,setsar=1,drawtext=',"${c.crop?'crop='+c.crop.join(':')+',':''}fps=60,scale=1920:1080,setsar=1,drawtext=");
 }
 if(file==='caption-expanded-v2.cjs')source=source.replace('native Ring Fit instructions, Hi-Fi beat rows and Sports physical-input inset excluded','native ONI resource, crew, jobs and build panels excluded');
 fs.writeFileSync(target,source);
}
const f=path.join(__dirname,'build-video.cjs');let s=fs.readFileSync(f,'utf8');
if(!s.includes("work=path.join(__dirname,'final-v1')"))throw Error('Preserve existing editor adaptation');
s=s.replace("work=path.join(__dirname,'final-v1')","work=path.join(__dirname,process.env.RESPONSIVE_REVISION||'final-v1')").replace("mf=path.join(root,'projects',slug,'project.json')","mf=path.resolve(root,process.env.RESPONSIVE_MANIFEST||`projects/${slug}/project.json`)");fs.writeFileSync(f,s);
console.log('Additive engine adapted; no synthesis/render started.');
