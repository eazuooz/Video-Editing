"""Record directly read current foreign changes and the observed Studio row."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = BASE / 'current-lighting-and-rendering-private-duplicate-rereview-v7.json'
assert not PROOF.exists(), 'Read the saved review; do not repeat it.'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/player-customization.json')
changed = {
    'projects/game-lighting-history-01/script/narration.ko.json': '7d13711b8ff5d73d7e68a877efccf49c484e321d022708ccc835d361ed7bc48b',
    'projects/game-math-rendering-light/project.json': 'ea538a9f07f2e58fa2c7fbc90e3c45ac7e41a447db49c957131042ba11261eef',
    'projects/game-math-rendering-light/publishing/youtube-upload.json': '4176de514a01d7fb034815359aff06d5663706e91c6a6017af563ff4275016d2',
}
actual = [dict(path=r['path'], sha256=sha(ROOT/r['path']), priorSha256=r['sha256']) for r in old['inputFiles']]
differences = [r for r in actual if r['sha256'] != r['priorSha256']]
assert {r['path']:r['sha256'] for r in differences} == changed, 'New inputs require another complete direct comparison.'
lighting = read(ROOT/'projects/game-lighting-history-01/script/narration.ko.json')
studio = ROOT/'shared/output/player-customization/research/studio-current-change-v7.ax.txt'
assert studio.exists()
assert '/video/-19ngvEqhao/edit' in studio.read_text('utf-8')
evidence = dict(schemaVersion=1, slug='player-customization', reviewedAt=datetime.now(timezone.utc).isoformat(),
    priorEvidence='projects/player-customization/production/current-lighting-repair-and-polygon-private-duplicate-rereview-v6.json',
    originalWholeSourceAndPriorFullPairedContentReviewsPreserved=True,
    changedForeignFilesWholeContentsDirectlyRead=True, changedForeignInputs=differences,
    unchangedForeignInputsRetainPriorDirectReads=True, foreignInputSnapshot=actual,
    lighting=dict(scenes=len(lighting['scenes']), paragraphs=sum(len(x['lines']) for x in lighting['scenes']),
        changedWholeKoRead=True, enUnchangedPriorWholeRead=True,
        distinction='Lightmap storage/filtering, geometry/normal maps, CSM, PCF and forward/deferred/SSAO history explain light evaluation. These questions differ from selecting a player function, previewing its visible action, trying it and personal expression.'),
    renderingLight=dict(wholeManifestAndSavedPrivateReceiptRead=True, videoId='-19ngvEqhao', frames=68540, seconds=1142.3333333333333,
        completeKoEnScriptsUnchangedPriorWholePairedReads=True,
        distinction='Visible surface/depth selection, radiometric units, BRDF/BSSRDF and the rendering equation explain pixel colour. These questions differ from player function choice/preview/trial/expression. Preserve foreign40:60/noBGM and historical pending fields.'),
    studio=dict(path=studio.relative_to(ROOT).as_posix(), sha256=sha(studio),
        scope='Current first-page snapshot saved; changed rendering-light row directly read. Prior whole channel inventory and earlier content comparisons preserved. No claim that all30rows were newly read.',
        renderingLight=dict(videoId='-19ngvEqhao', observed='19:03;private;uploaded2026.10.8;1view;no current alert', idLinkObserved=True),
        foreignPublicAndScheduledStatesPreserved=True, settingsChanged=False),
    foreignFilesModified=False, currentDistinctCheckPassed=False, uploaded=False)
PROOF.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n','utf-8')
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason = ('Preserve original whole source and prior full paired overlap comparisons. Directly reread the entire changed108paragraph lighting KO script, rendering-light68540frame manifest and saved-private receipt. The unchanged EN and rendering KOEN scripts retain their earlier complete direct comparisons. Current Studio exactID -19ngvEqhao19:03private/no alert observed. Lightmap/filtering/shadow/deferred history and surface/depth/radiometry/BRDF/rendering-equation questions differ from player function choice/preview/trial/expression. Foreign40:60/noBGM, pending historical fields and public/scheduled states are preserved. See '+PROOF.relative_to(ROOT).as_posix()+'.')
for label, args in [('record', ['--decision','distinct','--reason',reason,'--studio-evidence',PROOF.relative_to(ROOT).as_posix()]), ('check',['--check'])]:
    command = [node,'scripts/review-video-duplicates.cjs','player-customization',*args]
    result = subprocess.run(command,cwd=ROOT,encoding='utf-8',capture_output=True)
    evidence[label+'Command']=command; evidence[label+'ExitCode']=result.returncode
    evidence[label+'Output']=result.stdout+result.stderr
    assert result.returncode==0, evidence[label+'Output']
evidence['foreignHashChangesDuringReview']=[r['path'] for r in actual if sha(ROOT/r['path'])!=r['sha256']]
assert not evidence['foreignHashChangesDuringReview']
evidence['currentDistinctCheckPassed']=True
PROOF.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf-8')
print(evidence['checkOutput'],end='')
