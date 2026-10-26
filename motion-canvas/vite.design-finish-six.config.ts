import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {readFileSync, realpathSync} from 'node:fs';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';

const root = fileURLToPath(new URL('./', import.meta.url));
const slugs = ['limited-color-world', 'computer-controlled-players', 'in-game-cutscenes',
  'start-with-climax', 'kind-to-beginners', 'respect-player-time'];
const slug = process.env.DESIGN_EPISODE_SLUG ?? '';
if (!slugs.includes(slug)) throw Error('Choose one explicitly selected D25–D30 episode');
const projectRoot = resolve(root, '../projects', slug);
const logical = resolve(projectRoot, 'production/local/batch-v1');
const physical = resolve('C:/Users/1/.codex/video-production/design-finish-six-20261026', slug, 'batch-v1');
const routing = JSON.parse(readFileSync(resolve(projectRoot, 'production/batch-v1/storage-routing.json'), 'utf8'));
const same = (a:string, b:string) => resolve(a).toLowerCase() === resolve(b).toLowerCase();
if (!same(routing.logicalRoot, logical) || !same(routing.physicalRoot, physical)
    || !same(realpathSync(logical), physical)) throw Error('Exact selected episode storage route required');
const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
export default defineConfig({root,
  server: {host: '127.0.0.1', port: 9268, strictPort: true,
    fs: {allow: [resolve(root, '..'), physical]},
    watch: {ignored: ['**/*.wav', '**/*.mp3', '**/*.m4a', '**/*.mp4', '**/production/local/**']}},
  plugins: [ffmpeg(), motionCanvas({
    project: [`./src/projects/${slug}/batch-v1/project.ts`],
    output: resolve(physical, 'rendered'),
  })],
});
