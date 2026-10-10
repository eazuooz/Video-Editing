const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process'),{makeCuesGlobal,norm}=require('./caption-phrases-v2.cjs');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const slug='game-lighting-history-03',audio=read(`projects/${slug}/project.json`).productionState.generatedNarration;
const rel='production/research/game-lighting-history/local/spatial-narrated-rehearsal-v2',dst='motion-canvas/src/projects/game-lighting-history-03/spatial';
if(fs.existsSync(path.join(root,rel,'plan.json')))throw Error('Existing v2 preserved');
if(sha(audio.path)!==audio.sha256)throw Error('Current narration changed');
const old='production/research/game-lighting-history/local/spatial-narrated-rehearsal-v1/caption-plan-v2.json',chapters=read(old).chapters;
chapters[0].paragraphs[0].move=[8.22,13.28];
chapters[0].paragraphs[0].motionRevision={reason:'Move ray/box comparison during spoken triangle-group boundary-box argument instead of earlier ray-equation sentence.',prior:[3.06,7.84],current:[8.22,13.28],asrWordAnchorsDirectlyRead:true};
const specs=[
 {scene:'16a',model:'nanite',proof:'engine-animated-proof-review-v1.json',moves:[[4.82,7.24],[15.34,20.56],[32.38,36.70],[42.28,45.64],[54.36,58.56],[63.72,65.80],[79.78,84.02]]},
 {scene:'17a',model:'lumen',proof:'engine-animated-proof-review-v1.json',moves:[[3.54,14.40],[18.26,23.08],[31.86,38.02],[47.38,50.84],[60.64,66.04],[71.24,74.94],[79.80,83.06]]},
 {scene:'17b',model:'cache',proof:'cache-animated-proof-review-v1.json',moves:[[.60,5.44],[14.14,18.32],[32.10,37.16],[44.66,50.48],[56.04,61.00],[72.84,78.00]]}
];
for(const spec of specs){const proofPath=`projects/${slug}/production/${spec.proof}`;if(!read(proofPath).modelMotionProofReviewed)throw Error('Model proof unreviewed');
 const p=`projects/${slug}/production/local/voice-asr-v2/whole-${spec.scene}.json`,r=read(p);if(r.audioSha256!==audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('Recognition changed');
 const cues=makeCuesGlobal(r),duration=r.sourceToSeconds-r.sourceFromSeconds,paragraphs=r.expectedKo.map((originalKo,index)=>({index,originalKo,from:index===0?0:cues.find(c=>c.paragraph===index).from,to:index===r.expectedKo.length-1?duration:cues.find(c=>c.paragraph===index+1).from,pair:[index*2,index*2+1],move:spec.moves[index],asrWordMotionAnchorsDirectlyRead:true}));
 chapters.push({scene:spec.scene,model:spec.model,sourceFrom:r.sourceFromSeconds,sourceTo:r.sourceToSeconds,duration,wholeAsr:{path:p,sha256:sha(p)},paragraphs,cues,proofRecord:proofPath});
}
let offset=0;for(const c of chapters){c.timelineFrom=offset;offset+=c.duration;if(norm(c.cues.map(q=>q.text).join(' '))!==norm(c.paragraphs.map(p=>p.originalKo).join(' ')))throw Error('Caption words changed');for(const p of c.paragraphs)if(p.move[0]<p.from-.05||p.move[1]>p.to+.05)throw Error(`Motion outside paragraph ${c.scene}/${p.index}`);for(const q of c.cues)if(q.to>c.duration+.01)throw Error('Cue beyond unchanged PCM');}
fs.mkdirSync(path.join(root,rel),{recursive:true});
const plan={createdAt:new Date().toISOString(),scope:'Six complete chapter explanation rehearsals. Current PCM and all original arguments retained. Revised balanced captions and BVH first-paragraph movement. Not a final episode/mix/gameplay allocation.',slug,style:'research-black-v1',audio,previousCaptionPlan:{path:old,sha256:sha(old)},chapters,duration:offset,frames:Math.round(offset*60),allCaptionTimingsDirectlyReviewed:false,allRehearsalPixelsReviewed:false,finalVideoApproved:false,localOnly:true};
fs.writeFileSync(path.join(root,rel,'plan.json'),JSON.stringify(plan,null,2)+'\n');
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),out=path.join(root,rel,'narration.wav');
const graph=chapters.map((c,i)=>`[0:a]atrim=start=${c.sourceFrom.toFixed(8)}:end=${c.sourceTo.toFixed(8)},asetpts=PTS-STARTPTS[a${i}]`).join(';')+`;${chapters.map((_,i)=>`[a${i}]`).join('')}concat=n=${chapters.length}:v=0:a=1[out]`;
const args=['-hide_banner','-v','error','-threads','2','-i',path.join(root,audio.path),'-filter_complex_threads','2','-filter_complex',graph,'-map','[out]','-c:a','pcm_s16le',out];const rr=spawnSync(ffmpeg,args,{encoding:'utf8',windowsHide:true});if(rr.status!==0)throw Error(rr.stderr);
function pcm(b){let i=12;while(i+8<=b.length){const n=b.readUInt32LE(i+4);if(b.toString('ascii',i,i+4)==='data')return b.subarray(i+8,i+8+n);i+=8+n+(n%2);}throw Error('RIFF data missing');}
const current=pcm(fs.readFileSync(path.join(root,audio.path))),rendered=pcm(fs.readFileSync(out)),bpf=2,sr=24000;
const selected=Buffer.concat(chapters.map(c=>current.subarray(Math.round(c.sourceFrom*sr)*bpf,Math.round(c.sourceTo*sr)*bpf)));
if(!selected.equals(rendered))throw Error('Selected PCM samples changed');
fs.writeFileSync(path.join(root,rel,'pcm-preservation.json'),JSON.stringify({createdAt:new Date().toISOString(),source:audio,selectedPcmByteIdentical:true,selectedBytes:selected.length,sampleRate:sr,channels:1,path:`${rel}/narration.wav`,sha256:sha(`${rel}/narration.wav`),audioBuildCommand:[ffmpeg,...args],exitCode:rr.status,retimed:false,finalMix:false},null,2)+'\n');
fs.writeFileSync(path.join(root,dst,'narrated-data-v2.json'),JSON.stringify(plan,null,2)+'\n');
const names=[];for(let i=0;i<chapters.length;i++){const name=`narrated-${chapters[i].model}-v2`;names.push(name);fs.writeFileSync(path.join(root,dst,`${name}.tsx`),`import {narratedChapterV2} from './narrated-runtime-v2';\nexport default narratedChapterV2(${i});\n`);fs.writeFileSync(path.join(root,dst,`${name}.meta`),JSON.stringify({version:0,timeEvents:[],seed:2838358939},null,2)+'\n');}
fs.writeFileSync(path.join(root,dst,'narrated-project-v2.ts'),`import {makeProject} from '@motion-canvas/core';\n${names.map((n,i)=>`import p${i} from './${n}?scene';`).join('\n')}\nexport default makeProject({scenes:[${names.map((_,i)=>`p${i}`).join(',')}],audio:'/\\u0040fs/D:/Github/Video-Editing/${rel}/narration.wav'});\n`);
fs.copyFileSync(path.join(root,dst,'narrated-project-v1.meta'),path.join(root,dst,'narrated-project-v2.meta'));
console.log(JSON.stringify({plan:`${rel}/plan.json`,chapters:chapters.length,paragraphs:chapters.reduce((n,c)=>n+c.paragraphs.length,0),cues:chapters.reduce((n,c)=>n+c.cues.length,0),duration:offset,selectedPcmByteIdentical:true,finalVideoApproved:false}));
