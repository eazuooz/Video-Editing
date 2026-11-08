"""Finish this revision's handoff only; global ledgers and Git belong to root."""
from pathlib import Path
import json,datetime,shutil
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v4-video'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(n,v):(H/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
d=read(H/'delivery.json');tm=read(L/'timeline.json');auth=read(H/'authorization.json');master=d['files'][0];base=read(H.parent/'room-v3/checkpoint.json');now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
pub=P/'publishing/room-v3-upload-20261108';oldchap=read(pub/'chapters.json')['chapters'];byid={s['id']:s for s in tm['scenes']};chap=[]
for row in oldchap:
 if row['sceneId']=='R30':chap.append({'sceneId':'W36','seconds':int(byid['W36']['start']),'ko':'화면 안 메모와 브라우저 저장','en':'On-screen notes and browser-local saving'})
 r={k:v for k,v in row.items() if k in ['sceneId','ko','en']};r['seconds']=0 if row['sceneId']=='01' else int(byid[row['sceneId']]['start']);chap.append(r)
for c in chap:c['timestamp']=f"{c['seconds']//60:02d}:{c['seconds']%60:02d}"
save('chapters.json',{'source':'current room-v4-video timeline','duration':tm['duration'],'chapters':chap})
for lang in ['ko','en']:
 text=(pub/f'description.{lang}.txt').read_text('utf8');oldtext=(pub/f'chapters.{lang}.txt').read_text('utf8').rstrip();newtext='\n'.join(f"{c['timestamp']} {c[lang]}" for c in chap);assert oldtext in text;text=text.replace(oldtext,newtext)
 text=text.replace('공개 웹 버전에는 영상 제작 후 개선한 책상·라디오 UI·메모 기능도 반영했습니다.','영상과 공개 웹 게임 모두 전경 중앙 책상, 화면 안 라디오와 메모 기능을 반영했습니다.').replace('The live site also includes later desk, radio-UI and memo improvements.','Both the video and live game show the foreground desk, in-stage radio and memo features.')
 assert len(text)<5000;(H/f'description.{lang}.txt').write_text(text,'utf8');shutil.copy2(H/f'description.{lang}.txt',Path(d['directory'])/f'description.{lang}.txt')
