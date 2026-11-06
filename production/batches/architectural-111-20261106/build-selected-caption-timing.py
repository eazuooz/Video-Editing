"""CPU-only07.04 literal caption/diagram timing from verified selected voice ASR.

No voice/model, renderer, media encoder, platform or first-film mutation.
Assembled component recognition remains labelled as such; alignment is not
listening approval and never hides literal ASR differences with aliases.
"""
from __future__ import annotations
import argparse, difflib, hashlib, importlib.util, json, math, re, wave
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROJECT=ROOT/'projects/shorts-leveldesign-07-04'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-07-04')
FPS=60

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
base=module('selected_caption_first_helpers',HERE/'build-first-timeline.py')
asr=base.asr
def frame(seconds):return int(math.floor(seconds*FPS+.5))
def same_text(a,b):return re.sub(r'\s+','',a)==re.sub(r'\s+','',b)

class Pending(RuntimeError):pass

def voice_binding(voice,review,narration):
    if voice.get('topicId')!='07.04' or len(voice.get('sceneWavs',[]))!=14:raise Pending('Exact completed07.04 voice evidence required')
    for key,record in [('aggregateSHA256',voice['aggregateWav']),('timingSHA256',voice['timing'])]:
        if sha(record['path'])!=record['sha256'] or review.get(key)!=record['sha256']:raise Pending('ASR review is not bound to current unchanged voice/timing')
    if review.get('voiceFingerprint')!=voice['fingerprint']:raise Pending('ASR belongs to another synthesis version')
    timing=read(voice['timing']['path']);entries=timing['entries'];position=0;digest_pcm=hashlib.sha256();bounds={}
    if timing['sample_rate']!=24000 or len(entries)!=14:raise Pending('Canonical voice clock differs')
    for chunk,entry,mapping in zip(voice['sceneWavs'],entries,voice['paragraphMapping']):
        if sha(chunk['path'])!=chunk['sha256']:raise Pending('Selected raw voice chunk changed')
        with wave.open(chunk['path'],'rb') as audio:
            if (audio.getnchannels(),audio.getsampwidth(),audio.getframerate(),audio.getnframes())!=(1,2,24000,chunk['frames']):raise Pending('Raw PCM format/frame count differs')
            data=audio.readframes(audio.getnframes())
        if hashlib.sha256(data).hexdigest()!=chunk['pcmSHA256']:raise Pending('Raw chunk PCM differs')
        if entry['scene_id']!=mapping['sceneId'] or entry['text']!=mapping['canonicalText'] or abs(entry['start']-position/24000)>1e-9:raise Pending('Raw spoken text/order/start clock differs')
        start=position;position+=chunk['frames'];digest_pcm.update(data)
        if abs(entry['end']-position/24000)>1e-9:raise Pending('Raw end clock differs')
        bounds[mapping['sceneId']]=(start,position)
    with wave.open(voice['aggregateWav']['path'],'rb') as audio:
        aggregate=audio.readframes(audio.getnframes())
        if audio.getnframes()!=position:raise Pending('Canonical aggregate frame count differs')
    if digest_pcm.hexdigest()!=hashlib.sha256(aggregate).hexdigest() or digest_pcm.hexdigest()!=voice['aggregateWav']['pcmSHA256']:raise Pending('Canonical PCM is not exact selected raw concatenation')
    for n,p in enumerate(review['paragraphs'],1):
        mappings=[m for m in voice['paragraphMapping'] if m['paragraph']==n];ids=[m['sceneId'] for m in mappings]
        if not same_text(' '.join(m['canonicalText'] for m in mappings),narration['narrationKo'][n-1]) or p['sceneIds']!=ids:raise Pending('ASR paragraph coverage/order differs')
        first,last=bounds[ids[0]][0],bounds[ids[-1]][1]
        if (p['startSample'],p['endSample'])!=(first,last) or abs(p['start']-first/24000)>1e-9 or abs(p['end']-last/24000)>1e-9:raise Pending('ASR paragraph clock differs from actual canonical PCM')
    return dict(voiceFingerprint=voice['fingerprint'],aggregate=voice['aggregateWav'],timing=voice['timing'],rawSelectedTakes=14,canonicalExactConcatVerified=True,automaticSpeechPass=False)

