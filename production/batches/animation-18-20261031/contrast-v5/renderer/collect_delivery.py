"""Current signed explanation outputs, no shared batch/worklist mutations."""
from sources import *

def collect():
    plan=read(H/'replacement-plan.json');code=hashlib.sha256(b''.join((H/n).read_bytes()for n in ('compose.py','sources.py','config.py','render_rows.py'))).hexdigest();episodes=[]
    for e in plan['episodes']:
        rows=[];pending=[]
        for r in e['rows']:
            dest=R/r['output'];f=dest.with_suffix('.json')
            expected=hashlib.sha256(json.dumps({'code':code,'row':r,'source':e['sourceInputs'][r['key']]},sort_keys=True).encode()).hexdigest()
            if not f.exists()or not dest.exists():pending.append(r['id']);continue
            d=read(f)
            if d['signature']!=expected:pending.append(r['id']);continue
            assert d['sha256']==sha(dest),(r['id'],'file changed')
            assert d['frames']==r['frames']and d['resolution']==[1920,1080]and d['fps']==60 and d['audio']is False
            rows.append({'id':r['id'],'key':r['key'],'path':r['output'],'sha256':d['sha256'],'frames':d['frames'],'relationFrameStart':r['relationFrameStart'],'relationFrameEnd':r['relationFrameEnd']})
        episodes.append({'id':e['id'],'slug':e['slug'],'status':'silent-explanation-plates-complete'if not pending else'in-progress','completed':len(rows),'total':len(e['rows']),'rows':rows,'pending':pending})
    report={'schemaVersion':1,'status':'complete'if all(not e['pending']for e in episodes)else'in-progress','scope':'Silent authored explanation replacements only, no full masters or human approval. Parent integrates new gameplay, speech, music and captions.','plan':'production/batches/animation-18-20261031/contrast-v5/renderer/replacement-plan.json','planSHA256':sha(H/'replacement-plan.json'),'currentCodeSHA256':code,'A03Preserved':True,'episodes':episodes}
    (H/'explanation-delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print([(e['id'],e['completed'],e['total'])for e in episodes],flush=True)
if __name__=='__main__':collect()
