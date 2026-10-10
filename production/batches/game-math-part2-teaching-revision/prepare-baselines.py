"""Read-only production snapshots; never overwrite baseline media or records."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
q=read(BATCH/'queue.json');rows=[]
for item in q['items']:
 slug=item['slug'];base=ROOT/'projects'/slug
 paths=['project.json','script/narration.ko.json','script/narration.en.json','production/timeline.json','sources/gameplay-cuts.json','publishing/youtube-upload.json']
 lesson=ROOT/'production/batches/game-math-part2-full-series/lessons'/f'{slug}.json'
 pairs=[(base/p,Path(p)) for p in paths]+[(lesson,Path('lesson.json'))]
 evidence=[]
 for src,rel in pairs:
  raw=src.read_bytes();dst=BATCH/'baselines'/slug/rel
  if dst.exists():assert dst.read_bytes()==raw,f'Baseline changed since snapshot: {src}'
  else:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
  evidence.append({'source':src.relative_to(ROOT).as_posix(),'snapshot':dst.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()})
 data=read(lesson);timeline=read(base/'production/timeline.json');manifest=read(base/'project.json')
 rows.append({'slug':slug,'baselineVideoId':item['baseline']['videoId'],'originalScenes':len(data['scenes']),'koLines':sum(len(s['ko']) for s in data['scenes']),'enLines':sum(len(s['en']) for s in data['scenes']),'seconds':timeline['seconds'],'contract':data.get('contract'),'mediaReferences':{k:v for k,v in manifest['paths'].items() if k in ['videoClean','videoBurnedCaptions','narration','audioMix']},'snapshots':evidence})
write(BATCH/'baseline-inventory.json',{'originalFilesChanged':False,'mediaCopiedOrOverwritten':False,'items':rows})
print(json.dumps({'snapshotted':len(rows),'originalScenes':sum(r['originalScenes'] for r in rows),'originalKoLines':sum(r['koLines'] for r in rows),'baselineMediaPreserved':True}))
