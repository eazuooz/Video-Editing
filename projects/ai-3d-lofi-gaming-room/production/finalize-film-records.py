"""Truthful selected-project delivery records; no publication is performed."""
from pathlib import Path
import json,datetime,hashlib,zipfile,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];H=P/'production';L=H/'local/full-video-v2';W=H/'local/living-room-v8/webgl';F=L/'final'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();d=read(H/'full-video-delivery.json');assert d['stage']=='local-final-review-ready'
qa=read(H/'full-video-qa.json');assert qa['captionBoxAllCueCentersPassed']
web=read(H/'local/living-room-v8/web-build.json');assert web['result']=='Succeeded'
wiki=read(H/'companion-wiki.json');assert wiki['savedAndReadBack']
frames=read(H/'companion-frames.json')
assert len(frames)==wiki['imageBlocks']==7
assert all(f['masterSha256']==d['outputs'][1]['sha256'] and f['notionAttachmentId'] for f in frames),'Wiki images must match the current final master'
p=read(P/'project.json');p.update(status='local-final-review-ready',productionComplete=True,localMasterAvailable=True,humanReview='pending-full-final-review',websiteUrl=None,youtubeVideoId=None)
p['paths'].update(videoClean=d['outputs'][0]['path'],videoBurnedCaptions=d['outputs'][1]['path'],captionsKo=str(F/(P.name+'.ko.srt')),captionsEn=str(F/(P.name+'.en.srt')),fullVideoDelivery='projects/ai-3d-lofi-gaming-room/production/full-video-delivery.json',webGameBuild='projects/ai-3d-lofi-gaming-room/production/local/living-room-v8/webgl',wikiArticle=wiki['pageUrl'])
p['review']={'url':'http://127.0.0.1:9327/','gameUrl':'http://127.0.0.1:9326/','masterSha256':d['outputs'][1]['sha256'],'humanViewed':False,'wholeHumanListening':'pending','physicalMobileQa':False};save(P/'project.json',p)
plan=read(P/'planning/production-plan.json');plan['stage']='local-final-review-ready';plan['authorization']['immediatePriority']='Completed softer sitting, local browser build and full making-of video with companion wiki; user final review pending.';plan['authorization']['latestUserReplies']=['웹빌드 설치 추가했어 쭉 진행해서 영상제작까지 마무리','의자에 차분하게 앉도록 수정'];plan['game']['engine']['sceneTarget']='Assets/LofiRoom/Scenes/LofiFinalRoom.unity';plan['game']['platform'].update(webBuildComplete=True,currentReview='Full 1080p60 making-of and playable local WebGL room; user final review pending',publicUrl=None);plan['completion']={'video':d,'wiki':wiki,'updatedAtKst':now};save(P/'planning/production-plan.json',plan)
cp=read(H/'checkpoint.json');cp.update(status='local-final-review-ready',latestDelivery='production/full-video-delivery.json',reviewUrl='http://127.0.0.1:9327/',gameUrl='http://127.0.0.1:9326/',wiki=wiki,webBuildDeferred=False,youtubeUploaded=False,publicWebDeployment=False,humanReview=False,updatedAtKst=now);save(H/'checkpoint.json',cp)
ledger=read(H/'review-ledger.json');ledger['revisions']=[r for r in ledger.get('revisions',[]) if r.get('revision')!='living-room-v8-and-full-film-v2'];ledger['revisions'].append({'revision':'living-room-v8-and-full-film-v2','date':now,'technicalQa':True,'masterSha256':d['outputs'][1]['sha256'],'userViewed':False,'userListening':'pending','reviewUrl':'http://127.0.0.1:9327/','gameUrl':'http://127.0.0.1:9326/','wikiUrl':wiki['pageUrl']});save(H/'review-ledger.json',ledger)
for item in ledger['checks']:
 if item['id']=='final-video':item.update(status='local-final-review-ready',humanReviewed=False,fullListeningPerformed=False,outputHashes={Path(v['path']).name:v['sha256'] for v in d['outputs']},technicalQa='production/full-video-qa.json')
 if item['id']=='webgl-primary-platform':item.update(status='actual-web-build-and-browser-qa-complete',moduleExists=True,actualWebBuildOrBrowserPlaybackPerformed=True,evidence='production/web-browser-qa.json',dateKst=now)
 if item['id']=='source-capabilities':item['limits']='Candidate capabilities separated from actual Tripo/Unity/Codex execution. Paid Studio output and animation project-use sources reconciled in production/full-video-sources.json.'
