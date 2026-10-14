"""Reuse the verified9250 server with same-inode links for silent overview review."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
state=json.loads((O/'current34-overview-render-execution-v4.json').read_text('utf-8-sig'))
assert state['actualExitObserved'] and state['actualOuterExitCode']==0 and state['workerDead']
page=RAW/'orientation-current34-overview-v4-review.html';assert not page.exists()
items=[]
for s in state['scenes']:
    src=ROOT/s['output'];dst=RAW/f'orientation-overview-v4-{s["id"]}.mp4'
    assert hashlib.sha256(src.read_bytes()).hexdigest()==s['outputSha256'] and not dst.exists()
    os.link(src,dst);assert os.path.samefile(src,dst)
    items.append(f'<h2>Scene{s["id"]}</h2><video id="v{s["id"]}" aria-label="Scene{s["id"]}" controls muted preload="metadata" src="{dst.name}"></video>')
page.write_text('<!doctype html><meta charset="utf-8"><title>Orientation overview V4 review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>Current overview/conclusion depth repairs</h1><p>Silent normal1× review. Current mixed narration already compared; final burned244-caption pixels remain pending.</p>'+''.join(items),'utf-8')
print(json.dumps(dict(page=page.relative_to(ROOT).as_posix(),sameInodeLinks=3,newServer=0)))
