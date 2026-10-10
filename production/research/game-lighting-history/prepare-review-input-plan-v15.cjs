const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const tp=prod+'/measured-native-timeline-candidate-v15.json',np=prod+'/native-framing-plan-v16.json',cp=prod+'/retained-clean-render-plan-v2.json',dp='motion-canvas/src/projects/game-lighting-history-03/spatial/retained-clean-data-v2.json',out=prod+'/review-input-plan-v15.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve input plan');
const t=read(tp),n=read(np),c=read(cp),d=read(dp),inputs=[],chapterCursor=new Map();
const brand='projects/game-reward-planning/production/final-v1/white-segments/branding.mp4',member='projects/game-reward-planning/production/final-v1/white-segments/membership.mp4';
if(sha(brand)!=='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'||sha(member)!=='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123')throw Error('Original branding/member media changed');
inputs.push({id:'branding',kind:'preserved-original-branding',fromFrame:0,toFrame:120,frames:120,media:brand,sha256:sha(brand),copyByteIdentically:true});
for(const s of t.slots){
 if(s.role==='actual'){
  const cuts=n.cuts.filter(x=>x.slotId===s.id);if(!cuts.length||cuts.reduce((a,x)=>a+x.frames,0)!==s.frames)throw Error('Actual input allocation changed');
  for(const x of cuts)inputs.push({...x,kind:'actual-review-input',verification:x.output.replace(/\.mp4$/,'.verification.json'),allPixelsReviewed:false});
 }else{
  const clip=d.clips.find(x=>x.id===s.id),ch=c.chapters.find(x=>x.scene===s.scene),localFrom=chapterCursor.get(s.scene)||0;
  if(!clip||clip.frames!==s.frames||!ch)throw Error('Retained explanation changed');
  const output='production/research/game-lighting-history/local/explanation-framing-v15/'+s.id+'.mp4';
  inputs.push({id:s.id,kind:'explanation-review-input',scene:s.scene,sourceChapter:ch.output,sourceChapterVerification:ch.output.slice(0,ch.output.lastIndexOf('/'))+'/'+ch.name+'.verification.json',localFromFrame:localFrom,localToFrame:localFrom+s.frames,frames:s.frames,fromFrame:s.fromFrame,toFrame:s.toFrame,output,verification:output.replace(/\.mp4$/,'.verification.json'),posePair:s.posePair,wholeMotionSeconds:s.motionSeconds,allPixelsReviewed:false});
  chapterCursor.set(s.scene,localFrom+s.frames);
 }
}
for(const ch of c.chapters)if(chapterCursor.get(ch.scene)!==ch.frames)throw Error('Full retained chapter not used exactly once');
inputs.push({id:'membership',kind:'preserved-original-membership',fromFrame:t.totals.finalFrames-600,toFrame:t.totals.finalFrames,frames:600,media:member,sha256:sha(member),copyByteIdentically:true});
if(inputs.reduce((sum,x)=>sum+x.frames,0)!==t.totals.finalFrames||inputs.some((x,i)=>x.fromFrame!==(i?inputs[i-1].toFrame:0)))throw Error('Input frame gap/overlap');
const record={preparedAt:new Date().toISOString(),status:'review-input-plan-not-final-adopted',inputHashes:[tp,np,cp,dp].map(p=>({path:p,sha256:sha(p)})),inputs,totals:t.totals,finalSeconds:t.finalSeconds,cpuThreads:2,gpuJobs:0,noSourceAudio:true,loops:0,rateChanges:0,allOriginalPcmPreserved:true,retainedWholeExplanations:46,completeMotionTails:1,allInputPixelsReviewed:false,finalMixedAsrApproved:false,collected:false,uploaded:false};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({inputs:inputs.length,native:n.cuts.length,explanation:d.clips.length,frames:record.totals.finalFrames,mediaCreated:0,finalApproved:false}));
