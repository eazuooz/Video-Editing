"""Prepare a single CPU2 measured Manim batch, leaving prototype outputs intact."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
source=ROOT/'production/batches/unpublished-teaching-clarity-revision/render-orientation-structural-prototypes-v1.py'
code=source.read_text('utf-8')
code=code.replace('structural-prototypes-v1','measured-manim-v2').replace('teaching_revision_v1.py','teaching_revision_v2.py').replace('structural-prototype-timing-v1','measured-manim-timing-v2').replace('structural-prototype-execution-v1','measured-manim-execution-v2')
start=code.index('assert not STATE.exists()');end=code.index('L.mkdir(parents=True)',start)
code=code[:start]+'''assert not STATE.exists() and not L.exists(),'Inspect existing measured work; never duplicate it.'
resource=read(R/'resource-before-cross-game-CPU-v4.json')
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
baseline=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
closed=read(R/'post-splice-current-voice-asr-execution-v1.json');assert closed['actualOuterExitCode']==0 and closed['completed']==3
assert read(R/'21a-spliced-whole-and-seam-direct-review-v1.json')['current21aCompletenessApproved']
plan=read(TIMING);assert sha(M)==plan['codeSha256'];scenes=plan['scenes']
for slot in scenes:assert sha(ROOT/slot['voicePath'])==slot['voiceSha256']
processes=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],encoding='utf8',text=True))
assert psutil.virtual_memory().available//1024>8_000_000
''' +code[end:]
code=code.replace("allMovingPixelsApproved=False,narrationTimed=False", "allMovingPixelsApproved=False,narrationTimed=True")
code=code.replace("'rendering-structural-prototypes'","'rendering-measured-seven-Manim-scenes'").replace("'completed-structural-prototypes-awaiting-direct-review'","'completed-measured-Manim-awaiting-direct-review'")
code=code.replace("for slot in scenes:\n        sid=", "for slot in scenes:\n        assert sha(ROOT/slot['voicePath'])==slot['voiceSha256']\n        sid=")
out=B/'render-orientation-measured-manim-v2.py';assert not out.exists();out.write_text(code,'utf-8');compile(code,str(out),'exec');print('Prepared single CPU2/GPU0 measured7; render0.')
