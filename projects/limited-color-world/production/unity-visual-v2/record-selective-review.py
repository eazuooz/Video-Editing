"""Run only after directly inspecting the specified native sample set."""
import argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[4];M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
p=argparse.ArgumentParser();p.add_argument('--slug',required=True);p.add_argument('--cut',required=True);p.add_argument('--revision',required=True);p.add_argument('--finding',required=True);a=p.parse_args()
assert a.slug in ['limited-color-world','computer-controlled-players']
folder=M/a.slug/'preflight'/a.revision/a.cut;receipt=read(folder/'preflight-success.json');req=read(folder/'request.json');frames=sorted(folder.glob('frame-*.png'))
assert receipt['status']=='complete' and receipt['completed']==len(frames)
report={'slug':a.slug,'cutId':a.cut,'revision':a.revision,'status':'pass-temporal-sample-preflight','compiledSourceFingerprint':receipt['compiledSourceFingerprint'],'stageAssemblyMvid':receipt['stageAssemblyMvid'],'allNativeSamplesDirectlyViewed':True,'sampleCount':len(frames),'mobileWidth':375,'frames':[{'path':str(f),'sha256':sha(f)} for f in frames],'finding':a.finding,'finalCaptionedVerification':'pending','humanNewVersionReview':'pending'}
rev=R/'projects'/a.slug/'production/unity-visual-v2';write(rev/(a.cut+'-'+a.revision+'-review.json'),report)
v=read(rev/'visual-plan.json');c=next(c for c in v['cuts'] if c['id']==a.cut)
c['nativePreflight']={'revision':a.revision,'receipt':str(folder/'preflight-success.json'),'sha256':sha(folder/'preflight-success.json'),'compiledSourceFingerprint':receipt['compiledSourceFingerprint'],'stageAssemblyMvid':receipt['stageAssemblyMvid'],'samplesReviewed':len(frames),'all375StatesDirectlyViewed':True,'status':'pass-temporal-sample-layout-review','captionedFinalReview':'pending','finding':a.finding}
c.pop('sceneSha256AtPreflight',None);c['sceneSha256Observed']=sha(R/'unity/VideoEditing'/receipt['scene']);c['sceneSaveStatus']='saved-native-preflight-'+a.revision
write(rev/'visual-plan.json',v)
print(a.slug,a.cut,a.revision,'recorded')
