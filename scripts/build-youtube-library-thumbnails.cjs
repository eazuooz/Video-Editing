const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const puppeteer = require(path.join(root, 'motion-canvas', 'node_modules', 'puppeteer'));
const outputRoot = path.join(root, 'output', 'youtube-library-refresh');
const inventory = JSON.parse(fs.readFileSync(path.join(outputRoot, 'inventory.json'), 'utf8'));
const basesDir = path.join(outputRoot, 'bases');
const thumbnailsDir = path.join(outputRoot, 'thumbnails');
fs.mkdirSync(thumbnailsDir, {recursive: true});

const configs = {
  PLUU7_j2ihric: config('GAME DESIGN', '게임 디자인·테크', '게임 디자인', '#5DE1FF', 'course'),
  'PLWKwcHKTXy5T9P4uAQGAe5vsSzx-G2ihN': config('GRAPHICS PAPER', '그래픽스 논문', '그래픽스 논문 리뷰', '#67E8F9', 'course'),
  'PLWKwcHKTXy5SKMSjoO1c7kdk5oK55M_8o': config('GAME DEV STORY', '게임 개발 이야기', '게임 개발 이야기', '#FFB544', 'news'),
  PLWKwcHKTXy5Tw0Yk7arNvsJSr2pJqTRxS: config('CUDA RAY TRACING', 'CUDA 레이트레이싱', 'CUDA 레이트레이싱', '#FF7043', 'course'),
  'PLWKwcHKTXy5RhB8b42CjnfFL-4uRvHDyU': config('PBR RENDERING', '물리 기반 렌더링', 'PBR 렌더링', '#E8B868', 'course'),
  PLWKwcHKTXy5QEySaSo3JWoQXG9mk1DgVV: config('DEV TALK', '프로그래밍 이야기', '개발자 이야기', '#FFD95A', 'talk'),
  PLWKwcHKTXy5SJsZ3HD3TAkDv_ollFeSnL: config('DIRECTX 12', 'DirectX 12·자체엔진', 'DirectX 12 강의', '#7DD3FC', 'course'),
  PLWKwcHKTXy5Su5ZimPTNsZYRAsHrW290R: config('PORTFOLIO', '게임 포트폴리오', '게임 포트폴리오', '#FFB74D', 'showcase'),
  PLWKwcHKTXy5SVKTzTpgiZLcuCJkiMxcbb: config('DEV TIPS', '게임 프로그래밍 팁', '실전 게임개발 팁', '#D9F85F', 'course'),
  'PLWKwcHKTXy5QnZCqnrARipotYlkLU4m5-': config('UNREAL ENGINE 5', '언리얼 엔진 5', 'Unreal Engine 5', '#22D3EE', 'course'),
  PLWKwcHKTXy5T5v_qSsvUnjFZG85pDOZPq: config('DIRECTX 11', 'DirectX 11·그래픽스', 'DirectX 11 강의', '#FFB74D', 'course'),
  'PLWKwcHKTXy5Rm2vE8gUmQnEdxoX-r4KTT': config('YAMYAM CODING', '얌얌코딩', '얌얌코딩', '#FF9F43', 'mascot'),
  'PLWKwcHKTXy5QPd_uY3tNxm7hJi830d-g-': config('CLASS PROJECT', '수업 결과물', '수업 결과물', '#58E0C2', 'showcase'),
  PLWKwcHKTXy5RvBWvlUn72WZWKs8hLrnTz: config('WINDOWS API', 'Windows API·자체엔진', 'Windows API 강의', '#55E6C1', 'course'),
  'PLWKwcHKTXy5RK3F26-HPTtbSXEnMguTFs': config('GAME MATH', '게임 수학', '게임 수학', '#45E0D0', 'course'),
  PLWKwcHKTXy5SDbr6YuHIXpXeoybLCwX1e: config('ADVANCED ALGORITHM', 'C++ 고급 알고리즘', 'C++ 고급 알고리즘', '#FFC44D', 'problem'),
  'PLWKwcHKTXy5SaeuiYkJdc8juhwHKK2q-5': config('DESIGN PATTERN', '게임 디자인 패턴', '게임 디자인 패턴', '#FFB85C', 'course'),
  PLWKwcHKTXy5R3EqAZuOyGkB1JSRwwj7zF: config('GAME DEV CAREER', '게임 개발자 취업', '게임 개발자 취업', '#F0B45B', 'career'),
  PLWKwcHKTXy5RSkINElI7wZOwn9z4RcJff: config('CUSTOM ENGINE', 'C++ 게임 엔진', 'C++ 게임 엔진', '#B8F34B', 'course'),
  PLWKwcHKTXy5Smp6yIxm0i_krwYVvQJ4Ze: config('ALGORITHM SOLVED', '알고리즘 문제풀이', '알고리즘 문제풀이', '#FFB33E', 'problem'),
  PLWKwcHKTXy5SUZZ04yUYx_2yO3mkxDzR1: config('LIVE CODING', '게임 엔진 라이브', '게임 엔진 라이브 코딩', '#FF6B6B', 'course'),
};

