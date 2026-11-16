"""Record the user's selected nine revisions and prepare the title-only render."""
from pathlib import Path
import datetime, hashlib, importlib.util, json

H=Path(__file__).resolve().parent; ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
KEY='explicitOriginalTechTwelve20261115'
ORDERS=[2,3,5,6,7,8,10,11,12]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def source(p,s):
 assert not p.exists(),p
 compile(s,str(p),'exec');p.write_text(s,'utf8')
def main():
 batch=read(H/'batch.json');selected=[x for x in batch['projects']if x['order']in ORDERS]
 assert len(selected)==9
 request=H/'selected-clarity-request-v83.json'
 write(request,dict(recordedAtKst=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
  selectedOrders=ORDERS,selectedSlugs=[x['slug']for x in selected],
  titleOnlyOrder=2,expandedExplanationOrders=[3,5,6,7,8,10,11,12],
  userRequest='2 마리오64 제목 변경. 3 저니 모래 반짝임 예시와 쉬운 설명. 5 더 쉬운 설명. 6 실제 스파이더맨 비교. 7/8/10 설명 사이 예시와 길이 확장. 11 화학 엔진 정의와 실제 예시. 12 만든 이유와 중간 예시.',
  titleChoice='3D 게임 카메라를 바꾼 게임, 마리오64 #게임개발',
  titleCorrection=dict(reason='Nintendo Star Fox1993 manual already documents selectable camera viewpoints; a universal first-camera claim is false.',primaryUrls=['https://www.nintendo.co.jp/clvs/manuals/common/pdf/CLV-P-SADGE.pdf','https://www.nintendo.co.jp/clvs/soft/s_fox.html']),
  originalReview=pin(H/'local-final-review-manifest-v2.json'),
  preserveOrders=[1,4,9],originalsPreserved=True,sourceOrderPreserved=True,
  actualIndependentFhdExamplesBeforeNarrationLock=True,unchangedApprovedPcmByteExact=True,
  naturalSpeed=True,allowLongerSinglePortraitVideo=True,intermediateApprovalRequired=False,
  resourcePolicy=pin(H/'resource-policy-v19.json'),platformActions=[],otherBatchesUnchanged=True,humanApproval=False))
 spec=importlib.util.spec_from_file_location('scoped_splice',H/'finalize-cpu-preparation-v1.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
 evidence=[]
 for name in ['video-production-control.json','video-worklist.json']:
  path=ROOT/'shared/publishing'/name;raw=path.read_bytes().decode('utf-8-sig');before=read(path);own=before[KEY]
  own.update(status='selected-clarity-revisions-in-production',automaticAdvanceWithinExactList=True,
   activeRevisionScope=[x['slug']for x in selected],currentSelectedProject=selected[0]['slug'],
   latestUserRequest=str(request.relative_to(ROOT)).replace('\\','/'),intermediateApprovalRequired=False,
   automaticAdvanceOutsideRevisionScope=False,automaticHeartbeatContinuation=False)
  updated=sp.replace_value(raw,KEY,own);after=json.loads(updated)
  assert {k:v for k,v in before.items()if k!=KEY}=={k:v for k,v in after.items()if k!=KEY}
  path.write_bytes(updated.encode('utf8'));evidence.append(dict(path=str(path),foreignContentPreserved=True))
 write(M/'clarity-revision-v83'/'scope-activation.json',dict(request=pin(request),shared=evidence))
 # Clone the reviewed compositor; old render sources and versions remain immutable.
 layout=(H/'shorts-layout-v3.py').read_text('utf8')
 layout=layout.replace("['마리오64의 카메라는','누가 움직일까?']","['3D 게임 카메라를 바꾼','마리오64']")
 source(H/'shorts-layout-clarity-v83.py',layout)
 s=(H/'run-camera-film-v7.py').read_text('utf8')
 s=s.replace("'film-v7'","'title-revision-v83/film-v83'").replace("HERE/'shorts-layout-v3.py'","HERE/'shorts-layout-clarity-v83.py'")
 s=s.replace("PROTOCOL='original-tech-twelve-camera-film-v7'","PROTOCOL='original-tech-twelve-mario-title-v83'")
 anchor="native.guard.qualifier.BASE=BASE/'resource-observations'"
 s=s.replace(anchor,anchor+";cooperative=module('camera_title_cooperative_v83',HERE/'cooperative-resource-policy-v19.py');cooperative.install(native)")
 s=s.replace("MEDIA/P.name/'final-review-v1'","MEDIA/P.name/'title-revision-v83/local-review-v2'")
 s=s.replace("'captioned-v7.mp4'","'captioned-v83.mp4'").replace("'clean-v7.mp4'","'clean-v83.mp4'")
 s=s.replace("audio=Path(prep['mix']['mix']['path'])if captioned else Path(read(BASE/'pilot-proof.json')['video']['path']);codec=['-c:a','aac','-b:a','192k','-ar','24000']if captioned else['-c:a','copy']","audio=MEDIA/P.name/'final-review-v1/captioned-v7.mp4';codec=['-c:a','copy']")
 s=s.replace("prep,reason=prepare(mode)\n            if prep:","reason=native.busy();prep=None\n            if reason is None:prep,reason=prepare(mode)\n            if prep:")
 source(H/'run-camera-title-revision-v83.py',s)
 print(json.dumps(dict(request=pin(request),selectedOrders=ORDERS,titleRenderer=pin(H/'run-camera-title-revision-v83.py'))))
if __name__=='__main__':main()
