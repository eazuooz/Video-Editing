// Local narrated review: preserve picture timing, approved voice and source media.
// Publication permissions for the third-party examples remain a separate gate.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const slug = 'gpt-astra-showcase';
const base = path.join(root, 'projects', slug);
const manifest = JSON.parse(fs.readFileSync(path.join(base, 'project.json'), 'utf8'));
const plan = JSON.parse(fs.readFileSync(path.join(root, manifest.editing.plan), 'utf8'));
const posts = JSON.parse(fs.readFileSync(path.join(base, 'sources/posts.generated.json'), 'utf8')).posts;
const script = JSON.parse(fs.readFileSync(path.join(root, manifest.paths.script), 'utf8'));
const out = path.join(root, manifest.tts.outputDir), stem = manifest.tts.filenameStem;
const cache = path.join(base, 'review', `audio-v${plan.version}`);
const A = manifest.audio, duration = plan.durationSeconds;
fs.mkdirSync(cache, {recursive: true});
if (!manifest.approvals.voice.startsWith('approved') || !manifest.approvals.music.startsWith('approved')) throw Error('Voice and music approvals required');
const json = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
const hash = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function run(cmd, args) {
  const result = spawnSync(cmd, args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 16e6});
  if (result.status !== 0) throw Error(result.stderr || String(result.error));
  return result.stdout + result.stderr;
}
const ff = args => run('ffmpeg', ['-hide_banner', '-nostats', ...args]);
const probe = f => JSON.parse(run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', f]));
function meter(file, target = -16) {
  const log = ff(['-i', file, '-vn', '-af', `aformat=channel_layouts=stereo,loudnorm=I=${target}:TP=-2:LRA=11:print_format=json`, '-f', 'null', '-']);
  return JSON.parse(log.slice(log.lastIndexOf('{'), log.lastIndexOf('}') + 1));
}
function concatAudio(parts, dest) {
  const list = dest + '.ffconcat';
  fs.writeFileSync(list, 'ffconcat version 1.0\n' + parts.map(f => `file '${f.replaceAll('\\', '/')}'`).join('\n') + '\n');
  ff(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', dest]);
}
function normalize(input, dest, target) {
  const cacheFile = dest + '.json', identity = {sha256: hash(input), target, version: 2};
  if (fs.existsSync(dest) && fs.existsSync(cacheFile)) {
    const cached = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
    if (JSON.stringify(cached.identity) === JSON.stringify(identity)) return cached;
  }
  const measured = meter(input, target);
  if (!Number.isFinite(Number(measured.input_i))) throw Error('Silent normalization input: ' + input);
  const filter = `aformat=channel_layouts=stereo,loudnorm=I=${target}:TP=-2:LRA=11:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true`;
  ff(['-v', 'error', '-y', '-i', input, '-vn', '-af', filter, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', dest]);
  let normalized=meter(dest,target);const corrections=[];
  for(let pass=0;pass<2&&Math.abs(+normalized.input_i-target)>.2;pass++){
    const gain=target-Number(normalized.input_i),corrected=dest+'.corrected.wav';
    ff(['-v','error','-y','-i',dest,'-af',`volume=${gain}dB,alimiter=limit=0.794:level=false:latency=true`,'-ar','48000','-ac','2','-c:a','pcm_s16le',corrected]);
    fs.renameSync(corrected,dest);corrections.push(gain);normalized=meter(dest,target);
  }
  if(Math.abs(+normalized.input_i-target)>.75)throw Error('Loudness target not reached: '+dest);
  const report = {identity, input: measured, normalized, correctionGainsDb:corrections};
  json(cacheFile, report);
  console.log(`Normalized ${path.basename(dest)}: ${report.normalized.input_i} LUFS`);
  return report;
}
let clock = 0;
const scenes = plan.scenes.map(s => {
  const scene = {...s, start: clock, example: s.cuts.reduce((n, c) => n + c.out - c.in, 0)};
  clock += s.duration;
  return scene;
});
if (Math.abs(clock - duration) > 1e-6) throw Error('Plan total mismatch');
const timelineWav = path.join(out, stem + '.timeline.wav');
const normalizedVoice = path.join(cache, 'narration-normalized.wav');

function assemblePicture(){
  const pieces=[];
  for(const s of scenes){
    if(s.example)pieces.push(path.join(root,`motion-canvas/src/projects/${slug}/assets/examples/scene${s.id}.mp4`));
    const remaining=s.duration-s.example;
    if(remaining>0){
      const file=path.join(root,`shared/output/motion-canvas/astra-review-v${plan.reuseGraphicsVersion??plan.version}-graphics-${s.id}.mp4`);
      if(+probe(file).streams.find(v=>v.codec_type==='video').nb_frames!==Math.round(remaining*plan.fps))throw Error('Reused graphic length mismatch');
      pieces.push(file);
    }
  }
  const list=path.join(base,'review',`picture-v${plan.version}.ffconcat`);
  fs.writeFileSync(list,'ffconcat version 1.0\n'+pieces.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n')+'\n');
  const target=path.join(root,manifest.paths.pictureReview);
  if(fs.existsSync(target))throw Error('Preserve existing picture; choose new revision');
  ff(['-v','error','-n','-f','concat','-safe','0','-i',list,'-map','0:v:0','-an','-c:v','copy','-movflags','+faststart',target]);
  const info=probe(target);
  if(+info.streams[0].nb_frames!==Math.round(duration*plan.fps))throw Error('Picture frame count mismatch');
  json(path.join(base,'review',`picture-assembly-v${plan.version}.json`),{duration,frames:+info.streams[0].nb_frames,pieces,sourceFootageSeconds:scenes.reduce((n,s)=>n+s.example,0),middleSummarySeconds:scenes.filter(s=>s.example).reduce((n,s)=>n+s.duration-s.example,0),introOutroRetained:true});
  console.log('Picture assembled: '+target);
}

function prepareNarration() {
  const timingPath = path.join(out, stem + '.timing.json');
  const rawTimingPath = path.join(out, stem + '.timing.speech-only.json');
  const current = JSON.parse(fs.readFileSync(timingPath, 'utf8'));
  if (!fs.existsSync(rawTimingPath)) {
    if (current.timeline_source) throw Error('Missing original speech timing');
    fs.copyFileSync(timingPath, rawTimingPath);
  }
  const raw = JSON.parse(fs.readFileSync(rawTimingPath, 'utf8'));
  const entries = [], parts = [], normalizedParts = [], reports = [];
  for (const s of scenes) {
    const wav = path.join(out, 'chunks', `${s.id}-scene.wav`);
    const speechSeconds = +probe(wav).format.duration;
    if (speechSeconds + .15 > s.duration) throw Error(`Scene ${s.id}: speech ${speechSeconds}s exceeds available ${s.duration}s; extend picture without changing voice speed`);
    const sourceEntries = raw.entries.filter(e => e.scene_id === s.id), origin = sourceEntries[0].start;
    if (sourceEntries.length !== script.scenes.find(x => x.id === s.id).lines.length) throw Error('Caption count mismatch');
    for (const e of sourceEntries) entries.push({...e, start: s.start + e.start - origin, end: s.start + e.end - origin});
    const rawPart = path.join(cache, `voice-${s.id}-padded.wav`);
    const normalized = path.join(cache, `voice-${s.id}-normalized.wav`);
    const normalizedPart = path.join(cache, `voice-${s.id}-normalized-padded.wav`);
    const loudness = normalize(wav, normalized, A.narrationTargetLufs);
    for (const [input, dest] of [[wav, rawPart], [normalized, normalizedPart]]) {
      ff(['-v', 'error', '-y', '-i', input, '-af', `afade=t=in:d=0.006,afade=t=out:st=${speechSeconds-.006}:d=0.006,apad,atrim=duration=${s.duration}`, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', dest]);
    }
    parts.push(rawPart); normalizedParts.push(normalizedPart);
    reports.push({scene: s.id, start: s.start, duration: s.duration, speechSeconds, wavSha256: hash(wav), loudness});
  }
  concatAudio(parts, timelineWav); concatAudio(normalizedParts, normalizedVoice);
  json(timingPath, {...raw, duration_seconds: duration, sample_rate: 48000, timeline_source: manifest.editing.plan, entries, scenes: reports.map(({loudness, ...r}) => r)});
  json(path.join(cache, 'narration-report.json'), reports);
  console.log(`Narration placed without speed changes: ${duration}s`);
}

function mixAndMux() {
  const bedOnly=process.argv.includes('--prepare-bed');
  if (!bedOnly && !fs.existsSync(normalizedVoice)) throw Error('Run --prepare-narration first');
  const music = path.join(root, A.backgroundMusic.file);
  if (hash(music) !== A.backgroundMusic.sha256) throw Error('Approved music hash mismatch');
  const musicNormalized = path.join(cache, 'music-normalized.wav');
  const musicMeter = normalize(music, musicNormalized, A.bgmTargetLufs);
  const parts = [], sourceReports = [], activeRanges = [], fallbacks = [];
  for (const s of scenes) {
    let offset = s.start, audible = false;
    const post = posts.find(p => p.index === s.post);
    for (const [i, cut] of s.cuts.entries()) {
      const media = post.videos[cut.video - 1], len = cut.out - cut.in;
      const source = path.join(root, media.file), raw = path.join(cache, `source-${s.id}-${i+1}-raw.wav`);
      const normalized = path.join(cache, `source-${s.id}-${i+1}-normalized.wav`), final = path.join(cache, `source-${s.id}-${i+1}.wav`);
      const hasAudio = media.streams.some(x => x.codec_type === 'audio');
      const extraction = hasAudio ? ['-ss', String(cut.in), '-i', source, '-vn', '-af', `apad,atrim=duration=${len}`] : ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'];
      ff(['-v', 'error', '-y', ...extraction, '-t', String(len), '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', raw]);
      const level = meter(raw, -31), isAudible = hasAudio && Number.isFinite(+level.input_i) && +level.input_i > -65;
      let stats = null;
      if (isAudible) {
        // Keep source music/commentary subordinate to the approved narration.
        stats = normalize(raw, normalized, A.sourceReviewTargetLufs ?? -31);
        ff(['-v', 'error', '-y', '-i', normalized, '-af', `afade=t=in:d=0.12,afade=t=out:st=${len-.3}:d=0.3,apad,atrim=duration=${len}`, '-ar', '48000', '-ac', '2', final]);
        activeRanges.push([offset, offset + len]); audible = true;
      } else fs.copyFileSync(raw, final);
      parts.push(final); sourceReports.push({scene: s.id, cut: i+1, source: media.file, in: cut.in, out: cut.out, audible: isAudible, stats});
      offset += len;
    }
    if (s.example && !audible) fallbacks.push(s.id);
    const rest = s.duration - s.example, silence = path.join(cache, `silence-${s.id}.wav`);
    if (rest) { ff(['-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', String(rest), silence]); parts.push(silence); }
  }
  const sourceBus = path.join(cache, 'source-only.wav'); concatAudio(parts, sourceBus);
  // Merge adjacent cuts so BGM attenuation does not pump at every cut.
  const merged = [];
  for (const range of activeRanges) {
    const last = merged.at(-1);
    if (last && Math.abs(last[1] - range[0]) < .001) last[1] = range[1]; else merged.push([...range]);
  }
  const cross = A.bgmLoopCrossfadeSeconds, fullMusicDuration = +probe(musicNormalized).format.duration;
  // Join before the track's quiet ending so continuous music does not drop out.
  const musicDuration = A.bgmLoopEndSeconds ?? fullMusicDuration;
  if(musicDuration>fullMusicDuration||musicDuration<=cross)throw Error('Invalid music loop region');
  const repeats = Math.max(1, Math.ceil((duration-cross)/(musicDuration-cross)));
  const inputs = Array.from({length: repeats}, () => ['-i', musicNormalized]).flat(), filters = [];
  for(let i=0;i<repeats;i++)filters.push(`[${i}:a]atrim=duration=${musicDuration},asetpts=PTS-STARTPTS[m${i}]`);
  let prev = 'm0';
  for (let i=1; i<repeats; i++) { filters.push(`[${prev}][m${i}]acrossfade=d=${cross}:c1=tri:c2=tri[b${i}]`); prev = `b${i}`; }
  const envelope = merged.map(([a,b]) => `max(0,min(1,min((t-${a})/0.45,(${b}-t)/0.45)))`).reduce((a,b) => `max(${a},${b})`, '0');
  const bgm = path.join(cache, 'bgm-only-before-narration-ducking.wav');
  filters.push(`[${prev}]atrim=duration=${duration},volume='pow(10,${A.bgmDuringGameplayDb}/20*(${envelope}))':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${duration-.45}:d=0.45[bgm]`);
  ff(['-v', 'error', '-y', ...inputs, '-filter_complex', filters.join(';'), '-map', '[bgm]', '-ar', '48000', '-ac', '2', bgm]);
  if (bedOnly) {json(path.join(cache, 'bed-report.json'), {duration, musicMeter, sourceReports, musicFallbackScenes:fallbacks, musicRepeats:repeats, bgm, sourceBus});console.log('Continuous music + quiet source stems prepared.');return;}
  const mix = path.join(cache, 'final-mix.wav'), background = path.join(cache, 'background-only.wav');
  const duck = `sidechaincompress=threshold=${A.duckingThreshold}:ratio=${A.duckingRatio}:attack=15:release=280:makeup=1`;
  // Match the approved sample: duck the quiet source + music bus together.
  const graph = `[0:a]asplit=2[n][key];[1:a][2:a]amix=inputs=2:normalize=0[bed];[bed][key]${duck},asplit=2[bg][bgout];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=${A.limiterCeilingLinear ?? 0.82}:level=false:latency=true,atrim=duration=${duration}[out]`;
  ff(['-v', 'error', '-y', '-i', normalizedVoice, '-i', sourceBus, '-i', bgm, '-filter_complex', graph, '-map', '[out]', '-ar', '48000', '-ac', '2', mix, '-map', '[bgout]', '-ar', '48000', '-ac', '2', background]);
  const aac = path.join(root, manifest.paths.audioMix), editor = path.join(root, manifest.paths.editorAudioMix);
  ff(['-v', 'error', '-y', '-i', mix, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', aac]);
  ff(['-v', 'error', '-y', '-i', aac, '-af', `apad,atrim=duration=${duration}`, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', editor]);
  const finalLevels = meter(aac);
  if (+finalLevels.input_tp > A.truePeakDbtp) throw Error(`AAC peak ${finalLevels.input_tp} exceeds ${A.truePeakDbtp} dBTP ceiling`);
  const target = path.join(root, manifest.paths.videoClean);
  if (fs.existsSync(target)) throw Error('Preserve existing narrated output; choose a new version');
  ff(['-v', 'error', '-n', '-i', path.join(root, manifest.paths.pictureReview), '-i', aac, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-t', String(duration), '-movflags', '+faststart', target]);
  for (const [key, suffix] of [['captionsKo', '.ko.srt'], ['captionsEn', '.en.srt']]) fs.copyFileSync(path.join(root, manifest.paths[key]), target.replace(/\.mp4$/, suffix));
  const info = probe(target), video = info.streams.find(s => s.codec_type === 'video');
  if (+video.nb_frames !== Math.round(duration*plan.fps) || Math.abs(+info.format.duration-duration)>.06) throw Error('Mux timing mismatch');
  ff(['-v', 'error', '-i', target, '-f', 'null', '-']);
  const levels = [];
  for (const s of scenes) for (const kind of ['speech', 'tail']) {
    const sec = s.start + (kind==='speech' ? 1 : s.duration - 2);
    const layerLevels = {};
    for (const [layer, file] of Object.entries({voice:normalizedVoice, source:sourceBus, bgm, background})) {
      const log=ff(['-ss', String(sec), '-t', '1', '-i', file, '-af', 'volumedetect', '-f', 'null', '-']);
      layerLevels[layer]=Number(log.match(/mean_volume:\s*([-\d.]+) dB/)?.[1] ?? -100);
    }
    if (layerLevels.bgm < -65 || (kind==='speech' && layerLevels.voice < -60)) throw Error('Missing layer: '+s.id+' '+kind);
    levels.push({scene:s.id, kind, seconds:sec, meanDbfs:layerLevels});
  }
  json(path.join(cache, 'mix-report.json'), {duration, pictureStreamCopied:true, fullDecodePassed:true, finalLevels, music: A.backgroundMusic.title, musicMeter, sourceTargetLufs:A.sourceReviewTargetLufs??-31, sourceReports, musicFallbackScenes:fallbacks, musicRepeats:repeats, musicLoopEndSeconds:musicDuration, loopCrossfadeSeconds:cross, continuousBgm:true, levels, aac, editor, target, publishReady:false, sourceReuse:'pending', humanFullListening:'pending'});
  console.log('Narrated review ready: '+target);
}
if (process.argv.includes('--assemble-picture')) assemblePicture();
else if (process.argv.includes('--prepare-narration')) prepareNarration();
else if (process.argv.includes('--mix') || process.argv.includes('--prepare-bed')) mixAndMux();
else throw Error('Use --prepare-narration, align subtitles, then --mix');