function config(badge, category, suffix, accent, type) {
  return {badge, category, suffix, accent, type};
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function normalizeTitle(value) {
  return String(value)
    .replace(/\s+/g, ' ')
    .replace(/\s+([,.!?])/g, '$1')
    .replace(/\s*\|\s*/g, ' | ')
    .replace(/Directx/gi, 'DirectX')
    .replace(/Gpt\s*/gi, 'GPT ')
    .replace(/unreal engine/gi, 'Unreal Engine')
    .replace(/windows\s*api/gi, 'Windows API')
    .trim();
}

function proposedTitle(original, suffix) {
  const base = normalizeTitle(original).replace(/[|·\-–—\s]+$/, '').trim();
  const ending = ` | ${suffix}`;
  const maxBase = 100 - ending.length;
  const clipped = base.length > maxBase ? `${base.slice(0, Math.max(1, maxBase - 1)).trim()}…` : base;
  return `${clipped}${ending}`;
}

function thumbnailHeadline(value) {
  let text = normalizeTitle(value)
    .replace(/#[\p{L}\p{N}_]+/gu, '')
    .replace(/\s*[|｜]\s*/g, ' · ')
    .replace(/\s+/g, ' ')
    .trim();
  if (text.length <= 52) return text;
  const window = text.slice(0, 53);
  const cut = Math.max(window.lastIndexOf('?'), window.lastIndexOf('!'), window.lastIndexOf(' · '), window.lastIndexOf(' - '));
  if (cut >= 28) text = text.slice(0, cut + 1);
  else text = `${text.slice(0, 50).trim()}…`;
  return text;
}

function splitHighlight(text) {
  const words = text.split(' ');
  const first = [];
  while (words.length && `${first.join(' ')} ${words[0]}`.trim().length <= 14) first.push(words.shift());
  if (!first.length && words.length) first.push(words.shift());
  return [first.join(' '), words.join(' ')];
}

function fontSizeFor(text) {
  if (text.length <= 16) return 96;
  if (text.length <= 24) return 82;
  if (text.length <= 34) return 70;
  if (text.length <= 44) return 61;
  return 54;
}

function descriptionIntro(originalTitle, config) {
  const topic = thumbnailHeadline(originalTitle).replace(/[.!?]+$/, '');
  const bullets = {
    course: ['핵심 개념과 전체 흐름', '코드·도식·예제로 이해하는 원리', '직접 적용할 때 놓치기 쉬운 포인트'],
    news: ['이번 주제의 배경과 핵심', '게임 개발자 관점에서 봐야 할 의미', '실무와 학습에 연결할 판단 기준'],
    talk: ['주제의 배경과 맥락', '현업과 학습 관점의 판단 기준', '직접 시도할 수 있는 다음 단계'],
    career: ['채용과 포트폴리오에서 보는 핵심', '준비 과정에서 점검할 기준', '다음 단계로 이어지는 실전 조언'],
    showcase: ['프로젝트의 핵심 구성', '구현 결과와 플레이 특징', '포트폴리오에서 확인할 포인트'],
    mascot: ['얌얌코딩의 이야기와 활동', '함께 즐길 수 있는 제작 장면', '게임 개발을 이어가는 채널의 분위기'],
    problem: ['문제에서 먼저 찾아야 할 조건', '풀이 아이디어와 구현 흐름', '복잡도와 예외 케이스 점검'],
  }[config.type];
  return [
    `${topic}를 중심으로 꼭 알아야 할 내용을 정리했습니다.`,
    '',
    '이 영상에서 확인할 내용',
    ...bullets.map((bullet) => `• ${bullet}`),
  ].join('\n');
}

function renderHtml({baseData, config, headline, position}) {
  const [highlight, rest] = splitHighlight(headline);
  const fontSize = fontSizeFor(headline);
  return `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><style>
@font-face{font-family:NotoKR;src:url('file:///C:/Windows/Fonts/NotoSansKR-VF.ttf') format('truetype');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1280px;height:720px;overflow:hidden;font-family:NotoKR,'Malgun Gothic',sans-serif}
.canvas{position:relative;width:1280px;height:720px;background-image:url('${baseData}');background-size:cover;background-position:center}
.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(7,12,34,.96) 0%,rgba(7,12,34,.88) 35%,rgba(7,12,34,.28) 58%,rgba(7,12,34,0) 76%)}
.safe{position:absolute;inset:28px 34px}
.top{display:flex;align-items:center;gap:14px}
.mark{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:${config.accent};border:3px solid #fff;box-shadow:0 4px 0 rgba(0,0,0,.42);font-size:25px}
.category{padding:10px 20px 11px;border:2px solid rgba(255,255,255,.9);border-radius:25px;background:rgba(10,20,52,.72);color:#fff;font-weight:800;font-size:24px;letter-spacing:-.3px;box-shadow:0 4px 0 rgba(0,0,0,.35)}
.level{position:absolute;right:22px;top:4px;padding:9px 19px 10px;border-radius:22px;background:${config.accent};color:#101526;font-weight:900;font-size:23px;box-shadow:0 4px 0 rgba(0,0,0,.35);border:2px solid rgba(255,255,255,.8)}
.headline{position:absolute;left:8px;top:126px;width:645px;color:#fff;font-weight:950;font-size:${fontSize}px;line-height:1.05;letter-spacing:-3px;text-wrap:balance;filter:drop-shadow(0 7px 0 rgba(4,8,25,.95)) drop-shadow(0 0 2px #07102b)}
.headline .hi{display:block;color:${config.accent};-webkit-text-stroke:2px #0b1232;margin-bottom:4px}.headline .rest{-webkit-text-stroke:1.5px #0b1232}
.badge{position:absolute;left:8px;bottom:26px;display:inline-block;padding:10px 18px 11px;border-radius:20px;background:#fff;color:#10182d;font-weight:900;font-size:23px;letter-spacing:.5px;border:4px solid ${config.accent};box-shadow:0 6px 0 rgba(0,0,0,.36)}
.rule{position:absolute;left:14px;bottom:90px;width:360px;height:5px;border-radius:4px;background:linear-gradient(90deg,${config.accent},rgba(255,255,255,0))}
</style></head><body><div class="canvas"><div class="shade"></div><div class="safe">
<div class="top"><div class="mark">🐾</div><div class="category">얌얌코딩 · ${escapeHtml(config.category)}</div></div>
<div class="level">LV ${String(position || 0).padStart(2, '0')}</div>
<div class="headline"><span class="hi">${escapeHtml(highlight)}</span><span class="rest">${escapeHtml(rest)}</span></div>
<div class="rule"></div><div class="badge">${escapeHtml(config.badge)}</div>
</div></div></body></html>`;
}

(async () => {
  const browser = await puppeteer.launch({headless: true});
  const page = await browser.newPage();
  await page.setViewport({width: 1280, height: 720, deviceScaleFactor: 1});
  const changes = [];
  let rendered = 0;

  for (const video of inventory.videos.filter((item) => item.target)) {
    const primary = video.playlists.find((playlist) => !playlist.excluded && configs[playlist.id]);
    if (!primary) throw new Error(`No configured target playlist for ${video.id}: ${video.title}`);
    const cfg = configs[primary.id];
    const basePath = path.join(basesDir, `${primary.id}.png`);
    if (!fs.existsSync(basePath)) throw new Error(`Missing base image: ${basePath}`);
    const baseData = `data:image/png;base64,${fs.readFileSync(basePath).toString('base64')}`;
    const headline = thumbnailHeadline(video.title);
    const title = proposedTitle(video.title, cfg.suffix);
    const intro = descriptionIntro(video.title, cfg);
    const thumbnailPath = path.join(thumbnailsDir, `${video.id}.jpg`);

    await page.setContent(renderHtml({baseData, config: cfg, headline, position: primary.position}), {waitUntil: 'load'});
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({path: thumbnailPath, type: 'jpeg', quality: 91, clip: {x: 0, y: 0, width: 1280, height: 720}});

    changes.push({
      id: video.id,
      url: video.url,
      originalTitle: video.title,
      proposedTitle: title,
      descriptionIntro: intro,
      thumbnailPath,
      primaryPlaylist: primary,
      category: cfg.category,
      badge: cfg.badge,
      headline,
      targetPlaylists: video.playlists.filter((playlist) => !playlist.excluded),
    });
    rendered += 1;
    if (rendered % 25 === 0) console.log(`Rendered ${rendered}/${inventory.counts.targetVideos}`);
  }

  await browser.close();
  const changesPath = path.join(outputRoot, 'changes.json');
  fs.writeFileSync(changesPath, `${JSON.stringify({generatedAt: new Date().toISOString(), count: changes.length, changes}, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({rendered, changesPath, thumbnailsDir}, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
