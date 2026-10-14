from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[4]; P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
current=read(P.parent/'preflight/limited-color-world.json'); old=read(P/'duplicate-history-approved58-v6.json')
before={x['path']:x['sha256'] for x in old['inputFiles']}
changed=[x for x in current['inputFiles'] if before.get(x['path'])!=x['sha256']]
dest=ROOT/'shared/output/limited-color-world/research/duplicate-review-v7'; dest.mkdir(parents=True,exist_ok=True)
rows=[]
for i,x in enumerate(changed):
    target=dest/f'{i}.json'; assert not target.exists()
    data=(ROOT/x['path']).read_bytes(); assert hashlib.sha256(data).hexdigest()==x['sha256']
    target.write_bytes(data); rows.append(dict(**x,snapshotPath=target.relative_to(ROOT).as_posix()))
proof=P/'changed-input-snapshot-v7.json';assert not proof.exists()
proof.write_text(json.dumps(dict(inputsDigest=current['inputsDigest'],projects=len(current['existingProjects']),inputCount=len(current['inputFiles']),inputs=rows,gitExcluded=True),indent=2)+'\n','utf-8')
print(json.dumps(dict(path=proof.relative_to(ROOT).as_posix(),inputs=rows)))
