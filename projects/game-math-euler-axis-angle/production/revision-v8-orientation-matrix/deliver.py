"""Collect the four reviewed local artifacts; never mutates a platform."""
from pathlib import Path
import importlib.util,json,subprocess,html,datetime
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_delivery_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
SLUG='game-math-orientation-matrix'
def main():
 c.authorized();timeline=c.read(H/'timeline.json');qa=c.read(c.O/'qa/quality-review.json');master=c.read(c.O/'edit/master-build.json');captioned=next(x for x in master['outputs']if x['kind']=='captioned')
 assert qa['masterSha256']==captioned['sha256'] and qa['technicalStatus']=='passed'
 decode=c.read(c.O/'qa/decode-clock.json');assert decode['allExact'];assert qa['humanFinalReview']=='pending'
 assert master['timelineSha256']==c.sha(H/'timeline.json') and master['mixSha256']==c.sha(c.O/'mix/final-mix.m4a')
 visual=c.read(c.O/'edit/visual-build.json');assert visual['timelineSha256']==c.sha(H/'timeline.json') and visual['editPlanSha256']==c.sha(H/'edit-plan.json')
 for kind in ['clean','captioned']:
  file=c.O/('orientation-matrix.'+kind+'.mp4');actual=c.sha(file);record=next(x for x in master['outputs']if x['kind']==kind)
  assert record['file']==c.rel(file) and record['sha256']==actual
  evidence=next(x for x in decode['results']if x['file']==c.rel(file));assert evidence['sha256']==actual and evidence['exactFrameClock'] and evidence['frames']==timeline['totalFrames']
 title='게임은 물체의 기울기를 어떻게 기억할까? — 자세와 회전행렬'
 project=c.R/'projects'/SLUG;folder=c.R/'output'/SLUG;files=[]
 sources=[('clean',SLUG+'.clean.mp4',c.O/'orientation-matrix.clean.mp4'),('captioned',SLUG+'.captioned.mp4',c.O/'orientation-matrix.captioned.mp4'),('ko',SLUG+'.ko.srt',c.O/'captions/full/captions.ko.srt'),('en',SLUG+'.en.srt',c.O/'captions/full/captions.en.srt')]
 if (project/'project.json').exists():
  previous=c.read(project/'project.json');assert previous['revision']=='orientation-matrix-v8' and previous['finalRender']['captionedSha256']==captioned['sha256'],'Preserve differing prior project manifest'
 if folder.exists():
  assert (project/'production/delivery-output.json').exists(),'Existing output has no matching collector receipt'
  for _,name,source in sources:assert (folder/name).exists() and c.sha(folder/name)==c.sha(source),'Preserve differing prior output before metadata writes'
 manifest=dict(schemaVersion=2,slug=SLUG,parentProject=c.P.name,worklistUnit='M04',revision='orientation-matrix-v8',status='complete-local-final-review-pending',titles=dict(ko=title,en='How Does a Game Remember an Object’s Tilt? — Orientation and Rotation Matrices'),publishReady=False,sourceScope='Article8.1–8.2.5; approved V8 script only',authorization=c.rel(H/'authorization.json'),paths=dict(script=c.rel(c.S/'narration.ko.json'),scriptEn=c.rel(c.S/'narration.en.json'),timeline=c.rel(H/'timeline.json'),sceneProductionPlan=c.rel(c.P/'planning/revision-v8-orientation-matrix/production-plan.json'),videoClean=c.rel(c.O/'orientation-matrix.clean.mp4'),videoBurnedCaptions=c.rel(c.O/'orientation-matrix.captioned.mp4'),captionsKo=c.rel(c.O/'captions/full/captions.ko.srt'),captionsEn=c.rel(c.O/'captions/full/captions.en.srt')),format=dict(width=1920,height=1080,fps=60),delivery=dict(directory='output/'+SLUG,required=['captioned.mp4','clean.mp4','ko.srt','en.srt'],collector='node scripts/collect-video-output.cjs '+SLUG,review=dict(provider='local-filesystem',humanReview='pending',reviewedSha256=None,masterSha256=captioned['sha256'],driveUploadRequired=False)),membershipOutro=dict(enabled=True,appliedToFinal=True,durationFrames=600,source=timeline['branding']['membership']['file']),audio=dict(backgroundMusic=dict(enabled=False,policy='lecture-no-added-bgm-standard-game-audio-v3'),currentMix=c.rel(c.O/'mix/mix-report.json')),finalRender=dict(status='complete-local-final-review-pending',frames=timeline['totalFrames'],durationSeconds=timeline['duration'],captionedSha256=captioned['sha256'],qualityReview=c.rel(c.O/'qa/quality-review.json'),knownIssues=[],openItems=['사용자 최종 영상 검수·전체 청취 대기']))
 c.save(project/'project.json',manifest)
 if not folder.exists():
  subprocess.run(['node','scripts/collect-video-output.cjs',SLUG],cwd=c.R,check=True)
 else:
  assert (project/'production/delivery-output.json').exists(),'Existing delivery must have the canonical collector receipt'
 for kind,name,source in sources:
  target=folder/name;digest=c.sha(source)
  assert target.exists() and c.sha(target)==digest,'Preserve differing prior delivery before explicit replacement'
  assert c.sha(target)==digest;files.append(dict(kind=kind,file=c.rel(target),absolutePath=str(target),sha256=digest,bytes=target.stat().st_size))
 chapters=[]
 for scene in timeline['scenes']:
  sec=scene['startFrame']/60;minutes=int(sec)//60;seconds=int(sec)%60
  chapters.append(f'<button type="button" data-time="{sec:.6f}"><time>{minutes:02}:{seconds:02}</time> {html.escape(scene["title"])}</button>')
 page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>자세와 회전행렬 · 얌얌코딩</title><style>
 :root{color-scheme:dark;font-family:"Malgun Gothic",sans-serif}body{margin:0;background:#080808;color:#f5f5f5;line-height:1.6}main{max-width:1280px;margin:auto;padding:24px}h1{font-size:28px;color:#e8cf83}p{color:#d5d5d5}video{display:block;width:100%;background:#000}nav{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}a{color:#73c7c2}details{border-top:1px solid #383838;padding:16px 0}button{display:block;text-align:left;background:none;color:#f5f5f5;border:0;font:inherit;padding:10px;cursor:pointer}button:hover,button:focus-visible{background:#252525;outline:2px solid #73c7c2}time{color:#e8cf83;margin-right:12px}small{display:block;word-break:break-all;color:#b8b8b8} @media(max-width:600px){main{padding:12px}h1{font-size:22px}}
 </style><main><h1>'''+html.escape(title)+'''</h1><p>8.1 자세부터 8.2.5 행렬 표현 정리까지 · 1920×1080 · 60fps · 추가 배경음악 없음</p><video id="player" controls preload="metadata" playsinline src="'''+SLUG+'''.captioned.mp4"></video><nav><a href="'''+SLUG+'''.captioned.mp4" download>자막 포함 영상</a><a href="'''+SLUG+'''.clean.mp4" download>자막 없는 영상</a><a href="'''+SLUG+'''.ko.srt" download>한국어 자막</a><a href="'''+SLUG+'''.en.srt" download>영어 자막</a></nav><details open><summary>설명 위치로 이동</summary>'''+''.join(chapters)+'''</details><p>현재 버전은 사용자 최종 검수 대기입니다. 플랫폼에 업로드하지 않았습니다.</p><small>자막 포함 완성본 SHA256: '''+captioned['sha256']+'''</small></main><script>document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{const v=document.querySelector('video');v.currentTime=Number(b.dataset.time);v.play();});</script></html>'''
 (folder/'index.html').write_text(page,encoding='utf8')
 receipt=dict(schemaVersion=1,revision='orientation-matrix-v8',title=title,scope='8.1–8.2.5',directory=c.rel(folder),index=c.rel(folder/'index.html'),files=files,masterSha256=captioned['sha256'],durationSeconds=timeline['duration'],frames=timeline['totalFrames'],dimensions=[1920,1080],fps=60,status='ready-for-local-user-review',technicalQa=c.rel(c.O/'qa/quality-review.json'),humanFinalReview='pending',humanReviewMessage=None,reviewedAt=None,linksReady=True,deliveredAt=None,platformMutation=False,youtubeUploaded=False,driveUploaded=False,automaticNextVideo=False,recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
 c.save(H/'local-delivery.json',receipt);c.save(folder/'manifest.json',receipt);print(json.dumps(dict(folder=str(folder),captioned=str(folder/(SLUG+'.captioned.mp4')),duration=timeline['duration']),ensure_ascii=False))
if __name__=='__main__':main()
