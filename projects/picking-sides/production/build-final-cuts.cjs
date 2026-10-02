// Select inspected existing-game footage against actual current narration timing.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),mc=path.join(root,'motion-canvas/src/projects/picking-sides');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');},abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const plan=read(path.join(work,'plan.json')),bank=read(path.join(root,'projects/picking-sides/planning/action-map.json')),alignment=read(path.join(work,'caption-alignment.json'));
const meta={},ranges={},cuts=[];function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:4e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const F=t=>Math.round(t*60),p=(s,n)=>n===1?0:F(s.paragraphs.find(x=>x.paragraph===n).start);
function allocate(s,from,to,specs,focus){
 let cursor=from;for(const spec of specs){if(cursor>=to)break;const [id,start,end,crop]=spec,n=Math.min(to-cursor,Math.floor((end-start)*60+1e-6));if(n<1)continue;const file=`shared/output/picking-sides/media-cache/${id}.mp4`;
 meta[file]??=JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',abs(file)]));if(start+n/60>Number(meta[file].format.duration))throw Error('Source bounds');
 const used=ranges[file]??=[];if(used.some(([a,b])=>start<b-.0001&&start+n/60>a+.0001))throw Error('Repeated source interval '+file);used.push([start,start+n/60]);ranges[file]=used;
 const label=id==='iagyci5LMTY'||id==='VOZRzwlzQeA'?'Gang Beasts · 개발사 초기 플레이 (2014)':id==='BZRZmJnPmmA'?'Ultimate Chicken Horse · 공식 알파 플레이 (2015)':id==='Z5jytMiH4rI'?'Ultimate Chicken Horse · 개발팀 플레이':'공식 게임플레이 예고편 · 발췌';
 const c={id:String(cuts.length+1).padStart(3,'0'),scene:s.id,sourceId:id,file,sourceIn:start,sourceOut:start+n/60,reviewedSourceEnd:end,frames:n,seconds:n/60,timelineStart:s.start+cursor/60,timelineEnd:s.start+(cursor+n)/60,localStartFrame:cursor,localEndFrame:cursor+n,crop:crop??null,sourceLabel:label,visibleAction:focus,viewerFocus:focus,diagramConnection:bank.chapters.find(c=>c.scene===s.id).diagramConnection,classification:'actual-existing-game-action',speed:1,loop:false,captionCenter:[960,970],continuity:'Distinct inspected excerpts; cut changes do not claim one uninterrupted match.',sourceAudio:'muted-original-presenter-and-music; continuous-approved-Nimbus',nativeBoundaryAndCaptionReview:'pending'};s.cuts.push(c);cuts.push(c);cursor+=n;
 }
 if(cursor!==to)throw Error(`Insufficient concept-matched source scene${s.id}: need${(to-from)/60}s, covered${(cursor-from)/60}s. Find fresh appropriate footage; never loop or slow.`);
}
const bankSpecs=(sid,id)=>bank.chapters.find(c=>c.scene===sid).cuts.filter(c=>!id||c.sourceId===id).map(c=>[c.sourceId,c.start,c.end,c.crop]);
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 s.cuts=[];const f=s.frames;
 if(s.id==='01'){
  allocate(s,0,p(s,3),bankSpecs('01','4KBUHwBx5i4'),'Choose one animal, notice its jump and nearby saw/next platform.');
  allocate(s,p(s,3),p(s,5),bankSpecs('01','tNgCy92QWZY').map(v=>v[1]===8.5?[v[0],9,10.65,v[3]]:v[1]===13.2?[v[0],13.2,15.05,v[3]]:v),'Separate trailer gripping/hanging actions; follow one body and the remaining hand contact. Authored black-letter transition10.7–13is excluded.');
  allocate(s,p(s,5),f,bankSpecs('01','iagyci5LMTY'),'Developer early truck attempts; choose a colored body and follow its next actual movement.');
 }else if(s.id==='03'){
  const transition=994; //16.5667s: animal-specific words finish16.30; general screen-position sentence follows.
  allocate(s,0,transition,[['Z5jytMiH4rI',70,85,[180,0,1520,855]],['Z5jytMiH4rI',85,86.566667,[120,100,1664,936]]],'Costumed monkey and hat bunny move at different heights; silhouette and costume persist across jumps.');
  allocate(s,transition,f,bankSpecs('03','iagyci5LMTY'),'General position-memory limitation then early truck introduction; track colored bodies, hand contacts and camera movement.');
 }else if(s.id==='05'){
  allocate(s,0,p(s,3),bankSpecs('05','VOZRzwlzQeA'),'Separate scaffold attempts: red/yellow grip and stance provide immediate questions, without personality or winner inference.');
  allocate(s,p(s,3),p(s,5),[['iagyci5LMTY',462,489]],'Cyan/yellow grips and tilts, green moves nearby in the same inspected attempt.');
  allocate(s,p(s,5),f,[['iagyci5LMTY',496,522]],'Explicitly separate following attempt; choose a different body and observe its actions, no behavioral-experiment claim.');
 }else if(s.id==='07'){
  allocate(s,0,p(s,2),[['VOZRzwlzQeA',27,38]],'Remaining hand at scaffold edge while bodies descend.');
  allocate(s,p(s,2),p(s,3),[['VOZRzwlzQeA',67,72.3],['VOZRzwlzQeA',46,48.9],['VOZRzwlzQeA',51,53.5]],'Distinct hanging attempts: retained hand and next foot placement above open space, excluding ground and reset frames.');
  const whiteCue=alignment.entries.find(c=>c.scene==='07'&&c.paragraph===3&&c.ko.startsWith('움직이는'));if(!whiteCue)throw Error('White-character sentence timing required');const whiteStart=F(whiteCue.start-s.start);
  allocate(s,p(s,3),whiteStart,[['BZRZmJnPmmA',23,25.4],['BZRZmJnPmmA',48.1,51.6]],'General introduction to official alpha gameplay only; horse footage must end before white-character jump sentence.');
  allocate(s,whiteStart,p(s,4),[['BZRZmJnPmmA',39.9,44.9],['BZRZmJnPmmA',27.8,29.4],['BZRZmJnPmmA',58.5,60.2]],'Three distinct white-character jump attempts show moving saws, takeoff and nearby landing platform; no build/scorecard or GetReady quota.');
  allocate(s,p(s,4),p(s,5),[['BZRZmJnPmmA',70,78.5]],'The explicitly separate later horse attempt; never present it as the previous white character’s outcome.');
  allocate(s,p(s,5),p(s,6),[['iagyci5LMTY',755.2,764.8]],'Visible yellow/cyan hands and bodies hang beside truck roofs with the road underneath.');
  allocate(s,p(s,6),f,[['iagyci5LMTY',651,674]],'The narrated separate roof attempt: grips, nearby edge and rotating view remain visible; new664–674action supports later camera/space sentence.');
 }else if(s.id==='09')allocate(s,0,f,bankSpecs('09'),'Follow moving space-level animals, flames and nearby rocks across distinct excerpts, preserving the no-camera-formula/no-best-view claim.');
 else if(s.id==='11'){
  allocate(s,0,p(s,2),[['iagyci5LMTY',270,279.54]],'Cyan and yellow converge and grip, tilt and separate on roofs.');
  allocate(s,p(s,2),p(s,3),[['iagyci5LMTY',282,291]],'Later excerpt of the same attempt: yellow falls over and rights itself near cyan; only visible action is claimed.');
  allocate(s,p(s,3),p(s,4),[['iagyci5LMTY',293.9,304]],'Later same-attempt excerpt reaches the roof edge, both bodies descend and remaining contact is visible.');
  allocate(s,p(s,4),p(s,5),[['VOZRzwlzQeA',102,107.8]],'A separate scaffold attempt shows hanging bodies and platform tilt, excluding the earlier reset and ground.');
  allocate(s,p(s,5),p(s,6),[['VOZRzwlzQeA',107.82,117.9]],'Separate red grip-to-drop excerpt: watch red’s retained hand, descent and shown outcome; do not infer a match winner.');
  allocate(s,p(s,6),f,[['VOZRzwlzQeA',72.5,88.9]],'Another actual scaffold attempt under explicit no-overall-winner caveat and final participant/action/result observation.');
 }
 if(s.cuts.reduce((a,c)=>a+c.frames,0)!==f)throw Error('Incomplete actual coverage');
}
for(const c of cuts){if(c.scene==='09'||(c.scene==='11'&&c.sourceId==='VOZRzwlzQeA'&&c.sourceIn===107.82))c.composition='caption-safe-upper870-over-fullscreen-game-background';}
plan.cuts=cuts;plan.sourceRangeAudit={noRepeatedInterval:true,ranges};plan.finalSourceTimingApproved=false;write(path.join(work,'plan.json'),plan);write(path.join(work,'cut-selection.json'),{status:'measured-selected-awaiting-direct-native-and-caption-review',normalClock:true,existingGamesOnly:true,cuts});
if(process.argv.includes('--plan-only')){console.log(`${cuts.length} current-voice cuts planned; no final media or QA approval implied.`);process.exit(0);}
const gate=read(path.join(work,'final-source-cut-review.json'));if(!gate.approved||gate.selectionSha256!==crypto.createHash('sha256').update(fs.readFileSync(path.join(work,'cut-selection.json'))).digest('hex'))throw Error('Direct source boundary/action/caption-layout review gate required.');
plan.finalSourceTimingApproved=true;
for(const c of cuts)c.nativeBoundaryAndCaptionReview='direct-source-preview-approved; rendered-pixel-review-still-required';
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 const files=[];for(const c of s.cuts){const dest=path.join(work,`cut-${c.id}.mp4`),label=path.join(work,`source-label-${c.id}.txt`);write(label,c.sourceLabel+' · 발췌');const crop=c.crop?`crop=${c.crop[2]}:${c.crop[3]}:${c.crop[0]}:${c.crop[1]},`:'';
  const textfile=rel(label).replaceAll(':','\\:');const text=`drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${textfile}':fontsize=25:fontcolor=0x073c32:x=(w-tw)/2:y=30:box=1:boxcolor=white@0.9:boxborderw=10`;
  const vf=crop+`fps=60,scale=1920:1080,setsar=1,${text}`;
  const filters=c.composition?['-filter_complex_threads','2','-filter_complex',`[0:v]${crop}fps=60,split[bg][fg];[bg]scale=1920:1080,boxblur=20:1[back];[fg]scale=1546:870[front];[back][front]overlay=187:0,setsar=1,${text}[v]`,'-map','[v]']:['-vf',vf];
  run('ffmpeg',['-v','error','-y','-threads','2','-ss',String(c.sourceIn),'-i',abs(c.file),'-frames:v',String(c.frames),...filters,...enc,dest]);c.video=rel(dest);files.push(dest);
 }
 const list=path.join(work,`scene-${s.id}-concat.txt`);write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));const dest=abs(`shared/output/picking-sides/actual-scenes/scene${s.id}.mp4`);fs.mkdirSync(path.dirname(dest),{recursive:true});run('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',list,'-c','copy',dest]);s.actualVideo=rel(dest);
 const stats=JSON.parse(run('ffprobe',['-v','error','-show_entries','stream=nb_frames,duration,width,height,r_frame_rate','-of','json',dest])).streams[0];if(Number(stats.nb_frames)!==s.frames)throw Error('Compiled frame mismatch');s.actualMediaVerified={...stats,sha256:crypto.createHash('sha256').update(fs.readFileSync(dest)).digest('hex')};
}
write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);console.log('Actual scenes compiled from reviewed existing-game sources; full final QA still required.');
