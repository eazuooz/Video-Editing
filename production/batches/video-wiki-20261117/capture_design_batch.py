"""Capture bounded native frames; two CPU/network workers, no editor/GPU control."""
import concurrent.futures,json
from pathlib import Path
from capture import capture
P=Path(__file__).resolve().parent
src={r['id']:r for r in json.loads((P/'sources.json').read_text(encoding='utf8'))['rows']}
pub=json.loads((P/'publication.json').read_text(encoding='utf8'))
ids=['D04','D09','D11','D12','D13','D14','D15']+['D'+str(i) for i in range(17,31)]
progress={}
def one(ident):
 s=src[ident];c=s.get('cues',[]);end=max((x.get('seconds',0) for x in c),default=360)+4
 if ident=='D04':end=410
 t=round(min(end*.38,190),2)
 return capture(ident,s['videoId'],t)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for fut,ident in [(f,i) for i,f in [(i,ex.submit(one,i)) for i in ids]]:
  try:progress[ident]=fut.result();print(ident,'captured',flush=True)
  except Exception as e:progress[ident]={'status':'failed','reason':str(e)};print(ident,'failed',flush=True)
  (P/'design-capture-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
