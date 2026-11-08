"""Plan the relocation of existing pre-map observation blocks, without editing media."""
from pathlib import Path
import hashlib, json, re

P = Path(__file__).resolve().parent
R = P.parents[4]
B = R / 'production/batches/animation-18-20261031'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
plan = read(P / 'relations-plan.json')
out = {
    'schemaVersion': 1,
    'status': 'edit-recommendation-not-rendered',
    'coordinates': 'Original current pacing-v3 master, zero-based half-open frame ranges at 60 fps; audio sample ranges at 48000 Hz.',
    'decision': 'Keep the current diagram sentence anchor after the actual-game opening and overview. Relocate pre-anchor explanation observation inserts to immediately after the narrated map. Preserve original gameplay, all original spoken PCM and the order of the original sentences.',
    'unchangedNarration': 'The 18 relationship paragraphs are already in TTS; this plan changes no sentence text.',
    'relocationRules': [
        'Delete only the identified old explanation repeat picture blocks and their music-only audio intervals. Independent-gameplay repeats remain in place.',
        'Insert the new narrated map at its existing sentence anchor adjusted for the removed intervals. Immediately follow it with the relocated normal-speed sets, in their original order, and then resume the original body.',
        'If a two-pass insert had its third normal-speed pass in the original body before the map, keep that single short pass as an introductory preview and make the relocated main set three complete passes. This is one preview plus one three-pass study, not two three-pass studies.',
        'If the third normal-speed body pass begins at the map anchor itself, retain only the two relocated passes, then use the unchanged first body pass as pass three. Do not append a fourth consecutive pass.',
        'Only newly extended observation time receives the existing music bed. Do not duplicate, stretch, suppress, or reorder spoken PCM. Retiming subtitles follows the audio deletions/insertions, not picture-cut positions.',
        'Do not use the measured event list as evidence that no UE image occurs earlier: ordinary baseline explanatory shots can remain brief topic previews. The complete repeated study must follow the relationship map.',
    ],
    'episodes': [],
}

for ep in plan['episodes']:
    source_path = R / 'projects' / ep['slug'] / 'production/pacing-v3/edit-plan.json'
    pacing = read(source_path)
    events = pacing['events']
    picture = {}
    removed = 0
    for event in events:
        start = event['pictureAt'] + removed
        picture[event['key']] = (start, start + event['frames'])
        removed += event['frames']
    audio = {}
    removed = 0
    # Stable ordering matches pacing-v3/render.py, including same-time events.
    for event in sorted(events, key=lambda x: x['audioAt']):
        start = round(event['audioAt'] * 800) + removed * 800
        audio[event['key']] = (start, start + event['frames'] * 800)
        removed += event['frames']
    anchor = ep['insertion']['atSeconds']
    anchor_frame = round(anchor * 60)
    anchor_sample = round(anchor * 48000)
    moves = []
    for event in events:
        start, end = picture[event['key']]
        if event['kind'] != 'explanation' or start / 60 >= anchor:
            continue
        a, b = audio[event['key']]
        assert end <= anchor_frame + 1, (ep['id'], event['key'], 'anchor inside repeat picture')
        assert b <= anchor_sample + 800, (ep['id'], event['key'], 'anchor inside repeat music')
        n = event['sourceEndFrame'] - event['sourceStartFrame']
        body_pass_at_anchor = bool(event.get('followingNativePass') and abs(end - anchor_frame) <= 1)
        # A01's body changes the left panel into a frozen pose; its moving
        # preview is not the same comparison, so finish all three passes first.
        different_body_comparison = ep['id'] == 'A01' and event['key'] == 'pose'
        third_at_anchor = body_pass_at_anchor and not different_body_comparison
        repeat = 2 if third_at_anchor and event['repeatCount'] == 2 else 3
        moves.append({
            'key': event['key'],
            'originalPictureRangeFrames': [start, end],
            'originalPictureRangeSeconds': [start / 60, end / 60],
            'originalMusicOnlyRangeSamples': [a, b],
            'originalMusicOnlyRangeSeconds': [a / 48000, b / 48000],
            'existingInsertedPassCount': event['repeatCount'],
            'nativeSource': event['source'],
            'nativeSourceSha256': event['sourceSHA256'],
            'nativeSourceRangeFrames': [event['sourceStartFrame'], event['sourceEndFrame']],
            'normalSpeed': 1.0,
            'newInsertedPassCount': repeat,
            'newInsertedFrames': n * repeat,
            'thirdPassFromUnchangedBodyAtAnchor': third_at_anchor and repeat == 2,
            'shortIntroPreviewRetained': bool(event.get('followingNativePass') and not body_pass_at_anchor),
            'retainedPreviewCandidateRangeFrames': [end, end + n] if event.get('followingNativePass') and not body_pass_at_anchor else None,
            'bodyPassDifferentComparison': different_body_comparison,
            'thirdPassDecision': 'A01 body freezes the left panel at 34F for pose-versus-motion analysis. Replay the moving preview three times, then retain that analysis.' if different_body_comparison else 'Reuse the complete native body pass at the anchor as pass 3.' if third_at_anchor and repeat == 2 else 'Complete three native preview passes after the map.',
            'purpose': event['reason'],
        })
    removed_frames = sum(x['originalPictureRangeFrames'][1] - x['originalPictureRangeFrames'][0] for x in moves)
    new_frames = sum(x['newInsertedFrames'] for x in moves)
    prior = 0
    for move in moves:
        move['newStartFrameFormula'] = f"{anchor_frame - removed_frames} + mapFrames + {prior}"
        prior += move['newInsertedFrames']
    later = [e for e in events if e['kind'] == 'explanation' and picture[e['key']][0] / 60 >= anchor]
    out['episodes'].append({
        'id': ep['id'],
        'slug': ep['slug'],
        'pacingPlan': source_path.relative_to(R).as_posix(),
        'pacingPlanSha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'originalMapAnchorSeconds': anchor,
        'originalMapAnchorFrame': anchor_frame,
        'originalMapAnchorSample': anchor_sample,
        'beforeSentence': ep['insertion']['beforeSentence'],
        'mapAnchorAfterRemovalFrame': anchor_frame - removed_frames,
        'mapAnchorAfterRemovalSample': anchor_sample - removed_frames * 800,
        'moves': moves,
        'removedFrames': removed_frames,
        'newStudyFrames': new_frames,
        'durationDeltaExcludingMapFrames': new_frames - removed_frames,
        'firstUnmovedExplanationRepeat': {
            'key': later[0]['key'], 'originalRangeFrames': list(picture[later[0]['key']])
        } if later else None,
        'editStatus': 'relocate early normal-speed studies behind map' if moves else 'map already precedes first inserted explanation study; preserve original cuts',
        'qaRequired': [
            'Check final opening in motion with actual captions; map must precede the first complete repeated explanation study.',
            'Verify all old spoken PCM in the original order, and distinguish music-only removal intervals from neighboring speech.',
            'Check the three passes are whole actions at 1.0x, not partial cycles or six consecutive repeats.',
            'Check the return into the original beforeSentence and its matching body picture; do not freeze the former picture across the map.',
        ],
    })

(P / 'opening-layout.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', 'utf-8')
for ep in out['episodes']:
    print(ep['id'], 'moves', len(ep['moves']), 'removed', ep['removedFrames'], 'new', ep['newStudyFrames'], 'anchor', ep['mapAnchorAfterRemovalFrame'])
