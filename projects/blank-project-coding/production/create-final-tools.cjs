const fs=require('fs'),path=require('path');const src=path.join(__dirname,'../../game-writing/production');
let build=fs.readFileSync(path.join(src,'build-final.cjs'),'utf8').replaceAll('game-writing','blank-project-coding');
const begin=build.indexOf("if(stage==='setup'){"),end=build.indexOf("}else if(stage==='mix'){");
const setup=`if(stage==='setup'){
 const explanations=plan.scenes.filter(s=>s.classification==='explanation');let start=2;for(const s of explanations){s.reelStart=start;start+=s.seconds;}
 plan.explanationReelFrames=120+plan.explanationFrames+600;write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);
 console.log('34 independent scenes use the measured current narration; final actual captures remain gated separately.');
`;
build=build.slice(0,begin)+setup+build.slice(end);
build=build.replace("Official English presenter/dialogue and any underlying music are omitted; own UI screencasts carry no audio.","All examples are owned silent executing-code/playtest screencasts.");
build=build.replace("const reel=abs('shared/output/motion-canvas/blank-project-coding-explanation-reel.mp4'),files=[];", "if(plan.scenes.some(s=>s.classification!=='explanation'&&!s.actualMediaVerified))throw Error('Final actual capture review required');\n const reel=abs('shared/output/motion-canvas/blank-project-coding-explanation-reel.mp4'),files=[];");
fs.writeFileSync(path.join(__dirname,'build-final.cjs'),build);
let reel=fs.readFileSync(path.join(src,'render-reel.cjs'),'utf8').replaceAll('game-writing','blank-project-coding').replace('127.0.0.1:9210','127.0.0.1:9342');fs.writeFileSync(path.join(__dirname,'render-reel.cjs'),reel);
let captions=fs.readFileSync(path.join(src,'caption-video.cjs'),'utf8').replaceAll('game-writing','blank-project-coding');
captions=captions.replace(/maxTextWidth:cuts\.some\([^\n]+?\?1236:1570/g,'maxTextWidth:1570');
captions=captions.replace('if(measure(text)>1050)','if(measure(text)>1570)');
captions=captions.replace(/const protectedRegions=\['gm','overview'\][^\n]+;/,"const protectedRegions=cut?[[0,0,1920,920]]:[[100,240,1820,883]];");
captions=captions.replace("placement:'All narration bottom-center960,970; official source actions recomposed above captions with source-filled blurred background'","placement:'Every burned narration cue fixed at bottom-center960,970; owned workbench controls composed above920px'");
captions=captions.replace(/   \/\/ The current channel rule[\s\S]+?   const protectedRegions=/,"   // Fixed caption center; recompose source UI instead of moving captions.\n   const protectedRegions=");
fs.writeFileSync(path.join(__dirname,'caption-video.cjs'),captions);
