"""Deliver the internally checked v2 master; private upload was explicitly requested."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];O=P/'production/local/final-gameplay-v2';A=P/'production/local/audio'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(R).as_posix()
now=datetime.now(timezone.utc).isoformat();b=read(O/'build.json');integrity=read(O/'integrity.json');asr=read(O/'mix-asr.json');head=read(O/'header-integrity.json')
existing=read(P/'publishing/youtube-upload.json')
assert existing.get('revision')!='flow-map-gameplay-v2' or existing.get('status')=='prepared-not-uploaded', 'Do not overwrite a started/completed platform receipt.'
assert integrity['status']==head['status']=='pass' and asr['inputSha256']==b['captionedSha256']==sha(O/'captioned.mp4')
assert asr['similarity']>=.97 and asr['voiceSha256']==b['voiceSha256']
assert len(read(P/'script/captions.json')['cues'])==24
master=dict(path=rel(O/'captioned.mp4'),sha256=b['captionedSha256'])
out=R/'output'/P.name/'gameplay-v2';out.mkdir(parents=True,exist_ok=True);files=[]
for source,name in [(O/'captioned.mp4',P.name+'.captioned.mp4'),(O/'clean.mp4',P.name+'.clean.mp4'),(A/'captions.ko.srt',P.name+'.ko.srt'),(A/'captions.en.srt',P.name+'.en.srt')]:
 dest=out/name
 if dest.exists():assert sha(dest)==sha(source)
 else:shutil.copyfile(source,dest)
 files.append(dict(name=name,source=rel(source),bytes=dest.stat().st_size,sha256=sha(dest)))
html='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>플로 맵 · 실제 게임 추가본</title><style>body{background:#151a17;color:white;font:17px sans-serif;margin:24px}a{color:#ffd25a}video{width:375px;max-width:100%}</style><h1>플로 맵 · 실제 게임 추가본</h1><p>51초 · 1080×1920 · 60fps</p><video controls src="'+P.name+'.captioned.mp4"></video><ul>'+''.join('<li><a href="'+f['name']+'">'+f['name']+'</a></li>' for f in files)+'</ul><p>실제 게임 두 구간8.62초 · 기존 설명과 음성 유지</p></html>'
(out/'index.html').write_text(html,encoding='utf-8')
delivery=dict(directory=rel(out),captioned=rel(out/(P.name+'.captioned.mp4')),index=rel(out/'index.html'))
save(P/'production/delivery-output.json',dict(slug=P.name,revision='flow-map-gameplay-v2',createdAt=now,**delivery,previousDeliveryDirectory='output/'+P.name,publishReady=False,files=files,cues=24,captionAlignment='unchanged24KO/ENcueTiming',video=dict(width=1080,height=1920,fps=60,frames=3067,durationSeconds=3067/60)))
m=read(P/'project.json');m.update(status='ready-for-authorized-private-replacement-upload',currentRevision='flow-map-gameplay-v2',updatedAt=now,delivery=delivery)
m['paths'].update(videoClean=rel(O/'clean.mp4'),videoBurnedCaptions=master['path'],audioMix=rel(O/'final-mix.m4a'))
m['finalRender']=dict(revision=m['currentRevision'],sha256=master['sha256'],technicalChecks='passed',knownIssues=[],openItems=['Modified master has no separate human whole-video review claim; user explicitly requested this revision and re-upload.','Replacement private upload and action-time old-video deletion confirmation pending.'])
m['uploadReview']=dict(status='explicit-revision-and-reupload-authorized',evidence='실제 게임영상도 넣어서 만들어줘 기존꺼 업로드 삭제하고 다시 업로드해줘',scope='V2 private replacement only; no public/schedule/next video',humanViewingOfV2='not-claimed',masterSha256=master['sha256'])
save(P/'project.json',m)
cp=read(P/'production/checkpoint.json');cp.update(stage='ready-for-authorized-private-replacement-upload',updatedAt=now,finalMaster=master,delivery=delivery,technicalChecks='passed',humanFinalReview='v2-not-separately-viewed;revision-and-reupload-explicitly-requested',nextAction='Upload v2 privately, verify settings and1080p60; then request action-time confirmation to permanently delete old9cRdnf8wKEI.')
cp['baselineV1']=m['baselineV1'];cp['youtubeUploadAuthorization']=m['uploadReview'];cp['uploadReview']=m['uploadReview'];save(P/'production/checkpoint.json',cp)
plan=read(P/'planning/production-plan.json');plan.update(status='internally-reviewed-ready-for-requested-private-upload',finalMaster=master,humanFinalReview='not-claimed-for-v2',platformActionsAuthorized='Explicit user request for v2 private reupload; old deletion action-time confirmation pending');save(P/'planning/production-plan.json',plan)
ledger=dict(slug=P.name,revision='flow-map-gameplay-v2',updatedAt=now,masterSha256=master['sha256'],baselineV1=m['baselineV1'],checks=[dict(id='source-and-rights',status='pass',evidence=rel(P/'sources/sources.json'),summary='Valve technique source and video policy; SCuprikovCCBY native1920x1080 recording. Original aspect and speed.'),dict(id='video-integrity',status='pass',evidence=rel(O/'integrity.json')),dict(id='fixed-header-all-frames',status='pass',evidence=rel(O/'header-integrity.json')),dict(id='unchanged-voice-and-caption-input',status='pass',voiceSha256=b['voiceSha256'],cueCount=24),dict(id='changed-mix-unprompted-asr',status='technical-pass',evidence=rel(O/'mix-asr.json'),similarity=asr['similarity'],note='RawASR retained; spacing/particles/쉐이더/되감돼 differ, same approvedvoicePCM. No omitted sentence detected; not a human-listening claim.'),dict(id='changed-mix-headroom',status='pass',evidence=rel(O/'audio-stats.log'),peakDbFS=-2.692260,nan=0,inf=0),dict(id='mobile-native-and-transition-review',status='pass',evidence=rel(O/'qa'),summary='Nativeframes and375pxsheet, full browser playback and changedjoins. Header repaired, contours absent during enemy/boat occlusion, no captions/target collision; game labels not credits.'),dict(id='human-final-review',status='not-claimed-for-modified-v2',evidence=m['uploadReview']['evidence'])],platform=dict(youtube='replacement-upload-pending',oldVideoId='9cRdnf8wKEI',drive='v1-preserved;not-requested-for-v2',automaticNextVideo=False))
save(P/'production/review-ledger.json',ledger)
prior=read(P/'publishing/youtube-upload.flow-map-v1.json')
receipt=dict(schemaVersion=1,slug=P.name,revision='flow-map-gameplay-v2',status='prepared-not-uploaded',preparedAt=now,authorization=m['uploadReview'],video=dict(path=delivery['captioned'],sha256=master['sha256'],bytes=(O/'captioned.mp4').stat().st_size,seconds=3067/60,width=1080,height=1920,fps=60,frames=3067),metadata={**prior['metadata'],'description':(P/'publishing/upload-description.ko.txt').read_text(encoding='utf-8'),'tags':prior['metadata']['tags']+['레프트4데드2','Left 4 Dead 2']},englishMetadata=dict(title=m['titles']['en'],description=(P/'publishing/upload-description.en.txt').read_text(encoding='utf-8')),playlist=dict(id='PLWKwcHKTXy5SKMSjoO1c7kdk5oK55M_8o',name='도움이 되는 게임 개발 이야기'),captions=dict(ko=rel(A/'captions.ko.srt'),en=rel(A/'captions.en.srt')),replacement=dict(oldVideoId='9cRdnf8wKEI',oldReceipt=rel(P/'publishing/youtube-upload.flow-map-v1.json'),deletion='awaiting-action-time-confirmation-after-new-upload'),sourceCredits=dict(position='description-bottom',recording='SCuprikovCCBY',publisher='ValvevideoPolicy',changesDisclosed=True),platformChecks='pending')
save(P/'publishing/youtube-upload.json',receipt)
wpath=R/'shared/publishing/shorts-worklist.json';w=read(wpath);matches=[]
def visit(x):
 if isinstance(x,list):
  for y in x:visit(y)
 elif isinstance(x,dict):
  if x.get('slug')==P.name and 'title' in x:matches.append(x)
  else:
   for y in x.values():visit(y)
visit(w);assert len(matches)==1
matches[0].update(status=m['status'],revision=m['currentRevision'],production='Complete51.1167s1080x1920/60;L4D2actual8.6167s+Unity/MC;voicepreserved',review='internalQApass;explicitv2reuploadrequest;humanv2viewingnotclaimed',finalMaster=master,delivery=delivery)
w['updatedAt']=now;save(wpath,w)
print(json.dumps(dict(master=master,delivery=delivery),ensure_ascii=False))
