"""Truthful selected-project delivery records; no publication is performed."""
from pathlib import Path
import json,datetime,hashlib,zipfile,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];H=P/'production';L=H/'local/full-video-v5';W=H/'local/living-room-v11/webgl';F=L/'final'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();d=read(H/'full-video-delivery.json');assert d['stage']=='local-final-review-ready'
reuse=read(H/'tutorial-v5-voice-reuse.json');reuse['actuallyUnchangedPcm']=[];reuse['existingTextRegeneratedForEndingQuality']=[]
for scene in reuse['reusedExactTextScenePcm']:
 old=H/'local/full-video-v4/narration/chunks'/(scene+'-scene.wav');new=L/'narration/chunks'/(scene+'-scene.wav')
 reuse['actuallyUnchangedPcm' if sha(old)==sha(new) else 'existingTextRegeneratedForEndingQuality'].append(scene)
save(H/'tutorial-v5-voice-reuse.json',reuse)
qa=read(H/'full-video-qa.json');assert qa['captionBoxAllCueCentersPassed']
web=read(H/'local/living-room-v11/web-build.json');assert web['result']=='Succeeded'
wiki=read(H/'companion-wiki.json');assert wiki['savedAndReadBack']
frames=read(H/'companion-frames.json')
assert len(frames)==wiki['imageBlocks']==12
assert wiki['homepageVerified'] and wiki['publicUrl'].startswith('https://www.yamyamcoding.com/')
assert all(f['masterSha256']==d['outputs'][1]['sha256'] and f['notionAttachmentId'] for f in frames),'Wiki images must match the current final master'
p=read(P/'project.json');p.update(status='local-final-review-ready',productionComplete=True,localMasterAvailable=True,humanReview='pending-full-final-review',websiteUrl=None,youtubeVideoId=None)
p['paths'].update(videoClean=d['outputs'][0]['path'],videoBurnedCaptions=d['outputs'][1]['path'],captionsKo=str(F/(P.name+'.ko.srt')),captionsEn=str(F/(P.name+'.en.srt')),narration=str(L/'narration-aligned.wav'),audioMix=str(L/'final-mix.wav'),audioReport='projects/ai-3d-lofi-gaming-room/production/full-video-audio-qa.json',fullVideoDelivery='projects/ai-3d-lofi-gaming-room/production/full-video-delivery.json',webGameBuild='projects/ai-3d-lofi-gaming-room/production/local/living-room-v11/webgl',wikiArticle=wiki['publicUrl'])
p['review']={'url':'http://127.0.0.1:9329/','gameUrl':'http://127.0.0.1:9324/','masterSha256':d['outputs'][1]['sha256'],'humanViewed':False,'wholeHumanListening':'pending','physicalMobileQa':False};save(P/'project.json',p)
plan=read(P/'planning/production-plan.json');plan['stage']='local-final-review-ready';plan['authorization']['immediatePriority']='Natural calico coat and fitted book/wrist/elbow contact. Reproducible AI-tool tutorial, 19 requests and corresponding homepage wiki; user final review pending.';plan['authorization']['latestUserReplies']=['고양이 텍스처를 자연스럽게','누워 책 볼 때 팔과 책 겹침 수정','개발과정 기록 대신 AI 모델로 같은 게임 만드는법 공유','도구별 입력·요청문·설정·결과'];plan['game']['engine']['sceneTarget']='Assets/LofiRoom/Scenes/LofiRattanRoomV11.unity';plan['game']['platform'].update(webBuildComplete=True,currentReview='Full 1080p60 AI-tool recreation tutorial and playable local WebGL room; user final review pending',publicUrl=None);plan['completion']={'video':d,'wiki':wiki,'updatedAtKst':now};save(P/'planning/production-plan.json',plan)
cp=read(H/'checkpoint.json');cp.update(productionComplete=True,blockers=[],pending=['User whole final video review and listening before any new upload or public game deployment'],nextAction='User whole final review of this exact new master; preserve mobile review deferral and existing platform boundaries.',status='local-final-review-ready',latestDelivery='production/full-video-delivery.json',reviewUrl='http://127.0.0.1:9329/',gameUrl='http://127.0.0.1:9324/',wiki=wiki,webBuildDeferred=False,youtubeUploaded=False,publicWebDeployment=False,humanReview=False,updatedAtKst=now);cp.get('rattanV11',{}).update(targetFullFilmRendered=True,currentFinalFilmStill='full-video-v5');save(H/'checkpoint.json',cp)
ledger=read(H/'review-ledger.json');ledger['revisions']=[r for r in ledger.get('revisions',[]) if r.get('revision')!='living-room-v11-and-tutorial-v5'];ledger['revisions'].append({'revision':'living-room-v11-and-tutorial-v5','date':now,'technicalQa':True,'masterSha256':d['outputs'][1]['sha256'],'userViewed':False,'userListening':'pending','reviewUrl':'http://127.0.0.1:9329/','gameUrl':'http://127.0.0.1:9324/','wikiUrl':wiki['publicUrl']});save(H/'review-ledger.json',ledger)
for item in ledger['checks']:
 if item['id']=='final-video':item.update(status='local-final-review-ready',humanReviewed=False,fullListeningPerformed=False,outputHashes={Path(v['path']).name:v['sha256'] for v in d['outputs']},technicalQa='production/full-video-qa.json')
 if item['id']=='webgl-primary-platform':item.update(status='actual-web-build-and-browser-qa-complete',moduleExists=True,actualWebBuildOrBrowserPlaybackPerformed=True,evidence='production/web-browser-qa.json',dateKst=now)
 if item['id']=='source-capabilities':item['limits']='Candidate capabilities separated from actual Tripo/Unity/Codex execution. Paid Studio output and animation project-use sources reconciled in production/full-video-sources.json.'
