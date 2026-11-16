const fs=require('node:fs'),path=require('node:path');
const {Resvg}=require('C:/Users/1/AppData/Local/YamyamCoding/VideoEditingWork/game-math-upload-20261117/node_modules/@resvg/resvg-js');
const batch=JSON.parse(fs.readFileSync(path.join(__dirname,'batch.json'),'utf8'));
const cat='data:image/png;base64,'+fs.readFileSync('D:/Github/VideoEditing/shared/assets/branding/cat-reactions-v1/realize.png').toString('base64');
for(const r of batch.rows){const dir=path.join(__dirname,r.id);let svg=fs.readFileSync(path.join(dir,'thumbnail.svg'),'utf8').replace('{{CAT_URI}}',cat);const x=new Resvg(svg,{font:{fontFiles:['C:/Windows/Fonts/malgunbd.ttf','C:/Windows/Fonts/malgun.ttf'],loadSystemFonts:false,defaultFontFamily:'Malgun Gothic'}});fs.writeFileSync(path.join(dir,'thumbnail.png'),x.render().asPng());console.log(r.id,'thumbnail rendered');}
