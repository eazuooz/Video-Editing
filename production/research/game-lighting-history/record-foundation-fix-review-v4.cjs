const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const extraction='production/research/game-lighting-history/local/foundation-fix-v4/qa/extraction.json',q=read(extraction);
if(q.frames.length!==3||q.boards.length!==1||q.wholeDecode.exitCode!==0)throw Error('Scoped extraction incomplete');
for(const f of[q.video,...q.modelInputs,...q.frames,...q.boards])if(sha(f.path)!==f.sha256)throw Error('Reviewed input changed: '+f.path);
q.boards[0].directlyViewed=true;
const record={reviewedAt:new Date().toISOString(),scope:'All three before/middle/after frames directly read on board01. White input labels are on their own front faces, separated vertically. Three differently colored arrows grow independently and converge on the reconstruction output. Top and side faces remain visible. This is one DLSS2 principle diagram, not a neural-network reproduction or final narration approval.',video:q.video,modelInputs:q.modelInputs,boards:q.boards,wholeDecodeExit:0,scopedPassed:[{scene:'14b',paragraph:1}],remainingDefects:[],modelMotionProofReviewed:true,narrationTimingApproved:false,fullEpisodeApproved:false,localOnlyImages:true};
q.directReview=record;q.modelMotionProofReviewed=true;
fs.writeFileSync(path.join(root,extraction),JSON.stringify(q,null,2)+'\n');
const review='projects/game-lighting-history-03/production/foundation-fix-animated-proof-review-v4.json';
fs.writeFileSync(path.join(root,review),JSON.stringify(record,null,2)+'\n');
const refs=['foundation-animated-proof-review-v1.json','foundation-fix-animated-proof-review-v2.json','foundation-fix-animated-proof-review-v3.json','foundation-fix-animated-proof-review-v4.json'].map(p=>'projects/game-lighting-history-03/production/'+p);
const baseline=read(refs[0]),data=read('motion-canvas/src/projects/game-lighting-history-03/spatial/foundation-proof-data-v1.json');
const keys=p=>p.scene+':'+p.paragraph,coverage=data.map(p=>({scene:p.scene,paragraph:p.paragraph,review:refs[0]}));
for(const p of baseline.blockingDefects){const item=coverage.find(c=>keys(c)===keys(p));if(!item)throw Error('Unknown defect');item.review=null;}
for(const ref of refs.slice(1))for(const p of read(ref).scopedPassed){const item=coverage.find(c=>keys(c)===keys(p));if(!item)throw Error('Unknown scoped correction');item.review=ref;}
if(coverage.length!==31||coverage.some(c=>!c.review))throw Error('Unreviewed paragraph');
const composite={reviewedAt:new Date().toISOString(),scope:'Thirty-one foundation paragraph models: twenty unchanged baseline paragraphs, nine v2 corrections, one BLAS sharing v3 correction and one DLSS2 v4 correction. Every selected model has direct before/middle/after pixel evidence. This closes scoped model layout/motion defects only; full narration-timed render and caption boundaries are still required.',references:refs.map(p=>({path:p,sha256:sha(p)})),coverage,currentModel:{path:'motion-canvas/src/projects/game-lighting-history-03/spatial/foundation-models-v4.tsx',sha256:sha('motion-canvas/src/projects/game-lighting-history-03/spatial/foundation-models-v4.tsx')},remainingScopedDefects:[],modelMotionProofReviewed:true,narrationTimingApproved:false,allFinalPixelsReviewed:false,fullEpisodeApproved:false,finalVideoProduced:false};
const out='projects/game-lighting-history-03/production/foundation-current-model-review-v4.json';fs.writeFileSync(path.join(root,out),JSON.stringify(composite,null,2)+'\n');
console.log(JSON.stringify({review,composite:out,paragraphs:31,scopedModelMotionReviewed:true,fullEpisodeApproved:false}));
