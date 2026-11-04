"""Measure caption/animation times from actual speech; preserve every sentence.

M22–M33 alignment uses source-authored phase anchors.
Outputs are alignment candidates requiring transcript and encoded-frame review.
No duration estimates are substituted when a phrase cannot be aligned.
"""
from pathlib import Path
from datetime import datetime,timezone
from difflib import SequenceMatcher
import argparse,hashlib,json,math,re,copy
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--audio-revision',default='audio-v1');args=ap.parse_args()
c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))['explicitMathRemainingBatch20261104']
assert c['productionAllowedNow'] and args.project in c['projectSlugs'] and args.project!='game-math-shading-lights'
assert re.fullmatch(r'audio-v\d+',args.audio_revision)
P=R/'projects'/args.project;A=P/'production/local'/args.audio_revision;OUT=P/'production/local'/args.audio_revision.replace('audio-','edit-')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ALIASES={'tbn':'티비엔','srgb':'에스알지비','bitangent':'비탄젠트','tangent':'접선','brdf':'비알디에프','rgb':'알지비','hlsl':'에이치엘에스엘','sh':'에스에이치','uv':'유브이','phong':'퐁','blinn':'블린','lambert':'램버트','gouraud':'구로','reflect':'리플렉트',
         'sx':'에스엑스','sy':'에스와이','sz':'에스제트','m':'미터','doom':'둠',
         'n':'엔','l':'엘','r':'알','v':'브이','h':'에이치','x':'엑스','y':'와이','z':'제트','t':'티','s':'에스','p':'피','d':'디','a':'에이','b':'비','c':'씨','e':'이','k':'케이','i':'아이','j':'제이','w':'더블유','u':'유'}
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
def normalize_owned(s,owners):
    s=s.lower()
    def replace(pattern,replacement):
        nonlocal s,owners
        parts=[];mapped=[];cursor=0
        for m in re.finditer(pattern,s):
            value=replacement(m) if callable(replacement) else replacement
            parts.extend([s[cursor:m.start()],value]);mapped.extend(owners[cursor:m.start()]);mapped.extend([owners[m.start()]]*len(value));cursor=m.end()
        parts.append(s[cursor:]);mapped.extend(owners[cursor:]);s=''.join(parts);owners=mapped
    # Orthographic/number-name equivalence only. Unrecognized speech is not
    # rewritten to the expected script; substantive differences stay flagged.
    for source,target in [('쉐이딩','셰이딩'),('쉐이더','셰이더'),('세이더','셰이더'),('두 배','이배'),('두배','이배'),('여덟 제곱','팔제곱'),('여덟제곱','팔제곱'),('둠 쓰리','둠삼')]:replace(re.escape(source),target)
    # Korean particles are attached to Latin symbols (e.g. BRDF가, N과).
    # Latin-only boundaries preserve words such as "normal" while matching those.
    for a,b in sorted(ALIASES.items(),key=lambda p:-len(p[0])):replace(r'(?<![a-z])'+re.escape(a)+r'(?![a-z])',b)
    replace(r'\d+(?:\.\d+)?',lambda m:number_ko(m.group()))
    keep=[i for i,c in enumerate(s) if c.isalnum()]
    return ''.join(s[i] for i in keep),[owners[i] for i in keep]

