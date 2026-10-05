// Record reviewed code only. Measured timing, diagram/caption pixels and full ASR remain separate gates.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug='making-game-sequels';
const proof='production/batches/sakurai-planning-game-design/proof-making-game-sequels/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const save=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const now=new Date().toISOString(),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const sourceReview=read(`projects/${slug}/production/script-source-review.json`);
for(const input of sourceReview.inputs)if(sha(input.path)!==input.sha256)throw Error('Locked reviewed input changed: '+input.path);
const command=['node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.making-game-sequels.json'];
const result=cp.spawnSync(process.execPath,command,{cwd:path.join(root,'motion-canvas'),encoding:'utf8',windowsHide:true});
if(result.status!==0)throw Error(result.stdout+result.stderr);
const base=`motion-canvas/src/projects/${slug}/`,plan=read(base+'scene-plan.json');
const code=[base+'project.ts',base+'scene-factory.tsx',base+'scene-plan.json',...plan.scenes.map(s=>base+'scenes/scene'+s.id+'.tsx'),'motion-canvas/tsconfig.making-game-sequels.json'];
const record={schemaVersion:1,reviewedAt:now,sceneCount:12,independentEntrypoints:plan.scenes.map(s=>s.id),
  code:code.map(p=>({path:p,sha256:sha(p)})),typeScript:{command:'node '+command.join(' '),exitCode:result.status,output:(result.stdout+result.stderr).trim()},
  rolePlan:plan.scenes.map(s=>({id:s.id,role:s.role,title:s.title,diagram:s.diagram})),
  overviewIndependentSceneCreated:true,whiteComparisonsArrowsAndDepthAuthored:true,
  actualGameplaySubstitution:false,sourceAudioGate:'Each compiled segment must have sourceAudioStreams=0 before playback.',
  historicalTypeError:{diagnostic:'Lookdev union lacked mediaUrl; unsupported VideoProps.volume.',resolved:true,repair:'Typed Segment array and zero-source-audio-stream gate matching installed Video API.'},
  finalTimingApproved:false,allFinalCaptionPixelsReviewed:false,allSourceSegmentPixelsReviewed:false,diagramPixelsReviewed:false,
  finalVideoComplete:false,newGitImages:0,mediaCommitted:false,
  nextAction:'After current CPU measurement completes, inspect full current-hash ASR and exact native word/cut placement; review white diagrams and all fixed-caption pixels before final measured60:40.'};
save(`projects/${slug}/production/independent-code-review.json`,record);
const manifest=read(`projects/${slug}/project.json`);
manifest.status='reviewed-bilingual-text-and-independent-code-CPU-voice-measuring';
manifest.editing.openingOverview.independentMotionCanvasSceneCreated=true;
manifest.editing.independentMotionCanvasSceneCount=12;
manifest.editing.motionCanvasCodeReview=`projects/${slug}/production/independent-code-review.json`;
manifest.editing.finalDiagramPixelsReviewed=false;
manifest.audio.mixStatus='Approved Nimbus retained; CPU narration measurement running, full ASR and final mix pending.';
save(`projects/${slug}/project.json`,manifest);
const git=read(proof+'source-bank-progress-git-verification.json');
const queuePath='production/batches/sakurai-planning-game-design/queue.json',queue=read(queuePath);
const item=queue.items.find(x=>x.slug===slug);
item.sourceProgressGit={status:'pushed-progress-not-completed-video',productionCommit:git.progressCommit,latestVerification:git,record:proof+'source-bank-progress-git-verification.json'};
item.independentCodeReview={path:`projects/${slug}/production/independent-code-review.json`,sceneCount:12,typeScriptPassed:true,pixelsReviewed:false,finalTimingApproved:false};
item.execution.newSceneCreated=true;
item.updatedAt=now;save(queuePath,queue);
for(const p of [`projects/${slug}/production/latest-checkpoint.json`,proof+'latest-checkpoint.json']){
 const c=read(p);c.motionCanvasCreated=true;c.independentCodeReview=item.independentCodeReview;c.sourceProgressGit=item.sourceProgressGit;c.updatedAt=now;save(p,c);
}
const readme='production/batches/sakurai-planning-game-design/README.md',old=fs.readFileSync(path.join(root,readme),'utf8');
const heading='2026-10-05 현재:11완료본·중복제외1편과 남은12편을 보존한다. making-game-sequels의 current distinct 뒤 공식 OMD2/3/Deathtrap native자료를 먼저 직접읽고 독립12장48KOEN문단·전체안내 도입의 약속을 직접대조했다. OMD2 교정16구성샘플4판에서 하단hotbar 제외와 남은 실제관찰/UI 한계를 기록했다.12독립MC/여섯흰2.5D비교 코드는 TypeScript를 통과했지만 최종도식·고정자막픽셀/타이밍 승인 전에는 최종factory가 실행을 거부한다. 승인Qwen/reference로 단일CPU12장 측정이 진행 중이며 전체ASR/믹스/최종60:40/렌더QA/수집/새비공개 전달은 미완료다. 실제 상태·PID·세션은 프로젝트 narration-tts-execution.json과 최신queue를 우선한다. source진행42ec5c3b79ca7cd14c7473d5a7cac7cefec4e4ff는 origin/main 일반푸시/실제원격일치이며 새이미지·미디어0이다. 완성영상이나 종료작업을 반복하지 않고 다른GPU학습/공유변경을 보존한다. 아래는 이전 이력이다.';
fs.writeFileSync(path.join(root,readme),old.replace(/^# 기획·게임 디자인 영상 일괄 제작\r?\n/, '# 기획·게임 디자인 영상 일괄 제작\n\n'+heading+'\n'));
console.log(JSON.stringify({scenes:12,typeScriptExitCode:0,finalPixelsReviewed:false,sourceProgressSha:git.progressCommit,voiceJob:'CPU measurement remains active; no extra production worker started'}));
