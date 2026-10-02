const fs=require('node:fs');
const b='projects/picking-sides/',p=b+'production/';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const at=new Date().toISOString();
const initial=read(p+'asr-direct-review-initial.json'),report=read('shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1/picking-sides-qwen3-1.7b-balanced-v1.asr-review.json');
write(p+'voice-approval.json',{reviewedAt:at,allCurrentScenesTechnicallyReviewed:false,kind:'partial-scene-content-readback-review-not-final-mix-approval',humanListening:'pending',scenes:report.scenes.map(s=>({id:s.scene,decision:s.scene==='09'?'rejected-awaiting-repair09b':'content-readback-pass',audioSha256:s.audio_sha256,wav:`shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1/chunks/${s.scene}-scene.wav`,approvedAsr:`shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1/asr/${s.scene}.json`,reason:s.scene==='09'?'Unscripted 다음 영상에서 만나요 and ambiguous 발밑의 pronunciation. Latest source-aligned script requires another take.':s.scene==='03'?'Current repaired seven-paragraph ASR recovered; 잎/입 and 세/새 are homophones.':initial.scenes.find(x=>x.scene===s.scene).notes,acousticChecks:s.acousticChecks})),pending:['09 current-script full ASR without invented words','All current-hash final full-mix ASR','Human listening']});
write(p+'lookdev-review/review.json',{reviewedAt:at,kind:'silent-explanation-lookdev-only',video:'shared/output/motion-canvas/picking-sides-lookdev-v1.mp4',frames:1440,fps:30,seconds:48,directlyViewedContactPages:[1,2,3],directlyViewedSamples:18,scenes:['02','04','06','08','10','12'],findings:'All six layouts inspected at first/middle/end: white depth cards, contrasting identities, connection arrows and focus frame readable without overlap; content leaves bottom-center caption strip free.',finalNarratedRender:false,finalCueReview:false,pending:['Full-duration narration timing','Every final cut/cue','Membership ending','Final audio/video QA']});
let thumb=read(b+'publishing/thumbnail-recipe.json');
thumb.visualReview={status:'direct-local-image-review-passed',at,notes:'Yellow strip, white ground, large Korean black title, original cats and actual game crop directly inspected; no text/identity overlap observed. Platform preview/upload pending.'};thumb.uploaded=false;write(b+'publishing/thumbnail-recipe.json',thumb);
for(const [id,notes] of [['identity-reacquire','Four samples inspected: Star name/emblem follows body through jumps and moving scenery; original world remains above fixed caption area.'],['choice-timed','Six samples inspected around both selection events: Leaf17.8 and Moon26.8 change marker/camera while racers continue. No result card at42.3.']]){
 let q=read(p+`source-qa/${id}-qa.json`);q.review='direct-source-sample-review-passed';q.reviewedAt=at;q.findings=notes;q.finalCueReview=false;write(p+`source-qa/${id}-qa.json`,q);
}
const findings={
 'crop-review':{
  identity:'Three samples candidate-safe; all final frames pending.',
  'space-a':'Target near lower safe limit; needs all final cues.',
  'space-b':'Stationary rabbit observed; change narrated target to horned sheep.',
  'space-c':'Rejected black borders; superseded by v2.',
  'space-d':'Rejected373.85 scorecard; superseded by v3 crop/out373.1.',
  'space-e':'Rejected left black bar; superseded by v2.',
  'space-f':'Rejected403.85 next level/low target; superseded by v3.',
  choice:'Rejected uncut4–26:15s body/scaffold under fixed captions; split v2 windows.',
  grip:'Three grip/body samples visible above fixed captions; final cut QA pending.',
  framing:'54s landing aftermath; no static-ground padding.55–63 reviewed separately.',
  outcome:'Red fall visible; yellow near lower edge117.65; verify every final cue.',
  'alpha-a':'Three sampled jumps/landings readable; retain right control UI.',
  'alpha-b':'Three samples readable; no scorecard.',
  'alpha-c':'Three samples readable; stop before62 scorecard.',
  'alpha-d':'Three samples readable; stop before79 scorecard.'
 },
 'crop-review-v2':{
  'space-c':'Black borders removed at three samples; sheep visible.',
  'space-d':'372.95 goal too close to subtitle box; superseded by v3.',
  'space-e':'Left border removed; horned sheep moves at three samples.',
  'space-f':'403.0 low target; superseded by v3.',
  'choice-a':'Three samples clear above captions; excludes15s occlusion.',
  'choice-b':'Three action samples clear; separate source attempt.',
  'choice-c':'Three grip/body samples clear; separate source attempt.',
  'outcome-a':'Grip, collapse and new attempt; not one continuous match.',
  'outcome-b':'Grip and descent visible; no whole-match winner inference.'
 },
 'crop-review-v3':{
  'space-d':'Scorecard excluded; goal/target above caption zone in three samples.',
  'space-f':'Next level excluded; horned sheep clear in three samples; lower rabbit is not target.',
  'identity-extension':'Rejected as actual quota:67–70 is lobby/level-selection area.',
  'flight-extension':'Sheep at left edge in first sample; wider crop or exclusion needs final review.'
 }
};
for(const [dir,notes] of Object.entries(findings)){
 let q=read(p+dir+'/recipes.json');q.reviewedAt=at;q.directlyViewedSamples=q.recipes.length*3;q.finalCueReview=false;
 for(const r of q.recipes){r.review='directly-inspected-see-findings';r.findings=notes[r.id]||'Pending';}
 write(p+dir+'/recipes.json',q);
}
let src=read(p+'script-source-review.json');
Object.assign(src,{updatedAt:at,status:'partial-asr-reviewed-scene09-repair-and-measured-editorial-pending',ttsStarted:true,narrationTechnicalReview:'11 scenes content-readback pass;09 current-script repair pending. Full mix not assembled.',editNotes:b+'planning/measured-edit-notes.md',lookdevReview:p+'lookdev-review/review.json',thumbnailReview:b+'publishing/thumbnail-recipe.json',finalRender:false});write(p+'script-source-review.json',src);
let plan=read(b+'planning/action-map.json');Object.assign(plan,{resumeNotes:b+'planning/measured-edit-notes.md',finalTimingApproved:false,updatedAt:at});
Object.assign(plan.chapters.find(c=>c.scene==='09'),{rejectedTarget:'Hat-wearing rabbit: stationary/dead in several samples',correctedTarget:'Horned sheep (Ram), moving between rocks and goal',review:'See crop-review-v2/v3 and current narration repair09b; final cuts/captions pending.'});write(b+'planning/action-map.json',plan);
let q=read('production/batches/sakurai-planning-game-design/queue.json'),i=q.items.find(x=>x.slug==='picking-sides');
i.updatedAt=at;Object.assign(i.checkpoints,{script:true,narration:false,scenes:false,finalRender:false});
i.execution={...i.execution,toolSessionId:81811,resourceHistory:[{session:23250,pid:60160,state:p+'resource-runner.json',status:'finished'},{session:84461,pid:59480,state:p+'repair-runner.json',status:'finished'}],sourceAdditional:[{session:34829,pid:26816,state:p+'race-identity-checkpoint.json',status:'finished-source-reviewed'},{session:36014,state:p+'race-choice-timed-checkpoint.json',status:'finished-source-reviewed'}],previewServer:{session:79128,pid:56476,port:9212,url:'http://127.0.0.1:9212/picking-sides-render.html',config:'motion-canvas/vite.picking-sides.config.ts'},lookdev:{status:'finished-silent-only',renderResult:p+'lookdev-render-result.json',visualReview:p+'lookdev-review/review.json',samples:18},voiceReview:p+'voice-approval.json',resumeNotes:b+'planning/measured-edit-notes.md'};
i.nextAction='Resume alive repair09b runner60972/session81811 after other project synthesis finishes; do not duplicate GPU work. Reject old09 signoff take. Review new09 ASR, then word-align mixed ACT/EX timeline and60:40 with six explanations preserved. Final render/QA/private upload/Git pending.';
write('production/batches/sakurai-planning-game-design/queue.json',q);
const readme='production/batches/sakurai-planning-game-design/README.md';let t=fs.readFileSync(readme,'utf8');
const marker='**아직 TTS·최종12개 Motion Canvas 씬',k=t.indexOf(marker);if(k<0)throw Error('Checkpoint marker missing');
t=t.slice(0,k)+`**2026-10-02 22시대 갱신:** 최초12장72문단 단일TTS/CPU-ASR는 종료됐고 전체 대사를 직접 대조했다. 03을 고쳐 재합성한 현재64.16초 음성은 통과했다. 09는 실제로 움직이는 뿔 있는 양으로 대상을 바꿨지만 첫 수정본에 대본에 없는 ‘다음 영상에서 만나요’가 붙어 거부했다. 현재 repair09b-runner 단일 세션81811/PID60972가 다른 프로젝트 합성이 끝날 때까지 기다린 뒤09만 같은 승인 목소리로 합성/CPU-ASR한다. 실제 상태는 queue/repair09b-runner.json을 우선하고 종료된23250/84461을 기다리지 않는다.\n\n12개 독립MC씬 진입점을 작성했고 여섯 설명의48초 무음 룩데브를 실제 렌더해18화면을 직접 확인했다. 최종 영상은 아니다. 새 썸네일도 로컬 직접 검수를 마쳤다. 원본 게임의 검은 여백·점수표·자막 충돌을 사전 크롭84화면에서 검토하고 수정/제외 근거를 남겼다. 대사 시점에 맞는 identity-reacquire32초와 choice-timed42.5초를 추가 렌더해 전체 디코딩과4/6화면을 검수했다. 기존8개 소스는 보존했다.\n\n**최종 실측 타임라인·12장 최종 영상·전체 자막/음성QA·수집·업로드·커밋은 미완료다.** 출처 인아웃, ASR 경계, EX/ACT 분류와 다음 작업은 projects/picking-sides/planning/measured-edit-notes.md에 있다. 새 Vite는9212/PID56476/세션79128이며 살아 있으면 재사용한다. 다른 사용자 blank-project-coding 복원/TTS/변경을 중단하거나 커밋하지 않는다.\n`;
fs.writeFileSync(readme,t);
console.log('Saved factual partial checkpoint. No final render/upload/commit completion claimed.');
