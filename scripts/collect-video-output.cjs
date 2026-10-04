// Collect the four explicitly configured deliverables; never pick files by mtime.
// Usage: node scripts/collect-video-output.cjs <project-slug>
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const slug = process.argv[2];
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug || '')) throw Error('Provide a project slug.');
const project = path.join(root, 'projects', slug);
const manifest = JSON.parse(fs.readFileSync(path.join(project, 'project.json'), 'utf8'));
const p = manifest.paths;
const sources = {
  'captioned.mp4': p.videoBurnedCaptions || p.bodyVideoCaptioned,
  'clean.mp4': p.videoClean || p.bodyVideoClean,
  'ko.srt': p.captionsKo || p.subtitlesKo,
  'en.srt': p.captionsEn || p.subtitlesEn,
};
function inside(base, name) {
  const absolute = path.resolve(base, name);
  const relative = path.relative(base, absolute);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) throw Error('Unsafe path: ' + absolute);
  return absolute;
}
const run = (cmd, args) => {
  const r = spawnSync(cmd, args, {encoding:'utf8', windowsHide:true, maxBuffer:16e6});
  if (r.status !== 0) throw Error(r.stderr || r.error || `${cmd} failed`);
  return r.stdout;
};
const hash = async file => {
  const h = crypto.createHash('sha256');
  for await (const chunk of fs.createReadStream(file)) h.update(chunk);
  return h.digest('hex');
};
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page = (title, content) => `<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${esc(title)}</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.7 'Malgun Gothic',sans-serif;color:#202020;background:white}a{color:#24569b}video{width:100%;background:#eee}section{margin:32px 0}small{color:#666}.notice{padding:16px;border-left:4px solid #bb8624;background:#fff8e9}</style><h1>${esc(title)}</h1>${content}</html>`;
function srt(file) {
  const text = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '').trim();
  const cues = text.split(/\r?\n\s*\r?\n/).map((block, i) => {
    const lines = block.split(/\r?\n/);
    if (+lines[0] !== i+1 || !lines.slice(2).join('').trim()) throw Error(`Bad SRT cue ${i+1}: ${file}`);
    const match = /^(\d+):(\d{2}):(\d{2}),(\d{3}) --> (\d+):(\d{2}):(\d{2}),(\d{3})$/.exec(lines[1]);
    if (!match) throw Error('Bad SRT timecode');
    const time = j => +match[j]*3600 + +match[j+1]*60 + +match[j+2] + +match[j+3]/1000;
    return {start:time(1), end:time(5), timecode:lines[1]};
  });
  cues.forEach((c,i) => {if (!(c.start>=0 && c.end>c.start) || (i && c.start < cues[i-1].end-.001)) throw Error('Invalid/overlapping SRT');});
  return cues;
}
async function main() {
  for (const [key, value] of Object.entries(sources)) {
    if (!value) throw Error('Missing manifest path: ' + key);
    sources[key] = inside(root, value);
    if (!fs.statSync(sources[key]).isFile()) throw Error('Missing source file: ' + value);
  }
  const videos = ['captioned.mp4', 'clean.mp4'].map(key => {
    const info = JSON.parse(run('ffprobe', ['-v','error','-show_streams','-show_format','-of','json',sources[key]]));
    const v = info.streams.find(s=>s.codec_type==='video');
    if (!v || !info.streams.some(s=>s.codec_type==='audio')) throw Error('Video/audio stream missing: ' + key);
    return {duration:+info.format.duration,width:v.width,height:v.height,fps:v.r_frame_rate};
  });
  if (Math.abs(videos[0].duration-videos[1].duration)>.08 || videos[0].width!==videos[1].width || videos[0].height!==videos[1].height || videos[0].fps!==videos[1].fps) throw Error('Video pair does not match.');
  const ko=srt(sources['ko.srt']), en=srt(sources['en.srt']);
  if (Math.max(ko.at(-1).end,en.at(-1).end)>videos[0].duration+.05) throw Error('Subtitles extend beyond the video.');
  let captionAlignment = 'identical-cue-timing';
  if (JSON.stringify(ko)!==JSON.stringify(en)) {
    // Independent translations may need different clause lengths. Require a
    // current, directly reviewed paragraph map instead of accepting arbitrary timing.
    if (!p.captionAlignmentReview) throw Error('Subtitle timing mismatch: reviewed semantic paragraph alignment required.');
    const alignmentPath=inside(root,p.captionAlignmentReview);
    const alignment=JSON.parse(fs.readFileSync(alignmentPath,'utf8'));
    if (alignment.status!=='approved-semantic-paragraph-alignment' || alignment.approved!==true || alignment.manualSemanticReview!==true || alignment.allParagraphTextsRetained!==true || !alignment.paragraphs?.length) throw Error('Semantic caption review is incomplete.');
    for (const [language,cues] of [['ko',ko],['en',en]]) {
      const track=alignment.captions?.find(x=>x.language===language);
      if (!track || inside(root,track.path)!==sources[language+'.srt'] || track.sha256!==await hash(sources[language+'.srt']) || track.cues!==cues.length) throw Error('Semantic caption review is stale: '+language);
      const covered=[];
      for (const paragraph of alignment.paragraphs) {
        const indices=paragraph[language+'Cues'];
        if (!indices?.length || indices.some(n=>!Number.isInteger(n) || n<1 || n>cues.length)) throw Error('Invalid semantic caption paragraph.');
        if (Math.abs(cues[indices[0]-1].start-paragraph.start)>.002 || Math.abs(cues[indices.at(-1)-1].end-paragraph.end)>.002) throw Error('Semantic caption paragraph timing differs from review.');
        covered.push(...indices);
      }
      if (JSON.stringify(covered)!==JSON.stringify(cues.map((_,i)=>i+1))) throw Error('Semantic caption review omits or repeats cues.');
    }
    captionAlignment=p.captionAlignmentReview;
  }
  const outputRoot=path.join(root,'output');
  fs.mkdirSync(outputRoot,{recursive:true});
  if (fs.lstatSync(outputRoot).isSymbolicLink()) throw Error('Output root must not be a link.');
  const dest=inside(outputRoot,slug);
  if (fs.existsSync(dest) && fs.lstatSync(dest).isSymbolicLink()) throw Error('Output project must not be a link.');
  const production=path.join(project,'production');fs.mkdirSync(production,{recursive:true});
  const stage=fs.mkdtempSync(path.join(production,'delivery-stage-'));
  const files=[];
  for (const [key, source] of Object.entries(sources)) {
    const name=`${slug}.${key}`, target=path.join(stage,name);
    fs.copyFileSync(source,target,fs.constants.COPYFILE_EXCL);
    const sha256=await hash(source);
    if (sha256!==await hash(target)) throw Error('Copy hash mismatch: '+key);
    files.push({name,source:path.relative(root,source).replaceAll('\\','/'),bytes:fs.statSync(target).size,sha256});
  }
  const notices=[];
  if (!manifest.publishReady) notices.push('최신 완성 파일 모음입니다. 게시 승인 완료 상태는 아니며 최종 청취·잔여 검수를 확인하세요.');
  if (manifest.membershipOutro?.enabled && !manifest.membershipOutro.appliedToFinal) notices.push('멤버십 감사 엔딩 미포함 — 회원 원본 이미지 확보 후 추가 예정.');
  notices.push(...(manifest.finalRender?.knownIssues||[]),...(manifest.finalRender?.openItems||[]));
  const title=manifest.titles?.ko||slug;
  const links=files.map(f=>`<li><a href="${esc(f.name)}" download>${esc(f.name)}</a></li>`).join('');
  fs.writeFileSync(path.join(stage,'index.html'),page(title,`<p><a href="../index.html">전체 목록</a> · ${Math.floor(videos[0].duration/60)}분 ${Math.round(videos[0].duration%60)}초 · 한글 자막 ${ko.length}개 / 영어 자막 ${en.length}개</p>${notices.length?`<div class="notice">${notices.map(esc).join('<br>')}</div>`:''}<section><h2>한글 자막 영상</h2><video controls preload="metadata" src="${slug}.captioned.mp4"></video></section><section><h2>자막 없는 영상</h2><video controls preload="none" src="${slug}.clean.mp4"></video></section><h2>파일</h2><ul>${links}</ul><small>원본 작업 파일은 유지됩니다. SRT는 별도로 내려받아 편집기나 YouTube에 넣어 주세요.</small>`));
  // Preserve previous deliveries outside output, so output only shows the current set.
  if (fs.existsSync(dest)) {
    const archive=path.join(production,'delivery-history');fs.mkdirSync(archive,{recursive:true});
    const saved=inside(archive,new Date().toISOString().replace(/[:.]/g,'-'));
    if (fs.existsSync(saved)) throw Error('Archive collision');
    fs.renameSync(dest,saved);
  }
  fs.renameSync(stage,dest);
  const report={slug,createdAt:new Date().toISOString(),directory:`output/${slug}`,publishReady:!!manifest.publishReady,notices,videos,cues:ko.length,cueCounts:{ko:ko.length,en:en.length},captionAlignment,files};
  fs.writeFileSync(path.join(production,'delivery-output.json'),JSON.stringify(report,null,2)+'\n');
  require('./build-rebuild-manifests.cjs').generate(slug);
  const projects=fs.readdirSync(outputRoot,{withFileTypes:true}).filter(e=>e.isDirectory()&&!e.isSymbolicLink()&&fs.existsSync(path.join(outputRoot,e.name,'index.html')));
  fs.writeFileSync(path.join(outputRoot,'index.html'),page('영상 결과물 모음',`<p>프로젝트마다 자막 영상·무자막 영상·한글 SRT·영어 SRT를 모았습니다. 게시 전 확인 사항은 각 페이지에 표시됩니다.</p><ul>${projects.map(e=>`<li><a href="${encodeURIComponent(e.name)}/index.html">${esc(e.name)}</a></li>`).join('')}</ul>`));
  console.log(JSON.stringify({directory:dest,files:files.map(f=>f.name),duration:videos[0].duration,cues:ko.length,publishReady:!!manifest.publishReady}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