def normalized(s):return normalize_owned(s,[None]*len(s))[0]
def map_chars(expected,words):
    observed='';owners=[]
    for w in words:
        if None in w['timestamp']:continue
        s=w['text'];observed+=s;owners.extend([w]*len(s))
    # Decimal ASR tokens can be split as "0" + ".5". Normalize the continuous
    # transcript once so the decimal point and its original word origin survive.
    observed,owners=normalize_owned(observed,owners)
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
    """Keep clauses and numeric lists together; balance unavoidable long splits."""
    clauses=[]
    for m in re.finditer(r'.+?(?:[,.!?;](?=\s|$)|$)',text):
        value=m.group().strip()
        if not value:continue
        if clauses and not re.search(r'[.!?]$',clauses[-1]) and len(clauses[-1])+len(value)+1<=limit and (len(clauses[-1])<limit/3 or len(value)<limit/4):
            clauses[-1]+=' '+value
        else:clauses.append(value)
    result=[]
    for value in clauses:
        words=value.split()
        while len(' '.join(words))>limit:
            remaining=' '.join(words);count=math.ceil(len(remaining)/limit);target=len(remaining)/count
            candidates=[i for i in range(1,len(words)) if len(' '.join(words[:i]))<=limit]
            assert candidates,'Single unbreakable token exceeds caption width'
            split=min(candidates,key=lambda i:abs(len(' '.join(words[:i]))-target))
            result.append(' '.join(words[:split]));words=words[split:]
        if words:result.append(' '.join(words))
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
    adjustments_file=P/'planning/caption-reading-adjustments.json'
    adjustments={(x['scene'],x['koStart']):x for x in read(adjustments_file)['groups']}
    scenes=[];ko_cues=[];en_cues=[];flags=[];entries=timing['entries']
    for i,e in enumerate(entries):
        sid=e['scene_id'];row=next(r for r in bindings['scenes'] if r['id']==sid);speech=e['text'];display=e['display_text']
        words=[w for w in asr['chunks'] if None not in w['timestamp'] and e['start']<=w['timestamp'][0]<e['end']+.01]
        expected,observed,mapping,owners,match=map_chars(speech,words)
        coverage=len(mapping)/max(1,len(expected))
        expansion=len(observed)/max(1,len(expected))
        if expansion>1.18:flags.append({'scene':sid,'type':'possible-repeated-or-extra-speech','recognizedLengthRatio':expansion,'recognized':' '.join(w['text'] for w in words)})
        if coverage<.93:flags.append({'scene':sid,'type':'source-transcript-difference','coverage':coverage,'expected':speech,'recognized':' '.join(w['text'] for w in words),'opcodes':match.get_opcodes()})
        start_frame=round(e['start']*60);end_frame=round(entries[i+1]['start']*60) if i+1<len(entries) else math.ceil(timing['duration_seconds']*60)
        cue=copy.deepcopy(row['shot']);duration=(end_frame-start_frame)/60;cue['durationSeconds']=duration
        pairs=[(0.0,0.0)];proof=[];value_evidence=[]
        for anchor in row.get('speechPhaseAnchors',[]):
            try:
                t,ev=phrase_time(speech,anchor['phrase'],mapping,owners,anchor.get('character'))
                localtime=round((t-start_frame/60)*60)/60
                if localtime<0 or localtime>=duration:raise ValueError(('anchor outside paragraph',localtime,duration))
                if localtime==0:pairs[0]=(0.0,anchor['position'])
                else:pairs.append((localtime,anchor['position']))
                proof.append(dict(ev,localSeconds=localtime,phase=anchor['position']))
            except ValueError as exc:flags.append({'scene':sid,'type':'unresolved-animation-anchor','detail':repr(exc)})
        pairs.append((duration,1.0))
        if any(b[0]<=a[0] or b[1]<a[1] for a,b in zip(pairs,pairs[1:])):
            flags.append({'scene':sid,'type':'nonmonotonic-animation-clock','values':pairs})
        time_field,position_field=row.get('clockFields',['phaseSeconds','phasePositions'])
        cue[time_field]=[v[0] for v in pairs];cue[position_field]=[v[1] for v in pairs]
        cursor=0;local=[]
        for clause in chunks(speech):
            a=speech.find(clause,cursor);b=a+len(clause);cursor=b
            try:t,ev=phrase_time(speech,clause,mapping,owners,a)
            except ValueError as exc:flags.append({'scene':sid,'type':'unresolved-caption-start','detail':repr(exc)});continue
            local.append({'scene':sid,'start':t,'end':e['end'],'text':display_span(speech,display,a,b),'spoken':clause,'evidence':ev})
        for x,y in zip(local,local[1:]):x['end']=y['start']
        # Short enumerated values and predicate tails should not flash alone.
        # Join only adjacent fragments inside a sentence, keeping measured starts
        # and ends. Up to two fixed-size lines remain available for the rare join.
        i=0
        while i<len(local):
            x=local[i]
            if x['end']-x['start']<.85:
                if i>0 and not re.search(r'[.!?]$',local[i-1]['text']) and len(local[i-1]['text'])+len(x['text'])<55:
                    left=local[i-1];left.update(end=x['end'],text=left['text']+' '+x['text'],spoken=left['spoken']+' '+x['spoken']);left.setdefault('mergedWordEvidence',[]).append(x['evidence']);local.pop(i);i=max(0,i-1);continue
                if i+1<len(local) and not re.search(r'[.!?]$',x['text']) and len(x['text'])+len(local[i+1]['text'])<55:
                    right=local.pop(i+1);x.update(end=right['end'],text=x['text']+' '+right['text'],spoken=x['spoken']+' '+right['spoken']);x.setdefault('mergedWordEvidence',[]).append(right['evidence']);continue
            i+=1
        for x in local:
            if x['end']<=x['start']:flags.append({'scene':sid,'type':'zero-caption','text':x['text']})
        if re.sub(r'\s','',''.join(x['text'] for x in local))!=re.sub(r'\s','',display):
            flags.append({'scene':sid,'type':'display-text-not-preserved'})
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
            if (sid,j) in adjustments:
                change=adjustments[(sid,j)];assert change['source']==et;et=change['caption']
            try:
                phrase=km.group().strip();begin,_=phrase_time(speech,phrase,mapping,owners,speech.find(phrase,km.start()))
                if after<len(ks):
                    nm=ks[after];np=nm.group().strip();end=phrase_time(speech,np,mapping,owners,speech.find(np,nm.start()))[0]
                else:end=e['end']
            except ValueError as exc:
                flags.append({'scene':sid,'type':'unresolved-bilingual-group','detail':repr(exc)});continue
            parts=chunks(et,68);size=sum(len(x) for x in parts)
            n=0
            while n<len(parts) and len(parts)>1:
                if (end-begin)*len(parts[n])/size<.85:
                    if n>0 and len(parts[n-1])+len(parts[n])+1<=100:
                        parts[n-1]+=' '+parts.pop(n);n=max(0,n-1);continue
                    if n+1<len(parts) and len(parts[n])+len(parts[n+1])+1<=100:
                        parts[n]+=' '+parts.pop(n+1);continue
                n+=1
            size=sum(len(x) for x in parts);t=begin
            for part in parts:
                finish=t+(end-begin)*len(part)/size
                en_cues.append({'scene':sid,'start':t,'end':finish,'text':part,'timingBasis':'reviewed meaning group / actual KO words / English reading proportions','listeningVerified':False});t=finish
        scenes.append({'id':sid,'startFrame':start_frame,'endFrame':end_frame,'shot':cue,'cueEvidence':proof,'valueEvidence':value_evidence,'spokenEnd':e['end'],'sourceAsrCoverage':coverage,'actualGamePart':row.get('actualGamePart')})
    report={'createdAt':datetime.now(timezone.utc).isoformat(),'narrationSha256':asr['audio_sha256'],'bindingsSha256':sha(P/'planning/scene-bindings.json'),'timingSha256':sha(A/'narration.timing.json'),'captionReadingAdjustmentsSha256':sha(adjustments_file),'project':P.name,'status':'needs-targeted-review' if flags else 'word-aligned-requires-integrated-review','flags':flags,'scenes':scenes,'ko':ko_cues,'en':en_cues,'humanListening':False,'finalCompositeQa':False}
    OUT.mkdir(parents=True,exist_ok=True);save(OUT/'word-aligned-timeline.json',report)
    if not flags:srt(OUT/'narration.ko.srt',ko_cues);srt(OUT/'narration.en.srt',en_cues)
    print(json.dumps({'scenes':len(scenes),'koCues':len(ko_cues),'enCues':len(en_cues),'requiresReview':len(flags)},ensure_ascii=False))
if __name__=='__main__':main()
