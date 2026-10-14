// A local listening index. Generated narration is never treated as approved.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const clock = value => `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, '0')}`;
const episodes = [];
for (const number of [1, 2, 3, 4]) {
  const slug = `game-lighting-history-${String(number).padStart(2, '0')}`;
  const manifest = read(path.join(root, 'projects', slug, 'project.json'));
  const ko = read(path.join(root, manifest.paths.script));
  const en = read(path.join(root, manifest.paths.scriptEn));
  let audioPath, timingPath;
  if (number === 1) {
    const current = read(path.join(root, 'projects', slug, 'production/tts-repair-completion-v4.json'));
    audioPath = path.join(root, current.audio.file);
    timingPath = path.join(root, current.timing.file);
    if (sha(audioPath) !== current.audio.sha256) throw Error('Current episode1 WAV changed.');
  } else {
    const stem = path.join(root, manifest.tts.outputDir, manifest.tts.filenameStem);
    audioPath = stem + '.wav';
    timingPath = stem + '.timing.json';
  }
  const available = fs.existsSync(audioPath) && fs.existsSync(timingPath);
  const timing = available ? read(timingPath) : null;
  const pairCount = ko.scenes.reduce((sum, scene) => sum + scene.lines.length, 0);
  if (timing && timing.entries.length !== pairCount) throw Error(slug + ': paragraph count changed.');
  let index = 0;
  const paragraphs = ko.scenes.flatMap((scene, sceneIndex) => {
    const translation = en.scenes[sceneIndex];
    if (translation.id !== scene.id || translation.lines.length !== scene.lines.length) throw Error(slug + ': bilingual topology differs.');
    return scene.lines.map((text, lineIndex) => {
      const entry = timing?.entries[index++];
      if (entry && (entry.scene_id !== scene.id || entry.text !== text)) throw Error(slug + ': displayed script differs from current measured take.');
      return {scene: scene.id, title: scene.title, ko: text, en: translation.lines[lineIndex], start: entry?.start, end: entry?.end};
    });
  });
  episodes.push({number, slug, title: ko.title, audioPath, available, durationSeconds: timing?.duration_seconds ?? null,
    audioSha256: available ? sha(audioPath) : null, sceneCount: ko.scenes.length, paragraphPairs: pairCount,
    paragraphs, currentNarrationApproved: false, humanWholeListeningApproved: false, finalVideoProduced: false});
}
if (process.argv.includes('--require-all') && episodes.some(e => !e.available)) throw Error('Four measured WAVs required.');
const generated = episodes.filter(e => e.available).length;
const cards = episodes.map(e => `<section id="episode-${e.number}"><h2>${e.number}편 · ${escape(e.title)}</h2>
<p class="state">${e.available ? `음성 생성됨 · 실측 ${clock(e.durationSeconds)} · ${e.sceneCount}장 / ${e.paragraphPairs}문단` : '음성 생성 대기'} · 청취·발음 승인 대기</p>
${e.available ? `<audio id="audio-${e.number}" controls preload="metadata" src="${escape(pathToFileURL(e.audioPath).href)}"></audio><p class="hash">WAV SHA256 ${e.audioSha256}</p>` : ''}
<details><summary>한영 대본 ${e.paragraphPairs}문단 펼치기</summary>${e.paragraphs.map((p, i) => `<article><h3>${escape(p.scene)} · ${escape(p.title)} · ${i + 1}번 문단${p.start === undefined ? '' : ` <button data-audio="audio-${e.number}" data-time="${p.start}">${clock(p.start)} 듣기</button>`}</h3><p>${escape(p.ko)}</p><p lang="en">${escape(p.en)}</p></article>`).join('')}</details></section>`).join('\n');
const html = `<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>렌더링 역사 4편 · 내레이션 검토</title>
<style>body{max-width:1000px;margin:40px auto;padding:0 24px;font-family:system-ui,sans-serif;line-height:1.7;background:#f6f7f4;color:#17231d}h1{font-size:30px}h2{font-size:23px}section{background:white;border:1px solid #cbd4cc;padding:24px;margin:24px 0}audio{width:100%}.state{font-weight:600;color:#315b41}.hash{font:12px monospace;overflow-wrap:anywhere;color:#5e6b62}summary,button{cursor:pointer}article{padding:12px 0;border-bottom:1px solid #e4e9e4}h3{font-size:15px}p[lang=en]{color:#5e6962}button{border:1px solid #5d7764;background:#eef5ee;border-radius:4px;padding:5px 10px;margin-left:8px}nav a{display:inline-block;margin-right:20px;color:#315b41}</style>
<h1>게임 렌더링 역사 · 4편 내레이션 검토</h1><p>현재 ${generated}/4편의 실측 음성이 있습니다. 이 페이지는 대본과 생성 음성을 비교하는 검토본입니다. 사람 전체 청취·기술 발음·정확한 단어 자막 정렬·최종 혼합 ASR·2.5D 장면 및 실제 시연의 최종 픽셀·비공개 업로드는 별도 검수 단계입니다.</p><p>문단 이동 시각은 생성기의 임시 배분값이며 단어 단위 승인 타이밍이 아닙니다. 기존 음성과 대본을 수정하지 않습니다.</p><nav>${episodes.map(e=>`<a href="#episode-${e.number}">${e.number}편</a>`).join('')}</nav>${cards}
<script>document.addEventListener('click',event=>{const button=event.target.closest('button[data-audio]');if(!button)return;const selected=document.getElementById(button.dataset.audio);document.querySelectorAll('audio').forEach(a=>{if(a!==selected)a.pause()});selected.currentTime=Number(button.dataset.time);selected.play().catch(()=>{});});</script></html>`;
const htmlPath = path.join(__dirname, 'narration-review.html');
fs.writeFileSync(htmlPath, html);
fs.writeFileSync(path.join(__dirname, 'narration-review-index.json'), JSON.stringify({builtAt:new Date().toISOString(),generatedEpisodes:generated,allFourNarrationsGenerated:generated===4,episodes:episodes.map(({paragraphs,...e})=>e),currentNarrationApproved:false,finalVideoProduced:false},null,2)+'\n');
console.log(JSON.stringify({html:htmlPath,generatedEpisodes:generated,approvedEpisodes:0}));
