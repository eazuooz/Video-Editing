"""Build a review plan from preserved seven paragraphs; no TTS/model rerender."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix();now=lambda:datetime.now(timezone.utc).isoformat();rf=lambda t:math.floor(t*60+.5)
def proof(p):return {'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=P/'additive-unmixed-review-assembly-v2.json';sp=P/'clean-source-selection-v8.json';cp=P/'local/caption-word-draft-v2.json'
a=read(ap);s=read(sp);byId={m['id']:m for m in s['selected']}
ids=['original-22-1','original-22-2','18-pre-generated-frame-count','19-guide-generated-ui','original-22-3','original-22-4','original-22-5']
entries=[e for e in a['entries'] if e['id'] in ids];assert [e['id'] for e in entries]==ids
priorPath=P/'hair-chapter-review-build-v30.json';prior=read(priorPath);assert sha(R/prior['outputs'][0]['path'])==prior['outputs'][0]['sha256']
start=entries[0]['start']-.72;end=entries[-1]['end'];ff,lf=rf(start),rf(end);N=lf-ff
cuts=[]
def add(id,x,y,kind,**kw):
 f,t=rf(x)-ff,rf(y)-ff;assert t>f
 if cuts:assert cuts[-1]['toFrame']==f
 cuts.append({'id':id,'from':round(x-start,9),'to':round(y-start,9),'fromFrame':f,'toFrame':t,'frames':t-f,'kind':kind,**kw})
def model(e,id=None,x=None,y=None,span=None,**kw):
 m=byId[id or e['id']];span=span or m['mediaSpanFrames'];x=e['start'] if x is None else x;y=e['end'] if y is None else y
 assert abs(rf(y)-rf(x)-(span[1]-span[0]))<=1
 add(e['id'] if id is None else e['id']+'-diagram',x,y,'explanation',entryId=e['id'],path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,verification=m['verification'],shiftUpPixels=60,**kw)
po=prior['outputs'][0];add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=po['path'],sha256=po['sha256'],sourceStart=(po['frames']-1)/60,freezeFrameOnly=True)
nativeProof=P/'native-direct-progress-v3.json';artistProof=P/'native-source-observation-v7.json'
for e in entries:
 if e['id']=='19-guide-generated-ui':
  path='production/research/game-lighting-history/local/episode04-native-v1/dlss45-ui-comparison.mp4';assert sha(R/path)=='2ad4a2fabc8034416ad0051456d2fa76c912c7b9ff2f98a010c45642726bb9ab'
  add(e['id']+'-actual-ui-comparison',e['start'],e['start']+6.35,'actual',entryId=e['id'],path=path,sha256=sha(R/path),sourceStart=0,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,label='NVIDIA · DLSS 4.5 표시 프레임 시연 · 2026',secondaryLabel='화면 움직임과 UI 관찰 · 입력 지연을 측정한 영상이 아님',sourceSampleReview=proof(nativeProof))
  m=byId['18-pre-generated-frame-count'];span=[m['mediaSpanFrames'][0]+247,m['mediaSpanFrames'][0]+850]
  model(e,id='18-pre-generated-frame-count',x=e['start']+6.35,y=e['end'],span=span,label='설명용 도식 · 실제 렌더 프레임과 표시 프레임 구별',opaqueHeaderStrip=True)
 elif e['id']=='original-22-4':
  path='production/research/game-lighting-history/local/episode04-process-windows-v4/dlss5-artist-character-controls.mp4';assert sha(R/path)=='8577ebd102f6ba435062daf4f24773cdfa2ba802b084db3f7880caa29736d29f'
  add(e['id']+'-actual-artist-controls',e['start'],e['end'],'actual',entryId=e['id'],path=path,sha256=sha(R/path),sourceStart=8,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,label='NVIDIA · DLSS 5 기술 시연 · 2026',secondaryLabel='상단 강도·영역 제어와 인물 표현 비교 · NBA 2K27 장면 아님',sourceSampleReview=proof(artistProof))
 else:model(e)
assert cuts[-1]['toFrame']==N
cues=[]
for c in read(cp)['cues']:
 if c['entryId'] in ids:
  x,y=round(c['from']-start,9),round(c['to']-start,9);cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':x,'to':y,'firstFrame':math.ceil(x*60-1e-7),'exclusiveEndFrame':math.ceil(y*60-1e-7)})
audio={**a['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
research={'checkedAt':now(),'sources':[{'url':'https://www.nvidia.com/en-us/geforce/news/dlss-4-5-dynamic-multi-frame-generation-6x-mode-released/','publishedAt':'2026-03-31','supports':'DLSS4 maxthree additional;4.5 maxfive additional on supported RTX50; dynamic versus fixed and per-title conditions.'},{'url':'https://www.nvidia.com/en-us/geforce/news/dlss-5-3d-guided-neural-rendering/','publishedAt':'2026-09-01','supports':'Current official article confirms NBA2K27 availability, color/motion input, independent feature and strength/tone/region controls. Treat quality/physics as vendor claims; observed footage is a separate technology demonstration.'}],'method':'Official pages searched/opened on2026-10-11; current supplied wording compared; no narration re-generation needed.'}
rp=P/'dlss-current-primary-review-v31.json';write(rp,research)
j={'preparedAt':now(),'scope':'DLSS4/4.5/5 seven paragraphs, actual UI/control demonstrations and original PCM; chapter review only, not final60:40 allocation','selection':proof(sp),'assembly':proof(ap),'captionDraft':proof(cp),'nativeReview':proof(nativeProof),'artistReview':proof(artistProof),'currentPrimaryReview':proof(rp),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':sum(c['frames'] for c in cuts if c['kind']=='actual'),'explanationFrames':sum(c['frames'] for c in cuts if c['kind']=='explanation'),'body60to40Approved':False},'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'causalPlan':['Hair material response versus display reconstruction responsibilities.','One actual render plus generated display frames does not multiply simulated updates/ray evaluations.','Moving UI comparison does not establish input latency.','DLSS5 vendor description and technology controls are separate from NBA2K27 independent measurements.','Computed linear light still needs exposure/tone mapping; next chapter follows.'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'newTts':0,'newGitImages':0}
pp=P/'dlss-chapter-review-plan-v31.json';write(pp,j)
src=R/'production/research/game-lighting-history/build-episode04-hair-chapter-v29.py'
b=src.read_text('utf-8').replace('hair','dlss').replace('Hair','Dlss').replace('v29','v31').replace('V29','V31')
b=b.replace('assert N==8577 and len(plan[\'cuts\'])==12 and len(plan[\'entries\'])==10 and len(plan[\'cues\'])==34',f"assert N=={N} and len(plan['cuts'])=={len(cuts)} and len(plan['entries'])==7 and len(plan['cues'])=={len(cues)}")
b=b.replace("'captionCues':34",f"'captionCues':{len(cues)}").replace("'total':10",f"'total':{len(cuts)}")
b=b.replace('Review22 encoded cues/cuts/annotations, then transparency/hair chapter','Review encoded DLSS cues/cuts/controls; postprocess chapter follows').replace('Direct path chapter encoded review; all moving/full episode approvals pending','Direct DLSS chapter encoded review; remaining postprocess/RenderDoc/conclusion and final allocation pending')
dest=src.with_name('build-episode04-dlss-chapter-v31.py');assert not dest.exists();compile(b,str(dest),'exec');dest.write_text(b,'utf-8')
print(json.dumps({'plan':rel(pp),'frames':N,'cuts':len(cuts),'cues':len(cues),'pcm':audio['samplesInChapter'],'finalApproved':False}))
