// Mechanical assembly: generated typography header + unchanged actual deployed game pixels.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {createCanvas,loadImage}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const H=__dirname;
const generated='C:/Users/1/.codex/generated_images/01a1382b-9f87-7b82-942b-ba38e671a085/exec-bee1c109-4aaf-493c-8a5a-723752745c7d.png';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const headerPath=path.join(H,'thumbnail-header.png');fs.copyFileSync(generated,headerPath);
 const gamePath=path.join(H,'thumbnail-game-source.png');
 const header=await loadImage(headerPath),game=await loadImage(gamePath);
 const canvas=createCanvas(1280,720),c=canvas.getContext('2d');
 c.fillStyle='#ffffff';c.fillRect(0,0,1280,720);
 c.imageSmoothingEnabled=true;c.drawImage(header,0,0,header.width,366,0,0,1280,280);
 // Fixed aspect-ratio crop, nearest-neighbour export; no generated character or room.
 c.imageSmoothingEnabled=false;c.drawImage(game,0,420,1920,660,0,280,1280,440);
 fs.writeFileSync(path.join(H,'thumbnail-v2.png'),canvas.toBuffer('image/png'));
 const mobile=createCanvas(375,211),m=mobile.getContext('2d');m.drawImage(canvas,0,0,375,211);
 const local=path.resolve(H,'../../production/local/room-v4-video/thumbnail-qa');fs.mkdirSync(local,{recursive:true});
 fs.writeFileSync(path.join(local,'thumbnail-v2-375.png'),mobile.toBuffer('image/png'));
 fs.writeFileSync(path.join(H,'thumbnail-v2.provenance.json'),JSON.stringify({
  revision:'actual-game-thumbnail-v2',userInstruction:'썸네일도 실제 게임 이미지로 바꿔주고',
  method:'Built-in image_gen typography-only header; mechanical assembly with actual game pixels',
  gameSource:gamePath,gameSourceSHA256:hash(gamePath),
  gameCapture:{runtime:'projects/ai-2d-game-assets/production/room-v4-video/game-runtime.cjs',siteVersion:6,action:'write',time:4,weather:'sun',dimensions:[1920,1080]},
  gameCrop:[0,420,1920,660],gameDestination:[0,280,1280,440],gameCharactersOrSceneryRegenerated:false,
  generatedHeaderSource:generated,headerSHA256:hash(headerPath),headerCrop:[0,0,header.width,366],
  exactText:['얌얌코딩','AI 제작 도구 실전','도트부터 게임까지'],
  finalDimensions:[1280,720],finalSHA256:hash(path.join(H,'thumbnail-v2.png')),
  bytes:fs.statSync(path.join(H,'thumbnail-v2.png')).size,
  exception:'Current user explicitly requests actual game image instead of default illustrated channel thumbnail; preserve other videos.',
  platformApplied:false
 },null,2)+'\n');
 console.log(JSON.stringify({thumbnail:path.join(H,'thumbnail-v2.png'),mobile:path.join(local,'thumbnail-v2-375.png')}));
})();
