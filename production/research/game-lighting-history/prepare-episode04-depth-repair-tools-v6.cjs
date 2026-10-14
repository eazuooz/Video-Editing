// Reuse inspected source-render guards for the three explicit v6 repairs.
const fs=require('fs');
const replacements=[
 ['motion-canvas/vite.game-lighting-history04.clean-inputs-v5.config.ts','motion-canvas/vite.game-lighting-history04.depth-repairs-v6.config.ts'],
 ['production/research/game-lighting-history/verify-episode04-clean-input-v5.cjs','production/research/game-lighting-history/verify-episode04-depth-repair-v6.cjs'],
 ['production/research/game-lighting-history/extract-episode04-clean-input-qa-v5.py','production/research/game-lighting-history/extract-episode04-depth-repair-qa-v6.py']
];
for(const [from,to] of replacements){
 if(fs.existsSync(to))throw Error('Preserve prepared repair tools');
 let source=fs.readFileSync(from,'utf8');
 source=source.replaceAll('episode04-clean-model-inputs-v5','episode04-depth-repairs-v6').replaceAll('game-lighting-history04-clean-inputs-v5-cpu-options','game-lighting-history04-depth-repairs-v6-cpu-options');
 if(from.endsWith('.config.ts'))source=source.replace('port:9265','port:9266');
 fs.writeFileSync(to,source);
}
console.log(JSON.stringify({preparedTools:3,renderStarted:false,newTts:0,final:false}));
