const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),slug='responsive-game-feedback',old='praise-player',mc=path.join(root,'motion-canvas/src/projects',slug);
for(const name of ['build-video.cjs','render-reel.cjs','verify-video.py','align-captions.py']){
 if(name==='align-captions.py'&&fs.existsSync(path.join(__dirname,name)))continue;
 let code=fs.readFileSync(path.join(root,'projects',old,'production',name),'utf8').replaceAll(old,slug);
 if(name==='build-video.cjs'){
  const a=code.indexOf('const catalog={'),b=code.indexOf('fs.mkdirSync(work',a);
  code=code.slice(0,a)+`const catalog={
 desk:{file:raw('desk-job-official'),originalOffset:0,title:'에이퍼처 데스크 잡 · 화면 안의 조작 패널',credit:'Valve | mVDFJRM6F9k | source audio omitted',url:'https://www.youtube.com/watch?v=mVDFJRM6F9k',muteSourceAudio:true},
 alyx:{file:raw('alyx-official'),originalOffset:0,title:'하프라이프 알릭스 · 대상 강조와 손',credit:'Valve | LTLotwKpLgk | source audio omitted',url:'https://www.youtube.com/watch?v=LTLotwKpLgk',muteSourceAudio:true},
 ${['receipt','blocked','menu','cutscene','pending','context'].map(n=>`${n}:{file:${n==='menu'?"'shared/assets/responsive-game-feedback/playtests-v2/menu-sound.mp4'":"own('"+n+"-sound')"},originalOffset:0,title:'직접 만든 입력 상태 테스트 · ${n}',credit:'Original actual keyboard state transitions; simulated save explicitly identified'}`).join(',\n')}
};
const slots=[
 [['desk',4,5],['alyx',125,8],['receipt',0,19]],
 [['blocked',1,31]],[['menu',2,30]],[['cutscene',0,32]],[['pending',0,32]],[['context',0,32]]
];
`+code.slice(b);code=code.replace('const weights=[.58,.62,.62,.60,.60,.58]','const weights=[.60,.60,.58,.62,.60,.60]').replaceAll('게임은 왜 플레이어를 칭찬할까 — 검토본','버튼 눌렀는데 무반응 — 검토본');
 }
 if(name==='verify-video.py')code=code.replaceAll("['sports','ringfit']","['desk','alyx']");
 fs.writeFileSync(path.join(__dirname,name),code);
}
// Keep future directly reviewed UI corrections in the new caption file.
if(!fs.existsSync(path.join(__dirname,'caption-video.cjs'))){
 let code=fs.readFileSync(path.join(root,'projects',old,'production/caption-video.cjs'),'utf8').replaceAll(old,slug);
 code=code.replace("...(c.key==='sports'&&c.sourceIn===244?[c.timelineStart+1]:[])","");
 code=code.replace("['timing','specificity','strength','honesty','placement']","['receipt','blocked','menu','cutscene','pending','context']");
 const first=code.indexOf('  const sportsPortrait='),last=code.indexOf('  if(cue.lines.length',first);
 code=code.slice(0,first)+"  const centerX=960,centerY=cut?.key==='alyx'?155:970,x=Math.round(centerX-width/2),y=Math.round(centerY-height/2);\n"+code.slice(last);
 const a=code.indexOf("  const protectedRegion="),b=code.indexOf('  // Actual external-game',a);
 code=code.slice(0,a)+"  const protectedRegion=cut?.key==='alyx'?[0,350,1920,1080]:own?[0,220,1920,885]:cut?[0,180,1920,890]:[120,250,1800,883];\n  const extraProtectedUi=[];\n"+code.slice(b);
 code=code.replace('bottom by default; Ring Fit upper-right preserves movement instructions, Sports shifts left or above name/rating HUD after the actual Win transition','bottom on desk/prototypes/explanations; Alyx top-center preserves lower object/hand interaction');
 fs.writeFileSync(path.join(__dirname,'caption-video.cjs'),code);
}
for(const name of ['body-scene.tsx','scenes/membership-outro.tsx'])fs.copyFileSync(path.join(root,'motion-canvas/src/projects',old,name),path.join(mc,name));
for(let i=0;i<6;i++){const id=String(i+1).padStart(2,'0');fs.writeFileSync(path.join(mc,`scenes/scene${id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {bodyScene} from '../body-scene';\nexport default makeScene2D(function*(view){yield* bodyScene(view,${i});});\n`);fs.writeFileSync(path.join(mc,`lookdev-scene${i}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from './diagram';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${i},10);});\n`);}
fs.writeFileSync(path.join(mc,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${Array.from({length:6},(_,i)=>`import s${i} from './lookdev-scene${i}?scene';`).join('\n')}\nexport default makeProject({name:'responsive-game-feedback-lookdev',scenes:[s0,s1,s2,s3,s4,s5]});\n`);
const file=path.join(root,'motion-canvas/projects.json'),routes=JSON.parse(fs.readFileSync(file,'utf8'));for(const name of ['lookdev-project','explanation-project']){const route='./src/projects/'+slug+'/'+name+'.ts';if(!routes.includes(route))routes.push(route);}fs.writeFileSync(file,JSON.stringify(routes,null,2)+'\n');
console.log('Six independent original explanation wrappers; final production remains gated by ASR and actual input logs.');
