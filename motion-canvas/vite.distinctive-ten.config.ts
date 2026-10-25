import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {fileURLToPath} from 'node:url';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
const owned='C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025';
// Isolated finite-batch server. Existing preview servers and project registration stay unchanged.
export default defineConfig({server:{port:9267,strictPort:true,fs:{allow:[searchForWorkspaceRoot(process.cwd()),fileURLToPath(new URL('..',import.meta.url)),owned]}},plugins:[ffmpeg(),motionCanvas({project:['./src/projects/shorts-d2r-renderer-logic-separation/project.ts','./src/projects/shorts-d2r-controller-input-adapter/project.ts'],output:owned+'/motion-canvas-output'})]});
