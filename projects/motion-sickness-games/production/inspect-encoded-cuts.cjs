const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),crypto=require('node:crypto');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),dest=path.join(work,'encoded-boundary-review');
fs.mkdirSync(dest,{recursive:true});if(fs.existsSync(path.join(dest,'index.json')))throw Error('Inspect existing encoded samples, do not duplicate');
const plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
function run(args){const r=spawnSync('ffmpeg',['-v','error','-y','-threads','2',...args],{encoding:'utf8',windowsHide:true});if(r.status!==0||r.stderr.trim())throw Error(r.stderr);}
(async()=>{const decoding=[];for(const s of plan.scenes.filter(s=>s.classification==='actual')){run(['-i',path.join(root,s.actualVideo),'-f','null','-']);decoding.push({scene:s.id,exitCode:0,stderr:''});}
 const samples=[];for(const cut of plan.cuts){for(const [role,frame]of [['first',0],['middle',Math.floor(cut.frames/2)],['last',cut.frames-1]]){
  const filename=path.join(dest,`${cut.id}-${role}.png`);run(['-i',path.join(root,cut.video),'-vf',`select=eq(n\\,${frame})`,'-frames:v','1','-fps_mode','vfr',filename]);
  samples.push({cut:cut.id,scene:cut.scene,role,frame,path:path.relative(root,filename).replaceAll('\\','/')});
 }}
 const pages=[];for(let begin=0;begin<samples.length;begin+=15){const batch=samples.slice(begin,begin+15),c=createCanvas(1920,Math.ceil(batch.length/3)*405),x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,c.width,c.height);for(const[i,s]of batch.entries()){let left=i%3*640,top=Math.floor(i/3)*405;x.drawImage(await loadImage(path.join(root,s.path)),left,top+38,640,360);x.fillStyle='#111';x.font='20px Malgun Gothic';x.fillText(`Encoded ${s.scene}/${s.cut} ${s.role} frame${s.frame}`,left+6,top+25);}const f=path.join(dest,`contact-${Math.floor(begin/15)+1}.jpg`);fs.writeFileSync(f,c.toBuffer('image/jpeg'));pages.push(path.relative(root,f).replaceAll('\\','/'));}
 fs.writeFileSync(path.join(dest,'index.json'),JSON.stringify({createdAt:new Date().toISOString(),pid:process.pid,status:'decoded-six-chapters-102-encoded-boundaries-pending-direct-read',planSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(work,'plan.json'))).digest('hex'),decoding,samples,pages},null,2)+'\n');console.log('Six full decodes/102 exact encoded first-middle-last samples ready for direct reading.');
})().catch(e=>{console.error(e);process.exitCode=1;});
