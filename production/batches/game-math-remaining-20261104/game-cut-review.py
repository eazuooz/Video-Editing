"""Build a local native-motion proof from the actual selected files and tracks.

For editorial checks while complete lectures render. No game re-encode, invented
timing, platform access, or reference-lesson footage. Separate original sound
follows its recorded source offset. This is not a final audiovisual QA receipt.
"""
from pathlib import Path
import json,os,hashlib,html
from urllib.parse import quote
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OUT=R/'output/game-math-remaining-20261104'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow']
def url(p):
 p=(R/p).resolve();assert p.is_relative_to(R) and p.is_file()
 return quote(Path(os.path.relpath(p,OUT)).as_posix(),safe='/')
rows=[]
for ep in read(B/'batch.json')['items'][1:]:
 p=R/'projects'/ep['slug'];assert p.name in c['projectSlugs']
 sources={s['id']:s for s in read(p/'planning/footage-audit.json')['sources']};windows=read(p/'planning/game-annotation-tracks.json')['windows']
 for s in read(p/'planning/scene-bindings.json')['scenes']:
  g=s.get('actualGamePart')
  if not g:continue
  source=sources[g['sourceId']];assert source['sha256']==g['sourceSha256'] and g['playbackRate']==1 and not g['freezePadding'] and not g['loop']
  ws=[]
  for w in windows:
   if w['sourceId']!=g['sourceId'] or min(w['end'],g['sourceOut'])<=max(w['start'],g['sourceIn']):continue
   data=read(R/w['trackFile']);assert data['sourceSha256']==source['sha256']
   ws.append(dict(phases=w.get('observedPhases',[]),label=data['label'],start=data['start'],end=data['end'],frames=[{k:f[k] for k in ('time','bbox','points','visible') if k in f} for f in data['keyframes']]))
  assert ws
  a=source.get('audio',{});sound=a.get('separateFullOriginalAudio') or a.get('separateOriginalAudio') or a.get('recoveredOriginalAudio')
  speech=s['speech'];prefix=g['speechTarget']['prefixKo'];i=speech.index(prefix);end=g['speechTarget'].get('endBeforeKo')
  spoken=speech[i:speech.index(end,i) if end else None];assert spoken.strip()
  # Do not imply an estimated audio cue is the finished narration: this is
  # the preceding and following text that an editor compares to the shot.
  rows.append(dict(ep=ep['id'],title=ep['title'],sid=s['id'],game=source['game'],file=url(source['file']),sound=url(sound) if sound else None,offset=g.get('fullOriginalAudioIn',g['sourceIn'])-g['sourceIn'] if sound else 0,start=g['sourceIn'],end=g['sourceOut'],minEnd=g.get('minimumObservedResultOut',g['sourceOut']),speech=spoken,tracks=ws))
  if g.get('nativeDetailInset'):rows[-1]['inset']=g['nativeDetailInset']
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 | 게임 장면 검수</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{max-width:1100px;background:#101111;color:#f4f3ef;font:17px/1.6 system-ui;margin:20px auto;padding:0 16px}a{color:#88d1c8}h1,h2{color:#f2d072;line-height:1.25}label{display:block;font-size:.9em;margin:.3em 0}select,button{font:inherit;margin:3px 3px 4px 0;padding:6px 9px;max-width:100%}p{max-width:58em}#screen{position:relative;background:#080808;aspect-ratio:16/9;width:100%;max-height:70vh}video,canvas{position:absolute;width:100%;height:100%;object-fit:contain;inset:0}canvas{pointer-events:none}#pos{font-variant-numeric:tabular-nums}#mark{color:#89d8ce;min-height:1.6em}small{color:#ccc}
</style><main><a href="index.html">전체 제작표</a><h1>강의에 들어갈 게임 장면</h1><p>강의와 장면을 고르면 녹화된 동작을 원래 속도로 볼 수 있어요. 선은 설명할 대상을 가리킵니다. 아래 글은 해당 대본이고, 이 페이지에는 강의 음성이 들어 있지 않아요.</p>
<label>강의 <select id="lesson"></select></label><label>장면 <select id="cut"></select></label><div id="mark"></div><div id="screen"><video id="v" playsinline preload="metadata"></video><canvas id="guides" width="1920" height="1080"></canvas></div><audio id="side" preload="none"></audio><p><button id="run">재생</button><button id="again">처음부터</button><label style="display:inline"><input id="aud" type="checkbox"> 게임 원음</label> · <span id="pos"></span></p><h2>이 장면의 설명</h2><p id="speech"></p><small id="err"></small></main>
<script>
const rows=DATA,$=s=>document.getElementById(s),v=$('v'),snd=$('side'),ctx=$('guides').getContext('2d'),lesson=$('lesson'),cut=$('cut'),sel=$('aud');let r,serial=0,cb=0;
for(const ep of [...new Set(rows.map(x=>x.ep))]){const e=rows.find(x=>x.ep===ep);lesson.add(new Option(ep+' · '+e.title,ep))}
function box(k){if(k.points)return k.points;const [x,y,w,h]=k.bbox;return Array.from({length:49},(_,i)=>[x+w*(1+Math.cos(i*Math.PI/24))/2,y+h*(1+Math.sin(i*Math.PI/24))/2]);}
function redraw(){ctx.clearRect(0,0,1920,1080);if(!r)return;const t=v.currentTime;let labels=[];for(const w of r.tracks){const ph=w.phases.find(p=>p.start<=t&&t<p.end);if(ph)labels.push(ph.label);if(t<w.start||t>=w.end)continue;const i=w.frames.findIndex(f=>f.time>t);if(i<1)continue;let a=w.frames[i-1],b=w.frames[i];if(a.visible===false||b.visible===false)continue;const u=(t-a.time)/(b.time-a.time),p=box(a),q=box(b);if(p.length!==q.length)continue;const ps=p.map((a,i)=>a.map((x,j)=>x+(q[i][j]-x)*u));const ds=ps.slice(1).map((a,i)=>Math.hypot(a[0]-ps[i][0],a[1]-ps[i][1]));let left=ds.reduce((a,b)=>a+b,0)*Math.min(1,(t-w.start+1/60)/.18);
ctx.beginPath();ctx.moveTo(...ps[0]);for(let j=0;j<ds.length;j++){if(ds[j]<.00001)continue;if(left>=ds[j]){ctx.lineTo(...ps[j+1]);left-=ds[j]}else{ctx.lineTo(...ps[j].map((x,k)=>x+(ps[j+1][k]-x)*left/ds[j]));break}}ctx.lineJoin='round';ctx.lineCap='round';ctx.lineWidth=9;ctx.strokeStyle='#101010';ctx.stroke();ctx.lineWidth=5;ctx.strokeStyle='#73c7c2';ctx.stroke();if(!w.phases.length)labels.push(w.label)}$('mark').textContent=labels.join(' · ')||' ';$('pos').textContent=Math.max(0,Math.min(r.end-r.start,t-r.start)).toFixed(1)+' / '+(r.end-r.start).toFixed(1)+'초';}
function inset(){const z=r?.inset,t=v.currentTime;if(!z||v.readyState<2||t<z.start||t>z.end)return;const k=z.centers,i=k.findIndex(v=>v[0]>=t),a=k[Math.max(0,i-1)],b=k[i<0?k.length-1:i],u=a[0]===b[0]?0:(t-a[0])/(b[0]-a[0]),cx=a[1]+u*(b[1]-a[1]),cy=a[2]+u*(b[2]-a[2]),[cw,ch]=z.cropSize,[dw,dh]=z.displaySize,x=(z.displayAt[0]-192)/.8,y=(z.displayAt[1]-48)/.8;ctx.fillStyle='#73c7c2';ctx.fillRect(x,y,(dw+8)/.8,(dh+8)/.8);ctx.drawImage(v,cx-cw/2,cy-ch/2,cw,ch,x+5,y+5,dw/.8,dh/.8);}
const baseDraw=redraw;redraw=()=>{baseDraw();inset()};
function sync(){if(!r||!r.sound||!sel.checked)return;if(Number.isFinite(snd.duration)&&Math.abs(snd.currentTime-(v.currentTime+r.offset))>.18)snd.currentTime=v.currentTime+r.offset;}
function pump(){cancelAnimationFrame(cb);redraw();if(v.currentTime>=r.end){v.pause();return}if(!v.paused)cb=requestAnimationFrame(pump);}
async function play(){
  if(!r)return;
  const selection=serial;
  try{
    if(v.currentTime<r.start-.1||v.currentTime>=r.end-.02)v.currentTime=r.start;
    const videoPlaying=v.play();
    if(r.sound&&sel.checked){
      snd.currentTime=v.currentTime+r.offset;
      await Promise.all([videoPlaying,snd.play()]);
      if(selection===serial)sync();
    }else await videoPlaying;
  }catch(error){
    if(selection!==serial||error.name==='AbortError')return;
    v.pause();snd.pause();
    $('err').textContent='영상을 열 수 없어요. 검수 링크를 이 컴퓨터의 Chrome에서 열어 주세요.';
  }
}
function choose(){serial++;const token=serial;r=rows[Number(cut.value)];v.pause();snd.pause();cancelAnimationFrame(cb);v.muted=!!r.sound||!sel.checked;snd.muted=!sel.checked;v.src=r.file;
if(r.sound){snd.src=r.sound;snd.preload='metadata';snd.load()}else {snd.removeAttribute('src');snd.load()}v.onloadedmetadata=()=>{if(token!==serial)return;v.currentTime=r.start;redraw()};v.preload='metadata';v.load();$('speech').textContent=r.speech;$('err').textContent='';redraw();history.replaceState(null,'','#'+r.ep+'-'+r.sid);}
function setcuts(id){cut.replaceChildren();rows.forEach((r,i)=>{if(r.ep===lesson.value)cut.add(new Option((cut.length+1)+' · '+r.game+' · '+(r.end-r.start).toFixed(0)+'초',i))});if(id!=null&&rows[id]?.ep===lesson.value)cut.value=id;choose()}
v.addEventListener('play',()=>{$('run').textContent='일시 정지';pump()});v.addEventListener('pause',()=>{snd.pause();$('run').textContent='재생';redraw()});v.addEventListener('seeked',()=>{sync();redraw()});v.addEventListener('timeupdate',()=>{sync();if(r&&v.currentTime>=r.end)v.pause();redraw()});snd.addEventListener('loadedmetadata',sync);v.addEventListener('error',()=>{$('err').textContent='이 브라우저에서 녹화 파일을 열 수 없어요.'});$('run').onclick=()=>v.paused?play():v.pause();$('again').onclick=()=>{v.currentTime=r.start;play()};sel.onchange=()=>{v.muted=!!r.sound||!sel.checked;snd.muted=!sel.checked;if(!sel.checked)snd.pause();else if(!v.paused&&r.sound){sync();snd.play().catch(()=>{})}};lesson.onchange=()=>setcuts(null);cut.onchange=choose;const id=rows.findIndex(r=>r.ep+'-'+r.sid===location.hash.slice(1));if(id>=0)lesson.value=rows[id].ep;setcuts(id>=0?id:null);
</script></html>'''
OUT.mkdir(exist_ok=True,parents=True);(OUT/'gameplay.html').write_text(doc.replace('DATA',json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),1),encoding='utf-8')
print(len(rows),'native-motion windows across',len(set(r['ep'] for r in rows)),'lectures; no approximated lecture audio')
