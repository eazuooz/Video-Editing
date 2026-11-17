// Validate reviewed illustrated assets; the rejected geometric SVG renderer is retired.
const fs=require('node:fs'),path=require('node:path');
const batch=JSON.parse(fs.readFileSync(path.join(__dirname,'batch.json'),'utf8'));
for(const row of batch.rows){
 const file=path.join(__dirname,'thumbnail-revision-v2',row.id,'thumbnail.png');
 const png=fs.readFileSync(file);
 if(png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error(row.id+': invalid PNG');
 const w=png.readUInt32BE(16),h=png.readUInt32BE(20);
 if(w<1280||Math.abs(w/h-16/9)>.01||png.length>=2097152)throw new Error(row.id+': invalid thumbnail size');
 console.log(row.id,'reviewed illustrated thumbnail',w,h,png.length);
}