save(H/'review-ledger.json',ledger)
archive=F/'yamyam-lofi-room-web-v8.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for f in W.rglob('*'):
  if f.is_file():z.write(f,'lofi-room/'+f.relative_to(W).as_posix())
 z.writestr('lofi-room/README.txt','Unity WebGL build. Serve this folder over HTTP; file:// does not support loading the WASM/data files. Local review: http://127.0.0.1:9326/\nNotes are stored only in the current browser and origin. No public deployment was performed.\n')
d.update(wiki=wiki,webBuild=web,webArchive={'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive)},technicalQa='production/full-video-qa.json',humanReview=False,updatedAtKst=now);save(H/'full-video-delivery.json',d)
publishing=P/'publishing';publishing.mkdir(exist_ok=True)
title='이 3D 방, AI로 만들었습니다 | Tripo·Unity로 LOFI 웹게임 완성하기'
save(publishing/'metadata.ko.json',{'title':title,'status':'prepared-local-review-only','youtubeUploaded':False,'publicGameUrl':None,'descriptionSourcesPosition':'absolute-bottom','thumbnail':'production/local/full-video-v2/final/thumbnail.png'})
sources='''사용 도구·자료\nimagegen — 자체 디자인 참고 이미지\nTripo Studio H3.1 — 캐릭터·헤드폰 생성, 정리와 리깅\nhttps://www.tripo3d.ai/product-doc/model-generation/image-to-3d\nUnity 6000.6 URP, Unity 공식 CLI/MCP, Codex, FFmpeg — 실제 구현·빌드·영상 제작\nhttps://docs.unity.com/en-us/engine/6000.6/manual/platform-specific/webgl/develop/input\nhttps://docs.unity.com/en-us/engine/6000.0/manual/platform-specific/webgl/develop/audio\n비교 후보: Meshy, ComfyUI + Hunyuan3D, Blockbench, Material Maker, Mixamo, DeepMotion\nhttps://docs.meshy.ai/en/webapp/image-to-3d\nhttps://github.com/Comfy-Org/ComfyUI\nhttps://github.com/Tencent-Hunyuan/Hunyuan3D-2\nhttps://www.blockbench.net/\nhttps://www.materialmaker.org/\nhttps://www.mixamo.com/\nhttps://www.deepmotion.com/\nKayKit Character Animations / Kay Lousberg, Free 1.1, CC0 1.0\nhttps://kaylousberg.itch.io/kaykit-character-animations\nPHILIPP / EmacEArt — licensed native reading motion, rendered project use; no source redistribution\nhttps://emaceart.itch.io/philipp-stylized-modular-low-poly-character\nMorning Coffee — HoliznaCC0, CC0 1.0\nFireplace Sound loop — PaGDev, CC0 1.0\nhttps://opengameart.org/content/fireplace-sound-loop\n'''
description='''AI로 만든 캐릭터와 소품을 실제 플레이 가능한 3D LOFI 방으로 연결했습니다.\nTripo 모델 정리와 PBR 텍스처, 자연스럽게 앉고 책을 읽는 동작, 숲과 달빛, 음악·장작 소리, 메모·집중 타이머까지 제작 과정을 따라갑니다.\n\n이 영상은 실제 적용한 도구와 같은 단계의 비교 후보를 구분해서 소개합니다.\n게임 공개 플레이 주소는 공개 웹 배포 후 추가할 예정입니다. 현재는 로컬 검수 단계입니다.\n\n제작 상세 글: '''+wiki['pageUrl']+'\n\n'+sources
(publishing/'description.ko.txt').write_text(description,'utf-8')
index=F/'index.html';page=index.read_text('utf-8').replace('https://app.notion.com/p/41b0b1ffa61e81f1a484f6c3e4b0555b',wiki['pageUrl']).replace('AI 게임 제작 위키','제작 상세 위키')
if 'href="yamyam-lofi-room-web-v8.zip"' not in page:page=page.replace('</p><p>사용자의 전체','<a href="yamyam-lofi-room-web-v8.zip">웹 빌드 ZIP</a></p><p>사용자의 전체')
index.write_text(page,'utf-8')
if 'v.scrollIntoView' not in page:page=page.replace('v.currentTime=+b.dataset.t;v.play()','v.currentTime=+b.dataset.t;v.play();v.scrollIntoView({block:"start",behavior:"smooth"})')
index.write_text(page,'utf-8')
print('Updated selected delivery, project, plan, review ledger and upload draft')
