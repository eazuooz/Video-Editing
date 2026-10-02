const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname,'..','output','youtube-library-refresh','v2');
const manifest = JSON.parse(fs.readFileSync(path.join(root,'prompts.json'),'utf8'));
function size(bytes) {
  let offset=2;
  while(offset<bytes.length){
    if(bytes[offset]!==255)throw new Error('Invalid JPEG marker');
    const marker=bytes[offset+1];
    const length=bytes.readUInt16BE(offset+2);
    if([0xc0,0xc1,0xc2].includes(marker))return {width:bytes.readUInt16BE(offset+7),height:bytes.readUInt16BE(offset+5)};
    offset+=2+length;
  }
  throw new Error('No JPEG dimensions');
}
const generated=[];const failures=[];
for(const item of manifest.items){
  const file=path.join(root,'thumbnails',`${item.id}.jpg`);
  if(!fs.existsSync(file))continue;
  const bytes=fs.readFileSync(file);const dimensions=size(bytes);
  const sha256=crypto.createHash('sha256').update(bytes).digest('hex');
  if(dimensions.width!==1280||dimensions.height!==720||bytes.length>2*1024*1024)failures.push({id:item.id,...dimensions,bytes:bytes.length});
  generated.push({id:item.id,...dimensions,bytes:bytes.length,sha256});
}
const duplicates=generated.filter((x,i)=>generated.findIndex(y=>x.sha256===y.sha256)!==i);
const result={checkedAt:new Date().toISOString(),generated:generated.length,total:manifest.count,pending:manifest.count-generated.length,failures,duplicates,files:generated};
fs.writeFileSync(path.join(root,'validation.json'),`${JSON.stringify(result,null,2)}\n`);
console.log(JSON.stringify({...result,files:undefined}));
if(failures.length||duplicates.length)process.exitCode=1;
