"""Create a separate local review package. Never upload or infer human approval."""
from pathlib import Path
import json,hashlib,shutil,html,zipfile
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v2';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v2/video');F=O/'final';D=O/'review';D.mkdir(exist_ok=True)
qa=json.loads((H/'technical-qa.json').read_text('utf8'));review=json.loads((H/'final-review.json').read_text('utf8'));assert review['encodedVisualReview']=='sampled-pass' and review['asrReview']=='complete-current-added-text-reviewed'
tm=json.loads((L/'timeline.json').read_text('utf8'));plan=json.loads((H/'revision-plan.json').read_text('utf8'));records=[]
for f,name in [(F/'ai-2d-game-assets.room-v2.clean.mp4','ai-2d-game-assets.clean.mp4'),(F/'ai-2d-game-assets.room-v2.captioned.mp4','ai-2d-game-assets.captioned.mp4'),(L/'captions.ko.srt','ai-2d-game-assets.ko.srt'),(L/'captions.en.srt','ai-2d-game-assets.en.srt')]:
 dest=D/name
 if not dest.exists():shutil.copy2(f,dest)
 sha=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest();assert sha==hashlib.file_digest(f.open('rb'),'sha256').hexdigest();records.append({'name':name,'path':str(dest),'sha256':sha,'bytes':dest.stat().st_size})
for src,name in [(H/'full-narration.ko.txt','전체-대본.txt'),(H/'public-tool-records-snapshot.json','tool-records.json'),(H/'public-provenance-snapshot.json','provenance.json'),(O/'qa/R01-68.jpg','poster.jpg')]:shutil.copy2(src,D/name)
with zipfile.ZipFile(D/'room-process-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in H.glob('*'):
  if f.is_file() and f.suffix in ['.txt','.json','.py','.cjs']:z.write(f,'process/'+f.name)
 for f in (R/'sites/yamyam-cartographers-room/dist/assets/motions').glob('*.png'):z.write(f,'motions/'+f.name)
 for f in (R/'sites/yamyam-cartographers-room/dist/assets/2dimg2motion').glob('*.png'):z.write(f,'map-loop/'+f.name)
 for f in (R/'sites/yamyam-cartographers-room/dist/assets/codixel').glob('read-*.png'):z.write(f,'book-read/'+f.name)
link='https://yamyam-cartographers-room.eazuooz.chatgpt.site';secs=tm['duration'];chapters=''.join(f'<li><a href="#" onclick="v.currentTime={s["start"]};v.play();return false">{int(s["start"]//60):02}:{int(s["start"]%60):02} · {html.escape(s["title"])}</a></li>' for s in tm['scenes'])
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AI 2D 리소스 · 방 게임 확장 검수</title><style>body{{background:#090d0d;color:#f5f4ed;font-family:system-ui,sans-serif;max-width:1160px;margin:auto;padding:24px}}a{{color:#83d8c1}}h1,h2{{color:#f1ce69}}video{{width:100%;max-height:70vh}}li{{padding:5px}}.note{{border-left:4px solid #f1ce69;padding:12px 18px;line-height:1.7}}p{{line-height:1.7}}@media(max-width:600px){{body{{padding:14px}}}}</style><h1>AI 그림을 움직이는 2D 게임으로</h1><p>1920×1080 · 60fps · {int(secs//60)}분 {int(secs%60)}초 · 기존 30문단 + 실제 제작 설명 16문단</p><video id="v" controls preload="metadata" poster="poster.jpg" src="ai-2d-game-assets.captioned.mp4"></video><p><a href="ai-2d-game-assets.captioned.mp4">전체 자막영상</a> · <a href="ai-2d-game-assets.clean.mp4">자막 없는 영상</a> · <a href="ai-2d-game-assets.ko.srt">한국어 자막</a> · <a href="ai-2d-game-assets.en.srt">영어 자막</a></p><p><a href="{link}" target="_blank">완성한 방 게임 직접 플레이</a> · <a href="room-process-kit.zip">모션·프롬프트·실행 기록 모음</a> · <a href="전체-대본.txt">전체 대본</a></p><p class="note">7개 공개 도구와 ComfyUI·이미지 생성의 실제 결과를 사용했습니다. Sprite-Sheet-Diffusion은 공식 필수 가중치 누락과 호환 다운로드 오류로 추론을 완성하지 못했으며, 해당 과정과 한계를 영상에 명시했습니다. 캐릭터 LoRA를 새로 학습한 결과로 표시하지 않습니다.</p><p>기술 검사와 추출 프레임·자막 검수를 통과했습니다. 실제 전체 음성 청취와 최종 사용자 검수는 별도이며 아직 완료로 기록하지 않았습니다. YouTube·Drive에는 업로드하지 않았습니다.</p><h2>장면별 검수</h2><ol>{chapters}</ol><h2>자료</h2><p><a href="tool-records.json">도구별 실제 실행 기록</a> · <a href="provenance.json">출처·에셋 기록</a></p><script>const v=document.getElementById('v')</script></html>'''
(D/'index.html').write_text(page,'utf8')
delivery={'revision':'room-v2','directory':str(D),'reviewUrl':'http://127.0.0.1:9286/','playableUrl':link,'duration':secs,'files':records,'userReview':False,'humanListening':False,'youtubeUploaded':False,'driveUploaded':False,'previousMasterPreserved':True,'unresolved':qa['unresolved']}
(H/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),'utf8');print(D)
