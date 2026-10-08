"""Preserve sixteen whole PCM files; propose literal cues from reviewed contexts.

No synthesis, media extraction, source allocation, final mix or approval occurs.
All character interpolation and English wrapping remain direct-review candidates.
"""
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib, json, math, re
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
DEST = BASE/'caption-candidate-v1'
TIMING = BASE/'current16-voice-timing-candidate-v1.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
norm = lambda s: ''.join(c.lower() for c in s if c.isalnum())

assert not DEST.exists() and not TIMING.exists(), 'Preserve existing candidate.'
original_review = read(BASE/'current-contexts-asr-direct-review-v1.json')
guide_review = read(BASE/'observation-guide-contexts-asr-direct-review-v2.json')
assert original_review['currentOriginalVoiceTextIntegrityApproved']
assert guide_review['allCompleteContextsTextCompared'] and guide_review['guideCurrentVoiceTextIntegrityApproved']
assert read(BASE/'observation-guide-contexts-asr-execution-v1.json')['actualExitObserved']
assert read(BASE/'observation-guide16-repair-contexts-asr-execution-v1.json')['actualExitObserved']
original_timing = read(BASE/'current-original-paragraph-timing-v1.json')
guide_timing = read(BASE/'observation-guide-paragraph-timing-v1.json')
assert original_timing['directBoundaryTextReview'] and guide_timing['directBoundaryTextReview']
ko_path = BASE.parent/'script/narration.ko.v3.json'
en_path = BASE.parent/'script/narration.en.v2.json'
ko, en = [read(p)['scenes'] for p in [ko_path, en_path]]
assert len(ko) == len(en) == 16 and sum(len(s['lines']) for s in ko) == 64
voice = {r['id']: r for r in original_timing['scenes']+guide_timing['scenes']}
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
scene_rows, paragraphs, cues, en_cues, corrections = [], [], [], [], []
position = 120
for scene, english in zip(ko, en):
    sid = scene['id']; assert english['id'] == sid and len(scene['lines']) == len(english['lines']) == 4
    row = voice[sid]; source = ROOT/row['path']; assert sha(source) == row['sha256']
    assert row['sampleRate'] == 24000 and row['allOriginalSamplesRetained']
    count = row['totalSamples']; frames = math.ceil(count/400)
    directory = BASE/('current-contexts-asr-v1' if int(sid[:2]) <= 8 else 'observation-guide-contexts-asr-v1')
    words, provenance = [], []
    for half in ['first-half', 'last-half']:
        context_path = ROOT/guide_review['contextAsrFiles'][sid][half] if int(sid[:2]) > 8 else directory/(sid+'-'+half+'.json')
        context = read(context_path)
        assert context['sourcePath'] == row['path'] and context['sourceSha256'] == row['sha256']
        assert context['exactSourceSampleBytesMatched']
        offset = context['startSample']/24000
        current_words = list(context['words'])
        for override in guide_review.get('wordAlignmentOverrides', []):
            if override['contextId'] != context['id']: continue
            assert override['directlyReviewed'] and sha(context_path) == override['originalContextSha256']
            assert current_words[:len(override['originalWords'])] == override['originalWords']
            corroboration = read(ROOT/override['corroboratingContextPath'])
            assert sha(ROOT/override['corroboratingContextPath']) == override['corroboratingContextSha256']
            assert corroboration['exactSourceSampleBytesMatched'] and corroboration['sourceSha256'] == context['sourceSha256']
            assert corroboration['words'][:len(override['replacementWords'])] == override['replacementWords']
            current_words = override['replacementWords'] + current_words[len(override['originalWords']):]
            corrections.append(dict(kind='corroborated-onset-word-segmentation', scene=sid,
                context=context['id'], originalWords=override['originalWords'],
                replacementWords=override['replacementWords'], audioChanged=False,
                reason=override['reason'], humanPronunciation='pending'))
        for word in current_words:
            a, b = word['timestamp']
            # This exact zero-duration06 artifact was compared with current PCM
            # and complete whole/context text in the preserved original review.
            known = sid == '06-quick-trial' and half == 'first-half' and word['text'].strip() == '자' and a == b == 0
            reviewed = any(x.get('contextId') == context['id'] and x.get('text') == word['text']
                and x.get('timestamp') == word['timestamp'] for x in guide_review.get('zeroDurationAsrArtifacts', []))
            if known or reviewed:
                corrections.append(dict(scene=sid, context=context['id'], skippedRecognizedWord=word,
                    reason='Previously directly reviewed zero-duration recognizer artifact; not positive-duration filler evidence.',
                    listeningApproval=False, audioChanged=False)); continue
            assert a is not None and b is not None and b > a, (sid, half, word)
            context_seconds = (context['endSample']-context['startSample'])/24000
            assert a >= 0 and b <= context_seconds+.08
            words.append(dict(text=word['text'], timestamp=[a+offset,b+offset]))
        provenance.append(dict(path=rel(context_path), sha256=sha(context_path),
            contextSha256=context['contextSha256'], exactSourceSampleBytesMatched=True, offsetSeconds=offset))
    recognized, character_times = '', []
    for word in words:
        a, b = word['timestamp']; token = norm(word['text'])
        for i, character in enumerate(token):
            recognized += character; character_times.append((a+(b-a)*i/len(token),a+(b-a)*(i+1)/len(token)))
    expected = norm(' '.join(scene['lines']))
    matcher = SequenceMatcher(None,expected,recognized,autojunk=False)
    assert matcher.ratio() >= .85, (sid,matcher.ratio())
    mapped = {a+i:character_times[b+i] for a,b,n in matcher.get_matching_blocks() for i in range(n)}
    exact = set(mapped); keys = sorted(mapped)
    for i in range(len(expected)):
        if i in exact: continue
        lo = max((k for k in keys if k<i),default=-1); hi = min((k for k in keys if k>i),default=len(expected))
        a = mapped[lo][1] if lo >= 0 else 0; b = mapped[hi][0] if hi < len(expected) else count/24000
        a,b = min(a,b),max(a,b); width = (b-a)/(hi-lo-1)
        mapped[i] = (a+(i-lo-1)*width,a+(i-lo)*width)
    convert = lambda t: position/60+t
    char_cursor = 0
    for pi,(kt,et,pt) in enumerate(zip(scene['lines'],english['lines'],row['paragraphs']),1):
        assert pt['expectedKo'] == kt
        ca,cz = char_cursor,char_cursor+len(norm(kt)); char_cursor = cz
        start_sample,end_sample = pt['sourceInSample'],pt['sourceOutSample']
        pa = max(start_sample/24000,min(mapped[k][0] for k in range(ca,cz)))
        pb = min(end_sample/24000,max(mapped[k][1] for k in range(ca,cz)))
        assert pb > pa, (sid,pi,pa,pb)
        paragraphs.append(dict(scene=sid,paragraph=pi,ko=kt,en=et,sourceSpeechStart=pa,sourceSpeechEnd=pb,
            startSeconds=convert(pa),endSeconds=convert(pb),evidence=provenance,exactMatchedCharacters=sum(k in exact for k in range(ca,cz)),
            scriptCharacters=cz-ca,approximateWordTimes=True,timingApproved=False,sourceActionAligned=False,pixelsApproved=False))
        tokens = list(re.finditer(r'\S+',kt)); first = 0; paragraph_cues = []
        while first < len(tokens):
            last = first+1
            while last < len(tokens):
                candidate = kt[tokens[first].start():tokens[last].end()]
                if font.getlength(candidate) > 620 or re.search(r'[.!?]$',kt[tokens[first].start():tokens[last-1].end()]): break
                last += 1
            text = kt[tokens[first].start():tokens[last-1].end()]; assert font.getlength(text) <= 620
            a = ca+len(norm(kt[:tokens[first].start()])); b = ca+len(norm(kt[:tokens[last-1].end()]))
            sa = max(pa,min(mapped[k][0] for k in range(a,b))); sb = min(pb,max(mapped[k][1] for k in range(a,b)))
            assert sb > sa, (sid,pi,text,sa,sb)
            cue = dict(scene=sid,paragraph=pi,ko=text,lines=[text],sourceSpeechStart=sa,sourceSpeechEnd=sb,
                startSeconds=convert(sa),endSeconds=convert(sb),fontPx=48,textWidthPx=font.getlength(text),
                center=[960,970],style='boxed-white-forest-v1',timingApproved=False,pixelsApproved=False)
            cues.append(cue); paragraph_cues.append(cue); first = last
        assert norm(' '.join(c['ko'] for c in paragraph_cues)) == norm(kt)
        parts,current = [],[]
        for token in et.split():
            if current and len(' '.join(current+[token])) > 78: parts.append(' '.join(current)); current = []
            current.append(token)
        if current: parts.append(' '.join(current))
        total = sum(len(t) for t in parts); cursor = convert(pa)
        for text in parts:
            stop = cursor+(pb-pa)*len(text)/total
            en_cues.append(dict(scene=sid,paragraph=pi,en=text,startSeconds=cursor,endSeconds=stop,
                timingMethod='provisional-paragraph-semantic-span-weighted-wrap',meaningAndTimingApproved=False)); cursor = stop
        assert norm(' '.join(parts)) == norm(et)
    scene_rows.append(dict(id=sid,audioPath=row['path'],audioSha256=row['sha256'],samples=count,sampleRate=24000,
        frames=frames,startFrame=position,endFrame=position+frames,paragraphStartSamples=[p['sourceInSample'] for p in row['paragraphs']],
        paragraphStarts=[p['sourceInSample']/24000 for p in row['paragraphs']],allOriginalSamplesRetained=True,
        tailPaddingSamples=frames*400-count,characterMatch=matcher.ratio(),recognizerWasPromptedWithExpected=False,
        provenance=provenance,directCueTimingReview=False))
    position += frames
