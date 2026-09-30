// Reuse verified technical helpers; all game intervals and editorial content are new.
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'../../..'),old='deconstruct-analyze-rebuild',slug='meaningful-quests';
for(const name of ['build-video.cjs','render-reel.cjs','align-captions.py','caption-video.cjs','verify-video.py']){
 let code=fs.readFileSync(path.join(root,'projects',old,'production',name),'utf8').replaceAll(old,slug).replaceAll('analyze-rebuild-explanation-reel','meaningful-quests-explanation-reel').replaceAll('analyze-rebuild-lookdev','meaningful-quests-lookdev');
 if(name==='build-video.cjs'){
  const a=code.indexOf('const catalog={'),b=code.indexOf('fs.mkdirSync(work',a);
  code=code.slice(0,a)+`const catalog={
 skyrim:{file:raw('skyrim-rybolt'),originalOffset:0,title:'스카이림 · 이동과 채집 행동 예시',credit:'Skyrim | Rybolt | youtu.be/jPZVtKpHjU8 · audio omitted',url:'https://www.youtube.com/watch?v=jPZVtKpHjU8',muteSourceAudio:true},
 subnautica:{file:raw('subnautica-rfgc'),originalOffset:0,title:'서브노티카 · 재료 탐색과 산소',credit:'Subnautica | Royalty Free Game Clips | youtu.be/0EUdWPaxoRA · audio omitted',url:'https://www.youtube.com/watch?v=0EUdWPaxoRA',muteSourceAudio:true},
 comparison:{file:own('comparison-sound'),originalOffset:0,title:'직접 만든 배달 테스트 · 점수와 세계 상태 비교',credit:'Original keyboard, inventory, delivery and collision-state test'},
 delivery:{file:own('delivery-sound'),originalOffset:0,title:'직접 만든 배달 테스트 · 수집에서 새 길까지',credit:'Original single continuous delivery; keyboard event capture'},
 shortcut:{file:own('shortcut-sound'),originalOffset:0,title:'직접 만든 귀환 테스트 · 빈 가방과 우회로',credit:'Original inventory gate, drop and route-choice capture'}
};
// Source intervals are unique across the entire body; normal speed, no loops.
const slots=[
 [['skyrim',380,8],['subnautica',30,12]],
 [['subnautica',446,16],['subnautica',134,10],['subnautica',64,12]],
 [['skyrim',396,22]],
 [['comparison',0,34]],
 [['delivery',14,8],['shortcut',0,35]],
 [['delivery',0,9],['delivery',22,12],['subnautica',146,13]]
];
`+code.slice(b);
  code=code.replace('const weights=[.60,.60,.60,.72,.62,.40]','const weights=[.55,.62,.55,.75,.65,.40]').replaceAll('게임을 베끼지 않고 배우는 법 — 검토본','심부름 퀘스트는 왜 지루할까 — 검토본');
  code=code.replace('const frames=Math.min(left,Math.round(available*60));left-=frames;','const frames=Math.min(left,Math.round(available*60));if(frames<180)throw Error(`Scene ${s.id}: avoid a sub-3-second flash cut (${key}, ${frames} frames)`);left-=frames;');
 }
 if(name==='caption-video.cjs'){
  code=code.replace("['landing','retry','observe','variants']","['comparison','delivery','shortcut']").replace('centerY=970',"centerY=cut&&['skyrim','subnautica'].includes(cut.key)?900:970");
  code=code.replace("const protectedRegion=own?[0,220,1920,890]:cut?[0,260,1920,885]:[120,250,1800,883];","const protectedRegion=own?[0,220,1920,890]:cut?[0,250,1920,820]:[120,250,1800,883];\n  if(cut&&['skyrim','subnautica'].includes(cut.key)&&y+height+14>990)throw Error('External-game caption overlaps bottom HUD');");
 }
 if(name==='verify-video.py')code=code.replace("['meat','hollow','portal']","['skyrim','subnautica']");
 if(name==='align-captions.py'){
  code=code.replace("for lang in ['ko','en']:","def english_wrap(text):\n    if len(text)<=68:return text\n    words=text.split();pairs=[(' '.join(words[:i]),' '.join(words[i:])) for i in range(1,len(words))]\n    a,b=min(pairs,key=lambda p:abs(len(p[0])-len(p[1])))\n    return a+'\\n'+b\nfor lang in ['ko','en']:");
  code=code.replace('{c[lang]}','{english_wrap(c[lang]) if lang=="en" else c[lang]}');
 }
 fs.writeFileSync(path.join(__dirname,name),code);
}
const mc=path.join(root,'motion-canvas/src/projects',slug);
fs.copyFileSync(path.join(root,'motion-canvas/src/projects',old,'body-scene.tsx'),path.join(mc,'body-scene.tsx'));
fs.copyFileSync(path.join(root,'motion-canvas/src/projects',old,'scenes/membership-outro.tsx'),path.join(mc,'scenes/membership-outro.tsx'));
for(let i=0;i<6;i++){const id=String(i+1).padStart(2,'0');fs.writeFileSync(path.join(mc,`scenes/scene${id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {bodyScene} from '../body-scene';\nexport default makeScene2D(function*(view){yield* bodyScene(view,${i});});\n`);}
fs.writeFileSync(path.join(mc,'lookdev-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${Array.from({length:6},(_,i)=>`import s${i} from './lookdev-scene${i}?scene';`).join('\n')}\nexport default makeProject({name:'meaningful-quests-lookdev',scenes:[s0,s1,s2,s3,s4,s5]});\n`);
for(let i=0;i<6;i++)fs.writeFileSync(path.join(mc,`lookdev-scene${i}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from './diagram';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${i},10);});\n`);
const registry=path.join(root,'motion-canvas/projects.json'),routes=JSON.parse(fs.readFileSync(registry,'utf8'));for(const n of ['lookdev-project','explanation-project']){const route='./src/projects/'+slug+'/'+n+'.ts';if(!routes.includes(route))routes.push(route);}fs.writeFileSync(registry,JSON.stringify(routes,null,2)+'\n');
