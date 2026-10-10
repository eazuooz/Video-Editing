const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const slug='game-lighting-history-03',manifest=read(`projects/${slug}/project.json`),audio=manifest.productionState.generatedNarration;
if(sha(audio.path)!==audio.sha256)throw Error('Current narration changed');
const rel='production/research/game-lighting-history/local/spatial-narrated-rehearsal-v1';
if(fs.existsSync(path.join(root,rel,'plan.json')))throw Error('Existing rehearsal preserved');
fs.mkdirSync(path.join(root,rel),{recursive:true});
const specs=[
{scene:'13a',model:'bvh',proof:'bvh-animated-proof-review-v3.json',pairs:[[0,1],[1,2],[1,3],[4,5],[1,6],[1,7],[1,8],[1,9]],moves:[[3.06,7.84],[17.64,22.28],[27.22,33.04],[49.06,53.40],[60.38,63.38],[71.80,76.88],[79.92,84.18],[98.18,103.34]]},
{scene:'15a',model:'ddgi',proof:'ddgi-animated-proof-review-v2.json',pairs:[[0,1],[2,3],[0,4],[4,5],[6,7],[8,9]],moves:[[4,7.50],[20.58,24.78],[25.26,30.18],[46,48.48],[51.82,54.16],[65.74,70.86]]},
{scene:'15b',model:'restir',proof:'restir-animated-proof-review-v2.json',pairs:Array.from({length:7},(_,i)=>[i*2,i*2+1]),moves:[[4.82,11.48],[19.36,26.30],[34.16,39.72],[45.54,50.50],[54.56,58.40],[66.52,69.30],[79.86,83.74]]}
];
// Typography wrapping is independent from timing. Original KO words are kept.
const width=s=>Array.from(s).reduce((n,c)=>n+(/[\x00-\x7f]/.test(c)?.5:1),0);
function wrap(words){const lines=[''];for(const w of words){const i=lines.length-1;if(width(lines[i]+(lines[i]?' ':'')+w)>28&&lines[i])lines.push(w);else lines[i]+=(lines[i]?' ':'')+w;}if(lines.length>2)throw Error('Caption exceeds two lines');return lines.join('\n');}
const aliases=[['비브이에이치','bvh'],['디디지아이','ddgi'],['지아이','gi'],['이천십팔','2018'],['이천이십','2020']];
function norm(s){for(const[a,b]of aliases)s=s.replaceAll(a,b);return s.toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');}
// Edit alignment maps original caption characters to independently recognized
// word intervals. It records substitutions/gaps for direct review, never approval.
function alignment(original,recognized){const a=Array.from(norm(original)),b=[];recognized.forEach((w,i)=>Array.from(norm(w.text)).forEach(c=>b.push({c,i})));const rows=Array.from({length:a.length+1},()=>new Uint16Array(b.length+1));for(let i=0;i<=a.length;i++)rows[i][0]=i;for(let j=0;j<=b.length;j++)rows[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)rows[i][j]=Math.min(rows[i-1][j]+1,rows[i][j-1]+1,rows[i-1][j-1]+(a[i-1]===b[j-1].c?0:1));let i=a.length,j=b.length;const mapping=Array(a.length).fill(null);while(i||j){if(i&&j&&rows[i][j]===rows[i-1][j-1]+(a[i-1]===b[j-1].c?0:1)){mapping[i-1]=b[j-1].i;i--;j--;}else if(i&&rows[i][j]===rows[i-1][j]+1)i--;else j--;}return{mapping,editDistance:rows[a.length][b.length],originalCharacters:a.length,recognizedCharacters:b.length};}
let offset=0;const chapters=[];
for(const spec of specs){const proof=read(`projects/${slug}/production/${spec.proof}`);if(!proof.modelMotionProofReviewed)throw Error('Model motion not reviewed');
const resultPath=`projects/${slug}/production/local/voice-asr-v2/whole-${spec.scene}.json`,r=read(resultPath);if(r.audioSha256!==audio.sha256||r.expectedTextUsedAsPrompt!==false)throw Error('ASR input mismatch');
const sentences=r.expectedKo.flatMap((p,paragraph)=>p.match(/[^.!?]+[.!?]/g).map(text=>({paragraph,text:text.trim()})));
const wordGroups=[];let group=[];for(const word of r.chunks){group.push(word);if(/[.!?]$/.test(word.text.trim())){wordGroups.push(group);group=[];}}if(group.length||wordGroups.length!==sentences.length)throw Error('Sentence boundaries need direct repair');
const cues=[],paragraphs=[];let cueId=0;
for(let s=0;s<sentences.length;s++){const sentence=sentences[s],words=wordGroups[s],map=alignment(sentence.text,words);const originalWords=sentence.text.split(/\s+/),parts=[];let part=[],used=0;
for(const w of originalWords){let fits=width([...part,w].join(' '))<=52;try{wrap([...part,w]);}catch{fits=false;}if(!fits&&part.length){parts.push({words:part,from:used-norm(part.join(' ')).length,to:used});part=[];}part.push(w);used+=norm(w).length;}if(part.length)parts.push({words:part,from:used-norm(part.join(' ')).length,to:used});
for(const part of parts){const matched=map.mapping.slice(part.from,part.to).filter(x=>x!==null);if(!matched.length)throw Error('Caption lacks recognition anchor');const lo=Math.min(...matched),hi=Math.max(...matched),from=words[lo].timestamp[0],to=words[hi].timestamp[1];if(!(to>from))throw Error('Degenerate caption');cues.push({id:++cueId,paragraph:sentence.paragraph,text:wrap(part.words),from,to,recognizerWordIndices:[lo,hi],sentence:s,alignment:{editDistance:map.editDistance,originalCharacters:map.originalCharacters,recognizedCharacters:map.recognizedCharacters},timingDirectlyReviewed:false,pixelsReviewed:false});}
}
for(let i=0;i<r.expectedKo.length;i++){const cs=cues.filter(c=>c.paragraph===i);paragraphs.push({index:i,originalKo:r.expectedKo[i],from:i===0?0:cs[0].from,to:i===r.expectedKo.length-1?r.sourceToSeconds-r.sourceFromSeconds:cues.find(c=>c.paragraph===i+1).from,pair:spec.pairs[i],move:spec.moves[i]});}
const chapter={scene:spec.scene,model:spec.model,sourceFrom:r.sourceFromSeconds,sourceTo:r.sourceToSeconds,duration:r.sourceToSeconds-r.sourceFromSeconds,timelineFrom:offset,wholeAsr:{path:resultPath,sha256:sha(resultPath)},paragraphs,cues,proofRecord:`projects/${slug}/production/${spec.proof}`};chapters.push(chapter);offset+=chapter.duration;
}
const plan={createdAt:new Date().toISOString(),scope:'Three complete chapter explanation rehearsals. All original current chapter PCM and KO arguments retained. No gameplay quota, final mix, full episode or private upload approval.',slug,style:'research-black-v1',audio,chapters,duration:offset,frames:Math.round(offset*60),allCaptionTimingsDirectlyReviewed:false,allRehearsalPixelsReviewed:false,finalVideoApproved:false,localOnly:true};
fs.writeFileSync(path.join(root,rel,'plan.json'),JSON.stringify(plan,null,2)+'\n');
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),out=path.join(root,rel,'narration.wav');
const graph=chapters.map((c,i)=>`[0:a]atrim=start=${c.sourceFrom.toFixed(8)}:end=${c.sourceTo.toFixed(8)},asetpts=PTS-STARTPTS[a${i}]`).join(';')+`;${chapters.map((_,i)=>`[a${i}]`).join('')}concat=n=${chapters.length}:v=0:a=1[out]`;
const args=['-hide_banner','-v','error','-threads','2','-i',path.join(root,audio.path),'-filter_complex_threads','2','-filter_complex',graph,'-map','[out]','-c:a','pcm_s16le',out];const rr=spawnSync(ffmpeg,args,{encoding:'utf8',windowsHide:true});if(rr.status!==0)throw Error(rr.stderr);
fs.writeFileSync(path.join(root,rel,'audio-build.json'),JSON.stringify({createdAt:new Date().toISOString(),command:[ffmpeg,...args],exitCode:rr.status,path:`${rel}/narration.wav`,sha256:sha(`${rel}/narration.wav`),finalMix:false},null,2)+'\n');
const dst='motion-canvas/src/projects/game-lighting-history-03/spatial';fs.writeFileSync(path.join(root,dst,'narrated-data-v1.json'),JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({plan:`${rel}/plan.json`,chapters:chapters.length,paragraphs:chapters.reduce((n,c)=>n+c.paragraphs.length,0),cues:chapters.reduce((n,c)=>n+c.cues.length,0),duration:offset,finalVideoApproved:false}));