for language,rows in [('ko',cues),('en',en_cues)]:
    rows.sort(key=lambda r:(r['startSeconds'],r['endSeconds']))
    for left,right in zip(rows,rows[1:]):
        if left['endSeconds'] > right['startSeconds']:
            overlap = left['endSeconds']-right['startSeconds']; assert overlap < .45
            mid = (left['endSeconds']+right['startSeconds'])/2
            corrections.append(dict(kind='candidate-recognizer-boundary-overlap',language=language,scene=left['scene'],
                previousText=left[language],nextText=right[language],overlapSeconds=overlap,sharedCandidateSeconds=mid,
                audioChanged=False,directTimingReviewRequired=True))
            left['endSeconds'] = right['startSeconds'] = mid
    for i,r in enumerate(rows,1): r['index'] = i
DEST.mkdir()
def stamp(t):
    n = round(t*1000); return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for language,rows in [('ko',cues),('en',en_cues)]:
    (DEST/f'candidate.{language}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[language]}' for r in rows)+'\n','utf-8')
timing = dict(schemaVersion=1,slug='player-customization',preparedAt=datetime.now(timezone.utc).isoformat(),rows=scene_rows,
    fps=60,introFrames=120,outroFrames=600,bodyFrames=position-120,proposedFinalFrames=position+600,
    wholePcmSamples=sum(r['samples'] for r in scene_rows),originalEightPcmPreserved=True,
    measuredVoiceBoundaries=True,sourceAllocationApproved=False,bodyRatioApproved=False,finalTimingApproved=False,finalTimelineAdopted=False)
TIMING.write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n','utf-8')
record = dict(schemaVersion=1,slug='player-customization',preparedAt=datetime.now(timezone.utc).isoformat(),
    status='literal-independent-context-anchored-candidate-only',timingCandidate=rel(TIMING),timingCandidateSha256=sha(TIMING),
    scriptInputs=[dict(path=rel(p),sha256=sha(p)) for p in [ko_path,en_path]],paragraphs=paragraphs,scenes=scene_rows,ko=cues,en=en_cues,
    corrections=corrections,paragraphCount=64,koCueCount=len(cues),enCueCount=len(en_cues),singleLineKo=True,maxKoWidthPx=620,
    captionCenter=[960,970],newTtsJobs=0,newAsrJobs=0,newMedia=0,newGitImages=0,allLiteralKoEnParagraphsPreserved=True,
    sourceActionAlignmentApproved=False,allCuePixelsReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False)
(DEST/'captions.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=16,paragraphs=64,koCues=len(cues),enCues=len(en_cues),bodyFrames=timing['bodyFrames'],
    proposedFinalFrames=timing['proposedFinalFrames'],minimumSceneMatch=min(r['characterMatch'] for r in scene_rows),finalApproved=False)))
