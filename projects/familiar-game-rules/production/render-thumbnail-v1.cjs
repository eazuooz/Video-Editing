// Native channel layout; original cat and observed existing-game pixels stay unchanged.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
const root=path.resolve(__dirname,'../../..'),dest=path.resolve(__dirname,'../publishing');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source='shared/output/familiar-game-rules/research/guide13-encoded-input-v7/frames/0085.jpg',logoPath='shared/assets/branding/yamyamcoding-cats-original.png';
if(sha(path.join(root,source))!=='b8667c6ec16792a0589065b627f6ed99bbef978f7be360d965690586a6df22f8')throw Error('Reviewed source changed');
fs.mkdirSync(dest,{recursive:true});const file=path.join(dest,'thumbnail.png');if(fs.existsSync(file))throw Error('Preserve and review existing thumbnail');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Channel Korean');
(async()=>{
 const game=await loadImage(path.join(root,source)),logo=await loadImage(path.join(root,logoPath));
 const canvas=createCanvas(1280,720),c=canvas.getContext('2d');
 const box=(x,y,w,h,color,border=true)=>{c.fillStyle=color;c.fillRect(x,y,w,h);if(border){c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(x,y,w,h);}};
 const text=(s,x,y,size,color='#111')=>{c.font=`900 ${size}px "Channel Korean"`;c.fillStyle=color;c.fillText(s,x,y);};
 box(0,0,1280,720,'#fff',false);box(14,14,1252,692,'#fff');box(16,16,1248,62,'#ffdf00',false);
 text('얌얌코딩  |  게임 기획',37,58,25);text('Game Dev',351,56,20);
 c.save();c.beginPath();c.arc(1220,47,26,0,Math.PI*2);c.clip();c.drawImage(logo,1194,21,52,52);c.restore();
 text('게임 조작',36,208,112);box(35,234,680,95,'#ffdf00',false);text('버튼만 옮기면?',40,309,75);
 text('재배치와 장치 변경의 차이',40,385,40);
 c.save();c.beginPath();c.arc(993,241,130,0,Math.PI*2);c.clip();c.drawImage(logo,863,111,260,260);c.restore();
 box(747,98,334,69,'#fff2a4');text('기능도 같은가요?',766,144,31);
 box(42,459,278,86,'#e0eade');text('버튼 연결',68,518,43);text('↔',339,520,45);box(415,459,278,86,'#fff2a4');text('입력 기능',440,518,43);
 text('익숙한 약속 + 새로운 행동',42,616,37);text('이동 · 조준 · 실행을 나누어 보기',42,674,28);
 box(738,410,488,278,'#ffdf00',false);c.drawImage(game,560,340,1100,580,749,424,466,246);c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(749,424,466,246);
 fs.writeFileSync(file,canvas.toBuffer('image/png'));
 fs.writeFileSync(path.join(dest,'thumbnail-recipe.json'),JSON.stringify({createdAt:new Date().toISOString(),width:1280,height:720,sha256:sha(file),method:'code-native channel-layout composition with original branding and directly read official existing-game pixels',source:{path:source,sha256:sha(path.join(root,source)),videoId:'FVkDc6u_4GQ',game:'Anger Foot',nativeFrame:1657,thumbnailCrop:[560,340,1100,580],captionExcludedByCrop:true,rights:'projects/familiar-game-rules/sources/SOURCES.md'},logo:{path:logoPath,sha256:sha(path.join(root,logoPath))},visualReview:'pending',uploaded:false,gitEssentialReview:'pending',customThumbnailLimitNonblocking:true},null,2)+'\n');
 console.log(JSON.stringify({prepared:true,sha256:sha(file),uploaded:false,gitAdded:false}));
})().catch(e=>{console.error(e);process.exitCode=1;});
