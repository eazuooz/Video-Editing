import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default ?? ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9249,strictPort:true,
  fs:{allow:['..']}},plugins:[ffmpeg(),motionCanvas({
  project:['./src/projects/player-customization/final-review-project-v1.ts'],
  output:'../shared/output/motion-canvas'})]});
