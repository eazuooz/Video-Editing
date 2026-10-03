const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games',dir=path.join(__dirname,'final-v1');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8'));
const write=(p,v)=>fs.writeFileSync(path.resolve(root,p),JSON.stringify(v,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const qa=read(`${base}/production/final-v1/qa.json`),plan=read(`${base}/production/final-v1/plan.json`);
const source=read(`${base}/production/final-v1/final-source-cut-review.json`),encoded=read(`${base}/production/final-v1/encoded-boundary-review/direct-review.json`);
const mixedPath=`${base}/production/final-v1/mixed-asr/asr.json`,contextPath=`${base}/production/final-v1/mixed-context/asr.json`,beamPath=`${base}/production/final-v1/mixed-input-beam-context/asr.json`;
const mixed=read(mixedPath),context=read(contextPath),beam=read(beamPath),now=new Date().toISOString();
if(!source.approved||!encoded.approved||!mixed.complete||mixed.results.length!==12||!context.complete||!beam.complete)throw Error('Incomplete current source, encoded or full mixed readback evidence');
for(const r of [mixed,context,beam])if(sha(r.mix)!==r.mixSha256)throw Error('Mixed audio changed after readback');
if(!beam.results[0].text.includes('돌리는 입력'))throw Error('Input/control pronunciation still unresolved');
if(sha(`${base}/production/final-v1/captions.ko.ass`)!=='73b8b4d991d5c156115ec047845c8fec63a4dac1c2b0dafa08ce2ee1c8e3b0ad')throw Error('Reviewed caption instructions changed');
for(const group of [qa.captionImages,qa.compositionImages])for(const im of group.images)if(sha(im.path)!==im.sha256)throw Error('Reviewed pixel changed: '+im.path);
const pfile=`${base}/project.json`,p=read(pfile);
for(const key of ['videoClean','videoBurnedCaptions'])if(sha(p.paths[key])!==qa[key].sha256||!qa[key].fullDecodePassed||qa[key].frames!==37985)throw Error('Final media changed or decode incomplete');
if(new Set(Object.values(qa.sameCopiedAacAudio)).size!==1||qa.ratioErrorFrames!==0||!qa.identicalKoEnTiming)throw Error('Audio/timing/ratio failed');
if(Math.abs(Number(qa.mixMeasurement.input_i)+16)>0.5||Number(qa.mixMeasurement.input_tp)>-1.5)throw Error('Final AAC loudness/peak outside standard');
const mixedReview={kind:'direct-full12-current-mix-ASR-plus-independent-contexts',status:'technical-readback-passed',reviewedAt:now,sceneCount:12,paragraphCount:60,mixSha256:mixed.mixSha256,
 reports:[mixedPath,contextPath,`${base}/production/final-v1/mixed-input-context/asr.json`,beamPath].map(path=>({path,sha256:sha(path)})),
 notes:['All sixty requested paragraphs in twelve current mixed windows were read against the current script, including every closing sentence. No omitted paragraph, added greeting or sustained repetition was accepted.',
 '03 full-window 고정되는되는 is absent from independent current-mix paragraph readback, which reads 고정되는 once; raw report is preserved.',
 '04 greedy ASR repeatedly writes 인력; a separate unprompted beam5 decode of the current mixed sentence reads 시점을 돌리는 입력 exactly. Current v2 original PCM full readback also reads 입력. Human hearing remains pending.',
 '06 도시계 is the same /do.si.ge/ sound as 도식의 in this context. All words and meaning remain, and the current v2 original PCM full readback spells 도식의 correctly.',
 '07 independent current-mix paragraph readback reads 읽지는 마세요 correctly. Other 의/에 and 므로/음으로 spelling variants preserve the spoken meaning; source reports remain intact.'],humanListening:'pending',automaticallyApproved:false};
write(`${base}/production/final-v1/full-mix-asr-review.json`,mixedReview);
qa.fullMixAsrReview=mixedReview;qa.captionImages.review='all174-current-rendered-caption-and-cut-segments-directly-reviewed';qa.compositionImages.review='all20-current-intro-PPT-and-original-membership-compositions-directly-reviewed';
qa.directVisualReview={status:'passed',reviewedAt:now,cueAndCutSegments:174,compositionImages:20,encodedCutBoundaryImages:102,sourcePlanningImages:221,captionCenter:[960,970],
 pages:[...Array.from({length:15},(_,i)=>`${base}/production/final-v1/caption-cues-${String(i+1).padStart(2,'0')}.jpg`),...Array.from({length:2},(_,i)=>`${base}/production/final-v1/final-composition-${String(i+1).padStart(2,'0')}.jpg`)].map(path=>({path,sha256:sha(path)})),
 notes:['Every final subtitle/cut segment and composition was directly inspected on fifteen caption pages and two composition pages; native1920x1080 member020 was also inspected.',
 'Actual captions retain the same bottom-center anchor and shorter cues leave tool UI at left and stance UI at right visible. PPT captions stay below content and explanatory callouts.',
 'All actual examples are normal-speed existing-game actions; no agent-created demo, repeated interval, title/score/menu/snow/idle quota fill is used.',
 'Original member profiles, handles, badges, cat logo and exact requested title and canonical coaching URL are present. A truncated original handle remains pending rather than guessed.']};
qa.approvedAt=now;qa.technicalApproval=true;qa.humanListening='pending';qa.publicRights='pending';write(`${base}/production/final-v1/qa.json`,qa);
p.status='rendered-QA-passed-awaiting-private-upload';p.membershipOutro.appliedToFinal=true;
p.editing.exampleInterleaving.reviewStatus='34-existing-game-cuts-102-encoded-boundaries-and174-final-caption-segments-directly-reviewed';p.editing.timingStatus='final-render-and-technical-QA-passed';
p.audio.mixStatus='final-current-mix-ASR-and-AAC-technical-QA-passed-human-hearing-pending';p.tts.outputDir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v2';p.tts.filenameStem='motion-sickness-games-qwen3-1.7b-balanced-v2';
p.approvals.final='technical-render-QA-passed-human-listening-and-public-rights-pending';p.publishReady=false;
p.finalRender={revision:'final-v1',qa:`${base}/production/final-v1/qa.json`,durationSeconds:qa.totalSeconds,frames:37985,knownIssues:[],openItems:['사람 전체 청취·발음 최종 확인 대기','최종 공개용 게임 자료 이용 권리 확인 대기','Nimbus 원래 Audio Library 파일 확인 대기','잘린 회원 핸들 원본 확인 대기','외부 미디어 백업 대기']};write(pfile,p);
const mcpath='motion-canvas/src/projects/motion-sickness-games/production-plan.json',mc=read(mcpath);mc.captionReviewComplete=true;mc.finalTechnicalQa=`${base}/production/final-v1/qa.json`;write(mcpath,mc);
plan.captionReviewComplete=true;plan.finalTechnicalQa=`${base}/production/final-v1/qa.json`;write(`${base}/production/final-v1/plan.json`,plan);
console.log(JSON.stringify({status:p.status,frames:37985,seconds:qa.totalSeconds,cues:166,captionSegments:174,cuts:34,lufs:qa.mixMeasurement.input_i,truePeak:qa.mixMeasurement.input_tp,humanListening:'pending'}));
