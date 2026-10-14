"""Guarded current mixed-word captions; retain200 cues and add44 editable cues."""
from pathlib import Path
from datetime import datetime, timezone
import difflib, hashlib, json, math, re
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'[^가-힣a-zA-Z0-9]', '', s).lower()
review = read(O / 'current34-mixed-complete-direct-review-v1.json')
mix = read(O / 'current34-mix-execution-v2.json')
assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared']
assert review['mixAacSha256'] == mix['mixAacSha256'] == sha(ROOT / mix['mixAac'])
outputs = ['current34.captions.ko.srt', 'current34.captions.en.srt', 'current34.captions.ko.ass',
    'current34-caption-alignment-v1.json', 'current34-caption-layout-v1.json', 'current34-measured-chapters-v1.json']
assert not any((O / name).exists() for name in outputs), 'Preserve existing caption preparation.'
plan = read(O / 'current34-measured-timing-plan-v1.json')
base = read(ROOT / plan['sourceBaselineTimeline'])
scenes = {s['id']: s for s in plan['scenes']}
previous = {s['id']: s for s in base['scenes']}
rows = []
assert len(base['koCaptions']) == len(base['enCaptions']) == 200
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
for i, (k, e) in enumerate(zip(base['koCaptions'], base['enCaptions']), 1):
    assert k['scene'] == e['scene'] and abs(k['start']-e['start']) < .001 and abs(k['end']-e['end']) < .001
    sid = k['scene']; shift = scenes[sid]['frameIn']/60 - previous[sid]['start']
    lines = k['text'].split('\n')
    assert 1 <= len(lines) <= 2 and max(font.getlength(x) for x in lines) <= 1570
    rows.append(dict(scene=sid, start=k['start']+shift, end=k['end']+shift,
        ko=k['text'].replace('\n', ' '), en=e['text'], lines=lines,
        boxWidth=math.ceil(max(font.getlength(x) for x in lines))+44,
        retainedCue=i, originalTextWrapAndRelativeTimingPreserved=True, finalPixelsReviewed=False))
groups = read(O / 'current34-caption-editorial-groups-v1.json')
assert groups['all40AddedKoEnParagraphsExactlyPreserved']
contexts = {x['id']: x for x in read(O / 'current34-mixed-independent-context-plan-v1.json')['contexts']}
for sid in [s['id'] for s in plan['scenes'] if not s['baseline']]:
    for paragraph in sorted({x['paragraph'] for x in groups['groups'] if x['scene'] == sid}):
        units = [x for x in groups['groups'] if x['scene'] == sid and x['paragraph'] == paragraph]
        context = contexts[f'{sid}-p{paragraph:02d}']
        rp = O / 'current34-mixed-contexts-asr-v1' / (context['id'] + '.json')
        result = read(rp)
        assert result['sourceSha256'] == mix['decodedAacSha256'] and result['exactSourceStereoPcmBytesMatched']
        expected = norm(' '.join(x['ko'] for x in units))
        words = result['words']; recognized = ''.join(norm(x['text']) for x in words)
        indexes = [i for i, w in enumerate(words) for _ in norm(w['text'])]
        matcher = difflib.SequenceMatcher(None, expected, recognized, autojunk=False)
        mapping = {a+i: b+i for a, b, n in matcher.get_matching_blocks() for i in range(n)}
        assert matcher.ratio() > .88, (sid, paragraph, 'Directly inspect recognition/timing alternative')
        offset = 0
        for unit in units:
            stop = offset + len(norm(unit['ko']))
            mapped = [mapping[i] for i in range(offset, stop) if i in mapping]
            assert len(mapped)/max(1, stop-offset) > .80
            first = words[indexes[min(mapped)]]; last = words[indexes[max(mapped)]]
            assert first['timestamp'][0] is not None and last['timestamp'][1] is not None
            start = max(context['coreStartSample']/48000, context['startSample']/48000+first['timestamp'][0]-.3)
            end = min(context['coreEndSample']/48000, context['startSample']/48000+last['timestamp'][1]-.3)
            proposed = start
            word_end = context['startSample']/48000+first['timestamp'][1]-.3
            windows = sorted((x['destinationStartSample']/24000, x['destinationEndSample']/24000)
                for x in mix['placements'] if x['scene'] == sid)
            gaps = []
            for (_, left), (right, _) in zip(windows, windows[1:]):
                if right-left >= .5 and start <= right < word_end:
                    start = right; gaps.append(dict(start=left, end=right))
            assert end-start > 2/60, (unit['id'], start, end)
            rows.append(dict(**unit, start=start, end=end, newCue=True,
                proposedRecognizerStart=proposed, knownObservationQuietGapsExcluded=gaps,
                currentContextResult=rp.relative_to(ROOT).as_posix(), currentContextResultSha256=sha(rp),
                contextAlignmentRatio=matcher.ratio(), finalCueTimingDirectlyReviewed=False))
            offset = stop
