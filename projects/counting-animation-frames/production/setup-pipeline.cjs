// Reuse technical rendering code; the script, prototype, diagrams and cuts are new.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),old='meaningful-quests',slug='counting-animation-frames';
for(const name of ['build-video.cjs','render-reel.cjs','align-captions.py','caption-video.cjs','verify-video.py','finalize.cjs']){
 let code=fs.readFileSync(path.join(root,'projects',old,'production',name),'utf8').replaceAll(old,slug);
 if(name==='build-video.cjs'){
  const a=code.indexOf('const catalog={'),b=code.indexOf('fs.mkdirSync(work',a);
  code=code.slice(0,a)+`const catalog={
 megaman:{file:raw('megaman11-capcom'),originalOffset:0,title:'메가맨 11 · 점프와 동작 관찰',credit:'Mega Man 11 | Official Capcom Europe | 3aSC5A726f0 · audio omitted',url:'https://www.youtube.com/watch?v=3aSC5A726f0',muteSourceAudio:true},
 rise:{file:raw('mhrise-capcom'),originalOffset:0,title:'몬스터 헌터 라이즈 · 수렵피리 동작 관찰',credit:'Monster Hunter Rise | Official Monster Hunter | n-5jAq2Nyhs · audio omitted',url:'https://www.youtube.com/watch?v=n-5jAq2Nyhs',muteSourceAudio:true},
 rate:{file:own('rate-sound'),originalOffset:0,title:'직접 만든 테스트 · 기준 속도 60 / 30',credit:'Original accepted-input and fixed-rule-clock test'},
 interval:{file:'shared/assets/counting-animation-frames/playtests-v3/interval-sound.mp4',originalOffset:0,title:'직접 만든 테스트 · 기본 B와 준비를 줄인 A',credit:'Original collision rectangle and action-ready boundaries; B is the fixed default'},
 poses:{file:own('poses-sound'),originalOffset:0,title:'직접 만든 테스트 · 그림 수만 변경',credit:'Original separate pose and collision clocks'},
 pause:{file:own('pause-sound'),originalOffset:0,title:'직접 만든 테스트 · 충돌 뒤 4눈금 멈춤',credit:'Original combat-clock pause with continuing wall clock'},
 render:{file:own('render-sound'),originalOffset:0,title:'직접 만든 테스트 · 화면 30 / 60',credit:'Original display-sampling rate with fixed 60Hz collision logic'}
};
const slots=[
 [['megaman',12,8],['rise',9,14]],
 [['rate',0,32]],
 [['interval',0,32]],
 [['poses',0,32]],
 [['pause',0,32]],
 [['render',0,32]]
];
`+code.slice(b);
  code=code.replace('const weights=[.55,.62,.55,.75,.65,.40]','const weights=[.58,.62,.65,.60,.62,.45]').replaceAll('심부름 퀘스트는 왜 지루할까 — 검토본','프레임이 게임 손맛을 바꾸는 이유 — 검토본');
  const start=code.indexOf(' scenes.forEach((s,i)=>s.gameFrames='),end=code.indexOf(' let diagramStart=',start);
  if(start<0||end<0)throw Error('Measured allocation helper changed; inspect before reuse');
  code=code.slice(0,start)+` // Respect each new capture's real duration. Balance the body rather than
 // extending a short source or forcing every scene to the same percentage.
 const caps=scenes.map((s,i)=>Math.min(Math.floor(slots[i].reduce((n,c)=>n+c[2],0)*60),s.frames-480));
 scenes.forEach((s,i)=>s.gameFrames=Math.min(caps[i],Math.round(s.frames*weights[i])));
 const target=Math.ceil(bodyFrames*.6);let delta=target-scenes.reduce((n,s)=>n+s.gameFrames,0);
 for(const i of [5,3,0,4,2,1]){
  if(!delta)break;
  const change=delta>0?Math.min(delta,caps[i]-scenes[i].gameFrames):-Math.min(-delta,scenes[i].gameFrames-180);
  scenes[i].gameFrames+=change;delta-=change;
 }
 if(delta)throw Error('Need fresh related capture; never loop/slow down footage to fill '+delta+' frames');
`+code.slice(end);
 }
 if(name==='caption-video.cjs'){
  code=code.replaceAll("['comparison','delivery','shortcut']","['rate','interval','poses','pause','render']").replaceAll("['skyrim','subnautica']","['megaman','rise']");
  code=code.replace("centerY=cut&&['megaman','rise'].includes(cut.key)?900:970","centerY=970");
  code=code.replace("if(cut&&['megaman','rise'].includes(cut.key)&&y+height+14>990)throw Error('External-game caption overlaps bottom HUD');",'// Actual external-game action is checked in every rendered cue segment.');
 }
 if(name==='verify-video.py')code=code.replace("['skyrim','subnautica']","['megaman','rise']");
 if(name==='align-captions.py')code=code.replace("assert match.ratio()>.93,(sid,match.ratio())",`# One actually inspected current-hash exception: only numerical orthography differs.
    approved=json.loads((BASE/'production/narration-scene-review.json').read_text(encoding='utf-8'))
    import hashlib
    digest=hashlib.sha256((out/'chunks'/f'{sid}-scene.wav').read_bytes()).hexdigest()
    numerical_exception=(sid=='02' and digest=='1952e3381f9b5a17fd27831ed03bf53df069690b19f3c76987571a75dded5a7f' and any(r['scene']==sid and r['audioSha256']==digest and r['result']=='passed-content-and-ending' for r in approved['scenes']))
    assert match.ratio()>.93 or numerical_exception,(sid,match.ratio())`);
 if(name==='finalize.cjs')code=code.replaceAll("['Skyrim','Subnautica']","['Mega Man 11','Monster Hunter Rise']").replaceAll("['Skyrim','Subnautica','Original Bridge Delivery Lab']","['Mega Man 11','Monster Hunter Rise','Original Frame Timing Lab']");
 fs.writeFileSync(path.join(__dirname,name),code);
}
const mc=path.join(root,'motion-canvas/src/projects',slug);
for(const name of ['body-scene.tsx','scenes/membership-outro.tsx'])fs.copyFileSync(path.join(root,'motion-canvas/src/projects',old,name),path.join(mc,name));
for(let i=0;i<6;i++){const id=String(i+1).padStart(2,'0');fs.writeFileSync(path.join(mc,`scenes/scene${id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {bodyScene} from '../body-scene';\nexport default makeScene2D(function*(view){yield* bodyScene(view,${i});});\n`);}
fs.writeFileSync(path.join(mc,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${Array.from({length:6},(_,i)=>`import s${i} from './lookdev-scene${i}?scene';`).join('\n')}\nexport default makeProject({name:'counting-animation-frames-lookdev',scenes:[s0,s1,s2,s3,s4,s5]});\n`);
for(let i=0;i<6;i++)fs.writeFileSync(path.join(mc,`lookdev-scene${i}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from './diagram';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${i},10);});\n`);
const file=path.join(root,'motion-canvas/projects.json'),routes=JSON.parse(fs.readFileSync(file,'utf8'));for(const name of ['lookdev-project','explanation-project']){const route='./src/projects/'+slug+'/'+name+'.ts';if(!routes.includes(route))routes.push(route);}fs.writeFileSync(file,JSON.stringify(routes,null,2)+'\n');
