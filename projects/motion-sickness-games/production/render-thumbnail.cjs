// New native thumbnail composition using the channel's original logo and a
// directly observed frame. This does not synthesise or replace game footage.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {createCanvas, loadImage, GlobalFonts} = require(require.resolve('@napi-rs/canvas', {
  paths: [path.join(process.env.USERPROFILE, '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')],
}));
const root = path.resolve(__dirname, '../../..'), output = path.resolve(__dirname, '../publishing');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf', 'Channel Korean');
const file = path.join(output, 'thumbnail.png');
if (fs.existsSync(file)) throw new Error('Thumbnail already exists. Review it before deliberately replacing it.');
(async () => {
  const canvas = createCanvas(1280, 720), ctx = canvas.getContext('2d');
  const rectangle = (x, y, w, h, color, border = false, radius = 0) => {
    ctx.beginPath(); ctx.roundRect(x, y, w, h, radius); ctx.fillStyle = color; ctx.fill();
    if (border) {ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.stroke();}
  };
  const text = (value, x, y, size, color = '#111', width = null) => {
    let actualSize = size;
    ctx.font = `900 ${actualSize}px "Channel Korean"`;
    while (width && ctx.measureText(value).width > width && actualSize > 20) {
      actualSize--; ctx.font = `900 ${actualSize}px "Channel Korean"`;
    }
    ctx.fillStyle = color; ctx.fillText(value, x, y);
    return {value, size: actualSize, width: ctx.measureText(value).width};
  };
  rectangle(0, 0, 1280, 720, 'white'); rectangle(15, 15, 1250, 690, 'white', true, 20);
  ctx.save(); ctx.beginPath(); ctx.roundRect(17, 17, 1246, 686, 18); ctx.clip(); rectangle(17, 17, 1246, 62, '#ffdf00'); ctx.restore();
  ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(17, 79); ctx.lineTo(1263, 79); ctx.stroke();
  text('얌얌코딩  |  게임 기획', 39, 58, 25); text('Game Dev', 351, 56, 20);
  rectangle(35, 230, 668, 87, '#ffdf00');
  const titleLayout = [text('게임하면', 35, 205, 108, '#111', 670), text('왜 멀미날까?', 35, 308, 96, '#111', 670)];
  text('카메라 움직임과 플레이어의 선택', 40, 370, 30, '#111', 670);
  rectangle(42, 416, 204, 55, '#ffdf00', true, 5); text('핵심 정리', 65, 457, 31);
  const logoFile = path.join(root, 'shared/assets/branding/yamyamcoding-cats-original.png');
  const logo = await loadImage(logoFile);
  ctx.save(); ctx.beginPath(); ctx.arc(1221, 47, 27, 0, Math.PI * 2); ctx.clip(); ctx.drawImage(logo, 1194, 20, 54, 54); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.arc(967, 264, 117, 0, Math.PI * 2); ctx.clip(); ctx.drawImage(logo, 850, 147, 234, 234); ctx.restore();
  rectangle(731, 104, 260, 86, '#fff2a4', true, 16); text('시점과 조준을', 750, 139, 29); text('따로 움직이면?', 750, 175, 29);
  rectangle(1041, 327, 175, 57, '#d9edff', true, 16); text('선택할 수 있게', 1051, 365, 24);
  const gameFile = path.join(output, 'thumbnail-source-frame.png');
  const game = await loadImage(gameFile);
  rectangle(730, 426, 492, 263, '#ffdf00', false, 10);
  ctx.save(); ctx.beginPath(); ctx.roundRect(721, 414, 492, 277, 10); ctx.clip(); ctx.drawImage(game, 721, 414, 492, 277); ctx.restore();
  ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(721, 414, 492, 277, 10); ctx.stroke();
  for (const [i, value] of ['시점', '조준', '선택'].entries()) {
    rectangle(43 + i * 213, 535, 178, 81, ['#dfeaf5', '#fff2a4', '#e0eade'][i], true, 12);
    text(value, 88 + i * 213, 588, 36);
    if (i < 2) text('→', 224 + i * 213, 587, 34);
  }
  text('필요한 움직임과 추가 연출 나누기', 43, 667, 29, '#111', 664);
  fs.writeFileSync(file, canvas.toBuffer('image/png'));
  fs.writeFileSync(path.join(output, 'thumbnail-recipe.json'), JSON.stringify({
    createdAt: new Date().toISOString(), width: 1280, height: 720,
    sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),
    method: 'nativeCanvas original-logo and directly-observed-game-frame composition',
    concept: 'yellow-strip,white,large-black-Korean,original-cats,actual-existing-game',
    titleLayout, source: {videoId: 'PF5L_2g9UVQ', seconds: 108, version: '2022 WIP developer preview',
      rights: 'projects/motion-sickness-games/sources/SOURCES.md', sourceFrameSha256: crypto.createHash('sha256').update(fs.readFileSync(gameFile)).digest('hex')},
    logo: 'shared/assets/branding/yamyamcoding-cats-original.png',
    screenshotNotAClinicalOutcome: true, visualReview: 'pending', uploaded: false,
  }, null, 2) + '\n');
  console.log('Created new native thumbnail draft; final-video and platform approval not implied.');
})().catch(error => {console.error(error); process.exitCode = 1;});
