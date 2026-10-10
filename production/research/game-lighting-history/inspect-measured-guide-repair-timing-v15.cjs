// Read-only proposal after selective repairs exist. Never adopts roles or writes
// audio, captions, scenes or a ratio approval from a subset calculation.
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-03/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const repaired=read(b+'/native-guide-repairs-tts-execution-v2.json');
if(!repaired.generationComplete||repaired.exitCode!==0||repaired.joinedGuides.length!==2)throw Error('Wait for actual completed selective repair candidates');
const originals=read(b+'/original-paragraph-cut-plan-v12.json').paragraphs,old=read(b+'/native-guides-tts-execution-v1.json');
const replacement=new Map(repaired.joinedGuides.map(x=>[x.id,x]));
const guides=old.results.map(x=>replacement.get(x.id)||x);
const originalFrames=originals.reduce((n,x)=>n+x.frames,0),guideFrames=guides.reduce((n,x)=>n+Math.ceil(x.samples/400),0);
const bodyFrames=originalFrames+guideFrames,baseExplanation=originals.filter(x=>x.retainedExplanation).reduce((n,x)=>n+x.frames,0);
const target=Math.round(bodyFrames*.4),needed=target-baseExplanation;
const candidates=originals.filter(x=>!x.retainedExplanation&&x.frames<=needed+1);
const dp=new Map([[0,[]]]);
for(const p of candidates)for(const [sum,ids] of [...dp]){const next=sum+p.frames;if(next>needed+1)continue;const prev=dp.get(next);if(!prev||prev.length>ids.length+1)dp.set(next,[...ids,p.index]);}
const proposals=[...dp].filter(([sum,ids])=>Math.abs(sum-needed)<=1&&ids.length).sort((a,b)=>a[1].length-b[1].length).map(([sum,ids])=>({additionalFrames:sum,ratioFrameError:baseExplanation+sum-bodyFrames*.4,paragraphs:ids.map(i=>{const p=originals.find(x=>x.index===i);return {index:i,scene:p.scene,frames:p.frames,text:p.text,model:p.sourceModel,motionSeconds:p.motionSeconds};})}));
console.log(JSON.stringify({bodyFrames,finalFrames:bodyFrames+720,bodySeconds:bodyFrames/60,originalFrames,guideFrames,baseExplanation,targetExplanation:target,neededAdditionalExplanation:needed,repairedGuides:repaired.joinedGuides.map(x=>({id:x.id,seconds:x.seconds,frames:Math.ceil(x.samples/400)})),wholeParagraphProposals:proposals,adopted:false,voiceApproved:false},null,2));
