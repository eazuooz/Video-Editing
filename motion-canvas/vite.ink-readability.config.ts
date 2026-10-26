import {defineConfig} from 'vite';
import motionCanvasPlugin from '@motion-canvas/vite-plugin';
import ffmpegPlugin from '@motion-canvas/ffmpeg';

const motionCanvas=(motionCanvasPlugin as any).default??motionCanvasPlugin;
const ffmpeg=(ffmpegPlugin as any).default??ffmpegPlugin;
const owned='C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-splatoon-ink-readability';
const output=owned+'/local/motion-canvas-output';
const workspace='D:/Github/VideoEditing';

export default defineConfig({
  cacheDir:owned+'/local/vite-cache',
  // FFmpeg needs the HMR websocket, but production must not reload on file writes.
  server:{host:'127.0.0.1',port:9278,strictPort:true,watch:null,fs:{allow:[workspace,owned]}},
  plugins:[
    {name:'yamyam-ink-readability-production-scope',configureServer(server){
      server.middlewares.use((req:any,res:any,next:any)=>{
        if(req.url?.split('?')[0]!=='/__yamyam_production_scope'){next();return;}
        res.setHeader('Content-Type','application/json; charset=utf-8');
        res.end(JSON.stringify({slug:'shorts-splatoon-ink-readability',revision:'ink-readability-v1',output,width:1080,height:1920,fps:60,productionWatch:'disabled',encoderWebSocket:true}));
      });
    }},
    ffmpeg(),
    motionCanvas({project:['./src/projects/shorts-splatoon-ink-readability/project.ts'],output}),
  ],
});
