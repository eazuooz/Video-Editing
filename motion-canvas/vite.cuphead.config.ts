import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {fileURLToPath} from 'node:url';

const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
const owned='C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-cuphead-animation-tick';
const output=owned+'/local/motion-canvas-output';

export default defineConfig({
  cacheDir:owned+'/local/vite-cache',
  server:{host:'127.0.0.1',port:9275,strictPort:true,fs:{allow:[searchForWorkspaceRoot(process.cwd()),fileURLToPath(new URL('..',import.meta.url)),owned]}},
  plugins:[
    {name:'yamyam-cuphead-production-scope',configureServer(server){
      server.middlewares.use((req,res,next)=>{
        if(req.url?.split('?')[0]!=='/__yamyam_production_scope'){next();return;}
        res.setHeader('Content-Type','application/json; charset=utf-8');
        res.end(JSON.stringify({slug:'shorts-cuphead-animation-tick',revision:'animation-tick-v1',output,width:1080,height:1920,fps:60}));
      });
    }},
    ffmpeg(),
    motionCanvas({project:['./src/projects/shorts-cuphead-animation-tick/project.ts'],output}),
  ],
});
