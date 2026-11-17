// Brand cover composed from the actual final room and the existing mascot.
const fs=require('fs'),path=require('path');
const {createCanvas,loadImage,GlobalFonts}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const L=path.join(__dirname,'local/full-video-v5'),root=path.resolve(__dirname,'../../..');
GlobalFonts.registerFromPath('C:/Windows/Fonts/NotoSansKR-VF.ttf','Noto Sans KR');
(async()=>{
 fs.mkdirSync(path.join(L,'final'),{recursive:true});
 const cv=createCanvas(1280,720),c=cv.getContext('2d');
 const room=await loadImage(fs.readFileSync(path.join(L,'assets/room.png')));
 const cat=await loadImage(fs.readFileSync(path.join(root,'shared/assets/branding/cat-reactions-v1/realize.png')));
 c.fillStyle='#fff';c.fillRect(0,0,1280,720);
 c.fillStyle='#ffe13b';c.fillRect(0,0,1280,94);
 c.fillStyle='#151515';c.font='850 41px "Noto Sans KR"';c.fillText('AI 게임 제작 · 3D 편',38,66);
 // Preserve the complete game view at its native 16:9 aspect ratio.
 c.drawImage(room,448,139,832,468);
 c.fillStyle='#151515';c.font='900 69px "Noto Sans KR"';c.fillText('이런 3D 방',32,221);
 c.fillStyle='#d92224';c.font='900 67px "Noto Sans KR"';c.fillText('AI로 만드는',32,320);c.fillText('방법 공개',32,408);
 c.fillStyle='#303930';c.font='650 29px "Noto Sans KR"';c.fillText('이미지 → 모델 → 웹게임',33,478);
 c.drawImage(cat,30,506,180,180);
 c.fillStyle='#141e17';c.font='850 32px "Noto Sans KR"';c.fillText('얌얌코딩',214,648);
 const f=path.join(L,'final/thumbnail.png');fs.writeFileSync(f,await cv.encode('png'));console.log(f);
})();
