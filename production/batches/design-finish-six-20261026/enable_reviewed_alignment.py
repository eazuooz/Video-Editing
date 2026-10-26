"""Permit an explicit ASR word-index selection, preserving raw ASR and PCM."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parents[3]
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
HELPER='''def reviewed_alignment_words(recognition,cache_path,audio_digest):
    selection=NARRATION/'alignment-selection-review.json'
    if not selection.exists():return recognition['words'],None
    review=read(selection)
    if review.get('sourceAsrSha256')!=sha(cache_path) or review.get('sourceAudioSha256')!=audio_digest or review.get('fullRawTextCompared') is not True or not review.get('reason'):
        raise ValueError('Reviewed alignment selection is stale or incomplete')
    indices=review.get('keepWordIndices')
    if not isinstance(indices,list) or not indices or indices!=sorted(set(indices)) or any(not isinstance(i,int) or i<0 or i>=len(recognition['words']) for i in indices):
        raise ValueError('Selection must preserve source index order; no invented words or timestamps')
    kept=[recognition['words'][i] for i in indices]
    starts=[w['timestamp'][0] for w in kept]
    if any(t is None for t in starts) or starts!=sorted(starts):raise ValueError('Selected source word starts must be monotonic')
    return kept,artifact(selection)


'''
for slug in SLUGS:
 p=R/'projects'/slug/'production/batch-v1/audio_pipeline.py';text=p.read_text('utf8')
 if 'def reviewed_alignment_words(' in text:continue
 text=text.replace('def split(review_path, overrides_path=None):',HELPER+'def split(review_path, overrides_path=None):')
 text=text.replace('    inputs = {"sourceSha256": digest, "asrSha256": sha(cache), "scripts": script_files,','    selected_words,selection_artifact=reviewed_alignment_words(recognition,cache,digest)\n    inputs = {"sourceSha256": digest, "asrSha256": sha(cache), "alignmentSelection":selection_artifact, "scripts": script_files,')
 text=text.replace('aligned_words = pronunciation_words(recognition["words"])','aligned_words = pronunciation_words(selected_words)')
 ast.parse(text);p.write_text(text,'utf8')
print('Six new runtimes support explicit reviewed alignment index selections; originals untouched')
