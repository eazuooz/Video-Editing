"""Prepare only the new evidenced 06a repair, after all V4 selected pixels."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, py_compile
ROOT = Path(__file__).resolve().parents[3]; B = Path(__file__).resolve().parent
O = ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
out = O/'current34-06a-caption-clearance-timing-v1.json'; assert not out.exists()
rp = O/'current34-final-v4-pixels-partial-direct-review-v1.json'; r = rd(rp)
assert r['allNewDirectPixelsRead'] and (r['boardsDirectlyRead'], r['samplesDirectlyRead']) == (205, 818)
fp = O/'current34-final-v4-additional-clearance-findings-v1.json'; f = rd(fp)
assert len(f['findings']) == 1 and f['findings'][0]['scene'] == '06a'
assert sha(ROOT/f['findings'][0]['proof']['path']) == f['findings'][0]['proof']['sha256']
pairp = O/'current34-final-pair-execution-v4.json'; pair = rd(pairp)
assert pair['workerDead'] and pair['actualOuterExitCode'] == 0
piece = next(p for p in pair['pieces'] if p['id'] == '06a')
slot = copy.deepcopy(next(s for s in rd(O/'current34-detailed-explanation-timing-v1.json')['scenes'] if s['id'] == '06a'))
assert piece['frames'] == slot['frames'] == 759 and sha(ROOT/slot['voice']) == slot['voiceSha256']
assert sha(ROOT/piece['path']) == piece['sha256']
code = ROOT/'manim/projects/game-math-orientation-matrices/teaching_caption_clearance_06a_v1.py'
assets = [code, *[code.parent/name for name in ['teaching_revision_detailed_v1.py', 'teaching_baseline_detailed_v1.py', 'detailed_subjects_v1.py', 'detailed_camera_subject_v1.py']]]
absolute = sum(p['frames'] for p in pair['pieces'][:pair['pieces'].index(piece)])
assert absolute == 14232
ass = O/'current34.captions.ko.ass'
plan = dict(preparedAt=datetime.now(timezone.utc).isoformat(), visualOnly=True, scenes=[slot], code=rel(code), codeSha256=sha(code), assets=[dict(path=rel(p), sha256=sha(p)) for p in assets],
    findings=rel(fp), findingsSha256=sha(fp), finalV4Review=rel(rp), finalV4ReviewSha256=sha(rp), priorPair=rel(pairp), priorPairSha256=sha(pairp), priorPiece=piece,
    absoluteStartFrame=absolute, ass=rel(ass), assSha256=sha(ass), newTts=0, newAsr=0, newMix=0, fixedCaptionCenter=[960,970], bodyRatioAndTimingPreserved=True)
py_compile.compile(str(code), doraise=True)
py_compile.compile(str(B/'build-orientation-06a-caption-clearance-v1.py'), doraise=True)
out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
cp = rd(O/'latest-checkpoint.json'); assert cp['activeOwnedWorkers'] == 0
cp.update(recordedAt=plan['preparedAt'], stage='prepared-single-06a-caption-clearance', additionalClearanceFinding=rel(fp), additionalClearanceTiming=rel(out),
    allFinalPixelsApproved=False, next='Fresh resource, then one06a visual repair/current-caption binding. Review only new samples and normal endpoints before finalV5, retaining completed V4 selected pixels.')
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json'; old=qp.read_bytes(); q=rd(qp)
q['currentOrientationReview'].update(stage=cp['stage'],additionalClearanceFinding=rel(fp),additionalClearanceTiming=rel(out),allFinalPixelsApproved=False,next=cp['next']); q['updatedAt']=plan['preparedAt']; assert qp.read_bytes()==old
temp=qp.with_name(qp.name+'.writing'); temp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,qp)
print(json.dumps(dict(preparedScene='06a',frames=759,absoluteStart=absolute,plan=rel(out),sha256=sha(out),newAudio=0)))
