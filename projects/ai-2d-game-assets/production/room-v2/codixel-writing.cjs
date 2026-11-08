// Actual Codixel rig on the native cleaned sprite; only writing arm/quill move.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const P=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/codixel/core/pixel.js');
const PROJECT=path.resolve(__dirname,'../..'),L=path.join(PROJECT,'production/local/room-v3'),input=path.join(L,'pixel-clean/96x132/writing/write-07.png'),out=path.join(L,'codixel-writing');fs.mkdirSync(out,{recursive:true});
const source=P.load(input),rig=new P.Rig(source)
 .bone('body',null,48,82,48,122)
 .bone('writing_arm','body',31,76,43,79,1)
 .bone('quill','writing_arm',43,79,34,63,2)
 .bind({joint:1,paint:{body:[[0,0],[96,0],[96,132],[0,132]],writing_arm:[[29,73],[35,74],[39,76],[45,75],[47,82],[35,82],[29,79]],quill:[[32,61],[35,62],[41,69],[44,75],[45,80],[41,79],[37,72],[33,68]]}});
const ruler=P.ruler(source,8,{step:8}),owner=P.ruler(rig.ownerMap(),8,{step:8});rig.drawBones(owner,0,0,{}, {scale:8});P.save(ruler,path.join(out,'writing-ruler.png'));P.save(owner,path.join(out,'writing-owners.png'));
const frames=[],records=[];
for(let i=0;i<24;i++){
 const phase=i/24*2*Math.PI,buf=new P.Buf(96,132),pose={writing_arm:{a:Math.sin(phase)*.035,dx:Math.sin(phase)*.8,dy:Math.sin(phase*2)*.25},quill:{a:Math.sin(phase+.2)*.075}};
 rig.draw(buf,0,0,pose);let outsideChanges=0,insideChanges=0;
 for(let y=0;y<132;y++)for(let x=0;x<96;x++){if(buf.px[y*96+x]!==source.px[y*96+x]){if(x<28||x>49||y<59||y>85)outsideChanges++;else insideChanges++;}}
 if(outsideChanges)throw Error('Unexpected non-writing movement '+i+':'+outsideChanges);
 const file=path.join(out,`write-loop-${String(i).padStart(2,'0')}.png`);P.save(buf,file);frames.push(buf);records.push({frame:i,pose,insideChangedPixels:insideChanges,outsideChangedPixels:outsideChanges,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
}
P.save(P.sheet(frames.map((buf,i)=>({buf,label:String(i).padStart(2,'0')})),{cols:6,scale:3}),path.join(out,'writing-preview.png'));fs.writeFileSync(path.join(out,'writing.gif'),P.gif(frames,{delay:125,scale:4}));
const packed=P.pack(frames,{cols:6});P.save(packed,path.join(out,'writing-atlas.png'));
const record={tool:'Codixel',actualExecution:true,input,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),inputNativeCanvas:[96,132],alpha:'binary; Rig nearest sampling preserves shared palette',frames:24,fps:8,loopSeconds:3,bones:[{name:'body',fixed:true},{name:'writing_arm',pivot:[31,76],hand:[43,79]},{name:'quill',pivot:[43,79],featherTip:[34,63]}],contactHints:{nib:[44,81],bookHoldingHand:[61,80],soleY:123},outsideWritingRegionUnchanged:true,changedRegion:[28,59,49,85],clip:{frames:records.map((_,i)=>`codixel-writing/write-loop-${String(i).padStart(2,'0')}.png`),canvas:[96,132],anchor:[48,125],gameScale:1,fps:8,loop:true},records};
fs.writeFileSync(path.join(__dirname,'writing-loop-execution.json'),JSON.stringify(record,null,2));console.log(JSON.stringify({out,frames:24,uniqueFrames:new Set(records.map(x=>x.sha256)).size,outsideWritingChanges:0}));
