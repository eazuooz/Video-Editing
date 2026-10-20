import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {resolve} from 'node:path';
const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
export default defineConfig({
  server: {host: '127.0.0.1', port: 9257, strictPort: true, fs: {allow: [searchForWorkspaceRoot(process.cwd()), resolve(__dirname, '..')]}},
  plugins: [ffmpeg(), motionCanvas({project: ['./src/projects/vampire-survivors-d2-copyright/preflight-project.ts'], output: '../shared/output/motion-canvas'})],
});
