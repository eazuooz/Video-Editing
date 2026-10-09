// Current raw PCM is authority. This produces a review candidate, never final approval.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.relative(root,__dirname).replaceAll('\\','/');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>{const f=path.join(root,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
const fail=(x,msg)=>{if(!x)throw new Error(msg);};
const out=base+'/measured-allocation-v1/plan.json';fail(!fs.existsSync(path.join(root,out)),'Preserve existing measured candidate.');
const duplicateCheck=require('child_process').spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','similar-game-design','--check'],{cwd:root,encoding:'utf8'});fail(duplicateCheck.status===0,'Current duplicate review failed: '+duplicateCheck.stdout+duplicateCheck.stderr);
for(const n of ['current-whole-asr-direct-review-v1.json','current-contexts-asr-direct-review-v1.json','guides-whole-asr-direct-review-v3.json','guides-contexts-asr-direct-review-v3.json','current-mining-join-asr-direct-review-v1.json','fresh-guides-asr-direct-review-v4.json','unresolved-brotato-cut-direct-review-v3.json']) fail(fs.existsSync(path.join(root,base,n)),n);
fail(read(base+'/fresh-guides-research-resume-verification-v4.json').restorationVerified,'Research restoration not sealed.');
fail(read(base+'/fresh-guides-asr-direct-review-v4.json').allExpectedActualCompleteTextsAndWordEndsDirectlyCompared,'New voices pending');
fail(read(base+'/current-mining-join-asr-direct-review-v1.json').currentJoinedVoiceApproved,'Current04 pending');
const scripts=['narration','observation-guides-with-onset-repair','fresh-observation-guides'];
const versions=['',' .v3',' .v4'].map(x=>x.trim());
const ko=[],en=[];for(let i=0;i<3;i++)for(const [lang,dest] of [['ko',ko],['en',en]]){let a=read(`projects/similar-game-design/script/${scripts[i]}.${lang}${versions[i]}.json`).scenes;dest.push(...a.filter(s=>!s.id.startsWith('22-')));}
fail(ko.length===24 && en.length===24 && ko.reduce((n,s)=>n+s.lines.length,0)===73,'24 scenes /73 paragraphs required');
const old=read(base+'/current-original-paragraph-timing-v1.json').scenes;
const guide=read(base+'/guides-paragraph-timing-candidate-v3.json').scenes;
const fresh=read(base+'/fresh-guides-paragraph-timing-v4.json').scenes;
const join=read(base+'/current-mining-pcm-join-prepared-v1.json');
const voices=new Map([...old,...guide,...fresh].map(x=>[x.id,structuredClone(x)]));
const r4=voices.get('04-mining-route');r4.path=join.sourcePath;r4.sha256=join.sourceSha256;r4.totalSamples=join.sourceSamples;
r4.paragraphs.forEach((p,i)=>{if(i===0)p.sourceOutSample+=480;else{p.sourceInSample+=480;p.sourceOutSample+=480;}p.seconds=(p.sourceOutSample-p.sourceInSample)/24000;});
const bank=read('projects/similar-game-design/sources/game-candidates.json');
const sourceMap=new Map(bank.sourceCandidates.map(s=>[s.stem,s]));
// Later native edge review supersedes the conservative discovery ranges only
// for these same hashed sources; final selected pixels are still unapproved.
const edgeReview=read(base+'/current-native-source-edge-direct-review-v2.json');
for(const s of edgeReview.sources.filter(s=>s.stem.startsWith('drgs-engineer-'))){const current=sourceMap.get(s.stem);fail(current.sha256===s.sourceSha256,'Source edge hash changed');current.ranges=s.review.candidateIntervalsSeconds;current.rangeEvidence=base+'/current-native-source-edge-direct-review-v2.json';}
sourceMap.set('drgs-engineer-crystalline-02',{stem:'drgs-engineer-crystalline-02',path:'shared/output/similar-game-design/preflight/fresh-engineer02-v1/drgs-engineer-crystalline-02.mp4',sha256:'0656b2b48f6ebadbdca420d3e10410ef246b0c1e575c134d61a38827b9802044',crop:'crop=2272:1278:144:0',ranges:[[43,73],[77,90.8]],action:'Fresh official Engineer02: large green pursuit through rock gaps; gold pieces disappear near the avatar; avatar approaches/enters circle near88s with enemies remaining.'});
const short={'scout':'drgs-scout-crystalline-01','driller':'drgs-driller-magma-core-01','solo':'brotato-full-release','coop':'brotato-local-coop','e1':'drgs-engineer-crystalline-01','e2':'drgs-engineer-crystalline-02','e3':'drgs-engineer-crystalline-03'};
const order=['01-overview','02-familiar-action','03-patterns-not-ranking','04-mining-route','23-mining-and-pursuit','05-route-under-pressure','16-effects-and-position','17-rock-and-route','18-target-and-effects','06-follow-the-space','14-corridor-pursuit','15-corridor-to-open','25-gap-during-pursuit','07-purpose-combination','08-world-and-route','09-combination-in-motion','19-visible-destination','24-destination-and-danger','10-playing-together','20-moving-relationships','21-read-before-ranking','11-several-appeals','12-check-your-reason','13-conclusion'];
let position=120;const scenes=[];let cuts=[];let sourceUsed=new Map();let originalWhite=0;
const frame=t=>Math.round(t*60);
for(const id of order){
 const v=voices.get(id),s=ko.find(x=>x.id===id),e=en.find(x=>x.id===id);
 fail(v&&s&&e&&s.lines.length===e.lines.length,id);
 fail(sha(v.path)===v.sha256,'Voice changed '+id);
 const samples=v.totalSamples??v.samples,frames=Math.ceil(samples/400);
 const paragraphs=v.paragraphs.map((p,i)=>{fail(!p.expectedKo || p.expectedKo===s.lines[i],'Literal changed '+id);return {...p,ko:s.lines[i],en:e.lines[i],localStartFrame:frame(p.sourceInSample/24000),localEndFrame:i===v.paragraphs.length-1?frames:frame(p.sourceOutSample/24000)};});
 const row={id,title:s.title,voicePath:v.path,voiceSha256:v.sha256,sourceSamples:samples,sampleRate:24000,voiceSeconds:samples/24000,frames,startFrame:position,endFrameExclusive:position+frames,startSample48k:position*800,padOnlySamples24k:frames*400-samples,allRawPcmSamplesRetained:true,paragraphs,parts:[]};
 const add=(a,b,role,source=null,sourceIn=null,note='')=>{fail(b>a,id+' empty part');let p={scene:id,localStartFrame:a,localEndFrameExclusive:b,startFrame:position+a,endFrameExclusive:position+b,frames:b-a,role,narrationConnection:note,sourceAudio:false,loop:false,slowdown:false,selectedNativePixelsReviewed:false,captionPixelsReviewed:false,finalEncodedPixelsReviewed:false};
  if(source){const stem=short[source],src=sourceMap.get(stem);fail(src,stem);p={...p,source:stem,sourcePath:src.path,sourceSha256:src.sha256,sourceInFrame:sourceIn,sourceOutFrameExclusive:sourceIn+b-a,cropFilter:src.crop,visibleAction:src.action};fail(src.ranges.some(([x,y])=>sourceIn>=frame(x) && p.sourceOutFrameExclusive<=frame(y)),id+' outside observed range '+JSON.stringify(p));const used=sourceUsed.get(stem)||[];fail(!used.some(([x,y])=>sourceIn<y&&p.sourceOutFrameExclusive>x),id+' repeated source '+stem);used.push([sourceIn,p.sourceOutFrameExclusive]);sourceUsed.set(stem,used);}
  row.parts.push(p);cuts.push(p);
 };
 const A=(a,b,source,inSec,note)=>add(a,b,'actual',source,frame(inSec),note);
 const W=(a,b,note)=>add(a,b,'explanation',null,null,note);
 const b=paragraphs.map(p=>p.localEndFrame),start=paragraphs.map(p=>p.localStartFrame);
 switch(id.slice(0,2)){
  case '01': W(0,frames,'Full narrated overview: arena, mining route, shared play and viewer question.');break;
  case '02': A(0,760,'solo',2,'Different edited avatars/builds show familiar avoidance and attacks.');add(760,b[1],'actual','solo',1748,'Separate arena shot continues following avatar/enemy positions.');W(b[1],frames,'Familiar action versus distinct experience; no universal ranking.');break;
  case '03': add(0,228,'actual','solo',880,'Red extended light appears while narrator names light at2.78–3.78s.');add(228,312,'actual','solo',1223,'Purple projectiles occupy several directions at3.78–5.18s.');add(312,472,'actual','solo',1493,'Placed small structures are visible as narrator names structures at5.18–7.54s.');add(472,587,'actual','solo',1108,'Separate red-light pattern, explicitly edited examples.');add(587,773,'actual','solo',1307,'Separate robot/projectile pattern.');add(773,868,'actual','solo',1653,'Small structures and nearby positions.');add(868,b[1],'actual','solo',2423,'Separate gunfire example; no weapon-strength inference.');W(b[1],frames,'Different pattern demands; far targets versus nearby risk.');break;
  case '04': A(0,b[1],'scout',8,'Bright and green ore pieces disappear while avatar moves around rocks/enemies.');W(b[1],b[2],'Mining destination adds a terrain-reading purpose to movement.');add(b[2],frames,'actual','scout',480+b[1],'Another movement/ore comparison; not same chronological result.');break;
  case '05': A(0,b[1],'scout',36,'Moving through pressure while mining and finding rock gaps.');W(b[1],frames,'Two demands coexist around the same movement action.');break;
  case '06': A(0,1800,'scout',63,'Large green enemy, rock route and later gold pieces; source action checked against full paragraphs.');A(1800,frames,'scout',136,'Separate terrain-route shot for general observation, without implied prior outcome.');break;
  case '07': A(0,b[0],'scout',93,'Marked destination and surrounding enemies.');add(b[0],b[0]+365,'actual','solo',2058,'Different arena: red circles around moving character, separate comparison.');add(b[0]+365,b[1],'actual','solo',2554,'Another arena shot compares nearby threats/avoidance.');W(b[1],frames,'Combine purpose and space around familiar actions.');break;
  case '08': A(0,b[1],'driller',3,'Magma-rock corridor, fire and pursuing enemy.');W(b[1],frames,'World/space connect to movement, rather than cosmetic labels alone.');break;
  case '09': add(0,b[1],'actual','driller',1141,'Destination and obstacle relations in magma terrain.');A(b[1],b[2],'scout',114,'Separate marked-circle approach; comparison rather than continuous outcome.');W(b[2],frames,'Connect destination, route and pressure; check visible relations.');break;
  case '10': add(0,300,'actual','solo',2733,'Solo shot accompanies solo/introduction clause; coop starts before multiple avatars clause at5.08s.');A(300,b[1],'coop',40,'Several avatars share arena; no rescue/winner claim.');W(b[1],frames,'Shared play is an additional appeal, not one numeric strength axis.');break;
  case '11': W(0,start[2],'Different combinations appeal in different situations.');add(start[2],b[2],'actual','scout',8520,'Avatar, nearby targets and rock route as observable experience.');W(b[2],frames,'Separate appeal communication from preference/market evidence.');break;
  case '12': W(0,b[0],'Write the familiar action, situation and experience in one sentence.');A(b[0],b[1],'scout',162,'Crowded enemies and usable escape space.');A(b[1],b[1]+420,'driller',40,'Circle approach and arriving supply pod during specific observation.');A(b[1]+420,b[2],'driller',55,'Separate terrain example while narrator explicitly disclaims chronological next outcome.');W(b[2],frames,'Ask whether a small trial conveys the intended choice reason.');break;
  case '13': A(0,b[0],'driller',58,'Rock route, nearby enemy and avatar in one spatial relationship.');W(b[0],frames,'Return to purpose/space/shared-play combinations and own implementation question.');break;
  case '14': A(0,frames,'e3',0,'Fresh separate official pursuer and narrow-to-open rock-route example.');break;
  case '15': A(0,583,'e3',14.1666666667,'Follow narrow-to-open movement; start conceptual comparison while useful source action remains.');W(583,frames,'White spatial comparison continues observation question; no idle quota.');break;
  case '16': A(0,622,'e1',4,'Fire, small structures and avatar route viewed separately.');W(622,frames,'Compare trajectory and effect as separate spatial observations.');break;
  case '17': A(0,frames,'e1',14.3666666667,'Avatar moves beside rock edge toward open areas with approaching enemies.');break;
  case '18': A(0,frames,'e1',27.25,'Large green target appears around34.5s, aligned to second paragraph7.26s; keep effect/target distinct.');break;
  case '19': A(0,552,'e1',53,'Separate return segment: arrows, approach pod, surrounding targets remain.');W(552,frames,'Spatial purpose changes which relations to observe.');break;
  case '20': A(0,frames,'e3',41,'Near-route targets and green/purple lines observed without inferring weapon identity.');break;
  case '21': A(0,740,'e3',55.65,'Swarm message does not establish outcome; follow avatar path and approaching targets.');W(740,frames,'Experience combination as new-work choice question.');break;
  case '23': A(0,frames,'e2',59.7,'Gold approach/pieces disappear and following enemies in same terrain.');break;
  case '24': A(0,513,'e2',82,'Approach circle, enter around88s; second paragraph starts6.035s/current shot88.035, nearby enemies remain.');W(513,frames,'Destination and danger both remain active spatial demands.');break;
  case '25': A(0,frames,'e2',43,'Large green pursuer and rock gap; connect movement to terrain judgment.');break;
  default: throw new Error(id);
 }
 fail(row.parts[0].localStartFrame===0&&row.parts.at(-1).localEndFrameExclusive===frames,'Coverage '+id);
 row.parts.forEach((p,i)=>{if(i)fail(row.parts[i-1].localEndFrameExclusive===p.localStartFrame,'Gap '+id);});
 if(Number(id.slice(0,2))<=13)originalWhite+=row.parts.filter(p=>p.role==='explanation').reduce((n,p)=>n+p.frames,0);
 scenes.push(row);position+=frames;
}
const actual=cuts.filter(p=>p.role==='actual').reduce((n,p)=>n+p.frames,0),white=position-120-actual;
// Only the natural conclusion reflection tail is adjustable; no actual footage padding.
const tail=Math.round(actual*2/3-white);fail(tail>=0 && tail<=60,'Reflection tail must be0–1s: '+tail);
if(tail){const last=scenes.at(-1);last.frames+=tail;last.endFrameExclusive+=tail;last.padOnlySamples24k+=tail*400;last.parts.at(-1).localEndFrameExclusive+=tail;last.parts.at(-1).endFrameExclusive+=tail;last.parts.at(-1).frames+=tail;last.reflectionTailFrames=tail;position+=tail;}
const body=position-120,final=position+600,explanation=body-actual,error=actual-body*.6;
fail(Math.abs(error)<=1,'60:40 exceeds1frame');fail(originalWhite/60>=222.670041667-1/60,'Original white explanations shortened');
const selected=cuts.filter(p=>p.role==='actual').flatMap(p=>{const internal=({solo:[309,550,880,1223,1493,1748,2423,2654,2953],coop:[2555,2902]})[Object.keys(short).find(k=>short[k]===p.source)]||[];const edges=[p.sourceInFrame,...internal.filter(n=>n>p.sourceInFrame&&n<p.sourceOutFrameExclusive),p.sourceOutFrameExclusive];return edges.slice(1).map((z,i)=>({...p,sourceInFrame:edges[i],sourceOutFrameExclusive:z,startFrame:p.startFrame+edges[i]-p.sourceInFrame,endFrameExclusive:p.startFrame+z-p.sourceInFrame,frames:z-edges[i],internalMontageSplit:edges.length>2}));});
const plan={schemaVersion:1,createdAt:new Date().toISOString(),slug:'similar-game-design',candidateOnly:true,sourceAllocationApproved:false,allSelectedNativePixelsReviewed:false,finalTimingApproved:false,bodyRatioApproved:false,allFinalPixelsReviewed:false,finalMixedAsrApproved:false,render:false,qa:false,collected:false,uploaded:false,videoId:null,sceneCount:24,paragraphCount:73,rawPcmSeconds:scenes.reduce((n,s)=>n+s.voiceSeconds,0),allCurrentPcmRetained:true,originalWhiteFrames:originalWhite,originalWhiteSeconds:originalWhite/60,originalWhitePcmSeconds:222.670041667,actualFrames:actual,explanationFrames:explanation,bodyFrames:body,finalFrames:final,fps:60,width:1920,height:1080,videoTimeBase:'1/90000',expectedPtsStep:1500,ratioErrorFrames:error,introFrames:120,outroFrames:600,conclusionReflectionTailFrames:tail,sourceAudioJobs:0,selfCreatedGameplay:false,loops:0,slowdowns:0,scenes,selectedNativeCuts:selected,sources:[...sourceMap.values()].map(s=>({id:s.stem,path:s.path,sha256:s.sha256,crop:s.crop,ranges:s.ranges})),reviewNote:'Measured frame/sample candidate only. All selected edges, active named actions, crops, captions, actual animated white states and final encoded pixels require direct review. Original PCM and useful white explanation preserved; no recognizer-only or ratio-only approval.'};
write(out,plan);
write(base+'/measured-allocation-v1/script.ko.json',{title:read('projects/similar-game-design/script/narration.ko.json').title,language:'ko',independentlyAuthored:true,scenes:order.map(id=>ko.find(s=>s.id===id))});
write(base+'/measured-allocation-v1/script.en.json',{title:read('projects/similar-game-design/script/narration.en.json').title,language:'en',independentlyAuthored:true,scenes:order.map(id=>en.find(s=>s.id===id))});
console.log(JSON.stringify({candidate:out,rawPcmSeconds:plan.rawPcmSeconds,bodyFrames:body,actualFrames:actual,whiteFrames:explanation,ratioErrorFrames:error,tailFrames:tail,nativeCuts:selected.length,finalFrames:final,approved:false}));
