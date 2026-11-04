"""Measure caption/animation times from actual speech; preserve every sentence.

Outputs are alignment candidates requiring transcript and encoded-frame review.
No duration estimates are substituted when a phrase cannot be aligned.
"""
from pathlib import Path
from datetime import datetime,timezone
from difflib import SequenceMatcher
import hashlib,json,math,re
P=Path(__file__).resolve().parents[1];R=P.parents[1];A=P/'production/local/audio-v1';OUT=P/'production/local/edit-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ALIASES={'brdf':'비알디에프','rgb':'알지비','hlsl':'에이치엘에스엘','sh':'에스에이치','uv':'유브이','phong':'퐁','blinn':'블린','lambert':'램버트','gouraud':'구로','reflect':'리플렉트'}
DIGITS='영일이삼사오육칠팔구'
def integer_ko(n):
    n=int(n)
    if n==0:return '영'
    if n>=10000:return ''.join(DIGITS[int(x)] for x in str(n))
    out=''
    for power,unit in ((1000,'천'),(100,'백'),(10,'십'),(1,'')):
        d,n=divmod(n,power)
        if d:out+=('' if d==1 and power>1 else DIGITS[d])+unit
    return out
def number_ko(s):
    a,*b=s.split('.')
    return integer_ko(a)+('점'+''.join(DIGITS[int(x)] for x in b[0]) if b else '')
def normalized(s):
    s=s.lower()
    for a,b in sorted(ALIASES.items(),key=lambda p:-len(p[0])):s=re.sub(r'\b'+re.escape(a)+r'\b',b,s)
    s=re.sub(r'\d+(?:\.\d+)?',lambda m:number_ko(m.group()),s)
    return ''.join(c for c in s if c.isalnum())
def map_chars(expected,words):
    observed='';owners=[]
    for w in words:
        if None in w['timestamp']:continue
        s=normalized(w['text']);observed+=s;owners.extend([w]*len(s))
    expected=normalized(expected);match=SequenceMatcher(None,expected,observed,autojunk=False)
    mapping={a+k:b+k for a,b,n in match.get_matching_blocks() for k in range(n)}
    return expected,observed,mapping,owners,match
def phrase_time(text,phrase,mapping,owners,start_offset=None):
    start=text.find(phrase) if start_offset is None else start_offset
    if start<0:raise ValueError(('missing literal anchor',phrase))
    if text[start:start+len(phrase)]!=phrase:raise ValueError(('invalid anchor offset',phrase,start))
    offset=len(normalized(text[:start]));end=offset+len(normalized(phrase))
    matched=[i for i in range(offset,end) if i in mapping]
    if not matched or matched[0]-offset>2 or len(matched)/max(1,end-offset)<.7:raise ValueError(('uncertain anchor',phrase))
    w=owners[mapping[matched[0]]]
    return float(w['timestamp'][0]),{'phrase':phrase,'matchedFraction':len(matched)/(end-offset),'word':w}
def chunks(text,limit=32):
    """Retain all text; punctuation first, then complete word boundaries."""
    result=[]
    for m in re.finditer(r'.+?(?:[,.!?;](?=\s|$)|$)',text):
        value=m.group().strip()
        if not value:continue
        words=value.split();part=[]
        for w in words:
            if part and len(' '.join(part+[w]))>limit:result.append(' '.join(part));part=[]
            part.append(w)
        if part:result.append(' '.join(part))
    assert re.sub(r'\s','',text)==re.sub(r'\s','',' '.join(result))
    return result
