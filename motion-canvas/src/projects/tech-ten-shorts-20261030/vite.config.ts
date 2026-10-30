import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {createReadStream, readFileSync, realpathSync, statSync} from 'node:fs';
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
  // Project modules are imported dynamically by render-worker.html. Discovering
  // these after rendering starts reloads the page and destroys the encoder call.
  optimizeDeps: {
    entries: ['render-worker.html', route],
    include: ['@motion-canvas/core', '@motion-canvas/2d',
      '@motion-canvas/2d/lib/jsx-dev-runtime', '@motion-canvas/ffmpeg/lib/client'],
    noDiscovery: true,
  },
  server: {host: '127.0.0.1', port: 9284, strictPort: true,
    fs: {allow: [searchForWorkspaceRoot(process.cwd()), root, 'C:/Users/1/Videos/YamyamProduction/' + batchId]}},
  plugins: [
    {name: 'yamyam-tech-ten-production-scope', configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // Vite5's Windows raw-FS server drops a drive letter. Our server is on D:
        // and captures are on C:, so serve only this slug's verified image roots
        // before that middleware, without widening general filesystem access.
        const pathname = new URL(req.url ?? '/', 'http://127.0.0.1').pathname;
        const imagePrefixes = ['frames', 'unity-capture'].map(directory =>
          ('/@fs/' + owned + '/local/' + directory + '/').toLowerCase());
        if (imagePrefixes.some(prefix => pathname.toLowerCase().startsWith(prefix))) {
          if (req.method !== 'GET' && req.method !== 'HEAD') {res.statusCode = 405; res.end(); return;}
          try {
            const requested = decodeURIComponent(pathname.slice('/@fs/'.length));
            const file = realpathSync(requested);
            const inside = ['frames', 'unity-capture'].some(directory => {
              try {
                const base = realpathSync(path.join(owned, 'local', directory));
                const relative = path.relative(base, file);
                return relative !== '' && !relative.startsWith('..') && !path.isAbsolute(relative);
              } catch {return false;}
            });
            if (!inside || !/\.jpe?g$/i.test(file)) {res.statusCode = 403; res.end(); return;}
            const info = statSync(file);
            if (!info.isFile()) {res.statusCode = 404; res.end(); return;}
            res.setHeader('Content-Type', 'image/jpeg');
            res.setHeader('Content-Length', info.size);
            res.setHeader('Cache-Control', 'no-store');
            if (req.method === 'HEAD') {res.end(); return;}
            createReadStream(file).on('error', () => res.destroy()).pipe(res);
          } catch {res.statusCode = 404; res.end();}
          return;
        }
        if (req.url?.split('?')[0] !== '/__yamyam_production_scope') {next(); return;}
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.end(JSON.stringify({batchId, slug, revision, output, width: 1080, height: 1920, fps: 60}));
      });
    }}, ffmpeg(), motionCanvas({project: [route], output}),
  ],
});
