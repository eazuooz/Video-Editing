"""Collect all twelve new openings while preserving every preceding review artifact."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,html,json
H=Path(__file__).resolve().parent
C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def save(p,d):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def bundles():
 plan=read(H/'innovation-opening-plan-v181.json');mixed=read(C/'mixed-content-review-v183.json');rows=[]
 for row in plan['rows']:
  out=C/row['slug'];qa=read(out/'encoded-qa-v184.json');visual=read(out/'encoded-visual-review-v184.json');proof=read(out/'render-proof-v183.json');mix=read(out/'audio-build-v182.json')
  assert qa['allowedForUserReview']and visual['allowedForBatch']and qa['fullVideoDecodeAndPtsPassed']and qa['retainedBodyVclAndDecodedSamplesExact']
  folder=out/'local-review-v8';assert not folder.exists();folder.mkdir();arts={key:pin(proof['masters'][key]['path'])for key in ['captioned','clean']}
  for lang,key in [('ko','metadataKo'),('en','metadataEn')]:
   old=Path(row['baseline']['artifacts'][key]['path']).read_text('utf-8-sig');title,rest=old.split('\n',1);marker='Wholesome Kevin MacLeod (incompetech.com)';body,credits=rest.rsplit(marker,1)
   note='도입 추가: 기존의 어려움 → 이 기술의 변화 → 플레이어에게 생긴 이점 순서로 설명합니다. 기존 본문 영상·음성·배경음악은 보존했습니다. 새 도입은 같은 음악을 음성에 맞춰 조절했고, 새 발화는 문장 전체에 일정한 음량 조절만 적용했습니다.'if lang=='ko'else'Opening revision: the prior difficulty, the technical change, and the player benefit. The preceding body picture, voice, and background music are retained. The new opening uses the same music with voice-dependent background gain and constant gain per complete new utterance.'
   text=title+'\n\n'+row['newOpening'][lang]+'\n\n'+body.strip()+'\n\n'+note+'\n\n'+marker+credits.rstrip()+'\n';p=folder/('metadata-'+lang+'.txt');p.write_text(text,'utf8');assert text.rstrip().endswith('http://creativecommons.org/licenses/by/4.0/');arts[key]=pin(p)
  for lang,key in [('ko','subtitlesKo'),('en','subtitlesEn')]:arts[key]=pin(out/('captions-v182.'+lang+'.srt'))
  uncertainties=mixed['rows'][row['order']-1]['recognizerDisagreements'];prior=read(row['baseline']['bundle']['path'])
  bundle=dict(slug=row['slug'],order=row['order'],version='innovation-opening-v183-preserved-body',titleKo=row['titleKo'],durationSeconds=mix['durationSeconds'],addedOpeningSeconds=mix['introSeconds'],innovationTag=row['innovationTag'],opening=row['newOpening'],artifacts=arts,evidence=[pin(out/x)for x in ['render-proof-v183.json','audio-build-v182.json','encoded-qa-v184.json','encoded-visual-review-v184.json']]+[pin(C/'mixed-content-review-v183.json'),pin(H/'innovation-opening-plan-v181.json')],previousBundle=row['baseline']['bundle'],localFinalBundleComplete=True,priorBodyCodedPicturesPreserved=True,priorBodyFloatPcmPreserved=True,allTwelveAudibleMusicRetained=True,sourceSpeed=1,sourceAspectsPreserved=True,newWholeWordCaptions=True,unresolvedMachineRecognition=uncertainties,publicationHoldFromPreviousBundle=prior.get('publishingHold',prior.get('publicationHold')),actualFullListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])
  if row['order']==1:bundle['publicationHold']='Kyoto ninja-show reuse rights remain unverified; private review only. Existing publication hold preserved.'
  bp=folder/'bundle-v8.json';save(bp,bundle);rows.append(dict(order=row['order'],slug=row['slug'],titleKo=row['titleKo'],version=bundle['version'],bundle=pin(bp),artifacts=arts,actualMixSeconds=mix['durationSeconds'],addedOpeningSeconds=mix['introSeconds'],innovationTag=row['innovationTag'],checks=dict(fullDecodedVideoAudioChecksPassed=True,retainedBodyCodedPictureAndRgbExact=True,audibleMusicRetained=True,actualEncodedSamplesInspected=True,unresolvedMachineRecognition=uncertainties),humanApproval=False,platformActions=[]))
 save(C/'all-bundles-v186.json',dict(projects=rows,artifacts=72,humanApproval=False));print(json.dumps(dict(bundles=12,artifacts=72,manifest=pin(C/'all-bundles-v186.json'))))
def finalize():
 rows=read(C/'all-bundles-v186.json')['projects'];delivery=read(H/'mobile-review-delivery-v186.json');assert len(rows)==len(delivery['files'])==12 and delivery['verifiedOwnerOnly']
 for row,f in zip(rows,delivery['files']):
  assert f['order']==row['order']and f['localSha256']==row['artifacts']['captioned']['sha256']and int(f['remoteBytes'])==row['artifacts']['captioned']['bytes'];row['mobileReviewUrl']=f['url']
  for ref in row['artifacts'].values():assert pin(ref['path'])==ref
 manifest=dict(schemaVersion=8,exactProjectCount=12,selectedOrders=list(range(1,13)),previousDeliveredManifest=pin(H/'local-final-review-manifest-v7.json'),request=pin(H/'innovation-opening-plan-v181.json'),projects=rows,allArtifactHashesVerified=True,artifacts=72,totalExactAudioSeconds=sum(x['actualMixSeconds']for x in rows),completedSelectedRevisions=12,pendingSelectedRevisions=0,allTwelveInnovationOpeningsAdded=True,allTwelveAudibleMusicRevised=True,originalRe2ComparisonOrder=2,mobileFolder=delivery['folderUrl'],mobileUnifiedDelivery=pin(H/'mobile-review-delivery-v186.json'),actualRealtimePlayback=False,actualFullListening=False,humanApproval=False,deliveryPostedInChat=False,atUtc=datetime.now(timezone.utc).isoformat(),platformActions=['owner-private Drive review copies only'])
 save(H/'local-final-review-manifest-v8.json',manifest)
 esc=html.escape;cards=[]
 for row in rows:
  b=read(row['bundle']['path']);warning='<p class="note">새 도입의 기계 음성인식 결과에 차이가 있어 청취 확인 항목으로 남겼습니다.</p>'if b['unresolvedMachineRecognition']else''
  if row['order']==1:warning+='<p class="note">교토 닌자 공연 재사용 권리 확인은 별도 보류 중입니다. 비공개 검수본입니다.</p>'
  links=' · '.join('<a href="'+esc(Path(row['artifacts'][k]['path']).as_uri(),quote=True)+'">'+label+'</a>'for k,label in [('clean','클린 영상'),('subtitlesKo','KO 자막'),('subtitlesEn','EN 자막'),('metadataKo','KO 제목·설명'),('metadataEn','EN 제목·설명')])
  cards.append(f'<article id="v{row["order"]}"><h2>{row["order"]:02}. {esc(row["titleKo"])}</h2><p class="tag">{esc(row["innovationTag"])}</p><p>{esc(b["opening"]["ko"])}</p><p>총 {row["actualMixSeconds"]:.2f}초 · 새 도입 {row["addedOpeningSeconds"]:.2f}초 · 기술검사·표본 화면 확인 · 사람 검수 대기</p><a class="button" href="{esc(row["mobileReviewUrl"],quote=True)}">폰에서 영상 보기</a><video controls playsinline preload="none" src="{esc(Path(row["artifacts"]["captioned"]["path"]).as_uri(),quote=True)}"></video>{warning}<p>{links}</p><details><summary>전체 KO 제목·설명</summary><pre>{esc(Path(row["artifacts"]["metadataKo"]["path"]).read_text("utf8"))}</pre></details><details><summary>전체 EN 제목·설명</summary><pre>{esc(Path(row["artifacts"]["metadataEn"]["path"]).read_text("utf8"))}</pre></details><p class="hash">v183 · SHA256 {row["artifacts"]["captioned"]["sha256"]}</p></article>')
 page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>혁신 포인트 도입 추가 · 12편 검수</title><style>body{font:17px/1.65 system-ui;margin:auto;padding:20px;max-width:920px;color:#edf5f0;background:#112019}h1{font-size:28px}h2{font-size:23px}article{margin:32px 0;padding:22px;background:#1d3027;border-radius:16px}a{color:#9eeec8}.button{display:inline-block;padding:10px 18px;background:#bfeb9d;color:#102019;border-radius:9px;text-decoration:none}.tag{color:#f3cf77}video{display:block;width:100%;max-width:430px;margin:18px auto}.hash{font-size:12px;overflow-wrap:anywhere;color:#b4c5bb}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}.note{color:#ffda98}summary{cursor:pointer}</style><h1>혁신 포인트를 먼저 설명하는 12편</h1><p>기존 어려움 → 달라진 방식 → 플레이어에게 생긴 이점. 최신 마리오64·바이오하자드2·Unity 좌우 비교와 12편의 배경음악을 보존했습니다.</p><p><a class="button" href="'+esc(delivery['folderUrl'],quote=True)+'">12편 폰 검수 폴더</a></p><p>01~12 순서입니다. 영상·음성 자동 검사와 표본 화면 확인을 마쳤으며, 전체 청취·실시간 재생·사용자 승인은 별도입니다.</p>'+''.join(cards)+'</html>'
 p=H/'local-final-review-v8.html';assert not p.exists();p.write_text(page,'utf8');print(json.dumps(dict(manifest=pin(H/'local-final-review-manifest-v8.json'),page=pin(p),mobileFolder=delivery['folderUrl'])))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-bundles',action='store_true');ap.add_argument('--finalize',action='store_true');a=ap.parse_args();assert a.prepare_bundles!=a.finalize;bundles()if a.prepare_bundles else finalize()
