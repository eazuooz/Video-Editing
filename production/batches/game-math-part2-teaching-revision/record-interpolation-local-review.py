"""Save manually performed final reviews, tied to an explicit current SHA."""
from pathlib import Path
import json,hashlib,sys,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug,digest=sys.argv[1:3];assert slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
P=ROOT/'projects'/slug;W=ROOT/'shared/output'/slug
m=read(P/'project.json');t=read(P/'production/timeline.json');qa=read(P/'production/qa.json')
assert sha(ROOT/m['paths']['videoBurnedCaptions'])==digest==qa['videos']['videoBurnedCaptions']['sha256']
assert qa['fullDecodePassed'] and qa['ratioErrorFrames']==0 and qa['koEnMatchingTimes']
assert t['actualFrames']*5==t['bodyFrames']*2 and t['explanationFrames']*5==t['bodyFrames']*3
assert not qa['backgroundMusic'] and not qa['sourceAudioUsed']
native=read(W/'native-final-playback.json')
assert native['sha256']==digest and native['ended'] and native['playbackRate']==1
assert abs(native['currentTime']-t['seconds'])<.04
moving=read(W/'moving-pixel-review/index.json');assert moving['sha256']==digest
pixel=read(W/'final-pixel-review/extraction.json');assert pixel['sha256']==digest
audit={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'fullDecode':True,'body40To60Exact':True,'allCaptionCueSheetsDirectlyViewed':len(t['koCaptions']),'allCompositionSheetsDirectlyViewed':len(t['scenes'])+2,'allActualMovingSheetsDirectlyViewed':[{'scene':r['scene'],'pages':len(r['sheets'])} for r in moving['samples']],'nativeWholePlayback':native,'explanationMotion':'All19 additive Manim scenes directly reviewed in narration sequence; current IP04/IP08 numeric retakes separately rendered and reviewed. Original explanation scenes/order retained.','mathReview':'Right-handed column vectors, y-up, Hamilton wxyz; Ry(h)Rx(p)Rz(b); unit-length and inverse numerical examples checked. Screen projected lines and illustrative numbers distinguished from world/engine evidence.','causalFlow':'Same body and axes carried through interpolation, timing, representation change and round-trip verification; camera/cut changes announced. Next question motivates lines/bounds.','preservationAudit':'interpolation-preservation-audit.json','humanWholeListening':'pending','gameIPHumanRights':'pending','nativeMotionCanvasEditorPlayback':'unverified','uploadedCaptionProof':'pending'}
write(P/'production/current-pixel-review.json',audit)
qa['directVisualReview']='complete current hash: whole native1x playback, all cue/composition sheets, all action moving sheets and additive explanation motion';qa['currentPixelReview']='production/current-pixel-review.json';write(P/'production/qa.json',qa)
m['status']='reviewed-local-render; private-upload-pending';m['membershipOutro']['appliedToFinal']=True
m['approvals'].update(script='Original26 dictionaries/144KO/144EN preserved across two episodes; additive prerequisites and causal bridges reviewed',voice='Approved reference and preserved original PCM; current alignment/numeric retakes checked; human whole listening pending',pixels='Current final moving pixels, captions and whole native playback reviewed')
m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[],'openItems':['Human whole listening and game-IP review pending.','Private upload and actual platform verification pending.','Native Motion Canvas editor playback unverified.']};m['publishReady']=False
m['editing']['exampleInterleaving']['reviewStatus']='native candidate comparison and current final moving annotations directly reviewed'
write(P/'project.json',m)
print('Current local review saved:',slug,digest)
