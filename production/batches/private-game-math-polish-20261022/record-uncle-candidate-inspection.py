"""Record actual candidate-sheet findings; grants no production-cut approval."""
from polish_common import *

p = B / 'uncle-triangle-cut-samples.json'
d = read(p)
d.update(
    status='sample-inspection-complete-cut-revision-required',
    directlyInspectedSheets=list(range(1, 11)),
    directlyInspectedSampleCount=len(d['samples']),
    continuousPlaybackReviewed=False,
    productionCutApproved=False,
    observations=[
        {'sourceRange': [325, 341], 'finding': 'M11 opening mismatch: floor/bridge and generic glyphs first, then a fall/reset; bright triangle narration lacks matching initial target. Reject this proposed start.'},
        {'sourceRange': [342, 355], 'finding': 'Triangular components on glowing rock glyph visible during approach/grapple and floor landing. Candidate alternative M11 start342 needs continuous playback and fixed narration cue check.'},
        {'sourceRange': [375, 431.5], 'finding': 'M12 upward/downward grapples, changing rock targets and triangle components, then landing/walking bridge. Potential match; not approved until narration alignment and playback.'},
    ],
    nextAction='Retarget M11 scene08 candidate to342s; verify exact windows with original narration. Preserve frame counts. No master or cut approval yet.',
)
save(p, d)

p = B / 'portal-fhd-format-search.json'
d = read(p)
meta = R / 'shared/output/private-game-math-polish-20261022/fhd-candidates/8h0XTRFGwOQ.research.info.json'
m = read(meta)
formats = sorted(set((x.get('width', 0), x.get('height', 0), x.get('fps', 0)) for x in m.get('formats', []) if x.get('height')))
d['8h0XTRFGwOQ'] = {
    'url': 'https://www.youtube.com/watch?v=8h0XTRFGwOQ',
    'title': m.get('title'), 'uploader': m.get('uploader'),
    'formats': formats, 'metadata': rel(meta), 'metadataSha256': sha(meta),
    'approved': False,
    'reason': 'Maximum available video height720; publisher upload fails required native FHD.',
}
save(p, d)
print('Candidate findings recorded; no production-cut approval.')
