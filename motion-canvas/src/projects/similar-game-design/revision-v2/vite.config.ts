import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {readFileSync, realpathSync} from 'node:fs';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';

const root = fileURLToPath(new URL('../../../../', import.meta.url));
const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
const route = './src/projects/similar-game-design/revision-v2/';
const logicalMedia = resolve(root, '../projects/similar-game-design/production/local/reference-preserving-v2');
const physicalMedia = resolve('C:/Users/1/.codex/video-production/similar-game-design/reference-preserving-v2');
const routing = JSON.parse(readFileSync(resolve(root, '../projects/similar-game-design/production/reference-preserving-v2/storage-routing.json'), 'utf8'));
const same = (a: string, b: string) => resolve(a).toLowerCase() === resolve(b).toLowerCase();
if (!same(routing.logicalRoot, logicalMedia) || !same(routing.physicalRoot, physicalMedia)
    || JSON.stringify(routing.allowedOutputSubdirectories) !== JSON.stringify(['edit', 'rendered'])) {
  throw Error('Only the exact D22 edit/rendered storage routes are authorized');
}
const physicalRendered = resolve(physicalMedia, 'rendered');
if (!same(realpathSync(resolve(logicalMedia, 'rendered')), physicalRendered)
    || !same(realpathSync(physicalRendered), physicalRendered)) {
  throw Error('Root must create the exact D rendered -> C rendered junction before starting Vite');
}

// An isolated finite project list. Never mutate the shared project registry.
export default defineConfig({
  root,
  server: {
    host: '127.0.0.1', port: 9254, strictPort: true,
    fs: {allow: [resolve(root, '..'), physicalMedia]},
    watch: {ignored: ['**/*.wav', '**/*.mp3', '**/*.m4a', '**/*.mp4', '**/*.webm', '**/production/local/**']},
  },
  plugins: [ffmpeg(), motionCanvas({
    project: [route + 'preflight-project.ts', route + 'production-project.ts', route + 'patch-v4-project.ts'],
    output: physicalRendered,
  })],
});
