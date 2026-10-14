const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const previous=base+'native-source-observation-v5.json',output=base+'native-source-observation-v6.json';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
if(fs.existsSync(path.join(root,output)))throw Error('Existing direct observation record preserved');
const old=JSON.parse(fs.readFileSync(path.join(root,previous),'utf8'));
const rd='production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4';
const vsm='production/research/game-lighting-history/local/episode04-native-v1/virtual-shadow-editor-2024.mp4';
old.previousEvidence={path:previous,sha256:sha(previous)};old.reviewedAt=new Date().toISOString();
old.observations.push(
 {source:'own-renderdoc-capture',path:rd,sha256:sha(rd),requestedRange:[35,80],observedTimes:[35.074,80.04],action:'Frame622/EID14 triangle draw reaches MeshViewer vertex input/output table and Debug this Vertex menu. This is distinct from the preceding EID11clear-only window.',limits:'No inference about an Unreal GBuffer or complex lighting; exact panel crop and fixed-caption clearance remain pending.'},
 {source:'own-renderdoc-capture',path:rd,sha256:sha(rd),requestedRange:[80,125],observedTimes:[80,125.259],action:'Recorded shader debugging reaches return input.color. At125.259COLORinput is(.96125,.01312,.02562,1); SV_Target/main return remain(0,0,0,0)before the step.',limits:'Do not treat the zero-before value as the final returned color. Source-request offset526has not independently been aligned.'},
 {source:'own-renderdoc-capture',path:rd,sha256:sha(rd),requestedRange:[125,133.016],observedTimes:[125,133.017],action:'Normal-speed original recording steps return input.color; final displayed SV_Target/main return match(.96125,.01312,.02562,1). SameFrame622/EID14is retained.',limits:'Input and output tables lie low in the original frame; final framing must make both readable above fixed captions. No new crop/extract/render approved.'},
 {source:'virtual-shadow-editor-2024',path:vsm,sha256:sha(vsm),requestedRange:[104,151],observedTimes:[113.118085,118.384,139.913,140.19,151.074],action:'Selected Shadow.Virtual.PhysicalPagePool is Texture512MB in initial table. Console autocomplete shows r.Shadow.Virtual.MaxPhysicalPages but the applied numeric value was not directly read. At151.074refreshed selected row reads Texture256MB, Resident|UAV; source totals43197resources/8379MB.',limits:'512→256is displayed resource-size evidence, not total-VRAM/FPS/quality proof. Do not invent an applied command value or confuse camera/cloud changes with a controlled shadow test. Console is near caption region and needs a suitable source layout.'}
);
old.newRasterImages=0;old.newMedia=0;old.allFinalAnnotationPixelsReviewed=false;old.finalTimingApproved=false;old.approvedActualFootageFrames=0;
fs.writeFileSync(path.join(root,output),JSON.stringify(old,null,2)+'\n');console.log(JSON.stringify({record:output,observations:old.observations.length,sourceShaVerified:true,newImages:0,newMedia:0,finalTimingApproved:false}));
