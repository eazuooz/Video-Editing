import json,concurrent.futures
from pathlib import Path
from capture import capture
P=Path(__file__).resolve().parent
inv={r['id']:r for r in json.loads((P/'inventory.json').read_text(encoding='utf8'))['rows']}
ids=['S41','S52','S69','S71','S72','S73','S74'];out={}
def one(i):
 p=P/'evidence/legacy-audio'/f'{i}.json';end=json.loads(p.read_text(encoding='utf8'))['seconds'] if p.exists() else 5.5
 return capture(i,inv[i]['videoId'],round(end*.43,2))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 fs={i:ex.submit(one,i) for i in ids}
 for i,f in fs.items():
  try:out[i]=f.result();print(i,'captured',flush=True)
  except Exception as e:out[i]={'status':'failed','reason':str(e)};print(i,'failed',flush=True)
  (P/'short-recovery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
