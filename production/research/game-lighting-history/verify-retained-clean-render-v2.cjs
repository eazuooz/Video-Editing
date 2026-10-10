const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),rel='production/research/game-lighting-history/local/episode03-chapter-render-v4',read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const scene=process.argv[2],plan=read('projects/game-lighting-history-03/production/retained-clean-render-plan-v2.json'),chapter=plan.chapters.find(c=>c.scene===scene);if(!chapter)throw Error('Exact planned scene required');
const out=rel+'/renders/'+chapter.name+'.verification.json';if(fs.existsSync(path.join(root,out)))throw Error('Existing verified chapter preserved');
const live=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'episode03-chapter-render-v4' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(live.status!==0)throw Error('Resource inspection failed');
if(live.stdout.trim())throw Error('Owned chapter render/verification is still running; wait for its recorded exit');
const metaFormatting=[];
for(const i of plan.inputs){
 if(sha(i.path)===i.sha256)continue;
 if(!i.path.endsWith('-project.meta'))throw Error('Input changed:'+i.path);
 const c=plan.chapters.find(x=>i.path.endsWith('/'+x.name+'.meta'));
 const expected={version:0,shared:{background:null,range:[0,(c.renderEndFrameInclusive??c.frames)/60],size:{x:1920,y:1080},audioOffset:0},preview:{fps:c.previewFps||30,resolutionScale:1},rendering:{fps:60,resolutionScale:1,colorSpace:'srgb',exporter:{name:'@motion-canvas/ffmpeg',options:{fastStart:true,includeAudio:false}}}};
 if(JSON.stringify(read(i.path))!==JSON.stringify(expected))throw Error('Rendering settings changed:'+i.path);
 metaFormatting.push({path:i.path,preparedSha256:i.sha256,actualSha256:sha(i.path),allSettingsSemanticallyIdentical:true});
}
const e=read(chapter.execution);if(e.status!=='complete'||e.exitCode!==0||!e.command.includes(chapter.name+'.mp4'))throw Error('Chapter exporter not complete');
const ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe',ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),video=path.join(root,chapter.output);
const run=(exe,args)=>{const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return{command:[exe,...args],exitCode:0,stdout:r.stdout};};
const p=run(ffprobe,['-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',video]),probe=JSON.parse(p.stdout),v=probe.streams[0];
if(probe.streams.length!==1||v.codec_type!=='video'||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||v.time_base!=='1/90000'||Number(v.nb_read_frames)!==chapter.frames)throw Error('Unexpected frame/stream count');
const packetRun=run(ffprobe,['-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',video]),pts=JSON.parse(packetRun.stdout).packets.map(p=>p.pts).sort((a,b)=>a-b);
if(pts.length!==chapter.frames||pts.some((p,i)=>p!==i*1500))throw Error('Presentation timestamps not exact continuous60fps');
const decode=run(ffmpeg,['-v','error','-threads','2','-i',video,'-f','null','NUL']);
const record={verifiedAt:new Date().toISOString(),chapter:scene,video:{path:chapter.output,sha256:sha(chapter.output)},exporter:e,probe,plannedFrames:chapter.frames,observedFrames:pts.length,presentationTimebase:90000,firstPts:pts[0],lastPts:pts.at(-1),allPresentationPtsContinuous:true,probeCommand:p.command,packetCommand:packetRun.command,wholeDecode:decode,metaFormatting,allPixelsReviewed:false,finalEpisodeApproved:false,localOnly:true};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({scene,frames:pts.length,exactPts:true,decode:0,pixelsReviewed:false}));
