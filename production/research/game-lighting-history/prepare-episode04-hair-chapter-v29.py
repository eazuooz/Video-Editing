"""Transparency/hair chapter, ten complete bilingual paragraphs and original PCM."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix();now=lambda:datetime.now(timezone.utc).isoformat();rf=lambda t:math.floor(t*60+.5)
def proof(p):return {'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=P/'additive-unmixed-review-assembly-v2.json';sp=P/'clean-source-selection-v8.json';cp=P/'local/caption-word-draft-v2.json';nr=P/'hair-native-direct-review-v27.json'
a=read(ap);s=read(sp);byId={x['id']:x for x in s['selected']};entries=[e for e in a['entries'] if e['start']>=960.8 and e['end']<=1103.2];assert len(entries)==10
start=960.1600833333334;end=entries[-1]['end'];ff,lf=rf(start),rf(end);N=lf-ff;assert(ff,lf,N)==(57610,66187,8577)
cuts=[]
def add(id,x,y,kind,**kw):
 f,t=rf(x)-ff,rf(y)-ff;assert t>f
 if cuts:assert cuts[-1]['toFrame']==f
 cuts.append({'id':id,'from':round(x-start,9),'to':round(y-start,9),'fromFrame':f,'toFrame':t,'frames':t-f,'kind':kind,**kw})
def model(e,id=None,x=None,y=None,span=None,**kw):
 m=byId[id or e['id']];span=span or m['mediaSpanFrames'];x=e['start'] if x is None else x;y=e['end'] if y is None else y
 assert abs(rf(y)-rf(x)-(span[1]-span[0]))<=1
 add(e['id'] if id is None else e['id']+'-diagram',x,y,'explanation',entryId=e['id'],path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,verification=m['verification'],shiftUpPixels=60,**kw)
prior=read(P/'megalights-chapter-review-build-v28.json')['outputs'][0]
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',path=prior['path'],sha256=prior['sha256'],sourceStart=(prior['frames']-1)/60,freezeFrameOnly=True)
for e in entries:
 if e['id']=='17-guide-hair-material':
  path='production/research/game-lighting-history/local/episode04-native-v2/strand-hair-editor-ue426-2021.mp4';assert sha(R/path)=='63cd36424f88e7e687ef104ee242289f02dbf58f93cd455d52879db2efb22a75'
  add(e['id']+'-material-input-result',e['start'],e['start']+9.32,'actual',entryId=e['id'],path=path,sha256=sha(R/path),sourceStart=817,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,label='Unreal Engine · 머리카락 재질 입력 시연 · 2021',secondaryLabel='노랑: MelaninMainColor · 청록: 색이 달라지는 가닥',annotation={'type':'hair-input-result','note':'Same editor view, material-input change; no strand-count or full renderer-replacement claim','screenIntervals':[{'from':0,'to':9.32,'boxes':[[1325,430,285,55,'0xF6D872'],[705,330,215,355,'0x43D7CC']]}]},sourceSampleReview=proof(nr))
  m=byId['original-21a-7'];span=[m['mediaSpanFrames'][0]+338,m['mediaSpanFrames'][0]+878]
  model(e,id='original-21a-7',x=e['start']+9.32,y=e['end'],span=span,label='설명용 도식 · 가닥 구조와 재질 색의 책임 구별',opaqueHeaderStrip=True)
 else:model(e)
assert cuts[-1]['toFrame']==N
ids={e['id'] for e in entries};cues=[]
for c in read(cp)['cues']:
 if c['entryId'] in ids:
  x,y=round(c['from']-start,9),round(c['to']-start,9);cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':x,'to':y,'firstFrame':math.ceil(x*60-1e-7),'exclusiveEndFrame':math.ceil(y*60-1e-7)})
audio={**a['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
j={'preparedAt':now(),'scope':'Transparency/hair chapter review: preserve10 KO/EN paragraphs, numerical alpha order and full PCM; nine seconds of actual material input/result plus spatial models, not final60:40 allocation','selection':proof(sp),'assembly':proof(ap),'captionDraft':proof(cp),'nativeReview':proof(nr),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':sum(c['frames'] for c in cuts if c['kind']=='actual'),'explanationFrames':sum(c['frames'] for c in cuts if c['kind']=='explanation'),'body60to40Approved':False},'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,'causalPlan':['Selected light contributions → transparent colors require background contributions.','Alpha definition → red/blue numerical order → why object-center sorting fails.','Per-pixel layers → depth peeling/list costs → weighted approximation limits.','Hair coverage/visibility/scattering → actual material input changes color, not new strands.','Production demonstration date versus algorithm invention; next display reconstruction responsibilities.'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'newTts':0,'newGitImages':0}
write(P/'hair-chapter-review-plan-v29.json',j)
src=R/'production/research/game-lighting-history/build-episode04-megalights-chapter-v28.py';b=src.read_text('utf-8').replace('megalights','hair').replace('MegaLights','Hair').replace('v28','v29').replace('V28','V29')
b=b.replace("assert N==6456 and len(plan['cuts'])==10 and len(plan['entries'])==7 and len(plan['cues'])==22",f"assert N==8577 and len(plan['cuts'])=={len(cuts)} and len(plan['entries'])==10 and len(plan['cues'])=={len(cues)}")
b=b.replace("elif a['type']=='native-light-surface':","elif a['type'] in ['native-light-surface','hair-input-result']:")
# This is a new chapter PCM, so encode its AAC once, then copy to captioned pair.
b=b.replace("'-i',ROOT/'production/research/game-lighting-history/local/episode04-hair-chapter-v26/game-lighting-history-04-hair-chapter.clean.mp4','-map','0:v:0','-map','1:a:0','-c','copy'","'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2'")
b=b.replace("'captionCues':22",f"'captionCues':{len(cues)}")
dest=src.with_name('build-episode04-hair-chapter-v29.py');assert not dest.exists();dest.write_text(b,'utf-8');compile(b,str(dest),'exec')
print(json.dumps({'plan':rel(P/'hair-chapter-review-plan-v29.json'),'entries':10,'cuts':len(cuts),'cues':len(cues),'frames':N,'newTts':0,'newGitImages':0}))
