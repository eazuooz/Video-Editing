"""View rendered motion independently; this page grants no review approval."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
videos=O/'caption-safe-v2/videos/interpolation_additions/1080p60'
records=[{'id':p.stem,'url':p.relative_to(O).as_posix()+'?v='+hashlib.sha256(p.read_bytes()).hexdigest()[:16]} for p in sorted(videos.glob('*.mp4'))]
buttons=''.join(f'<button data-id="{r["id"]}" data-src="{r["url"]}">{r["id"]} 재생</button>' for r in records)
page='''<!doctype html><meta charset="utf-8"><title>보간 추가 설명 움직임 검수</title><style>body{background:#222;color:white;font:16px sans-serif}video{display:block;width:min(100%,1100px);max-height:70vh}button{margin:3px;padding:6px}</style><h1>추가 설명 실제 렌더 · 원래 배속</h1><p>무음 화면 검수용. 최종 음성·자막 결합 검수는 별도.</p>'''+buttons+'''<video controls id="v"></video><p id="status">장면을 선택하세요</p><script>const v=document.querySelector('video'),s=document.querySelector('#status');for(const b of document.querySelectorAll('button'))b.onclick=()=>{v.src=b.dataset.src;v.play();s.textContent=b.dataset.id};v.ontimeupdate=()=>s.textContent=s.textContent.split(' | ')[0]+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);v.onended=()=>s.textContent+=' | ended';</script>'''
(O/'explanation-moving-review.html').write_text(page,encoding='utf8')
print(json.dumps({'scenes':len(records),'actualViewingApproval':False}))
