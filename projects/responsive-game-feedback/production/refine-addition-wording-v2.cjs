// Only after the first single runner finishes; preserve its actual review evidence.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2');
const run=JSON.parse(fs.readFileSync(path.join(__dirname,'revision-v2.json'),'utf8'));
if(run.execution?.state==='running')throw Error('Finish the existing runner before changing its script');
const asrPath=path.join(root,'shared/output/narration/responsive-game-feedback/qwen3-1.7b-additions-v2/responsive-game-feedback-additions-v2.asr-review.json');
const first=JSON.parse(fs.readFileSync(asrPath,'utf8'));
if(!first.scenes.find(s=>s.scene==='02')?.recognized.includes('다음 영상에서'))throw Error('Inspect actual first ASR before applying this repair');
fs.writeFileSync(path.join(work,'first-addition-asr-review.json'),JSON.stringify(first,null,2)+'\n');
const changes=[
  {scene:'02',line:8,ko:'우리 게임의 안내도, 막힌 이유와 다음에 확인할 정보를 나누어 적어 보세요.',en:'In your game, separate the current obstacle from the information to check next.',reason:'First scene02 recognition appends an unauthored sign-off at the ending with zero-duration words. Do not approve that uncertain ending; rephrase and re-synthesize only this scene, then verify the new hash.'},
  {scene:'05',line:7,ko:'선택한 작업의 표시는 남아 있지만, 캐릭터와 주변 지형이 바뀌는 모습을 함께 읽으면 계획과 진행을 구별하기 쉽습니다.',en:'The work markers remain while characters and nearby terrain change; reading them together helps distinguish a plan from work in progress.',reason:'Replace production-process wording with a useful observation of the actual work markers, movement and terrain changes. All original explanations remain intact.'}
];
const englishTitles=['Read Pointing, Selection and Work Separately','Resource Warnings and the Next Action','Selection State and Confirmation Conventions','Changes After Confirmation','Planned Work and Actual Progress','Responses for the Current Tool'];
const generator=path.join(__dirname,'prepare-additions-v2.cjs');let code=fs.readFileSync(generator,'utf8');
for(const language of ['ko','en']){
  const file=path.join(work,`additions.${language}.json`),script=JSON.parse(fs.readFileSync(file,'utf8'));
  for(const c of changes){const scene=script.scenes.find(s=>s.id===c.scene);code=code.replace(scene.lines[c.line],c[language]);scene.lines[c.line]=c[language];}
  if(language==='en')script.scenes.forEach((s,i)=>s.title=englishTitles[i]);
  fs.writeFileSync(file,JSON.stringify(script,null,2)+'\n');
}
fs.writeFileSync(generator,code);
fs.writeFileSync(path.join(work,'addition-repair-decision.json'),JSON.stringify({recordedAt:new Date().toISOString(),firstPassAllSixRead:true,rejectedScenes:['02'],editorialRefreshScenes:['05'],changes,next:'Force02,05 once in the same approved voice; CPU ASR all current hashes; no full TTS regeneration.',humanListening:'pending'},null,2)+'\n');
console.log('Only new02/05 wording changed; original PPT and narration untouched.');
