"""Read-only hash and metadata validation before explicit PowerShell deletion."""
from pathlib import Path
import json,hashlib,concurrent.futures,datetime,time
B=Path(__file__).resolve().parent;R=Path('D:/Github/VideoEditing').resolve()
raw=(B/'plan.json').read_bytes();plan=json.loads(raw)
groups={}
for f in plan['files']:groups.setdefault(f['inode'],[]).append(f)
def check(f):
    p=Path(f['absolute'])
    assert p.resolve(strict=True).is_relative_to(R) and p.drive.upper()=='D:'
    for part in [p,*p.parents]:
        if part==R.parent:break
        assert not(part.lstat().st_file_attributes&0x400),str(part)
    s=p.stat();assert s.st_size==f['bytes'] and s.st_mtime_ns==f['mtimeNs'] and s.st_ino==f['inode'],f['path']
    return p
def digest(items):
    f=items[0];p=check(f);h=hashlib.sha256()
    with p.open('rb') as stream:
        while data:=stream.read(8*1024*1024):h.update(data)
    for f in items:check(f)
    return [{'path':f['path'],'sha256':h.hexdigest(),'bytes':f['bytes'],'inode':f['inode']} for f in items]
done=0;total=0;last=time.monotonic();records=[]
with (B/'hashes.jsonl').open('w',encoding='utf8') as log,concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for rows in pool.map(digest,groups.values()):
        for row in rows:log.write(json.dumps(row,ensure_ascii=False)+'\n')
        records.extend(rows);done+=len(rows);total+=sum(x['bytes'] for x in rows)
        if time.monotonic()-last>20:
            log.flush();print(json.dumps({'hashedFiles':done,'GB':round(total/1e9,2)},ensure_ascii=False),flush=True);last=time.monotonic()
receipt={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planSha256':hashlib.sha256(raw).hexdigest(),'files':len(records),'bytes':total}
(B/'hash-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt),flush=True)
