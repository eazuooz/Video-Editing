import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
export default defineConfig({
  plugins: [ffmpeg(), motionCanvas({
    project: ['./src/projects/game-reward-planning/revision-v2/project.ts', './src/projects/game-reward-planning/revision-v2/footage-project.ts', './src/projects/game-reward-planning/revision-v2/lesson-project.ts', './src/projects/game-reward-planning/revision-v2/lookdev-fixes-project.ts', './src/projects/game-reward-planning/revision-v2/production-project.ts'],
    output: '../shared/output/game-reward-planning/reference-preserving-v2',
  })],
});