def verified_asr_review(path):
    """Verify existing immutable summary against all exact raw task caches."""
    qa=module('selected_caption_current_qa',HERE/'run-selected-voice-qa.py');job=qa.prepare_job()
    expected=Path(job['output'])/'review.json'
    if Path(path).resolve()!=expected.resolve() or not expected.is_file():raise Pending('Use current complete selected ASR review, not another file/version')
    current=read(expected)
    if any(qa.cached(job,t) is None for t in job['identity']['tasks']):raise Pending('Missing independently recognized take/join cache')
    # Existing summary is required above; summary() only verifies identical
    # immutable JSON here. It cannot create a missing review in this path.
    if qa.summary(job)!=current:raise Pending('Existing ASR summary differs from exact blind task caches')
    return current

def literal_alignment(expected,recognized,words,start,end):
    if not words or not 0<=start<end:raise Pending('Positive actual PCM interval and blind ASR words required')
    text='';owners=[];previous=start
    for index,w in enumerate(words):
        a,b=w['timestamp']
        if a is None or b is None or not all(math.isfinite(x) for x in (a,b)) or a>b or a<start-.08 or b>end+.08 or a<previous-.08:
            raise Pending('Blind ASR clock is missing, nonfinite, backwards or outside exact PCM')
        previous=a;part=asr.folded(w['text']);text+=part;owners.extend([index]*len(part))
    if text!=asr.folded(recognized):raise Pending('Word transcript differs from raw assembled recognition literal')
    normalized=asr.folded(expected);mapping={};differences=[]
    for kind,i,j,k,l in difflib.SequenceMatcher(None,normalized,text,autojunk=False).get_opcodes():
        if kind=='equal':mapping.update((i+n,k+n) for n in range(j-i))
        else:differences.append(dict(kind=kind,expected=normalized[i:j],recognized=text[k:l],expectedRange=[i,j],recognizedRange=[k,l]))
    if not mapping:raise Pending('No literal anchors; pronunciation aliases are forbidden')
    diagnostics=[]
    def boundary(position):
        if not 0<=position<=len(normalized):raise ValueError('Character boundary outside authored paragraph')
        if position==0:return max(start,words[owners[min(mapping.values())]]['timestamp'][0])
        if position==len(normalized):return min(end,words[owners[max(mapping.values())]]['timestamp'][1])
        left=max((i for i in mapping if i<position),default=None);right=min((i for i in mapping if i>=position),default=None)
        if left is None or right is None or position-1-left>12 or right-position>12:raise Pending('Caption boundary lacks nearby literal word anchors')
        li,ri=owners[mapping[left]],owners[mapping[right]]
        if li==ri:
            indices=[i for i,v in enumerate(owners) if v==li];fraction=(mapping[left]+1-indices[0])/len(indices)
            a,b=words[li]['timestamp'];value=a+(b-a)*fraction
            diagnostics.append(dict(position=position,method='within-ASR-word interpolation',sourceWordIndex=li,humanTimingReviewRequired=True))
        else:
            value=(words[li]['timestamp'][1]+words[ri]['timestamp'][0])/2
            if right-left>1:diagnostics.append(dict(position=position,method='adjacent literal anchors across raw ASR difference',leftWord=li,rightWord=ri,humanTimingReviewRequired=True))
        return max(start,min(end,value))
    def span(begin,finish):
        indices=sorted(set(owners[v] for k,v in mapping.items() if begin<=k<finish))
        return dict(expectedNormalizedRange=[begin,finish],sourceWordIndices=indices,recognizedLiteral=' '.join(words[i]['text'] for i in indices),aliasesApplied=False)
    return boundary,span,dict(expectedLiteral=expected,recognizedLiteral=recognized,comparison=asr.comparison(expected,recognized),alignmentDifferences=differences,boundaryDiagnostics=diagnostics,aliasesApplied=False,humanListening=False,automaticSpeechPass=False)