def display_span(spoken,display,a,b):
    """Project the spoken clause onto canonical display spelling."""
    def boundary(pos):
        for tag,i,j,u,v in SequenceMatcher(None,spoken,display,autojunk=False).get_opcodes():
            if i<=pos<=j:
                return u+(pos-i) if tag=='equal' else round(u+(v-u)*(pos-i)/max(1,j-i))
        return len(display)
    return display[boundary(a):boundary(b)].strip()
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def srt(path,rows):path.write_text('\n\n'.join(f"{i+1}\n{stamp(x['start']+2)} --> {stamp(x['end']+2)}\n{x['text']}" for i,x in enumerate(rows))+'\n',encoding='utf-8')
def main():
    control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert control['productionAllowedNow'] and P.name in control['projectSlugs']
    timing=read(A/'narration.timing.json');asr=read(A/'review/source-full-asr.timestamps.json');bindings=read(P/'planning/scene-bindings.json')
    assert asr['audio_sha256']==sha(A/'narration.wav')
    scripts={s['id']:s for s in read(P/'script/narration.ko.json')['scenes']}
    en={s['id']:s for s in read(P/'script/narration.en.json')['scenes']}
    bilingual=read(P/'planning/bilingual-caption-map.json')
    assert bilingual['status']=='complete-semantic-map'
    assert bilingual['koSha256']==sha(P/'script/narration.ko.json') and bilingual['enSha256']==sha(P/'script/narration.en.json')
    bilingual_rows={s['id']:s['groups'] for s in bilingual['scenes']}
    scenes=[];ko_cues=[];en_cues=[];flags=[];entries=timing['entries']
    for i,e in enumerate(entries):
        sid=e['scene_id'];row=next(r for r in bindings['scenes'] if r['id']==sid);speech=e['text'];display=e['display_text']
        words=[w for w in asr['chunks'] if None not in w['timestamp'] and e['start']<=w['timestamp'][0]<e['end']+.01]
        expected,observed,mapping,owners,match=map_chars(speech,words)
        coverage=len(mapping)/max(1,len(expected))
        if coverage<.93:flags.append({'scene':sid,'type':'source-transcript-difference','coverage':coverage,'expected':speech,'recognized':' '.join(w['text'] for w in words),'opcodes':match.get_opcodes()})
        start_frame=round(e['start']*60);end_frame=round(entries[i+1]['start']*60) if i+1<len(entries) else math.ceil(timing['duration_seconds']*60)
        cue=dict(row['cue']);cue['duration']=(end_frame-start_frame)/60
        times=[];proof=[]
        for phrase in row.get('speechAnchorPhrases',[]):
            try:t,ev=phrase_time(speech,phrase,mapping,owners);times.append(round((t-start_frame/60)*60)/60);proof.append(ev)
            except ValueError as exc:flags.append({'scene':sid,'type':'unresolved-animation-anchor','detail':repr(exc)})
        if times and times!=sorted(times):flags.append({'scene':sid,'type':'nonmonotonic-animation-steps','times':times})
        if times:cue['stepTimes']=times
        value_times=[];value_numbers=[];value_evidence=[]
        for anchor in row.get('valueAnchorPhrases',[]):
            try:
                t,ev=phrase_time(speech,anchor['phrase'],mapping,owners)
                value_times.append(round((t-start_frame/60)*60)/60);value_numbers.append(anchor['value']);value_evidence.append(ev)
            except ValueError as exc:flags.append({'scene':sid,'type':'unresolved-variable-anchor','detail':repr(exc)})
        if value_times:
            cue['valueTimes']=value_times;cue['values']=value_numbers
        if cue.get('diagram','').startswith(('math:','advanced:')) and not times:flags.append({'scene':sid,'type':'missing-required-animation-steps'})
        cursor=0;local=[]
        for clause in chunks(speech):
            a=speech.find(clause,cursor);b=a+len(clause);cursor=b
            try:t,ev=phrase_time(speech,clause,mapping,owners,a)
            except ValueError as exc:flags.append({'scene':sid,'type':'unresolved-caption-start','detail':repr(exc)});continue
            local.append({'scene':sid,'start':t,'end':e['end'],'text':display_span(speech,display,a,b),'spoken':clause,'evidence':ev})
        for x,y in zip(local,local[1:]):x['end']=y['start']
        for x in local:
            if x['end']<=x['start']:flags.append({'scene':sid,'type':'zero-caption','text':x['text']})
        ko_cues+=local
        # Directly reviewed meaning groups may join or split sentence boundaries.
        # Group endpoints use the corresponding actual Korean word timestamps.
        ks=[m for m in re.finditer(r'.+?(?:[.!?](?=\s|$)|$)',speech) if m.group().strip()]
        es=[x.strip() for x in re.split(r'(?<=[.!?])\s+',en[sid]['lines'][e['paragraph']-1]) if x.strip()]
        groups=bilingual_rows[sid]
        assert sum(g['koCount'] for g in groups)==len(ks) and sum(g['enCount'] for g in groups)==len(es)
        for group in groups:
            j=group['koStart'];after=j+group['koCount'];km=ks[j]
            et=' '.join(es[group['enStart']:group['enStart']+group['enCount']]);assert et==group['en']
            try:
                phrase=km.group().strip();begin,_=phrase_time(speech,phrase,mapping,owners,speech.find(phrase,km.start()))
                if after<len(ks):
                    nm=ks[after];np=nm.group().strip();end=phrase_time(speech,np,mapping,owners,speech.find(np,nm.start()))[0]
                else:end=e['end']
            except ValueError as exc:
                flags.append({'scene':sid,'type':'unresolved-bilingual-group','detail':repr(exc)});continue
            parts=chunks(et,68);size=sum(len(x) for x in parts);t=begin
            for part in parts:
                finish=t+(end-begin)*len(part)/size
                en_cues.append({'scene':sid,'start':t,'end':finish,'text':part,'timingBasis':'reviewed meaning group / actual KO words / English reading proportions','listeningVerified':False});t=finish
        scenes.append({'id':sid,'startFrame':start_frame,'endFrame':end_frame,'cue':cue,'cueEvidence':proof,'valueEvidence':value_evidence,'spokenEnd':e['end'],'sourceAsrCoverage':coverage,'actualGamePart':row.get('actualGamePart')})
    report={'createdAt':datetime.now(timezone.utc).isoformat(),'narrationSha256':asr['audio_sha256'],'bindingsSha256':sha(P/'planning/scene-bindings.json'),'timingSha256':sha(A/'narration.timing.json'),'status':'needs-targeted-review' if flags else 'word-aligned-requires-integrated-review','flags':flags,'scenes':scenes,'ko':ko_cues,'en':en_cues,'humanListening':False,'finalCompositeQa':False}
    OUT.mkdir(parents=True,exist_ok=True);save(OUT/'word-aligned-timeline.json',report)
    if not flags:srt(OUT/'narration.ko.srt',ko_cues);srt(OUT/'narration.en.srt',en_cues)
    print(json.dumps({'scenes':len(scenes),'koCues':len(ko_cues),'enCues':len(en_cues),'requiresReview':len(flags)},ensure_ascii=False))
if __name__=='__main__':main()
