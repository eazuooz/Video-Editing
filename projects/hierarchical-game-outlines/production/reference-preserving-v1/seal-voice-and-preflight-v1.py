from pathlib import Path
import json,datetime,hashlib,psutil,subprocess
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[3];now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'voice-direct-review-v1.json').exists()
whole=read(P/'voice-asr-v1.json');ctx=read(P/'voice-contexts-v1.json')
closed=[]
for s,session,chunk in [(whole,51920,'2c9309'),(ctx,90153,'c26d90')]:
 try:assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
 except psutil.NoSuchProcess:pass
 closed.append(dict(session=session,completion=chunk,actualOuterExit=0,workerDead=True,pid=s['pid'],createTime=s['createTime']))
review=dict(at=now(),whole=closed[0],contexts=closed[1],wholeSha256=sha(P/'voice-asr-v1.json'),contextsSha256=sha(P/'voice-contexts-v1.json'),allEightFullTextsDirectlyCompared=True,
 findings=['01–04 and07–08 complete expected concepts and endings recovered; ordinary whitespace/particle transcription variants do not warrant new TTS.',
 '05 whole ASR overlaps 확인 and 확인하세요 at25.18s. Independent14.24–31.44 complete context recovers single 확인하세요 and full remainder.',
 '06 whole ASR 개어 is recovered as 개요 in independent0–9.64 complete paragraph. No PCM edit or regenerated voice.',
 '05 context expected field included two earlier sentences by metadata line selection. Actual crop starts with 반대로; the corrected expected context below matches its actual source interval. This is a record correction, not an audio omission.'],
 corrected05ContextExpected='반대로 순서를 바꾸고 싶을 때는 제목과 그 아래 설명을 한 묶음으로 옮깁니다. 옆으로 한 단계 옮기면 소속이 달라집니다. 같은 층으로 올린 것인지, 다른 제목의 아래에 넣은 것인지 확인하세요. 순서 이동과 단계 변경을 구분하면 내용이 엉뚱한 곳에 붙는 일을 줄일 수 있습니다.',
 generatedAudioCompleteForEditing=True,humanListening=False,humanPronunciationApproval=False,mixApproval=False)
write(P/'voice-direct-review-v1.json',review)
pre=read(P/'white-preflight-direct-review.json');backup=P/'white-preflight-before-timing-v1.json';backup.write_bytes((P/'white-preflight-direct-review.json').read_bytes())
pre.update(previousLayoutSourceSha256=pre['sourceSha256'],sourceSha256=sha(ROOT/'motion-canvas/src/projects/hierarchical-game-outlines/reference-explanations-v1.tsx'),measuredTimingSha256=sha(ROOT/'motion-canvas/src/projects/hierarchical-game-outlines/reference-reel-plan-v1.json'),timingOnlyUpdate=dict(at=now(),reason='05 fold5.5 / expand8.02 / groupmove14.36 / reparent19.2 use actual word landmarks. Shapes/text/layout unchanged. Prior representative layout evidence retained; final moving pixels still pending.'))
write(P/'white-preflight-direct-review.json',pre)
newsource=dict(at=now(),url='https://www.youtube.com/watch?v=EyaXufIsK48',range=[48,72.5],cuaTab=145,startObserved=48.000126,endObserved=72.654342,rate=1,muted=True,endedPaused=True,sourceSamples='qa-independent-source-v1, prior50/60/70s direct readings',finding='Continuous Yoshi/Donkey Kong actions and response; supports familiar input/action/result subject of working notes, no exact button or measured damage claim.',everyIntermediateFrameReviewed=False,humanListening=False)
write(P/'move-continuation-direct-review-v1.json',newsource)
# Create new transparent graphic layers; no source pixels are modified here.
dest=P/'annotations-local';dest.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',29)
for kind in ['parent','children']:
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
 if kind=='parent':d.line([(309,81),(583,81)],fill='#d93b38',width=6)
 else:
  d.line([(1491,155),(1512,155),(1512,472),(1491,472)],fill='#0b8c86',width=6)
  d.rounded_rectangle((1744,174,1904,310),radius=12,fill='#111820de')
  d.multiline_text((1824,242),'소리 아래\n세부 항목',font=font,fill='white',anchor='mm',align='center',spacing=8)
 im.save(dest/f'sound-{kind}.png')
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['privateUploadAuthorized'] and control['newProductionAuthorization']['fullProductionAuthorized']
resource=dict(at=now(),cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout,
 ownedHeavy=[dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline()) for p in psutil.process_iter() if p.pid!=__import__('os').getpid() and any('reference-preserving-v1/'+x in ' '.join(p.cmdline()).replace('\\','/') for x in ['render-reference.cjs','review-audio-v1.py','review-voice-contexts-v1.py'])])
assert not resource['ownedHeavy'] and resource['cpu']<85 and resource['availableMemoryBytes']>8e9
write(P/'final-render-resource-v1.json',resource)
cp=read(P/'latest-checkpoint.json');cp.update(updatedAt=now(),stage='measured-timeline-ready-for-final-render',workerState=None,session=None,next='Render exact current eight PPT scenes once, then current gameplay composites/mix/final QA.',voiceReview='voice-direct-review-v1.json',timeline='final-timeline-v1.json');write(P/'latest-checkpoint.json',cp)
print('Voice whole/contexts closed; measured timeline and layout-only reuse bound; resources recorded.')
