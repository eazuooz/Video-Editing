import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1048576), b''):
            h.update(part)
    return h.hexdigest()

results = []
for number in range(1, 10):
    episode = f'A{number:02d}'
    folder = HERE / episode
    path = folder / 'source-map.json'
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    evidence = data['reviewEvidence']
    video = folder / evidence['referenceMedia']
    transcript = folder / evidence['transcript']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate,duration:format=duration',
        '-of', 'json', str(video)
    ], text=True, encoding='utf-8'))
    stream = probe['streams'][0]
    duration = float(probe['format']['duration'])
    evidence.update({
        'transcriptSha256': digest(transcript),
        'referenceMediaSha256': digest(video),
        'durationSeconds': duration,
        'decodedDimensions': [stream['width'], stream['height']],
        'frameRate': stream['r_frame_rate'],
        'resolutionNote': 'Research-only reference media; never a production source. Independent production footage still requires genuine FHD or higher.',
        'fullFrameByFrameReview': False,
        'rawSourceFilesForResearchOnly': True,
        'rawSourceFilesMayBeCommitted': False,
    })
    assert data['episode'] == episode
    assert data['sourceClassification'] == 'research-reference-only'
    assert data['sourceMediaAllowedInProduction'] is False
    for rel in evidence['visualEvidence']:
        assert (folder / rel).is_file(), (episode, rel)
    previous_end = 0
    warnings = []
    for section in data['sections']:
        start, end = section['sourceTime']
        assert 0 <= start < end <= duration, (episode, section['id'], end, duration)
        assert start >= previous_end, (episode, section['id'], 'out of order')
        if start > previous_end:
            warnings.append({'gapBefore': section['id'], 'seconds': start - previous_end})
        previous_end = end
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    results.append({'episode': episode, 'map': str(path.relative_to(HERE)), 'sections': len(data['sections']), 'durationSeconds': duration, 'transcriptRead': evidence['fullTranscriptRead'], 'visualReview': evidence['visualReviewMethod'], 'warnings': warnings})
    print(f'{episode}: {len(data["sections"])} sections; {duration:.3f}s; evidence paths and ordered time ranges verified', flush=True)

(HERE / 'early-research-validation.json').write_text(json.dumps({'scope': 'A01-A09', 'checked': '2026-10-31', 'results': results, 'scopeLimit': 'File, hash, metadata, order and range validation; does not certify narration, rights, production footage, audio listening or final video.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
