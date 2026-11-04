from pathlib import Path
from datetime import datetime,timezone
import json,shutil,html
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;R=H.parents[3];P=H.parents[1];L=H.parent/'local/fighters-v2';D=L/'delivery/output/animation-exaggeration'
def main():
 p=ap.read(H/'edit-plan.json');qa=ap.read(L/'edit/structural-verification.json');assert qa['status']=='pass'
 pixels=ap.read(H/'final-pixel-review.json');assert pixels['status']=='sampled-pixels-reviewed'
 asr=ap.read(H/'final-audio-asr-review.json');assert asr['matchedCharacterCoverage']>.95
 expected_old='4e66ee28fe8913c8761e9b50c6994cdcc92b143f7106233d07ec3eaf82d3b030'
 old=H.parent/'local/grid-v1/delivery/output/animation-exaggeration/animation-exaggeration.captioned.mp4';assert ap.sha(old)==expected_old
 D.mkdir(parents=True,exist_ok=True);files=[]
 for role in ['captioned.mp4','clean.mp4','ko.srt','en.srt']:
  if role.endswith('.mp4'):source=L/f'edit/animation-exaggeration-{role}'
  else:source=L/f'edit/captions.{role}'
  target=D/f'animation-exaggeration.{role}'
  if not target.exists():shutil.copy2(source,target)
  assert ap.sha(source)==ap.sha(target)
  files.append({'role':role,'name':target.name,'path':ap.relative(target),'sha256':ap.sha(target),'bytes':target.stat().st_size})
 cap=files[0];duration=p['totalFrames']/60;stamp=datetime.now(timezone.utc).isoformat()
 manifest={'episode':'A02','slug':'animation-exaggeration','revision':'fighters-v2','status':'collected-verified-master-pair-user-review-pending','directory':ap.relative(D),'createdAt':stamp,'format':{'width':1920,'height':1080,'fps':60,'frames':p['totalFrames'],'durationSeconds':duration},'files':files,'verification':{'structuralFinalPair':'pass','sampledCaptionPixels':132,'sampledSceneMidpoints':41,'fullEncodedSpeechCharacterCoverage':asr['matchedCharacterCoverage'],'humanFinalViewingAndListening':False},'gameplayShare':p['expectedGameplayShare'],'baselinePreserved':{'path':ap.relative(old),'sha256':expected_old},'platformMutation':False}
 ap.save(D/'delivery-manifest.json',manifest)
 title='동작의 과장 | 게임 캐릭터는 왜 현실보다 과장되게 움직일까?'
 page='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 A02 · 격투게임 예시 보강</title><style>:root{--bg:#0b0d0b;--text:#f4f4ee;--muted:#b3bab0;--yellow:#e8cf83;--line:#394037}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.7 'Malgun Gothic',sans-serif}main{max-width:1120px;margin:36px auto;padding:0 24px 48px}h1{font-size:30px;line-height:1.4}.brand,h2,a{color:var(--yellow)}.meta,small{color:var(--muted)}video{width:100%;aspect-ratio:16/9;background:black;display:block}.status{border-left:4px solid var(--yellow);padding-left:16px}button{border:1px solid var(--line);background:transparent;color:var(--text);padding:9px 12px;font:inherit;cursor:pointer;margin:5px 6px 5px 0}a{text-underline-offset:4px}li{padding:6px 0}code{font-size:12px;overflow-wrap:anywhere}@media(max-width:600px){main{padding:0 16px}h1{font-size:24px}}</style></head><body><main><div class="brand">얌얌코딩 · 애니메이션 A02</div><h1>'''+html.escape(title)+'''</h1><p class="meta">1080p · 60fps · 6분 4초 · 실제 게임 60% / 설명 40%</p><p class="status">킹 오브 파이터즈 XV·길티기어 -스트라이브- 예시를 보강한 새 검수본입니다.</p><video id="film" controls playsinline preload="metadata"><source src="animation-exaggeration.captioned.mp4" type="video/mp4"></video><p><a href="animation-exaggeration.captioned.mp4">전체 자막 영상 열기</a></p><p><button data-t="45.6">0:46 랄프의 펀치</button><button data-t="92.3">1:32 솔의 실루엣</button><button data-t="256.6">4:17 준비·공격·회복</button></p><h2>이번 수정</h2><ul><li>짧은 펀치와 크게 휘두르는 공격을 실제 게임으로 비교했습니다.</li><li>공격 방향과 준비 자세에 설명 표시를 넣었습니다.</li><li>기존 Unity 비교·수치 설명을 유지하고 샘플 B 내레이션을 추가했습니다.</li></ul><h2>영상과 자막</h2><ul>'''
 for f in files:page+=f'<li><a href="{f["name"]}" download>{ {"captioned.mp4":"한글 자막 영상","clean.mp4":"자막 없는 영상","ko.srt":"한글 SRT","en.srt":"영어 SRT"}[f["role"]]}</a> <small>{f["bytes"]/1e6:.1f} MB</small></li>'
 page+='</ul><details><summary>검수 및 파일 기록</summary><p>전체 파일 재생·프레임·음성 텍스트 검사와 화면 표본 검사를 마쳤습니다. 최종 시청·청취 검수는 대기 상태입니다.</p><code>'+cap['sha256']+'</code><p><a href="delivery-manifest.json">파일 기록</a></p></details></main><script>document.querySelectorAll("button[data-t]").forEach(b=>b.onclick=()=>{const v=document.getElementById("film");v.currentTime=Number(b.dataset.t);v.play()})</script></body></html>'
 (D/'index.html').write_text(page,encoding='utf-8')
 (D/'README.md').write_text('# A02 격투게임 예시 보강 검수본\n\n1080p60 · 6분4초 · 실제60:설명40.\n\n`index.html` 또는 `animation-exaggeration.captioned.mp4`로 전체 영상을 확인하세요. 기존 grid-v1은 보존했습니다.\n\n확인할 부분: 랄프와 솔의 움직임이 내레이션과 함께 잘 읽히는지, 추가 음성의 연결이 자연스러운지.\n\nYouTube·Drive 업로드는 수행하지 않았습니다.\n',encoding='utf-8')
 (D/'sources.txt').write_text('영상 출처 (YouTube 더보기 맨 아래용)\n\nThe King of Fighters XV — Ralf Jones Moveset Exhibition / Cykioh\nhttps://www.youtube.com/watch?v=fjEe1S7aNJs\n\nGuilty Gear Strive — Sol Badguy Full Command List and Gameplay / Chaos Productions Inc\nhttps://www.youtube.com/watch?v=Pe1CZN7txe8\n\nKirby Needle evolution (gameplay excerpt)\nhttps://www.youtube.com/watch?v=aNEUsTkLa5o\n\nBGM: Nimbus — Eveningland / YouTube Audio Library\n\nPublisher policies and separate recorder-rights review are recorded in the production ledger.\n',encoding='utf-8')
 manifest['captionedMasterSha256']=cap['sha256']
 manifest['metadataArtifacts']=[dict(ap.artifact(D/name),name=name) for name in ['index.html','README.md','sources.txt']]
 ap.save(D/'delivery-manifest.json',manifest)
 ledger={'episode':'A02','revision':'fighters-v2','status':'local-delivery-user-review-pending','updatedAt':stamp,'directory':ap.relative(D),'index':ap.relative(D/'index.html'),'captioned':cap,'files':files,'manifest':ap.artifact(D/'delivery-manifest.json'),'sourcePlan':ap.artifact(H/'edit-plan.json'),'qa':{'structure':ap.artifact(L/'edit/structural-verification.json'),'pixels':ap.artifact(H/'final-pixel-review.json'),'audio':ap.artifact(H/'final-audio-asr-review.json')},'humanFinalReview':False,'platformMutation':False,'baselinePreserved':manifest['baselinePreserved']}
 ap.save(H/'local-delivery-ledger.json',ledger);ap.save(H/'checkpoint.json',{'episode':'A02','revision':'fighters-v2','status':'local-delivery-user-review-pending','updatedAt':stamp,'localCaptionedMaster':cap['path'],'captionedMasterSha256':cap['sha256'],'durationSeconds':duration,'actualFootageShare':p['expectedGameplayShare'],'newVoiceSeconds':79.2333333333,'nextAction':'User reviews this exact local captioned master. No YouTube upload authorized for fighters-v2. Batch remainder authorization remains recorded separately.','baselinePreserved':True,'humanFinalReview':False})
 print(json.dumps({'directory':str(D),'sha256':cap['sha256'],'files':4},ensure_ascii=False))
if __name__=='__main__':main()
