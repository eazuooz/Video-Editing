// Independent source-boundary review; leaves active TTS inputs immutable.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const from='production/research/game-lighting-history/local/part1-extended-review-v170/index.html';
const dir='production/research/game-lighting-history/local/part1-boundary-review-v174';
const html=fs.readFileSync(path.join(root,from),'utf8');
const start=html.indexOf('const rows=')+'const rows='.length,end=html.indexOf(',pick=document.querySelector');
if(start<11||end<start)throw Error('Unknown viewer');
const rows=JSON.parse(html.slice(start,end));
const ranges={
 'shadow-moving-wheel':[[108,185.8]],
 'texture-stack-uv':[[90,126]],
 'texture-project-settings':[[242,272]],
 'tsr-moving-silhouette':[[0,40.5]],
 'tsr-rotating-vectors':[[0,35]],
 'fortnite-mobile-profiling':[[240,276]],
 'mobile-device-profile':[[30,50]],
 'mobile-lod-cvars':[[66,116]]
};
const selected=rows.filter(r=>r.id in ranges).map(r=>({...r,ranges:ranges[r.id],boundaryExtensionReviewed:false,finalNativeUseApproved:false}));
fs.mkdirSync(path.join(root,dir),{recursive:true});
for(const name of ['index.html','plan.json'])if(fs.existsSync(path.join(root,dir,name)))throw Error('Preserve existing viewer');
fs.writeFileSync(path.join(root,dir,'index.html'),html.slice(0,start)+JSON.stringify(selected)+html.slice(end));
fs.writeFileSync(path.join(root,dir,'plan.json'),JSON.stringify({preparedAt:new Date().toISOString(),sourceViewer:{path:from,sha256:crypto.createHash('sha256').update(html).digest('hex')},purpose:'Normal-speed boundary and framing review after measured guide durations; no source interval or gate is adopted automatically',rows:selected,ttsInputsChanged:false,newMediaExtracted:0,allDirectlyReviewed:false,allFinalPixelsReviewed:false,uploaded:false},null,2)+'\n');
console.log(JSON.stringify({viewer:dir+'/index.html',candidates:selected.length,TtsInputsChanged:false}));
