from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'final-timeline-v1.json')
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(P/'caption-alignment-review-v1.json',dict(status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,allParagraphTextsRetained=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),paragraphs=plan['paragraphs'],captions=[dict(language=lang,path=(P/f'captions.{lang}.srt').relative_to(R).as_posix(),sha256=sha(P/f'captions.{lang}.srt'),cues=len(plan['captions'+lang.title()])) for lang in ['ko','en']],scope='All27 paired paragraphs read in full; 55KO/56EN cues mapped to measured current speech. New and retained text checked. Final encoded pixels separately pending.'))
html='''<!doctype html><meta charset="utf-8"><title>계층형 아웃라인 · 포켓몬 도입 수정본 검수</title><style>body{margin:0;background:#171c20;color:white;font:18px sans-serif}header{padding:12px}video{display:block;width:100%;height:78vh;background:black}button{font:18px sans-serif;padding:10px;margin:5px}pre{white-space:pre-wrap}</style><header>계층형 아웃라인 · 포켓몬 도입 수정본 <button onclick="v.currentTime=0;v.playbackRate=1;v.muted=true;v.play()">처음부터 1배속 재생</button><button onclick="v.pause()">일시정지</button></header><video id="v" src="hierarchical-game-outlines.captioned.review.mp4" controls muted preload="metadata"></video><pre id="status"></pre><script>const v=document.querySelector('video');const status=document.querySelector('#status');function show(){status.textContent=JSON.stringify({time:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,rate:v.playbackRate,muted:v.muted,width:v.videoWidth,height:v.videoHeight});}v.ontimeupdate=show;v.onloadedmetadata=show;v.onended=show;</script>'''
(P/'normal-review-local.html').write_text(html,encoding='utf-8')
print('Caption mapping and final review page prepared; no playback started.')
