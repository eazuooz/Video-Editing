"""Frame-exact edit plan from measured narration: our recordings per paragraph,
full-length overlay timing for Motion Canvas, and boxed-white-forest-v1 captions
with one emphasized span per cue (caption-clause-keyword-v1)."""
from pathlib import Path
import json, math, re, hashlib, subprocess
from PIL import ImageFont
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; O = P / 'production/local/edit'; O.mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
project = read(P / 'project.json'); tts = project['tts']; N = R / tts['outputDir']; STEM = tts['filenameStem']
timing = read(N / f'{STEM}.timing.json'); assert timing.get('alignment'), 'Run review-voice.py (ASR + alignment) first'
script = read(P / 'script/narration.ko.json'); aliases = read(P / 'script/pronunciation.json')['aliases']
recordings = read(P / 'sources/recordings.json')['recordings']
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
LEAD = 2.0  # original 2 s branding before the body
# --- captions ------------------------------------------------------------
def display(s):
    for canonical, spoken in sorted(aliases.items(), key=lambda p: len(p[1]), reverse=True):
        s = re.sub(r'(?<![가-힣A-Za-z0-9])' + re.escape(spoken), lambda _: canonical, s)
    return s
def wrap(text):
    if font.getlength(text) <= 1570: return text
    words = text.split(); split = min(range(1, len(words)), key=lambda i: abs(font.getlength(' '.join(words[:i])) - font.getlength(' '.join(words[i:]))))
    lines = [' '.join(words[:split]), ' '.join(words[split:])]; assert max(font.getlength(x) for x in lines) <= 1570, (text, lines); return '\n'.join(lines)
def stamp(s, ass=False):
    scale = 100 if ass else 1000; t = round(s * scale); h, t = divmod(t, 3600 * scale); m, t = divmod(t, 60 * scale); sec, ms = divmod(t, scale)
    return f'{h}:{m:02d}:{sec:02d}.{ms:02d}' if ass else f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'
def seconds(s): h, m, z = s.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(z)
# one emphasized span per cue: term=teal, result=green, problem=red (measured >=4.5:1 on white)
ROLE = {'term': '&H00666B0B', 'result': '&H00377F1A', 'problem': '&H001823B4'}
KEYWORDS = [('AI 생성 콘텐츠 표기', 'term'), ('생성형 AI', 'term'), ('사전 생성', 'term'), ('실시간 생성', 'term'), ('가드레일', 'term'), ('콘텐츠 설문', 'term'), ('플레이스홀더', 'term'), ('캡슐', 'term'), ('넥스트 페스트', 'term'), ('확장 프로그램', 'term'), ('No AI', 'term'), ('해자', 'term'), ('복제', 'problem'), ('베꼈', 'problem'), ('흉내 낸', 'problem'), ('전가', 'problem'), ('주홍글씨', 'problem'), ('거절', 'problem'), ('사고', 'problem'), ('묻힐', 'problem'), ('협박', 'problem'), ('36%', 'result'), ('52%', 'result'), ('8천 개', 'result'), ('8천2백 개', 'result'), ('2만 개', 'result'), ('608개', 'result'), ('3%', 'result'), ('59곳', 'result'), ('여덟 배', 'result'), ('21.4달러', 'result'), ('270억 달러', 'result'), ('156%', 'result'), ('80달러', 'result'), ('70달러', 'result'), ('14개', 'result'), ('열네 개', 'result'), ('24시간', 'result'), ('도구', 'term'), ('결과물', 'term'), ('표기', 'term')]
def emphasize(text):
    for key, role in KEYWORDS:
        i = text.find(key)
        if i >= 0: return text[:i] + '{\\c' + ROLE[role] + '\\b1}' + key + '{\\c&H00090B08\\b0}' + text[i + len(key):], key, role
    return text, None, None
header = (R / 'projects/game-reward-planning/production/local/reference-preserving-v2/edit/captions.ko.ass').read_text(encoding='utf8').split('[Events]')[0] + '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
captions = []
for lang in ['ko', 'en']:
    blocks = []; prev = 0
    for i, block in enumerate((R / project['paths']['captionsKo' if lang == 'ko' else 'captionsEn']).read_text(encoding='utf8').strip().split('\n\n'), 1):
        lines = block.splitlines(); a, b = [seconds(s) + LEAD for s in lines[1].split(' --> ')]
        text = ' '.join(lines[2:]); text = wrap(display(text)) if lang == 'ko' else '\n'.join(lines[2:]); assert a >= prev - .002 and b > a; prev = b
        blocks.append(f'{i}\n{stamp(a)} --> {stamp(b)}\n{text}')
        if lang == 'ko':
            styled, key, role = emphasize(text); captions.append({'id': i, 'start': a, 'end': b, 'text': text, 'emphasis': {'span': key, 'role': role} if key else None, 'ass': styled})
    (O / f'captions.{lang}.srt').write_text('\n\n'.join(blocks) + '\n', encoding='utf8')
# boxed-white-forest-v1 as three ASS layers per cue (approved game-reward-planning construction):
# forest shadow rect (+14,+14), white rect with 3px outline, then centred text at (960,970).
events = []
for c in captions:
    lines = c['text'].split('\n'); w = math.ceil(max(font.getlength(l) for l in lines)) + 44; h = len(lines) * 62 + 22
    x0, y0 = 960 - w // 2, 970 - h // 2; t0, t1 = stamp(c['start'], True), stamp(c['end'], True)
    events.append(f"Dialogue: 0,{t0},{t1},Default,,0,0,0,,{{\\an7\\pos({x0 + 14},{y0 + 14})\\p1\\bord0\\shad0\\1c&H323C07&\\3c&H181B16&}}m 0 0 l {w} 0 {w} {h} 0 {h}")
    events.append(f"Dialogue: 1,{t0},{t1},Default,,0,0,0,,{{\\an7\\pos({x0},{y0})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}m 0 0 l {w} 0 {w} {h} 0 {h}")
    events.append(f"Dialogue: 2,{t0},{t1},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0}}" + c['ass'].replace('\n', r'\N'))
    c['box'] = {'x': x0, 'y': y0, 'w': w, 'h': h}
