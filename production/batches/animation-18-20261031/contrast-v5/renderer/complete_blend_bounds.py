"""A14-only common crop: include every captured transition frame, not 7 samples."""
from sources import *
import compose
import render_rows as rr
from copy import deepcopy

def measure(key):
    boxes=[];ep='A14'
    for n in range(source(ep,key)['definition']['frames']):
        arr=np.asarray(image(ep,key,n).resize((960,540),Image.Resampling.NEAREST))
        for side in (0,1):
            a=arr[35:530,10+480*side:470+480*side]
            lab,count=components(a.mean(axis=2)<145);sizes=np.bincount(lab.ravel());sizes[0]=0
            keep=np.flatnonzero(sizes>max(30,sizes.max(initial=0)*.02))
            yy,xx=np.nonzero(np.isin(lab,keep))
            if len(xx)>25:
                offset=960*side-panel_offset(ep,key,side)
                boxes.append([xx.min()*2+20+offset,yy.min()*2+70,xx.max()*2+20+offset,yy.max()*2+70])
    q=np.array(boxes);x0,y0=q[:,:2].min(axis=0)-35;x1,y1=q[:,2:].max(axis=0)+35
    return [int(max(0,x0)),int(max(0,y0)),int(min(960,x1)),int(min(1080,y1))]

def execute():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert control['renderAuthorized']and'A14'in control['episodes']
    cache=H/'blend-crop-evidence.json'
    if cache.exists():
        evidence=read(cache)
        assert all(evidence['sourceMetadataSHA256'][key]==sha(source('A14',key)['metadata'])for key in ('blend','duration'))
    else:
        crops={k:measure(k)for k in ('blend','duration')}
        evidence={'scope':'All180 original frames per study, both actors, common aligned crop. Half-resolution silhouette bounding,35px original-coordinate margin.','crops':crops,
            'sourceMetadataSHA256':{k:sha(source('A14',k)['metadata'])for k in crops},'sourcePixelsAltered':False,
            'limitation':'The authored blending source itself has no foot-lock IK; the baseline line is preserved. This fixes cropping only.'}
        cache.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf8')
    crops=evidence['crops'];original=compose.bounds
    compose.bounds=lambda ep,key:tuple(crops[key])if ep=='A14'and key in crops else original(ep,key)
    base=read(H/'replacement-plan.json');episode=next(e for e in base['episodes']if e['id']=='A14');rows=[]
    code=hashlib.sha256(Path(__file__).read_bytes()+cache.read_bytes()+b''.join((H/n).read_bytes()for n in ('compose.py','sources.py','config.py','render_rows.py'))).hexdigest()
    for source_row in episode['rows']:
        if source_row['key']not in crops:continue
        r=deepcopy(source_row);r['showLegend']=False;r['episode']='A14';r['overrideReason']='Full captured body retained at the middle of both blend transitions; same crop and scale for both actors.'
        dest=B/'local/contrast-v5/explanation-plates/A14/complete-bounds'/(r['id']+'.mp4');r['output']=str(dest.relative_to(R)).replace('\\','/')
        signature=hashlib.sha256(json.dumps({'code':code,'row':r,'source':input_receipt('A14',r['key']),'crop':crops[r['key']]},sort_keys=True).encode()).hexdigest()
        print(rr.render('A14',r,signature),r['id'],flush=True);r['sha256']=sha(dest);rows.append(r)
    (H/'blend-crop-corrections.json').write_text(json.dumps({'schemaVersion':1,'status':'rendered-current-silent-overrides','evidenceSHA256':sha(cache),'rows':rows,'sameLength':True,'audioChanged':False},ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':execute()
