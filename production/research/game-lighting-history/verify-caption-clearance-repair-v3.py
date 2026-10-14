"""Verify the sole targeted explanation render without changing audio or final approval."""
import importlib.util
from pathlib import Path
p = Path(__file__).with_name('review-media-common-v15.py')
s = importlib.util.spec_from_file_location('review_media', p)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
plan_path = m.PROD / 'caption-clearance-repair-plan-v3.json'
plan = m.read(plan_path)
execution = m.read(m.ROOT / plan['execution'])
assert execution['status'] == 'complete' and execution['exitCode'] == 0
assert plan['name'] + '.mp4' in execution['command']
formatting = []
for i in plan['inputs']:
    if m.sha(m.ROOT / i['path']) == i['sha256']: continue
    assert i['path'].endswith('-project.meta'), 'Actual input changed: ' + i['path']
    expected = dict(version=0, shared=dict(background=None, range=[0, (plan['frames']-1)/60], size=dict(x=1920,y=1080), audioOffset=0),
                    preview=dict(fps=60,resolutionScale=1), rendering=dict(fps=60,resolutionScale=1,colorSpace='srgb',
                    exporter=dict(name='@motion-canvas/ffmpeg',options=dict(fastStart=True,includeAudio=False))))
    assert m.read(m.ROOT / i['path']) == expected, 'Render settings changed'
    formatting.append(dict(path=i['path'], preparedSha256=i['sha256'], actualSha256=m.sha(m.ROOT / i['path']), semanticallyIdentical=True))
assert m.sha(m.ROOT / plan['sourceReview']['path']) == plan['sourceReview']['sha256']
state_path = m.PROD / 'caption-clearance-repair-verification-execution-v3.json'
assert not state_path.exists(), 'Preserve completed or partial verification'
out = (m.ROOT / plan['output']).parent
state = dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=m.resources(),cpuThreads=2,gpuJobs=0,active=None)
m.save(state_path,state)
try:
    proof = m.verify_video(m.ROOT / plan['output'],plan['frames'],state,state_path,out,plan['name'])
    proof.update(plan=dict(path=m.rel(plan_path),sha256=m.sha(plan_path)),exporter=execution,metaFormatting=formatting,
                 unchangedNarration=True,unchangedCaptions=True,allFinalPixelsReviewed=False,collected=False,uploaded=False)
    m.save(out/(plan['name']+'.verification.json'),proof)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),verification=m.rel(out/(plan['name']+'.verification.json')),active=None)
    m.save(state_path,state)
    print(m.json.dumps(dict(clips=17,frames=plan['frames'],ptsContinuous=True,decode=0,pixelsApproved=False)),flush=True)
except BaseException as e:
    state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=str(e));m.save(state_path,state);raise
