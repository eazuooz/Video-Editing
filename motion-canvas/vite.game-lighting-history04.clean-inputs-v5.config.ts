import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const workspace=path.resolve(fileURLToPath(new URL('..',import.meta.url)));
const base='production/research/game-lighting-history/local/episode04-clean-model-inputs-v5';
const plan=JSON.parse(fs.readFileSync(path.join(workspace,base,'plan.json'),'utf8'));
const allowed=new Map(plan.jobs.map((j:any)=>[j.name+'.mp4',j]));
const require=createRequire(import.meta.url);
const {FFmpegExporterServer}=require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
const original=FFmpegExporterServer.prototype.start;
const guard=Symbol.for('game-lighting-history04-clean-inputs-v5-cpu-options');
if(!(FFmpegExporterServer.prototype as any)[guard])FFmpegExporterServer.prototype.start=async function(){
 const command=(this as any).command;
 const name=command._outputs[0].target.split(/[\\/]/).pop(),job:any=allowed.get(name);
 if(!job)throw Error('This owned source renderer accepts only prepared episode04 input projects');
 const destination=path.join(workspace,job.output);
 if(fs.existsSync(destination))throw Error('Preserve completed input render: use observed verification or a scoped repair version');
 for(const input of command._inputs){
  if(typeof input.source==='string'&&input.source.startsWith('@fs/')){
   const resolved=path.resolve(input.source.slice(4));
   if(!resolved.toLowerCase().startsWith(workspace.toLowerCase()+path.sep)||!fs.existsSync(resolved))throw Error('Unresolved workspace PCM input');
   input.source=resolved;
  }
 }
 (this as any).promise.catch(()=>{});
 command._outputs[0].target=destination;
 fs.mkdirSync(path.dirname(destination),{recursive:true});
 const record=path.join(workspace,job.execution),observed:any={startedAt:new Date().toISOString(),serverPid:process.pid,cwd:process.cwd(),name,expectedFrames:job.frames,status:'starting',cpuThreads:2,gpuJobs:0,scope:'Complete paragraph model source render only. Final interleaving/mix/pixels/private are separate gates.'};
 const write=()=>fs.writeFileSync(record,JSON.stringify(observed,null,2)+'\n');
 command.on('start',(text:string)=>{observed.command=text;observed.status='rendering';observed.ffmpegPid=command.ffmpegProc?.pid??null;write();});
 command.on('end',()=>{observed.status='complete';observed.exitCode=0;observed.completedAt=new Date().toISOString();write();});
 command.on('error',(error:Error)=>{observed.status='failed';observed.error=error.message;observed.completedAt=new Date().toISOString();write();});
 command.outputOptions(['-threads 2','-preset veryfast','-crf 18','-video_track_timescale 90000',`-frames:v ${job.frames}`]);
 return original.call(this);
};
(FFmpegExporterServer.prototype as any)[guard]=true;
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin,ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9265,strictPort:true,fs:{allow:[workspace]},watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/local/**']}},plugins:[ffmpeg(),motionCanvas({project:plan.jobs.map((j:any)=>'./'+j.project.replace('motion-canvas/','')),output:'../'+base+'/renders'})]});
