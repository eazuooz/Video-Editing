import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
const root = path.resolve(fileURLToPath(new URL('../../../../', import.meta.url)));
const batchId = 'tech-ten-shorts-20261030', revision = 'tech-ten-v1';
const batch = JSON.parse(readFileSync(path.join(root, 'production/batches', batchId, 'batch.json'), 'utf8'));
const slug = process.env.YAMYAM_TECH_TEN_SLUG;
if (!slug || !batch.projects.some((p: {slug: string}) => p.slug === slug)) throw new Error('Select exactly one authorized batch project.');
const owned = 'C:/Users/1/Videos/YamyamProduction/' + batchId + '/' + slug;
const output = owned + '/local/motion-canvas-output';
const route = './src/projects/' + batchId + '/entries/' + slug + '/project.ts';

export default defineConfig({
  cacheDir: owned + '/local/vite-cache',
  server: {host: '127.0.0.1', port: 9284, strictPort: true,
    fs: {allow: [searchForWorkspaceRoot(process.cwd()), root, 'C:/Users/1/Videos/YamyamProduction/' + batchId]}},
  plugins: [
    {name: 'yamyam-tech-ten-production-scope', configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url?.split('?')[0] !== '/__yamyam_production_scope') {next(); return;}
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.end(JSON.stringify({batchId, slug, revision, output, width: 1080, height: 1920, fps: 60}));
      });
    }}, ffmpeg(), motionCanvas({project: [route], output}),
  ],
});
