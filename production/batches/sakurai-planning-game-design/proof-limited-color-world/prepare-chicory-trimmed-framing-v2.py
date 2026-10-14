"""Prepare precise candidate cuts only; preserve all first review files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
notes=json.loads((P/'chicory-native-observations-v1.json').read_text(encoding='utf-8'))
review=json.loads((P/'chicory-native-sample-direct-review-v1.json').read_text(encoding='utf-8'))
assert review['allSamplesAndBoardsDirectlyRead'] and review['actualOuterExitCode']==0
original=json.loads((P/'chicory-native-action-plan-v1.json').read_text(encoding='utf-8'))
cuts=[];excluded=[]
for n in notes['windows']:
    w=next(x for x in original['candidateWindows'] if x['key']==n['key'])
    keeps=n.get('candidateKeeps') or ([n['candidateKeep']] if n.get('candidateKeep') else [])
    if not keeps:excluded.append({'key':n['key'],'reason':n['heldReason']});continue
    for i,(a,b) in enumerate(keeps):
        af,bf=int(a*60),int(b*60);assert af/60==a and bf/60==b and af<bf
        cuts.append({'key':n['key']+(f'-part{i+1}' if len(keeps)>1 else ''),'reviewWindow':n['key'],'source':w['source'],'sourceFile':w['sourceFile'],'startFrame':af,'endFrameExclusive':bf,'startPts':af*256,'endPtsExclusive':bf*256,'timeBase':'1/15360','frameRate':'60/1','sourceStartSeconds':a,'sourceEndSecondsExclusive':b,'availableFrames':bf-af,'availableSeconds':b-a,'framingUpPixels':n.get('framingUpPixels',0),'sameFrameBottomBlurPixels':n.get('framingUpPixels',0),'observation':n['note'],'adopted':False,'exactTrimmedBoundaryReviewed':False,'captionFramedPixelReviewed':False,'allContinuousFramesReviewed':False})
out=P/'chicory-trimmed-framing-plan-v2.json';assert not out.exists()
data={'schemaVersion':2,'slug':'limited-color-world','recordedAt':datetime.now(timezone.utc).isoformat(),'priorReview':str((P/'chicory-native-sample-direct-review-v1.json').relative_to(ROOT)).replace('\\','/'),'priorReviewSha256':sha(P/'chicory-native-sample-direct-review-v1.json'),'cuts':cuts,'cutCount':len(cuts),'uniqueAvailableFrames':sum(c['availableFrames'] for c in cuts),'uniqueAvailableSeconds':sum(c['availableSeconds'] for c in cuts),'heldWindows':excluded,'captionTest':{'scope':'QA placeholder only; every final cue still needs direct review','style':'boxed-white-forest-v1','position':[960,970],'fontSize':48,'lineHeight':62,'padding':[22,11],'borderPixels':3,'shadowOffsetPixels':[14,14],'shadowColor':'#073c32','text':'색이 바뀌어도 윤곽과 높이로\n길의 상태를 읽을 수 있습니다.'},'sourceAudio':'exclude-all','speed':1,'loops':0,'footageAdopted':False,'publicRightsApproved':False,'projectOrScriptCreated':False,'gitImagesOrMediaAdded':0}
assert data['uniqueAvailableSeconds']==101.5
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:data[k] for k in ('cutCount','uniqueAvailableFrames','uniqueAvailableSeconds','footageAdopted')},ensure_ascii=False))
