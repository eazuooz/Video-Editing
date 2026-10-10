const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2],scene=process.argv[3];
if(!['game-lighting-history-03','game-lighting-history-04'].includes(slug)||!/^\w+$/.test(scene||''))throw Error('Explicit current scene required');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=read(`projects/${slug}/project.json`),voicePath=manifest.paths.narration,b=fs.readFileSync(path.join(root,voicePath));
let fmt,data;for(let at=12;at+8<=b.length;){const size=b.readUInt32LE(at+4),tag=b.toString('ascii',at,at+4);if(tag==='fmt ')fmt={format:b.readUInt16LE(at+8),channels:b.readUInt16LE(at+10),rate:b.readUInt32LE(at+12),block:b.readUInt16LE(at+20),bits:b.readUInt16LE(at+22)};if(tag==='data'){data={at:at+8,bytes:size};break;}at+=8+size+(size%2);}
if(!fmt||!data||fmt.format!==1||fmt.bits!==16||fmt.channels!==1)throw Error('Reviewed PCM16 mono contract required');
const whole=read(`projects/${slug}/production/local/voice-asr-v2/whole-${scene}.json`),context=read(`projects/${slug}/production/local/voice-asr-v2/context-${scene}.json`);
if(sha(b)!==whole.audioSha256||context.audioSha256!==whole.audioSha256)throw Error('Current audio mismatch');
function stats(from,to){const a=Math.max(0,Math.round(from*fmt.rate)),z=Math.min(data.bytes/fmt.block,Math.round(to*fmt.rate));let sum=0,peak=0,nonzero=0;for(let i=a;i<z;i++){const x=b.readInt16LE(data.at+i*fmt.block)/32768;sum+=x*x;peak=Math.max(peak,Math.abs(x));nonzero+=Number(x!==0);}const n=z-a,rms=Math.sqrt(sum/Math.max(n,1));return{fromSeconds:a/fmt.rate,toSeconds:z/fmt.rate,samples:n,nonzero,rms,peak,rmsDbfs:rms?20*Math.log10(rms):null,sha256:sha(b.subarray(data.at+a*fmt.block,data.at+z*fmt.block))};}
const end=whole.sourceToSeconds,start=whole.sourceFromSeconds;
const windows=[stats(end-1,end-.5),stats(end-.5,end-.3),stats(end-.3,end-.1),stats(end-.1,end)];
const suspicious=context.chunks.filter(c=>c.timestamp?.[0]>=end-context.sourceFromSeconds-.3).map(c=>({text:c.text,timestamp:c.timestamp,pcm:stats(context.sourceFromSeconds+c.timestamp[0],context.sourceFromSeconds+(c.timestamp[1]??c.timestamp[0]))}));
const record={checkedAt:new Date().toISOString(),voice:{path:voicePath,sha256:sha(b),...fmt},scene,startSeconds:start,endSeconds:end,tailWindows:windows,contextTailTokens:suspicious,wholeLastTokens:whole.chunks.slice(-16),interpretation:'PCM energy and collapsed token durations are evidence about this exact interval, not a replacement for human listening or approval of the entire voice.',humanWholeListeningApproved:false,humanPronunciationApproved:false,currentNarrationApproved:false};
const out=`projects/${slug}/production/local/voice-asr-v2/tail-pcm-${scene}.json`;fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify(record,null,2));
