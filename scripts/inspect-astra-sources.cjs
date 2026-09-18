// Public source inspection only. Downloaded media are local, rights-pending research copies.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const base = path.join(root, 'projects/gpt-astra-showcase');
const cache = path.join(base, 'media/research');
const entries = [
  ['01', 'vib3coded', '2100350159540596760'],
  ['02', 'baku_lab', '2100523878628147641'],
  ['03', 'chongdashu', '2100569546776301667'],
  ['04', 'Stefan_3D_AI', '2100201776905633901'],
  ['05', 'cicicic66386703', '2100477846238212271'],
  ['06', 'cicicic66386703', '2097293343474774353'],
  ['07', 'aniketjart', '2100382480658518492'],
  ['08', 'RealFedeURU', '2100356546022584826'],
];
fs.mkdirSync(cache, {recursive:true});
async function get(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status}: ${url}`);
  return r;
}
async function inspect(entry) {
  const [index, author, id] = entry;
  const metadataFile = path.join(cache, `${index}-${id}.json`);
  const data = fs.existsSync(metadataFile) ? JSON.parse(fs.readFileSync(metadataFile, 'utf8')) : await (await get(`https://api.fxtwitter.com/${author}/status/${id}`)).json();
  if (data.code !== 200 || !data.tweet) throw new Error(`Missing public post ${id}`);
  fs.writeFileSync(metadataFile, JSON.stringify(data, null, 2)+'\n');
  const post = data.tweet;
  const videos = [];
  for (const [i, media] of (post.media?.all || []).entries()) {
    if (media.type !== 'video') continue;
    const variants = (media.variants || []).filter(v => v.content_type === 'video/mp4').map(v => {
      const match = v.url.match(/\/(\d+)x(\d+)\//);
      return {...v, height:match ? +match[2] : Infinity};
    }).filter(v => v.height <= 1080).sort((a,b) => b.bitrate-a.bitrate);
    const url = variants[0]?.url || media.url;
    const key = `${index}-${id}-${i+1}`;
    const file = path.join(cache, `${key}.mp4`);
    if (!fs.existsSync(file)) {
      fs.writeFileSync(file, Buffer.from(await (await get(url)).arrayBuffer()));
    }
    const probe = JSON.parse(execFileSync('ffprobe', ['-v','error','-show_format','-show_streams','-of','json',file],{encoding:'utf8',windowsHide:true}));
    const duration = +probe.format.duration;
    const sheet = path.join(cache, `${key}-contact.jpg`);
    if (!fs.existsSync(sheet)) {
      execFileSync('ffmpeg',['-v','error','-y','-ss','0.5','-i',file,'-vf',`fps=1/${Math.max(1,(duration-1)/6)},scale=480:-2,tile=3x2`,'-frames:v','1','-q:v','3',sheet],{stdio:'pipe',windowsHide:true});
    }
    videos.push({key, file:path.relative(root,file).replaceAll('\\','/'), contact:path.relative(root,sheet).replaceAll('\\','/'), duration, streams:probe.streams.map(s=>({codec_type:s.codec_type,codec_name:s.codec_name,width:s.width,height:s.height,r_frame_rate:s.r_frame_rate})), downloadedFrom:url});
  }
  console.log(`${index} @${author}: ${videos.length} videos inspected`);
  return {index, id, url:post.url, author:post.author.name, handle:author, text:post.text, createdAt:post.created_at, quoteText:post.quote?.text || null, rightsStatus:'unverified-no-explicit-reuse-license-in-post', videos};
}
(async()=>{
  const result=[];
  for(let i=0;i<entries.length;i+=3) result.push(...await Promise.all(entries.slice(i,i+3).map(inspect)));
  const out=path.join(base,'sources/posts.generated.json');
  fs.writeFileSync(out,JSON.stringify({inspectedAt:new Date().toISOString(),retrieval:'Public X media; post text retrieved through FxTwitter public mirror. Not a reuse license.',posts:result},null,2)+'\n');
  console.log(`Saved ${result.length} posts / ${result.flatMap(p=>p.videos).length} videos to ${out}`);
})().catch(error=>{console.error(error);process.exitCode=1;});
