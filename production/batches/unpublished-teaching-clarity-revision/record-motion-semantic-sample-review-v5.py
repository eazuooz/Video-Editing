from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('v5',Path(__file__).with_name('prepare-motion-semantic-anchors-v5.py'))
v5=importlib.util.module_from_spec(spec);spec.loader.exec_module(v5)
R,ROOT,d=v5.R,v5.ROOT,v5.draw
v4=d.read(R/'retained-semantic-anchor-preparation-v4.json');v5state=d.read(R/'retained-semantic-anchor-preparation-v5.json')
for s in [v4,v5state]:
    for w in s['windows']:
        for row in w['samples']+w['boards']:assert d.sha(ROOT/row['path'])==row['sha256']
p=R/'retained-semantic-sample-direct-review-v5.json';assert not p.exists()
d.save(p,dict(schemaVersion=1,reviewedAt=d.now(),reviewMethod='Direct reading of all24 v4 boards, all7 changed v5 boards, and native full-frame05/07/09/11 details.',
  v4=dict(samples=127,boards=24,allBoardsDirectlyRead=True,approved=False,
    findings=['05 f45/60/75/90 near-post coordinates lie beside timber; repaired in v5.',
      '07 later manual door mark lies past the actual blue door boundary; replaced by directly inspected cyan-edge samples in v5.']),
  selectedVersion='v5(two changed windows)+v4(four retained windows)',selectedSamples=127,selectedBoards=24,
  changedSamplesDirectlyRead=39,changedBoardsDirectlyRead=7,reusedSamplesDirectlyRead=88,reusedBoardsDirectlyRead=17,
  selectedSampleReviewPassed=True,allIntermediateFramesApproved=False,allFinalCaptionedPixelsApproved=False,currentMixedAudioApproved=False,
  sceneFindings={
    '01':'Compact white dot matches visible aim positions; unresolved f90 is hidden. Background marker suppressed after210 during camera turn.',
    '03':'Red mark surrounds observed aim dot; blue guide marks the left background upright. SourceHUD/credit and lower caption space are retained.',
    '05':'Repaired sampled near-post points lie on actual timber. Distant fence is separately named; no measured world depth/velocity or continuous same-fence-point claim. Fast pan1..14 and turn after90 unmarked.',
    '07':'The sampled cyan markers now touch the visible blue door boundary; absence/low visibility is hidden. The red arrow identifies the game laser; excerpts are not presented as a continuous solved puzzle.',
    '09':'Reticle centre changes after300; sampled red guides follow the observed aim region. Water begins at the end and is explicitly labelled as water.',
    '11':'Early off-centre/hidden reticle is unmarked. Later spray follows observed aim locations. Blue crossbar is suppressed when its previous line would lie in sky.'},
  quantitativeGameWorldClaims=False,clinicalComfortOutcomeClaimed=False,newGitImages=0,sourceOrPcmModified=0,
  selectedSampleArtifacts=[dict(scene=w['scene'],samples=w['samples'],boards=w['boards']) for w in v5state['windows']],
  next='SerialCPU2/GPU0 native-frame encode and direct encoded moving/caption review; this sample record does not approve final footage.'))
print('All selected127 samples/24 boards verified; moving final review remains pending.')
