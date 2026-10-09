"""A local-only normal-speed raw-source review page; does not edit media."""
from pathlib import Path
import hashlib, json
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
proof = ROOT / 'production/batches/sakurai-planning-game-design/proof-presenting-game-scores'
bank_path = proof / 'source-action-bank-v4.json'
bank = json.loads(bank_path.read_text('utf-8-sig'))
assert hashlib.sha256(bank_path.read_bytes()).hexdigest() == '6317296ed845e2aefb34f45872f880e8f63557a1a0c3ffc44fb87cac52923ab2'
sources = {s['name']: s for s in bank['sources']}
cuts = []
for c in bank['cuts']:
    den = int(c['timebase'].split('/')[1])
    cuts.append(dict(id=c['cutId'], source=c['source'], url=quote(Path(sources[c['source']]['rawPath']).name),
        start=c['startPts']/den, end=c['endPtsExclusive']/den, scene=c['scene'], action=c['visibleAction']))
page = '''<!doctype html><html lang="ko"><meta charset="utf-8"><title>점수 편 — 선정 구간 정상 속도 관찰</title>
<style>body{margin:16px;background:#111;color:#eee;font:16px sans-serif}h1{font-size:22px}nav{display:flex;gap:6px;flex-wrap:wrap}button{padding:8px;background:#e8cf83;color:#111;border:0;cursor:pointer}#player{display:block;margin:10px auto;width:min(100%,1280px);aspect-ratio:16/9;background:#000}#info{margin:8px 0;line-height:1.5}#status{font-family:monospace}small{color:#bbb}</style>
<h1>선정 구간 정상 속도 관찰 — 원본 화면</h1>
<small>재생 속도 1× / 음소거. 브라우저 종료 지점은 관찰용이며 실제 편집 인아웃은 봉인된 원본 PTS를 사용한다. 최종 자막·크롭 픽셀 승인 아님.</small>
<nav id="choices"></nav><div id="info">구간을 선택하세요.</div><div id="status">대기</div>
<video id="player" controls muted preload="metadata"></video>
<button id="resume">현재 구간 재생/일시정지</button>
<script>
const cuts=__CUTS__; const video=document.querySelector('#player'); const status=document.querySelector('#status');let current=null;let history=[];
for(const cut of cuts){const b=document.createElement('button');b.textContent=cut.id;b.onclick=()=>select(cut);document.querySelector('#choices').append(b)}
function select(cut){video.pause();current=cut;document.querySelector('#info').textContent=cut.id+' | '+cut.scene+' | '+cut.action;const src=new URL(cut.url,location.href).href;const seek=()=>{video.currentTime=cut.start;video.playbackRate=1;video.muted=true;video.play()};if(video.currentSrc!==src){video.src=src;video.addEventListener('loadedmetadata',seek,{once:true});video.load()}else seek();history.push({type:'selected',id:cut.id,at:new Date().toISOString(),start:cut.start,end:cut.end})}
video.addEventListener('timeupdate',()=>{if(!current)return;status.textContent=current.id+' | source '+video.currentTime.toFixed(6)+'s | '+video.playbackRate+'× | '+(video.paused?'paused':'playing');if(video.currentTime>=current.end&&!video.paused){video.pause();history.push({type:'observed-end',id:current.id,sourceTime:video.currentTime,at:new Date().toISOString()})}});
document.querySelector('#resume').onclick=()=>video.paused?video.play():video.pause();
window.reviewObservation={get current(){return current},get history(){return history}};
</script></html>'''.replace('__CUTS__', json.dumps(cuts, ensure_ascii=False))
target = ROOT / 'shared/assets/presenting-game-scores/raw/action-playback-review-v1.html'
assert not target.exists(), 'Preserve an existing playback-review page'
target.write_text(page, 'utf-8')
print(str(target)); print('Existing localhost9250 helper reused; source bytes/frames untouched, GPU0.')
