"""Index the actual local master, not an approximate script reading time."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,html,json

P=Path(__file__).resolve().parents[1];R=P.parents[1];W=P/'production/local/render-v4'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
proof=read(W/'content-review.json');tech=read(W/'final-qa/report.json')
cap=Path(tech['files']['captioned']['path']);dest=cap.parent
assert sha(cap)==proof['masterSha256']==tech['files']['captioned']['sha256']
checks=[('037',0.,'조명식을 어디서 계산할까?','앞 문장에 이어 첫 단어 ‘지금까지는’이 자연스럽게 들리는지.'),
        ('042',13.84,'평균과 제곱의 순서','0과 1을 먼저 평균 내고 제곱하면 0.25, 각각 제곱하고 평균 내면 0.5.'),
        ('058',10.04,'거리로 조명의 세기 구하기','안쪽 2m, 바깥쪽 6m일 때 4m에서 남는 세기는 (6−4)/(6−2) = 0.5.')]
rows=[];records=[]
for sid,at,title,desc in checks:
 f=W/'final-mix-review/paragraphs'/f'{sid}-01.json';data=read(f);assert data['masterSha256']==proof['masterSha256']
 assert any(abs(w['timestamp'][0]-at)<.001 for w in data['chunks'])
 t=2+data['entry']['start']+at;start=max(0,t-1.3);label=f'{int(start)//60:02}:{int(start)%60:02}'
 records.append(dict(scene=sid,anchorSeconds=t,startWithContext=start,timingFile=str(f.relative_to(R)),sha256=sha(f)))
 rows.append(f'<li><a data-t="{start:.3f}" href="{cap.name}#t={start:.3f}">{label} · {html.escape(title)}</a><br><small>{html.escape(desc)}</small></li>')
for name in [P.name+'.clean.mp4',P.name+'.ko.srt',P.name+'.en.srt']:assert (dest/name).is_file()
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>빛과 셰이딩 | 얌얌코딩 게임수학</title><style>
body{max-width:1100px;margin:20px auto;padding:0 16px 32px;background:#101111;color:#fafaf8;font:18px/1.65 system-ui}a{color:#83d5ce}h1{color:#f4d077;margin:.35em 0}h2{font-size:1.18em}video{width:100%;background:#040404}small{color:#ddd}li{margin:.7em 0}nav a{display:inline-block;margin-right:1.1em}
</style><main><a href="../game-math-remaining-20261104/index.html">전체 13편 제작표</a><h1>M21 · 빛과 셰이딩</h1><p>32분 10초 · 1080p60 · 내부 검수 중</p><video id="v" controls playsinline preload="metadata" src="CAP"></video>
<nav><a href="CAP">자막 영상</a><a href="SLUG.clean.mp4">자막 없는 영상</a><a href="SLUG.ko.srt">한국어 자막</a><a href="SLUG.en.srt">영어 자막</a></nav><h2>다시 들어볼 구간</h2><p>재생 위치를 누르면 설명 직전부터 들을 수 있어요.</p><ul>ROWS</ul></main>
<script>const v=document.getElementById("v");document.querySelectorAll("[data-t]").forEach(a=>a.addEventListener("click",e=>{if(e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();const seek=()=>{v.currentTime=Number(a.dataset.t);v.play().catch(()=>{});};if(v.readyState)seek();else{v.addEventListener("loadedmetadata",seek,{once:true});v.load();}}));</script></html>'''
(dest/'index.html').write_text(page.replace('CAP',cap.name).replace('SLUG',P.name).replace('ROWS',''.join(rows)),encoding='utf8')
(W/'review-seek-evidence.json').write_text(json.dumps(dict(masterSha256=proof['masterSha256'],chapterOrigins=records,approved=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('3 master-relative checks;',dest/'index.html')
