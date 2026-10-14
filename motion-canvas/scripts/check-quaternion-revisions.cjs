// Isolated target checks preserve the shared catalogue and foreign projects.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');const slugs=['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2'];
const config=path.join(root,'.quaternion-revision-tsconfig.json');
fs.writeFileSync(config,JSON.stringify({extends:'./tsconfig.json',include:['src/env.d.ts',...slugs.flatMap(s=>[`src/projects/${s}/**/*.ts`,`src/projects/${s}/**/*.tsx`])]},null,2)+'\n');
const args=[path.join(root,'node_modules/typescript/bin/tsc'),'--project',config];
let result=cp.spawnSync(process.execPath,args,{cwd:root,stdio:'inherit',windowsHide:true});if(result.status!==0)process.exit(result.status||1);
if(process.argv.includes('--build')){
 const vite=path.join(root,'.quaternion-revision-vite.config.ts');
 fs.writeFileSync(vite,`import {defineConfig} from 'vite';\nimport mcPlugin from '@motion-canvas/vite-plugin';\nconst mc=(mcPlugin as any).default??mcPlugin;\nexport default defineConfig({build:{outDir:'../shared/output/game-math-part2-teaching-revision/editor-build'},plugins:[mc({project:${JSON.stringify(slugs.map(s=>'./src/projects/'+s+'/project.ts'))},output:'../shared/output/motion-canvas'})]});\n`);
 result=cp.spawnSync(process.execPath,[path.join(root,'node_modules/vite/bin/vite.js'),'build','--config',vite],{cwd:root,stdio:'inherit',windowsHide:true});if(result.status!==0)process.exit(result.status||1);
}
console.log('The two quaternion editors passed the requested targeted checks. Actual editor playback remains separate.');
