"""Record actual direct reads and prepare remaining preserved PCM chapter sources.

Preparations never grant final pixel/audio/ratio or publishing approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math, psutil

R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(R).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
proof = lambda p: {'path': rel(p), 'sha256': sha(p)}
rf = lambda t: math.floor(t * 60 + .5)
def write(p, j):
    assert not p.exists(), p
    p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')

execution = P / 'postprocess-chapter-review-execution-v37.json'
ex = read(execution)
assert ex['status'] == 'technical-review-pair-ready' and ex['active'] is None
assert all(c['exitCode'] == 0 for c in ex['commands'])
try:
    assert abs(psutil.Process(ex['worker']['pid']).create_time() - ex['worker']['createTime']) > .01
except psutil.NoSuchProcess:
    pass
session = R / 'production/research/game-lighting-history/local/episode04-postprocess-chapter-v37/session.json'
write(session, {'sessionId': 64970, 'worker': ex['worker'], 'terminalCompletionObserved': True,
                'exitCode': 0, 'completedAt': ex['endedAt'], 'verifiedAt': stamp(), 'execution': proof(execution),
                'originalWorkerAlive': False})

oldExtraction = R / 'production/research/game-lighting-history/local/episode04-postprocess-encoded-v34/execution.json'
old = read(oldExtraction)
readNums = set(range(1, 13)) | set(range(19, 59))
boards = []
for b in old['boards']:
    n = int(Path(b['path']).stem.split('-')[-1])
    if b['source'] == 'clean' or n in readNums:
        assert sha(R / b['path']) == b['sha256']
        boards.append({**b, 'directlyViewed': True, 'reviewedAt': stamp(),
                       'continuity': 'Direct reads continued across preceding and current contexts.'})
oldReview = P / 'postprocess-unchanged-sample-review-v38.json'
write(oldReview, {'reviewedAt': stamp(), 'extraction': proof(oldExtraction),
                 'cleanBoardsRead': list(range(1, 25)), 'captionBoardsRead': sorted(readNums), 'boards': boards,
                 'unreadHistoricalCaptionBoards': list(range(13, 19)),
                 'historicalMathRejection': proof(P / 'postprocess-encoded-math-rejection-v34.json'),
                 'findings': [
                     'Exposure settings and camera change together; the visible label explicitly excludes a controlled fixed-camera A/B.',
                     'Focus debug preserves blue far/green near/black focus legend and 250 focal distance; ordinary blur is a separate settings/camera interval.',
                     'The debug/normal cut is exactly cue298 at frame5608. Fixed two-line captions do not cover relevant controls.',
                     'Bloom image spreading is distinguished from light arriving at another face; projected focus/motion diagrams are explanation.',
                     'sRGB .500 decodes to about .214, doubled linear value .428 encodes to about .686.',
                     'Final six role blocks and arrows stay above fixed captions; no claim of universal engine pass order.',
                     'The rejected historical tone scenes remain rejected; corrected v37 math samples require independent direct review.'
                 ], 'unchangedSampledCaptionClearanceApproved': True,
                 'allHistoricalSamplesRead': False, 'allMovingPixelsReviewed': False,
                 'allFinalPixelsReviewed': False, 'uploaded': False, 'newGitImages': 0})

nx = R / 'production/research/game-lighting-history/local/episode04-renderdoc-native-v35/execution.json'
native = read(nx); assert len(native['samples']) == 19 and len(native['boards']) == 6
nb = []
for b in native['boards']:
    assert sha(R / b['path']) == b['sha256']
    nb.append({**b, 'directlyRead': True, 'reviewedAt': stamp(),
               'continuity': 'All six boards directly read in preceding context; mesh66/shader116 reread now for framing.'})
nativeReview = P / 'renderdoc-native-direct-review-v38.json'
write(nativeReview, {'reviewedAt': stamp(), 'extraction': proof(nx), 'sampleCount': 19, 'boards': nb,
                     'allPlannedSamplesDirectlyRead': True,
                     'observations': [
                         '64/66: TextureViewer selected DrawInstanced EID14 and the colored triangle. 68–74: vertex/pipeline input and MeshViewer POSITION are different views.',
                         '100/102 is the vertex shader return output, so it cannot stand in for the pixel shader returning input.color.',
                         '104–114: triangle pixel selection. 116–124: pixel shader return input.color and COLOR input (.96125,.01312,.02562,1).',
                         'SV_Target/return are still zero before stepping; do not claim final returned values in this interval.',
                         '125–132.5 already supports the opening example; the new guide ends before125 to avoid duplicated source time.'
                     ], 'selected': [{'sourceIn': 64, 'seconds': 3}, {'sourceIn': 109.52, 'seconds': 15.48}],
                     'comparisonLimit': 'Own simple triangle shader inspection; no proof of another game lighting implementation or benchmark.',
                     'nativeContinuousPlaybackReviewed': False, 'allMovingPixelsReviewed': False,
                     'finalApproved': False, 'newGitImages': 0})

# Extract only the two repaired scenes. Nine existing clean cuts are byte-identical.
src = R / 'production/research/game-lighting-history/extract-episode04-postprocess-encoded-v34.py'
s = src.read_text('utf-8').replace('v34', 'v37').replace('V34', 'V37')
start = s.index('def points_for('); end = s.index('\ntry:', start)
s = s[:start] + '''def points_for(captioned):
 points={}
 changed=[c for c in plan['cuts'] if c['id'] in ['original-22p-1','original-22p-2']]
 def add(frame,label):
  if 0<=frame<N:points.setdefault(frame,[]).append(label)
 for cut in changed:
  for f,name in [(cut['fromFrame']-1,'before'),(cut['fromFrame'],'first'),((cut['fromFrame']+cut['toFrame']-1)//2,'middle'),(cut['toFrame']-1,'last'),(cut['toFrame'],'after')]:add(f,cut['id']+' '+name)
  for frac in [.15,.3,.5,.7,.85]:add(cut['fromFrame']+round((cut['frames']-1)*frac),'corrected tone geometry '+str(frac))
 if captioned:
  for c in metrics:
   if c['entryId'] in ['original-22p-1','original-22p-2']:
    first,last=c['firstFrame'],c['exclusiveEndFrame']
    for f,name in [(first,'first'),((first+last-1)//2,'middle'),(last-1,'last'),(first-1,'before'),(last,'after')]:add(f,'cue'+str(c['id'])+' '+name)
 return points
''' + s[end:]
dest = R / 'production/research/game-lighting-history/extract-episode04-postprocess-encoded-v37.py'
assert not dest.exists(); compile(s, str(dest), 'exec'); dest.write_text(s, 'utf-8')

aPath=P/'additive-unmixed-review-assembly-v2.json'; a=read(aPath)
selPath=P/'clean-source-selection-v8.json'; selection=read(selPath)
capPath=P/'local/caption-word-draft-v2.json'; byId={m['id']:m for m in selection['selected']}
entries=[e for e in a['entries'] if e['originalScene'] in ['22r','22rb','conclusion']]
assert len(entries)==22
ids=[e['id'] for e in entries]
start=entries[0]['start']-.72; end=entries[-1]['end']; ff,lf=rf(start),rf(end); N=lf-ff; cuts=[]
def add(id,x,y,kind,**kw):
    f,t=rf(x)-ff,rf(y)-ff; assert t>f
    if cuts:assert cuts[-1]['toFrame']==f
    cuts.append({'id':id,'from':round(x-start,9),'to':round(y-start,9),'fromFrame':f,'toFrame':t,'frames':t-f,'kind':kind,**kw})
priorPath=P/'postprocess-chapter-review-build-v37.json'; prior=read(priorPath); po=prior['outputs'][0]
assert sha(R/po['path'])==po['sha256']
def gap(x,y):
    add('preserved-silent-boundary-'+str(len(cuts)),x,y,'explanation',path=po['path'],sha256=po['sha256'],sourceStart=(po['frames']-1)/60,freezeFrameOnly=True)
gap(start,entries[0]['start'])
path='production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4'
digest='4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8';assert sha(R/path)==digest
for i,e in enumerate(entries):
    if i and e['start']>entries[i-1]['end']+.0001:gap(entries[i-1]['end'],e['start'])
    if e['id']=='24-guide-renderdoc-input':
        split=e['start']+3
        base={'entryId':e['id'],'path':path,'sha256':digest,'sourceCrop':[244,123,1570,923],
              'normalSpeed':True,'loop':False,'slowdown':False,'sourceAudio':False,'nativeShiftUpPixels':120,
              'sourceSampleReview':proof(nativeReview),'label':'우리 채널 · RenderDoc · 삼각형 셰이더 검사',
              'secondaryLabel':'직접 확인한 입력·코드 · 다른 게임의 조명 패스 증거 아님','opaqueHeaderStrip':True}
        add(e['id']+'-triangle',e['start'],split,'actual',sourceStart=64,**base)
        add(e['id']+'-pixel-shader',split,e['end'],'actual',sourceStart=109.52,
            annotation={'type':'native-light-surface','screenIntervals':[{'from':6.48,'to':15.48,
                         'boxes':[[545,460,195,38,'0xE95757'],[465,795,495,48,'0x43D7CC']]}]},**base)
    else:
        m=byId[e['id']];span=m['mediaSpanFrames']
        assert abs(rf(e['end'])-rf(e['start'])-(span[1]-span[0]))<=1
        add(e['id'],e['start'],e['end'],'explanation',entryId=e['id'],path=m['media']['path'],
            sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,
            verification=m['verification'],shiftUpPixels=60)
assert cuts[-1]['toFrame']==N
cues=[]
for c in read(capPath)['cues']:
    if c['entryId'] in ids:
        x,y=round(c['from']-start,9),round(c['to']-start,9)
        cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':x,'to':y,
                     'firstFrame':math.ceil(x*60-1e-7),'exclusiveEndFrame':math.ceil(y*60-1e-7)})
audio={**a['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),
       'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
plan={'preparedAt':stamp(),'scope':'Preserved RenderDoc/resource inspection, continuation and conclusion; chapter review only. Exact final allocation/splits remain pending.',
      'selection':proof(selPath),'assembly':proof(aPath),'captionDraft':proof(capPath),'nativeReview':proof(nativeReview),
      'priorBuild':proof(priorPath),'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,
      'totals':{'frames':N,'globalFromFrame':ff,'globalToFrame':lf,'videoSeconds':N/60,'pcmSeconds':audio['secondsInChapter'],
                'roundingErrorFrames':N-audio['secondsInChapter']*60,'actualFrames':sum(c['frames'] for c in cuts if c['kind']=='actual'),
                'explanationFrames':sum(c['frames'] for c in cuts if c['kind']=='explanation'),'body60to40Approved':False},
      'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,
      'causalPlan':['Display transform motivates inspection of data provenance.','Specific question then matched conditions, format and producer/consumer relationships.',
                   'Simple recorded pixel shader connects a visible triangle to its color input and return location.',
                   'Depth, encoded channels, shadow and reflection fallbacks are different resources.',
                   'Volume, temporal history and final transforms motivate separate repeated performance measurements.',
                   'Conclude the whole series with storage, search domain, and reuse questions.'],
      'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'finalMixedAsrApproved':False,
      'wholeEpisode60to40Approved':False,'newTts':0,'newGitImages':0}
pp=P/'inspection-chapter-review-plan-v38.json';write(pp,plan)
s=(R/'production/research/game-lighting-history/build-episode04-postprocess-chapter-v37.py').read_text('utf-8')
s=s.replace('postprocess','inspection').replace('Postprocess','Inspection').replace('v37','v38').replace('V37','V38')
s=s.replace("N==7637 and len(plan['cuts'])==11 and len(plan['entries'])==9 and len(plan['cues'])==31",
            f"N=={N} and len(plan['cuts'])=={len(cuts)} and len(plan['entries'])==22 and len(plan['cues'])=={len(cues)}")
s=s.replace("'total':11",f"'total':{len(cuts)}").replace("'captionCues':31",f"'captionCues':{len(cues)}")
s=s.replace("  if c.get('cropTopPixels'):","  if c.get('sourceCrop'):\n   x,y,w,h=c['sourceCrop'];vf.append(f'crop={w}:{h}:{x}:{y}')\n  if c.get('cropTopPixels'):")
s=s.replace('Direct DLSS chapter encoded review; remaining inspection/RenderDoc/conclusion and final allocation pending','Review final resource/conclusion samples, then exact final ratio and episode boundary planning')
dest=R/'production/research/game-lighting-history/build-episode04-inspection-chapter-v38.py'
assert not dest.exists();compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
checkpoint=R/'production/research/game-lighting-history/checkpoint.json';j=read(checkpoint)
j['episode04PostprocessChapterV37']={'execution':proof(execution),'session':proof(session),'status':ex['status'],'frames':7637,'sameAac':True,'allFinalPixelsReviewed':False}
j['episode04RenderdocNativeReviewV38']=proof(nativeReview)
j['episode04PostprocessUnchangedSamplesV38']=proof(oldReview)
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'Extract repaired postprocess scenes once; direct read; compose inspection/conclusion from completed sources. No GPU TTS.'}
j['updatedAt']=stamp();tmp=checkpoint.with_suffix('.prepare-v38.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(checkpoint)
print(json.dumps({'plan':rel(pp),'frames':N,'cuts':len(cuts),'entries':len(entries),'cues':len(cues),'actualFrames':plan['totals']['actualFrames'],'newTts':0,'newGitImages':0}))
