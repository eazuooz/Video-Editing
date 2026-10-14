import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9198,strictPort:true,fs:{allow:['..']}},plugins:[ffmpeg(),motionCanvas({project:['./src/projects/ai-game-development-human-craft/unity-sample/project.ts'],output:'../shared/output/motion-canvas'})]});
