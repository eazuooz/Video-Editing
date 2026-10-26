import {defineConfig, searchForWorkspaceRoot} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';
import {fileURLToPath} from 'node:url';

const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
const owned='C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-teardown-spray-palette';
const output=owned+'/local/motion-canvas-output';

export default defineConfig({
  cacheDir:owned+'/local/vite-cache',
  // Freeze production inputs until an explicit server restart. Keep Vite's HMR
  // websocket: Motion Canvas uses it for FFmpeg frame/ack transport.
  server:{host:'127.0.0.1',port:9277,strictPort:true,watch:null,fs:{allow:[searchForWorkspaceRoot(process.cwd()),fileURLToPath(new URL('..',import.meta.url)),owned]}},
  plugins:[
    {name:'yamyam-teardown-production-scope',configureServer(server){
      server.middlewares.use((req,res,next)=>{
        if(req.url?.split('?')[0]!=='/__yamyam_production_scope'){next();return;}
        res.setHeader('Content-Type','application/json; charset=utf-8');
        res.end(JSON.stringify({slug:'shorts-teardown-spray-palette',revision:'spray-palette-v1',output,width:1080,height:1920,fps:60,productionWatch:'disabled',encoderWebSocket:true}));
      });
    }},
    ffmpeg(),
    motionCanvas({project:['./src/projects/shorts-teardown-spray-palette/project.ts'],output}),
  ],
});
