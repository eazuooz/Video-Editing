const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT=__dirname,OUT=path.join(ROOT,'covers');
// Source pixels are retained verbatim in an image element. Only uniform scale,
// portrait framing, vector title and editorial target outlines are added.
const frames=[
 [580,610,1.5], [1030,545,1.5], [530,500,3.05], [1190,490,1.7],
 [1240,610,1.5], [1340,650,1.5], [770,740,1.8], [960,470,2.9],
 [960,570,1.65], [953,451,3.0], [920,540,1.44], [670,660,1.65],
 [1270,770,1.6], [1090,500,1.7]
];
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const text=(s,y,size,color)=>`<text x="540" y="${y}" text-anchor="middle" font-family="Malgun Gothic,맑은 고딕,sans-serif" font-weight="900" font-size="${size}" fill="${color}">${esc(s)}</text>`;
(async()=>{
 const mapPath=path.join(ROOT,'covermap.json');
 const m=JSON.parse(fs.readFileSync(mapPath,'utf8'));
 if(!fs.existsSync(path.join(ROOT,'covermap.landscape-v2.json')))fs.copyFileSync(mapPath,path.join(ROOT,'covermap.landscape-v2.json'));
 for(let i=0;i<m.covers.length;i++){
  const c=m.covers[i], [cx,cy,scale]=frames[i];
  if(c.sourceFrameSHA256!==sha(c.sourceFramePath))throw Error('sourcehash '+c.slug);
  const tx=540-cx*scale,ty=1130-cy*scale;
  const f=c.focus.source, fx=f.x*scale+tx,fy=f.y*scale+ty;
  const mime=path.extname(c.sourceFramePath).toLowerCase()==='.png'?'image/png':'image/jpeg';
  const first=c.headline[0],second=c.headline[1];
  const a=Math.min(92,870/(first.length*.96)),b=Math.min(108,900/(second.length*.96));
  const gameSize=Math.min(28,900/(c.game.length*.65));
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1920" viewBox="0 0 1080 1920">
   <defs><clipPath id="game"><rect x="0" y="370" width="1080" height="1550"/></clipPath></defs>
   <rect width="1080" height="1920" fill="#050505"/>
   <g clip-path="url(#game)"><image x="${tx}" y="${ty}" width="${1920*scale}" height="${1080*scale}" preserveAspectRatio="xMidYMid meet" xlink:href="data:${mime};base64,${fs.readFileSync(c.sourceFramePath).toString('base64')}"/>
   <ellipse cx="${fx}" cy="${fy}" rx="${f.rx*scale}" ry="${f.ry*scale}" fill="none" stroke="#10141b" stroke-width="17"/><ellipse cx="${fx}" cy="${fy}" rx="${f.rx*scale}" ry="${f.ry*scale}" fill="none" stroke="#55E1E8" stroke-width="9"/></g>
   <rect width="1080" height="370" fill="#050505"/>
   ${text(first,148,a,'#FFFFFF')}${text(second,285,b,'#FFD15A')}
   <path d="M72 355H1008" stroke="#FFD15A" stroke-width="5"/>
   <rect x="60" y="1805" width="960" height="56" fill="#050505" fill-opacity=".9"/>
   ${text(c.game,1844,gameSize,'#FFFFFF')}
  </svg>`;
  const stem=path.join(OUT,c.slug+'.portrait');
  fs.writeFileSync(stem+'.svg',svg);
  await sharp(Buffer.from(svg)).png().toFile(stem+'.png');
  await sharp(stem+'.png').jpeg({quality:94,mozjpeg:true}).toFile(stem+'.jpg');
  await sharp(stem+'.png').resize(375,667).png().toFile(stem+'.mobile-375.png');
  c.landscape=c.landscape||{svgPath:c.svgPath,pngPath:c.pngPath,jpgPath:c.jpgPath,pngSHA256:c.pngSHA256,jpgSHA256:c.jpgSHA256,dimensions:c.dimensions};
  c.svgPath=stem+'.svg';c.pngPath=stem+'.png';c.jpgPath=stem+'.jpg';c.mobilePath=stem+'.mobile-375.png';
  c.svgSHA256=sha(c.svgPath);c.pngSHA256=sha(c.pngPath);c.jpgSHA256=sha(c.jpgPath);c.dimensions=[1080,1920];c.jpgBytes=fs.statSync(c.jpgPath).size;
  c.transform={scale,translateX:tx,translateY:ty,sourceWidth:1920,sourceHeight:1080,portraitViewport:{x:0,y:370,width:1080,height:1550}};
  c.focus.output={x:fx,y:fy};c.qa={originalsInspected:true,contactSheetInspected:false,mobileInspected:false,mobileWidth:375,portraitSafeTextWidth:900};
  if(c.jpgBytes>=2000000)throw Error('image size '+c.slug);
 }
 const sheets=[];
 for(let batch=0;batch<2;batch++){
  const group=m.covers.slice(batch*7,batch*7+7), comp=[];
  for(let j=0;j<group.length;j++)comp.push({input:group[j].mobilePath,left:(j%3)*375,top:Math.floor(j/3)*687+20});
  const p=path.join(ROOT,`portrait-mobile-${batch+1}.png`);
  await sharp({create:{width:1125,height:2061,channels:3,background:'#333'}}).composite(comp).png().toFile(p);sheets.push(p);
 }
 m.version='actual-game-portrait-svg-cover-v3';m.portraitContactPaths=sheets;m.qaStatus='portrait-rendered-awaiting-visual-check';m.note='1080x1920 portrait chosen for Shorts preview, with centered headlines inside safe width. Landscape v2 files and map preserved. No platform mutation.';
 fs.writeFileSync(mapPath,JSON.stringify(m,null,2));
 let html='<!doctype html><html lang="ko"><meta charset="utf-8"><title>쇼츠 세로 표지 14편</title><style>body{background:#111;color:#fff;font:16px "Malgun Gothic",sans-serif;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{max-width:375px}img{width:100%}a{color:#FFD15A}</style><h1>쇼츠 세로 표지 · 1080×1920</h1><main>';
 for(const c of m.covers)html+=`<article><a href="covers/${c.slug}.portrait.png"><img src="covers/${c.slug}.portrait.jpg" alt="${esc(c.headline.join(' '))}"></a><p>${c.videoId} · ${esc(c.game)}</p></article>`;
 fs.writeFileSync(path.join(ROOT,'covers-review-portrait.html'),html+'</main></html>');
 console.log(JSON.stringify({count:m.covers.length,portraitContactPaths:sheets,maxJpgBytes:Math.max(...m.covers.map(x=>x.jpgBytes))}));
})();
