import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const require=createRequire(import.meta.url);
const {FFmpegExporterServer}=require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
const start=FFmpegExporterServer.prototype.start;
const guard=Symbol.for('game-lighting-history-chapter-v4-cpu-export-options');
if(!(FFmpegExporterServer.prototype as any)[guard])FFmpegExporterServer.prototype.start=async function(){
 // The upstream exporter strips only the initial slash from /@fs/D:/... .
 // Normalize Vite's local-audio URL in this owned exporter, without changing
 // the dependency or other productions' audio handling.
 for(const input of (this as any).command._inputs){
  if(typeof input.source==='string'&&input.source.startsWith('@fs/')){
   const resolved=path.resolve(input.source.slice(4));
   const workspace=fileURLToPath(new URL('..',import.meta.url));
   if(!resolved.toLowerCase().startsWith(path.resolve(workspace).toLowerCase()+path.sep)||!fs.existsSync(resolved))throw Error('Unresolved workspace audio input');
   input.source=resolved;
  }
 }
 // Preserve rejection for end(), but avoid an unhandled rejection killing
 // this server before the browser can receive an exporter failure.
 (this as any).promise.catch(()=>{});
 const outputName=(this as any).command._outputs[0].target.split(/[\\/]/).pop();
 const isWordClock04=outputName.startsWith('episode04-word-clock-scope-v3');
 const isEpisode04=outputName.startsWith('additive-prerequisite')||isWordClock04;
 const proofFolder=isWordClock04?'episode04-word-clock-proof-v3':'episode04-prerequisite-proof-v1';
 if(isEpisode04){
  const destination=fileURLToPath(new URL('../production/research/game-lighting-history/local/'+proofFolder+'/'+outputName,import.meta.url));
  if(fs.existsSync(destination))throw Error('Preserve completed prerequisite proof: inspect before a scoped new version.');
  fs.mkdirSync(path.dirname(destination),{recursive:true});
  (this as any).command._outputs[0].target=destination;
 }
 const record=fileURLToPath(new URL('../production/research/game-lighting-history/local/'+(isWordClock04?'episode04-word-clock-render-execution-v3.json':isEpisode04?'episode04-prerequisite-render-execution-v1.json':'current-render-execution-v1.json'),import.meta.url));
 const observed:any={startedAt:new Date().toISOString(),serverPid:process.pid,cwd:process.cwd(),status:'starting',cpuThreads:2,gpuJobs:0};
 const chapterRecord=fileURLToPath(new URL('../production/research/game-lighting-history/local/'+(isEpisode04?proofFolder+'/':'episode03-chapter-render-v4/renders/')+outputName.replace(/\.mp4$/,'.execution.json'),import.meta.url));
 fs.mkdirSync(path.dirname(chapterRecord),{recursive:true});
 const write=()=>{fs.writeFileSync(record,JSON.stringify(observed,null,2)+'\n');fs.writeFileSync(chapterRecord,JSON.stringify(observed,null,2)+'\n');};
 (this as any).command.on('start',(command:string)=>{observed.command=command;observed.status='rendering';write();});
 (this as any).command.on('end',()=>{observed.status='complete';observed.exitCode=0;observed.completedAt=new Date().toISOString();write();});
 (this as any).command.on('error',(error:Error)=>{observed.status='failed';observed.error=error.message;observed.completedAt=new Date().toISOString();write();});
 (this as any).command.outputOptions(['-threads 2','-preset veryfast','-crf 18','-video_track_timescale 90000']);
 return start.call(this);
};
(FFmpegExporterServer.prototype as any)[guard]=true;
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9265,strictPort:true,
 fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},
 watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/local/**']}},
 plugins:[ffmpeg(),motionCanvas({project:["./src/projects/game-lighting-history-04/spatial/episode04-word-clock-scope-v3-project.ts","./src/projects/game-lighting-history-04/spatial/additive-prerequisite-capture-repair-v2-project.ts","./src/projects/game-lighting-history-04/spatial/additive-prerequisite-project-v1.ts","./src/projects/game-lighting-history-03/spatial/caption-clearance-repair-v3-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-overview-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-12a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-13a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-13b-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-14a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-14b-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-15a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-15b-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-16aa-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-16ab-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-16a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-17a-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-17b-v2-project.ts","./src/projects/game-lighting-history-03/spatial/retained-clean-conclusion-v2-project.ts","./src/projects/game-lighting-history-03/spatial/chapter-overview-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-12a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-13a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-13b-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-14a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-14b-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-15a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-15b-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-16aa-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-16ab-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-16a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-17a-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-17b-v4.ts","./src/projects/game-lighting-history-03/spatial/chapter-conclusion-v4.ts","./src/projects/game-lighting-history-04/spatial/vsm-project-v1.ts","./src/projects/game-lighting-history-04/spatial/upscaling-project-v1.ts","./src/projects/game-lighting-history-04/spatial/visibility-project-v1.ts","./src/projects/game-lighting-history-04/spatial/mobile-project-v1.ts","./src/projects/game-lighting-history-04/spatial/vsm-layout-project-v2.ts","./src/projects/game-lighting-history-04/spatial/upscaling-layout-project-v2.ts","./src/projects/game-lighting-history-03/spatial/caption-frame-boundary-project-v6.ts","./src/projects/game-lighting-history-04/spatial/path-budget-project-v1.ts","./src/projects/game-lighting-history-04/spatial/path-budget-layout-project-v2.ts","./src/projects/game-lighting-history-04/spatial/path-budget-layout-project-v3.ts","./src/projects/game-lighting-history-04/spatial/reconstruction-transparency-project-v1.ts","./src/projects/game-lighting-history-04/spatial/reconstruction-transparency-layout-project-v1.ts","./src/projects/game-lighting-history-04/spatial/reconstruction-transparency-peeling-project-v1.ts","./src/projects/game-lighting-history-04/spatial/megalights-dlss-project-v1.ts","./src/projects/game-lighting-history-03/spatial/temporal-pipeline-project-v1.ts","./src/projects/game-lighting-history-04/spatial/postprocess-inspection-project-v1.ts","./src/projects/game-lighting-history-04/spatial/postprocess-layout-project-v1.ts","./src/projects/game-lighting-history-04/spatial/postprocess-camera-project-v1.ts","./src/projects/game-lighting-history-03/spatial/rehearsal-layout-project-v1.ts"],
 output:'../production/research/game-lighting-history/local/episode03-chapter-render-v4/renders'})]});
