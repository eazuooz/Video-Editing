// Original channel cats and a reviewed frame from an existing game.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{
 paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')],
}));
const root=path.resolve(__dirname,'../../..'),output=path.resolve(__dirname,'../publishing');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Channel Korean');
const file=path.join(output,'thumbnail.png');
if(fs.existsSync(file))throw Error('Existing thumbnail must be reviewed before replacement.');
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{
 const source='production/batches/sakurai-planning-game-design/proof-hierarchical-game-outlines/source-research/frames/native-bank-v1/museum-19-middle.jpg';
 const index=JSON.parse(fs.readFileSync(path.join(root,path.dirname(source),'index.json'),'utf8'));
 const row=index.rows.find(row=>row.croppedFile===source);
 if(!row||Math.abs(row.ptsSeconds-3173)>1/120)throw Error('Observed native source-frame witness required.');
 const game=await loadImage(path.join(root,source));
 const sourceCanvas=createCanvas(game.width,game.height);sourceCanvas.getContext('2d').drawImage(game,0,0);
 const sourceFrame=path.join(output,'thumbnail-source-frame.png');
 fs.writeFileSync(sourceFrame,sourceCanvas.toBuffer('image/png'));
 const canvas=createCanvas(1280,720),ctx=canvas.getContext('2d');
 const rectangle=(x,y,w,h,color,border=false,radius=0)=>{
  ctx.beginPath();ctx.roundRect(x,y,w,h,radius);ctx.fillStyle=color;ctx.fill();
  if(border){ctx.strokeStyle='#111';ctx.lineWidth=4;ctx.stroke();}
 };
 const text=(value,x,y,size,color='#111',width=null)=>{
  let actualSize=size;ctx.font=`900 ${actualSize}px "Channel Korean"`;
  while(width&&ctx.measureText(value).width>width&&actualSize>20){actualSize--;ctx.font=`900 ${actualSize}px "Channel Korean"`;}
  ctx.fillStyle=color;ctx.fillText(value,x,y);
  return {value,size:actualSize,width:ctx.measureText(value).width};
 };
 rectangle(0,0,1280,720,'white');rectangle(15,15,1250,690,'white',true,20);
 ctx.save();ctx.beginPath();ctx.roundRect(17,17,1246,686,18);ctx.clip();rectangle(17,17,1246,62,'#ffdf00');ctx.restore();
 ctx.strokeStyle='#111';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(17,79);ctx.lineTo(1263,79);ctx.stroke();
 text('얌얌코딩  |  게임 기획',39,58,25);text('Game Dev',351,56,20);
 rectangle(35,230,668,87,'#ffdf00');
 const titleLayout=[text('기획서 정리',35,205,108,'#111',670),text('계층형 아웃라인',35,308,96,'#111',670)];
 text('목표 · 기능 · 세부 규칙을 묶는 법',40,370,30,'#111',670);
 rectangle(42,416,204,55,'#ffdf00',true,5);text('핵심 정리',65,457,31);
 const logoFile=path.join(root,'shared/assets/branding/yamyamcoding-cats-original.png'),logo=await loadImage(logoFile);
 ctx.save();ctx.beginPath();ctx.arc(1221,47,27,0,Math.PI*2);ctx.clip();ctx.drawImage(logo,1194,20,54,54);ctx.restore();
 ctx.save();ctx.beginPath();ctx.arc(967,264,117,0,Math.PI*2);ctx.clip();ctx.drawImage(logo,850,147,234,234);ctx.restore();
 rectangle(731,104,260,86,'#fff2a4',true,16);
 text('목표부터 묶고',750,139,29,'#111',223);text('필요할 때 펼치기',750,175,29,'#111',223);
 rectangle(1041,327,175,57,'#d9edff',true,16);text('가지째 이동',1055,365,24,'#111',146);
 rectangle(730,426,492,263,'#ffdf00',false,10);
 ctx.save();ctx.beginPath();ctx.roundRect(721,414,492,277,10);ctx.clip();ctx.drawImage(game,721,414,492,277);ctx.restore();
 ctx.strokeStyle='#111';ctx.lineWidth=4;ctx.beginPath();ctx.roundRect(721,414,492,277,10);ctx.stroke();
 for(const [i,value]of ['목표','기능','규칙'].entries()){
  rectangle(43+i*213,535,178,81,['#dfeaf5','#fff2a4','#e0eade'][i],true,12);text(value,88+i*213,588,36);
  if(i<2)text('→',224+i*213,587,34);
 }
 text('큰 목표부터 필요한 조건까지',43,667,29,'#111',664);
 fs.writeFileSync(file,canvas.toBuffer('image/png'));
 fs.writeFileSync(path.join(output,'thumbnail-recipe.json'),JSON.stringify({
  createdAt:new Date().toISOString(),width:1280,height:720,sha256:hash(file),
  method:'nativeCanvas original-logo and directly-observed-existing-game-frame composition',
  concept:'yellow-strip,white,large-black-Korean,original-cats,actual-existing-game',titleLayout,
  source:{videoId:'I-ccSZ5J1Bo',seconds:row.ptsSeconds,version:'2026-10-01 official Update12 demonstration / Rides & Relics preview',
   nativeFrame:row.nativeFrame,crop:row.crop,originalCropPath:source,sourceFrameSha256:hash(sourceFrame),
   rights:'projects/hierarchical-game-outlines/sources/SOURCES.md'},
  logo:'shared/assets/branding/yamyamcoding-cats-original.png',
  gameFrameIsNotAnOutlineEditor:true,visualReview:'pending',uploaded:false,
 },null,2)+'\n');
 console.log('New local thumbnail prepared; actual upload and final video remain pending.');
})().catch(error=>{console.error(error);process.exitCode=1;});
