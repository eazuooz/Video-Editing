"""Make local comparison boards from already extracted samples; never approve by score."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
old=read(PROOF/'source-action-bank-v2.json')['clips']
new=[c for c in read(PROOF/'additional-action-bank-candidates-v2.json')['clips'] if c['exactEdgeApproval']]
assert len(old)==37 and len(new)==22
out=ROOT/'shared/output/familiar-game-rules/research/cross-source-v1'
assert not out.exists(),'Do not regenerate comparison images'
out.mkdir()
frames={}
for name in ['native-boards-v1.json','additional-native-boards-v1.json','additional-native-boards-v2.json','additional-native-boards-v3.json','additional-native-boards-v5.json']:
    m=read(PROOF/name);assert m['allDirectlyRead']
    for b in m['boards']:
        for t in b['tiles']:frames.setdefault(b['sourceId'],{})[t['sourceFrame']]=t
cache={}
def vec(t):
    p=t['path']
    if p not in cache:
        with Image.open(ROOT/p) as im:cache[p]=np.asarray(im.convert('RGB').resize((32,18)),dtype=np.float32).reshape(-1)
    return cache[p]
anger={'7kJo0miz08g','FVkDc6u_4GQ','XbW4873OPZo'}
pedro={'YIVtT7SJrMM','q-AsYZCdpts'}
def group(s):return 'anger' if s in anger else 'pedro' if s in pedro else 'gunbrella'
def samples(c):return [t for n,t in sorted(frames[c['sourceVideoId']].items()) if c['inFrameInclusive']<=n<c['outFrameExclusive']]
def pool(clips):return [(c,t) for c in clips for t in samples(c)]
oldpool=pool(old);newpool=pool(new)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
records=[]
for c in new:
    ss=samples(c);assert ss
    chosen=[ss[0],ss[len(ss)//2],ss[-1]]
    op=[(x,t) for x,t in oldpool if group(x['sourceVideoId'])==group(c['sourceVideoId'])]
    npool=[(x,t) for x,t in newpool if x['id']!=c['id'] and group(x['sourceVideoId'])==group(c['sourceVideoId'])]
    board=Image.new('RGB',(2880,1710),'white');draw=ImageDraw.Draw(board);rows=[]
    for row,t in enumerate(chosen):
        v=vec(t)
        def closest(p):
            x,tt=min(p,key=lambda xt:float(np.mean((vec(xt[1])-v)**2)))
            return x,tt,float(np.mean((vec(tt)-v)**2))
        ox,ot,score=closest(op);nx,nt,nscore=closest(npool)
        tiles=[]
        for col,(label,tt) in enumerate([(f'{c["id"]} candidate',t),(f'{ox["id"]} OLD closest score={score:.0f}',ot),(f'{nx["id"]} ADD closest score={nscore:.0f}',nt)]):
            x=col*960;y=row*570
            with Image.open(ROOT/tt['path']) as im:board.paste(im,(x,y+30))
            draw.text((x+5,y+3),f'{label} t={tt["seconds"]:.3f}',font=font,fill='black')
            tiles.append({**tt,'role':label})
        rows.append(dict(candidate=t,oldActionId=ox['id'],old=ot,oldScore=score,additionalActionId=nx['id'],additional=nt,additionalScore=nscore,tiles=tiles))
    p=out/f'{c["id"]}.jpg';board.save(p,quality=95)
    records.append(dict(actionId=c['id'],board=rel(p),sha256=sha(p),rows=rows,directlyRead=False))
manifest=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=datetime.now(timezone.utc).isoformat(),boards=records,boardCount=len(records),frameSlots=len(records)*9,method='Low-resolution RGB distance is a navigation aid only. Each selected frame and nearest same-game old/additional sample must be directly compared; no threshold approves or rejects a clip.',allDirectlyRead=False,crossSourceDuplicateSelectionApproved=False,imagesGitPolicy='local-only')
(PROOF/'cross-source-comparison-v1.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(boards=len(records),frameSlots=len(records)*9,approval=False)))
