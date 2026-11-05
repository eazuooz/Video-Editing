"""Promote only a decoded, audio-checked news master into its own local review directory."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,html,shutil,subprocess
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/newsroom-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
v=read(L/'encoded-verification.json');a=read(L/'encoded-audio-readback.json');cuts=read(L/'news-cut-ledger.json')
plan=read(L/'timeline.json');aud=read(L/'encoded-level-continuity.json')
assert a['complete'] and len(a['scenes'])==8 and a['aacContainerSha256']==aud['aacSha256']==sha(L/'audio.m4a')
assert cuts['timelineSha256']==sha(L/'timeline.json') and v['masters']['captioned']['sha256']==sha(L/'captioned.mp4')
assert all('문을' not in c['ko'] and 'door' not in c['en'].lower() for c in read(L/'cue-review.json'))
assert sha(L/'clean.mp4')==v['masters']['clean']['sha256']
title='블루프린트가 사라지면 언리얼을 왜 쓸까? | 언리얼 6·고도·유니티 비교'
project=read(P/'project.json');manifest=read(H/'tts-manifest.json')
project.update(revision='newsroom-v3',title=title,status='local-delivery-user-review-pending',tts=manifest['tts'],delivery=manifest['delivery'],narrationSources=[{'scenes':'01–08','folder':rel(L/'voice/chunks'),'ttsManifest':rel(H/'tts-manifest.json')}])
project['paths'].update(script=rel(H/'narration.spoken-ko.json'),scriptKo=rel(H/'narration.ko.json'),scriptEn=rel(H/'narration.en.json'),narrationScriptReview=rel(H/'caption-pairs.txt'),videoClean=rel(L/'clean.mp4'),videoBurnedCaptions=rel(L/'captioned.mp4'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt'),timeline=rel(H/'final-timeline.json'),audioMix=rel(L/'final-mix.wav'),narration=rel(L/'voice/narration.wav'))
project['finalRender']={'status':'local-final-review','openItems':['새 버전 사용자 최종 시청·청취 대기']}
save(P/'project.json',project);shutil.copyfile(L/'timeline.json',H/'final-timeline.json')
subprocess.run(['node','scripts/collect-video-output.cjs',P.name],cwd=R,check=True)
directory=L/'delivery/output'/P.name
shutil.copyfile(H/'sources.txt',directory/'sources.txt')
index=directory/'index.html';page=index.read_text(encoding='utf-8')
anchors=' · '.join(f'<a href="{P.name}.captioned.mp4#t={2+s["startFrame"]/60:.3f}">{html.escape(s["title"])}</a>' for s in plan['scenes'])
index.write_text(page.replace('</h1>','</h1><p>'+anchors+'</p>',1)+'<p><a href="sources.txt">영상·기사·음악 출처</a></p>',encoding='utf-8')
report=read(P/'production/delivery-output.json')
assert all(sha(directory/f['name'])==f['sha256'] for f in report['files'])
shutil.copyfile(L/'news-cut-ledger.json',H/'final-cut-ledger.json')
summary={'episode':P.name,'revision':'newsroom-v3','title':title,'status':'local-delivery-user-review-pending','createdAt':datetime.now(timezone.utc).isoformat(),'directory':rel(directory),'reviewIndex':rel(index),'captioned':rel(directory/(P.name+'.captioned.mp4')),'masterSha256':v['masters']['captioned']['sha256'],'files':report['files'],'totalFrames':plan['totalFrames'],'durationSeconds':v['seconds'],'format':'1920x1080 60fps','bilingualCueCount':v['allCuePixelSamples'],'sourceFilmShareInBody':round(cuts['sourceFilmFrames']/cuts['bodyFrames'],4),'articleOrDocumentRemainder':True,'editorialScope':'Report on Epic with source-timed Blueprint/PIE, dated Chicago stage, November Tokyo reporting, Scene Graph, UE5.8 MCP and current terms for three engines. No door example.','filmSources':cuts['sources'],'descriptionSources':rel(H/'sources.txt'),'editDecisionList':rel(H/'final-cut-ledger.json'),'audioChecks':{'allSceneSourceAsrBoundToExactPCM':len(plan['sealedPrimaryTakes']),'encodedReadbackComplete':a['complete'],'encodedAudioSha256':a['aacContainerSha256'],'integratedLufs':v['audioMeasurement']['input_i'],'peakDbtp':v['audioMeasurement']['input_tp'],'levelContinuity':rel(L/'encoded-level-continuity.json')},'bothMastersDecode':True,'userReviewedThisHash':False,'wholeHumanListening':False,'platformMutation':False}
save(P/'production/checkpoint.json',summary)
print(json.dumps({k:summary[k] for k in ['durationSeconds','captioned','masterSha256','sourceFilmShareInBody']},ensure_ascii=False))
