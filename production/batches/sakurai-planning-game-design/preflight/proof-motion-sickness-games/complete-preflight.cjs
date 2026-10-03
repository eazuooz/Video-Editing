const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../../../../');
const now = new Date().toISOString();
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const save = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
const proofPath = path.join(__dirname, 'content-review.json');
const proof = read(proofPath);
proof.status = 'distinct-content-and-studio-reviewed';
proof.completedAt = now;
proof.viewerQuestion = 'How can a developer separate necessary view movement from additional presentation motion and give players control over camera comfort?';
proof.boundaries = ['Do not retell FOV geometry or an FPS/rendering-pipeline lesson.', 'Do not teach SetTarget or camera coordinate conversion again.', 'Do not promise a medical outcome or repeat the reference video\'s medication advice.', 'Use observed existing-game actions, never a fabricated game or a symptom test.'];
proof.cameraUploadContentReview = [
  {videoId:'tmL7WV17r5g', method:'Full local CPU ASR text and timestamps read, plus actual watch-page code screenshot at 2:10.', focus:'SetTarget, mTarget Transform position, lookPosition fallback, keeping the cat target at screen centre; final Q&A and repository workflow.', difference:'Object-follow implementation is distinct from additional camera motion, separate aiming/view controls, stable references and optional comfort presentation.', asr:'tmL7WV17r5g.asr.json', screenshot:'watch-target-camera-content.png', limitation:'Automatic recognition has technical-term errors and silence hallucinations. This is a substantive topic comparison, not human listening or an exact transcript approval.'},
  {videoId:'upO4CW3INvE', method:'Full 31:26 timestamped Korean platform automatic transcript read, plus camera code/diagram observed at 26:00.', transcriptExport:'C:/Users/eazuo/AppData/Local/Temp/browser-use/exports/youtube-upO4CW3INvE-0a3fc023-1c3e-4dab-94c5-8e0eb98b3491.txt', intervals:[{start:0,end:1447,topic:'Sprite sheets, bone animation, animator switching, per-frame duration, alpha blending and component study.'},{start:1447,end:1712,topic:'2D camera coordinate subtraction, resolution-half origin adjustment, target look-position and if/else correction.'},{start:1712,end:1886,topic:'Sprite size/resource preparation and next lesson.'}], difference:'The camera section computes object screen coordinates and target following. It does not discuss head bob, motion settings or camera comfort.'},
  {videoId:'qfkL1VjnYo8', method:'Full 20:24 timestamped Korean platform automatic transcript read, plus actual depth/alpha rendering lesson screen observed at 10:00.', transcriptExport:'C:/Users/eazuo/AppData/Local/Temp/browser-use/exports/youtube-qfkL1VjnYo8-61b2011e-3bc2-4d3e-a604-8deb0bf44b2a.txt', intervals:[{start:0,end:156,topic:'Scene/Game/editor/UI cameras and separate views.'},{start:156,end:804,topic:'Camera-by-camera rendering, opaque/cutout/transparent grouping, ordering, blending and depth rules.'},{start:804,end:1224,topic:'Base renderer, external dependency source debugging/build setup and engine-learning scope.'}], difference:'Multiple rendering views and transparent-object sorting are engine implementation topics; they do not cover player camera-motion comfort.', screenshot:'watch-multiple-camera-content.png'}
];
for (const evidence of proof.cameraUploadContentReview) {
  if (evidence.transcriptExport) evidence.transcriptSha256 = crypto.createHash('sha256').update(fs.readFileSync(evidence.transcriptExport)).digest('hex');
  evidence.humanListeningCompleted = false;
}
proof.localReview.fullScriptsRead.push(
  {slug:'yamyam-dx12-frame-sync',chapters:10,comparison:'Full script: CPU/GPU submission, allocator reuse, fences, two slots and editor viewport lifetime; distinct from player motion comfort.'},
  {slug:'yamyam-dx12-texture-views',chapters:10,comparison:'Full script: camera RenderTargets, texture descriptors, per-draw matrices, ImGui panel composition and resizing; distinct from optional player view motion.'},
  {slug:'yamyam-dx12-pso-composition',chapters:10,comparison:'Full script: alpha modes, PSO selection, transparent order, display SRVs and lifetime; no motion-comfort chapter.'},
  {slug:'yamyam-dx12-rendering',chapters:8,comparison:'Full script: safe rendering submission, camera textures, material modes and display composition; no comfort settings or camera-motion question.'}
);
proof.researchProcess = {sessionId:5989,parentPid:59520,workerPid:23124,status:'stopped-own-redundant-cpu-research-after-full-platform-transcript-review',stoppedAt:now,completedAsr:['tmL7WV17r5g'],notAnAudioProductionFailure:true,otherUserProcessesStopped:false};
proof.pending = ['Review precise existing-game action intervals and source conditions before authoring narration.', 'Complete fresh game candidate selection; no final cut or ratio approval yet.'];
save(proofPath, proof);
const asrPath = path.join(__dirname, 'tmL7WV17r5g.asr.json');
const asr = read(asrPath); asr.manualContentReview = {status:'topic-content-reviewed',at:now,scope:'Duplicate review only',note:proof.cameraUploadContentReview[0].limitation,humanListeningCompleted:false}; save(asrPath,asr);
const reason = 'Distinct viewer question: camera-motion comfort and player control, rather than FOV visibility, FPS mechanics, sprite animation or camera/RenderTarget implementation. Read the full related local scripts and the substantive content of all three actual Studio camera matches. Targeting tmL7WV17r5g teaches SetTarget/lookPosition; upO4CW3INvE teaches sprite/2D coordinate conversion; qfkL1VjnYo8 teaches multiple camera views, alpha sorting and dependency debugging. No matching motion-comfort chapter was found. Details and explicit boundaries are in proof-motion-sickness-games/content-review.json. Do not repeat those existing lessons or make medical treatment claims.';
const studioEvidence = 'Actual Studio searches: 멀미 0; 카메라 3 IDs qfkL1VjnYo8/upO4CW3INvE/tmL7WV17r5g; 시야각 1 ID 84xPzR2ww88. Saved actual screenshots/state in proof-motion-sickness-games. Actual own watch pages inspected; full platform transcripts of upO4CW3INvE and qfkL1VjnYo8, full tmL7WV17r5g CPU ASR read. Source hashes, intervals, screenshots, limitations and topic comparison are recorded in content-review.json. Automatic text is not human listening.';
for (const args of [[ 'motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',studioEvidence ],['motion-sickness-games','--check']]) {
  const result = spawnSync(process.execPath, ['scripts/review-video-duplicates.cjs',...args],{cwd:root,encoding:'utf8'});
  process.stdout.write(result.stdout || ''); process.stderr.write(result.stderr || '');
  if (result.status !== 0) process.exit(result.status || 1);
}
const queuePath = path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const queue = read(queuePath); const item = queue.items.find(i=>i.slug==='motion-sickness-games');
item.stage = 'preflight-distinct-existing-game-source-research';
item.execution = {...item.execution,phase:item.stage,cpuContentAsr:proof.researchProcess,sessionId:null,pid:null,workerPid:null,noNewProject:true,noTts:true};
item.nextAction = 'Create project only after the current distinct check; review exact normal-speed PowerWash Simulator / other existing-game source actions and rights before drafting independent bilingual narration.';
queue.updatedAt = now; save(queuePath,queue);
