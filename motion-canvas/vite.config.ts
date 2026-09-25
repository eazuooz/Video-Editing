import {defineConfig, searchForWorkspaceRoot} from 'vite';
import {fileURLToPath} from 'node:url';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import projects from './projects.json';

const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;

export default defineConfig({
  server: {
    fs: {
      // Serve this lecture's exports without exposing the rest of the filesystem.
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        fileURLToPath(new URL('../projects/renderformer-explained/production/body-review', import.meta.url)),
      ],
    },
  },
  plugins: [
    // Adds the "Video (FFmpeg)" exporter to the editor, so the narrated cut can
    // be rendered straight to an .mp4 with its audio track muxed in -- rather
    // than an image sequence that would then need assembling by hand.
    ffmpeg(),
    motionCanvas({
      // Existing projects plus entries registered by
      // scripts/new-video-project.ps1.
      project: projects,
      output: '../shared/output/motion-canvas',
    }),
  ],
});
