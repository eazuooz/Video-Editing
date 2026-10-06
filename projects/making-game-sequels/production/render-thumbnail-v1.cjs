// Code-native channel layout with unchanged original branding and observed game pixels.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {createCanvas, loadImage, GlobalFonts} = require(require.resolve('@napi-rs/canvas', {paths: ['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
const root = path.resolve(__dirname, '../../..'), dest = path.resolve(__dirname, '../publishing');
const file = path.join(dest, 'thumbnail.png');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if (fs.existsSync(file)) throw Error('Preserve the existing thumbnail and review it first');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf', 'Channel Korean');
(async () => {
  const source = 'projects/making-game-sequels/production/measured-edit-v4/wall-guide-target-local-v4/02-p4-action-17-18990-19200/sample-012.png';
  const logoPath = 'shared/assets/branding/yamyamcoding-cats-original.png';
  if (sha(path.join(root, source)) !== '02ba4f7df035d58148ad2ec7dce94f5da0e2b2d4d1e79e98ac5d7873cb152f7c') throw Error('Reviewed source changed');
  const game = await loadImage(path.join(root, source)), logo = await loadImage(path.join(root, logoPath));
  const canvas = createCanvas(1280, 720), c = canvas.getContext('2d');
  const box = (x,y,w,h,color,border=true) => { c.fillStyle=color; c.fillRect(x,y,w,h); if(border){c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(x,y,w,h);} };
  const text = (s,x,y,size,color='#111') => {c.font=`900 ${size}px "Channel Korean"`;c.fillStyle=color;c.fillText(s,x,y);};
  box(0,0,1280,720,'#fff',false); box(14,14,1252,692,'#fff'); box(16,16,1248,62,'#ffdf00',false);
  text('얌얌코딩  |  게임 기획',37,58,25); text('Game Dev',351,56,20);
  c.save();c.beginPath();c.arc(1220,47,26,0,Math.PI*2);c.clip();c.drawImage(logo,1194,21,52,52);c.restore();
  text('게임 속편',36,208,112); box(35,234,680,95,'#ffdf00',false); text('그대로? 바꿀까?',40,309,79);
  text('다시 하게 만드는 기획',40,385,42);
  c.save();c.beginPath();c.arc(993,241,130,0,Math.PI*2);c.clip();c.drawImage(logo,863,111,260,260);c.restore();
  box(747,98,334,69,'#fff2a4');text('무엇을 남길까요?',766,144,32);
  box(42,459,278,86,'#e0eade');text('남길 재미',68,518,44);
  text('↔',339,520,45); box(415,459,278,86,'#fff2a4');text('새 선택',465,518,44);
  text('익숙한 행동 + 달라진 판단',42,616,39);text('제작 재사용과 플레이 이유 구분',42,674,29);
  box(738,410,488,278,'#ffdf00',false);
  // Caption-free observed action area; no fabricated sequel feature or internal-code claim.
  c.drawImage(game,230,200,1460,690,749,424,466,250);c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(749,424,466,250);
  fs.writeFileSync(file, canvas.toBuffer('image/png'));
  fs.writeFileSync(path.join(dest, 'thumbnail-recipe.json'), JSON.stringify({createdAt:new Date().toISOString(),width:1280,height:720,sha256:sha(file),
    method:'code-native channel-layout composition with unchanged original cat and directly observed official existing-game pixels',
    source:{path:source,sha256:sha(path.join(root,source)),videoId:'MXxOg1xuWcI',game:'Orcs Must Die! 2',nativeFrame:19095,
      nativeInterval:[18990,19200],inputFraming:'crop1536x864 at192,0 scaled to1920x1080',thumbnailCrop:[230,200,1460,690],rights:'projects/making-game-sequels/sources/SOURCES.md'},
    logo:{path:logoPath,sha256:sha(path.join(root,logoPath))},visualReview:'pending',uploaded:false,gitEssentialReview:'pending',
    customThumbnailLimitNonblocking:true},null,2)+'\n');
  console.log(JSON.stringify({prepared:true,sha256:sha(file),uploaded:false,gitAdded:false}));
})().catch(error => {console.error(error);process.exitCode=1;});
