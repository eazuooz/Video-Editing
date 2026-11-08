"""Re-sign only byte-identical outputs unaffected by the legacy-camera fallback.

The old signature is reconstructed and must match before any receipt changes.
All selected source definitions must have explicit cameraWidth, so the changed
default is never evaluated. This does not authorize reuse for A04/A11 defaults.
"""
from sources import *
BLOCK="""    # The old series templates inherit the A01 walk camera (ortho width500).
    # Its value is explicit in unreal-kit-v2/build_stages.py, not inferred from
    # pixels. Newer captures carry cameraWidth in their own saved definition.
    scale=1920/d.get('cameraWidth',500);return np.array([960+np.dot(rel,right)*scale,540-np.dot(rel,up)*scale])"""
OLD="    scale=1920/d['cameraWidth'];return np.array([960+np.dot(rel,right)*scale,540-np.dot(rel,up)*scale])"

def main():
    names=('compose.py','sources.py','config.py','render_rows.py');now={n:(H/n).read_bytes()for n in names}
    before=dict(now);text=now['sources.py'].decode('utf8');assert BLOCK in text
    text=text.replace(BLOCK,OLD)
    for added in ("    if ep=='A09' and key=='fist':return (300,180,765,575)\n","    if ep=='A18' and key=='wrist':return (250,220,850,850)\n"):
        assert added in text;text=text.replace(added,'')
    before['sources.py']=text.encode('utf8')
    code=lambda x:hashlib.sha256(b''.join(x[n]for n in names)).hexdigest()
    oldcode,newcode=code(before),code(now);plan=read(H/'replacement-plan.json');proof=[]
    for e in plan['episodes']:
        if e['id'] not in ('A01','A02'):continue
        assert all('cameraWidth'in source(e['id'],k)['definition']for k in e['sourceInputs'])
        live={k:input_receipt(e['id'],k)for k in e['sourceInputs']}
        for row in e['rows']:
            dest=R/row['output'];receipt=dest.with_suffix('.json');d=read(receipt);assert d['sha256']==sha(dest)
            sign=lambda c:hashlib.sha256(json.dumps({'code':c,'row':row,'source':live[row['key']]},sort_keys=True).encode()).hexdigest()
            if d['signature']==sign(newcode):continue
            assert d['signature']==sign(oldcode),(e['id'],row['id'],'unexpected prior signature; no migration')
            d['signatureMigration']={'from':d['signature'],'reason':'Only missing cameraWidth fallback and A09/A18 crops changed; A01/A02 define cameraWidth explicitly and use neither crop, so all pixels remain identical.','oldCodeSHA256':oldcode,'currentCodeSHA256':newcode}
            d['signature']=sign(newcode);receipt.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
            proof.append({'episode':e['id'],'row':row['id'],'preservedMediaSha256':d['sha256']})
    (H/'adapter-equivalence.json').write_text(json.dumps({'scope':'A01/A02 only; old signature reconstructed and current media SHA checked. No re-encode or source change.','oldCodeSHA256':oldcode,'currentCodeSHA256':newcode,'preservedOutputs':proof},ensure_ascii=False,indent=2),'utf8')
    print('Validated exact unaffected output signatures',len(proof),flush=True)
if __name__=='__main__':main()
