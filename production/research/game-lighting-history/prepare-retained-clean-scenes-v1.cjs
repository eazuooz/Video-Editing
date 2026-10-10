const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),project='projects/game-lighting-history-03',spatial='motion-canvas/src/'+project+'/spatial';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const timelinePath=project+'/production/measured-native-timeline-candidate-v13.json',dataPath=spatial+'/narrated-data-v3.json',outputPath=spatial+'/retained-clean-data-v1.json';
if(fs.existsSync(path.join(root,outputPath)))throw Error('Preserve prepared clean scenes');
const timeline=read(timelinePath),data=read(dataPath),clips=timeline.slots.filter(x=>x.role==='explanation');
if(clips.length!==47||clips.reduce((n,x)=>n+x.frames,0)!==37244)throw Error('Exact47 complete explanations required');
for(const x of clips){const c=data.chapters[x.chapterIndex],p=c.paragraphs[x.paragraphIndex];if(x.text!==p.originalKo)throw Error('Original text changed');if(p.move[0]<x.sourceSampleRange[0]/24000-c.sourceFrom||p.move[1]>x.sourceSampleRange[1]/24000-c.sourceFrom)throw Error('Complete original motion must fit source sample interval');}
const record={schemaVersion:1,preparedAt:new Date().toISOString(),timeline:{path:timelinePath,sha256:sha(timelinePath)},originalData:{path:dataPath,sha256:sha(dataPath)},clips,
 noCaptions:true,noAudio:true,rendered:false,finalUseApproved:false,allOriginalExplanationContentPreserved:true,originalVoiceChanged:false};
fs.writeFileSync(path.join(root,outputPath),JSON.stringify(record,null,2)+'\n');
const files=[outputPath,spatial+'/retained-clean-runtime-v1.tsx'];
for(let i=0;i<data.chapters.length;i++){
 const c=data.chapters[i],selected=clips.filter(x=>x.chapterIndex===i),frames=selected.reduce((n,x)=>n+x.frames,0),name='retained-clean-'+c.scene+'-v1',scene=spatial+'/'+name+'.tsx',projectFile=spatial+'/'+name+'-project.ts',meta=spatial+'/'+name+'-project.meta';
 if(!selected.length)continue;
 for(const f of [scene,projectFile,meta])if(fs.existsSync(path.join(root,f)))throw Error('Preserve existing '+f);
 fs.writeFileSync(path.join(root,scene),"import {retainedCleanChapterV1} from './retained-clean-runtime-v1';\nexport default retainedCleanChapterV1("+i+");\n");
 fs.writeFileSync(path.join(root,projectFile),"import {makeProject} from '@motion-canvas/core';\nimport scene from './"+name+"?scene';\nexport default makeProject({scenes:[scene]});\n");
 fs.writeFileSync(path.join(root,meta),JSON.stringify({version:0,shared:{background:null,range:[0,frames/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:false}}}},null,2)+'\n');
 files.push(scene,projectFile,meta);
}
const out=project+'/production/retained-clean-scene-preparation-v1.json';
fs.writeFileSync(path.join(root,out),JSON.stringify({schemaVersion:1,preparedAt:new Date().toISOString(),files:files.map(p=>({path:p,sha256:sha(p)})),explanationFrames:37244,completeExplanationParagraphs:47,
 generatedSceneCodeOnly:true,newImages:0,newMedia:0,actualRenderingStarted:false,allPixelsApproved:false,finalTimelineAdopted:false},null,2)+'\n');
console.log(JSON.stringify({out,files:files.length,frames:37244,newMedia:0,rendered:false}));
