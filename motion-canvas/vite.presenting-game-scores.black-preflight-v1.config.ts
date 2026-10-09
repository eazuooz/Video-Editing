import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {FFmpegExporterServer}=require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
if(!FFmpegExporterServer.prototype.scorePreflightThreadsCapped){
 const originalStart=FFmpegExporterServer.prototype.start;
 FFmpegExporterServer.prototype.start=async function(){
  (this as any).command.outputOptions(['-threads 2','-filter_threads 1','-preset veryfast','-crf 18','-video_track_timescale 90000']);
  return originalStart.call(this);
 };
 FFmpegExporterServer.prototype.scorePreflightThreadsCapped=true;
}
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({
 server:{host:'127.0.0.1',port:9251,strictPort:true,
  fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},
  watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/*.webm','**/.runtime/**']}},
 plugins:[ffmpeg(),motionCanvas({project:['./src/projects/presenting-game-scores/black-explanation-preflight-v1.ts'],output:'../shared/output/presenting-game-scores/black-structural-preview-v1'})],
});
