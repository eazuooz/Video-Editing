import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
const sceneProjects=Array.from({length:28},(_,i)=>`./src/projects/ai-game-development-human-craft/scenes/${String(i+1).padStart(2,'0')}/project.ts`);
export default defineConfig({server:{host:'127.0.0.1',port:9199,strictPort:true,fs:{allow:['..']}},plugins:[ffmpeg(),motionCanvas({project:['./src/projects/ai-game-development-human-craft/project.ts','./src/projects/ai-game-development-human-craft/member-project.ts',...sceneProjects],output:'../shared/output/motion-canvas'})]});
