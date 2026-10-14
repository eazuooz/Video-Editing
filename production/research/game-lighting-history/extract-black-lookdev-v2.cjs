const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const dir = path.join(root, 'projects/game-lighting-history-01/production/local/black-lookdev-v2');
const video = path.join(dir, 'project.mp4');
const qa = path.join(dir, 'qa');
const ffmpeg = path.join(root, 'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe');
const ffprobe = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const plan = JSON.parse(fs.readFileSync(path.join(__dirname, 'black-lookdev-plan-v2.json'), 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function run(exe, args) {
  const result = spawnSync(exe, args, {encoding: 'utf8', windowsHide: true, maxBuffer: 16 * 1024 * 1024});
  if (result.status !== 0) throw Error(JSON.stringify({exe, args, exitCode: result.status, stderr: result.stderr}));
  return {command: [exe, ...args], exitCode: result.status, stdout: result.stdout, stderr: result.stderr};
}
if (fs.existsSync(path.join(qa, 'extraction.json'))) throw Error('Existing completed extraction preserved.');
fs.mkdirSync(qa, {recursive: true});
const probeRun = run(ffprobe, ['-v','error','-select_streams','v:0','-count_frames','-show_entries',
  'stream=codec_name,width,height,r_frame_rate,time_base,duration,nb_frames,nb_read_frames','-of','json',video]);
const probe = JSON.parse(probeRun.stdout).streams[0];
if (probe.width !== 1920 || probe.height !== 1080 || probe.r_frame_rate !== '60/1' || probe.time_base !== '1/90000')
  throw Error('Unexpected proof format');
const decode = run(ffmpeg, ['-hide_banner','-v','error','-threads','2','-i',video,'-f','null','NUL']);
const frames = plan.cases.flatMap((item, i) => [30,90,150].map((offset, pose) => ({
  caseIndex:i, key:item.key, model:item.model, pose:['start','middle','end'][pose], frame:i*180+offset,
})));
const filter = `select='${frames.map(f=>`eq(n,${f.frame})`).join('+')}'`;
const extraction = run(ffmpeg, ['-hide_banner','-v','error','-threads','2','-i',video,
  '-vf',filter,'-vsync','0','-threads','2',path.join(qa,'frame-%02d.png')]);
frames.forEach((f,i) => {
  f.path = path.relative(root,path.join(qa,`frame-${String(i+1).padStart(2,'0')}.png`)).replaceAll('\\','/');
  f.sha256 = sha(path.join(root,f.path));
});
const boards=[];
for (let i=0; i<6; i++) {
  const output=path.join(qa,`board-${i+1}.png`);
  const result=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-start_number',String(i*6+1),
    '-i',path.join(qa,'frame-%02d.png'),'-vf','scale=960:540,tile=2x3:nb_frames=6',
    '-frames:v','1','-threads','2',output]);
  boards.push({path:path.relative(root,output).replaceAll('\\','/'),sha256:sha(output),
    models:plan.cases.slice(i*2,i*2+2).map(c=>c.model),exitCode:result.exitCode,directlyViewed:false});
}
const record={createdAt:new Date().toISOString(),video:{path:path.relative(root,video).replaceAll('\\','/'),sha256:sha(video),...probe},
  plannedFrames:plan.plannedFramesAt60,observedFrames:Number(probe.nb_read_frames),
  endpointDifference:Number(probe.nb_read_frames)-plan.plannedFramesAt60,
  endpointNote:'Motion Canvas GUI proof includes its final endpoint frame. This short proof is not the final timing-approved master.',
  wholeDecode:decode,probeCommand:probeRun.command,extractionCommand:extraction.command,frames,boards,
  finalVideoProduced:false,pixelsReviewed:false,localOnly:true};
fs.writeFileSync(path.join(qa,'extraction.json'),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({observedFrames:record.observedFrames,duration:probe.duration,wholeDecode:decode.exitCode,
  frames:frames.length,boards:boards.length,localOnly:true}));