save(H/'review-ledger.json',ledger)
archive=F/'yamyam-lofi-room-web-v11.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for f in W.rglob('*'):
  if f.is_file():z.write(f,'lofi-room/'+f.relative_to(W).as_posix())
 z.writestr('lofi-room/README.txt','Unity WebGL build. Serve this folder over HTTP; file:// does not support loading the WASM/data files. Local review: http://127.0.0.1:9324/\nNotes are stored only in the current browser and origin. No public deployment was performed.\n')
d.update(wiki=wiki,webBuild=web,webArchive={'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive)},technicalQa='production/full-video-qa.json',humanReview=False,updatedAtKst=now);save(H/'full-video-delivery.json',d)
publishing=P/'publishing';publishing.mkdir(exist_ok=True)
title='AI로 3D 게임 만드는 법 | 이미지·Tripo·Codex·Unity로 LOFI 방 완성'
save(publishing/'metadata.ko.json',{'title':title,'status':'prepared-local-review-only','youtubeUploaded':False,'publicGameUrl':None,'descriptionSourcesPosition':'absolute-bottom','thumbnail':'production/local/full-video-v5/final/thumbnail.png'})
sources='''사용 도구·자료\nQwen3-TTS 12Hz 1.7B Base — 로컬 내레이션, 사용자 음성 레퍼런스\nhttps://github.com/QwenLM/Qwen3-TTS\n\nimagegen — 자체 디자인 참고 이미지\nTripo Studio H3.1 — 캐릭터·헤드폰 생성·리깅, 사진 기준 삼색고양이 생성·정리\nhttps://www.tripo3d.ai/product-doc/model-generation/image-to-3d\nUnity 6000.6 URP, Unity 공식 CLI/MCP, Codex, FFmpeg — 실제 구현·빌드·영상 제작\nhttps://docs.unity.com/en-us/engine/6000.6/manual/platform-specific/webgl/develop/input\nhttps://docs.unity.com/en-us/engine/6000.0/manual/platform-specific/webgl/develop/audio\n비교 후보: Meshy, ComfyUI + Hunyuan3D, Blockbench, Material Maker, Mixamo, DeepMotion\nhttps://docs.meshy.ai/en/webapp/image-to-3d\nhttps://github.com/Comfy-Org/ComfyUI\nhttps://github.com/Tencent-Hunyuan/Hunyuan3D-2\nhttps://www.blockbench.net/\nhttps://www.materialmaker.org/\nhttps://www.mixamo.com/\nhttps://www.deepmotion.com/\nKayKit Character Animations / Kay Lousberg, Free 1.1, CC0 1.0\nhttps://kaylousberg.itch.io/kaykit-character-animations\nPHILIPP / EmacEArt — initial desk-reading motion; sofa uses PHILIPP reclining body and reading arms, KayKit sit and stand; no source redistribution\nhttps://emaceart.itch.io/philipp-stylized-modular-low-poly-character\nTripo Studio H3.1 — original wood/rattan sofa and coffee table, 180 generation/retopology credits; 4K export
Calico Cat Asleep / Am9489 — CC0 1.0, image-AI-cleaned derivative used as Tripo input
https://commons.wikimedia.org/wiki/File:Calico_Cat_Asleep.jpg
Morning Coffee, Glad To Be Stuck Inside, Laundry On The Wire, A Little Shade, Keeping Cool, Come Again, Windows Down, Waves, Something In the Air, Everything You Ever Dreamed — HoliznaCC0, CC0 1.0\nhttps://opengameart.org/content/lo-fi-and-chill-collection\nhttps://creativecommons.org/publicdomain/zero/1.0/\nFireplace Sound loop — PaGDev, CC0 1.0\nhttps://opengameart.org/content/fireplace-sound-loop\n'''
timeline=read(L/'timeline.json')
chapterRows=[(0,'AI로 같은 방을 만드는 세 단계')]+[(s['start'],s['title']) for s in timeline['scenes'] if s['id'] in {'03','05','06','08','10','13','15','17','18','19','20','29','21','22','30','23','24','25','26','31','28'}]
chapters='챕터\n'+'\n'.join(f'{int(t)//60:02d}:{int(t)%60:02d} {label}' for t,label in chapterRows)
defaults=read(R/'shared/publishing/youtube-defaults.json')
footer=(R/defaults['description']['channelDefaultSnapshot']).read_text('utf-8').split('📚 수업 노트')[0].strip()
intro='이미지 생성부터 Tripo의 3D 모델·텍스처·리깅, Codex 요청과 Unity 구현까지 연결해 같은 LOFI 웹게임을 만드는 방법을 설명합니다. 입력 이미지, 요청문, 설정과 다음 도구로 넘길 결과를 실제 게임 화면과 함께 봅니다. 걷기·앉기·소파 독서, 숲과 비, 잠자는 삼색고양이, 음악·메모·집중 타이머를 차례로 연결합니다. 전체 요청문과 확인 기준은 아래 위키에 정리했습니다.'
description='\n\n'.join([intro,'제작 상세 글 · 얌얌위키\n'+wiki['publicUrl'],'게임은 현재 로컬 최종 검수 단계입니다. 공개 플레이 주소는 공개 웹 배포 후 추가합니다.',chapters,footer,sources])
assert len(description)<=5000 and description.endswith(sources)
(publishing/'description.ko.txt').write_text(description,'utf-8')
enTitle='How to Build a 3D LOFI Game with AI | Images, Tripo, Codex and Unity'
enTitles={r['id']:r['title'] for r in read(P/'script/narration.en.json')['scenes']}
enChapters='Chapters\n00:00 Three steps from an image to a playable room\n'+'\n'.join(f'{int(s["start"])//60:02d}:{int(s["start"])%60:02d} {enTitles[s["id"]]}' for s in timeline['scenes'] if s['id'] in {'03','05','06','08','10','25','13','15','18','20','22','30','23','26','28'})
enSources=sources.replace('사용 도구·자료','Tools, assets and sources').replace('비교 후보:','Alternatives discussed:').replace('자체 디자인 참고 이미지','original design reference images').replace('캐릭터·헤드폰 생성, 정리와 리깅','character/headphone generation, retopology and rigging').replace('실제 구현·빌드·영상 제작','implementation, builds and video production').replace('Unity 공식 CLI/MCP','Unity CLI/MCP')
enDescription='\n\n'.join(['Build the same playable LOFI room with AI: prepare image inputs, generate and retopologize models in Tripo, then use Codex and Unity to connect walking, reading, music, weather, notes and a focus timer. The tutorial shows requests, settings, outputs and handoffs. Four tools form the demonstrated route; six alternatives are discussed separately.','Detailed guide and reproducible requests\n'+wiki['publicUrl'],'The game is currently in local final review. A public play link will be added after public deployment.',enChapters,footer,enSources])
assert len(enDescription)<=5000 and enDescription.endswith(enSources)
(publishing/'description.en.txt').write_text(enDescription,'utf-8')
save(publishing/'metadata.en.json',{'title':enTitle,'status':'prepared-local-review-only','youtubeUploaded':False,'descriptionSourcesPosition':'absolute-bottom'})

index=F/'index.html';page=index.read_text('utf-8').replace('https://app.notion.com/p/41b0b1ffa61e81f1a484f6c3e4b0555b',wiki['publicUrl']).replace('AI 게임 제작 위키','제작 상세 위키')
if 'href="yamyam-lofi-room-web-v11.zip"' not in page:page=page.replace('</p><p>사용자의 전체','<a href="yamyam-lofi-room-web-v11.zip">웹 빌드 ZIP</a></p><p>사용자의 전체')
index.write_text(page,'utf-8')
if 'v.scrollIntoView' not in page:page=page.replace('v.currentTime=+b.dataset.t;v.play()','v.currentTime=+b.dataset.t;v.play();v.scrollIntoView({block:"start",behavior:"smooth"})')
index.write_text(page,'utf-8')
print('Updated selected delivery, project, plan, review ledger and upload draft')
