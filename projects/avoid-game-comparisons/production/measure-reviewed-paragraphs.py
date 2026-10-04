"""Propose current PCM paragraph boundaries from already reviewed ASR; no audio changes."""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,math,re,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub(r'[^a-z0-9가-힣]','',t.lower())
def measure(s,m,asr,english):
    file=ROOT/m['path'];x,rate=sf.read(file,dtype='float32');assert rate==24000 and x.ndim==1 and sha(file)==m['sha256']
    assert asr.get('audio_sha256',asr.get('audioSha256'))==sha(file)
    words=asr['words'];text='';times=[]
    for w in words:
        t=norm(w['text']);a,b=w['timestamp'];assert a is not None and b is not None and 0<=a<=b<=len(x)/rate+.04
        for j,ch in enumerate(t):
            text+=ch;times.append((a+(b-a)*j/max(1,len(t)),a+(b-a)*(j+1)/max(1,len(t))))
    expected=''.join(norm(z) for z in s['lines']);matcher=difflib.SequenceMatcher(None,expected,text,autojunk=False);mapped={};matched=set()
    for tag,a,b,c,d in matcher.get_opcodes():
        if tag=='equal':
            for j in range(b-a):mapped[a+j]=times[c+j];matched.add(a+j)
        elif b>a and d>c:
            for j in range(b-a):mapped[a+j]=times[c+min(d-c-1,math.floor(j*(d-c)/(b-a)))]
        elif b>a:
            prior=times[max(0,c-1)][1];later=times[min(c,len(times)-1)][0]
            for j in range(b-a):mapped[a+j]=(min(prior,later),max(prior,later))
    ps=[];offset=0;assert len(english)==len(s['lines'])
    for i,line in enumerate(s['lines']):
        count=len(norm(line));vals=[mapped[k] for k in range(offset,offset+count)]
        ps.append(dict(paragraph=i+1,ko=line,en=english[i],speechStart=vals[0][0],speechEnd=vals[-1][1],normalizedCharacterMatch=len(matched.intersection(range(offset,offset+count)))/count));offset+=count
    boundaries=[0];quiet=[]
    for left,right in zip(ps,ps[1:]):
        lo=max(0,round((left['speechEnd']-.045)*rate));hi=min(len(x),round((right['speechStart']+.015)*rate))
        if hi<=lo:
            midpoint=(left['speechEnd']+right['speechStart'])/2;lo=max(0,round((midpoint-.2)*rate));hi=min(len(x),round((midpoint+.2)*rate))
        win=384;center=(lo+hi)//2;cs=[]
        for k in range(lo,hi,24):
            q=x[max(0,k-win//2):min(len(x),k+win//2)];r=float(np.sqrt(np.mean(q*q)));cs.append((r+abs(k-center)/rate*.0004,k,r,float(np.max(np.abs(q)))))
        _,point,rms,peak=min(cs);assert point>boundaries[-1]
        boundaries.append(point);quiet.append(dict(afterParagraph=left['paragraph'],sample=point,seconds=point/rate,rms16ms=rms,peak16ms=peak,asrTimestampOverlap=right['speechStart']<left['speechEnd'],preserveAllPcm=True,newTimingJoinReviewRequired=True))
    boundaries.append(len(x))
    for i,p in enumerate(ps):p.update(pcmFromSample=boundaries[i],pcmToSample=boundaries[i+1],pcmSeconds=(boundaries[i+1]-boundaries[i])/rate)
    return dict(id=s['id'],title=s['title'],classification='explanation' if s['id'] in ['01','03','05','07','09','11'] else 'actual',audio=m['path'],audioSha256=m['sha256'],samples=len(x),sampleRate=rate,speechSeconds=len(x)/rate,minimumSpeechFrames=math.ceil(len(x)*60/rate),paragraphs=ps,quietBoundaries=quiet,allPcmUnchanged=True)
def main():
    scope=sys.argv[1] if len(sys.argv)>1 else 'original12';assert scope in ['original12','expanded14']
    target=BASE/f'measured-paragraphs-{scope}.json';assert not target.exists(),'Preserve existing measured evidence.'
    ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json');current=read(BASE/'narration-current-index.json');assert current['fullCurrentHashAsrApproved']
    ms={x['scene']:x for x in current['measurements']}
    if scope=='expanded14':
        add=read(BASE/'additive-narration-direct-review.json');assert add['allSixParagraphsTechnicallyReviewed']
        ms.update({x['id']:x for x in read(BASE/'additive-narration-tts-execution.json')['results']})
    rows=[]
    for s in ko['scenes']:
        if s['id'] not in ms:continue
        sid=s['id'];m=ms[sid]
        if sid in ['06','10']:asr_path=BASE/f'asr-post-repair-local/{sid}-whole-v2.json'
        elif sid in ['13','14']:asr_path=BASE/f'additive-whole-asr-local/{sid}.json'
        else:asr_path=ROOT/f'shared/output/narration/avoid-game-comparisons/qwen3-1.7b-balanced-v1/asr/{sid}.json'
        english=next(t for t in en['scenes'] if t['id']==sid)['lines'];row=measure(s,m,read(asr_path),english);row['asrEvidence']={'path':asr_path.relative_to(ROOT).as_posix(),'sha256':sha(asr_path)};rows.append(row)
    assert len(rows)==(12 if scope=='original12' else 14)
    d=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),scope=scope,status='measured-PCM-paragraph-proposal-not-final-edit',scenes=rows,scriptKoSha256=sha(BASE.parent/'script/narration.ko.json'),scriptEnSha256=sha(BASE.parent/'script/narration.en.json'),finalTimingApproved=False,finalRatioApproved=False,humanWholeListening='pending')
    target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'id':s['id'],'seconds':s['speechSeconds'],'paragraphs':[[p['paragraph'],round(p['speechStart'],3),round(p['speechEnd'],3),round(p['pcmSeconds'],3)] for p in s['paragraphs']]} for s in rows]))
if __name__=='__main__':main()
