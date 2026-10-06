"""Prepare literal KO/EN cues from current PCM/ASR; never approve a timeline.

No synthesis, media extraction or canonical script mutation occurs here.
Independent tail windows replace backward whole-ASR timestamps, with their
original evidence retained. Interpolated character anchors are candidates.
"""
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
import argparse, hashlib, json, math, re
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
norm = lambda s: ''.join(c.lower() for c in s if c.isalnum())
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=['v1','v2'],default='v1');args=parser.parse_args()
target = BASE / f'word-caption-candidate-{args.revision}'
assert not target.exists(), 'Preserve prior candidate.'
plan_path = BASE / f'measured-word-timing-candidate-{args.revision}.json'
plan = read(plan_path)
assert not plan['finalTimelineAdopted']
ko_path = BASE.parent / 'script/narration.ko.json'
en_path = BASE.parent / 'script/narration.en.json'
ko = read(ko_path)['scenes']; en = read(en_path)['scenes']
guide_path = BASE.parent / 'planning/observation-guides-v1.json'
guides = read(guide_path)['guides']
extra_inputs=[]
if args.revision=='v2':
    request_path=BASE/'guide12-room-tts-request-v2.json'
    assert read(BASE/'guide12-room-contexts-direct-review-v2.json')['structuralContentReviewComplete']
    corrected=read(request_path)['guides'][0]
    guides=[corrected if g['id']=='12' else g for g in guides]
    extra_inputs=[request_path]
sentences = lambda t: [m.group().strip() for m in re.finditer(r'.+?(?:[.!?](?=\s|$)|$)', t) if m.group().strip()]
scripts = {s['id']: dict(ko=s['lines'], en=next(x['lines'] for x in en if x['id']==s['id'])) for s in ko}
for g in guides:
    scripts[g['id']] = dict(ko=sentences(g['ko']), en=sentences(g['en']))
assert sum(len(s['ko']) for s in scripts.values()) == 70

