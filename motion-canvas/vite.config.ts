import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';

const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;

export default defineConfig({
  plugins: [
    motionCanvas({
      project: './src/project.ts',
      output: '../shared/output/motion-canvas',
    }),
  ],
});
