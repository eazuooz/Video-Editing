"""Record the directly inspected final encoded samples; never infer human approval."""
from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent;P=H.parents[1]
O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
qa=read(H/'technical-qa.json');baseline=read(H/'baseline-asr-review.json');levels=read(H/'level-continuity.json')
assert qa['fullDecode']=='passed' and len(qa['samples'])==72
assert not levels['flagsWithMixIntroducedDipEvidence']
master=next(v for v in qa['videos'] if v['kind']=='captioned')
assert sha(Path(master['path']))==master['sha256']
result={
 'revision':'room-v3','reviewedAt':datetime.datetime.now().astimezone().isoformat(),
 'masterSha256':master['sha256'],'audioM4aSha256':sha(O/'final-mix.m4a'),
 'encodedVisualReview':'sampled-pass','asrReview':'complete-current-added-text-reviewed',
 'technicalEvidence':'technical-qa.json','baselineAsrEvidence':'baseline-asr-review.json',
 'addedAsrEvidence':'mix-asr-review.json','independentContextEvidence':'asr-context-review.json',
 'visualScope':{'encodedSamples':72,'allSceneIds':51,'contactSheetsViewed':[f'contact-{i}.jpg' for i in range(8)],
  'fullResolutionDetailsViewed':['R16-68','V33-68','V34-68','V35-68','branding','outro'],
  'mobile375SamplesViewed':['R01-68','R25-68','V31-68','V32-68','V33-68','V34-68','V35-68','R30-68'],
  'checks':['Actual game and sprite output visible; no blank async images','Same scale and stool-seat/sole contact guides match final room','Writing hands and large ledger remain visible','Lamp/candle labels point at the actual wicks','Meaningful motion/pose stages retain original aspect and pixel grid','Final boxed captions visible and clear of main explanatory targets','Overview and closing show actual active actions within their scene durations','Branding and original membership end preserved'],
  'materialDefects':[],'fullRealtimeWatch':False},
 'audioScope':{'allParagraphAsrCount':51,'originalPcmHashPreserved':30,'newParagraphs':21,
  'wholeActualListening':False,'unverified':'ASR cannot establish naturalness or exact pronunciation. Canonical display names are retained; named-term spelling differences remain listening candidates.',
  'asrSemanticOmissions':0,'negationOrNumericMeaningErrors':0,
  'levelContinuityEvidence':'level-continuity.json','mixIntroducedDipEvidence':0,
  'sourceRmsCandidateInterpretation':'52 contextual candidates exist in the source too; none shows a new mix-induced drop. This does not approve source intonation.',
  'integratedLufs':-16.17,'truePeakDbtp':-2.0,'sameAacInCleanAndCaptioned':True},
 'gameEvidence':'game-visual-audit.json','siteEvidence':'site-deployment.json',
 'toolExecutionBoundary':{'completedOssTools':7,'Sprite-Sheet-Diffusion':'Official required PoseGuider file missing; real installation attempt documented, no inference output claimed.','characterLoraTraining':'Not performed; independently explained as an alternative path.'},
 'humanVideoReview':False,'humanListening':False,'youtubeUploaded':False,'driveUploaded':False,
 'next':'Deliver exact local master for user review; preserve previous master and platform state.'}
(H/'final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
qa['encodedVisualReview']='sampled-pass';qa['visualEvidence']='final-review.json'
(H/'technical-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf8')
print(master['sha256'])
