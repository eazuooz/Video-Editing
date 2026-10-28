"""Read-only D-drive media inventory. Never follow junctions/symlinks."""
from pathlib import Path
import os,json,collections,shutil,datetime
R=Path('D:/Github/VideoEditing'); B=Path(__file__).resolve().parent
EXT={'.mp4','.mov','.mkv','.webm','.m4v','.avi','.wav'}
SKIP={'.git','node_modules','Library','Temp','obj','Obj','Binaries','Intermediate','DerivedDataCache','.venv','venv','__pycache__'}
files=[]; links=[]; errors=[]
def walk(folder):
    try:
        with os.scandir(folder) as it:
            for e in it:
                try:
                    s=e.stat(follow_symlinks=False)
                    if getattr(s,'st_file_attributes',0)&0x400:
                        links.append({'path':e.path,'resolved':str(Path(e.path).resolve())}); continue
                    if e.is_dir(follow_symlinks=False):
                        if e.name not in SKIP: walk(e.path)
                    elif Path(e.name).suffix.lower() in EXT:
                        p=Path(e.path); actual=p.resolve(strict=True)
                        if not actual.is_relative_to(R.resolve()): raise ValueError('outside root')
                        files.append({'path':p.relative_to(R).as_posix(),'absolute':str(actual),'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'links':s.st_nlink,'ext':p.suffix.lower()})
                except Exception as ex: errors.append({'path':e.path,'error':str(ex)})
    except Exception as ex: errors.append({'path':str(folder),'error':str(ex)})
walk(R)
d={'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(R),'driveBefore':dict(zip(['total','used','free'],shutil.disk_usage('D:/'))),'files':files,'skippedLinks':links,'errors':errors}
(B/'inventory.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
groups=collections.defaultdict(lambda:[0,0])
for f in files:
    p=f['path'].split('/'); group='/'.join(p[:2] if p[0]!='shared' else p[:3]); groups[group][0]+=f['bytes'];groups[group][1]+=1
print(json.dumps({'fileCount':len(files),'GB':round(sum(f['bytes'] for f in files)/1e9,2),'skippedLinks':len(links),'errors':len(errors),'largestGroups':[{'group':g,'GB':round(v[0]/1e9,2),'count':v[1]} for g,v in sorted(groups.items(),key=lambda x:-x[1][0])[:45]]},ensure_ascii=False,indent=2))
