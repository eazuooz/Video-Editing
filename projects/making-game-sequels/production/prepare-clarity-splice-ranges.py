"""Measure quiet paragraph splice proposals without changing original PCM or scripts."""
import difflib, hashlib, json, math, re
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'[^a-z0-9가-힣]','',s.lower())
request=read(BASE/'targeted-clarity-request.json')
target=BASE/'original-clarity-splice-proposal.json'
if target.exists():raise RuntimeError('Preserve existing measured splice proposal')
for p in request['protectedInputs']:
    assert sha(ROOT/p['path'])==p['sha256'],p['path']
measurements=read(BASE/'narration-tts-execution.json')['measurements']
ko=read(BASE.parent/'script/narration.ko.json'); en=read(BASE.parent/'script/narration.en.json')
rows=[]
for sid in ['01','04','07','11']:
    m=next(v for v in measurements if v['scene']==sid)
    audio,rate=sf.read(ROOT/m['path'],dtype='float32')
    assert rate==24000 and sha(ROOT/m['path'])==m['sha256']
    source=ROOT/f'shared/output/narration/making-game-sequels/qwen3-1.7b-balanced-v1/asr/{sid}.json'
    asr=read(source);assert asr['audio_sha256']==m['sha256']
    text='';times=[]
    for w in asr['words']:
        a,b=w['timestamp'];t=norm(w['text'])
        assert a is not None and b is not None and 0<=a<=b<=len(audio)/rate+.04
        for j in range(len(t)):
            text+=t[j];times.append((a+(b-a)*j/len(t),a+(b-a)*(j+1)/len(t)))
    scene=next(s for s in ko['scenes'] if s['id']==sid)
    expected=''.join(norm(x) for x in scene['lines'])
    mapped={};matched=set()
    for tag,a,b,c,d in difflib.SequenceMatcher(None,expected,text,autojunk=False).get_opcodes():
        if tag=='equal':
            for j in range(b-a):mapped[a+j]=times[c+j];matched.add(a+j)
        elif b>a and d>c:
            for j in range(b-a):mapped[a+j]=times[c+min(d-c-1,math.floor(j*(d-c)/(b-a)))]
        elif b>a:
            prior=times[max(0,c-1)][1];later=times[min(c,len(times)-1)][0]
            for j in range(b-a):mapped[a+j]=(min(prior,later),max(prior,later))
    paragraphs=[];offset=0
    for i,line in enumerate(scene['lines']):
        count=len(norm(line));vals=[mapped[k] for k in range(offset,offset+count)]
        paragraphs.append(dict(paragraphIndex=i,ko=line,speechStart=vals[0][0],speechEnd=vals[-1][1],normalizedMatch=len(matched.intersection(range(offset,offset+count)))/count));offset+=count
    points=[0];boundaries=[]
    for left,right in zip(paragraphs,paragraphs[1:]):
        lo=round((left['speechEnd']-.045)*rate);hi=round((right['speechStart']+.015)*rate)
        if hi<=lo:
            middle=(left['speechEnd']+right['speechStart'])/2
            lo=round((middle-.2)*rate);hi=round((middle+.2)*rate)
        lo=max(0,lo);hi=min(len(audio),hi);center=(lo+hi)//2
        options=[]
        for k in range(lo,hi,24):
            a=audio[max(0,k-192):min(len(audio),k+192)]
            rms=float(np.sqrt(np.mean(a*a)));peak=float(np.max(np.abs(a)))
            options.append((rms+abs(k-center)/rate*.0004,k,rms,peak))
        _,point,rms,peak=min(options)
        assert point>points[-1]
        points.append(point)
        boundaries.append(dict(afterParagraph=left['paragraphIndex']+1,sample=point,seconds=point/rate,rms16ms=rms,peak16ms=peak,previousWordEnd=left['speechEnd'],nextWordStart=right['speechStart'],timestampOverlap=right['speechStart']<left['speechEnd'],directRangeReview=False))
    points.append(len(audio))
    for i,p in enumerate(paragraphs):p.update(pcmStartSample=points[i],pcmEndSample=points[i+1],pcmSeconds=(points[i+1]-points[i])/rate)
    repairs=[]
    for r in request['repairs']:
        if r['scene']==sid:
            p=paragraphs[r['paragraphIndex']]
            repairs.append(dict(id=r['id'],paragraphIndex=r['paragraphIndex'],originalSampleRange=[p['pcmStartSample'],p['pcmEndSample']],oldParagraphSeconds=p['pcmSeconds'],originalKo=r['originalKo']))
    rows.append(dict(scene=sid,audioPath=m['path'],audioSha256=m['sha256'],samples=len(audio),sampleRate=rate,asrPath=source.relative_to(ROOT).as_posix(),asrSha256=sha(source),paragraphs=paragraphs,boundaries=boundaries,repairs=repairs,allOriginalPCMUnchanged=True,directRangesApproved=False))
target.write_text(json.dumps(dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),scenes=rows,original48ParagraphsUnchanged=True,proposalOnly=True,finalMixApproved=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'scene':x['scene'],'repairs':x['repairs'],'boundaries':x['boundaries']} for x in rows],ensure_ascii=False))