(O / 'captions.ko.ass').write_text(header + '\n'.join(events) + '\n', encoding='utf8')
save(O / 'caption-layout.json', {'style': 'boxed-white-forest-v1', 'cueRule': 'caption-clause-keyword-v1', 'rows': captions, 'textWidthMaximum': 1570, 'allMeasured': True})
# --- visuals per scene paragraph (recording ids from sources/recordings.json) --
V = {
 '01': [['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur']],
 '02': [['hub-random'], ['steamdb-releases', 'hub-random'], ['hub-random'], ['search-demos-plain'], ['search-demos-plain'], ['search-demos-plain']],
 '03': [['store-disclosure'], ['store-disclosure'], ['store-disclosure'], ['store-disclosure'], ['store-disclosure'], ['gdc-report'], ['crimson-desert'], ['search-demos-plain']],
 '04': [['hub-random'], ['search-demos-plain'], ['gdc-report'], ['aftermath-list'], ['aftermath-list'], ['hub-random']],
 '05': [['hub-random'], ['hub-random'], ['search-demos-hide', 'curator-noai', 'itch-tag'], ['price-70'], ['gdco-prices'], ['mp1st-budgets'], ['hub-charts']],
 '06': [['search-needle'], ['search-needle'], ['kotaku-needle'], ['kotaku-needle'], ['gamemeca'], ['reflux-store'], ['steamdb-releases', 'search-needle'], ['search-needle'], ['hub-random']],
 '07': [['hub-random'], ['hub-charts'], ['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur'], ['search-demos-blur']],
}
cursor = {}
FILLERS = ['hub-16-click', 'hub-random', 'search-demos-plain', 'hub-charts', 'search-demos-blur', 'search-demos-hide', 'curator-noai', 'itch-tag']
def remaining(rid): return max(0.0, recordings[rid]['duration'] - cursor.get(rid, 0.0) - 0.1)
def take(rid, need_frames):
    # Use the requested recording while it has unseen footage; then continue on an
    # unseen stretch of a filler recording instead of freezing a frame (no loops).
    if rid not in recordings or remaining(rid) < 1.0:
        pool = [f for f in FILLERS if f in recordings and remaining(f) >= 1.0]
        rid = max(pool, key=remaining) if pool else rid
    rec = recordings[rid]; start = cursor.get(rid, 0.0); use = min(remaining(rid), need_frames / 60)
    cursor[rid] = start + use
    return {'sourceFile': rec['file'], 'sourceSha256': rec['sha256'], 'sourceStart': round(start, 3), 'holdFrames': need_frames - round(use * 60), 'recording': rid}
total = math.ceil((LEAD + timing['duration_seconds'] + 10) * 60); scenes = []; cuts = []; overlays = []
for idx, s in enumerate(script['scenes']):
    sid = s['id']; entries = [e for e in timing['entries'] if e['scene_id'] == sid]; a = round((entries[0]['start'] + LEAD) * 60)
    nxt = [e for e in timing['entries'] if e['scene_id'] == script['scenes'][idx + 1]['id']] if idx + 1 < len(script['scenes']) else []
    b = round((nxt[0]['start'] + LEAD) * 60) if nxt else total - 600
    scenes.append({'id': sid, 'title': s['title'], 'startFrame': a, 'endFrame': b, 'paragraphs': entries})
    assert len(V[sid]) == len(entries), (sid, len(V[sid]), len(entries))
    for j, e in enumerate(entries):
        start = a if j == 0 else round((e['voice_start'] + LEAD) * 60); end = round((entries[j + 1]['voice_start'] + LEAD) * 60) if j + 1 < len(entries) else b
        overlays.append({'id': f'{sid}-{j + 1}', 'scene': sid, 'paragraph': j + 1, 'startFrame': start, 'frames': end - start, 'text': e['text']})
        options = [r for r in V[sid][j] if r in recordings] or [r for r in ['hub-random', 'search-demos-plain'] if r in recordings]
        for k, rid in enumerate(options):
            x = start + round((end - start) * k / len(options)); y = start + round((end - start) * (k + 1) / len(options))
            piece = take(rid, y - x); piece.update(startFrame=x, frames=y - x, scene=sid, paragraph=j + 1, kind='own-recording'); cuts.append(piece)
cuts.sort(key=lambda c: c['startFrame']); at = 120
for i, c in enumerate(cuts): assert c['startFrame'] == at, (i, c, at); at += c['frames']; c['endFrame'] = at; c['id'] = f'cut-{i + 1:03d}'
assert at == total - 600
plan = {'schemaVersion': 1, 'timing': 'measured-and-asr-aligned', 'totalFrames': total, 'bodyFrames': total - 720, 'fps': 60, 'leadSeconds': LEAD, 'scenes': scenes, 'cuts': cuts, 'ratioPolicy': 'reality-check-no-ratio-v1 (reported only)', 'humanWholeListening': 'pending'}
save(O / 'edit-plan.json', plan)
save(O / 'overlay-timing.json', {'fps': 60, 'bodyStartFrame': 120, 'bodyFrames': total - 720, 'segments': overlays, 'captionZone': {'centerX': 960, 'centerY': 970}})
print(json.dumps({'durationSeconds': total / 60, 'cuts': len(cuts), 'captions': len(captions), 'overlaySegments': len(overlays), 'heldFrames': sum(c['holdFrames'] for c in cuts)}))
