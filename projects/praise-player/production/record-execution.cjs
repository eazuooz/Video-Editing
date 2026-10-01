const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),file=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const q=JSON.parse(fs.readFileSync(file,'utf8')),v=q.items.find(x=>x.slug==='praise-player');
const processText=execFileSync('powershell',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'praise-player' -and $_.Name -match 'python|powershell' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Depth 3"],{windowsHide:true,encoding:'utf8'});
const found=processText.trim()?JSON.parse(processText):[];v.activeExecution={...(v.activeExecution||{}),tts:{sessionId:16168,state:'running-single-approved-voice-synthesis',log:'projects/praise-player/production/tts-v1.log',processes:Array.isArray(found)?found:[found],command:'scripts/build-project-narration.ps1 -Project praise-player -SkipAsr'}};
v.stage='single-narration-synthesis-and-new-visuals';v.nextAction='Resume live narration once; create and verify five new keyboard/collision comparisons and six original white 2.5D scenes. ASR/render/collection/upload remain pending.';
v.freshGameReview={titles:['Nintendo Switch Sports','Ring Fit Adventure'],manifest:'projects/praise-player/sources/game-candidates.json',rejected:['Devil May Cry 5','Trackmania','Rocket League','Hades','Hi-Fi Rush']};
v.updatedAt=q.updatedAt=new Date().toISOString();fs.writeFileSync(file,JSON.stringify(q,null,2)+'\n');console.log(v.activeExecution.tts);
