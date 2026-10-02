import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import standard from './vite.config';

// A dedicated render server must not watch binary media being written by other
// concurrent production jobs. Files remain served normally when requested.
const base = standard as any;
export default defineConfig({
  ...base,
  server: {
    ...base.server,
    fs: {
      ...base.server?.fs,
      allow: [...base.server.fs.allow, fileURLToPath(new URL('../shared/assets/blank-project-coding', import.meta.url))],
    },
    watch: {
      ...base.server?.watch,
      ignored: ['**/*.wav', '**/*.m4a', '**/*.mp4', '**/*.webm', '**/.runtime/**'],
    },
  },
});
