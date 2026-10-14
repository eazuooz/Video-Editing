const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),old='production/research/game-lighting-history/local/part1-capacity-review-v183',out='production/research/game-lighting-history/local/part1-safe-capacity-review-v189';
const p=JSON.parse(fs.readFileSync(path.join(root,old,'plan.json'),'utf8')),before=JSON.stringify(p.rows).replaceAll('<','\\u003c');
const ranges={'geometry-barrier-debug':[[96,135.3]],'geometry-courtyard-mask':[[180,217.8]],'mobile-texture-group':[[0,17.9]],'mobile-device-profile':[[28,51.5]],'mobile-compiler-warning':[[132,150]],'fortnite-mobile-profiling':[[263,283]],'rivalry-mobile-lighting':[[26,41],[51,90]],'outer-generated-display':[[0,16.4]],'cyber-light-reconstruction':[[44,63.5]]};
for(const r of p.rows){r.ranges=ranges[r.id];r.capacityExtensionApproved=false;r.wholeMotionReviewed=false;r.exactCropApproved=false;r.finalNativeUseApproved=false;}
p.preparedAt=new Date().toISOString();p.scope='Safe normal-speed candidates after directly observed title/presenter transitions. Fortnite source263–283 contains wall/rock/wall diagnostic route; preserve full narration, inspect chronology before selection.';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve viewer');fs.mkdirSync(path.join(root,out),{recursive:true});
fs.writeFileSync(path.join(root,out,'index.html'),fs.readFileSync(path.join(root,old,'index.html'),'utf8').replace(before,JSON.stringify(p.rows).replaceAll('<','\\u003c')));
fs.writeFileSync(path.join(root,out,'plan.json'),JSON.stringify(p,null,2)+'\n');
console.log(JSON.stringify({viewer:out+'/index.html',images:0,approved:false}));
