const fs = require('fs'), path = require('path'), crypto = require('crypto');
const sharp = require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT=__dirname, OUT=path.join(ROOT,'covers');
const PRIOR='C:/Users/1/Videos/YamyamProduction/shorts-private-schedule-20261028/covermap.json';
const FONT='Noto Sans KR';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const txt=(s,x,y,size,fill,extra='')=>`<text x="${x}" y="${y}" text-anchor="middle" font-family="${FONT},Malgun Gothic,sans-serif" font-weight="900" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
async function metrics(s,size){
  const test=`<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="500">${txt(s,1500,300,size,'white')}</svg>`;
  const {info}=await sharp(Buffer.from(test)).trim().png().toBuffer({resolveWithObject:true});
  return {width:info.width,height:info.height,left:info.trimOffsetLeft,top:info.trimOffsetTop};
}
async function fitted(s){
  let size=190,m=await metrics(s,size);
  if(m.width>956){size=Math.floor(190*956/m.width);m=await metrics(s,size);}
  if(size<135)throw Error(`Hook too long for readable cover: ${s}, font ${size}`);
  if(m.width>960||m.height>205)throw Error(`Text bounds exceed cover: ${s}`);
  return {text:s,fontSize:size,ink:m,gridFontSize180:size/6,gridInkHeight180:m.height/6};
}
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const old=JSON.parse(fs.readFileSync(PRIOR,'utf8'));
  const proposal=JSON.parse(fs.readFileSync(path.join(ROOT,'title-proposals.json'),'utf8'));
  const arr=Array.isArray(proposal)?proposal:(proposal.items||proposal.proposals);
  if(!Array.isArray(arr)||arr.length!==14)throw Error('Expected final fourteen title proposals');
  const result=[];
  for(const c of old.covers){
    const p=arr.find(x=>x.videoId===c.videoId); if(!p)throw Error('Missing proposal '+c.videoId);
    const lines=p.thumbnailLines;if(!Array.isArray(lines)||lines.length!==2)throw Error('Two concise title lines required');
    if(sha(c.sourceFramePath)!==c.sourceFrameSHA256)throw Error('Changed source '+c.slug);
    const t={...c.transform};
    if(c.videoId==='Tt7hCWPjcpc')t.translateX+=120;
    const f=c.focus.source,fx=f.x*t.scale+t.translateX,fy=f.y*t.scale+t.translateY;
    const lineMetrics=await Promise.all(lines.map(fitted));
    const source=fs.readFileSync(c.sourceFramePath);
    const mime=path.extname(c.sourceFramePath).toLowerCase()==='.png'?'image/png':'image/jpeg';
    const badgeSize=Math.min(47,950/(c.game.length*.65));
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1920" viewBox="0 0 1080 1920">
      <defs><clipPath id="game"><rect x="0" y="530" width="1080" height="1390"/></clipPath></defs>
      <rect width="1080" height="1920" fill="#050505"/>
      <g clip-path="url(#game)"><image x="${t.translateX}" y="${t.translateY}" width="${1920*t.scale}" height="${1080*t.scale}" preserveAspectRatio="xMidYMid meet" xlink:href="data:${mime};base64,${source.toString('base64')}"/>
      <ellipse cx="${fx}" cy="${fy}" rx="${f.rx*t.scale}" ry="${f.ry*t.scale}" fill="none" stroke="#050505" stroke-width="25"/>
      <ellipse cx="${fx}" cy="${fy}" rx="${f.rx*t.scale}" ry="${f.ry*t.scale}" fill="none" stroke="#55E1E8" stroke-width="13"/></g>
      <rect width="1080" height="530" fill="#050505"/>
      ${txt(lines[0],540,235,lineMetrics[0].fontSize,'#FFFFFF')}
      ${txt(lines[1],540,450,lineMetrics[1].fontSize,'#FFD15A')}
      <rect x="38" y="1808" width="1004" height="74" fill="#050505" fill-opacity=".94"/>
      ${txt(c.game,540,1861,badgeSize,'#FFFFFF')}
    </svg>`;
    const stem=path.join(OUT,c.slug+'.readable-v4');
    fs.writeFileSync(stem+'.svg',svg);
    await sharp(Buffer.from(svg)).png().toFile(stem+'.png');
    await sharp(stem+'.png').jpeg({quality:94,mozjpeg:true}).toFile(stem+'.jpg');
    for(const width of [375,180])await sharp(stem+'.png').resize(width,Math.round(width*1920/1080)).png().toFile(stem+`.mobile-${width}.png`);
    const focusBounds={left:fx-f.rx*t.scale-13,right:fx+f.rx*t.scale+13,top:fy-f.ry*t.scale-13,bottom:fy+f.ry*t.scale+13};
    if(focusBounds.left<0||focusBounds.right>1080||focusBounds.top<530||focusBounds.bottom>1808)throw Error('Target outline clipped '+c.slug+' '+JSON.stringify(focusBounds));
    const item={videoId:c.videoId,slug:c.slug,game:c.game,priorTitle:p.currentTitle,proposedTitle:p.proposedTitle,headline:lines,sourceFramePath:c.sourceFramePath,sourceFrameSHA256:c.sourceFrameSHA256,sourceFrameDimensions:c.sourceFrameDimensions,sourceProvenance:c.sourceProvenance,masterSHA256:c.masterSHA256,priorCoverPath:c.jpgPath,priorCoverSHA256:c.jpgSHA256,svgPath:stem+'.svg',pngPath:stem+'.png',jpgPath:stem+'.jpg',mobilePath:stem+'.mobile-375.png',gridPath:stem+'.mobile-180.png',dimensions:[1080,1920],transform:{...t,portraitViewport:{x:0,y:530,width:1080,height:1390}},focus:{source:f,output:{x:fx,y:fy},bounds:focusBounds,editorial:true},typography:{fontFamily:FONT,fontWeight:900,maxInkWidth:960,headerHeight:530,lineMetrics,nominalFontRange:[135,190],fontPath:'C:/Windows/Fonts/NotoSansKR-VF.ttf',fontSHA256:sha('C:/Windows/Fonts/NotoSansKR-VF.ttf')},rendering:{renderer:'sharp/librsvg',gpu:false,sourceBitmapRepainted:false,sourceBitmapBytesEmbeddedUnchanged:true},qa:{priorOriginalInspected:true,grid180Inspected:false,mobile375Inspected:false,textInkBoundsPass:true,focusBoundsPass:true,actualStudioApplied:false}};
    for(const ext of ['svg','png','jpg'])item[ext+'SHA256']=sha(item[ext+'Path']);
    item.jpgBytes=fs.statSync(item.jpgPath).size;if(item.jpgBytes>2000000)throw Error('Too large');
    result.push(item);
  }
  const comp=[];
  for(let i=0;i<result.length;i++)comp.push({input:result[i].gridPath,left:(i%4)*200+10,top:Math.floor(i/4)*345+12});
  const grid=path.join(ROOT,'readable-grid-180.png');
  await sharp({create:{width:800,height:1380,channels:3,background:'#333'}}).composite(comp).png().toFile(grid);
  const mobile=[];
  for(let b=0;b<2;b++){
    const part=result.slice(b*7,b*7+7),cells=part.map((c,i)=>({input:c.mobilePath,left:(i%3)*395+10,top:Math.floor(i/3)*692+10}));
    const file=path.join(ROOT,`readable-mobile-${b+1}.png`);
    await sharp({create:{width:1185,height:2076,channels:3,background:'#333'}}).composite(cells).png().toFile(file);mobile.push(file);
  }
  const map={version:'actual-game-big-type-short-hooks-v4',createdAt:new Date().toISOString(),scope:'Same recent fourteen uploaded Shorts; local cover assets only',priorMap:PRIOR,priorMapSHA256:sha(PRIOR),coverCount:14,covers:result,gridContactPath:grid,mobileContactPaths:mobile,qaStatus:'rendered-awaiting-visual-review',platformMutation:false,sourceBitmapRepainted:false};
  fs.writeFileSync(path.join(ROOT,'covermap.json'),JSON.stringify(map,null,2));
  fs.writeFileSync(path.join(ROOT,'covers-review.html'),'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>쇼츠 큰 글씨 표지</title><style>body{background:#111;color:white;font:16px system-ui;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:24px}article{max-width:375px}img{width:100%}h1{color:#FFD15A}</style><h1>모바일에서 읽히는 쇼츠 표지</h1><main>'+result.map(c=>`<article><img src="covers/${path.basename(c.jpgPath)}" alt="${esc(c.headline.join(' '))}"><p>${esc(c.proposedTitle)}</p></article>`).join('')+'</main></html>');
  console.log(JSON.stringify({count:14,gridContactPath:grid,mobileContactPaths:mobile,minFont:Math.min(...result.flatMap(c=>c.typography.lineMetrics.map(m=>m.fontSize))),maxJpg:Math.max(...result.map(c=>c.jpgBytes))}));
})();
