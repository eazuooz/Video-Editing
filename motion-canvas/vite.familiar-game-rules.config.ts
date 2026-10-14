import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {appendFileSync} from 'node:fs';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
// Scope the exporter resource cap and command log to this Vite process.
const require=createRequire(import.meta.url);
const {FFmpegExporterServer}=require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
if(!FFmpegExporterServer.prototype.familiarThreadsCapped){
  const start=FFmpegExporterServer.prototype.start;
  FFmpegExporterServer.prototype.start=async function(...args:any[]){
    this.command.outputOptions(['-threads 2','-filter_threads 1']);
    this.command.on('start',(commandLine:string)=>appendFileSync(fileURLToPath(new URL('../projects/familiar-game-rules/production/timed-white-exporter-v1.jsonl',import.meta.url)),JSON.stringify({observedAt:new Date().toISOString(),vitePid:process.pid,commandLine})+'\n'));
    return start.apply(this,args);
  };
  FFmpegExporterServer.prototype.familiarThreadsCapped=true;
}
export default defineConfig({
  server:{host:'127.0.0.1',port:9224,strictPort:true,
    fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},
    watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/*.webm','**/.runtime/**']},
  },
  plugins:[ffmpeg(),motionCanvas({project:[
    './src/projects/familiar-game-rules/timed-white-reel-project-v1.ts',
  ],output:'../shared/output/motion-canvas'})],
});
