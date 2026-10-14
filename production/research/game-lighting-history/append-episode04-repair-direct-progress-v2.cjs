// These six completed results were directly read, including every word timestamp.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production',read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const target=base+'/voice-repair-direct-progress-v1.json',review=read(target);
const findings={
 'whole-18tg2':{findings:'Both complete target paragraphs and final dependence sentence represented; no omitted sentence, repetition, arbitrary greeting or backward timestamp observed.',differences:['지터→짙어 at5.06–5.44','프레임의→프레임에 at15.50–16.06','얇은→얄은 at19.76–20.02'],independentAudioContext:false,samePcmAs:'context-18tg2'},
 'context-18tg2':{findings:'Same entire two-paragraph PCM as whole-18tg2. Same recognition differences. This is a repeated recognizer run, not independent audio context evidence.',differences:['지터→짙어 at5.06–5.44','프레임의→프레임에 at15.50–16.06','얇은→얄은 at19.76–20.02'],independentAudioContext:false,samePcmAs:'whole-18tg2'},
 'whole-18tg3':{findings:'Both complete target paragraphs and final 서로 다른 효과를 섞게 됩니다 represented. Prior paragraph repetition is absent in this result. Final words run monotonically26.88–28.22s; no ASR omission, arbitrary greeting or extra ending observed. Selected TTS attempt still fails its numerical tail criterion; recognition does not waive that failure.',differences:[],independentAudioContext:false,samePcmAs:'context-18tg3',tailCriterionApproved:false},
 'context-18tg3':{findings:'Same entire two-paragraph PCM as whole-18tg3, identical full recognition. This does not resolve the failed tail criterion through independent complete context.',differences:[],independentAudioContext:false,samePcmAs:'whole-18tg3',tailCriterionApproved:false},
 'whole-22rg4':{findings:'Recognition starts 엔진이라도 버전과... and omits the entire first sentence 엔진의 기능 이름만으로 실제 프레임의 구조를 확정하지 않겠습니다 plus 같은 at the start of sentence2. Remaining three-paragraph content and final cause-isolation sentence are represented without repetition/backward timestamps. Missing opening is unresolved: do not assume recognizer loss or actual synthesis loss until a distinct opening context and current PCM are checked.',differences:['Opening first sentence absent; 같은 absent before 엔진이라도','밖의→밖에 at14.64–14.88'],independentAudioContext:true,openingContentApproved:false},
 'context-22rg4':{findings:'Both target paragraphs represented and end29.18s. This window begins at111.0425s and excludes the missing first sentence in whole-22rg4, so it cannot validate that opening.',differences:['밖의→밖에 at4.26–4.50'],independentAudioContext:true,openingContentApproved:false}
};
for(const [label,details] of Object.entries(findings)){
 if(review.windows.some(w=>w.label===label))throw Error('Already recorded '+label);
 const result=base+'/local/voice-repair-asr-v1/'+label+'.json',r=read(result);
 if(r.audio.sha256!==review.audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('Current audio/prompt mismatch');
 review.windows.push({label,result,sha256:sha(result),sourceSampleRange:r.sourceSampleRange,pcmFloat32Sha256:r.pcmFloat32Sha256,expectedKo:r.job.expectedKo,actualFullText:r.text,allWordTimestampsDirectlyRead:true,directFullTextCompared:true,...details,pronunciationListening:'pending; recognition spelling is not a definitive synthesis diagnosis',currentNarrationApproved:false});
}
review.reviewedAt=new Date().toISOString();review.reviewedWindows=review.windows.length;review.scope='Eight of12 repaired-group recognition windows directly compared; duplicate whole/context PCM identified and not counted as independent context.';
review.unresolvedTailCriterion='18tg3 selectedattempt1 ratio.071 exceeds.07; whole/context recognition uses identical PCM and does not waive the failure.';
review.unresolvedOpening='22rg4 whole recognition omits sentence1 and start of sentence2; context22rg4 excludes this region. Distinct opening context/current PCM comparison required.';
review.allCurrentVoiceApproved=false;review.all12DirectlyCompared=false;review.humanWholeListeningApproved=false;review.finalMixedAsrApproved=false;
fs.writeFileSync(path.join(root,target),JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify({directlyCompared:review.reviewedWindows,total:12,approved:false,unresolvedOpening:true}));
