import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9231,strictPort:true,fs:{allow:['D:/Github/VideoEditing']}},plugins:[ffmpeg(),motionCanvas({project:['./src/projects/avoid-game-comparisons/revision-v2/project.ts'],output:'../shared/output/motion-canvas'})]});
