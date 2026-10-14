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
const guard=Symbol.for('game-lighting-history-black-v2-cpu-export-options');
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
 const record=fileURLToPath(new URL('../production/research/game-lighting-history/local/current-render-execution-v1.json',import.meta.url));
 const observed:any={startedAt:new Date().toISOString(),serverPid:process.pid,cwd:process.cwd(),status:'starting',cpuThreads:2,gpuJobs:0};
 const write=()=>fs.writeFileSync(record,JSON.stringify(observed,null,2)+'\n');
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
 plugins:[ffmpeg(),motionCanvas({project:['./src/projects/game-lighting-history-01/black-lookdev-v2/project.ts','./src/projects/game-lighting-history-03/spatial/project.ts','./src/projects/game-lighting-history-03/spatial/ddgi-project.ts','./src/projects/game-lighting-history-03/spatial/restir-project.ts','./src/projects/game-lighting-history-03/spatial/narrated-project-v1.ts','./src/projects/game-lighting-history-03/spatial/engine-project-v1.ts','./src/projects/game-lighting-history-03/spatial/cache-project-v1.ts','./src/projects/game-lighting-history-03/spatial/narrated-project-v2.ts','./src/projects/game-lighting-history-03/spatial/work-project-v1.ts','./src/projects/game-lighting-history-03/spatial/work-project-v2.ts','./src/projects/game-lighting-history-03/spatial/foundation-project-v1.ts','./src/projects/game-lighting-history-03/spatial/foundation-fix-project-v2.ts','./src/projects/game-lighting-history-03/spatial/foundation-fix-project-v3.ts','./src/projects/game-lighting-history-03/spatial/foundation-fix-project-v4.ts','./src/projects/game-lighting-history-03/spatial/narrated-project-v3.ts'],
 output:'../production/research/game-lighting-history/local/black-proof-v3'})]});
