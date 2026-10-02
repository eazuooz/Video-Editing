// Use only fresh, normal-clock source ranges which demonstrate the spoken chapter.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),mc=path.join(root,'motion-canvas/src/projects/game-writing');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const plan=read(path.join(work,'plan.json')),abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const sources={gm:'shared/assets/game-writing/raw/gm-tutorial.mp4',overview:'shared/assets/game-writing/raw/gameplay-overview.mp4'};
const source=k=>sources[k]||`shared/assets/game-writing/story-takes-v1/${k}.mp4`;
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:3e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y','-threads','2',...a]);
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
const ranges={},metadata={},allCuts=[];
function p(s,n){return n===1?0:Math.round((plan.paragraphs.find(a=>a.scene===s.id&&a.paragraph===n).start-s.start)*60);}
function allocate(s,from,to,specs,focus){
 const length=to-from;if(length<=0)throw Error('Invalid spoken action block');let taken=0;
 for(const [i,v]of specs.entries()){
  const frames=i===specs.length-1?length-taken:(v.frames??Math.round(length*(v.weight??1/specs.length)));taken+=frames;
  const file=source(v.key),start=v.in,end=start+frames/60;if(frames<1)throw Error('Empty source cut');
  metadata[file]??=JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',abs(file)]));const meta=metadata[file];
  if(end>Number(meta.streams.find(x=>x.codec_type==='video').duration)+.01)throw Error(`Source ${v.key} too short: ${end}`);
  const prior=ranges[file]??=[];if(prior.some(([a,b])=>start<b-.0001&&end>a+.0001))throw Error(`Source range repeated: ${v.key} ${start}-${end}`);prior.push([start,end]);ranges[file]=prior;
  const c={id:String(allCuts.length+1).padStart(3,'0'),scene:s.id,key:v.key,file,sourceIn:start,sourceOut:end,frames,seconds:frames/60,timelineStart:s.start+(from+taken-frames)/60,timelineEnd:s.start+(from+taken)/60,classification:'actual',visibleAction:focus,viewerFocus:focus,connection:s.title,presentation:'native-16:9-full-screen-normal-clock',sourceAudio:'muted-original-English-dialogue-and-music; continuous-approved-Nimbus',captionPosition:v.key==='overview'?'top150':v.key==='gm'?'lower-left970':'bottom970'};
  allCuts.push(c);s.cuts.push(c);
 }
}
for(const s of plan.scenes){if(s.classification!=='actual')continue;s.cuts=[];const f=s.frames;
 if(s.id==='01'){
  const end=p(s,4);allocate(s,0,end,[{key:'overview',in:35,frames:768},{key:'gm',in:466}],'Actual character conversations with answer choices, then author edits question/options; no claim about hidden conditions.');
  allocate(s,end,f,[{key:'guard-first',in:1.3}],'Fresh guard-first visit, item requirement, notice reading and explicit sharing.');
 }else if(s.id==='03'){
  const split=p(s,6);allocate(s,0,162,[{key:'overview',in:47.8}],'Caryl addresses Ifan by name; only the visible recognition is claimed.');
  allocate(s,162,split,[{key:'note-first',in:0}],'Read notice, share the rule and continue a repeat conversation.');
  allocate(s,split,f,[{key:'verify-unshared-first',in:1.0}],'A separately captured notice-first path reaches an uninformed guard with a share-rule choice.');
 }else if(s.id==='05'){
  const end=p(s,3);allocate(s,0,end,[{key:'gm',in:1223,frames:300},{key:'gm',in:1232,frames:300},{key:'gm',in:1242}],'Create ring, enter name/description and move it into inventory; no invented plot outcome.');
  allocate(s,end,p(s,5),[{key:'owner-chain',in:1.4}],'Acquire seal, transfer to companion and observe the companion-present reply.');
  allocate(s,p(s,5),p(s,6),[{key:'owner-chain',in:21.65}],'Companion rests, player returns alone and the unavailable seal reply disappears.');
  allocate(s,p(s,6),f,[{key:'owner-chain',in:35.70}],'Guard gives a recovery path; player walks back and recovers the seal.');
 }else if(s.id==='07'){
  const end=p(s,3);allocate(s,0,end,[{key:'gm',in:484,frames:480},{key:'gm',in:513}],'Distinct wolf response labels and authoring action are visible; label editing is separated from outcome implementation.');
  allocate(s,end,p(s,4),[{key:'route-feed',in:1.2,weight:.5},{key:'route-detour',in:1.2}],'Fresh road encounters offer food, detour and calm dismissal.');
  allocate(s,p(s,4),p(s,5),[{key:'route-feed',in:9.18,weight:.5},{key:'route-detour',in:9.19}],'Food transfer consumes a ration; the separately captured detour moves around the coast.');
  allocate(s,p(s,5),p(s,6),[{key:'route-feed',in:22.64,weight:.5},{key:'route-detour',in:24.15}],'Guard acknowledgements reflect each actual route.');
  allocate(s,p(s,6),f,[{key:'route-feed',in:30.40,weight:.5},{key:'route-detour',in:31.93}],'Both routes present the seal and enter the shared harbor; resources remain different.');
 }else if(s.id==='09'){
  const end=p(s,2);allocate(s,0,end,[{key:'gm',in:429}],'Map and event card are edited separately.');
  allocate(s,end,p(s,4),[{key:'skip-essential',in:.3}],'Skip opening exposition, approach the guard and obtain the necessary rule naturally.');
  allocate(s,p(s,4),p(s,5),[{key:'skip-essential',in:Math.max(16.7,.3+(p(s,4)-end)/60)}],'Notice provides the required seal and its location.');
  const length=p(s,6)-p(s,5);allocate(s,p(s,5),p(s,6),[{key:'read-essential',in:.3,frames:Math.min(180,Math.round(length*.4))},{key:'read-essential',in:14.1}],'The read-exposition route is separately captured and uses a short known-rule confirmation.');
  allocate(s,p(s,6),f,[{key:'skip-essential',in:31.1,weight:.5},{key:'read-essential',in:35.9}],'Guard setting provides the rule and the informed path proceeds through the gate.');
 }else if(s.id==='11'){
  allocate(s,0,p(s,2),[{key:'verification-standard',in:.2}],'Fresh record-first run starts with notice reading.');
  allocate(s,p(s,2),p(s,3),[{key:'verification-standard',in:9.3,weight:.27},{key:'verification-standard',in:42.74,weight:.31},{key:'verification-standard',in:47.80}],'Acquire the seal, visibly present it and enter the new scene.');
  allocate(s,p(s,3),p(s,4),[{key:'verify-unknown-path',in:1.1}],'Fresh skipped-exposition guard-first route asks rather than pretending to know.');
  allocate(s,p(s,4),p(s,5),[{key:'verification-absent',in:6.6,weight:.21},{key:'verification-absent',in:12.7,weight:.21},{key:'verification-absent',in:18.8,weight:.27},{key:'verification-absent',in:33.0}],'Pass seal to companion, let companion leave, observe the missing reply, then recover it.');
  allocate(s,p(s,5),p(s,6),[{key:'verify-feed-again',in:4.9,weight:.32},{key:'verification-standard',in:18.42,weight:.32},{key:'verify-feed-again',in:21.1}],'A fresh feed run and the standard calm-dismissal run leave different resources and enter the same harbor.');
  allocate(s,p(s,6),f,[{key:'verification-absent',in:39.06}],'Recovered ownership restores the actual reply; accepted item and entry continue without a dialogue contradiction.');
 }else if(s.id==='13')allocate(s,0,f,[{key:'observe-question-memory',in:.5}],'Fresh question, explanation and repeat conversation remember the completed exchange.');
 else if(s.id==='14')allocate(s,0,f,[{key:'observe-companion-return',in:5,frames:480},{key:'observe-companion-return',in:13.2}],'Companion absence removes access; physical return restores the reply without changing owner.');
 else if(s.id==='15')allocate(s,0,f,[{key:'observe-drive-result',in:1}],'Third route moves the animal aside and gets the matching guard acknowledgement.');
 else if(s.id==='16')allocate(s,0,f,[{key:'observe-finished-event',in:4.8}],'Hand over the seal, revisit the same guard and receive entry instead of another demand.');
 if(s.cuts.reduce((n,c)=>n+c.frames,0)!==f)throw Error('Scene source coverage failed');
}
plan.cuts=allCuts;plan.sourceRangeAudit={noRepeatedInterval:true,ranges};write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);write(path.join(work,'cut-selection.json'),{selectedAt:new Date().toISOString(),status:'measured-selected-awaiting-native-first-middle-end-and-caption-review',normalClock:true,sourceAudioMuted:true,cuts:allCuts});
if(process.argv.includes('--plan-only')){console.log(`${allCuts.length} normal-clock cuts selected; native review remains pending.`);process.exit(0);}
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 const files=[];for(const c of s.cuts){const out=path.join(work,`cut-${c.id}.mp4`);console.log(`Cut ${c.id} scene${c.scene} ${c.key} ${c.sourceIn} + ${c.seconds.toFixed(3)}s`);ff(['-ss',String(c.sourceIn),'-i',abs(c.file),'-frames:v',String(c.frames),'-vf','fps=60,scale=1920:1080,setsar=1',...enc,out]);c.video=rel(out);files.push(out);}
 const list=path.join(work,`scene-${s.id}-concat.txt`);write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
 const dest=abs(`shared/assets/game-writing/playtest/scene${s.id}.mp4`);fs.mkdirSync(path.dirname(dest),{recursive:true});ff(['-f','concat','-safe','0','-i',list,'-c','copy',dest]);s.actualVideo=rel(dest);
 const stats=JSON.parse(run('ffprobe',['-v','error','-show_entries','stream=nb_frames,duration,width,height,r_frame_rate','-of','json',dest])).streams[0];if(Number(stats.nb_frames)!==s.frames)throw Error('Compiled actual frame mismatch');s.actualMediaVerified={...stats,sha256:crypto.createHash('sha256').update(fs.readFileSync(dest)).digest('hex')};
}
write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);console.log('All actual scene clips compiled; final visual and full-mix QA remain pending.');
