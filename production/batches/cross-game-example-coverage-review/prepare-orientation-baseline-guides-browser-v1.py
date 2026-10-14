"""Reuse the existing9250 server for native guide review; no media copying."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
s=json.loads((O/'current34-baseline-guides-render-execution-v1.json').read_text('utf-8-sig'))
assert s['actualOuterExitCode']==0 and s['workerDead'] and len(s['results'])==8
page=RAW/'orientation-current34-baseline-guides-v1-review.html'
assert not page.exists()
items=[]
for x in s['results']:
    src=ROOT/x['output'];dst=RAW/f'orientation-baseline-guides-v1-{x["id"]}.mp4'
    assert hashlib.sha256(src.read_bytes()).hexdigest()==x['outputSha256'] and not dst.exists()
    os.link(src,dst);assert os.path.samefile(src,dst)
    items.append(f'<h2>Scene{x["id"]}</h2><video id="v{x["id"]}" aria-label="Scene{x["id"]}" controls muted preload="metadata" src="{dst.name}"></video>')
page.write_text('<!doctype html><meta charset="utf-8"><title>Orientation baseline guides V1 review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>Native gameplay guides</h1><p>Silent normal1x. Cyan torso screen observation, red screen displacement, gold fixed image-up. These do not measure game-world axes. Final burned captions remain pending.</p>'+''.join(items),'utf-8')
print(json.dumps(dict(page=page.relative_to(ROOT).as_posix(),sameInodeLinks=8,newServer=0)))
