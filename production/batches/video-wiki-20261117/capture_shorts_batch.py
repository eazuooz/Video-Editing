"""Retrieve one relevant middle frame per public short; no whole video restoration."""
import concurrent.futures,json
from pathlib import Path
from capture import capture
P=Path(__file__).resolve().parent
src={r['id']:r for r in json.loads((P/'sources.json').read_text(encoding='utf8'))['rows']}
inv={r['id']:r for r in json.loads((P/'inventory.json').read_text(encoding='utf8'))['rows']}
ids=[i for i in inv if i.startswith('S') and int(i[1:])>=8]
progress={}
def one(i):
 s=src.get(i,inv[i]);c=s.get('cues',[]);end=max((x.get('end',0) for x in c),default=45)
 return capture(i,s['videoId'],round(min(max(end*.48,8),25),2))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 fs={i:ex.submit(one,i) for i in ids}
 for i,f in fs.items():
  try:progress[i]=f.result();print(i,'captured',flush=True)
  except Exception as e:progress[i]={'status':'failed','reason':str(e)};print(i,'failed',flush=True)
  (P/'shorts-capture-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
