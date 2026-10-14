import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {FFmpegExporterServer}=require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
const start=FFmpegExporterServer.prototype.start;
const guard=Symbol.for('game-lighting-history-01-cpu-export-options');
if(!(FFmpegExporterServer.prototype as any)[guard]) FFmpegExporterServer.prototype.start=async function(){
  (this as any).command.outputOptions(['-threads 2','-preset veryfast','-crf 18','-video_track_timescale 90000']);
  return start.call(this);
};
(FFmpegExporterServer.prototype as any)[guard]=true;
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9264,strictPort:true,
  fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},
  watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/local/**']}},
  plugins:[ffmpeg(),motionCanvas({project:['./src/projects/game-lighting-history-01/lookdev/paragraph-fixes-v3/project.ts'],output:'../projects/game-lighting-history-01/production/local/scoped-lookdev-v3'})]});
