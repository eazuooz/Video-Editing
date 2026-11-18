"""Read all twelve real revised bundles into one sequential local review page."""
from pathlib import Path
import datetime,hashlib,json,copy,html
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def main():
 previous=H/'local-final-review-manifest-v4.json';old=read(previous);rows=[];folder='https://drive.google.com/drive/folders/1SsM1tBG-dB-VRWYfd9ZsbDSjYrTZ-DTY'
 for prior in old['projects']:
  slug=prior['slug'];root=M/slug/'camera-music-v139';bp=root/'local-review-v5/bundle-v5.json'if prior['order']==2 else root/('remux-v152'if prior['order']==1 else'remux-v162')/'local-review-v5/bundle-v5.json';b=read(bp);assert b['localFinalBundleComplete']and not b['humanApproval']and b['slug']==slug
  artifacts={}
  for key,source in b['artifacts'].items():
   actual=pin(source['path']);assert actual['sha256']==source['sha256'];artifacts[key]=actual
  assert len(artifacts)==6
  row=copy.deepcopy(prior);row.update(titleKo=b['titleKo'],version=b['version'],bundle=pin(bp),artifacts=artifacts,actualMixSeconds=b['durationSeconds'],checks=dict(priorVisualChecksPreserved=prior['checks'],newTechnicalEvidence=b['evidence'],wholeWordAudioAndTruePeakChecked=True,musicMedianDbBelowVoice=b['musicMedianDbBelowVoice'],actualRealtimePlayback=False,actualFullListening=False,humanApproval=False),selectedRevisionComplete=True);rows.append(row)
 assert [r['order']for r in rows]==list(range(1,13))and len({r['slug']for r in rows})==12
 manifest=dict(schemaVersion=5,exactProjectCount=12,selectedRevision='camera-comparison-and-audible-bgm',previousDeliveredManifest=pin(previous),projects=rows,allArtifactHashesVerified=True,artifacts=72,totalExactAudioSeconds=sum(x['actualMixSeconds']for x in rows),completedSelectedRevisions=12,pendingSelectedRevisions=0,originalRe2ComparisonOrder=2,allTwelveAudibleMusicRevised=True,actualRealtimePlayback=False,actualFullListening=False,humanApproval=False,deliveryPostedInChat=False,mobileFolder=folder,platformActions=[],request=pin(H/'user-camera-music-revision-v139.json'),atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 mp=H/'local-final-review-manifest-v5.json';assert not mp.exists();mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 E=html.escape;uri=lambda p:Path(p).as_uri();parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임 개발 쇼츠12편 · 수정 검수표 v5</title><style>body{max-width:980px;margin:25px auto;padding:0 16px;background:#101713;color:#edf4ef;font:17px/1.65 system-ui,sans-serif}a{color:#8ee5c8}section{padding:20px;border:1px solid #43564a;border-radius:12px;margin:24px 0}video{display:block;width:min(100%,380px);max-height:75vh;margin:16px auto;background:black}code{overflow-wrap:anywhere}.notice{background:#413520;padding:16px}.tag{color:#bfd1c5}.button{display:inline-block;background:#1b4b3c;padding:10px 16px;border-radius:8px}table{width:100%;border-collapse:collapse}td,th{padding:9px;text-align:left;border-bottom:1px solid #43564a}</style><body><h1>게임 개발 쇼츠12편 · 수정 검수표 v5</h1><p>2번: 바이오하자드2 원작의 고정 카메라와 마리오64의 카메라 조작 비교. 전12편: 배경음악 음량 수정.</p><p><a class="button" href="'+folder+'">폰으로 수정본12편 열기</a></p><p class="notice">자동 검사와 기술 검토를 마친 로컬 검수본입니다. 실제 전체 청취·실시간 재생·사용자 승인은 아직입니다. 1번 교토 공연 소스의 공개 재사용 권한 미확인 상태는 유지되며, 이 폴더는 본인만 접근하는 비공개 검수용입니다. YouTube 게시 상태는 바꾸지 않았습니다.</p><table><tr><th>순서</th><th>영상</th><th>길이</th></tr>']
 for r in rows:parts.append(f'<tr><td>{r["order"]:02}</td><td><a href="#v{r["order"]}">{E(r["titleKo"])}</a></td><td>{r["actualMixSeconds"]:.2f}초</td></tr>')
 parts.append('</table>')
 labels=dict(clean='클린 영상',subtitlesKo='KO 자막',subtitlesEn='EN 자막',metadataKo='KO 제목·설명',metadataEn='EN 제목·설명')
 for r in rows:
  a=r['artifacts'];n=r['order'];parts.append(f'<section id="v{n}"><h2>{n:02}. {E(r["titleKo"])}</h2><p class="tag">{E(r["version"])} · {r["actualMixSeconds"]:.2f}초 · 1080×1920 / 60fps · 사람 검수 대기</p><video controls playsinline preload="none" src="{E(uri(a["captioned"]["path"]))}"></video><p>')
  parts.append(' · '.join(f'<a href="{E(uri(a[k]["path"]))}">{label}</a>'for k,label in labels.items()))
  parts.append('</p>')
  if n==1:parts.append('<p>음성 확인 메모: 새 믹스의 자동 인식에서 ‘숲의 신전’ 고유명사가 다르게 잡혔습니다. 기존 검증 원음은 그대로이며, 이 이름의 발음을 직접 들어 확인해 주세요.</p>')
  parts.append('<details><summary>파일 버전·SHA256</summary>')
  for k,f in a.items():parts.append(f'<p>{k} · {f["bytes"]:,} bytes<br><code>{f["sha256"]}</code></p>')
  parts.append('</details>')
  if n<12:parts.append(f'<p><a href="#v{n+1}">다음 영상으로</a></p>')
  parts.append('</section>')
 parts.append('<p><a href="'+E(uri(mp))+'">전체 manifest</a> · <a href="'+E(uri(H/'local-final-review-v4.html'))+'">이전 검수표 v4</a></p></body></html>');page=H/'local-final-review-v5.html';assert not page.exists();page.write_text(''.join(parts),'utf8');print(json.dumps(dict(page=pin(page),manifest=pin(mp),videos=12,artifacts=72)))
if __name__=='__main__':main()
