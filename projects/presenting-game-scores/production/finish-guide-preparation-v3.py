"""Finish owned preparation after a path-format error; preserve prior files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
kp=ROOT/'projects/presenting-game-scores/script/observation-candidates-v3.ko.json'
ep=ROOT/'projects/presenting-game-scores/script/observation-candidates-v3.en.json'
mp=BASE/'observation-candidates-voice-manifest-v3.json'
ko=read(kp);en=read(ep);assert len(ko['scenes'])==len(en['scenes'])==11
assert all(len(s['lines'])==1 for s in ko['scenes'])
save(BASE/'guide-preparation-path-recovery-v3.json',dict(recordedAt=now,
 error='relative_to was called with a relative production Path and an absolute root; stopped during metadata preparation',
 preservedCompleteFiles=[dict(path=rel(p),sha256=sha(p)) for p in [kp,ep,mp]],
 ownTtsStateCreated=False,modelLoaded=False,gpuJobs=0,sourcePcmChanged=False))
rp=BASE/'observation-candidates-paired-direct-review-v3.json'
review=read(BASE/'observation-candidates-paired-direct-review-v2.json')
review.update(reviewedAt=now,guideParagraphs=9,
 priorPreparedOnlyReview=rel(BASE/'observation-candidates-paired-direct-review-v2.json'),
 priorPreparedOnlyReviewSha256=sha(BASE/'observation-candidates-paired-direct-review-v2.json'),
 decision='Keep each guide’s concrete source-reading paragraph; omit the prepared second paragraph’s repeated general advice. Original ten-scene/30-paragraph script and PCM are untouched. v2 files remain preparation history, not adopted footage or audio.',
 actualPairedTexts=[dict(id=k['id'],ko=k['lines'],en=e['lines']) for k,e in zip(ko['scenes'],en['scenes'])],
 estimatedGuideSeconds=None,guideSeconds='unmeasured; do not count character estimates as approved timing')
save(rp,review)
req=read(BASE/'observation-candidates-tts-request-v2.json')
out='shared/output/narration/presenting-game-scores/qwen3-observation-candidates-v3'
req.update(preparedAt=now,scriptReview=rel(rp),manifestOverride=rel(mp),scenes=[dict(id=x['id'],title=x['title'],paragraphs=len(x['lines']),text=' '.join(x['lines']),path=out+'/chunks/'+x['id']+'-scene.wav') for x in ko['scenes']])
req['protectedInputs']=[x for x in req['protectedInputs'] if x['path'] not in [
 'projects/presenting-game-scores/script/observation-candidates-v2.ko.json',
 'projects/presenting-game-scores/script/observation-candidates-v2.en.json',
 'projects/presenting-game-scores/production/observation-candidates-voice-manifest-v2.json',
 'projects/presenting-game-scores/production/observation-candidates-paired-direct-review-v2.json']]
req['protectedInputs'] += [dict(path=rel(p),sha256=sha(p)) for p in [kp,ep,mp,rp]]
save(BASE/'observation-candidates-tts-request-v3.json',req)
for k,e in zip(ko['scenes'],en['scenes']):print(json.dumps({'id':k['id'],'ko':k['lines'],'en':e['lines']},ensure_ascii=False))
src=(ROOT/'projects/similar-game-design/production/render-fresh-observation-guides-v4.py').read_text('utf-8-sig')
src=src.replace('similar-game-design','presenting-game-scores').replace('fresh-guides-tts-execution-v4','observation-candidates-tts-execution-v3').replace('fresh-guides-tts-request-v4','observation-candidates-tts-request-v3').replace('fresh-guides-tts-session-v4','observation-candidates-tts-session-v3')
src=src.replace("len(request['scenes'])==3","len(request['scenes'])==11").replace('total=3','total=11').replace("len(state['results'])==3","len(state['results'])==11")
src=src.replace('Three fresh primary-source observation guides only; original13, current joined04 and approved8 guides are immutable inputs.','Nine fresh observation guides and two unadopted exact-text paragraph takes; original10 PCM scenes are immutable inputs.')
src=src.replace('Prepared3 fresh guides/6 paired paragraphs; protected current67 PCM, approved voice inputs and current duplicate gate verified. Model0/GPU0.','Prepared9 guides/9 paired paragraphs plus2 exact-text candidates; protected original10 PCM and current duplicate gate verified. Model0/GPU0.')
src=src.replace('original13ChunksRegenerated=False','originalTenChunksRegenerated=False, candidateParagraphsAdopted=False')
src=src.replace('three-fresh-guides-voice-measurement-v4','single-observation-candidates-voice-measurement-v3').replace('three-fresh-guides-measured-awaiting-full-ASR-and-research-resume-verification','observation-candidates-measured-awaiting-full-ASR-and-research-resume-verification')
needle="check_gpu_tts_hold('presenting-game-scores','cuda:0',False)"
waiting="""import psutil
me=psutil.Process()
leasep=ROOT/'shared/output/GPU_HANDOFF.json'
lease=read(leasep) if leasep.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
owned=lease and lease.get('project')=='presenting-game-scores' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
    resource=read(BASE/'observation-candidates-resource-v3.json')
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    waiting=dict(schemaVersion=1,slug='presenting-game-scores',recordedAt=now(),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),stage='cooperative-job-boundary-wait-before-model',modelLoaded=False,gpuJobs=0,request=rel(REQUEST),requestSha256=sha(REQUEST),resource='projects/presenting-game-scores/production/observation-candidates-resource-v3.json',sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None)
    save(BASE/'observation-candidates-tts-waiting-v3.json',waiting)
"""
assert src.count(needle)==1;src=src.replace(needle,waiting+'\n'+needle)
wp=BASE/'render-observation-candidates-v3.py';assert not wp.exists();wp.write_text(src,'utf-8')
print('Prepared11 voice items. No model/render/adoption created.')
