// Reproducible channel thumbnail layout; original logo and directly reviewed game pixels.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
const root=path.resolve(__dirname,'../../..'),dest=path.resolve(__dirname,'../publishing'),file=path.join(dest,'thumbnail.png'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(fs.existsSync(file))throw Error('Review existing thumbnail');GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Channel Korean');
(async()=>{
 const source='projects/avoid-game-comparisons/production/measured-edit-v6/current-framed-cue-local/02-p1-action-02-195-255/sample-003.png',logoPath='shared/assets/branding/yamyamcoding-cats-original.png',game=await loadImage(path.join(root,source)),logo=await loadImage(path.join(root,logoPath)),canvas=createCanvas(1280,720),c=canvas.getContext('2d');
 const box=(x,y,w,h,color,border=true)=>{c.fillStyle=color;c.fillRect(x,y,w,h);if(border){c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(x,y,w,h);}},text=(s,x,y,size,color='#111')=>{c.font=`900 ${size}px "Channel Korean"`;c.fillStyle=color;c.fillText(s,x,y);};
 box(0,0,1280,720,'#fff',false);box(14,14,1252,692,'#fff');box(16,16,1248,62,'#ffdf00',false);text('얌얌코딩  |  게임 기획',37,58,25);text('Game Dev',351,56,20);
 c.save();c.beginPath();c.arc(1220,47,26,0,Math.PI*2);c.clip();c.drawImage(logo,1194,21,52,52);c.restore();
 text('게임 기획',37,207,110);box(35,233,672,91,'#ffdf00',false);text('이름만 말하면?',38,310,86);text('같은 작품, 다른 머릿속 장면',40,375,32);
 c.save();c.beginPath();c.arc(986,245,126,0,Math.PI*2);c.clip();c.drawImage(logo,860,119,252,252);c.restore();box(726,98,315,71,'#fff2a4');text('무엇을 하는 게임인가요?',741,143,23);
 text('목표 → 행동 → 조건',730,407,33);box(717,439,500,250,'#ffdf00',false);
 // Use the clean action area above the narration band in the already reviewed source frame.
 c.drawImage(game,0,0,1920,900,728,427,490,263);c.strokeStyle='#111';c.lineWidth=4;c.strokeRect(728,427,490,263);
 for(const [k,s]of ['목표','행동','조건'].entries()){box(42+k*213,476,177,83,['#dfeaf5','#fff2a4','#e0eade'][k]);text(s,72+k*213,531,38);if(k<2)text('→',226+k*213,531,32);}
 text('세 문장으로 전달하기',43,643,43);text('듣는 사람의 되말하기로 확인',43,683,24);
 fs.writeFileSync(file,canvas.toBuffer('image/png'));fs.writeFileSync(path.join(dest,'thumbnail-recipe.json'),JSON.stringify({createdAt:new Date().toISOString(),width:1280,height:720,sha256:sha(file),method:'code-native channel-layout composition with original logo and directly observed existing-game pixels',source:{path:source,sha256:sha(path.join(root,source)),videoId:'z4utn4Sm6SY',nativeAction:'02-p1-action-02-195-255',crop:[0,0,1920,900],rights:'projects/avoid-game-comparisons/sources/SOURCES.md'},logo:{path:logoPath,sha256:sha(path.join(root,logoPath))},visualReview:'pending',uploaded:false,customThumbnailLimitNonblocking:true},null,2)+'\n');console.log(JSON.stringify({prepared:true,sha256:sha(file),uploaded:false}));
})().catch(e=>{console.error(e);process.exitCode=1;});
