import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
BATCH = json.loads((BASE / 'batch.json').read_text(encoding='utf-8-sig'))
entries = []
scripts = []
for item in BATCH['episodes']:
    eid = item['id']
    folder = HERE / eid
    path = folder / ('source-map.json' if int(eid[1:]) < 10 else 'research-map.json')
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    review = data.get('reviewEvidence', data.get('review'))
    parts = data.get('sections', data.get('teachingOrder'))
    assert data['episode'] == eid
    assert data['sourceUrl'] == item['sourceUrl']
    assert data.get('sourceClassification', data.get('classification')) == 'research-reference-only'
    assert data.get('sourceMediaAllowedInProduction', data.get('productionUseOfReferenceMediaAllowed')) is False
    assert review['fullTranscriptRead'] is True
    assert len(review.get('transcriptSha256', '')) == 64
    assert len(review.get('referenceMediaSha256', review.get('sourceSha256', ''))) == 64
    for name in review['visualEvidence']:
        assert (folder / name).is_file(), (eid, name)
    assert (folder / review['transcript']).is_file()
    duration = review['durationSeconds']
    previous_end = 0
    for part in parts:
        start, end = part.get('sourceTime', part.get('sourceSeconds'))
        assert 0 <= start < end <= duration, (eid, part['id'], duration)
        assert start >= previous_end, (eid, part['id'], 'order')
        previous_end = end
    entries.append({
        'episode': eid,
        'sourceTitleEn': item['sourceTitleEn'],
        'sourceUrl': item['sourceUrl'],
        'map': str(path.relative_to(BASE)).replace('\\', '/'),
        'status': data.get('status', review.get('status')),
        'textBasis': 'official-English-burned-captions-OCR' if eid in ['A07','A08','A11','A15'] else 'Japanese-automatic-transcript-plus-official-English-visual-cross-check',
        'fullTextRead': True,
        'relevantVisualsReviewed': True,
        'continuousOriginalAudioListening': False,
        'everyFrameReview': False,
        'sectionCount': len(parts),
        'durationSeconds': duration,
        'sourceFilesResearchOnly': True,
        'independentProductionFootageComplete': False
    })
    if 2 <= int(eid[1:]) <= 18:
        draft_path = BASE / 'scripts' / eid / 'narration.ko.json'
        draft = json.loads(draft_path.read_text(encoding='utf-8-sig'))
        assert draft['title'] == item['titleKo']
        assert draft['ttsReady'] is False and draft['timingLocked'] is False
        covered = [s for scene in draft['scenes'] for s in scene['referenceSections']]
        expected = [part['id'] for part in parts]
        assert covered == expected, (eid, covered, expected)
        text = '\n'.join(line for s in draft['scenes'] for line in s['lines'])
        for banned in ['사쿠라이', '원영상', '마사히로']:
            assert banned not in text, (eid, banned)
        scripts.append({'episode':eid,'draft':str(draft_path.relative_to(BASE)).replace('\\','/'),'titleMatchesBatch':True,'allSourceSectionsCoveredInOrder':True,'sceneCount':len(draft['scenes']),'narrationCharacters':len(text),'ttsReady':False,'timingLocked':False,'readThrough':'Independent Korean wording checked as connected paragraphs; no source-creator framing. Exact footage, cue timing, pronunciation, actual audio/visual delivery remain unverified.'})

(HERE / 'research-index.json').write_text(json.dumps({
    'schemaVersion':1,'batch':BATCH['id'],'checkedOnKst':'2026-10-31',
    'total':len(entries),'fullTextAndRelevantVisualReviews':len(entries),
    'researchOnly':True,'independentFootageOrProductionClaim':False,
    'rawArtifactsMayBeCommitted':False,
    'commitCandidates':'Only independently authored source-map.json/research-map.json and this research index; raw reference video, transcript, OCR, contacts and dependencies are excluded.',
    'scopeLimit':'Full narration content was read through available Japanese automatic text with official English visual cross-check, or full official English burned-caption OCR for four episodes. Visual review used full-timeline sampled contact sheets and relevant detailed frames. This does not claim real-time complete original-audio listening or exhaustive every-frame inspection.',
    'importantClarifications':[
        {'episode':'A01','note':'Production communication/specification, not runtime animation assignment.'},
        {'episode':'A03','note':'Four elements include standby; three active motion phases. Keep cancellation/control timing distinct from visual clip end.'},
        {'episode':'A09','note':'Use visible volume/2D area accurately, separate from physical mass; do not assert unconfirmed final Kirby blend-shape implementation.'},
        {'episode':'A13','note':'Flipped Animation is source team terminology; verify implementation canonical term, not universal label.'},
        {'episode':'A17','note':'No universal 180-degree cap on all CG joints; clarify arm straightening, rig constraints and IK bend direction with primary evidence.'}
    ],'episodes':entries
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE / 'scripts' / 'draft-validation.json').write_text(json.dumps({'schemaVersion':1,'scope':'A02-A18','checkedOnKst':'2026-10-31','status':'working-drafts-only','checks':scripts,'notCompleted':['Exact independent FHD footage and rights binding','Final game/genre/Nintendo selection and observed examples','Unity scene/animation implementation','Timing lock and TTS','Actual audio and final video review']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Research: {len(entries)}/18 mapped and evidence-validated. Drafts: {len(scripts)}/17 source-section order/title/flags validated.')