rows.sort(key=lambda x: x['start'])
assert len(rows) == 244
def stamp(t, ass=False):
    base = 100 if ass else 1000; n = round(t*base)
    return f'{n//(base*3600):0{1 if ass else 2}d}:{n//(base*60)%60:02d}:{n//base%60:02d}{"." if ass else ","}{n%base:0{2 if ass else 3}d}'
ass = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
layout = []
for i, c in enumerate(rows, 1):
    c['id'] = i; a, b = c['start'], c['end']
    assert 2 <= a < b <= (plan['totalFrames']-600)/60
    if i > 1:
        assert a >= rows[i-2]['end']-.001, (i, 'Resolve overlapping caption boundaries')
    width = c['boxWidth']; height = len(c['lines'])*62+22
    x, y = round(960-width/2), round(970-height/2)
    assert width <= 1614 and x > 0 and x+width+16 < 1920 and y+height+16 < 1080
    def event(layer, text):
        global ass
        ass += f'Dialogue: {layer},{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{text}\n'
    def box(xx, yy, color, border):
        return '{\\an7\\pos('+f'{xx},{yy}'+')\\p1\\bord'+str(border)+'\\shad0\\1c&H'+color+'&\\3c&H181B16&}m 0 0 l '+f'{width} 0 {width} {height} 0 {height}'
    event(0, box(x+14, y+14, '323C07', 0)); event(1, box(x, y, 'FFFFFF', 3))
    for n, line in enumerate(c['lines']):
        event(2, '{\\an5\\pos('+f'960,{y+42+n*62}'+')\\bord0\\shad0}'+line.replace('{', '').replace('}', ''))
    layout.append(dict(cue=i, scene=c['scene'], start=a, end=b, x=x, y=y, width=width, height=height,
        centerX=960, centerY=970, shadowBottom=y+height+14, lines=c['lines'], finalPixelsReviewed=False))
for lang in ['ko', 'en']:
    (O / f'current34.captions.{lang}.srt').write_text('\n\n'.join(
        f'{c["id"]}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+
        ('\n'.join(c['lines']) if lang == 'ko' else c['en']) for c in rows)+'\n', 'utf-8')
(O / 'current34.captions.ko.ass').write_text(ass, 'utf-8')
def write(name, data):
    (O / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
write('current34-caption-alignment-v1.json', dict(entries=rows, retainedCueCount=200, newCueCount=44,
    addedParagraphCount=40, allOriginalCueTextWrapAndRelativeTimingPreserved=True,
    mixAacSha256=mix['mixAacSha256'], planSha256=sha(O / 'current34-measured-timing-plan-v1.json'),
    allNewCueTimingDirectlyReviewed=False, humanListeningApproved=False))
write('current34-caption-layout-v1.json', dict(preparedAt=datetime.now(timezone.utc).isoformat(),
    style='boxed-white-forest-v1', font='Malgun Gothic', fontSize=48, allCuesMeasured=True,
    cueCount=244, cues=layout, unresolvedLayoutErrors=[],
    assSha256=sha(O / 'current34.captions.ko.ass'), allFinalCuePixelsReviewed=False))
write('current34-measured-chapters-v1.json', dict(chapters=[dict(scene=s['id'], title=s['title'],
    start=s['frameIn']/60, startFrame=s['frameIn']) for s in plan['scenes']],
    introFrames=120, membershipStartFrame=plan['totalFrames']-600, membershipFrames=600,
    totalFrames=plan['totalFrames'], mixAacSha256=mix['mixAacSha256'], platformChaptersSaved=False))
print(json.dumps(dict(cues=244, retained=200, added=44, finalPixels=False)))
