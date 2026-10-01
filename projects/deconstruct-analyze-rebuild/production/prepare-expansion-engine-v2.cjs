// Reuse the verified additive preservation/QA implementation with this project's inputs.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),source=path.join(root,'projects/counting-animation-frames/production');
function adapt(name,target,more=[]){
 let s=fs.readFileSync(path.join(source,name),'utf8').replaceAll('counting-animation-frames','deconstruct-analyze-rebuild').replaceAll('final-v3','final-v2').replaceAll('expanded-v3','expanded-v2').replaceAll('-v3','-v2').replaceAll('COUNTING_','DECONSTRUCT_');
 for(const [from,to] of more){if(!s.includes(from))throw Error('Template marker missing '+from);s=s.replaceAll(from,to);}
 fs.writeFileSync(path.join(__dirname,target),s);
}
adapt('build-expansion-v3.cjs','build-expansion-v2.cjs',[
 ["oldVoice=abs('shared/output/narration/deconstruct-analyze-rebuild/qwen3-1.7b-balanced-v1/deconstruct-analyze-rebuild-qwen3-1.7b-balanced-v1.wav')","oldVoice=abs(oldManifest.paths.narration)"],
 ["['megaman','rise']","['meat','hollow','portal']"],
 ["original.gameFrames=i===0?s.gameFrames:0","original.gameFrames=original.cuts.filter(c=>['meat','hollow','portal'].includes(c.key)).reduce((n,c)=>n+c.frames,0)"],
 ["url:`https://www.youtube.com/watch?v=${source.id}`","url:source.url"],
 ["Numeric/timeline-dominated executable frame labs count as explanation; only actual arena gameplay counts as footage.","Diagram-dominated original landing/retry/rule tests count as explanation; only preserved commercial play and fresh observable game actions count as actual footage."],
 ["60:40 actual arena footage / all explanations and diagram-like tests; 1-frame rounding","60:40 actual game actions / all preserved explanations and diagram-like tests; 1-frame rounding"],
 ["const ggst=['ky','sol'].includes(c.key)","const ggst=false"],
 ["x=${ggst?1000:500}:y=25:fontsize=${ggst?23:27}","x=${c.labelX??500}:y=${c.labelY??25}:fontsize=23"],
 ["name:'deconstruct-analyze-rebuild-expanded-recap'","name:'deconstruct-analyze-rebuild-expanded-recap'"],
 ["프레임 세기 — 원본 설명 보존·격투게임 해설 확장 검토본","게임 분석·재조립 — 원본 설명 보존·실제 선택 관찰 확장본"],
 ]);
adapt('render-recap-v3.cjs','render-recap-v2.cjs');
adapt('review-expanded-sources.py','review-expanded-sources.py');
adapt('run-expansion-render-v3.cjs','run-expansion-render-v2.cjs',[
 ["plan-preserved-originals-plus-spoken-fighting-insertions","plan-preserved-originals-plus-spoken-choice-and-result-insertions"],
 ["projects/deconstruct-analyze-rebuild/production/verify-video.py","projects/deconstruct-analyze-rebuild/production/verify-expanded-v2.py"],
 ["projects/deconstruct-analyze-rebuild/production/caption-video.cjs","projects/deconstruct-analyze-rebuild/production/caption-expanded-v2.cjs"]
 ]);
adapt('verify-video.py','verify-expanded-v2.py',[["['megaman','rise']","['meat','hollow','portal']"]]);
let old=fs.readFileSync(path.join(__dirname,'build-video.cjs'),'utf8');
if(!old.includes("work=path.join(__dirname,'final-v1')"))throw Error('Original work marker changed');
old=old.replace("work=path.join(__dirname,'final-v1')","work=path.join(__dirname,process.env.DECONSTRUCT_REVISION||'final-v1')");
old=old.replace("mf=path.join(root,'projects',slug,'project.json')","mf=path.resolve(root,process.env.DECONSTRUCT_MANIFEST||`projects/${slug}/project.json`)");
fs.writeFileSync(path.join(__dirname,'build-video.cjs'),old);
console.log('Additive engine prepared; no original renderer or narration was executed. Caption source placements still require their own review.');
