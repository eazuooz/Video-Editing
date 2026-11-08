"""Meaningful checks: joint projection data, actual changed controls, safe ownership."""
from sources import *
from compose import contract
from config import EPISODES
def validate():
    plan=read(H/'replacement-plan.json');out={'scope':'Data/geometry validation; sampled visual review is separate. No human listening or full-watch claim.','episodes':{},'A03Omitted':True}
    assert 'A03' not in EPISODES
    for ep in plan['episodes']:
        eid=ep['id'];checked=[]
        for key in ep['sourceInputs']:
            s=source(eid,key);d=s['definition'];errors=[]
            for side in (0,1):
                trace=d.get('motionEvidence')
                if not trace:continue
                for n in sorted(set([0,min(34,d['frames']-1),min(88,d['frames']-1),d['frames']-1])):
                    q=points(eid,key,n,side)
                    for name,value in trace[side][n].items():
                        if name in q:errors.append(float(np.max(abs(q[name]-value))))
            maximum=max(errors,default=0)
            assert maximum<.006,(eid,key,'FK mismatches recorded motion',maximum)
            checked.append({'key':key,'actualMotionPointsCompared':len(errors),'maxCoordinateErrorCm':maximum,'projection':'Saved orthographic camera, per-actor location/yaw, unchanged pixel scale across two variants'})
        out['episodes'][eid]={'studies':checked,'replacementRanges':len(ep['rows']),'protectedMapsAndRepairs':ep['preservedRelationRegions'],'capturePending':bool(ep['pending'])}
    d=source('A15','keys')['definition'];a,b=[v['tracks']for v in d['animations']];names=[k for k in a if k.endswith('_r')and k.startswith(('index','middle','ring','pinky','thumb'))]
    sample=lambda t,k,n:np.array(t[k]['q'][min(n,len(t[k]['q'])-1)])
    changed=lambda t:[n for n in range(1,d['frames'])if any(not np.allclose(sample(t,k,n),sample(t,k,n-1),atol=1e-7)for k in names)]
    assert all(np.array_equal(sample(a,k,n),sample(b,k,n))for k in names for n in (0,d['frames']-1))
    assert changed(a)==[65]and len(changed(b))>50
    out['A15SteppedVsContinuous']={'sameStartAndEndFingerRotations':True,'steppedChangedFrames':changed(a),'continuousChangedFrames':changed(b),
         'sameNonFingerTracks':all(a[k]==b[k]for k in a if k not in names),'sourcePoseDefinitionSHA256':sha(source('A15','keys')['metadata'])}
    assert out['A15SteppedVsContinuous']['sameNonFingerTracks']
    (H/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('Validated',len(out['episodes']),'episode adapters; A15 actual transition regression passed')
if __name__=='__main__':validate()
