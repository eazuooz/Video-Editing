"""Update only the current finite twelve rows and their shared batch key."""
from pathlib import Path
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181');KEY='explicitOriginalTechTwelve20261115'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 target=H/'innovation-opening-source-validation-v187.json';assert not target.exists();manifest=read(H/'local-final-review-manifest-v8.json');assert manifest['completedSelectedRevisions']==12 and manifest['allArtifactHashesVerified'];delivery=read(H/'mobile-review-delivery-v186.json');assert delivery['verifiedOwnerOnly']and len(delivery['files'])==12
 frozen=ROOT/'projects/shorts-leveldesign-11-05/checkpoint.json';assert pin(frozen)['sha256']=='7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
 sp=module('innovation_scope187',H/'finalize-cpu-preparation-v1.py');rm=module('innovation_rows187',H/'finish-lockon-revision-ledger-v80.py');ids={f'OT12-{i:02}'for i in range(1,13)};scopes=[];originals=[];page=str((H/'local-final-review-v8.html').relative_to(ROOT)).replace('\\','/')
 for p in [ROOT/'shared/publishing/video-production-control.json',ROOT/'shared/publishing/video-worklist.json']:
  raw=p.read_bytes();text=raw.decode('utf-8-sig');data=json.loads(text);originals.append(dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),ownKey=copy.deepcopy(data[KEY]),ownRows=copy.deepcopy([r for r in data.get('rows',[])if r.get('id')in ids])))
  own=data[KEY];own.update(status='all-twelve-innovation-openings-ready-for-user-review',automaticAdvanceWithinExactList=False,automaticAdvanceOutsideList=False,automaticHeartbeatContinuation=False,localFinalVideos=12,newOpeningVideos=12,reviewPage=page,localFinalReviewReady=True,finalDeliveryPrepared=True,deliveryPostedInChat=False,selectedRevisionReviewReady=True,completedRevisionScope=[r['slug']for r in manifest['projects']],humanFinalReviewRequired=True)
  own['currentFiniteRevision'].update(status='all-twelve-new-openings-rendered-encoded-QA-and-visual-samples-complete',newOpeningVideos=12,manifest=pin(H/'local-final-review-manifest-v8.json'),reviewPage=page,mobileReceipt=pin(H/'mobile-review-delivery-v186.json'),mobileFolder=delivery['folderUrl'],actualPhonePlayback=False,actualFullListening=False,humanApproval=False,unresolvedMachineRecognitionOrders=[5,12])
  own['mobileReviewDelivery']=dict(receipt=pin(H/'mobile-review-delivery-v186.json'),folderUrl=delivery['folderUrl'],verifiedFiles=12,ownerOnly=True,actualPhonePlayback=False,humanApproval=False,postedInChat=False,previousDeliveryReceipt=own.get('mobileReviewDelivery',{}).get('receipt'))
  own['latestUnifiedMobileReview']=own['mobileReviewDelivery'];new=sp.replace_value(text,KEY,own)
  if 'rows'in data:
   assert {r['id']for r in data['rows']if r.get('id')in ids}==ids
   for info in manifest['projects']:
    row=next(r for r in data['rows']if r.get('id')==f'OT12-{info["order"]:02}');assert row['slug']==info['slug'];uncertain=bool(info['checks']['unresolvedMachineRecognition'])
    revision=dict(version=info['version'],bundle=info['bundle'],artifacts=info['artifacts'],durationSeconds=info['actualMixSeconds'],addedOpeningSeconds=info['addedOpeningSeconds'],manifest=pin(H/'local-final-review-manifest-v8.json'),reviewPage=page,mobileUrl=info['mobileReviewUrl'],mobileReceipt=pin(H/'mobile-review-delivery-v186.json'),checks=info['checks'],actualFullListening=False,humanApproval=False)
    row.update(productionComplete=True,productionStatus='혁신 이유 도입 추가 수정본 완료',executionStatus='유한 12편 수정 제작 완료',reviewStatus='기술검사·표본 화면 확인 / 사용자 시청 대기'+(' / 새 도입 음성인식 차이 청취 확인'if uncertain else''),humanApproval=False,platformStatus='YouTube 미업로드 / Drive 비공개 폰 검수본 준비',localMasterAvailable=True,reviewPage=page,currentSelectedRevision=revision,innovationOpeningRevision=revision,mobileReviewDelivery=dict(receipt=pin(H/'mobile-review-delivery-v186.json'),url=info['mobileReviewUrl'],folderUrl=delivery['folderUrl'],ownerOnly=True,actualPhonePlayback=False,humanApproval=False),automaticChecksPassed=True)
    progress=row.get('latestVerifiedProductionProgress',{});progress.update(finalVideo=True,finalBundle=info['bundle'],finalCaptioned=info['artifacts']['captioned'],durationSeconds=info['actualMixSeconds'],innovationOpening=revision);row['latestVerifiedProductionProgress']=progress;new=rm.replace_one_row(new,row)
  before=json.loads(text);after=json.loads(new)
  for obj in [before,after]:
   obj.pop(KEY,None)
   if 'rows'in obj:obj['rows']=[r for r in obj['rows']if r.get('id')not in ids]
  assert before==after,'Preserve foreign rows and all other shared values'
  p.write_bytes((b'\xef\xbb\xbf'if raw.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'));after=json.loads(new);scopes.append(dict(path=str(p),ownKeySha256=canonical(after[KEY]),rowSha256=canonical([r for r in after.get('rows',[])if r.get('id')in ids])if'rows'in after else None))
 baseline=C/'pre-innovation-ledger-v187.json';assert not baseline.exists();baseline.write_text(json.dumps(originals,ensure_ascii=False,indent=2)+'\n','utf8')
 evidence=[pin(H/'local-final-review-manifest-v8.json'),pin(H/'local-final-review-v8.html'),pin(H/'mobile-review-delivery-v186.json'),pin(C/'all-bundles-v186.json'),pin(baseline)]
 result=dict(sourceInputs=[pin(H/'finalize-innovation-review-v186.py'),pin(H/'finish-innovation-ledger-v187.py'),pin(H/'verify-innovation-phone-v189.py'),pin(H/'record-innovation-mobile-v189.py'),pin(H/'mobile-review-delivery-v186.json'),pin(H/'local-final-review-manifest-v8.json'),pin(H/'local-final-review-v8.html')],scopedSharedInputs=scopes,scopedDocInputs=[],evidence=evidence,progress=dict(finalVideos=12,newOpeningVideos=12,all72ArtifactsVerified=True,mobileOwnerOnlyFiles=12,unresolvedMachineRecognitionOrders=[5,12],humanApproval=False),frozenOld111Checkpoint=pin(frozen),otherRowsAndAutomationsPreserved=True)
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(sourceValidation=pin(target),newOpeningVideos=12,allForeignRowsPreserved=True,humanApproval=False)))
if __name__=='__main__':main()
