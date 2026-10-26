"""Local review page for existing, hash-verified outputs; no platform operations."""
from pathlib import Path
import html, json, hashlib, os
B=Path(__file__).resolve().parent;R=B.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
batch=read(B/'batch.json');out=Path(batch['mediaRoot'])/'delivery';out.mkdir(exist_ok=True)
cards=[];manifest=[]
for item in batch['projects']:
    p=R/'projects'/item['slug'];record=p/'production/local-review.json'
    if not record.exists() or read(record).get('status') != 'local-final-review-pending':
        cards.append('<article><h2>'+html.escape(read(p/'project.json')['title'])+'</h2><p>제작 진행 중 · 완성본 미전달</p></article>');continue
    d=read(record);metadata=read(p/'publishing/metadata.json');entry=dict(slug=item['slug'],revision=d['revision'],metadata=metadata,review=d)
    for name,row in d['outputs'].items():assert sha(row['path'])==row['sha256']
    local_url=lambda path:Path(os.path.relpath(path,out)).as_posix()
    video=local_url(d['outputs']['captioned.mp4']['path'])
    cover=out/'covers'/(item['slug']+'.cover-v1.jpg')
    assert cover.is_file(), 'Missing current real-game cover: '+str(cover)
    entry['cover']={'path':str(cover),'sha256':sha(cover)}
    links=' · '.join('<a href="'+local_url(v['path'])+'">'+html.escape(k)+'</a>' for k,v in d['outputs'].items())
    links+=' · <a href="'+local_url(cover)+'">썸네일</a>'
    cards.append('<article><h2>'+html.escape(metadata['title'])+'</h2><video controls preload="metadata" playsinline poster="'+local_url(cover)+'" src="'+video+'"></video><p>'+links+'</p><p>'+str(round(d['seconds'],2))+'초 · 1080×1920 · 60fps · '+html.escape(d['revision'])+'</p><details><summary>설명과 파일 확인</summary><pre>'+html.escape(metadata['description'])+'</pre><code>SHA256 '+d['outputs']['captioned.mp4']['sha256']+'</code></details><p>자동 검사·표본 화면 검수 완료. 전체 청취·연속 재생·사용자 최종검수는 별도 확인이 필요합니다.</p></article>')
    manifest.append(entry)
document='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 · 새 쇼츠 4편 검수</title><style>body{background:#0b0b0b;color:#eee;font:17px system-ui;max-width:1100px;margin:32px auto;padding:0 20px}h1,h2{color:#ffd458}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:32px}article{border-top:1px solid #555;padding:20px 0}video{width:min(100%,375px);display:block;background:black}a{color:#5bcee1}pre{white-space:pre-wrap;font:14px system-ui}code{overflow-wrap:anywhere;font-size:12px}p{line-height:1.6}</style><h1>새 쇼츠 4편 · 로컬 검수</h1><p>각 영상의 전체 자막본과 자막 파일입니다. 업로드·공개 전 최종검수용입니다.</p><main>'+''.join(cards)+'</main></html>'
(out/'review-four.html').write_text(document,encoding='utf8')
(out/'review-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(page=str(out/'review-four.html'),completed=len(manifest),total=len(batch['projects'])),ensure_ascii=False))
