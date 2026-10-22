"""Register one permission-labelled inbound lead; no footage adoption."""
from polish_common import *
catalog = read(B / 'fhd-candidate-catalog.json')
ident = 'oU__wsOyeiY'
meta = R / f'shared/output/private-game-math-polish-20261022/fhd-candidates/{ident}.research.info.json'
m = read(meta)
assert m['id'] == ident and m['uploader'] == 'LUXURY GAMEZ'
assert 'Free To Use Gameplay' in m['description']
catalog[ident] = dict(
    game='A Story About My Uncle', url=f'https://www.youtube.com/watch?v={ident}',
    replaces='SSekdYTL4Ck', selectionStatus='metadata-only-await-decoding-and-content-review',
    permissionEvidence='Uploader labels this recording Free To Use Gameplay in title and description; no formal license identifier. General like/subscribe/share request is not performed. Preserve exact metadata, inspect recording provenance and credit uploader before adoption.',
    permissionMetadata=rel(meta), permissionMetadataSha256=sha(meta),
    uploader=m['uploader'], uploaderUrl=m['channel_url'],
    requiredCredit=f'A Story About My Uncle gameplay: LUXURY GAMEZ — https://www.youtube.com/watch?v={ident}',
    requiredAction='M10 scene19 village wooden columns and rails, if actually present; same game and narrated action only.',
    sourceAudioUsed=False, cutApproved=False)
save(B / 'fhd-candidate-catalog.json', catalog)
