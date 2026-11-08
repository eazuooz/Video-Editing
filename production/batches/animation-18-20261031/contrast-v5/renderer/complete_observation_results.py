"""Same-length selected plate overrides: show the actual demonstrated result."""
from sources import *
import render_rows as rr
from copy import deepcopy

def prepare():
    plan=read(H/'replacement-plan.json');rows=[]
    for ep in plan['episodes']:
        for r in ep['rows']:
            if r['mode']!='analysis' or(ep['id'],r['key'])not in {('A08','overview'),('A06','control')}:continue
            q=deepcopy(r);q['episode']=ep['id'];q['replacesBaseRow']=r['id'];q['showLegend']=False
            dest=B/'local/contrast-v5/explanation-plates'/ep['id']/'complete-result'/(r['id']+'.mp4')
            q['output']=str(dest.relative_to(R)).replace('\\','/');q['resultFrame']=171 if ep['id']=='A08' else 72;rows.append(q)
    return {'schemaVersion':1,'status':'planned','scope':'Same-length result-visibility overrides only; no changed narration or baseline clock.','fps':60,'rows':rows,'A03Preserved':True,
        'reasons':{'A08':'The cumulative overview reaches the completed legs/feet at171F; a generic88F observation would show only partial edits. Chapters02/08 hold the completed actual pose. Chapter07 compares all four actual stages.','A06':'Input recovery differs after54F and until72F; the comparison must reach that interval before showing the stage summary.'}}

def execute():
    ctrl=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ctrl['renderAuthorized']
    spec=prepare();original=rr.state
    def state(ep,row,i):
        f=i+row.get('cutOffset',0);total=row['originalCutFrames']
        if ep=='A08':
            chapter=str(row.get('chapter')).zfill(2)
            if chapter in ('02','08'):return 171,'compare'
            if chapter=='07':return 171,'stages'
            if f>=round(total*.7):return 171,'stages'
            return round(171*np.clip(f/max(1,round(total*.7)-1),0,1)),'compare'
        lead=row.get('nativeLeadFrames',0)
        if f<lead:return f,'native'
        end=round(total*.7)if row.get('phaseModeAtTail')else total
        if row.get('phaseModeAtTail')and f>=end:return 72,'stages'
        u=np.clip((f-lead)/max(1,end-lead-1),0,1)
        return round(27+45*min(1,u/.78)),'compare'
    rr.state=state
    code=hashlib.sha256(Path(__file__).read_bytes()+b''.join((H/n).read_bytes()for n in ('compose.py','sources.py','config.py','render_rows.py'))).hexdigest()
    for r in spec['rows']:
        ep=r['episode'];assert ep in ctrl['episodes'];inputs=input_receipt(ep,r['key'])
        signature=hashlib.sha256(json.dumps({'code':code,'row':r,'source':inputs},sort_keys=True).encode()).hexdigest()
        print(rr.render(ep,r,signature),r['id'],flush=True);r['sha256']=sha(R/r['output'])
    spec.update(status='rendered-current-silent-overrides',codeSHA256=code,humanReviewed=False)
    (H/'observation-corrections.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');a=ap.parse_args()
    if a.render:execute()
    else:(H/'observation-corrections.json').write_text(json.dumps(prepare(),ensure_ascii=False,indent=2)+'\n','utf8')
