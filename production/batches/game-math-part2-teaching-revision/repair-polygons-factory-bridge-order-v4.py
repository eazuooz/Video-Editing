"""Match the narrated next factory to QG06; preserve every scene dictionary/PCM."""
from pathlib import Path
import copy,json,hashlib
from datetime import datetime
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
slug='game-math-polygon-partition-v2';P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
lesson=read(P/'production/lesson.json');t=read(P/'production/timeline.json');m=read(P/'project.json');old=copy.deepcopy(t)
receipt=R/'factory-bridge-order-repair-v4.json';assert not receipt.exists(),'Already applied; do not repeat repair'
wav=ROOT/m['paths']['narration'];a,sr=sf.read(wav,dtype='float32');assert sr==24000
order=[s['id'] for s in lesson['scenes']];assert order[order.index('QB14')+1]=='QG07'
order.remove('QB14');order.insert(order.index('QG06'),'QB14')
lesson['scenes']=sorted(lesson['scenes'],key=lambda s:order.index(s['id']))
write(P/'production/lesson.json',lesson)
for lang in ['ko','en']:
    script=read(P/f'script/narration.{lang}.json');script['scenes']=sorted(script['scenes'],key=lambda s:order.index(s['id']));write(P/f'script/narration.{lang}.json',script)
rows=sorted(t['scenes'],key=lambda s:order.index(s['id']));start=2;b=np.zeros_like(a);deltas={}
for slot in rows:
    previous=next(s for s in old['scenes'] if s['id']==slot['id']);deltas[slot['id']]=start-previous['start']
    count=round(slot['seconds']*sr);samples=a[round(previous['start']*sr):round(previous['start']*sr)+count]
    b[round(start*sr):round(start*sr)+count]=samples;slot['start']=start;start+=slot['seconds']
    assert np.array_equal(samples,b[round(slot['start']*sr):round(slot['start']*sr)+count])
t['scenes']=rows
for lang in ['ko','en']:
    t[lang+'Captions']=sorted([{**c,'start':c['start']+deltas[c['scene']],'end':c['end']+deltas[c['scene']]} for c in old[lang+'Captions']],key=lambda c:c['start'])
    def stamp(x):
        n=round(x*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
    (P/f'script/final.{lang}.srt').write_text('\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(t[lang+'Captions'],1))+'\n',encoding='utf8')
assert [(c['start'],c['end']) for c in t['koCaptions']]==[(c['start'],c['end']) for c in t['enCaptions']]
assert abs(start+10-t['seconds'])<1e-7
sf.write(wav,b,sr);actual,_=sf.read(wav,dtype='float32');assert np.array_equal(b,actual),'PCM values must be exact'
write(P/'production/timeline.json',t)
flow=read(B/'polygons-episode-flow-audit.json');episode=next(e for e in flow['episodes'] if e['slug']==slug);episode['order']=order;episode['finalContinuousReview']=False;write(B/'polygons-episode-flow-audit.json',flow)
m['finalRender'].update(currentPixelApproval=False,status='factory-bridge-order-remix-required');m['approvals']['pixels']='Prior exact scene-local reviews preserved; new full ordering/composition/captions pending';write(P/'project.json',m)
write(receipt,{'recordedAt':datetime.now().astimezone().isoformat(),'reason':'QB14 promised the next factory, but QG07 begins with19.267s of Noita before a factory insert. Put the unchanged QB14 immediately before actual Shapez2 QG06.','oldOrder':[s['id'] for s in old['scenes']],'newOrder':order,'unchangedSceneDictionaries':True,'unchangedScenePcmSamples':True,'unchangedDurationsAnd40To60Ratio':True,'unchangedClipsAndLocalAnnotationTiming':True,'newSourceSha256':sha(wav),'newTimelineSha256':sha(P/'production/timeline.json'),'oldCaptionedSha256':'d3f7c54be67a98167f3ff1276ef135c9e941db4aee9e812c8afca937035a008e','mixedFinalApprovalInvalidated':True,'humanListening':'pending'})
print('Moved unchanged QB14 to directly before QG06; all24 scene PCM values, local clips, captions and exact40:60 preserved.')
