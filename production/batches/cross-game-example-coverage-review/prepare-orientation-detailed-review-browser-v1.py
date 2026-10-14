"""Local silent review using the already verified 9250 helper, no new server."""
from pathlib import Path
import hashlib, html, json, os
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[('current34-detailed-header-repair-render-execution-v2.json',None),
         ('current34-detailed-explanation-render-execution-v1.json',{'12','06a','09a','13a','16a','21a'})]
page=RAW/'orientation-current34-detailed-review-v1.html'
record=O/'current34-detailed-browser-preparation-v1.json'
assert not page.exists() and not record.exists()
items=[]; refs=[]
for name,ids in sources:
    state=json.loads((O/name).read_text('utf-8-sig'))
    assert state['actualExitObserved'] and state['actualOuterExitCode']==0 and state['workerDead']
    for s in state['scenes']:
        if ids is not None and s['id'] not in ids: continue
        src=ROOT/s['output']; dst=RAW/f'orientation-detailed-review-v1-{s["id"]}.mp4'
        assert sha(src)==s['outputSha256'] and not dst.exists()
        os.link(src,dst); assert os.path.samefile(src,dst)
        sid=html.escape(s['id'])
        items.append(f'<section><h2>Scene{sid}</h2><video id="v{sid}" aria-label="Scene{sid}" controls muted preload="metadata" src="{dst.name}"></video></section>')
        refs.append(dict(id=s['id'],state=name,stateSha256=sha(O/name),source=s['output'],sha256=s['outputSha256'],link=dst.relative_to(ROOT).as_posix(),sameInode=True))
assert len(refs)==17 and len({r['id'] for r in refs})==17
page.write_text('<!doctype html><meta charset="utf-8"><title>Orientation detailed subjects review V1</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}section{margin-bottom:36px}</style><h1>Detailed subject explanation review</h1><p>Silent normal 1x review: 11 header V2 and six detailed revision V1. Final 244 burned captions and human listening remain pending.</p>'+''.join(items),'utf-8')
data=dict(page=page.relative_to(ROOT).as_posix(),pageSha256=sha(page),sources=refs,newServer=0,mediaCopies=0,gitImages=0,serverIdentityEvidence=dict(pid=27140,create='2026-10-09T10:34:26.837781+09:00',cimChunk='f76bdf',cimExitCode=0))
record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(page=data['page'],links=len(refs),newServer=0)))
