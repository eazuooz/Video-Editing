const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{makeCuesGlobal,norm}=require('./caption-phrases-v2.cjs');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const slug='game-lighting-history-03',rel='production/research/game-lighting-history/local/episode03-spatial-rehearsal-v3',dst='motion-canvas/src/projects/game-lighting-history-03/spatial';
if(fs.existsSync(path.join(root,rel,'plan.json')))throw Error('Existing complete rehearsal plan preserved');
const project=read(`projects/${slug}/project.json`),audio=project.productionState.generatedNarration;
if(sha(audio.path)!==audio.sha256||sha(audio.timing.path)!==audio.timing.sha256)throw Error('Current audio/timing changed');
const old=read('production/research/game-lighting-history/local/spatial-narrated-rehearsal-v2/plan.json');
const foundation=read('motion-canvas/src/projects/game-lighting-history-03/spatial/foundation-proof-data-v1.json');
const reviewed='projects/game-lighting-history-03/production/foundation-current-model-review-v4.json';
if(!read(reviewed).modelMotionProofReviewed)throw Error('Foundation models unreviewed');
const moves={overview:[[3.30,16.54]],'12a':[[8.34,14.10],[18.06,20.68],[30.74,33.68],[43.06,48.28],[58.28,63.16],[72.28,74.48],[79.86,83.98],[95.08,98.30]],'13b':[[3.94,9.02],[14.26,20.18],[33.22,36.46],[45.18,48.66],[53.42,57.56],[68.88,72.28]],'14a':[[2.82,5.72],[18.74,23.66],[33.40,36.98],[47.48,50.80],[61.80,65.66],[73.76,77.16]],'14b':[[1.94,8.24],[20.20,25.04],[26.10,30.30],[39.78,43.14],[51.54,55.68],[62.82,68.02],[76.50,79.74]],'16aa':[[5.20,7.28],[16.12,21.00],[26.66,30.72],[39.56,42.80],[56.64,61.78],[70.76,74.76]],'16ab':[[9.56,13.38],[16.46,19.86],[27.84,32.94],[44.68,46.24],[58.26,62.84],[66.12,69.98]],conclusion:[[8.92,15.30],[15.56,20.56],[30.94,35.50]]};
const workTitles={'16aa':['시야 밖과 가림의 구별','시야 안에 있지만 벽 뒤에 가림','가능한 얼리 깊이 검사','보수적인 계층 깊이 요약','현재 가림과 과거 깊이','레이 질의와 렌더 제출'],'16ab':['메시 묶음의 처리','셰이딩 빈도와 픽셀 수','2×2 평가 공유','가상 페이지와 상주 메모리','수요 피드백과 데이터 도착','서로 다른 작업 자원']};
const modelNames={overview:'navigation','12a':'representation','13b':'dynamicRay','14a':'sampling','14b':'temporal','16aa':'culling','16ab':'pipeline',conclusion:'navigation'};
const rehearsedTitles=JSON.parse(fs.readFileSync(path.join(root,dst,'narrated-runtime-v2.tsx'),'utf8').match(/const titles=([\s\S]*?);\nconst topics/)[1].replaceAll("'",'"'));
const order=['overview','12a','13a','13b','14a','14b','15a','15b','16aa','16ab','16a','17a','17b','conclusion'],chapters=[];
for(const scene of order){
 const asrPath=`projects/${slug}/production/local/voice-asr-v2/whole-${scene}.json`,r=read(asrPath);
 if(r.audioSha256!==audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('Unexpected recognizer evidence');
 let chapter=old.chapters.find(c=>c.scene===scene);
 if(chapter){chapter=JSON.parse(JSON.stringify(chapter));chapter.titles=rehearsedTitles[old.chapters.findIndex(c=>c.scene===scene)];}
 else{
  const cues=makeCuesGlobal(r),paragraphs=r.expectedKo.map((originalKo,index)=>{
   const f=foundation.find(p=>p.scene===scene&&p.paragraph===index+1),mode=f?.mode??index;
   return {index,originalKo,from:index===0?0:cues.find(c=>c.paragraph===index).from,to:index===r.expectedKo.length-1?r.sourceToSeconds-r.sourceFromSeconds:cues.find(c=>c.paragraph===index+1).from,pair:[mode*2,mode*2+1],move:moves[scene][index],asrWordMotionAnchorsDirectlyRead:true};
  });
  chapter={scene,model:modelNames[scene],sourceFrom:r.sourceFromSeconds,sourceTo:r.sourceToSeconds,duration:r.sourceToSeconds-r.sourceFromSeconds,wholeAsr:{path:asrPath,sha256:sha(asrPath)},paragraphs,cues,titles:r.expectedKo.map((_,i)=>foundation.find(p=>p.scene===scene&&p.paragraph===i+1)?.title??workTitles[scene][i]),proofRecord:scene==='16aa'?`projects/${slug}/production/culling-fix-animated-proof-review-v2.json`:scene==='16ab'?`projects/${slug}/production/culling-pipeline-animated-proof-review-v1.json`:reviewed};
 }
 if(norm(chapter.cues.map(c=>c.text).join(' '))!==norm(r.expectedKo.join(' ')))throw Error('Caption words changed');
 chapter.timelineFrom=r.sourceFromSeconds;chapter.directTimingNotes=[];
 for(let i=1;i<chapter.cues.length;i++){
  const prev=chapter.cues[i-1],cur=chapter.cues[i];if(prev.to>cur.from){
   const boundary=(prev.to+cur.from)/2;
   if(boundary<=prev.from||boundary>=cur.to)throw Error('ASR overlap cannot be reconciled');
   chapter.directTimingNotes.push({scope:'caption-display-only',previousCue:prev.id,nextCue:cur.id,asrObservedPreviousEnd:prev.to,asrObservedNextStart:cur.from,displayBoundary:boundary,reason:'Small nonmonotonic ASR word boundary; split display at midpoint, preserve PCM and raw recognition. Full boundary pixels and human timing remain pending.'});
   prev.to=boundary;cur.from=boundary;
  }
 }
 for(let i=0;i<chapter.paragraphs.length;i++){const p=chapter.paragraphs[i];p.from=i===0?0:chapter.cues.find(c=>c.paragraph===i).from;p.to=i===chapter.paragraphs.length-1?chapter.duration:chapter.cues.find(c=>c.paragraph===i+1).from;
  if(p.move[0]<p.from-.01||p.move[1]>p.to+.15)throw Error(`Movement outside paragraph ${scene}/${i}`);
  if(p.move[1]>p.to){chapter.directTimingNotes.push({scope:'motion-end-only',paragraph:i+1,prior:p.move[1],current:p.to,reason:'Use reconciled display paragraph boundary, unchanged current PCM.'});p.move[1]=p.to;}
 }
 if(scene==='13a')chapter.paragraphs[0].earlyRay={from:3.06,to:7.84,anchor:'여기서 오 는 시작점이고 디 는 방향입니다. 티 를 바꾸면 레이 위의 점이 움직입니다.',independentOfBox:true};
 chapters.push(chapter);
}
for(let i=0;i<chapters.length;i++)chapters[i].sequenceDuration=(chapters[i+1]?.timelineFrom??audio.durationSeconds)-chapters[i].timelineFrom;
const inputPaths=[audio.path,audio.timing.path,`projects/${slug}/script/narration.ko.json`,`projects/${slug}/script/narration.en.json`,`${dst}/foundation-models-v4.tsx`,`${dst}/bvh-model-v1.tsx`,`${dst}/ddgi-model-v1.tsx`,`${dst}/restir-model-v1.tsx`,`${dst}/nanite-model-v1.tsx`,`${dst}/lumen-model-v1.tsx`,`${dst}/cache-model-v1.tsx`,`${dst}/culling-model-v2.tsx`,`${dst}/pipeline-model-v1.tsx`];
const plan={createdAt:new Date().toISOString(),scope:'All14 independent black2.5D explanation chapter rehearsals with all84 original paragraph pairs and unchanged1086.400s PCM, including original scene gaps. No gameplay allocation, Nimbus/final mix, intro/member ending, final narration listening or full episode approval.',slug,style:'research-black-v1',audio,chapters,duration:audio.durationSeconds,frames:Math.round(audio.durationSeconds*60),inputs:inputPaths.map(path=>({path,sha256:sha(path)})),currentNarrationApproved:false,humanWholeListeningApproved:false,allCaptionBoundaryPixelsReviewed:false,allRehearsalPixelsReviewed:false,finalVideoApproved:false,localOnly:true};
fs.mkdirSync(path.join(root,rel),{recursive:true});fs.writeFileSync(path.join(root,rel,'plan.json'),JSON.stringify(plan,null,2)+'\n');fs.writeFileSync(path.join(root,dst,'narrated-data-v3.json'),JSON.stringify(plan,null,2)+'\n');
const names=[];for(let i=0;i<chapters.length;i++){const name=`narrated-${chapters[i].scene}-v3`;names.push(name);fs.writeFileSync(path.join(root,dst,name+'.tsx'),`import {narratedChapterV3} from './narrated-runtime-v3';\nexport default narratedChapterV3(${i});\n`);fs.writeFileSync(path.join(root,dst,name+'.meta'),JSON.stringify({version:0,timeEvents:[],seed:2838358939},null,2)+'\n');}
fs.writeFileSync(path.join(root,dst,'narrated-project-v3.ts'),`import {makeProject} from '@motion-canvas/core';\n${names.map((n,i)=>`import p${i} from './${n}?scene';`).join('\n')}\nexport default makeProject({scenes:[${names.map((_,i)=>`p${i}`).join(',')}],audio:'/@fs/D:/Github/Video-Editing/${audio.path}'});\n`);fs.copyFileSync(path.join(root,dst,'narrated-project-v2.meta'),path.join(root,dst,'narrated-project-v3.meta'));
console.log(JSON.stringify({plan:rel+'/plan.json',chapters:chapters.length,paragraphs:chapters.reduce((n,c)=>n+c.paragraphs.length,0),cues:chapters.reduce((n,c)=>n+c.cues.length,0),duration:plan.duration,displayOnlyOverlapCorrections:chapters.reduce((n,c)=>n+c.directTimingNotes.length,0),audioByteIdentical:true,finalVideoApproved:false}));
