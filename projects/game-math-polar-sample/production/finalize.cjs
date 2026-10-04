// Record the caller's completed pixel review; never infer human listening.
const fs=require('fs');const path=require('path');const crypto=require('crypto');
const root=path.resolve(__dirname,'../../..');const base=path.join(root,'projects/game-math-polar-sample');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));const write=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
if(!process.argv.includes('--visual-reviewed'))throw new Error('Run after directly reviewing the current caption strips and composition sheets.');
const qpath=path.join(base,'production/qa.json');const qa=read(qpath);const mf=path.join(base,'project.json');const m=read(mf);
if(!qa.fullDecodePassed||qa.captionCount!==43||qa.ratioErrorFrames!==0)throw new Error('Current sample QA is incomplete.');
for(const v of Object.values(qa.videos)){
  const actual=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,v.path))).digest('hex');
  if(actual!==v.sha256)throw new Error('Video changed after QA: '+v.path);
}
qa.directVisualReview={status:'passed',reviewedAt:new Date().toISOString(),captionCuesChecked:43,method:'Direct inspection of all43 caption midpoint crops,13 full compositions, and native-size cues030/037; original game intervals also inspected every2seconds before narration.',images:['caption-strips-01.jpg','caption-strips-02.jpg','composition-sheet-01.jpg','composition-sheet-02.jpg','composition-sheet-03.jpg','composition-sheet-04.jpg','cue-030.jpg','cue-037.jpg'],findings:'Caption boxes and hard shadows remain within1080p; every cue is bottom-center with at most2lines. Essential formulas and diagrams stay above captions. Boss viewport preserves action while removing bottom health/name HUD. Original member profile/name/badge screenshot remains visible. Genuine3D tilt and independent height are visible.'};
write(qpath,qa);
const cpath=path.join(base,'production/caption-layout.json');const c=read(cpath);c.pixelReview=qa.directVisualReview;write(cpath,c);
m.status='sample-ready-for-review';m.membershipOutro.appliedToFinal=true;
m.editing.exampleInterleaving.reviewStatus='passed-source-interval-and-action-to-explanation-review';
m.editing.timingStatus='final-render-verified-10800-frames';
m.editing.finalBodyFrames={total:qa.bodyFrames,actual:qa.actualFrames,explanation:qa.explanationFrames,ratioErrorFrames:0};
m.audio.mixStatus='rendered-measured-human-listening-pending';
m.audio.musicFallbackScenes=['02','04','06'];
m.delivery.qa='projects/game-math-polar-sample/production/qa.json';
m.paths.timeline='projects/game-math-polar-sample/production/timeline.json';
m.finalRender={status:'local-review-sample-rendered',durationSeconds:180,fps:60,qa:m.delivery.qa,openItems:['사람의 전체 청취 승인 대기','공개 전 게임IP와 Nimbus Audio Library 원본 취득 확인 대기','회원 원본의 잘린 표시명 확인 대기'],renderer:'Manim Community0.20.1/Cairo, FFmpeg composition'};
m.approvals.visualPixelReview='passed';m.approvals.humanListening='pending';m.publishReady=false;
write(mf,m);
const checklist=path.join(base,'checklist.md');let text=fs.readFileSync(checklist,'utf8');
for(const label of ['모든 자막43개 및 대표 장면 화면 픽셀 직접 검토','두 MP4 전체 디코딩'])text=text.replace('- [ ] '+label,'- [x] '+label);
fs.writeFileSync(checklist,text);
console.log('Current rendered sample pixel review recorded; human listening and publication review remain pending.');
