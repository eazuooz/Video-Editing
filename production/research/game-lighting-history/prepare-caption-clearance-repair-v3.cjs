const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/game-lighting-history-03/production', spatial = 'motion-canvas/src/projects/game-lighting-history-03/spatial';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const write = (p, value) => { if (fs.existsSync(path.join(root, p))) throw Error('Preserve existing ' + p); fs.writeFileSync(path.join(root, p), value); };
const progressPath = base + '/encoded-pixel-direct-progress-v15.json';
const progress = read(progressPath);
if (progress.records.length !== 307 || progress.allFinalPixelsReviewed) throw Error('All307 directly read failed-QA boards required');
const source = spatial + '/retained-clean-data-v2.json', originalData = spatial + '/narrated-data-v3.json';
const ids = ['original-39','original-40','original-44','original-45','original-46','original-47','original-48','original-52','original-53','original-54','original-56','original-57','original-58','original-59','original-60','original-65','original-81-explanation'];
const selected = read(source).clips.filter(c => ids.includes(c.id));
if (selected.length !== ids.length) throw Error('Exact17 affected explanations required');
let frames = 0;
const clips = selected.map(c => { const result = {...c, repairFromFrame:frames, modelShiftY:c.id === 'original-65' ? 0 : -65}; frames += c.frames; return {...result,repairToFrame:frames}; });
const dataPath = spatial + '/caption-clearance-repair-data-v3.json';
write(dataPath, JSON.stringify({preparedAt:new Date().toISOString(),clips,frames,source:{path:source,sha256:sha(source)},originalData:{path:originalData,sha256:sha(originalData)},directReview:{path:progressPath,sha256:sha(progressPath)},changedNarration:false,changedCaptions:false,allFinalPixelsReviewed:false},null,2)+'\n');
// Version the explanatory model rather than changing old approved inputs.
const naniteSource = spatial + '/nanite-model-v1.tsx';
let nanite = fs.readFileSync(path.join(root,naniteSource),'utf8');
nanite = nanite.replace('export function naniteModel()', 'export function naniteModelV2()')
 .replace('d = ${distance().toFixed(1)} m','d ≈ ${distance().toFixed(1)} m')
 .replace('화면 오차: ${error().toFixed(2)} px','화면 오차 ≈ ${error().toFixed(2)} px')
 .replace('핀홀 근사 계산 · 실제 Nanite 선택 규칙의 전부가 아님','표시값 반올림 · 핀홀 근사 · 실제 Nanite 선택 규칙의 전부가 아님');
if(nanite === fs.readFileSync(path.join(root,naniteSource),'utf8'))throw Error('Precision repair missing');
write(spatial+'/nanite-model-v2.tsx',nanite);
const name = 'caption-clearance-repair-v3-project';
write(spatial+'/'+name+'.ts',"import {makeProject} from '@motion-canvas/core';\nimport scene from './caption-clearance-repair-v3?scene';\nexport default makeProject({scenes:[scene]});\n");
write(spatial+'/'+name+'.meta',JSON.stringify({version:0,shared:{background:null,range:[0,(frames-1)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:60,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:false}}}},null,2)+'\n');
const configPath = 'motion-canvas/vite.game-lighting-history.chapter-v4.config.ts';
let config = fs.readFileSync(path.join(root,configPath),'utf8');
const projectPath = './src/projects/game-lighting-history-03/spatial/'+name+'.ts';
if(config.includes(projectPath))throw Error('Already registered');
config = config.replace('project:[','project:['+JSON.stringify(projectPath)+',');
fs.writeFileSync(path.join(root,configPath),config);
const files = [dataPath,naniteSource,spatial+'/nanite-model-v2.tsx',spatial+'/caption-clearance-repair-v3.tsx',spatial+'/'+name+'.ts',spatial+'/'+name+'.meta',originalData,spatial+'/ddgi-model-v1.tsx',spatial+'/restir-model-v2.tsx',spatial+'/culling-model-v3.tsx',spatial+'/pipeline-model-v1.tsx',spatial+'/cache-model-v1.tsx'];
write(base+'/caption-clearance-repair-plan-v3.json',JSON.stringify({preparedAt:new Date().toISOString(),name,frames,clips,inputs:files.map(p=>({path:p,sha256:sha(p)})),sourceReview:{path:progressPath,sha256:sha(progressPath)},output:'production/research/game-lighting-history/local/episode03-chapter-render-v4/renders/'+name+'.mp4',execution:'production/research/game-lighting-history/local/episode03-chapter-render-v4/renders/'+name+'.execution.json',cpuThreads:2,gpuJobs:0,noAudio:true,noCaptions:true,geometryPreserved:true,modelsTranslatedWithinExplanation:true,fixedCaptionsUnchanged:true,originalMediaPreserved:true,rendered:false,allFinalPixelsReviewed:false,collected:false,uploaded:false},null,2)+'\n');
console.log(JSON.stringify({clips:clips.length,frames,seconds:frames/60,newImages:0,newMedia:0,rendered:false}));
