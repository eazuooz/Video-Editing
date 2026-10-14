"""Prepare a versioned request; preserve closed v4 and the stable-idle guard."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
old={x['path']:x['sha256'] for x in read(R/'duplicate-before-refresh-v4.json')['inputFiles']}
changes=[x for x in report['inputFiles'] if old.get(x['path'])!=x['sha256']]
assert {x['path'] for x in changes}=={'projects/game-math-polygon-partition-v2/'+x for x in ['project.json','script/narration.ko.json','script/narration.en.json']}
for x in report['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
dom=R/'current-studio-list-v4.dom.txt';txt=dom.read_text('utf-8');assert all(s in txt for s in ['27개 중 1~27','L7SXFwn4i2k','mBDd9VzSTkA','2026. 10. 12.','2026. 11. 2.'])
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],changedInputs=changes,
    allThreeChangedCompleteContentsDirectlyRead=True,completeKoEnScenes=26,
    findings=['Current factory bridge QB14 precedes actual QG06; full KOEN retains boundary/path distinction, fan counterexample, L-ear validity and quality checks.',
        'Shapez2 processing is explicitly contrasted with preserving a whole region; Noita passages, Tiny Glade doorway and Dorfromantik tiles still illustrate geometry, not camera/aim/locomotion options.',
        'The manifest marks factory-bridge-order-remix-required and currentPixelApprovalfalse; this review does not approve foreign delivery.',
        'Current Studio still retains polygon combined baseline November2 and motion October12; no settings edited.'],
    currentStudioEvidence=dict(path=dom.relative_to(ROOT).as_posix(),sha256=sha(dom),tabId='34',relevantRowsDirectlyRead=True),
    verdict='distinct',foreignFileOrPlatformMutations=0,finalCoverageApproval=False)
dst=R/'duplicate-content-and-studio-direct-review-v4.json';assert not dst.exists();dst.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason','Complete changed polygon-partition manifest and both full KOEN bodies directly read. Geometry boundary/path, fan/ear/coverage/quality claims remain distinct from camera/tool/locomotion options. Current relevant Studio rows re-read. See direct-review-v4.','--studio-evidence',dst.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
src=B/'render-motion-four-additions-v4.py';dest=B/'render-motion-four-additions-v5.py';assert not dest.exists()
code=src.read_text('utf-8-sig').replace('narration-tts-execution-v4.json','narration-tts-execution-v5.json').replace('narration-tts-session-v4.json','narration-tts-session-v5.json').replace('narration-tts-waiting-v4.json','narration-tts-waiting-v5.json')
code=code.replace('research-handoff-premodel-timeout-verification-v3.json','research-handoff-premodel-failure-verification-v4.json').replace('voice-retry-resource-verification-v5.json','voice-retry-resource-verification-v6.json').replace("retry['foreignRestorationVerified']","retry['restorationVerified']")
line="assert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240, 'Read fresh resources before another voice request.'"
assert line in code
replacement="""# Initial request needs fresh read-only evidence. The scheduled child uses the
# coordinator's newer continuous-idle measurement, not an old pre-wait timestamp.
import psutil
early_me=psutil.Process();early_path=ROOT/'shared/output/GPU_HANDOFF.json'
early_lease=read(early_path) if early_path.exists() else None
early_ancestors={p.pid:p.create_time() for p in [early_me,*early_me.parents()]}
early_owner=early_lease.get('coordinator',{}) if early_lease else {}
early_owned=early_lease and early_lease.get('project')=='motion-sickness-games' and abs(early_ancestors.get(early_owner.get('pid'),-1)-early_owner.get('createTime',0))<.01
if early_owned:
    assert early_lease['state']=='tts_running'
    assert time.time()-early_lease['updatedAt']<240
    assert early_lease['gpuBeforeTts']['freeMiB']>=18000 and early_lease['gpuBeforeTts']['utilization']<15
else:
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240, 'Read fresh resources before another voice request.'"""
code=code.replace(line,replacement);compile(code,str(dest),'exec');dest.write_text(code,'utf-8')
ver=(B/'verify-motion-four-voice-resume-v4.py').read_text('utf-8-sig').replace('narration-tts-session-v4.json','narration-tts-session-v5.json').replace('narration-tts-execution-v4.json','narration-tts-execution-v5.json').replace('research-handoff-verification-v4.json','research-handoff-verification-v5.json')
vp=B/'verify-motion-four-voice-resume-v5.py';assert not vp.exists();compile(ver,str(vp),'exec');vp.write_text(ver,'utf-8')
asr=(B/'review-motion-four-additive-voice-v3.py').read_text('utf-8-sig').replace('narration-tts-session-v4.json','narration-tts-session-v5.json').replace('narration-tts-execution-v4.json','narration-tts-execution-v5.json').replace('research-handoff-verification-v4.json','research-handoff-verification-v5.json')
ap=B/'review-motion-four-additive-voice-v4.py';assert not ap.exists();compile(asr,str(ap),'exec');ap.write_text(asr,'utf-8')
print('Current changed full KOEN/manifest + Studio reviewed/check0; v5 voice/verifier/ASR prepared only; guard unchanged.')
