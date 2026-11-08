"""Build the local review page after explicit current-file QA records exist."""
from pathlib import Path
import json,hashlib,shutil,html,datetime
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text('utf-8'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
qa=read(P/'production/technical-qa.json');review=read(P/'production/final-review.json')
assert review['encodedVisualReview']['status']=='sampled-pass'
assert review['asrTextReview']['status']=='reviewed-complete-current-text'
delivery=read(P/'production/delivery-output.json');D=R/delivery['directory'];tm=read(L/'timeline.json');rows=read(P/'script/content.json')['paragraphs']
for source,name in [(L/'ai-2d-demo-kit.zip','ai-2d-demo-kit.zip'),(P/'production/DEMO_KIT.ko.md','실습자료-안내.md'),(P/'script/full-script.md','전체-대본.md'),(P/'planning/sources.json','sources.json'),(L/'qa/encoded-01.jpg','poster.jpg')]:shutil.copy2(source,D/name)
page=(D/'index.html').read_text('utf-8');page=page.replace('<video controls preload="metadata"','<video id="main" poster="poster.jpg" controls preload="metadata"')
links='<h2>장면별 바로 보기</h2><ol>'
for row,t in zip(rows,tm['scenes']):
 stamp=f"{int(t['start']//60):02}:{int(t['start']%60):02}"
 links+=f'<li><a href="{P.name}.captioned.mp4#t={t["start"]:.3f}" onclick="const v=document.getElementById(\'main\');v.currentTime={t["start"]:.3f};v.scrollIntoView();v.play();return false;">{stamp} · {html.escape(row["title"])}</a></li>'
links+='</ol><h2>실습 자료와 대본</h2><p><a download href="ai-2d-demo-kit.zip">이미지·시트·ComfyUI 워크플로</a> · <a href="실습자료-안내.md">실습자료 안내</a> · <a href="전체-대본.md">전체 대본</a> · <a href="sources.json">출처·버전 기록</a></p>'
links+='<p>직접 실행: ComfyUI, PixelOE, pixelfx, Pixelbolt. 나머지는 공식 자료를 검토한 원리 도식입니다. 캐릭터 LoRA 학습과 Unity 에디터 실행을 완료한 결과로 표시하지 않았습니다.</p>'
page=page.replace('<a href="../index.html">전체 목록</a> · ','')
closing='</body>' if '</body>' in page else '</html>'
page=page.replace(closing,links+'\n'+closing) if closing in page else page+links
(D/'index.html').write_text(page,'utf-8')
captioned=next(f for f in delivery['files'] if f['name'].endswith('.captioned.mp4'))
save(P/'production/review-ledger.json',{'slug':P.name,'stage':'local-final-review-delivered','master':{'path':str((D/captioned['name']).relative_to(R)).replace('\\','/'),'sha256':sha(D/captioned['name']),'bytes':(D/captioned['name']).stat().st_size},'technicalQa':'production/technical-qa.json','sampledVisualQa':'production/final-review.json','narrationLevelContinuity':'production/level-continuity.json','wholeHumanListening':'pending','humanReview':{'status':'pending','viewingInferredFromLinks':False},'platform':{'youtubeUploaded':False,'driveUploaded':False,'uploadAuthorized':False},'reviewUrl':'http://127.0.0.1:9283/','extraKitSha256':sha(D/'ai-2d-demo-kit.zip')})
m=read(P/'project.json');m['status']='local-final-review';m['delivery'].update(directory=delivery['directory'],reviewUrl='http://127.0.0.1:9283/');save(P/'project.json',m)
print(D)
