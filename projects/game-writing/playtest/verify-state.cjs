const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {create,act}=require('./story-state.cjs');
const results=[];
function run(name,actions,check){let s=create();for(const a of actions)s=act(s,a);check(s);results.push({name,actions,state:s});return s;}
const ids=s=>s.dialogue.choices.map(c=>c[0]);
run('reading does not share the rule',['start-skip','read-note','talk-guard'],s=>{
 assert.equal(s.noteKnown,true);assert.equal(s.sharedRule,false);assert.equal(s.lastLineId,'guard.first');assert(ids(s).includes('share-rule'));
});
run('shared rule continues instead of introductory claim',['read-note','talk-guard','share-rule','talk-guard'],s=>{
 assert.equal(s.sharedRule,true);assert.equal(s.lastLineId,'guard.rule-shared');assert(!ids(s).includes('share-rule'));
});
run('unlearned knowledge cannot be reported',['start-skip','share-rule'],s=>{
 assert.equal(s.sharedRule,false);assert.equal(s.events.at(-1).accepted,false);
});
run('known introduction offers a short confirmation without inventing a board visit',['start-read','close','talk-guard'],s=>{
 assert.equal(s.introRead,true);assert.equal(s.noteKnown,false);assert.equal(s.sharedRule,false);
 assert(ids(s).includes('confirm-known-rule'));assert(!ids(s).includes('share-rule'));assert(!s.dialogue.text.includes('규칙은 이미'));
 const next=act(s,'confirm-known-rule');assert.equal(next.sharedRule,true);assert.equal(next.lastLineId,'guard.known-confirmed');
});
run('skipping introduction cannot confirm an unlearned rule',['start-skip','confirm-known-rule'],s=>{
 assert.equal(s.introRead,false);assert.equal(s.sharedRule,false);assert.equal(s.events.at(-1).accepted,false);
});
run('present companion may present its own seal',['take-seal','give-companion','talk-guard','present-seal'],s=>{
 assert.equal(s.gateOpen,true);assert.equal(s.sealOwner,'guard');
});
run('absent owner cannot present; recovery restores access',['take-seal','give-companion','rest-companion','talk-guard'],s=>{
 assert(!ids(s).includes('present-seal'));const denied=act(s,'present-seal');assert.equal(denied.gateOpen,false);assert.equal(denied.events.at(-1).accepted,false);
 const recovered=act(act(s,'recover-seal'),'talk-guard');assert(ids(recovered).includes('present-seal'));assert.equal(recovered.sealOwner,'player');
});
for(const route of ['feed','detour','drive'])run(`branch ${route} rejoins without resetting consequences`,['road',route,'take-seal','talk-guard','present-seal','enter-harbor'],s=>{
 assert.equal(s.arrived,true);assert.equal(s.route,route);assert.equal(s.rations,route==='feed'?0:1);assert.equal(s.minutes,route==='detour'?3:1);
});
run('skip path exposes a recoverable essential fact',['start-skip','talk-guard'],s=>{
 assert.equal(s.introRead,false);assert(s.dialogue.text.includes('証')||s.dialogue.text.includes('증표'));assert(ids(s).includes('ask-rule'));
 const n=act(s,'ask-rule');assert(n.dialogue.text.includes('등대 보관함'));assert.equal(n.sharedRule,true);
});
run('expected-order path completes',['start-read','close','read-note','close','take-seal','close','road','feed','close','talk-guard','present-seal','enter-harbor'],s=>assert.equal(s.arrived,true));
run('cannot replay an encounter to overwrite its past',['road','feed','detour'],s=>{assert.equal(s.route,'feed');assert.equal(s.minutes,1);assert.equal(s.events.at(-1).accepted,false);});
// Exhaustive reachable fact graph: every displayed option has a valid outcome.
const actions=['read-note','talk-guard','ask-rule','share-rule','confirm-known-rule','ask-seal','take-seal','give-companion','rest-companion','call-companion','recover-seal','road','feed','detour','drive','present-seal','enter-harbor','close'];
const factKeys=['started','introRead','noteKnown','sharedRule','sealOwner','companionPresent','route','rations','minutes','gateOpen','arrived','lastLineId'];
const signature=s=>JSON.stringify([...factKeys.map(k=>s[k]),s.dialogue?.id||null]);
const seen=new Set(),work=[create()];let optionsChecked=0;
while(work.length){const s=work.pop(),key=signature(s);if(seen.has(key))continue;seen.add(key);
 if(s.gateOpen)assert.equal(s.sealOwner,'guard');
 if(s.arrived)assert.equal(s.gateOpen,true);
 if(s.sharedRule)assert(s.events.some(e=>['share-rule','ask-rule','confirm-known-rule'].includes(e.action)));
 if(s.dialogue)for(const [a] of s.dialogue.choices){const next=act(s,a);assert.equal(next.events.at(-1).accepted,true,`${s.lastLineId}: invalid displayed ${a}`);optionsChecked++;}
 for(const a of s.started?actions:['start-read','start-skip']){const n=act(s,a);if(n.events.at(-1).accepted&&!seen.has(signature(n)))work.push(n);}
}
const proof={generatedAt:new Date().toISOString(),kind:'technical narrative-state verification, not human enjoyment or comprehension review',passed:true,cases:results.length,reachableFactStates:seen.size,displayedOptionsChecked:optionsChecked,results};
fs.mkdirSync(path.resolve(__dirname,'../production'),{recursive:true});
fs.writeFileSync(path.resolve(__dirname,'../production/playtest-state-proof.json'),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({passed:true,cases:results.length,reachableFactStates:seen.size,displayedOptionsChecked:optionsChecked}));
