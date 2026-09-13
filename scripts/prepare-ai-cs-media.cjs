// Reproducible licensed B-roll preparation; raw stock is a private cache.
// node scripts/prepare-ai-cs-media.cjs acquire|contacts|trim [sceneId]
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {Readable} = require('node:stream');
const {pipeline} = require('node:stream/promises');
const root = path.resolve(__dirname, '..');
const config = JSON.parse(fs.readFileSync(path.join(root, 'projects/ai-era-cs-fundamentals/sources/selected-footage.json'), 'utf8'));
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects/ai-era-cs-fundamentals/project.json'), 'utf8'));
if(config.clipDuration!==manifest.editing.exampleSeconds) throw Error('Example length differs from manifest');
const cache = path.join(root, 'shared/output/ai-cs-media-cache');
const dest = path.join(root, 'motion-canvas/src/projects/ai-era-cs-fundamentals/assets/broll');
const py = path.join(root, 'qwen3-tts/.venv/Scripts/python.exe');
const rawPath = c => path.join(cache,c.rawFile || `${c.scene}.mp4`);
const mode = process.argv[2];
const requestedScenes = process.argv[3]?.split(',').map(id=>id.padStart(2,'0'));
if(requestedScenes?.some(id=>!config.clips.some(c=>c.scene===id))) throw Error('Unknown scene ID');
const clips = config.clips.filter(c => !requestedScenes || requestedScenes.includes(c.scene));
fs.mkdirSync(cache, {recursive:true}); fs.mkdirSync(dest, {recursive:true});
function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {cwd:root, windowsHide:true}); let out = ''; let err = '';
    child.stdout.on('data', d => out += d); child.stderr.on('data', d => err += d);
    child.on('error', reject); child.on('close', code => code ? reject(new Error(`${cmd} (${code}): ${err.slice(-4000)}`)) : resolve(out));
  });
}
async function get(url) {const r = await fetch(url); if (!r.ok) throw Error(`${url}: ${r.status}`); return r;}
async function acquire(c) {
  const raw = rawPath(c);
  if (fs.existsSync(raw)) return console.log(`exists ${c.scene}`);
  if (c.provider === 'mixkit') {
    const page = await (await get(c.url)).text();
    if (!page.includes('data-license="videoFree"')) throw Error(`${c.scene}: not explicitly videoFree`);
    const endpoint = page.match(new RegExp(`(/free-stock-video/download/${c.id}/[^"<>]*type=1080p)`));
    if (!endpoint) throw Error(`${c.scene}: no advertised 1080p download`);
    const modal = await (await get(`https://mixkit.co${endpoint[1].replaceAll('&amp;', '&')}`)).text();
    const url = modal.match(/data-download--modal-url-value="([^"]+)"/)?.[1];
    if (!url) throw Error('No download URL');
    fs.writeFileSync(path.join(cache, `${c.scene}-license.html`), page);
    await pipeline(Readable.fromWeb((await get(url)).body), fs.createWriteStream(raw));
    fs.writeFileSync(path.join(cache, `${c.scene}-source.json`), JSON.stringify({url,license:'videoFree',checkedAt:new Date().toISOString()}, null, 2));
  } else {
    const meta = JSON.parse(await run(py, ['-m','yt_dlp','--js-runtimes','node','--skip-download','--dump-single-json',c.url]));
    if(c.provider==='youtubecc') {
      if(!/Creative Commons Attribution/i.test(meta.license||'') || meta.channel_id!==c.channelId) throw Error('CC license / uploader mismatch');
    } else if(c.provider==='gdquest') {
      if(meta.channel_id!==c.channelId || c.channelId!=='UCxboW7x0jZqFdvMdCFKTMsQ' ||
        !/CC-BY(?: 4\.0)? LICENSE/i.test(meta.description||'') ||
        !(meta.description||'').includes('https://creativecommons.org/licenses/by/4.0/')) throw Error('GDQuest explicit video license / uploader mismatch');
    } else if(c.provider!=='pyconjp' || (!/pycon.?jp/i.test(meta.uploader || '') && !/pyconjp/i.test(meta.uploader_id || ''))) throw Error(`Channel mismatch ${meta.uploader}`);
    fs.writeFileSync(path.join(cache, `${c.scene}-${c.id}-source.json`), JSON.stringify({id:meta.id,url:c.url,title:meta.title,uploader:meta.uploader,channel:meta.channel_url,channelId:meta.channel_id,duration:meta.duration,description:meta.description,chapters:meta.chapters,licensePolicy:config.licenses[c.provider].policy,checkedAt:new Date().toISOString()}, null, 2));
    await run(py, ['-m','yt_dlp','--js-runtimes','node','--no-playlist','-f','bv[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]','--merge-output-format','mp4','-o',raw,c.url]);
  }
  console.log(`downloaded ${c.scene}: ${Math.round(fs.statSync(raw).size/1e6)} MB`);
}
async function probe(file) {return JSON.parse(await run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]));}
async function contacts(c) {
  const raw = rawPath(c); const p = await probe(raw); const d = Number(p.format.duration);
  const times = Array.from({length:12},(_,i)=>process.argv[4]?Number(process.argv[4])+i*Number(process.argv[5]||10):c.provider==='mixkit'?(i+.5)*d/12:(i+1)*d/14);
  for(let i=0;i<times.length;i++) await run('ffmpeg',['-y','-v','error','-ss',String(times[i]),'-i',raw,'-frames:v','1','-vf',`scale=480:-2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='${c.scene}  ${times[i].toFixed(1)} sec':fontsize=22:fontcolor=white:box=1:boxcolor=black@0.8:x=8:y=8`,path.join(cache,`${c.scene}-frame-${String(i).padStart(2,'0')}.jpg`)]);
  await run('ffmpeg',['-y','-v','error','-i',path.join(cache,`${c.scene}-frame-%02d.jpg`),'-vf','tile=3x4','-frames:v','1',path.join(cache,`${c.scene}-contact.jpg`)]);
  console.log(`contact ${c.scene} duration=${d} audio=${p.streams.some(s=>s.codec_type==='audio')}`);
}
async function trim(c) {
  const output=path.join(dest,`scene${c.scene}.mp4`);
  const backup=path.join(cache,`archive-v${config.revision-1}`,`scene${c.scene}.mp4`);
  if(fs.existsSync(output)&&!fs.existsSync(backup)){fs.mkdirSync(path.dirname(backup),{recursive:true});fs.copyFileSync(output,backup);}
  const segments=c.segments; const args=['-y','-v','error']; const filters=[];
  let hasAudio=false; const audioFlags=[];
  for(let i=0;i<segments.length;i++) {
    const s=segments[i],src=config.clips.find(x=>x.scene===s.sourceScene),raw=rawPath(src),info=await probe(raw);
    if(s.start<0||Number(info.format.duration)+.001<s.start+s.duration) throw Error(`Source too short: ${c.scene} segment ${i}`);
    const audio=info.streams.some(x=>x.codec_type==='audio');hasAudio ||= audio;audioFlags.push(audio);
    args.push('-ss',String(s.start),'-t',String(s.duration),'-i',raw);
    filters.push(`[${i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=PTS-STARTPTS,fps=60:start_time=0,trim=end_frame=${Math.round(s.duration*60)},setpts=PTS-STARTPTS[v${i}]`);
  }
  if(Math.abs(segments.reduce((n,s)=>n+s.duration,0)-config.clipDuration)>.001)throw Error('Segment durations do not fill the example slot');
  if(hasAudio)for(let i=0;i<segments.length;i++) {
    const d=segments[i].duration;
    filters.push(audioFlags[i]?`[${i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:${d},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st=${d-.02}:d=0.02[a${i}]`:`anullsrc=r=48000:cl=stereo:d=${d}[a${i}]`);
  }
  filters.push(segments.map((_,i)=>`[v${i}]${hasAudio?`[a${i}]`:''}`).join('')+`concat=n=${segments.length}:v=1:a=${hasAudio?1:0}[out]${hasAudio?'[sound]':''}`);
  const part=path.join(cache,`scene${c.scene}-v${config.revision}-render.mp4`);
  await run('ffmpeg',[...args,'-filter_complex',filters.join(';'),'-map','[out]',...(hasAudio?['-map','[sound]']:[]),'-t',String(config.clipDuration),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',part]);
  const result=await probe(part),video=result.streams.find(s=>s.codec_type==='video');
  if(Number(video.nb_frames)!==Math.round(config.clipDuration*60))throw Error('Unexpected output frame count');
  fs.copyFileSync(part,output);
  fs.writeFileSync(path.join(cache,`${c.scene}-trim-report.json`),JSON.stringify({scene:c.scene,segments,duration:Number(result.format.duration),hasSourceAudio:hasAudio,videoFrames:video.nb_frames},null,2));
  console.log(`trimmed ${c.scene}: ${segments.length} cut(s), ${config.clipDuration}s`);
}
(async()=>{if(!['acquire','contacts','trim'].includes(mode)) throw Error('Usage: acquire|contacts|trim [sceneId]'); let queue=[...clips]; await Promise.all(Array.from({length:2},async()=>{while(queue.length){const c=queue.shift();await ({acquire,contacts,trim}[mode])(c);}}));})().catch(e=>{console.error(e);process.exitCode=1;});
