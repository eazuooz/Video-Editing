"""Seal direct reads of all181 encoded samples; prepare local normal-speed review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent; O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
s=read(O/'measured-manim-execution-v2.json')
assert s['actualOuterExitCode']==0 and s['actualCompletion']=='b522d3' and len(s['scenes'])==7
observations={
 '06a':'Local(1,0,0) / world(0,1,0) and the column interpretation are readable beside the projected body axes. Note/header/axis legend are separated; visible emphasis changes follow measured paragraph order.',
 '09a':'Body-to-world R and world-to-body transpose are distinguished. world(-1,2,0), dot results2/1 and R^T v_world=(2,1,0) are readable; orange vector appears before dot-product comparison.',
 '13a':'Length and angle distortion appear in the sampled body/axes, followed by restoration; length1, right angles, right-handedness and R^T R=I,det=+1 are separated from geometry.',
 '16a':'Parallel component removal is followed by normalization and zero/parallel fallback note. Formula/note/axis legend remain clear in the sampled motion; this uses a stated unit x-axis convention.',
 '21a':'Start I and targetRz180 are visible, followed by collapse of x/y columns at half component mixing. diag(0,0,1), zero x/y length and not-a-rotation result are readable.',
 '12':'Parent and child legend now sits below the axis-color legend with visible separation. ParentRx90 movement carries the child. AB maps(1,0,0) to(0,0,1); BA to(0,1,0), with rightmost-first reminder. Labels and figures do not overlap in all40 samples.',
 '18':'All44 samples show nine blue, three green and four gold cells with front/top/side projected faces. 36B/12B/16B headers,3DOF,unit-quaternion and component-only caveat stay clear. Timed enlargement emphasizes the corresponding storage groups without covering text.'}
rows=[]
for r in s['scenes']:
 for x in r['samples']+r['boards']:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/r['output'])==r['outputSha256']
 rows.append(dict(id=r['id'],samples=r['samples'],boards=r['boards'],output=r['output'],outputSha256=r['outputSha256'],renderExit=r['renderExitCode'],wholeDecodeExit=r['wholeDecodeExitCode'],extractExit=r['extractExitCode'],probe=r['probe'],observation=observations[r['id']]))
assert sum(len(r['samples']) for r in rows)==181 and sum(len(r['boards']) for r in rows)==34
p=O/'measured-manim-sampled-direct-review-v2.json';assert not p.exists()
p.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/measured-manim-execution-v2.json',executionSha256=sha(O/'measured-manim-execution-v2.json'),actualSession=20646,actualOuterExitCode=0,actualCompletion='b522d3',closureRecorder='c9efa9 exit0',all181EncodedSamplesAnd34BoardsDirectlyRead=True,shaMatched=True,rows=rows,sampledStructureAndLabelApproval=True,normalPlaybackApproved=False,allBetweenFramesApproved=False,humanContinuousListeningApproved=False,finalCuePixelsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGitAdded=0),ensure_ascii=False,indent=2)+'\n','utf-8')
media=ROOT/'shared/assets/presenting-game-scores/raw'
html=['<!doctype html><meta charset="utf-8"><title>Orientation measured7 · local only</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%;display:block}section{margin:20px 0}p{color:#ccc}</style><h1>Measured orientation explanation ·7 silent clips</h1><p>Normal1× muted visual review only. Final narration/captions/mix approval is pending.</p>']
for r in rows:
 src=ROOT/r['output'];dst=media/f"orientation-measured-v2-{r['id']}.mp4"
 if not dst.exists():os.link(src,dst)
 assert os.path.samefile(src,dst) and sha(dst)==r['outputSha256']
 html.append(f'<section><h2>{r["id"]}</h2><video id="v{r["id"]}" controls muted preload="metadata" src="{dst.name}"></video></section>')
hp=media/'orientation-measured-manim-v2-review.html';assert not hp.exists();hp.write_text('\n'.join(html),'utf-8')
print(json.dumps(dict(samples=181,boards=34,proof=rel(p),localPreview=rel(hp),sameInodeLinks=7,allFinalApprovals=False)))
