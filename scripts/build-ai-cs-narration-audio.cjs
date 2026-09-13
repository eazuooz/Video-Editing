// Full v5 voice + the twelve existing source-audio slots. Blue Dream is not
// silently substituted: this review mix deliberately remains BGM-pending.
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const projectDir = 'projects/ai-era-cs-fundamentals';
const assetDir = 'motion-canvas/src/projects/ai-era-cs-fundamentals/assets';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const manifest = read(`${projectDir}/project.json`);
if(manifest.editing.narrationPlacement==='continuous-across-example-and-explanation')throw Error('Use scripts/build-ai-cs-continuous-audio.cjs for continuous narration; this legacy mixer assumes a silent lead');
const media = read(`${projectDir}/sources/selected-footage.json`);
const script = read(manifest.paths.script);
const timing = read(`${manifest.tts.outputDir}/${manifest.tts.filenameStem}.timing.json`);
const example = manifest.editing.exampleSeconds;
if (media.clipDuration !== example || timing.example_seconds !== example) throw Error('Example timing mismatch');
if (manifest.audio.backgroundMusic.file) throw Error('A BGM file is configured: use a verified continuous-BGM mixer instead');
const first = new Map();
for (const entry of timing.entries) if (!first.has(entry.scene_id)) first.set(entry.scene_id, entry.start);
const starts = script.scenes.map(scene => Math.round((first.get(scene.id) - example) * 30) / 30);
const duration = Math.round(timing.duration_seconds * 30) / 30;
if (starts[0] !== 0 || starts.some(x => !Number.isFinite(x))) throw Error('Invalid measured scene starts');
if (Math.abs(duration - manifest.video.durationSeconds) > .002) throw Error('Run build_project_timing.py first');
function execute(cmd, args) {
  const r = spawnSync(cmd, args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 20 * 1024 * 1024});
  if (r.status !== 0) throw Error(`${cmd}: ${r.stderr}`);
  return r;
}
const probe = file => JSON.parse(execute('ffprobe', ['-v','error','-show_streams','-show_format','-of','json',file]).stdout);
function loudness(file, start, seconds) {
  const seek = start === undefined ? [] : ['-ss', String(start), '-t', String(seconds)];
  const r = execute('ffmpeg', ['-hide_banner', ...seek, '-i', file, '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-']);
  const json = r.stderr.match(/\{\s*"input_i"[\s\S]*?\}/);
  if (!json) throw Error(`No loudness measurement: ${file}`);
  return JSON.parse(json[0]);
}
const wav = manifest.paths.narration;
if (Math.abs(Number(probe(wav).format.duration) - timing.duration_seconds) > .01) throw Error('WAV/timing mismatch');
const measured = loudness(wav);
if (!Number.isFinite(Number(measured.input_i))) throw Error('Silent narration');
const cfg = manifest.audio;
const voiceNorm = `loudnorm=I=${cfg.narrationTargetLufs}:TP=${cfg.truePeakDbtp}:LRA=9:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true`;
let args = ['-y','-v','warning','-i',wav];
const filters = [`[0:a]${voiceNorm},aresample=48000,aformat=channel_layouts=stereo,volume=${cfg.narrationPostNormalizationDb??0}dB,apad,atrim=0:${duration}[voice]`];
const tracks = ['[voice]'];
const scenes = [];
for (const clip of media.clips) {
  const index = Number(clip.scene) - 1;
  const file = `${assetDir}/broll/scene${clip.scene}.mp4`;
  const info = probe(file);
  if (!info.streams.some(s => s.codec_type === 'audio')) throw Error(`Missing source audio: ${file}`);
  if (Math.abs(Number(info.format.duration) - example) > .05) throw Error(`Wrong clip length: ${file}`);
  const input = tracks.length;
  const tag = `source${clip.scene}`;
  args.push('-i', file);
  filters.push(`[${input}:a]atrim=0:${example},asetpts=PTS-STARTPTS,loudnorm=I=${cfg.gameAudioTargetLufs}:TP=${cfg.truePeakDbtp}:LRA=9,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.08,afade=t=out:st=${example-.25}:d=0.25,adelay=${Math.round(starts[index]*48000)}S:all=1[${tag}]`);
  tracks.push(`[${tag}]`);
  const entries = timing.entries.filter(e => e.scene_id === clip.scene);
  scenes.push({scene:clip.scene,start:starts[index],clipDuration:example,hasSourceAudio:true,narrationStart:entries[0].start,narrationEnd:entries.at(-1).end});
}
// Leave AAC overshoot headroom. level=0 avoids the limiter adding hidden gain.
filters.push(`${tracks.join('')}amix=inputs=${tracks.length}:normalize=0:duration=longest,alimiter=limit=0.7943:level=0:latency=1,atrim=0:${duration}[mix]`);
const tempDir = fs.mkdtempSync(path.join(root,'shared/output/ai-cs-media-cache/narration-mix-'));
const temp = path.join(tempDir,'voice-source.m4a');
execute('ffmpeg', [...args,'-filter_complex',filters.join(';'),'-map','[mix]','-c:a','aac','-b:a','192k','-ar','48000',temp]);
if (Math.abs(Number(probe(temp).format.duration) - duration) > .05) throw Error('Invalid mixed duration');
const levels = loudness(temp);
if (Number(levels.input_tp) > cfg.truePeakDbtp + .1) throw Error(`True peak too high: ${levels.input_tp}`);
for (const scene of scenes) {
  scene.sourceMeasuredLufs = Number(loudness(temp,scene.start+.2,example-.5).input_i);
  scene.voiceMeasuredLufs = Number(loudness(temp,scene.narrationStart,scene.narrationEnd-scene.narrationStart).input_i);
  if (!Number.isFinite(scene.sourceMeasuredLufs) || scene.sourceMeasuredLufs < -40 || !Number.isFinite(scene.voiceMeasuredLufs) || scene.voiceMeasuredLufs < -25) throw Error(`Silent/low scene ${scene.scene}`);
}
const mix = `${assetDir}/narration-source-mix.m4a`;
const target = path.join(root,mix);
if (fs.existsSync(target)) fs.copyFileSync(target,path.join(tempDir,'previous-narration-source-mix.m4a'));
fs.copyFileSync(temp,target);
const report = {kind:'FULL TTS + SOURCE AUDIO REVIEW; BGM PENDING',createdAt:new Date().toISOString(),scriptRevision:manifest.scriptRevision,duration,narration:wav,mix,bgm:null,bgmPendingReason:'Blue Dream audio-library file and license details unavailable',narrationInputMeasurement:measured,mixedMeasurement:levels,scenes};
fs.writeFileSync(path.join(root,`${projectDir}/audio/narration-source-report.json`),JSON.stringify(report,null,2)+'\n');
const stamp = seconds => {const ms=Math.round(seconds*1000);return `${String(Math.floor(ms/60000)).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')}.${String(ms%1000).padStart(3,'0')}`;};
const csv = ['scene,start,end,segment_type,visual,source,source_audio,bgm,status'];
for (let i=0;i<script.scenes.length;i++) {
  const scene=script.scenes[i],clip=media.clips.find(c=>c.scene===scene.id),end=starts[i+1]??duration;
  let cursor=starts[i];
  for (const segment of clip.segments) {
    const length=segment.duration;
    csv.push([scene.id,stamp(cursor),stamp(cursor+length),'real-example',clip.title,`${clip.url} @ ${segment.start}s`,'retained-in-narration-source-mix','continuous-selected-not-acquired','measured-tts-v5'].map(x=>`"${String(x).replaceAll('"','""')}"`).join(','));
    cursor+=length;
  }
  for (const row of [
    [scene.id,stamp(starts[i]+example),stamp(end),'channel-explanation',scene.title,'original-motion-canvas','full-balanced-v5-tts','continuous-selected-not-acquired','measured-tts-v5'],
    [scene.id,stamp(starts[i]+example),stamp(starts[i]+example+manifest.editing.memeSeconds),'meme-overlay','자체 밈 연출 (설명 구간과 겹침)','sources/MEMES.md','no-borrowed-meme-audio','continuous-selected-not-acquired','overlays-explanation-do-not-add-duration'],
  ]) csv.push(row.map(x=>`"${String(x).replaceAll('"','""')}"`).join(','));
}
fs.writeFileSync(path.join(root,`${projectDir}/planning/edit-cues.csv`),csv.join('\n')+'\n');
console.log(`Created ${mix}: ${duration.toFixed(3)}s, twelve full voices and twelve source-audio clips; BGM pending.`);
