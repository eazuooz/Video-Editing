// Direct comparison recorded after the completed one-paragraph candidate readback.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const state=read(base+'repair-phrases2.json');
if(state.status!=='candidates-ready-for-direct-review'||state.children.some(c=>c.exitCode!==0||c.status!=='finished'))throw Error('Repair2 not completed.');
const request=read(base+'repair2/request.json');for(const i of request.inputs)if(hash(i.path)!==i.sha256)throw Error('Frozen input mismatch '+i.path);
const dir='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair2/';
const report=read(dir+'motion-sickness-games-phrase-repair2.asr-review.json'),r=report.scenes[0];
if(!report.complete||report.sceneCount!==1||r.scene!=='05')throw Error('Unexpected candidate report.');
const wav=dir+'chunks/05-scene.wav',asr=dir+'asr/05.json',a=read(asr);
if(hash(wav)!==r.audio_sha256||a.audio_sha256!==r.audio_sha256)throw Error('Current hash not reviewed.');
const expected='이어지는 다른 면에서는 노즐이 기둥과 그 옆의 넓은 면을 따라 움직입니다. 먼저 자리를 잡는 구간과, 같은 방향을 바라보며 표면을 청소하는 구간을 구분해 보세요.';
const recognized=' 이어지는 다른 면에서는 노즐이 기둥과 그 옆의 넓은 면을 따라 움직입니다. 먼저 자리를 잡는 구간과 같은 방향을 바라보며 표면을 청소하는 구간을 구분해보세요.';
if(r.expected!==expected||r.recognized!==recognized)throw Error('Candidate text changed since direct review.');
const review={reviewedAt:new Date().toISOString(),status:'one-candidate-direct-content-readback-pass',candidateOnly:true,automaticallyApproved:false,wholeCompositeApproval:false,humanListening:'pending',scenes:[{scene:'05',decision:'content-readback-pass',audio:wav,audio_sha256:r.audio_sha256,asr,asr_sha256:hash(asr),expected:r.expected,recognized:r.recognized,acousticChecks:r.acousticChecks,allSentencesDirectlyCompared:true,
 reason:'Both sentences directly compared: posts/broad adjacent surfaces, taking a position, maintaining a viewing direction, cleaning and distinguishing intervals are complete. No additional syllable, omission, repetition or changed object. Final 구분해보세요 is recognized at9.72–10.56s in10.64s WAV. Prior ambiguous 판자 noun removed in this approved bilingual rephrasing; acoustic ending evidence is supplemental, not the sole approval.',lastWords:a.words.slice(-7),humanListening:'pending'}]};
const dest=path.join(root,base,'repair2/direct-review.json');if(fs.existsSync(dest))throw Error('Review already recorded; inspect rather than replace.');
fs.writeFileSync(dest,JSON.stringify(review,null,2)+'\n');
const qpath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=JSON.parse(fs.readFileSync(qpath,'utf8')),i=q.items.find(i=>i.slug==='motion-sickness-games');
i.execution.repair2={...i.execution.repair2,...state,alive:false,toolSessionId:27584,exitCode:0,doNotRestart:true,contentReview:base+'repair2/direct-review.json',acceptedCandidates:1};i.execution.alive=false;i.execution.status='repair2-candidate-readback-accepted-awaiting-composition';i.execution.activeTasks=[];i.execution.workerPid=null;i.nextAction='Compose separate v2 once from six retained repair1 candidates and accepted repair2 05; preserve original53 paragraphs/PCM and explanation duration. Then complete current-hash12-scene ASR and direct comparison before voice/timing approval.';i.updatedAt=q.updatedAt=review.reviewedAt;
fs.writeFileSync(qpath,JSON.stringify(q,null,2)+'\n');console.log('New05 candidate directly accepted; final composite ASR remains required.');
