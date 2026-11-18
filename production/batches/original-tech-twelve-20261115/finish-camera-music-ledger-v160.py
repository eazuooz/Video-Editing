"""Record only the requested exact12 revision and verified private phone files."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];KEY='explicitOriginalTechTwelve20261115'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 vp=H/'camera-music-final-validation-v160.json';assert not vp.exists();mp=H/'local-final-review-manifest-v5.json';manifest=read(mp);page=H/'local-final-review-v5.html';delivery=H/'mobile-review-delivery-v159.json';d=read(delivery)
 assert manifest['exactProjectCount']==12 and manifest['completedSelectedRevisions']==12 and manifest['allArtifactHashesVerified']and manifest['artifacts']==72
 assert len(d['projects'])==12 and d['folder']['ownerOnly']and d['folder']['permissionReadbackVerified']and not d['publicPublication']and not d['actualPhonePlayback']and not d['humanApproval']
 for row,mobile in zip(manifest['projects'],d['projects']):
  assert row['order']==mobile['order']and row['slug']==mobile['slug']and row['artifacts']['captioned']==mobile['source']
  for a in row['artifacts'].values():assert pin(a['path'])['sha256']==a['sha256']
  meta=mobile['drive'];assert int(meta['size'])==mobile['source']['bytes']and not meta['shared']and meta['parent_ids']==[d['folder']['id']]and meta['permissions']and all(x['type']=='user'and x['role']=='owner'for x in meta['permissions'])
 frozen=ROOT/'projects/shorts-leveldesign-11-05/checkpoint.json';assert pin(frozen)['sha256']=='7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
 sp=module('camera_music160_key',H/'finalize-cpu-preparation-v1.py');rows=module('camera_music160_rows',H/'finish-lockon-revision-ledger-v80.py');scopes=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat();relative=str(page.relative_to(ROOT)).replace('\\','/')
 summary=dict(request=pin(H/'user-camera-music-revision-v139.json'),manifest=pin(mp),reviewPage=relative,mobileDelivery=pin(delivery),completeLocalVideos=12,artifacts=72,newCameraComparisonOrder=2,audibleBgmRevisedOrders=list(range(1,13)),humanApproval=False,actualFullListening=False,actualRealtimePlayback=False,actualPhonePlayback=False,postedInChat=False)
 for name in ['video-production-control.json','video-worklist.json']:
  p=ROOT/'shared/publishing'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw);own=copy.deepcopy(data[KEY]);oldmobile=own.get('mobileReviewDelivery')
  own.update(status='camera-comparison-bgm-local-and-mobile-review-ready',updatedAtKst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),localFinalVideos=12,reviewPage=relative,progressPage=relative,localFinalReviewReady=True,finalDeliveryPrepared=True,selectedRevisionReviewReady=True,deliveryPostedInChat=False,automaticAdvanceWithinExactList=False,currentSelectedProject=None,activeRevisionScope=[],completedRevisionScope=[x['slug']for x in manifest['projects']],resourceStatus='Requested camera comparison and all twelve music revisions completed; finite production ended. Human viewing and listening pending.')
  own['currentFiniteRevision']=dict(summary,status='complete-local-and-private-mobile',automaticRetry=False,outsideScopeAuthorized=False)
  own['latestCameraMusicRevision']=summary
  own['mobileReviewDelivery']=dict(receipt=pin(delivery),folder=d['folder'],sourceManifest=pin(mp),verifiedFiles=12,originalVideoBytesPreserved=True,transcoding=False,publicPublication=False,actualPhonePlayback=False,humanApproval=False,postedInChat=False,previousDelivery=oldmobile)
  new=sp.replace_value(raw,KEY,own)
  if'rows'in data:
   for r,m in zip(manifest['projects'],d['projects']):
    row=copy.deepcopy(next(x for x in data['rows']if x.get('id')==f"OT12-{r['order']:02d}"));row.update(productionComplete=True,productionStatus=('바이오하자드2 원작 카메라 비교·BGM 수정 완료'if r['order']==2 else'배경음악 수정·자막/클린/한영 파일 검증 완료'),executionStatus='요청한 수정 제작 완료',reviewStatus='수정본 기술 검사 완료 / 사람 검수 대기',humanApproval=False,platformStatus='YouTube 미업로드 / Drive 비공개 수정 검수본 준비',status='camera-music-revision-review-ready',reviewPage=relative,progressPage=relative,localMasterAvailable=True,automaticChecksPassed=True)
    row['cameraMusicRevision']=dict(bundle=r['bundle'],version=r['version'],durationSeconds=r['actualMixSeconds'],request=summary['request'],humanApproval=False)
    row['previousMobileReviewDelivery']=row.get('mobileReviewDelivery');row['mobileReviewDelivery']=dict(fileId=m['drive']['id'],url=m['drive']['url'],folderUrl=d['folder']['url'],version=r['version'],sourceSha256=m['source']['sha256'],sourceBytes=m['source']['bytes'],ownerOnly=True,permissionReadbackVerified=True,actualPhonePlayback=False,humanApproval=False,receipt=pin(delivery))
    progress=copy.deepcopy(row.get('latestVerifiedProductionProgress',{}));progress.update(finalVideo=True,finalBundle=r['bundle'],voiceDuration=r['actualMixSeconds'],title=r['titleKo'],currentVersion=r['version'],humanApproval=False,mixedAudioContentAndLevelsReviewed=True)
    if r['order']==2:progress['voiceProof']=pin(Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/r['slug']/'voice-repair-v147/voice-generation-complete-proof.json')
    row['latestVerifiedProductionProgress']=progress;new=rows.replace_one_row(new,row)
  after=json.loads(new);foreign1=copy.deepcopy(data);foreign2=copy.deepcopy(after)
  for x in[foreign1,foreign2]:
   x.pop(KEY)
   if'rows'in x:x['rows']=[r for r in x['rows']if not r.get('id','').startswith('OT12-')]
  assert foreign1==foreign2 and p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'));scopes.append(dict(path=str(p),ownKeySha256=canonical(after[KEY]),rowSha256=canonical([r for r in after['rows']if r.get('id','').startswith('OT12-')])if'rows'in after else None))
 docscopes=[];start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
 for name in ['VIDEO_WORKFLOW.md','VIDEO_WORKLIST.md']:
  p=ROOT/'docs'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');a,z=raw.index(start),raw.index(end)+len(end);old=raw[a:z]
  note=f"2026-11-18 카메라·BGM 수정 완료: 정확12편의 [최신 검수표 v5](../{relative})에 실제72파일·버전·SHA를 연결했다. 2번은 바이오하자드2 원작(1998)의 고정 카메라와 마리오64(1996)의 직접 둘러보기를 비교하고 기존21발화·8새발화를 연결한93.2초 수정본이다. 전12편은 승인 Wholesome 음악을 다시 조절했고 원음·기존 버전·기존 폰 검수 폴더를 보존했다. [새 비공개 폰 검수 폴더]({d['folder']['url']})의12개 원본 자막 마스터는 재인코딩 없이 올렸으며 실제 용량·부모·본인만 접근하는 권한을 확인했다. 실제 폰 재생·전체 청취·사람 승인은 아직이며, 1번 교토 소스의 기존 공개 채택 보류는 유지한다. 이번 유한 수정 제작만 완료했고 다른111편·자동화·YouTube 게시 상태는 바꾸지 않았다."
  assert note not in old;updated=old[:-len(end)].rstrip()+'\n\n'+note+'\n'+end;assert p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+(raw[:a]+updated+raw[z:]).encode('utf8'));docscopes.append(dict(path=str(p),ownMarkerSha256=hashlib.sha256(updated.encode('utf8')).hexdigest()))
 source=[Path(__file__),H/'finalize-camera-comparison-bundle-v157.py',H/'collect-camera-music-review-v158.py',mp,page,delivery,H/'user-camera-music-revision-v139.json']
 result=dict(sourceInputs=[pin(p)for p in source],scopedSharedInputs=scopes,scopedDocInputs=docscopes,progress=dict(finalVideos=12,currentRevisedVideos=12,artifacts=72,phoneFiles=12,ownerOnlyVerified=True,humanApproval=False,actualFullListening=False,actualRealtimePlayback=False,platformActions=['exact12-private-phone-review-only'],old111FrozenCheckpointPreserved=True,otherAutomationsUnchanged=True),summary=summary)
 vp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(validation=pin(vp),videos=12,artifacts=72,phoneFiles=12,humanApproval=False)))
if __name__=='__main__':main()
