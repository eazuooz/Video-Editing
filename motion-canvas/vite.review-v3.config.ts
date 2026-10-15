import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
export default defineConfig({plugins:[ffmpeg(),motionCanvas({project:'./src/projects/game-lighting-history-01/review-v3/doom-project.ts',output:'../projects/game-lighting-history-01/production/local/review-v3/motion-canvas'})]});
