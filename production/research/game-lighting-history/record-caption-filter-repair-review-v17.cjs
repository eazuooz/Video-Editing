const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const base='projects/game-lighting-history-03/production/';
const diagnostic=read(base+'caption-frame-property-diagnostic-v15.json');
const state=read(base+'caption-filter-boundary-test-execution-v17.json');
const short=read(base+'caption-filter-boundary-test-execution-v16.json');
const [old,fixed]=state.results;
const oldLog=fs.readFileSync(path.resolve(root,old.encode.log),'utf8');
const fixedLog=fs.readFileSync(path.resolve(root,fixed.encode.log),'utf8');
const drops=s=>[...s.matchAll(/drop=(\d+)/g)].map(x=>Number(x[1]));
if(!oldLog.includes('Reconfiguring filter graph because video parameters changed') || Math.max(...drops(oldLog))!==4583)throw new Error('Require observed old reset/drop log');
if(fixedLog.includes('Reconfiguring filter graph') || drops(fixedLog).some(x=>x!==0))throw new Error('Corrected path changed state or dropped frames');
if(fixed.observedFrames!==4920 || !fixed.continuousExpectedPts || fixed.probe.streams[0].nb_read_frames!=='4920')throw new Error('Require exact corrected82s frames/PTS');
if(diagnostic.observedFrames!==93084 || !diagnostic.allInputPresentationPtsContinuous)throw new Error('Require current full decoded input');
const dest=base+'caption-filter-repair-review-v17.json';if(fs.existsSync(path.resolve(root,dest)))throw new Error('Preserve review');
const record={reviewedAt:new Date().toISOString(),status:'caption-only-recovery-authorized',
 inputDiagnostic:{path:base+'caption-frame-property-diagnostic-v15.json',sha256:hash(base+'caption-frame-property-diagnostic-v15.json')},
 boundaryTestState:{path:base+'caption-filter-boundary-test-execution-v17.json',sha256:hash(base+'caption-filter-boundary-test-execution-v17.json'),status:state.status,error:state.error},
 shortSeekTest:{path:base+'caption-filter-boundary-test-execution-v16.json',sha256:hash(base+'caption-filter-boundary-test-execution-v16.json'),failureNotReproduced:true,corrected600Frames:true},
 evidence:[old,fixed].map(x=>({label:x.label,video:{path:x.path,sha256:x.sha256},log:{path:x.encode.log,sha256:hash(x.encode.log)},directFullLogRead:true,probe:x.probe,observedFrames:x.observedFrames,continuousExpectedPts:x.continuousExpectedPts})),
 observedOriginalDropFrames:4583,correctedDropFrames:0,
 diagnosis:'At decoded frame4585 (76.416667s), input colour metadata changes from unknown tobt709/tv. The original filter reconfigures, resets N used by setpts, and logs4583 dropped frames. In a time-limited test, ffmpeg consumes later input to fill output82s; equal output counts alone do not prove original content alignment.',
 testAssertionLimitation:'The v17 harness failed because it incorrectly expected the old82s output frame count to differ. Its preserved log reproduces the reset and4583 drops. Corrected82s output has4920 decoded frames, exact1500PTS spacing and no drops/reinitialization; recorded separately without relabeling the failed harness.',
 correctedFilter:'-reinit_filter0; preserve existing absolute input PTS; setsar=1,ass; fps_mode=passthrough; enc_time_base=1/90000; decoder/filter/encoder CPU2; GPU0',
 preserved:['original narration','current mixed WAV/AAC','clean mux','native and Motion Canvas inputs','failed captioned encode','both short tests'],
 finalPairRecoveryAllowed:true,fullCorrectedFramesVerified:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitMedia:0,newGitImages:0,
 officialReference:'https://ffmpeg.org/ffmpeg.html#Main-options',humanWholeListening:'pending',humanPronunciation:'pending'};
fs.writeFileSync(path.resolve(root,dest),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({review:dest,oldDropped:4583,correctedBoundaryFrames:4920,captionOnlyRecoveryAuthorized:true,finalQA:false}));
