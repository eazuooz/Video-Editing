// Local-only, read-only viewer for acquired research video. It does not render or upload.
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const files={yareli155:path.join(root,'shared/output/player-customization/research/yareli-devstream155-v1/8eUfnQ8mWXs-yareli-2721-3087.mp4')};
const html=`<!doctype html><html lang="ko"><meta charset="utf-8"><title>Player customization Yareli155 native review</title>
<style>body{font:16px Arial,sans-serif;margin:16px;background:#eee;color:#111}button,input,select{font:inherit;margin:3px;padding:5px}h1{font-size:22px}#viewport{position:relative;width:960px;max-width:100%;aspect-ratio:16/9;overflow:hidden;background:#111}video{position:absolute;max-width:none}#cap{display:none;position:absolute;left:50%;top:calc(970/1080*100%);transform:translate(-50%,-50%);background:white;border:1.5px solid #161b18;box-shadow:7px 7px #073c32;color:#080b09;padding:5.5px 11px;font:500 24px/31px 'Malgun Gothic',sans-serif;white-space:nowrap;text-align:center}#status{font-family:monospace}label{display:inline-block}small{display:block;max-width:1000px;line-height:1.6}</style>
<h1>Player customization — local source/crop review</h1><small>Research only. Nominal source offsets are navigation aids. No final caption, action-boundary, timing or quota approval is implied. Yareli: 2021 official developer preview; current build performance is not inferred.</small>
<div><label>Source <select id="source"><option value="yareli155">2021 Yareli developer preview</option></select></label><button id="load">Load selected source</button></div>
<div><label>Local seconds <input id="seek" type="number" value="20" step="0.05" min="0"></label><label>Stop at seconds <input id="stop" type="number" value="0" step="0.05" min="0" style="width:85px"></label><button id="go">Seek and pause</button><button id="back">−1 sec</button><button id="next">+1 sec</button><button id="play">Play</button><button id="pause">Pause</button><button id="caption">Toggle two-line caption-position test</button></div>
<div><label>Crop x<input id="x" type="number" value="0" style="width:70px"></label><label>y<input id="y" type="number" value="0" style="width:70px"></label><label>w<input id="w" type="number" value="1920" style="width:90px"></label><label>h<input id="h" type="number" value="1080" style="width:90px"></label><button id="apply">Apply crop</button><button id="reset">Full native frame</button></div>
<p id="status">Source not loaded</p><div id="viewport"><video id="video" muted preload="metadata"></video><div id="cap">선택한 능력의 범위와 움직임을 봅니다.<br>이 문구는 고정 자막 자리만 확인하는 시험입니다.</div></div>
<script>
const ids=['source','seek','stop','x','y','w','h','video','status'];const e=Object.fromEntries(ids.map(k=>[k,document.getElementById(k)]));let key='yareli155';
function crop(){const [x,y,w,h]=['x','y','w','h'].map(k=>Number(e[k].value));if(!(w>0&&h>0&&x>=0&&y>=0&&x+w<=1920&&y+h<=1080))return;e.video.style.width=(1920/w*100)+'%';e.video.style.height=(1080/h*100)+'%';e.video.style.left=(-x/w*100)+'%';e.video.style.top=(-y/h*100)+'%';}
function status(){const t=e.video.currentTime||0;const offset={yareli155:2721}[key];e.status.textContent=key+' | local '+t.toFixed(3)+' sec | nominal source '+(t+offset).toFixed(3)+' sec | '+(e.video.paused?'paused':'playing')+' | native '+e.video.videoWidth+'×'+e.video.videoHeight+' | duration '+(e.video.duration||0).toFixed(3);}
function seek(t){e.video.pause();e.video.currentTime=Math.max(0,Math.min(t,e.video.duration||t));e.seek.value=t.toFixed(3);status();}
document.getElementById('load').onclick=()=>{key=e.source.value;e.video.src='/media/'+key;e.video.load();};
document.getElementById('go').onclick=()=>seek(Number(e.seek.value));document.getElementById('back').onclick=()=>seek(e.video.currentTime-1);document.getElementById('next').onclick=()=>seek(e.video.currentTime+1);
document.getElementById('play').onclick=()=>e.video.play();document.getElementById('pause').onclick=()=>{e.video.pause();status();};document.getElementById('apply').onclick=crop;
document.getElementById('reset').onclick=()=>{for(const [k,v]of Object.entries({x:0,y:0,w:1920,h:1080}))e[k].value=v;crop();};
document.getElementById('caption').onclick=()=>{const c=document.getElementById('cap');c.style.display=c.style.display==='block'?'none':'block';};
e.video.ontimeupdate=()=>{const end=Number(e.stop.value);if(end>0&&!e.video.paused&&e.video.currentTime>=end)e.video.pause();status();};e.video.onloadedmetadata=()=>{crop();status();};e.video.onseeked=status;e.video.onpause=status;e.video.onplay=status;e.video.onended=status;
crop();</script></html>`;
const server=http.createServer((req,res)=>{
  if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
  const url=new URL(req.url,'http://127.0.0.1:9248');
  if(url.pathname==='/'){res.writeHead(200,{'Content-Type':'text/html;charset=utf-8','Cache-Control':'no-store'});res.end(req.method==='HEAD'?'':html);return;}
  const key=url.pathname.startsWith('/media/')?url.pathname.slice(7):'';const file=files[key];
  if(!file||!fs.existsSync(file)){res.writeHead(404);res.end('No acquired source');return;}
  const size=fs.statSync(file).size;const range=req.headers.range;let start=0,end=size-1;
  if(range){const m=/^bytes=(\d+)-(\d*)$/.exec(range);if(!m){res.writeHead(416);res.end();return;}start=Number(m[1]);if(m[2])end=Math.min(Number(m[2]),size-1);if(start>end){res.writeHead(416);res.end();return;}}
  const headers={'Content-Type':'video/mp4','Accept-Ranges':'bytes','Content-Length':end-start+1,'Cache-Control':'no-store'};
  if(range)headers['Content-Range']=`bytes ${start}-${end}/${size}`;
  res.writeHead(range?206:200,headers);if(req.method==='HEAD')res.end();else fs.createReadStream(file,{start,end}).pipe(res);
});
server.listen(9248,'127.0.0.1',()=>console.log(JSON.stringify({pid:process.pid,url:'http://127.0.0.1:9248',scope:'Only acquired local Yareli155 source; no filesystem mutations',finalDelivery:false})));
