const fs=require('node:fs'),path=require('node:path');
const P=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/codixel/core/pixel.js');
const root=path.resolve(__dirname,'../../../..');
const input=path.join(root,'sites/yamyam-cartographers-room/dist/assets/motions/book-07.png');
const out=path.join(root,'projects/ai-2d-game-assets/production/local/room-v2/codixel');fs.mkdirSync(out,{recursive:true});
const sprite=P.load(input);
P.save(P.ruler(sprite,5,{step:8}),path.join(out,'reading-ruler.png'));
const rig=new P.Rig(sprite)
 .bone('body',null,64,84,64,160)
 .bone('head','body',65,45,65,18)
 .bind({joint:1,paint:{body:[[0,44],[128,44],[128,176],[0,176]],head:[[0,0],[128,0],[128,44],[0,44]]}});
const own=P.ruler(rig.ownerMap(),5,{step:8});rig.drawBones(own,0,0,{}, {scale:5});
P.save(P.sheet([own,rig.legend()]),path.join(out,'reading-owners.png'));
const frames=[];const assetOut=path.join(root,'sites/yamyam-cartographers-room/dist/assets/codixel');fs.mkdirSync(assetOut,{recursive:true});
for(let i=0;i<24;i++){
 const t=i/24*Math.PI*2,b=new P.Buf(128,176);
 rig.draw(b,0,0,{head:{a:Math.sin(t)*.035,dy:Math.sin(t)*.5}});
 frames.push(b);P.save(b,path.join(assetOut,`read-${String(i).padStart(2,'0')}.png`));
}
P.save(P.sheet(frames.map((buf,i)=>({buf,label:String(i).padStart(2,'0')})),{cols:6,scale:2}),path.join(out,'reading-preview.png'));
const packed=P.pack(frames,{cols:6});P.save(packed,path.join(assetOut,'reading-atlas.png'));
fs.writeFileSync(path.join(out,'reading.gif'),P.gif(frames,{delay:125,scale:3}));
const record={tool:'Codixel',repo:'https://github.com/mankidev/codixel',actualExecution:true,input:'motions/book-07.png',jointSource:'reading-ruler.png visually inspected',bones:[{name:'body',joint:[64,84],tip:[64,160]},{name:'head',joint:[65,45],tip:[65,18]}],parameters:{headAngleRadians:.035,headVerticalPixels:.5,frameCount:24,fps:8},operation:'P.Rig.bind/draw; P.pack; P.gif; no diffusion model',atlas:packed.frame,canvas:[128,176],anchor:[64,166],gameScale:.75,frames:frames.map((_,i)=>`codixel/read-${String(i).padStart(2,'0')}.png`)};
fs.writeFileSync(path.join(out,'reading.json'),JSON.stringify(record,null,2));fs.writeFileSync(path.join(assetOut,'reading.json'),JSON.stringify(record,null,2));
console.log(JSON.stringify({input,out,phase:'rig-and-24-frames',atlas:packed.frame}));
