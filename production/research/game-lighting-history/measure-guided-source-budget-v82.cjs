// Measure completed new takes against distinct native source capacity.
// This records deficits; it never approves footage, ASR, timing or publishing.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const source='projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json';
const execution=process.argv.includes('--execution')?process.argv[process.argv.indexOf('--execution')+1]:base+'part3-guided-actions-tts-execution-v69.json';
if(!execution?.startsWith(base)||execution.includes('..'))throw Error('Use an exact owned production execution path');
const request=base+'part3-guided-actions-tts-request-v69.json';
const split=base+'measured-additive-physical-split-v39.json';
const framing=base+'physical-framing-selected-execution-v55.json';
const includeHogwarts=process.argv.includes('--include-hogwarts');
const output=base+(includeHogwarts?'guided-observation-source-budget-measured-v89.json':'guided-source-budget-measured-v82.json');
function wavFormat(p){
 const b=fs.readFileSync(path.join(root,p));
 if(b.toString('ascii',0,4)!=='RIFF'||b.toString('ascii',8,12)!=='WAVE')throw Error('Unsupported WAV '+p);
 let format,data;
 for(let o=12;o+8<=b.length;){
  const tag=b.toString('ascii',o,o+4),n=b.readUInt32LE(o+4),a=o+8;
  if(a+n>b.length)throw Error('Truncated WAV '+p);
  if(tag==='fmt '){if(n<16)throw Error('Short format '+p);format={encoding:b.readUInt16LE(a),channels:b.readUInt16LE(a+2),rate:b.readUInt32LE(a+4),align:b.readUInt16LE(a+12),bits:b.readUInt16LE(a+14)};}
  if(tag==='data')data=n;
  o=a+n+(n%2);
 }
 if(!format||data===undefined||format.encoding!==1||format.channels!==1||format.rate!==24000||format.bits!==16||format.align!==2||data%2)throw Error('Expected mono24k PCM16 '+p);
 return {...format,samples:data/2};
}
function main(){
 if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing measured audit');
 const s=read(source),r=read(request),t=read(execution),p=read(split),f=read(framing);
 if(s.scenes.length!==37||r.scenes.length!==37||t.results?.length!==37||!t.generationComplete||t.exitCode!==0)throw Error('All37 completed technical takes required before measurement');
 if(t.requestSha256!==sha(request))throw Error('Execution request changed');
 for(const x of r.protectedInputs)if(sha(x.path)!==x.sha256)throw Error('Protected input changed '+x.path);
 const takes=new Map(t.results.map(x=>[x.id,x]));
 const scenes=[...s.scenes];let supplementaryBindings=null;
 if(includeHogwarts){
  const sp='projects/game-lighting-history-04/script/physical-part3-hogwarts-observation.koen.v81.json',rp=base+'hogwarts-observation-tts-request-v85.json',ep=base+'hogwarts-observation-tts-execution-v85.json';
  const ss=read(sp),rr=read(rp),ee=read(ep),hp='shared/output/gpu-handoff/'+ee.leaseToken+'.json';
  if(ss.scenes.length!==6||ee.results?.length!==6||!ee.generationComplete||ee.exitCode!==0||ee.requestSha256!==sha(rp)||read(hp).state!=='research_resume_verified')throw Error('All six measured technical takes and research restoration required');
  for(const x of rr.protectedInputs)if(sha(x.path)!==x.sha256)throw Error('Supplementary input changed '+x.path);
  for(const x of ee.results){if(takes.has(x.id))throw Error('Repeated narration identity');takes.set(x.id,x);}
  scenes.push(...ss.scenes);supplementaryBindings={script:ref(sp),request:ref(rp),execution:ref(ep),researchRestoration:ref(hp)};
 }
 const intervals=new Map(),rows=[];
 for(const scene of scenes){
  const take=takes.get(scene.id);
  if(!take?.technicalTailGatePassed||sha(take.path)!==take.sha256)throw Error('Changed or technically failed take '+scene.id);
  const wav=wavFormat(take.path);
  if(wav.samples!==take.samples||take.sampleRate!==24000)throw Error('Measured PCM changed '+scene.id);
  const pcmFrames=Math.ceil(wav.samples/400);
  let candidateSourceFrames=0;
  for(const [a,b] of scene.ranges){
   if(!(a>=0&&b>a))throw Error('Invalid native range '+scene.id);
   const range=[Math.ceil(a*60-1e-5),Math.floor(b*60+1e-5)];
   candidateSourceFrames+=range[1]-range[0];
   const file=scene.sourcePath||s.sources[scene.source].path,prior=intervals.get(file)||[];
   for(const other of prior)if(Math.max(range[0],other.frames[0])<Math.min(range[1],other.frames[1]))throw Error('Repeated proposed source '+scene.id+' / '+other.id);
   prior.push({id:scene.id,frames:range,nativeSeconds:[a,b]});intervals.set(file,prior);
  }
  rows.push({id:scene.id,proposedRole:scene.role,insertAfter:includeHogwarts&&scene.id==='appearance-to-controls'?'hogwarts-courtyard-ui':scene.insertAfter,pcm:ref(take.path),samples:wav.samples,seconds:wav.samples/24000,pcmFrames,silentRoundingSamples:pcmFrames*400-wav.samples,candidateSourceFrames,candidateSeconds:candidateSourceFrames/60,shortfallFrames:scene.role==='actual'?Math.max(0,pcmFrames-candidateSourceFrames):0,sourceCutAndMovingPixelsApproved:false,finalClassificationApproved:false,requiresSpecialRoleReview:scene.id.startsWith('focus-later-')||scene.id==='focus-observation-protocol'||scene.id==='focus-to-frame-inspection',note:'Candidate capacity is an upper bound. Held UI/diagram-led/frozen views must be excluded or reclassified after direct moving review; preserve the full PCM.'});
 }
 const part=p.parts.find(x=>x.physicalPart===3),overview=f.results.find(x=>x.id==='part3-overview');
 if(!part||!overview?.technicalTailGatePassed||sha(overview.path)!==overview.sha256||wavFormat(overview.path).samples!==overview.samples)throw Error('Preserved physical-part3 framing changed');
 const newE=rows.filter(x=>x.proposedRole==='explanation').reduce((n,x)=>n+x.pcmFrames,0),newA=rows.filter(x=>x.proposedRole==='actual').reduce((n,x)=>n+x.pcmFrames,0);
 const explanationFrames=part.preservedExplanationFrames+Math.ceil(overview.samples/400)+newE;
 const lowerBoundExtraA=Math.ceil(explanationFrames*1.5-part.preservedActualFrames-1e-5);
 const capacity=rows.filter(x=>x.proposedRole==='actual').reduce((n,x)=>n+x.candidateSourceFrames,0);
 const out={schemaVersion:1,measuredAt:new Date().toISOString(),status:'measured-PCM-and-candidate-source-budget; not-final-approval',bindings:{script:ref(source),request:ref(request),execution:ref(execution),preservedSplit:ref(split),selectedFraming:ref(framing),supplementaryHogwarts:supplementaryBindings},rows,
  measuredNewNarrationFrames:rows.reduce((n,x)=>n+x.pcmFrames,0),measuredNewNarrationSeconds:rows.reduce((n,x)=>n+x.samples,0)/24000,
  provisionalPart3:{preservedActualFrames:part.preservedActualFrames,preservedExplanationFrames:part.preservedExplanationFrames,overviewFrames:Math.ceil(overview.samples/400),newExplanationPcmFrames:newE,newActualProposedPcmFrames:newA,explanationFramesBeforeAnyReclassification:explanationFrames,minimumAdditionalActualFrames:lowerBoundExtraA,minimumAdditionalActualSeconds:lowerBoundExtraA/60,newDistinctCandidateSourceFrames:capacity,newDistinctCandidateSourceSeconds:capacity/60,candidateCapacityDeficitFrames:Math.max(0,lowerBoundExtraA-capacity),capacityIsApprovedActualFootage:false},
  overlapCheck:{newProposedRangesDistinct:true,retainedSourceRangeOverlapRequiresFinalTimelineAudit:true},
  supplementaryHogwartsV81:{preparedCandidateSeconds:127,measuredNarration:includeHogwarts,boundedNormalSpeedSamplesDirectlyRead:includeHogwarts,fullContinuousMovingReviewApproved:false,includedInThisBudget:includeHogwarts},
  sourceDurationDoesNotApproveActualRole:true,allWholeAndIndependentAsrDirectlyReviewed:false,humanListeningApproved:false,bodyRatioApproved:false,finalTimingApproved:false,allFinalPixelsReviewed:false,uploaded:false,newGitImages:0};
 fs.writeFileSync(path.join(root,output),JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({output,newNarrationSeconds:out.measuredNewNarrationSeconds,provisionalPart3:out.provisionalPart3,overCapacity:rows.filter(x=>x.shortfallFrames).map(x=>({id:x.id,missingSeconds:x.shortfallFrames/60})),bodyRatioApproved:false}));
}
main();
