"""Finish only selected order2; preserve the other eleven and all prior cloud files."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];KEY='explicitOriginalTechTwelve20261115';SLUG='shorts-mario64-lakitu-camera'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def canonical(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 vp=H/'camera-paired-final-validation-v173.json';assert not vp.exists();mp=H/'local-final-review-manifest-v6.json';manifest=read(mp);old=read(H/'local-final-review-manifest-v5.json');row=manifest['projects'][1];page=H/'local-final-review-v6.html';receipt=H/'mobile-selected-camera-review-v173.json';mobile=read(receipt)
 assert manifest['selectedOrders']==[2]and manifest['exactProjectCount']==12 and manifest['completedSelectedRevisions']==1 and manifest['pendingSelectedRevisions']==0
 assert row['titleKo']=='3D 게임의 판도를 바꾼 마리오64'and row['actualMixSeconds']==93.2
 assert all(manifest['projects'][i]==old['projects'][i]for i in range(12)if i!=1)
 for r in manifest['projects']:
  for f in r['artifacts'].values():assert pin(f['path'])['sha256']==f['sha256']
 assert mobile['source']==row['artifacts']['captioned']and mobile['selectedOrder']==2 and not mobile['publicPublication']and not mobile['humanApproval']
 meta=mobile['drive'];assert meta['shared']is False and meta['parent_ids']==[mobile['folder']['id']]and int(meta['size'])==mobile['source']['bytes']and meta['permissions']and all(x['type']=='user'and x['role']=='owner'for x in meta['permissions'])
 assert mobile['folder']['ownerOnly']and mobile['folder']['permissionReadbackVerified']
 assert pin(ROOT/'projects/shorts-leveldesign-11-05/checkpoint.json')['sha256']=='7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
 sp=module('pair173_keys',H/'finalize-cpu-preparation-v1.py');rm=module('pair173_row',H/'finish-lockon-revision-ledger-v80.py');scopes=[];relative=str(page.relative_to(ROOT)).replace('\\','/')
 summary=dict(request=pin(H/'user-camera-paired-revision-v164.json'),selectedOrders=[2],titleKo=row['titleKo'],bundle=row['bundle'],version=row['version'],durationSeconds=93.2,manifest=pin(mp),reviewPage=relative,mobileReceipt=pin(receipt),mobileUrl=meta['url'],newActualUnityFixedModes=5,newActualUnityFixedFrames=3600,matchingActorModelStates=3600,acceptedAudioAacUnchanged=True,otherElevenPreserved=True,actualRealtimePlayback=False,actualFullListening=False,actualPhonePlayback=False,humanApproval=False,postedInChat=False)
 for name in ['video-production-control.json','video-worklist.json']:
  p=ROOT/'shared/publishing'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw);own=copy.deepcopy(data[KEY]);own.update(status='selected-paired-camera-local-and-phone-review-ready',reviewPage=relative,progressPage=relative,localFinalVideos=12,localFinalReviewReady=True,finalDeliveryPrepared=True,deliveryPostedInChat=False,currentSelectedProject=None,activeRevisionScope=[],automaticAdvanceWithinExactList=False,automaticAdvanceOutsideRevisionScope=False,automaticHeartbeatContinuation=False,completedRevisionScope=[SLUG],resourceStatus='Selected order2 title and paired Unity camera revision complete. Existing audio and other11 masters preserved; user viewing approval pending.')
  own['latestPairedCameraRevision']=summary;own['currentFiniteRevision']=dict(summary,status='complete',scope=[SLUG],maximumSelectedProjects=1,otherProjectsAuthorized=False)
  own.setdefault('mobileReviewDelivery',{}).setdefault('selectedRevisionOverrides',{})['OT12-02']=dict(receipt=pin(receipt),fileId=meta['id'],url=meta['url'],version=row['version'],sourceSha256=mobile['source']['sha256'],ownerOnly=True)
  new=sp.replace_value(raw,KEY,own)
  if'rows'in data:
   selected=copy.deepcopy(next(r for r in data['rows']if r.get('id')=='OT12-02'));selected.update(title=row['titleKo'],productionComplete=True,productionStatus='새 제목·Unity 고정/조작 좌우 비교 수정본 검증 완료',executionStatus='선택한2번 수정 제작 완료',reviewStatus='자동 검사·표본 검토 완료 / 사용자 시청 대기',humanApproval=False,status='selected-paired-camera-review-ready',reviewPage=relative,progressPage=relative,platformStatus='YouTube 미업로드 / 새2번 Drive 비공개 폰 검수본 준비')
   selected['currentSelectedRevision']=dict(summary,status='complete');selected['pairedCameraRevision']=summary;selected['previousMobileReviewDelivery']=selected.get('mobileReviewDelivery');selected['mobileReviewDelivery']=dict(receipt=pin(receipt),fileId=meta['id'],url=meta['url'],folderUrl=mobile['folder']['url'],version=row['version'],sourceSha256=mobile['source']['sha256'],sourceBytes=mobile['source']['bytes'],ownerOnly=True,permissionReadbackVerified=True,actualPhonePlayback=False,humanApproval=False)
   progress=copy.deepcopy(selected.get('latestVerifiedProductionProgress',{}));progress.update(title=row['titleKo'],currentVersion=row['version'],finalVideo=True,finalBundle=row['bundle'],voiceDuration=93.2,pairedFixedNativeVerified=True,acceptedVoiceMusicAndAacUnchanged=True,humanApproval=False);selected['latestVerifiedProductionProgress']=progress;new=rm.replace_one_row(new,selected)
  after=json.loads(new);left=copy.deepcopy(data);right=copy.deepcopy(after)
  for d in[left,right]:
   d.pop(KEY)
   if'rows'in d:d['rows']=[r for r in d['rows']if r.get('id')!='OT12-02']
  assert left==right,'Unselected row or foreign key changed';assert p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+new.encode('utf8'));scopes.append(dict(path=str(p),ownKeySha256=canonical(after[KEY]),rowSha256=canonical([r for r in after['rows']if r.get('id','').startswith('OT12-')])if'rows'in after else None))
 docscopes=[];start='<!-- ORIGINAL-TECH-TWELVE-20261115 -->';end='<!-- ORIGINAL-TECH-TWELVE-20261115-END -->'
 for name in ['VIDEO_WORKFLOW.md','VIDEO_WORKLIST.md']:
  p=ROOT/'docs'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');a,z=raw.index(start),raw.index(end)+len(end);marker=raw[a:z]
  note=f"2026-11-18 사용자가 선택한2번만 추가 수정했다. 제목은 ‘{row['titleKo']}’이며 실제 두 게임 비교와 동일 캐릭터·상태의 Unity 고정 구도/시점 조작을 좌우에 함께 보여 준다. 새 고정 카메라5모드×720프레임은 실제 Unity 촬영·RGB 왕복 검증과 기존 조작 시연3600상태 대조를 마쳤고, 구역 경계의 실제329/330/331프레임을 확인했다. 기존93.2초 음성·음악 AAC와 한영 자막은 보존했다. [검수표 v6](../{relative})는2번만 새 파일로 교체하고 나머지11편의 경로·버전·SHA를 그대로 유지한다. [폰 검수용 새2번]({meta['url']})은 본인 계정만 접근하는 새 파일이며 이전12편 폴더와 파일은 보존했다. 실제 폰 재생·전체 청취·사용자 승인은 아직이고 YouTube/다른111편/자동화는 변경하지 않았다. 이번 한 편의 유한 수정 제작만 완료했다."
  assert note not in marker;updated=marker[:-len(end)].rstrip()+'\n\n'+note+'\n'+end;assert p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+(raw[:a]+updated+raw[z:]).encode('utf8'));docscopes.append(dict(path=str(p),ownMarkerSha256=hashlib.sha256(updated.encode('utf8')).hexdigest()))
 sources=[Path(__file__),H/'finalize-paired-camera-bundle-v172.py',H/'collect-paired-camera-review-v172.py',H/'user-camera-paired-revision-v164.json',ROOT/'projects'/SLUG/'planning/film-beats-paired-v171.json',mp,page,receipt]
 validation=dict(sourceInputs=[pin(p)for p in sources],scopedSharedInputs=scopes,scopedDocInputs=docscopes,progress=dict(finalVideos=12,currentRevisedVideos=1,selectedOrders=[2],otherElevenPreserved=True,newActualNativeFrames=3600,acceptedAudioAacByteExact=True,phoneFiles=1,humanApproval=False,actualFullListening=False,actualRealtimePlayback=False,platformActions=['selected-order2-owner-private-phone-review']),summary=summary)
 vp.write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(validation=pin(vp),selectedRevisionComplete=True,onlyOrder2Changed=True,phoneFiles=1)))
if __name__=='__main__':main()