paragraphs=[]; cues=[]; en_cues=[]; scenes=[]; corrections=[]
for sid, script in scripts.items():
    assert len(script['ko']) == len(script['en'])
    evidence = BASE / ('current-whole-asr-v1' if int(sid)<12 else 'observation-guides-whole-asr-v2') / f'{sid}.json'
    if sid=='12' and args.revision=='v2':evidence=BASE/'guide12-room-whole-asr-v2/12-whole.json'
    d = read(evidence); words = [dict(w) for w in d['words']]
    provenance = [dict(path=rel(evidence), sha256=sha(evidence), kind='whole-current-pcm')]
    if sid in ['06','08','10']:
        tail_path = BASE / 'current-independent-asr-v1' / f'{sid}-complete-tail.json'
        tail = read(tail_path); offset=tail['startSeconds']
        original = [w for w in words if w['timestamp'][0] is not None and w['timestamp'][0]>=offset]
        words = [w for w in words if w['timestamp'][1] is not None and w['timestamp'][1]<=offset]
        words += [dict(text=w['text'], timestamp=[a+offset if a is not None else None for a in w['timestamp']]) for w in tail['words']]
        provenance.append(dict(path=rel(tail_path),sha256=sha(tail_path),kind='independent-complete-tail',offsetSeconds=offset))
        corrections.append(dict(scene=sid,kind='independent-tail-replaces-backward-whole-ASR-anchors',
            preservedWholeEvidence=rel(evidence),preservedOriginalTailWords=original,independentEvidence=rel(tail_path),
            reason='Directly read complete independent context has monotonic anchors; whole-ASR timestamp reversals do not prove repeated speech.',audioChanged=False))
    valid=[]; recognized=''; character_times=[]
    for w in words:
        a,z=w['timestamp']
        if a is None or z is None or z<=a:
            raise AssertionError(f'Invalid timestamp needs direct review: {sid} {w}')
        assert a>=0 and z<=d['seconds']+.08
        n=norm(w['text'])
        if not n:continue
        valid.append(w)
        for i,c in enumerate(n):
            recognized+=c;character_times.append((a+(z-a)*i/len(n),a+(z-a)*(i+1)/len(n)))
    literal=' '.join(script['ko']); expected=norm(literal)
    matcher=SequenceMatcher(None,expected,recognized,autojunk=False)
    assert matcher.ratio()>=.85, f'Whole character matching insufficient {sid}: {matcher.ratio()}'
    mapped={a+i:character_times[b+i] for a,b,n in matcher.get_matching_blocks() for i in range(n)}
    exact=set(mapped); keys=sorted(mapped)
    for i in range(len(expected)):
        if i in exact:continue
        lo=max((k for k in keys if k<i),default=-1);hi=min((k for k in keys if k>i),default=len(expected))
        a=mapped[lo][1] if lo>=0 else 0;z=mapped[hi][0] if hi<len(expected) else d['seconds']
        a,z=min(a,z),max(a,z);unit=(z-a)/(hi-lo-1)
        mapped[i]=(a+(i-lo-1)*unit,a+(i-lo)*unit)
    pieces=[p for p in plan['pieces'] if p['logicalScene']==sid]
    boundaries=sorted((g['afterOriginalParagraph'],g['id']) for g in guides if g['parentScene']==sid)
    ranges=[]; first=1
    for last,gid in boundaries:
        ranges.append((first,last));first=last+1
    ranges.append((first,len(script['ko'])))
    assert len(pieces)==len(ranges)
    char_offset=0; scene_paragraphs=[]
    for pi,(kt,et) in enumerate(zip(script['ko'],script['en']),1):
        piece=next(p for p,(a,z) in zip(pieces,ranges) if a<=pi<=z)
        start_char=char_offset;end_char=start_char+len(norm(kt));char_offset=end_char
        times=[mapped[k] for k in range(start_char,end_char)]
        a=min(x[0] for x in times);z=max(x[1] for x in times)
        from_s=piece.get('sourceStartSample',0)/24000;to_s=piece.get('sourceEndSample',piece['samples'])/24000
        conversion=lambda t:piece['voiceStartFrame']/60+t-from_s
        pa=max(from_s,a);pz=min(to_s,z)
        assert pz>pa
        row=dict(scene=sid,paragraph=pi,pieceId=piece['id'],ko=kt,en=et,sourceSpeechStart=a,sourceSpeechEnd=z,
            clampedSourceStart=pa,clampedSourceEnd=pz,startSeconds=conversion(pa),endSeconds=conversion(pz),
            evidence=provenance,wordTimesAreApproximate=True,independentTailUsed=len(provenance)>1,
            exactMatchedCharacters=sum(k in exact for k in range(start_char,end_char)),scriptCharacters=end_char-start_char,
            timingApproved=False,meaningActionAligned=False,pixelsApproved=False)
        if pa!=a or pz!=z:
            corrections.append(dict(scene=sid,paragraph=pi,kind='candidate-anchor-limited-to-byte-exact-fragment',before=[a,z],after=[pa,pz],
                audioSamplesDiscarded=0,requiresDirectTimingReview=True,reason='ASR word anchor crosses an already reviewed quiet PCM insertion split; all source samples remain preserved.'))
        paragraphs.append(row);scene_paragraphs.append(row)
        tokens=list(re.finditer(r'\S+',kt));first=0;piece_cues=[]
        while first<len(tokens):
            last=first+1
            while last<len(tokens):
                text=kt[tokens[first].start():tokens[last].end()]
                if font.getlength(text)>620 or re.search(r'[.!?]$',kt[tokens[first].start():tokens[last-1].end()]):break
                last+=1
            text=kt[tokens[first].start():tokens[last-1].end()]
            assert font.getlength(text)<=620
            ca=start_char+len(norm(kt[:tokens[first].start()]));cz=start_char+len(norm(kt[:tokens[last-1].end()]))
            sa=max(pa,min(mapped[k][0] for k in range(ca,cz)));sz=min(pz,max(mapped[k][1] for k in range(ca,cz)))
            assert sz>sa, (sid,pi,text,sa,sz)
            cue=dict(scene=sid,paragraph=pi,pieceId=piece['id'],ko=text,lines=[text],sourceSpeechStart=sa,sourceSpeechEnd=sz,
                startSeconds=conversion(sa),endSeconds=conversion(sz),fontPx=48,textWidthPx=font.getlength(text),
                center=[960,970],style='boxed-white-forest-v1',timingApproved=False,pixelsApproved=False)
            cues.append(cue);piece_cues.append(cue);first=last
        assert norm(' '.join(c['ko'] for c in piece_cues))==norm(kt)
        # Independent English is preserved paragraph by paragraph. Proportional
        # wrapping here is provisional until direct semantic/timing review.
        parts=[];current=[]
        for token in et.split():
            if current and len(' '.join(current+[token]))>78:parts.append(' '.join(current));current=[]
            current.append(token)
        if current:parts.append(' '.join(current))
        total=sum(len(t) for t in parts);cursor=conversion(pa)
        for text in parts:
            stop=cursor+(pz-pa)*len(text)/total
            en_cues.append(dict(scene=sid,paragraph=pi,pieceId=piece['id'],en=text,startSeconds=cursor,endSeconds=stop,
                timingMethod='provisional-paragraph-semantic-span-weighted-wrap',meaningAndTimingApproved=False))
            cursor=stop
    scenes.append(dict(id=sid,characterMatch=matcher.ratio(),recognizedText=d['text'],evidence=provenance,
        expectedParagraphs=len(script['ko']),allLiteralParagraphsPreserved=True,directCueTimingReviewed=False))

