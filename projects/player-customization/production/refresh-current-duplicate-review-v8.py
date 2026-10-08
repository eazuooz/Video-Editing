"""Seal directly compared new camera content and description-only receipt changes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = BASE / 'current-camera-and-description-duplicate-rereview-v8.json'
assert not PROOF.exists(), 'Read the saved review; do not repeat it.'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old = read(ROOT/'production/batches/sakurai-planning-game-design/preflight/player-customization.json')
changed = dict(zip([
    'game-math-euler-axis-angle','game-math-lines-bounds','game-math-orientation-matrices',
    'game-math-planes-barycentric','game-math-polar-2d','game-math-polar-3d',
    'game-math-polygons-triangulation','game-math-quaternion-operations',
    'game-math-rendering-light','game-math-rotation-interpolation'],[
    'ed9cf326e9f16ed4b75395d254258fb74d97e8206cd6b777e024113a4bac7e06',
    'f8614aa11adb46bd199553ac357d3e864fb1e3f514c361959299c9de6d5f53a3',
    '36a2f89dbde41ebbc4f06d77ce9ca29293db07e7e566cc41ab4b3c9b6c1fbf70',
    'c787a155a24d51540e7da740467fa292ccb1b6332cb0aee087b4e287fd2151cb',
    '46708590eb906e8a5a61eb91a513761f19f3f1488b404288bc35ac3ae9ec5ad5',
    '7e5bb51d4cdeea4076c0306a8fd5de94b24af2213933db47e37aeb89ae40c98a',
    '49e9a5a91faf6feb47871966a95c5e94cb8e1e41623aaf115d1d5a1db53552f8',
    '3b8556d162e25c690fd6d58604ea1b7414338248826b027b9a9396a7f4221074',
    'ae1ddecb76f89a5cfd75636ff5b70d64d49a3b22dbdbc9fa34fdd62211923f54',
    'e78997012129baf88b55715fd4a378bc3251e50a7cdb3efc3795bf1894abb466']))
actual = [dict(path=r['path'],sha256=sha(ROOT/r['path']),priorSha256=r['sha256']) for r in old['inputFiles']]
differences = [r for r in actual if r['sha256']!=r['priorSha256']]
assert {r['path']:r['sha256'] for r in differences} == {f'projects/{s}/publishing/youtube-upload.json':h for s,h in changed.items()}
new = {
    'project.json':'4a1467eda8a4e7ef7d3b2c14bc216322a3ab9a1dcc14208fd820753fa4e4aacc',
    'script/narration.ko.json':'b6179a450442bcaece55af475e9d45df11339b873f04b932a665954775e3c718',
    'script/narration.en.json':'769dad5381089968f1ec20c9d431e156b24183e03244579a9195174283969860',
    'planning/outline.md':'ed1c0ec687a1287a19707f999038709090b51fb3764dcb000527d8ecd26a4c55',
    'sources/SOURCES.md':'af5c5dd1343986dce60a815bbc84e8ee524db8cde7681fd96ebb79ead4da6150',
    'README.md':'e4b54e2ca2c522fded5cb986a841a431e23209744fd54c91ee10802c793e0f8c'}
for p,h in new.items():
    path=f'projects/game-math-camera-frustum/{p}'
    assert sha(ROOT/path)==h
    actual.append(dict(path=path,sha256=h,priorSha256=None))
studio=ROOT/'shared/output/player-customization/research/studio-current-change-v8.ax.txt'
assert studio.exists()
ax=studio.read_text('utf-8')
for vid in ['6-kP65hrZcI','ZLOewk8JHXA','PcxaKEvbzjg','-19ngvEqhao','L7SXFwn4i2k','wsxSYEEj8aQ']:
    assert f'/video/{vid}/edit' in ax
evidence=dict(schemaVersion=1,slug='player-customization',reviewedAt=datetime.now(timezone.utc).isoformat(),
    priorEvidence='projects/player-customization/production/current-lighting-and-rendering-private-duplicate-rereview-v7.json',
    originalWholeSourceAndPriorFullPairedContentReviewsPreserved=True,
    foreignInputSnapshot=actual,changedReceiptFiles=differences,
    receiptReviewScope='Directly reread each changed KO/EN full title, description and chapters, description-links revision, status and pending fields. Hash/pixel evidence arrays were retained, not claimed as fresh human reads. Prior unchanged full KO/EN scripts retain their complete comparisons.',
    receipts=[dict(slug=s,videoId=(d:=read(ROOT/f'projects/{s}/publishing/youtube-upload.json')).get('videoId'),descriptionLinksRevision=d.get('descriptionLinksRevision')) for s in changed],
    receiptDistinction='Added PART2 course, homepage and wiki links preserve each existing geometry/rotation/rendering question. No new player function-choice/preview/trial/expression content. Preserve observed foreign public/scheduled states over historical metadata privacy fields.',
    camera=dict(newFiles=new,wholeManifestOutlineSourcesReadmeDirectlyRead=True,wholeKoEnDirectlyRead=True,scenesPerLanguage=22,paragraphsPerLanguage=134,
        distinction='Camera/view/output rectangles, pixel/physical aspect, six clipping planes, FOV x/y, dolly versus zoom at distinct depths and orthographic projection address screen geometry. They differ from player function choice, observable preview/trial and personal expression. No private receipt exists for the new camera project; foreign40:60/noBGM and source-rights pending remain untouched.'),
    studio=dict(path=studio.relative_to(ROOT).as_posix(),sha256=sha(studio),scope='Fresh first30row snapshot; selected changed rows directly inspected; prior whole-channel content comparisons preserved. Does not claim all482videos newly read.',
        orientation='6-kP65hrZcI scheduled2026.10.11',polar3d='ZLOewk8JHXA scheduled2026.10.10',polar2d='PcxaKEvbzjg public',renderingLight='-19ngvEqhao private19:03',polygons='L7SXFwn4i2k private16:24',planes='wsxSYEEj8aQ private17:18',settingsChanged=False),
    foreignFilesModified=False,currentDistinctCheckPassed=False,uploaded=False)
PROOF.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason='Preserve prior whole source and42project full paired content comparisons. Directly read new camera22KO/EN scenes134paragraphs each plus entire manifest/outline/sources/README. Camera/view/output/aspect/frustum/FOV/dolly/orthographic questions differ from function choice/preview/trial/expression. Directly reread10changed full KO/EN metadata descriptions/chapters and description-only revisions; prior unchanged full scripts retain earlier reads. Actual Studio selected rows confirm foreign public/scheduled/private states; no foreign settings changed. See '+PROOF.relative_to(ROOT).as_posix()
for label,args in [('record',['--decision','distinct','--reason',reason,'--studio-evidence',PROOF.relative_to(ROOT).as_posix()]),('check',['--check'])]:
    command=[node,'scripts/review-video-duplicates.cjs','player-customization',*args]
    result=subprocess.run(command,cwd=ROOT,encoding='utf-8',capture_output=True)
    evidence[label+'Command']=command; evidence[label+'ExitCode']=result.returncode; evidence[label+'Output']=result.stdout+result.stderr
    assert result.returncode==0,evidence[label+'Output']
assert not [r for r in actual if sha(ROOT/r['path'])!=r['sha256']], 'Inputs changed during review'
evidence['currentDistinctCheckPassed']=True
PROOF.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf-8')
print(evidence['checkOutput'],end='')
