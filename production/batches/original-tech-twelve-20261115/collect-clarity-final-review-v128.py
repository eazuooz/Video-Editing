"""Collect the exact twelve, replacing only the user's nine selected versions."""
from pathlib import Path
import copy,hashlib,html,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
SELECTED=[2,3,5,6,7,8,10,11,12]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def esc(s):return html.escape(str(s),quote=True)
def uri(p):return esc(Path(p).resolve().as_uri())
def main():
 original=read(H/'local-final-review-manifest-v2.json');manifest=copy.deepcopy(original);rows=manifest['projects'];assert len(rows)==12
 for row in rows:
  if row['order']not in SELECTED:continue
  bp=M/row['slug']/('title-revision-v83/local-review-v2/bundle-v2.json'if row['order']==2 else'clarity-revision-v83/local-review-v2/bundle-v2.json');bundle=read(bp);assert bundle['localFinalBundleComplete']
  row.update(version=bundle['version'],bundle=pin(bp),artifacts=bundle['artifacts'],actualMixSeconds=bundle['durationSeconds'],titleKo=bundle['titleKo'],selectedRevisionComplete=True,humanApproval=False,platformActions=[])
  row.pop('requestedClarityRevisionPending',None)
  if row['order']==2:
   row['checks']['technicalVisual']['approvedPilotReview']=pin(bp.parent.parent/'film-v83/pilot-visual-review.json')
   row['checks']['automatic']['aacPacketsByteExact']=True
  else:
   base=Path(next(x['path']for x in bundle['evidence']if Path(x['path']).name=='pilot-proof.json')).parent;pq=read(base/'pilot-encoded-qa.json');cq=read(base/'clean-encoded-qa.json');vr=read(base/'pilot-visual-review.json');assert pq['allAutomaticChecksPassed']and cq['allAutomaticChecksPassed']and vr['allowedForFinalBundle']
   row['checks']=dict(automatic=dict(size=[1080,1920],fps=60,videoFrames=pq['decodedVideoFrames'],bodyOnlyAudio=True,sourceSpeed=1,positiveWholeWordCaptions=True,encodedWordLevelsPassed=True),technicalVisual=dict(encodedCaptionSamples=len(pq['captionSamples']),displayWidth=375,approvedPilotReview=pin(base/'pilot-visual-review.json'),cleanDerivativeReview=pin(base/'clean-derivative-verification.json')),actualRealtimePlayback=False,actualFullListening=False,humanApproval=False)
 for i,row in enumerate(rows):
  assert row['order']==i+1
  if row['order']in[1,4,9]:assert row==original['projects'][i]
  assert set(row['artifacts'])=={'captioned','clean','metadataKo','metadataEn','subtitlesKo','subtitlesEn'}
  for r in row['artifacts'].values():assert pin(r['path'])==r
 previous_visual=manifest.pop('latestSelectedRevisionVisualReview',None)
 manifest.update(schemaVersion=3,previousSelectedRevisionVisualReview=previous_visual,latestSelectedRevisionVisualReviews=[dict(order=row['order'],slug=row['slug'],review=row['checks']['technicalVisual']['approvedPilotReview'])for row in rows if row['order']in SELECTED],selectedOrders=SELECTED,preservedOrders=[1,4,9],allArtifactHashesVerified=True,totalExactAudioSeconds=sum(row['actualMixSeconds']for row in rows),actualRealtimePlayback=False,actualFullListening=False,request=pin(H/'selected-clarity-request-v83.json'),selectedRevision='selected-nine-clarity-review-v4',previousDeliveredManifest=pin(H/'local-final-review-manifest-v2.json'),selectedLocalRevisionPreviewComplete=True,completedSelectedRevisions=9,pendingSelectedRevisions=0,unchangedOriginalFinalBundles=3,exactProjectCount=12,humanApproval=False,platformActions=[],deliveryPostedInChat=False)
 target=H/'local-final-review-manifest-v4.json';assert not target.exists();target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 style='body{max-width:1000px;margin:32px auto;padding:0 18px;font-family:system-ui,sans-serif;background:#101713;color:#edf4ef;line-height:1.65}a{color:#8ee5c8}table{border-collapse:collapse;width:100%}td,th{padding:9px;border-bottom:1px solid #43564a;text-align:left}section{border:1px solid #43564a;padding:22px;margin:26px 0;border-radius:12px}video{display:block;width:min(100%,380px);max-height:75vh;margin:16px auto;background:black}.notice{background:#413520;padding:15px;border-left:5px solid #f2ca77}.tag{color:#f2ca77}code{word-break:break-all;font-size:.82em}summary{cursor:pointer}h1{line-height:1.35}'
 parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임 개발 쇼츠12편 · 수정 검수표 v4</title><style>'+style+'</style><body><h1>게임 개발 쇼츠12편<br>수정 검수표 v4</h1><p>요청한9편의 수정을 반영했습니다. 2번은 제목 변경, 3·5·6·7·8·10·11·12번은 쉬운 설명과 예시를 보강했습니다. 1·4·9번은 기존 버전입니다.</p><p>자동 검사와 자막별375px 화면 검수는 완료했습니다. 연속 실시간 재생·전체 청취·사용자의 최종 승인은 별개이며, 이 표에서 차례로 직접 검수할 수 있습니다.</p><p class="notice">1번 교토 닌자 공연 영상은 사용 허락이 확인되지 않은 개인 로컬 검수용 참고 영상입니다. 1990년대 개발진 방문 당시 영상으로 설명하지 않습니다. 공개 채택 상태로 바꾸지 않았습니다.</p><table><thead><tr><th>번호</th><th>제목</th><th>길이</th><th>상태</th></tr></thead><tbody>']
 for row in rows:
  title=Path(row['artifacts']['metadataKo']['path']).read_text('utf8').splitlines()[0];sec=row['actualMixSeconds'];duration=f'{int(sec)//60}:{sec%60:05.2f}'
  parts.append(f'<tr><td>{row["order"]}</td><td><a href="#v{row["order"]}">{esc(title)}</a></td><td>{duration}</td><td>{"수정본 준비"if row["order"]in SELECTED else"기존본 유지"} / 사람 검수 대기</td></tr>')
 parts.append('</tbody></table>')
 for row in rows:
  f=row['artifacts'];title=Path(f['metadataKo']['path']).read_text('utf8').splitlines()[0]
  parts.append(f'<section id="v{row["order"]}"><h2>{row["order"]}. {esc(title)}</h2><p class="tag">{esc(row["version"])} · {row["actualMixSeconds"]:.2f}초 · 1080×1920 / 60fps · 사람 검수 대기</p><video controls preload="metadata" src="{uri(f["captioned"]["path"])}"></video><p>')
  parts.append(' · '.join(f'<a href="{uri(f[k]["path"])}">{label}</a>'for k,label in [('clean','클린 영상'),('subtitlesKo','KO 자막'),('subtitlesEn','EN 자막'),('metadataKo','KO 제목·설명'),('metadataEn','EN 제목·설명')]))
  parts.append('</p><details><summary>파일 버전·SHA256</summary>')
  for k,r in f.items():parts.append(f'<p>{esc(k)} · {r["bytes"]:,} bytes<br><code>{esc(r["sha256"])}</code></p>')
  parts.append('</details><p><a href="#v'+str(row['order']+1)+'">다음 영상으로</a></p></section>'if row['order']<12 else'</details></section>')
 parts.append('<p><a href="'+uri(target)+'">전체 manifest</a> · <a href="'+uri(H/'local-final-review-v2.html')+'">이전 검수표 v2</a></p></body></html>')
 page=H/'local-final-review-v4.html';assert not page.exists();page.write_text(''.join(parts),'utf8');print(json.dumps(dict(page=pin(page),manifest=pin(target),videos=12,selectedRevisions=9,artifacts=72,humanApproval=False)))
if __name__=='__main__':main()
