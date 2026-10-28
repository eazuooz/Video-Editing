const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('C:/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT = __dirname;
const OUT = path.join(ROOT, 'covers');
fs.mkdirSync(OUT, {recursive:true});
// All picture pixels below come from the recorded, unmodified source assets.
// The SVG adds only crop/scale, vector typography and editorial focus outlines.
const design = [
 ['NOITA', '배경인 줄 알았는데', '전부 움직인다?', 1.15, 960,540, 470,650,220,190],
 ['VIEWFINDER', '사진 한 장이', '진짜 길이 된다?', 1, 960,540, 1020,460,325,180],
 ['RAIN WORLD', '이 캐릭터의 몸은', '공 두 개라고?', 2.2, 550,520, 530,500,75,115],
 ['OUTER WILDS', '작은 행성의 중력', '현실과 다르다?', 1.45, 1190,490, 1190,510,230,195],
 ['RETURN OF THE OBRA DINN', '색은 딱 두 개', '그림자는 어떻게?', 1.12, 960,650, 1310,610,210,175],
 ['DIABLO II: RESURRECTED', '화면이 넓어지면', '적이 반격 못 한다?', 1.35, 1130,625, 1530,690,140,125],
 ['DIABLO II: RESURRECTED', '아이템이 안 보이자', '풀을 비켜 줬다', 1.4, 840,660, 820,778,90,70],
 ['DIABLO II', '갑옷을 바꾸는 순간', '그림을 갈아 끼운다', 2.2, 960,470, 960,470,70,125],
 ['DIABLO II: RESURRECTED', '버튼 하나 눌렀더니', '20년 전 그래픽?', 1.1, 960,540, 970,600,220,170],
 ['DIABLO II: RESURRECTED', '패드로 만들려고', '길 찾기를 껐다?', 1.8, 960,535, 953,451,85,115],
 ['CUPHEAD', '그림은 24프레임', '왜 매끄러울까?', 1.05, 1030,540, 690,515,135,145],
 ['TEARDOWN', '칠한 건 색인데', '바뀐 건 번호?', 1.08, 900,600, 610,650,235,155],
 ['SPLATOON', '잉크가 반짝이면', '적이 안 보인다?', 1.05, 1050,580, 1335,893,190,95],
 ['SPLATOON', '벽에 남은 잉크', '어떻게 붙일까?', 1.06, 1090,580, 1090,450,135,190],
];
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const label = (txt, x,y,size,fill,extra='') => `<text x="${x}" y="${y}" font-family="Malgun Gothic,맑은 고딕,sans-serif" font-weight="900" font-size="${size}" fill="${fill}" ${extra}>${esc(txt)}</text>`;
function buildSvg(item,d) {
 const [game,first,second,z,cx,cy,fx,fy,rx,ry] = d;
 const source = fs.readFileSync(item.sourceFramePath);
 if(sha(source)!==item.sourceFrameSHA256) throw Error('Source changed: '+item.slug);
 const mime = path.extname(item.sourceFramePath).toLowerCase()==='.png'?'image/png':'image/jpeg';
 const s = 1280/1920*z;
 const tx=640-cx*s, ty=435-cy*s;
 const xx=fx*s+tx, yy=fy*s+ty;
 const font1=Math.min(58,1120/(first.length*.96)), font2=Math.min(79,1120/(second.length*.96));
 const marking= yy>245 ? `<ellipse cx="${xx}" cy="${yy}" rx="${rx*s}" ry="${ry*s}" fill="none" stroke="#10141b" stroke-width="12"/><ellipse cx="${xx}" cy="${yy}" rx="${rx*s}" ry="${ry*s}" fill="none" stroke="#55E1E8" stroke-width="6"/>` : '';
 return {svg:`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1280" height="720" viewBox="0 0 1280 720">
 <rect width="1280" height="720" fill="#050505"/>
 <image x="${tx}" y="${ty}" width="${1920*s}" height="${1080*s}" preserveAspectRatio="xMidYMid meet" xlink:href="data:${mime};base64,${source.toString('base64')}"/>
 ${marking}
 <rect width="1280" height="218" fill="#050505"/>
 ${label(first,42,85,font1,'#FFFFFF')}
 ${label(second,40,179,font2,'#FFD15A')}
 <path d="M42 211H1238" stroke="#FFD15A" stroke-width="4"/>
 <rect x="24" y="669" width="${Math.min(700,game.length*16+34)}" height="34" fill="#050505" fill-opacity=".88"/>
 ${label(game,40,694,23,'#FFFFFF','letter-spacing=".4"')}
 </svg>`, transform:{scale:s,translateX:tx,translateY:ty,sourceWidth:1920,sourceHeight:1080}, focus:{source:{x:fx,y:fy,rx,ry},output:{x:xx,y:yy},editorial:true}};
}
(async()=>{
 const audit=JSON.parse(fs.readFileSync(path.join(ROOT,'assets-audit.json'),'utf8'));
 const covers=[];
 for(let i=0;i<audit.items.length;i++) {
  const item=audit.items[i], d=design[i];
  const {svg,transform,focus}=buildSvg(item,d);
  const svgPath=path.join(OUT,item.slug+'.svg');
  const pngPath=path.join(OUT,item.slug+'.png');
  const jpgPath=path.join(OUT,item.slug+'.jpg');
  fs.writeFileSync(svgPath,svg);
  await sharp(Buffer.from(svg)).png().toFile(pngPath);
  await sharp(pngPath).jpeg({quality:94,mozjpeg:true}).toFile(jpgPath);
  const mobilePath=path.join(OUT,item.slug+'.mobile-375.png');
  await sharp(pngPath).resize(375,211).png().toFile(mobilePath);
  covers.push({...item,game:d[0],headline:d.slice(1,3),svgPath,pngPath,jpgPath,mobilePath,svgSHA256:sha(fs.readFileSync(svgPath)),pngSHA256:sha(fs.readFileSync(pngPath)),jpgSHA256:sha(fs.readFileSync(jpgPath)),dimensions:[1280,720],transform,focus,rendering:{renderer:'sharp/librsvg',gpu:false,font:'Malgun Gothic Bold',bitmapUnchanged:true,sourceRepainted:false},qa:{originalsInspected:true,contactSheetInspected:false,mobileInspected:false},platformApplied:false});
 }
 const composites=[];
 for(let i=0;i<covers.length;i++) {
  composites.push({input:await sharp(covers[i].pngPath).resize(480,270).toBuffer(),left:(i%2)*480,top:Math.floor(i/2)*298+28});
  const title=`<svg width="480" height="28"><rect width="480" height="28" fill="#222"/><text x="8" y="20" font-family="Arial" font-size="14" fill="white">${i+1}. ${esc(covers[i].videoId)} — ${esc(covers[i].game)}</text></svg>`;
  composites.push({input:Buffer.from(title),left:(i%2)*480,top:Math.floor(i/2)*298});
 }
 const contactPath=path.join(ROOT,'cover-contact.jpg');
 await sharp({create:{width:960,height:2086,channels:3,background:'#000'}}).composite(composites).jpeg({quality:92}).toFile(contactPath);
 const result={version:'actual-game-svg-cover-v2',createdAt:new Date().toISOString(),note:'Local cover design only. No platform mutation. Actual gameplay pixels are embedded unchanged; transform and vector editorial annotations recorded.',contactPath,coverCount:covers.length,covers};
 fs.writeFileSync(path.join(ROOT,'covermap.json'),JSON.stringify(result,null,2));
 let html='<!doctype html><html lang="ko"><meta charset="utf-8"><title>얌얌코딩 쇼츠 표지 14편</title><style>body{background:#111;color:white;font:16px "Malgun Gothic",sans-serif;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}img{width:100%;height:auto}article{max-width:640px}a{color:#FFD15A}</style><h1>실제 게임 화면 기반 쇼츠 표지 · 14편</h1><p>1280×720 · SVG 원본 보존 · 마스코트 없음 · 플랫폼 적용 전</p><main>';
 covers.forEach(c=>html+=`<article><a href="covers/${c.slug}.png"><img src="covers/${c.slug}.jpg" alt="${esc(c.headline.join(' '))}"></a><p>${esc(c.game)} · ${c.videoId}<br>${esc(c.headline.join(' / '))}</p></article>`);
 fs.writeFileSync(path.join(ROOT,'covers-review.html'),html+'</main></html>');
 console.log(JSON.stringify({count:covers.length,contactPath,covermap:path.join(ROOT,'covermap.json')}));
})();
