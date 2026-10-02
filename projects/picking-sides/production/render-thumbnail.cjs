// Native composition of the original logo and an observed gameplay frame.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Channel Korean');
const root=path.resolve(__dirname,'../../..'),out=path.resolve(__dirname,'../publishing');fs.mkdirSync(out,{recursive:true});
const frame=path.join(out,'thumbnail-source-frame.png');
const r=spawnSync('ffmpeg',['-v','error','-y','-ss','77.5','-i',path.join(root,'shared/output/picking-sides/media-cache/Z5jytMiH4rI.mp4'),'-frames:v','1',frame],{encoding:'utf8',windowsHide:true});if(r.status)throw Error(r.stderr);
(async()=>{
 const c=createCanvas(1280,720),x=c.getContext('2d');
 function rect(l,t,w,h,color,stroke=false,r=0){x.beginPath();x.roundRect(l,t,w,h,r);x.fillStyle=color;x.fill();if(stroke){x.strokeStyle='#111';x.lineWidth=4;x.stroke();}}
 function txt(text,l,t,size,color='#111'){x.font=`900 ${size}px "Channel Korean"`;x.fillStyle=color;x.fillText(text,l,t);}
 rect(0,0,1280,720,'white');rect(15,15,1250,690,'white',true,20);
 x.save();x.beginPath();x.roundRect(17,17,1246,686,18);x.clip();rect(17,17,1246,62,'#ffdf00');x.restore();
 x.strokeStyle='#111';x.lineWidth=4;x.beginPath();x.moveTo(17,79);x.lineTo(1263,79);x.stroke();
 txt('얌얌코딩  |  게임 기획',39,58,25);txt('Game Dev',351,56,20);
 rect(36,230,660,86,'#ffdf00');txt('남의 게임인데',35,205,87);txt('왜 응원할까?',35,307,96);
 txt('관전의 재미를 만드는 3가지',41,371,31);
 rect(42,418,204,55,'#ffdf00',true,5);txt('핵심 정리',65,458,31);
 const logo=await loadImage(path.join(root,'shared/assets/branding/yamyamcoding-cats-original.png'));
 x.save();x.beginPath();x.arc(1221,47,27,0,Math.PI*2);x.clip();x.drawImage(logo,1194,20,54,54);x.restore();
 x.save();x.beginPath();x.arc(966,273,127,0,Math.PI*2);x.clip();x.drawImage(logo,839,146,254,254);x.restore();
 rect(753,107,219,63,'#fff2a4',true,18);txt('나는 토끼!',779,150,30);
 rect(1029,190,194,61,'#d9edff',true,18);txt('끝까지 가!',1048,232,29);
 const game=await loadImage(frame);rect(738,426,481,231,'#ffdf00',false,10);x.save();x.beginPath();x.roundRect(729,415,481,231,10);x.clip();x.drawImage(game,0,0,1920,980,729,415,481,246);x.restore();x.strokeStyle='#111';x.lineWidth=4;x.stroke();
 txt('같은 화면, 다른 관심',740,683,25);
 for(const [i,t]of ['누구를?','왜?','다음엔?'].entries()){
  rect(45+i*212,532,177,83,['#dfeaf5','#fff2a4','#e0eade'][i],true,12);txt(t,63+i*212,584,31);
  if(i<2)txt('→',224+i*212,582,33);
 }
 txt('대상 · 이유 · 상황',45,666,29);
 const file=path.join(out,'thumbnail.png');fs.writeFileSync(file,c.toBuffer('image/png'));
 fs.writeFileSync(path.join(out,'thumbnail-recipe.json'),JSON.stringify({createdAt:new Date().toISOString(),width:1280,height:720,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),method:'nativeCanvas original-logo and observed-game-frame composition',concept:'yellow-strip,white,large-black-Korean,original-cats,actual-game',source:{videoId:'Z5jytMiH4rI',seconds:77.5,rights:'projects/picking-sides/sources/SOURCES.md'},logo:'shared/assets/branding/yamyamcoding-cats-original.png',visualReview:'pending',uploaded:false},null,2)+'\n');console.log('Created new thumbnail draft; not uploaded.');
})().catch(e=>{console.error(e);process.exitCode=1});
