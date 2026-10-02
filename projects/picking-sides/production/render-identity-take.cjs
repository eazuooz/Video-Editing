// Offline game-state renderer. Uses no browser or OS input automation.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const {once}=require('node:events');
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
const root=path.resolve(__dirname,'../../..'),base=path.resolve(__dirname,'..'),game=require('../playtest/race.cjs');
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'race-takes-identity.json'),'utf8'));
const output=path.join(root,'shared/output/picking-sides/race-takes'),checkpoint=path.join(__dirname,'race-identity-checkpoint.json');
const hashes=['playtest/race.cjs','playtest/view.js','production/race-takes-identity.json'].map(p=>({path:'projects/picking-sides/'+p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(base,p))).digest('hex')}));
const digest=crypto.createHash('sha256').update(JSON.stringify(hashes)).digest('hex');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');fs.mkdirSync(output,{recursive:true});
const receipt={startedAt:new Date().toISOString(),pid:process.pid,kind:plan.kind,humanInputRecording:false,hashes,digest,completed:[],status:'rendering-original-game-sources'};
const save=()=>fs.writeFileSync(checkpoint,JSON.stringify(receipt,null,2)+'\n');
async function render(take){
 const file=path.join(output,take.id+'.mp4'),report=path.join(output,take.id+'.json');
 if(fs.existsSync(file)&&fs.existsSync(report)){const old=JSON.parse(fs.readFileSync(report));if(old.digest===digest&&old.complete){receipt.completed.push(old);save();console.log('Reused verified code-hash source '+take.id);return;}}
 const canvas=createCanvas(1920,1080),stubs=new Map();
 const context={Cloudpost:game,performance:{now:()=>0},URLSearchParams,location:{search:'?seed='+take.seed},window:{},structuredClone,requestAnimationFrame:()=>{},addEventListener:()=>{},document:{body:{classList:{add:()=>{}}},querySelector:s=>{if(s==='canvas')return canvas;if(!stubs.has(s))stubs.set(s,{setAttribute:()=>{},textContent:''});return stubs.get(s);},querySelectorAll:()=>[]}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(base,'playtest/view.js'),'utf8'),context);
 const start=Math.round(take.in*60),end=Math.round(take.out*60),count=end-start;
 vm.runInContext(`game.act(state,'select',${JSON.stringify(take.selected)});game.act(state,'markers',${take.markers});game.act(state,'camera','${take.camera}');game.act(state,'start');scale=${take.camera==='follow'?1:.245};camX=-50;`,context);
 const ff=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',file],{windowsHide:true,stdio:['pipe','ignore','pipe']});
 let errors='';ff.stderr.on('data',x=>errors+=x);const closed=once(ff,'close');ff.stdin.on('error',()=>{});
 receipt.active={take:take.id,ffmpegPid:ff.pid,frame:0,totalFrames:count,output:path.relative(root,file).replaceAll('\\','/')};save();
 try{
 for(let i=0;i<end;i++){
   for(const e of take.events||[])if(Math.round(e.at*60)===i)vm.runInContext(`game.act(state,${JSON.stringify(e.action)},${JSON.stringify(e.value)});`,context);
   vm.runInContext(`game.tick(state,1/60);{const target=state.racers.find(p=>p.id===state.selected)||[...state.racers].sort((a,b)=>b.x-a.x)[0];const goalScale=state.cameraMode==='overview'?.245:1;scale+=(goalScale-scale)/15;const goalX=state.cameraMode==='overview'?-70:Math.max(-50,Math.min(game.finish-1300,target.x-470));camX+=(goalX-camX)/15;}`,context);
   if(i<start)continue;
   vm.runInContext('world();',context);
   if(!ff.stdin.write(Buffer.from(canvas.getContext('2d').getImageData(0,0,1920,1080).data)))await once(ff.stdin,'drain');
   if((i-start)%300===0){receipt.active.frame=i-start;save();console.log(take.id+' '+(i-start)+'/'+count);}
 }
 ff.stdin.end();const [code]=await closed;if(code!==0)throw Error(errors||'ffmpeg exit '+code);
 const state=vm.runInContext('structuredClone(state)',context);
 const result={id:take.id,complete:true,digest,source:path.relative(root,file).replaceAll('\\','/'),frames:count,seconds:count/60,seed:take.seed,sourceIn:take.in,sourceOut:take.out,normalSpeed:true,humanInputRecording:false,finalFacts:game.raceFacts(state),events:state.events,visualReview:'pending',fullDecode:'pending'};
 fs.writeFileSync(report,JSON.stringify(result,null,2)+'\n');receipt.completed.push({id:take.id,frames:count,source:result.source,digest,complete:true});save();console.log('Source rendered '+take.id);
 }catch(error){ff.stdin.destroy();ff.kill();throw error;}
}
(async()=>{save();for(const t of plan.takes)await render(t);receipt.status='sources-rendered-awaiting-direct-visual-review';receipt.finishedAt=new Date().toISOString();receipt.active=null;save();console.log(receipt.status);})().catch(error=>{receipt.status='failed';receipt.error=error.stack;save();console.error(error);process.exitCode=1;});
