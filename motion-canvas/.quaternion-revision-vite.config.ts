import {defineConfig} from 'vite';
import mcPlugin from '@motion-canvas/vite-plugin';
const mc=(mcPlugin as any).default??mcPlugin;
export default defineConfig({build:{outDir:'../shared/output/game-math-part2-teaching-revision/editor-build'},plugins:[mc({project:["./src/projects/game-math-quaternion-foundations-v2/project.ts","./src/projects/game-math-quaternion-calculations-v2/project.ts"],output:'../shared/output/motion-canvas'})]});
