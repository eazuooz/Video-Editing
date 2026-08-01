import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';

const motionCanvas = (motionCanvasPlugin as any).default ?? motionCanvasPlugin;
const ffmpeg = (ffmpegPlugin as any).default ?? ffmpegPlugin;

export default defineConfig({
  plugins: [
    // Adds the "Video (FFmpeg)" exporter to the editor, so the narrated cut can
    // be rendered straight to an .mp4 with its audio track muxed in -- rather
    // than an image sequence that would then need assembling by hand.
    ffmpeg(),
    motionCanvas({
      project: [
        // Silent scene-by-scene showcase (each game explained on screen).
        './src/project.ts',
        // The narrated cut: same visuals timed to the TTS narration track.
        './src/narrated.ts',
      ],
      output: '../shared/output/motion-canvas',
    }),
  ],
});
