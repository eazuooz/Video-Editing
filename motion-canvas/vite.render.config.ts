// Render-only dev server: loads just the listed projects and ignores file changes, so edits elsewhere in
// the repo (projects.json, other scenes) cannot hot-reload or restart a long headless render.
// Usage: MC_RENDER_PROJECTS=./src/projects/play-first/project.ts,./src/projects/play-first/captioned.ts \
//        npx vite --config vite.render.config.ts --host 127.0.0.1 --port 9110
import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';

const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;
const projects = (process.env.MC_RENDER_PROJECTS ?? '').split(',').map(p => p.trim()).filter(Boolean);
if (!projects.length) throw new Error('Set MC_RENDER_PROJECTS to the project files to render');

export default defineConfig({
  plugins: [ffmpeg(), motionCanvas({project: projects, output: '../shared/output/motion-canvas'})],
  server: {watch: {ignored: ['**/*']}},
});
