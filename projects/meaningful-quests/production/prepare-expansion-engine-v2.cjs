// Adapt the verified additive editor without running any completed project's helpers.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'projects/deconstruct-analyze-rebuild/production');
const files=['build-expansion-v2.cjs','render-recap-v2.cjs','review-expanded-sources.py','run-expansion-v2.cjs','run-expansion-render-v2.cjs','verify-expanded-v2.py','caption-expanded-v2.cjs'];
for(const file of files){
 const target=path.join(__dirname,file);if(fs.existsSync(target))throw Error('Preserve existing adapted engine: '+file);
 let source=fs.readFileSync(path.join(base,file),'utf8').replaceAll('deconstruct-analyze-rebuild','meaningful-quests').replaceAll('DECONSTRUCT_','MEANINGFUL_').replaceAll("['meat','hollow','portal']","['skyrim','subnautica']");
 source=source.replaceAll('게임 분석·재조립 — 원본 설명 보존·실제 선택 관찰 확장본','퀘스트 설계 — 원본 설명 보존·실제 행동 해설 확장본').replaceAll('Diagram-dominated original landing/retry/rule tests','Diagram-dominated original delivery/bridge/shortcut tests');
 if(file==='run-expansion-v2.cjs'){
  source=source.replace("every(x=>x.status==='completed')","every(x=>x.status==='complete-private-review')");
  source=source.replace("if(q.items.slice(0,i.order-1).every(x=>x.status==='complete-private-review'))q.currentSlug=i.slug;else q.preparationSlug=i.slug;","if(q.items.slice(0,i.order-1).every(x=>x.status==='complete-private-review'))q.currentSlug=i.slug;else q.preparationSlug=i.slug;q.nextAction='Review all 54 current-hash additional spoken lines, then build and inspect the extended 60:40 timeline; all original PPT and voice remain unchanged.';");
 }
 fs.writeFileSync(target,source);
}
const file=path.join(__dirname,'build-video.cjs');let source=fs.readFileSync(file,'utf8');
if(!source.includes("work=path.join(__dirname,'final-v1')"))throw Error('Original editor marker changed');
source=source.replace("work=path.join(__dirname,'final-v1')","work=path.join(__dirname,process.env.MEANINGFUL_REVISION||'final-v1')").replace("mf=path.join(root,'projects',slug,'project.json')","mf=path.resolve(root,process.env.MEANINGFUL_MANIFEST||`projects/${slug}/project.json`)");
fs.writeFileSync(file,source);
console.log('Additive engine adapted; original renderer, narration and completed projects were not executed.');
