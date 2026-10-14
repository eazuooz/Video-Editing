// Narrow visual repair. Preserve every v5 source, narration sample and clock.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..');process.chdir(root);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sha=p=>hash(fs.readFileSync(p));
const src='motion-canvas/src/projects/game-lighting-history-04/spatial';
const base='production/research/game-lighting-history/local/episode04-depth-repairs-v6';
const priorPath='production/research/game-lighting-history/local/episode04-clean-model-inputs-v5/plan.json',prior=read(priorPath);
if(fs.existsSync(base))throw Error('Preserve prepared repair version');
if(sha(prior.runtime.path)!==prior.runtime.sha256||sha(prior.currentAudio.path)!==prior.currentAudio.sha256)throw Error('Current clock/PCM changed');
const replacements=[
 ['visibility-model-v1.tsx','visibility-model-v2.tsx',[["const e=layer(4),es=depthSpace(()=>0,[0,150],1);","const e=layer(4),es=depthSpace(()=>14,[0,150],1);"]]],
 ['upscaling-model-v2.tsx','upscaling-model-v3.tsx',[
  ["const b=layer(1),s=depthSpace(()=>0,[0,145],1);","const b=layer(1),s=depthSpace(()=>14,[0,145],1);"],
  ["b.add(text(label,0,145+y*.48-85,30,c));","b.add(text(label,-y*Math.sin(14*Math.PI/180),145+y*Math.cos(14*Math.PI/180)*.48-85,30,c));"],
  ["const f=layer(5),fs=depthSpace(()=>0,[0,95],1);","const f=layer(5),fs=depthSpace(()=>14,[0,95],1);"]
 ]]
];
const modelRecords=[];
for(const [from,to,edits] of replacements){let text=fs.readFileSync(src+'/'+from,'utf8');for(const [before,after]of edits){if(text.split(before).length!==2)throw Error('Exact scoped repair anchor missing');text=text.replace(before,after);}if(fs.existsSync(src+'/'+to))throw Error('Preserve existing model version');fs.writeFileSync(src+'/'+to,text);modelRecords.push({prior:src+'/'+from,priorSha256:sha(src+'/'+from),path:src+'/'+to,sha256:sha(src+'/'+to),edits});}
let runtime=fs.readFileSync(prior.runtime.path,'utf8').replace("from './upscaling-model-v2'","from './upscaling-model-v3'").replace("from './visibility-model-v1'","from './visibility-model-v2'");
const runtimePath=src+'/narrated-runtime-v3.tsx';if(fs.existsSync(runtimePath))throw Error('Preserve runtime version');fs.writeFileSync(runtimePath,runtime);
const ids=['original-18t-2','original-18t-6','original-18a-5'];
fs.mkdirSync(base+'/audio',{recursive:true});fs.mkdirSync(base+'/renders',{recursive:true});
const wav=fs.readFileSync(prior.currentAudio.path);let data;
for(let at=12;at+8<=wav.length;){const n=wav.readUInt32LE(at+4);if(wav.toString('ascii',at,at+4)==='data')data=wav.subarray(at+8,at+8+n);at+=8+n+(n%2);}
if(!data||data.length!==prior.currentAudio.samples*2)throw Error('PCM data mismatch');
const scenes=[],blocks=[],mapping=[];let cursor=0;
for(const id of ids){const s=prior.scenes.find(s=>s.id===id);if(!s)throw Error('Exact repair paragraph missing');const text=fs.readFileSync(s.wrapper,'utf8'),spec=JSON.parse(text.slice(text.indexOf('narratedScene04(')+16,text.lastIndexOf(');')));
 if(spec.renderCaptions!==false||spec.frames!==s.frames)throw Error('Clean exact-frame specification required');
 const wrapper=src+'/clean-depth-repair-'+id+'-v6.tsx';fs.writeFileSync(wrapper,"import {narratedScene04} from './narrated-runtime-v3';\nexport default narratedScene04("+JSON.stringify(spec,null,2)+");\n");
 const pcm=data.subarray(s.sourceSamples[0]*2,s.sourceSamples[1]*2);if(hash(pcm)!==s.originalPcmSha256)throw Error('Full paragraph PCM changed');blocks.push(pcm,Buffer.alloc(s.silentPaddingSamples*2));
 scenes.push({...s,wrapper,preservedV5Wrapper:s.wrapper,rendered:false,allPixelsReviewed:false});mapping.push({id,fromFrame:cursor,toFrame:cursor+s.frames,frames:s.frames});cursor+=s.frames;
}
const name='episode04-depth-repairs-v6',audio=base+'/audio/'+name+'.wav',pcm=Buffer.concat(blocks),h=Buffer.alloc(44);
h.write('RIFF');h.writeUInt32LE(pcm.length+36,4);h.write('WAVE',8);h.write('fmt ',12);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(24000,24);h.writeUInt32LE(48000,28);h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);fs.writeFileSync(audio,Buffer.concat([h,pcm]));
const project=src+'/'+name+'.ts';fs.writeFileSync(project,"import {makeProject} from '@motion-canvas/core';\n"+scenes.map((s,i)=>"import p"+i+" from './"+path.basename(s.wrapper,'.tsx')+"?scene';").join('\n')+"\nexport default makeProject({scenes:[p0,p1,p2],audio:"+JSON.stringify('/@fs/'+root.replace(/\\/g,'/')+'/'+audio)+"});\n");
fs.writeFileSync(project.replace(/\.ts$/,'.meta'),JSON.stringify({version:0,shared:{background:null,range:[0,(cursor-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:true}}}},null,2)+'\n');
const jobs=[{name,project,frames:cursor,scenes:mapping,audio:{path:audio,sha256:sha(audio),samples:pcm.length/2},output:base+'/renders/'+name+'.mp4',execution:base+'/renders/'+name+'.execution.json'}];
const plan={preparedAt:new Date().toISOString(),scope:'Only three projected side-face repairs. Preserve original v5 media and all audio/count/motion timing. Earlier pending journal named upscaling v1; actual v5 runtime uses v2, which is the corrected baseline here.',priorPlan:priorPath,runtime:{path:runtimePath,sha256:sha(runtimePath)},models:modelRecords,currentAudio:prior.currentAudio,currentAssembly:prior.currentAssembly,motion:prior.motion,captionDraft:prior.captionDraft,scenes,jobs,newTts:0,newGitImages:0,final:false,allFinalPixelsReviewed:false,finalMixedAsrApproved:false,final60to40Approved:false,outputCollected:false,uploaded:false};
fs.writeFileSync(base+'/plan.json',JSON.stringify(plan,null,2)+'\n');
fs.writeFileSync('motion-canvas/tsconfig.game-lighting-history04-depth-repairs-v6.json',JSON.stringify({extends:'./tsconfig.json',include:['src/env.d.ts',project.replace('motion-canvas/',''),...scenes.map(s=>s.wrapper.replace('motion-canvas/',''))]},null,2)+'\n');
console.log(JSON.stringify({prepared:3,frames:cursor,tts:0,rendered:false}));
