// Reuse verified rendering mechanics, never a prior video's teaching scenes/cuts.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),slug='praise-player',old='counting-animation-frames',mc=path.join(root,'motion-canvas/src/projects',slug);
for(const name of ['build-video.cjs','render-reel.cjs','caption-video.cjs','verify-video.py','finalize.cjs']){
 // The checked-in caption implementation owns source-specific UI placement.
 // Preserve its later direct-frame corrections when refreshing generic helpers.
 if(name==='caption-video.cjs'&&fs.existsSync(path.join(__dirname,name)))continue;
 let code=fs.readFileSync(path.join(root,'projects',old,'production',name),'utf8').replaceAll(old,slug);
 if(name==='build-video.cjs'){
  const a=code.indexOf('const catalog={'),b=code.indexOf('fs.mkdirSync(work',a);
  code=code.slice(0,a)+`const catalog={
 sports:{file:raw('switch-sports-official'),originalOffset:0,title:'닌텐도 스위치 스포츠 · 성공 직후의 인정',credit:'Nintendo of America | tiwjvBSS_Wk | source audio omitted',url:'https://www.youtube.com/watch?v=tiwjvBSS_Wk',muteSourceAudio:true},
 ringfit:{file:raw('ringfit-official'),originalOffset:0,title:'링 피트 어드벤처 · 동작 평가',credit:'Nintendo of America | skBNiJd61Qw | source audio omitted',url:'https://www.youtube.com/watch?v=skBNiJd61Qw',muteSourceAudio:true},
 timing:{file:'shared/assets/praise-player/playtests-v2/timing-sound.mp4',originalOffset:0,title:'직접 만든 방어 테스트 · 반응 시점',credit:'Original equal-state keyboard and collision test'},
 specificity:{file:own('specificity-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 행동 문구',credit:'Original actual block/dodge outcomes'},
 strength:{file:'shared/assets/praise-player/playtests-v2/strength-sound.mp4',originalOffset:0,title:'직접 만든 방어 테스트 · 성과와 강도',credit:'Original streak collision counter; equal fixed-center labels, full text visible'},
 honesty:{file:own('honesty-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 실패와 실제 성공',credit:'Original equal missed attack and health deduction'},
 placement:{file:own('placement-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 다음 행동 공간',credit:'Original same input and message, changed visual placement'}
};
const slots=[
 [['sports',237,5],['ringfit',442,10.5],['specificity',26.5,5.5]],
 [['timing',0,32]],
 [['specificity',0,32]],
 [['sports',244,3.5],['strength',0,32]],
 [['honesty',0,32]],
 [['placement',0,32]]
];
`+code.slice(b);
  code=code.replace('playtests-v2/${n}.mp4','playtests-v1/${n}.mp4');
  code=code.replace('const weights=[.58,.62,.65,.60,.62,.45]','const weights=[.58,.62,.62,.60,.60,.58]');
  code=code.replaceAll('프레임이 게임 손맛을 바꾸는 이유 — 검토본','게임은 왜 플레이어를 칭찬할까 — 검토본');
  // Source/rights stay in internal records; no new public credit block/overlay.
  const first=code.indexOf('     const creditFilter='),last=code.indexOf('     // 16:9 games',first);
  code=code.slice(0,first)+"     const creditFilter='null';\n"+code.slice(last);
 }
 if(name==='caption-video.cjs'){
  code=code.replaceAll("['rate','interval','poses','pause','render']","['timing','specificity','strength','honesty','placement']").replaceAll("['megaman','rise']","['sports','ringfit']");
  code=code.replace(',x=Math.round(960-width/2)','')
   .replace('centerY=970,y=',"centerX=cut?.key==='ringfit'?1120:960,centerY=cut?.key==='ringfit'?155:970,x=Math.round(centerX-width/2),y=")
   .replace('\\\\pos(960,','\\\\pos(${centerX},')
   .replace('const protectedRegion=own?',"const protectedRegion=cut?.key==='ringfit'?[0,250,1920,1080]:own?")
   .replace('centerY,shadowBottom','centerX,centerY,shadowBottom')
   .replace('bottom on all footage and explanations; input HUD is above caption area','bottom by default; Ring Fit upper-right region preserves bottom movement instruction and counters');
 }
 if(name==='verify-video.py')code=code.replaceAll("['megaman','rise']","['sports','ringfit']");
 if(name==='finalize.cjs'){
  code=code.replaceAll("['Mega Man 11','Monster Hunter Rise']","['Nintendo Switch Sports','Ring Fit Adventure']").replaceAll("['Mega Man 11','Monster Hunter Rise','Original Frame Timing Lab']","['Nintendo Switch Sports','Ring Fit Adventure','Original Praise Defense Lab']");
  code=code.replace("'Nimbus 복원", "'Nintendo 자료의 개인 이용자 조건과 채널의 게시 권리 확인은 남아 있습니다.','Nimbus 복원");
 }
 fs.writeFileSync(path.join(__dirname,name),code);
}
// No previous video's exact-hash numeric exception is carried into alignment.
fs.writeFileSync(path.join(__dirname,'align-captions.py'),fs.readFileSync(path.join(root,'projects/meaningful-quests/production/align-captions.py'),'utf8').replaceAll('meaningful-quests',slug));
for(const name of ['body-scene.tsx','scenes/membership-outro.tsx'])fs.copyFileSync(path.join(root,'motion-canvas/src/projects',old,name),path.join(mc,name));
for(let i=0;i<6;i++){const id=String(i+1).padStart(2,'0');fs.writeFileSync(path.join(mc,`scenes/scene${id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {bodyScene} from '../body-scene';\nexport default makeScene2D(function*(view){yield* bodyScene(view,${i});});\n`);fs.writeFileSync(path.join(mc,`lookdev-scene${i}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from './diagram';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${i},10);});\n`);}
fs.writeFileSync(path.join(mc,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${Array.from({length:6},(_,i)=>`import s${i} from './lookdev-scene${i}?scene';`).join('\n')}\nexport default makeProject({name:'praise-player-lookdev',scenes:[s0,s1,s2,s3,s4,s5]});\n`);
const file=path.join(root,'motion-canvas/projects.json'),routes=JSON.parse(fs.readFileSync(file,'utf8'));for(const name of ['lookdev-project','explanation-project']){const route='./src/projects/'+slug+'/'+name+'.ts';if(!routes.includes(route))routes.push(route);}fs.writeFileSync(file,JSON.stringify(routes,null,2)+'\n');
console.log('Six independent scene wrappers and reusable technical helpers ready.');