def display_cue(row,lang,group,start,end,normal,bold):
    if end<=start:raise Pending('Authored display cue has no positive actual frame span')
    text=row['text'];lines=row['lines']
    if not 1<=len(lines)<=2 or not same_text(' '.join(lines),text):raise Pending('Authored display lines omit text or exceed two lines')
    emph=base.one_line_emphasis(text,lines,row.get('emphasis',[]))
    cursor=0
    for line in lines:
        offset=text.find(line,cursor)
        if offset<0:raise Pending('Display line is not an exact authored substring')
        width=normal.getlength(line)
        if emph and offset<=emph[0]['start']<emph[0]['end']<=offset+len(line):
            a,b=emph[0]['start']-offset,emph[0]['end']-offset
            width=normal.getlength(line[:a])+bold.getlength(line[a:b])+normal.getlength(line[b:])
        if width>800:raise Pending('Actual48px mixed-weight display line exceeds800px; never shrink font')
        cursor=offset+len(line)
    return dict(id=row['id'],paragraph=group['paragraph'],groupId=group['id'],beatId=group['beatId'],language=lang,startFrame=start,endFrameExclusive=end,text=text,lines=lines,emphasis=emph,humanTimingReviewRequired=True)

def build(narration,clauses,review,diagram):
    normal,bold,_=base.fonts();paragraphs=review['paragraphs']
    if sha(clauses['style']['fontPath'])!=clauses['style']['fontSHA256']:raise Pending('Measured caption font changed')
    if len(paragraphs)!=7 or len(narration['narrationKo'])!=7:raise Pending('Exactly selected07.04 seven paragraphs required')
    cues={'ko':[],'en':[]};bound=[];paragraph_rows=[];group_frames=[]
    for n,(ko,en,p) in enumerate(zip(narration['narrationKo'],narration['paragraphsEn'],paragraphs),1):
        if p['paragraph']!=n or p['recognitionBasis']!='assembled-from-blind-component-takes' or p['expectedLiteral']!=ko:
            raise Pending('Exact paragraph/source recognition provenance required')
        rows=[c for c in clauses['groups'] if c['paragraph']==n]
        if not same_text(' '.join(c['ko'] for c in rows),ko) or not same_text(' '.join(c['en'] for c in rows),en):raise Pending('Caption groups must retain exact complete KO/EN')
        get,span,diagnostic=literal_alignment(ko,p['recognizedLiteral'],p['globalWords'],p['start'],p['end'])
        pos=0
        for row in rows:
            begin=pos;pos+=len(asr.folded(row['ko']));a,b=frame(get(begin)),frame(get(pos))
            if b<=a:raise Pending('Authored semantic group has no positive actual frame span')
            for lang in ('ko','en'):
                if not same_text(' '.join(c['text'] for c in row[lang+'Cues']),row[lang]):raise Pending('Display cue omits or rewrites source group')
            cursor=begin
            for cue in row['koCues']:
                finish=cursor+len(asr.folded(cue['text']));out=display_cue(cue,'ko',row,frame(get(cursor)),frame(get(finish)),normal,bold)
                out.update(literalAlignment=span(cursor,finish),recognitionBasis=p['recognitionBasis']);cues['ko'].append(out);cursor=finish
            if cursor!=pos:raise Pending('KO display coverage differs from semantic group')
            english=row['enCues']
            if len(english)==1:boundaries=[a,b]
            elif len(english)==2:
                anchor=asr.folded(row.get('enCueSplitAnchorKo') or '');grouptext=asr.folded(row['ko'])
                if anchor:
                    if grouptext.count(anchor)!=1:raise Pending('Two EN displays need one unique literal Korean speech split anchor')
                    relative=grouptext.index(anchor)
                    if not 0<relative<len(grouptext):raise Pending('EN translation split needs an interior Korean speech boundary')
                    middle=frame(get(begin+relative))
                elif row.get('translatedTimingReviewPending') is True:
                    candidates=[frame((x['timestamp'][1]+y['timestamp'][0])/2) for x,y in zip(p['globalWords'],p['globalWords'][1:])]
                    candidates=[x for x in candidates if a<x<b]
                    if not candidates:raise Pending('No actual Korean word boundary inside declared translated-display fallback')
                    middle=min(candidates,key=lambda x:abs(x-(a+b)/2))
                else:raise Pending('Two EN display clauses need an authored speech split or explicitly pending translated timing')
                boundaries=[a,middle,b]
            else:raise Pending('More than two translated displays needs an explicit semantic KO anchor map')
            for cue,left,right in zip(english,boundaries,boundaries[1:]):
                out=display_cue(cue,'en',row,left,right,normal,bold)
                fallback=len(english)>1 and not row.get('enCueSplitAnchorKo')
                out.update(timingBasis=('Declared translation-order fallback: nearest actual Korean word boundary to group temporal midpoint; untranslated subclause semantic timing NOT verified' if fallback else 'Translated display mapped to authored semantic Korean speech boundary; not English ASR'),spokenGroupLiteralKo=row['ko'],enCueSplitAnchorKo=row.get('enCueSplitAnchorKo'),translatedTimingReviewPending=bool(row.get('translatedTimingReviewPending')),recognitionBasis=p['recognitionBasis']);cues['en'].append(out)
            group_frames.append(dict(id=row['id'],paragraph=n,beatId=row['beatId'],startFrame=a,endFrameExclusive=b,literalAlignment=span(begin,pos)))
        for item in [x for x in diagram['cueKeyframes'] if x['paragraph']==n]:
            phrase=asr.folded(item['exactSpokenAnchorKo']);whole=asr.folded(ko)
            if whole.count(phrase)!=1:raise Pending('Diagram cue must have one exact unique spoken anchor')
            begin=whole.index(phrase);finish=begin+len(phrase)
            bound.append(dict(id=item['id'],paragraph=n,exactSpokenAnchorKo=item['exactSpokenAnchorKo'],startFrame=frame(get(begin)),endFrameExclusive=frame(get(finish)),literalAlignment=span(begin,finish),basis='Actual blind-component ASR word alignment, not normalized draft fraction',humanTimingReviewRequired=True))
        paragraph_rows.append(dict(paragraph=n,startFrame=frame(p['start']),endFrameExclusive=frame(p['end']),startSample=p['startSample'],endSample=p['endSample'],sceneIds=p['sceneIds'],recognitionBasis=p['recognitionBasis'],alignment=diagnostic))
    for language,rows in cues.items():
        if any(a['endFrameExclusive']>b['startFrame'] for a,b in zip(rows,rows[1:])):raise Pending(language+' ASR-derived caption cues overlap')
    return dict(schemaVersion='07-04-selected-caption-timing-v1',topicId='07.04',fps=FPS,totalFrames=math.ceil(paragraphs[-1]['end']*FPS),captions=cues,groups=group_frames,paragraphs=paragraph_rows,diagramCues=bound,automaticSpeechPass=False,actualListening=False,actualFinalPlayback=False,platformActions=[])

