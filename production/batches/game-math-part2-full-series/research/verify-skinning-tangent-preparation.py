"""Independent future-source checks; no new video or synthesis is started."""
from pathlib import Path
import json,hashlib,datetime
import numpy as np
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent.parent
close=lambda a,b:np.testing.assert_allclose(a,b,atol=1e-10,rtol=1e-10)
checks=[]
def check(name,evidence):checks.append({'name':name,'passed':True,'evidence':evidence})
# Course contract: column vectors and bone transforms expressed in one model frame.
bind=np.eye(4);bind[:3,3]=[2,0,0]
current=np.array([[0.,-1,0,2],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
p=np.array([3.,0,0,1]);palette=current@np.linalg.inv(bind)
close(bind@np.linalg.inv(bind),np.eye(4));close(palette@p,[2,1,0,1])
local=np.linalg.inv(bind)@p;close(current@local,palette@p)
close(.6*p+.4*(palette@p),[2.6,.4,0,1])
check('bind-space-to-current-model-and-weighted-position',{'contract':'Column vectors; all bones in common model coordinates; glTF node-output conventions are separate.','bindVertex':p.tolist(),'rigidCandidates':[p.tolist(),(palette@p).tolist()],'weights':[.6,.4],'weightedPosition':[2.6,.4,0],'restPalette':'identity; inverse bind is applied first'})
Rplus=np.array([[0.,-1],[1,0]]);Rminus=Rplus.T;blend=.5*Rplus+.5*Rminus
close(blend,np.zeros((2,2)));check('rigid-bones-do-not-guarantee-rigid-blend',{'individualDeterminants':[float(np.linalg.det(Rplus)),float(np.linalg.det(Rminus))],'blendDeterminant':float(np.linalg.det(blend)),'normalizationGuardRequired':True,'scope':'Independent LBS counterexample; do not call weighted rotations SLERP or promise general exact surface normals.'})
check('illustrative-unpadded-record-memory',{'assumptions':'int32,float32,Vector3=three floats; four influences; no padding/compression','separateBonePositionsAndNormalsBytes':4*2*12,'singleBindPositionAndNormalBytes':2*12,'reductionBytes':72,'fourInfluences':'Example cap, not a universal hardware limit'})
decoded=2*np.array([37.,128.,218.])/255-1;unit=decoded/np.linalg.norm(decoded)
assert abs(decoded[1])>0 and not np.isclose(np.linalg.norm(decoded),1)
check('eight-bit-normal-decoding-is-quantized',{'encoded':[37,128,218],'decoded':decoded.tolist(),'unit':unit.tolist(),'formula':'2c/255-1 then nonzero normalization','sourceApproximation':[-.707,0,.707]})
q1=np.array([2.,0,0]);q2=np.array([0.,1,0]);s1,t1,s2,t2=-1.,0.,0.,1.
det=s1*t2-s2*t1;T=(t2*q1-t1*q2)/det;Bt=(-s2*q1+s1*q2)/det
close(T,[-2,0,0]);close(Bt,[0,1,0]);N=np.array([0.,0,1]);tu=T/np.linalg.norm(T);bu=Bt/np.linalg.norm(Bt)
hand=float(np.sign(np.dot(np.cross(N,tu),bu)));close(hand,-1);close(hand*np.cross(N,tu),bu)
check('negative-uv-determinant-preserves-both-axis-signs',{'determinant':det,'tangent':T.tolist(),'bitangent':Bt.tolist(),'handedness':hand,'wrongIfDenominatorDropped':{'tangent':(t2*q1-t1*q2).tolist(),'bitangent':(-s2*q1+s1*q2).tolist()},'guards':['zero UV determinant','zero accumulated tangent','zero normal','mirrored seam duplication']})
skew=np.column_stack(([1.,0,0],[1/np.sqrt(2),1/np.sqrt(2),0],[0,0,1]))
assert not np.allclose(np.linalg.inv(skew),skew.T)
close(np.array([0.,0,1])@np.array([1.,0,0]),0)
check('unit-axes-alone-do-not-make-transpose-an-inverse',{'unitButNonorthogonal':True,'requires':'Orthogonalize with a nonzero Gram-Schmidt tangent and matched handedness; otherwise use a valid inverse in the declared space.'})
ids=['3e10b1ffa61e8152a895c0dc5c84dce5','3e10b1ffa61e81e78763ecf6583c03b9'];sources=[]
for page_id in ids:
 f=R/f'tmp/game-math-part2-sources/current-20261009-{page_id}.txt';text=f.read_text(encoding='utf8')
 assert text.rstrip().endswith('</page>')
 sources.append({'pageId':page_id,'path':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'wholeFetchedTextDirectlyRead':True,'notionVerification':'Do not imply verified-page status; metadata/rights remain separate.'})
record={'status':'future-source-and-independent-math-preparation','preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'game-math-skinning-normal-map','sources':sources,'checks':checks,'primaryReferences':[{'url':'https://terathon.com/blog/tangent-space.html','supports':'Signed UV determinant,TBN inverse,Gram-Schmidt and per-vertex handedness.'},{'url':'https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#skins','supports':'LBS joint weights and inverse-bind ordering; bitangent uses tangent.w.'}],'sourceCorrections':['Do not combine originalTomb Raider with PlayStation2 as a current platform fact.','Treat original skinning normal transform and performance observations as an approximation/history,not a universal2026 prescription.','Do not discard negative UV determinant sign or divide by a zero determinant.','Source75%/25% tooling split is an authors historical observation,not a measured current industry statistic.','Normal-map vector channels and UV y conventions must match; encoded images are not measured proprietary game internals.'],'completeDuplicateAndNativeChannelReview':'pending-before-new-production','newProjectCreated':False,'ttsStarted':False}
target=B/'preflight/skinning-normal-map-source-preparation.json';target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'future independent checks passed; current sequential video remains unchanged.')
