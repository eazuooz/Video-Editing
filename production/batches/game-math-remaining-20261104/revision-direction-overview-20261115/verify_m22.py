"""Validate the final clock-normalized mux, including copied picture payloads."""
import sys,concurrent.futures
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import render
def main():
 receipt=HERE/'deliveries/M22.json';j=render.read(receipt)
 if j.get('finalClockMuxFullyDecoded'):return
 row=next(r for r in render.read(HERE/'plan.json')['episodes'] if r['id']=='M22');p=render.base.work(render.base.EPISODES['M22'])
 def check(kind):
  f=j['files'][kind]['path'];render.ff(['-threads','2','-v','error','-xerror','-i',f,'-map','0:v:0','-map','0:a:0','-f','null','-'],p,'final-clock-decode-'+kind)
  proof=next(q for q in j['qa'] if q['kind']==kind)
  for part in proof['unchangedSpans']:
   s=part['span'];expected=render.vcl_hash(row['sources'][kind]['path'],s['start']/60,s['end']-s['start']);assert render.vcl_hash(f,s['start']/60,s['end']-s['start'])==expected;part['unchangedVclHash']=expected
  return kind
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for kind in pool.map(check,['clean','captioned']):print('M22 final mux full decode and copied VCL pass',kind,flush=True)
 j['finalClockMuxFullyDecoded']=True;render.save(receipt,j)
if __name__=='__main__':main()