def srt(cues,lang):
    def stamp(f):
        ms=round(f*1000/FPS);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
    return '\n\n'.join(f"{i}\n{stamp(c['startFrame'])} --> {stamp(c['endFrameExclusive'])}\n{c['text']}" for i,c in enumerate(cues,1))+'\n'

def diagram_cue_payload(timing,segment,refs,voice):
    if segment not in ('p2','p6','p7'):raise ValueError('Only selected three diagram segments permitted')
    n=int(segment[1:]);paragraph=next(p for p in timing['paragraphs'] if p['paragraph']==n)
    actual=[c for c in timing['diagramCues'] if c['paragraph']==n]
    if len(actual)!=4:raise Pending('Exactly four authored actual speech anchors required per diagram')
    start=actual[0]['startFrame'] if n==6 else paragraph['startFrame'];end=paragraph['endFrameExclusive']
    cues=[dict(id=c['id'],frame=c['startFrame']-start) for c in actual]
    if not 0<=start<end or any(not 0<=c['frame']<end-start for c in cues) or any(a['frame']>=b['frame'] for a,b in zip(cues,cues[1:])):raise Pending('Actual diagram cue frames must be strictly ordered inside the exact segment')
    return dict(schemaVersion='07-04-authored-diagram-cues-v1',topicId='07.04',segment=segment,timingStatus='actual-asr-clause-aligned',segmentStartGlobalFrame=start,segmentEndGlobalFrameExclusive=end,totalFrames=end-start,cues=cues,scenePlan=refs['scenePlan'],narration=refs['narration'],voiceEvidence=refs['voiceEvidence'],voiceWav=voice['aggregateWav'],captionTiming=refs['captionTiming'],alignment=dict(kind='actual-blind-asr-word-timestamps',review=refs['asrReview'],voiceFingerprint=voice['fingerprint'],voicePcmSHA256=voice['aggregateWav']['pcmSHA256'],narrationSHA256=refs['narration']['sha256']),actualListening=False,humanTimingReviewRequired=True,rendererStarted=False,platformActions=[])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--asr-review',required=True);parser.add_argument('--voice-evidence',default='C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/07-04-voice-evidence.json');parser.add_argument('--write',action='store_true');args=parser.parse_args()
    paths=[PROJECT/'narration-draft.json',PROJECT/'caption-clauses-v1.json',Path(args.asr_review).resolve(),PROJECT/'2d-scene-plan-v1.json',Path(__file__),HERE/'build-first-timeline.py',HERE/'run-first-asr.py',HERE/'run-selected-voice-qa.py',Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')]
    paths.append(Path(args.voice_evidence).resolve());inputs=[pin(x) for x in paths]
    review=verified_asr_review(paths[2]);binding=voice_binding(read(paths[-1]),review,read(paths[0]));result=build(read(paths[0]),read(paths[1]),review,read(paths[3]));result['voiceBinding']=binding;result['inputs']=inputs;result['fingerprint']=digest(inputs)
    if not args.write:print(json.dumps(dict(ready=True,captions={k:len(v) for k,v in result['captions'].items()},diagramCues=len(result['diagramCues']),fingerprint=result['fingerprint'],written=False)));return
    target=MEDIA/'caption-timing'/result['fingerprint'][:24];target.mkdir(parents=True,exist_ok=True)
    outputs={'caption-timing.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n','captions.ko.srt':srt(result['captions']['ko'],'ko'),'captions.en.srt':srt(result['captions']['en'],'en')}
    for name,text in outputs.items():
        path=target/name
        if path.exists() and path.read_text(encoding='utf-8-sig')!=text:raise RuntimeError('Preserve differing existing caption output')
        if not path.exists():path.write_text(text,encoding='utf-8')
    refs=dict(scenePlan=pin(paths[3]),narration=pin(paths[0]),voiceEvidence=pin(paths[-1]),captionTiming=pin(target/'caption-timing.json'),asrReview=pin(paths[2]));voice=read(paths[-1])
    for segment in ('p2','p6','p7'):
        path=target/(segment+'.authored-cues.json');payload=diagram_cue_payload(result,segment,refs,voice);text=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
        if path.exists() and path.read_text(encoding='utf-8-sig')!=text:raise RuntimeError('Preserve differing previous authored diagram cue plan')
        if not path.exists():path.write_text(text,encoding='utf-8')
    if inputs!=[pin(x) for x in paths]:raise RuntimeError('Caption inputs changed during CPU write; preserve output and inspect')
    print(json.dumps(dict(output=str(target),fingerprint=result['fingerprint'],automaticSpeechPass=False)))

if __name__=='__main__':main()
