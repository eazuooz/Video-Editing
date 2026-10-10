import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const {FFmpegExporterServer} = require('./node_modules/@motion-canvas/ffmpeg/lib/server/FFmpegExporterServer.js');
if (!FFmpegExporterServer.prototype.motionClarityThreadsCapped) {
  const start = FFmpegExporterServer.prototype.start;
  FFmpegExporterServer.prototype.start = async function () {
    (this as any).command.outputOptions(['-threads 2', '-filter_threads 1', '-preset veryfast', '-crf 18', '-video_track_timescale 90000']);
    return start.call(this);
  };
  FFmpegExporterServer.prototype.motionClarityThreadsCapped = true;
}
const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
export default defineConfig({
  server: {host: '127.0.0.1', port: 9253, strictPort: true,
    fs: {allow: [fileURLToPath(new URL('..', import.meta.url))]},
    watch: {ignored: ['**/*.wav', '**/*.m4a', '**/*.mp4', '**/*.webm', '**/.runtime/**']}},
  plugins: [ffmpeg(), motionCanvas({project: ['./src/projects/motion-sickness-games/teaching-clarity-v1/explanation-project.ts'],
    output: '../shared/output/unpublished-teaching-clarity-revision/motion/explanation-additions-v2'})],
});