for language,rows in [('ko',cues),('en',en_cues)]:
    rows.sort(key=lambda r:(r['startSeconds'],r['endSeconds']))
    for left,right in zip(rows,rows[1:]):
        if left['endSeconds']>right['startSeconds']:
            overlap=left['endSeconds']-right['startSeconds'];assert overlap<.45
            mid=(left['endSeconds']+right['startSeconds'])/2
            corrections.append(dict(kind='candidate-overlapping-recognizer-boundary',language=language,scene=left['scene'],
                previousText=left.get(language),nextText=right.get(language),overlapSeconds=overlap,sharedCandidateSeconds=mid,
                requiresDirectTimingReview=True,audioChanged=False))
            left['endSeconds']=right['startSeconds']=mid
    for i,r in enumerate(rows,1):r['index']=i
target.mkdir()
def timestamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang,rows in [('ko',cues),('en',en_cues)]:
    (target/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{timestamp(r["startSeconds"])} --> {timestamp(r["endSeconds"])}\n{r[lang]}' for r in rows)+'\n','utf-8')
data=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=datetime.now(timezone.utc).isoformat(),
    status='literal-word-anchored-candidate-only',plan=rel(plan_path),planSha256=sha(plan_path),
    scriptInputs=[dict(path=rel(p),sha256=sha(p)) for p in [ko_path,en_path,guide_path,*extra_inputs]],
    paragraphs=paragraphs,scenes=scenes,ko=cues,en=en_cues,corrections=corrections,
    paragraphCount=len(paragraphs),originalParagraphs=46,newParagraphs=24,koCueCount=len(cues),enCueCount=len(en_cues),
    singleLineKo=True,maxKoWidthPx=620,captionCenter=[960,970],audioChanged=False,newAsrJobs=0,newGitImages=0,
    sourceActionAlignmentApproved=False,allCuePixelsReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False,
    scope='Current literal text preserved; ASR supplies approximate anchors only. Every word/action boundary, lower target, motion and final encoded cue remains pending.')
(target/'captions.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(paragraphs=len(paragraphs),koCues=len(cues),enCues=len(en_cues),corrections=len(corrections),
    minimumSceneMatch=min(s['characterMatch'] for s in scenes),approved=False)))