paths={r['name']:r['path'] for r in d['files']}
patch={'applyBy':'root; no shared/project files changed by this helper','project':'projects/ai-2d-game-assets/project.json','preserveAllUnlistedKeys':True,'set':{'status':'local-final-review','video.durationSeconds':d['duration'],'delivery':{'directory':d['directory'],'reviewUrl':d['reviewUrl'],'revision':'room-v4-video','masterSha256':master['sha256']},'currentRevision':{'id':'room-v4-video','plan':(H/'revision-plan.json').relative_to(R).as_posix(),'checkpoint':(H/'checkpoint.json').relative_to(R).as_posix(),'sourceSnapshot':(H/'source-snapshot.json').relative_to(R).as_posix(),'siteVersion':6,'siteCommit':auth['siteCommit'],'humanReview':'pending','youtubeUploaded':False},'paths.videoBurnedCaptions':paths['ai-2d-game-assets.captioned.mp4'],'paths.videoClean':paths['ai-2d-game-assets.clean.mp4'],'paths.captionsKo':paths['ai-2d-game-assets.ko.srt'],'paths.captionsEn':paths['ai-2d-game-assets.en.srt'],'paths.audioMix':'C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video/final-mix.m4a','paths.audioReport':(H/'audio-qa.json').relative_to(R).as_posix(),'paths.sceneRenderer':(H/'render-scenes.cjs').relative_to(R).as_posix()},'reviewLedgerSuggestedEntry':{'revision':'room-v4-video','masterSha256':master['sha256'],'status':'local-final-review-user-pending','evidence':[(H/x).relative_to(R).as_posix() for x in ['final-review.json','technical-qa.json','version-coherence.json','delivery-http-qa.json','delivery.json']],'humanReview':False,'wholeListening':False},'preserveHistory':{'previousMasterSha256':auth['baselineMasterSha256'],'obsoletePrivateYouTubeId':'t7Li-IzqJyk','websiteSourceUnchanged':auth['siteCommit']}}
save('metadata-patch-spec.json',patch)
save('checkpoint.json',{'updatedAt':now,'stage':'local-final-review-ready','revision':'room-v4-video','siteVersion':6,'siteCommit':auth['siteCommit'],'durationSeconds':d['duration'],'frames':tm['frames'],'sceneCount':52,'masterSha256':master['sha256'],'delivery':d,'completed':['19 changed visuals plus1new memo scene','51 previous PCM sample ranges preserved exactly','new source and finalAAC independentASR meaning matched','wholefinaldecode; identicalAAC clean/captioned','40 changed encoded samples and6mobile375 samples visually inspected','HTTP200 andMP4Range206'],'next':'Root actualbrowserplayback evidence and selective bookkeeping; user review of this new exact master','humanReview':False,'wholeActualListening':False,'youtubeAuthorizedNow':False,'oldUploadPreserved':'t7Li-IzqJyk'})
(H/'README.md').write_text(f'''# AI 2D 게임 · 공개 v6 영상 반영

검수: {d['reviewUrl']}
공개 게임: {d['playableUrl']}
완성본: `{master['path']}`
SHA256: `{master['sha256']}`

1920×1080, 60fps, 75,289프레임, 20분54.817초. `delivery.json`에 자막 포함/없는 MP4와 KO/EN SRT 네 파일 경로·해시가 있습니다.

이번에는 기존 영상의 최신 게임 화면 불일치를 수정했습니다. 전경 중앙의 독립 나무 책상, 다리 앞 책상 부재와 상판 위 손·장부, 현재 촛불 위치, 화면 안 라디오, 500자 브라우저 메모를 반영했습니다. 19개 기존 시각 장면을 교체하고 메모 설명1장면을 추가했습니다. 기존51문단 최종 PCM 샘플은 삽입 앞뒤가 정확히 동일합니다. 총52장면입니다.

게임 시연은 공개 v6 소스 `{auth['siteCommit']}`의 동결 사본을 실행했습니다. `source-snapshot.json`은 게임·에셋별 해시, `version-coherence.json`은 교체20장면 및 배경/책상 정합성을 기록합니다. 원화·PixelOE 초안 등 과거 입력은 실제 제작 과정으로 명시하고 보존했습니다. 완성 게임이라고 제시하는 화면은 새판입니다. 사이트 자체는 수정하지 않았습니다.

연속 게임 화면은 실제 game.js의 Canvas 실행을1920×1080/60fps로 인코딩했습니다. 라디오·메모는 root가 공개 웹사이트에서 조작해 확보한 실제 브라우저 스크린샷이며, 영상 녹화/FHD 원본이라고 주장하지 않습니다. 실제 파일 형식·치수·해시는 `browser-evidence.json`에 있습니다.

실제 실행 도구7개(2dimg2motion, sprite-gen, pixelfx, PixelOE, Agent Sprite Forge, Codixel, Pixelbolt), 이미지 생성과 ComfyUI 비교를 보존했습니다. Sprite-Sheet-Diffusion은 실제 설치검증 후 공식 필수 가중치 누락으로 추론 재현 미완료라는 기존 설명을 유지했습니다. 캐릭터LoRA 학습이나 소개만 한 대안의 실사용을 주장하지 않습니다. 최신도구/출처목록과 게임 링크는 설명 파일에 포함했고 출처가 맨 아래입니다.

검증: 최종 전체 디코드, 크기/fps/길이/프레임수, 동일AAC, 기존 PCM 보존, 추가문단 raw/최종AAC 독립ASR 대조, 변경20장면 인코딩40표본 및6개375px표본 확인. 전체 실시간 시청·음성청취나 새 버전의 사용자 승인은 미완료입니다.

기존 room-v3 검수본과 비공개 YouTube `t7Li-IzqJyk`는 보존했습니다. 새 영상 업로드·삭제·공개·예약은 하지 않았습니다. project/shared ledgers/Git 변경은 root가 `metadata-patch-spec.json`과 정확한 변경목록을 이용해 수행합니다.
''','utf8')
files=sorted(f.relative_to(R).as_posix() for f in H.iterdir() if f.is_file() and f.name!='changed-files.json')
files.append((H/'changed-files.json').relative_to(R).as_posix())
save('changed-files.json',{'writeComplete':True,'ownedSourceAndMetadata':files,'rootOwnedIncludedForCommit':['production/room-v4-video/authorization.json'],'sharedFilesModified':[],'excluded':['production/local/room-v4-video/**','C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/**','sites/**'],'projectMetadataApplied':False,'gitActionPerformed':False})
print('Handoff complete',len(files),'source/metadata files')
