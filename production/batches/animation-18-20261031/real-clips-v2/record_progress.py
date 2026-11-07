"""Update only this finite revision's section in the existing batch checkpoint."""
from pathlib import Path
import json,hashlib,sys
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/real-clips-v2'
sys.path.insert(0,str(R/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load,patch
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    plan=json.loads((H/'revision-plan.json').read_text('utf-8'))
    registry=json.loads((L/'asset-registry.json').read_text('utf-8'))
    assert not registry['errors']
    plan['status']='source-motion-inspection-and-native-study-revision-in-progress'
    plan['sourceInventoryCounts']=registry['counts'];plan['sourceInventorySha256']=sha(L/'asset-registry.json')
    plan['visuallyRejectedCandidates']=[{'clip':'AS_Hack','reason':'Observed computer-hacking/crouched motion, not a weapon attack; excluded from attack studies.'}]
    for e in plan['episodes']:
        e['candidateClips'].pop('AS_Hack',None)
        if e['id']=='A03':
            e['selectedClip']='/Game/FreeAnimationLibrary/Animations/Update_2/Spear/AS_Spear_Attack_02'
            e['status']='native-four-study-prototype-rendered; contact-and-framing-QA-in-progress'
        if e['id'] in ('A09','A12','A15','A17','A18'):
            e['retentionReview']='Preserve exact volume, face, finger, FK/IK and axis controls where stock body mocap cannot demonstrate the narrated independent variable. Audit each before retaining; no unrelated motion substitutions.'
    (H/'revision-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
    cp=B/'checkpoint.json';raw=cp.read_bytes();section=load(raw)['fabPreparation20261107']
    section.update(status='user-imported-UE58-packs-inspected; source-motion-revision-in-progress',
        latestUserRequest=plan['userRequest'],nativeImportedRootsVerified=plan['newImportedRoots'],
        nativeInventory=plan['assetInventory'],nativeRegistryCounts=registry['counts'],nativeInspectionErrors=0,
        revisionPlan=str((H/'revision-plan.json').relative_to(R)).replace('\\','/'),
        newFinalVideoRenders=0,nativePrototypeStudies=4,
        nextAction='Review native A03 attack/cancel prototypes, replace only relevant explanation shots, then apply distinct concept-matched native motions sequentially across the exact A01-A18 review scope.')
    cp.write_bytes(patch(raw,['fabPreparation20261107'],section))
    print('Recorded genuine-source inspection and pending final deliveries')
if __name__=='__main__':main()
