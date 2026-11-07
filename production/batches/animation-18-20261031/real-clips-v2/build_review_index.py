"""Render the exact completed review table with local fallback links."""
from pathlib import Path
import json,html,os
H=Path(__file__).resolve().parent;R=H.parents[3];manifest=json.loads((H/'review-manifest.json').read_text('utf-8'));out=R/'output/animation-series-review/real-clips-v2';out.mkdir(parents=True,exist_ok=True)
esc=html.escape
def relative(path):return os.path.relpath(R/path,out).replace('\\','/')
def clock(t):
    seconds=round(t)
    return f'{seconds//60}:{seconds%60:02}'
rows=[]
for r in manifest['records']:
    movie=next(f['path']for f in r['files']if f['kind']=='captioned.mp4')
    rows.append('<tr id="'+r['id']+'"><td>'+r['id']+'</td><td><a class="play" href="'+relative(movie)+'">'+esc(r['title'])+'</a><small>'+esc(r['reviewFocus'])+'</small><small>'+esc(r['description'])+'</small></td><td>'+clock(r['durationSeconds'])+'</td><td>'+('수정본' if r['revised'] else '유지')+'<br><a class="files" href="'+relative(r['directory']+'/index.html')+'">파일 모음</a></td></tr>')
css='body{max-width:1120px;margin:30px auto;padding:16px;background:#111914;color:#eee;font:17px/1.6 sans-serif}h1{color:#f2d787}a{color:#a4d7c2}small{display:block;color:#b2bdb6}table{width:100%;border-collapse:collapse}td,th{padding:12px 8px;text-align:left;border-bottom:1px solid #405146}video{width:100%;max-height:70vh;background:black}tr[aria-current=true]{background:#233b2e}button{padding:10px;background:#294838;color:white;border:1px solid #7cac93;cursor:pointer}@media(max-width:540px){body{font-size:14px;margin:6px}td,th{padding:7px 4px}}'
script='''const rows=[...document.querySelectorAll('tbody tr')],v=document.querySelector('video'),heading=document.getElementById('now');let current=0;
if(location.protocol.startsWith('http'))for(const r of rows){r.querySelector('.play').href='/'+r.id+'/captioned.mp4';r.querySelector('.files').href='/'+r.id+'/';}
function select(i,play=false){if(i<0||i>=rows.length)return;rows[current].removeAttribute('aria-current');current=i;const row=rows[i];row.setAttribute('aria-current','true');v.src=row.querySelector('.play').href;heading.textContent=row.id+' · '+row.querySelector('.play').textContent;if(play)v.play().catch(()=>{});}
rows.forEach((r,i)=>r.querySelector('.play').onclick=e=>{e.preventDefault();select(i,true);});v.onended=()=>{if(document.querySelector('#auto').checked)select(current+1,true);};document.querySelector('#next').onclick=()=>select(current+1,true);select(0);'''
body='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>애니메이션 통합 검수 · 실제 클립 수정본</title><style>'+css+'</style><h1>애니메이션 18편 통합 검수</h1><p>14편 시연 수정 · 4편 전용 시연 유지 · 전체 '+clock(manifest['totalSeconds'])+' · 1080p 60fps</p><p>게임 영상·기존 음성·자막·배경음악 보존. 아래 표에서 편을 선택해 확인할 수 있습니다.</p><h2 id="now"></h2><video controls playsinline preload="metadata"></video><p><label><input id="auto" type="checkbox" checked> 다음 편 이어 보기</label> <button id="next">다음 편</button></p><table><thead><tr><th>편</th><th>주제와 변경 내용</th><th>길이</th><th>버전</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><p>기술 검사와 변경 화면 표본 검토 완료 · 사용자 최종 검수 대기</p><script>'+script+'</script></html>'
(out/'index.html').write_text(body,'utf-8');print(out/'index.html')
