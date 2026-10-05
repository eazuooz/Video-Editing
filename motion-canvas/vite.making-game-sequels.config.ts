import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({
  server:{host:'127.0.0.1',port:9222,strictPort:true,
    fs:{allow:[fileURLToPath(new URL('..',import.meta.url))]},
    watch:{ignored:['**/*.wav','**/*.m4a','**/*.mp4','**/*.webm','**/.runtime/**']},
  },
  plugins:[ffmpeg(),motionCanvas({project:[
    './src/projects/making-game-sequels/lookdev-project.ts',
    './src/projects/making-game-sequels/project.ts',
  ],output:'../shared/output/motion-canvas'})],
});
