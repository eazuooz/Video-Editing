const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-reward-planning/',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),write=(p,j)=>fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const qa=read(base+'production/final-v1/qa.json'),r=read(base+'production/final-v1/render-result.json'),m=read(base+'project.json');
if(!qa.technicalApproved||!qa.allRenderedCaptionPixelsReviewed||!qa.allCurrentFinalMixAsrDirectlyCompared)throw Error('Final gates incomplete');
for(const [kind,key] of [['clean','videoClean'],['captioned','videoBurnedCaptions']]){
 if(hash(r[kind])!==qa[kind+'Sha256'])throw Error('Current video changed');
 if(process.argv.includes('--finish-editor-flags')){if(hash(m.paths[key])!==qa[kind+'Sha256'])throw Error('Already promoted final differs');continue;}
 const dest=path.join(root,m.paths[key]);fs.mkdirSync(path.dirname(dest),{recursive:true});
 if(fs.existsSync(dest))throw Error('Preserve an existing final before promotion');
 fs.copyFileSync(path.join(root,r[kind]),dest,fs.constants.COPYFILE_EXCL);if(hash(m.paths[key])!==qa[kind+'Sha256'])throw Error('Promotion hash mismatch');
}
m.status='rendered-technically-reviewed-awaiting-private-delivery';m.membershipOutro.appliedToFinal=true;m.paths.captionAlignmentReview=base+'production/measured-edit-v3/caption-alignment-review.json';
m.editing.timingStatus='exact26693-frames-within-one-frame-ratio; all268-fixed-caption-pixels-reviewed';m.editing.exampleInterleaving.reviewStatus='67-existing-game-cuts-and-all-rendered-caption-intersections-directly-reviewed';m.audio.mixStatus='current-final-mix-all13-chapters-and11-contexts-directly-reviewed';
m.finalRender={technicalApproved:true,qa:base+'production/final-v1/qa.json',frames:26693,durationSeconds:26693/60,openItems:['사람 전체 청취·발음 승인 pending: 길/기, 발사 뒤/발사디, 컬트 표기 차이의 실제 발음 확인.','최종 공개 권리·원래 Nimbus 파일·잘린 회원 핸들·외부 백업 pending.','플랫폼 자동 더빙 미검수. 비공개 고정댓글은 공개 후 게시·고정 pending.']};
write(base+'project.json',m);const editorPlan='motion-canvas/src/projects/game-reward-planning/production-plan.json';const p=read(editorPlan);p.captionReviewComplete=true;p.finalVideoApproved=true;p.finalVideoApprovalScope='technical only; human listening/pronunciation/public rights pending';write(editorPlan,p);
console.log(JSON.stringify({promoted:true,frames:26693,publishReady:false}));
