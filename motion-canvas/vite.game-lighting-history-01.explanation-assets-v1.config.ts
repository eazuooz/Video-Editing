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
const guard=Symbol.for('game-lighting-history-01-explanation-assets-v1-cpu');
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
 const filename=path.basename((this as any).command._outputs[0].target).replace(/\.mp4$/,'.execution.json');
 const record=fileURLToPath(new URL('../projects/game-lighting-history-01/production/local/explanation-assets-v1/renders/'+filename,import.meta.url));
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
export default defineConfig({server:{host:'127.0.0.1',port:9272,strictPort:true,
 fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/local/**']}},
 plugins:[ffmpeg(),motionCanvas({project:["./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-01.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-02.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-03.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-04.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-04f.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-04t.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-07.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-08.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-09.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-09a.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-09b.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-10.ts", "./src/projects/game-lighting-history-01/explanation-assets-v1/explanation-24.ts"],
 output:'../projects/game-lighting-history-01/production/local/explanation-assets-v1/renders'})]});
