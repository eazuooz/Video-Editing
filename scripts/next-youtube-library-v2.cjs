const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname,'..','output','youtube-library-refresh','v2');
const manifest = JSON.parse(fs.readFileSync(path.join(root,'prompts.json'),'utf8'));
const args = process.argv.slice(2);
const explicit = args.filter(x=>/^[\w-]{11}$/.test(x));
const limit = Number(args.find(x=>/^\d+$/.test(x)) || 4);
const pending=manifest.items.filter(x=>!fs.existsSync(path.join(root,'thumbnails',`${x.id}.jpg`)));
if(args.includes('--ids')){
  console.log(JSON.stringify({referenceImage:manifest.referenceImage,total:manifest.count,pending:pending.length,ids:pending.map(x=>x.id)}));
  process.exit(0);
}
const items = explicit.length ? explicit.map(id=>pending.find(x=>x.id===id)).filter(Boolean) : pending.slice(0,limit);
console.log(JSON.stringify({referenceImage:manifest.referenceImage,total:manifest.count,pending:pending.length,items}));
