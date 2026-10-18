import {defineConfig,searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({server:{host:'127.0.0.1',port:9245,strictPort:true,fs:{allow:[searchForWorkspaceRoot(process.cwd()),'D:/Github/VideoEditing/projects/shorts-forgiving-hitbox/production/local']}},plugins:[ffmpeg(),motionCanvas({project:['./src/projects/shorts-forgiving-hitbox-fairness60/project.ts'],output:'../shared/output/motion-canvas'})]});
