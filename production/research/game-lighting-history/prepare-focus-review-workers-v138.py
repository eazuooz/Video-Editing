"""Version-scoped workers for the three evidenced focus overlay repairs."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'production/research/game-lighting-history'
def write(name, text):
    target = P / name
    assert not target.exists(), 'Preserve previous versions'
    target.write_text(text, 'utf-8')
audio = (P / 'assemble-guided-source-render-audio-v132.py').read_text('utf-8')
write('assemble-guided-focus-clearance-audio-v137.py', audio.replace('five selected', 'three selected').replace('guided-source-render-v132', 'guided-focus-clearance-v137'))
review = (P / 'build-guided-source-review-v135.py').read_text('utf-8')
review = review.replace('v132', 'v137').replace('v135', 'v138').replace('V135', 'V138')
review = review.replace('guided-source-render-v137', 'guided-focus-clearance-v137').replace('N == 5206', 'N == 3280').replace('len(cues) == 28', 'len(cues) == 18')
review = review.replace('Five black', 'Three repaired black').replace('all28', 'all18')
write('build-guided-focus-review-v138.py', review)
qa = (P / 'extract-guided-source-qa-v136.py').read_text('utf-8')
qa = qa.replace('v136', 'v139').replace('V136', 'V139').replace('v135', 'v138').replace('all28', 'all18').replace('all5', 'all3').replace("len(layout['cues'])==28", "len(layout['cues'])==18").replace('frame<5206', 'frame<3280')
write('extract-guided-focus-qa-v139.py', qa)
print('Prepared three scoped workers; no render, image or approval created.')
