"""Numerical and preservation checks before synthesis; not audiovisual QA."""
from pathlib import Path
import json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
d=json.loads((B/'quaternion-additive-draft.json').read_text(encoding='utf8'))
o=json.loads((B/'baselines/game-math-quaternion-operations/lesson.json').read_text(encoding='utf8'))
assert d['scenes']==o['scenes']
assert d['contract']==o['contract']
assert all(len(s['ko'])==len(s['en'])==len(s['beats']) for s in d['additions'])
def mul(a,b):
 a=np.array(a);b=np.array(b)
 return np.r_[a[0]*b[0]-a[1:]@b[1:],a[0]*b[1:]+b[0]*a[1:]+np.cross(a[1:],b[1:])]
c=math.sqrt(.5);q=[c,0,0,c];p=[0,1,0,1];inverse=[c,0,0,-c]
checks=[]
def check(name,a,b):
 assert np.allclose(a,b,atol=1e-12),name
 checks.append({'name':name,'computed':np.asarray(a).tolist(),'expected':np.asarray(b).tolist(),'passed':True})
z=(2+1j)*1j;check('complex i rotation',[z.real,z.imag],[-1,2]);check('planar length',abs(z),math.sqrt(5))
check('normalization',[v/5 for v in [3,0,0,4]],[.6,0,0,.8]);check('unit norm',np.dot([.6,0,0,.8],[.6,0,0,.8]),1)
check('x dot y',np.dot([1,0,0],[0,1,0]),0);check('x cross y',np.cross([1,0,0],[0,1,0]),[0,0,1]);check('y cross x',np.cross([0,1,0],[1,0,0]),[0,0,-1])
check('one sided scalar leakage',mul(q,p),[-c,c,c,c]);check('two sided vector rotation',mul(mul(q,p),inverse),[0,0,1,1]);check('inverse identity',mul(q,inverse),[1,0,0,0])
half=[math.cos(math.pi/8),0,0,math.sin(math.pi/8)];check('45+45=90',mul(half,half),q)
check('full angle from halved log',2*(math.pi/4/2),math.pi/4)
result={'status':'pre-TTS-math-and-preservation-only','originalSceneOrderAndAllFieldsExact':True,'originalScenes':len(o['scenes']),'originalKoLines':sum(len(s['ko']) for s in o['scenes']),'originalEnLines':sum(len(s['en']) for s in o['scenes']),'originalContractExact':True,'additions':len(d['additions']),'bridges':len(d['bridges']),'newDraftSha256':hashlib.sha256((B/'quaternion-additive-draft.json').read_bytes()).hexdigest(),'checks':checks,'narrationAndAnimatedPixelReviewComplete':False,'additionalFootageAndEpisodeRatiosComplete':False}
(B/'quaternion-pretts-math-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['originalScenes','originalKoLines','additions','bridges','originalContractExact']}))
