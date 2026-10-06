"""Local candidate playback UI. Events are observations, never approval gates."""
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
import json, mimetypes, re, os, argparse, hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=9240);parser.add_argument('--source',default='word-action-source-candidate-v2.json');args=parser.parse_args()
source_path=BASE/args.source
caption_path=BASE/'word-caption-candidate-v3/captions.json'
source=read(source_path);caption=read(caption_path)
cuts=[dict(c,audioPath=p['audioPath'],voiceStartFrame=p['voiceStartFrame'],pieceStartFrame=p['startFrame'],pieceEndFrame=p['endFrame']) for p in source['pieces'] for c in p['selectedSourceCuts']]
allowed={c['sourcePath'] for c in cuts}|{c['audioPath'] for c in cuts}
data=json.dumps(dict(cuts=cuts,ko=caption['ko'],paragraphs=caption['paragraphs']),ensure_ascii=False).replace('</','<\\/')
page='''<!doctype html><meta charset="utf-8"><title>익숙한 조작 — 입력 재생 검수</title>
<style>body{font:16px Arial;background:#f4f4f1;color:#161b18;margin:12px}button,select,input{font:16px Arial;padding:7px;margin:3px}canvas{width:100%;display:block}#stage{max-width:1200px}#gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;max-width:1200px}.card{background:white;border:1px solid #888}.card p{margin:4px}#status{white-space:pre-wrap}video,audio{display:none}</style>
<h2>현재 후보 · 음성/본문 보존 · 최종 승인 전</h2>
<label>구간 <select id="cut"></select></label>
<label>구도 <select id="mode"><option value="candidate">후보 크롭</option><option value="native">원래 전체 화면</option></select></label>
<button id="play">검수 재생</button><button id="pause">일시 정지</button>
<button id="prev">이전 구간</button><button id="next">다음 구간</button>
<label>소스 프레임 <input id="frame" type="number"></label><button id="seek">프레임 보기</button>
<div id="status" role="status">준비</div><div id="claim"></div>
<div id="stage"><canvas id="main" width="1920" height="1080"></canvas></div>
<button id="gprev">이전 관찰판</button><button id="gnext">다음 관찰판</button><span id="ginfo"></span><div id="gallery"></div>
<video id="v" muted playsinline preload="auto"></video><audio id="a" preload="auto"></audio>
<script>const DATA=__DATA__;let idx=0,frames=[],pageNo=0,running=false,last=-100,loaded='',mode='candidate',events=[];
const $=x=>document.getElementById(x),v=$('v'),a=$('a'),main=$('main'),ctx=main.getContext('2d');
DATA.cuts.forEach((c,i)=>{let o=document.createElement('option');o.value=i;o.textContent=`${i+1}/${DATA.cuts.length} ${c.id} ${c.sourceVideoId}@${c.inFrameInclusive}–${c.outFrameExclusive}`;$('cut').append(o)});
const rate=c=>{let [n,d]=c.sourceFrameRate.split('/').map(Number);return n/d};
const event=(kind,extra={})=>{const e={at:new Date().toISOString(),kind,cutId:DATA.cuts[idx].id,mode,...extra};events.push(e);fetch('/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(e)})};
const seekTo=t=>new Promise(resolve=>{if(Math.abs(v.currentTime-t)<0.001&&v.readyState>=2){resolve();return}v.addEventListener('seeked',resolve,{once:true});v.currentTime=t});
function paint(canvas,t){const c=DATA.cuts[idx],g=canvas.getContext('2d'),crop=mode==='native'?[0,0,1920,1080]:c.sourceCrop;g.drawImage(v,...crop,0,0,1920,1080);const out=c.startFrame/60+(t-c.inSeconds);const cue=DATA.ko.find(q=>q.startSeconds<=out&&out<q.endSeconds);if(cue){g.font='48px Malgun Gothic';const w=g.measureText(cue.ko).width+44,x=960-w/2,y=928;g.fillStyle='#073c32';g.fillRect(x+14,y+14,w,84);g.fillStyle='#fff';g.fillRect(x,y,w,84);g.strokeStyle='#161b18';g.lineWidth=3;g.strokeRect(x,y,w,84);g.fillStyle='#080b09';g.textAlign='center';g.textBaseline='top';g.fillText(cue.ko,960,y+11)}return {cue:cue?.index,text:cue?.ko,outFrame:Math.round(out*60)}}
function gallery(){const start=pageNo*6,list=frames.slice(start,start+6);$('gallery').replaceChildren();for(const f of list){const box=document.createElement('div');box.className='card';const p=document.createElement('p');p.textContent=`${f.order} src${f.sourceFrame} out${f.outFrame} cue${f.cue??'없음'} · ${f.text??''}`;box.append(p,f.canvas);$('gallery').append(box)}$('ginfo').textContent=`${pageNo+1}/${Math.max(1,Math.ceil(frames.length/6))} · ${frames.length}개 순차 관찰 화면`;}
function observe(t,force=false){paint(main,t);if(force||t-last>=1/6){const can=document.createElement('canvas');can.width=1920;can.height=1080;const info=paint(can,t);frames.push({canvas:can,order:frames.length+1,sourceFrame:Math.round(t*rate(DATA.cuts[idx])),...info});last=t;}const c=DATA.cuts[idx];$('status').textContent=`${c.id} | ${mode} | 소스 ${t.toFixed(4)}초 / frame${Math.round(t*rate(c))} | ${running?'재생 중':'정지'} | 관찰 ${frames.length}개`;}
async function load(){running=false;v.pause();a.pause();const c=DATA.cuts[idx];$('cut').value=idx;$('frame').value=c.inFrameInclusive;$('claim').textContent=c.visibleActionConnection;frames=[];pageNo=0;last=-100;if(loaded!==c.sourcePath){v.src='/media/'+encodeURIComponent(c.sourcePath);loaded=c.sourcePath;await new Promise(resolve=>v.addEventListener('loadedmetadata',resolve,{once:true}));}a.src='/media/'+encodeURIComponent(c.audioPath);await seekTo(c.inSeconds);observe(v.currentTime,true);gallery();event('loaded',{inFrame:c.inFrameInclusive,outFrame:c.outFrameExclusive});}
$('cut').onchange=async()=>{idx=+$('cut').value;await load()};$('mode').onchange=async()=>{mode=$('mode').value;await load()};
$('play').onclick=async()=>{const c=DATA.cuts[idx];frames=[];last=-100;pageNo=0;await seekTo(c.inSeconds);a.currentTime=Math.max(0,(c.startFrame-c.voiceStartFrame)/60);running=true;observe(v.currentTime,true);event('play-start');await v.play();if(c.startFrame>=c.voiceStartFrame)await a.play();};
$('pause').onclick=()=>{running=false;v.pause();a.pause();observe(v.currentTime,true);gallery();event('pause',{sourceFrame:Math.round(v.currentTime*rate(DATA.cuts[idx]))})};
$('next').onclick=async()=>{idx=Math.min(DATA.cuts.length-1,idx+1);await load()};$('prev').onclick=async()=>{idx=Math.max(0,idx-1);await load()};
$('seek').onclick=async()=>{running=false;v.pause();a.pause();await seekTo(+$('frame').value/rate(DATA.cuts[idx]));observe(v.currentTime,true);pageNo=Math.floor((frames.length-1)/6);gallery();event('seek',{sourceFrame:+$('frame').value})};
$('gnext').onclick=()=>{pageNo=Math.min(Math.ceil(frames.length/6)-1,pageNo+1);gallery()};$('gprev').onclick=()=>{pageNo=Math.max(0,pageNo-1);gallery()};
function tick(now,meta){if(running){const c=DATA.cuts[idx];if(meta.mediaTime>=c.outSeconds-1/rate(c)){running=false;v.pause();a.pause();const lastIn=(c.outFrameExclusive-1)/rate(c);seekTo(lastIn).then(()=>{observe(v.currentTime,true);gallery();event('play-end',{sourceFrame:Math.round(v.currentTime*rate(c)),samples:frames.length,completeSourceIntervalTraversed:true});});}else{observe(meta.mediaTime);if(a.paused&&c.startFrame/60+(meta.mediaTime-c.inSeconds)>=c.voiceStartFrame/60){a.currentTime=c.startFrame/60+(meta.mediaTime-c.inSeconds)-c.voiceStartFrame/60;a.play();}}}v.requestVideoFrameCallback(tick)}v.requestVideoFrameCallback(tick);load();</script>'''.replace('__DATA__',data)
events_path=PROOF/'browser-word-action-playback-events-v1.jsonl'
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        if self.path!='/event':self.send_error(404);return
        n=int(self.headers.get('Content-Length','0'))
        if n>8192:self.send_error(413);return
        e=json.loads(self.rfile.read(n));e['serverObservedAt']=datetime.now(timezone.utc).isoformat()
        with events_path.open('a',encoding='utf-8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
        self.send_response(204);self.end_headers()
    def do_GET(self):
        from urllib.parse import unquote
        if self.path=='/':
            b=page.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b);return
        key=unquote(self.path.removeprefix('/media/'))
        if not self.path.startswith('/media/') or key not in allowed:self.send_error(404);return
        p=ROOT/key;size=p.stat().st_size;start,end=0,size-1;range_=self.headers.get('Range','')
        if range_:
            m=re.fullmatch(r'bytes=(\d+)-(\d*)',range_)
            if not m:self.send_error(416);return
            start=int(m[1]);end=min(int(m[2]) if m[2] else end,end)
        self.send_response(206 if range_ else 200);self.send_header('Content-Type',mimetypes.guess_type(p.name)[0] or 'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',end-start+1)
        if range_:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with p.open('rb') as f:
                f.seek(start);remaining=end-start+1
                while remaining:
                    b=f.read(min(remaining,1024*256))
                    if not b:break
                    self.wfile.write(b);remaining-=len(b)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
state=dict(pid=os.getpid(),commandLine=[os.sys.executable,*os.sys.argv],startedAt=datetime.now(timezone.utc).isoformat(),port=args.port,bind='127.0.0.1',sourceCandidateSha256=sha(source_path),captionCandidateSha256=sha(caption_path),status='serving-candidate-ui-no-render-no-approval',events=str(events_path.relative_to(ROOT)),gpuJobs=0)
(PROOF/'browser-word-action-review-server-v1.json').write_text(json.dumps(state,indent=2)+'\n','utf-8')
print(json.dumps(state),flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
