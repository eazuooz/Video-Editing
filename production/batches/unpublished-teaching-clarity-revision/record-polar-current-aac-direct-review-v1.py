"""Record all38 full expected/recognized texts read; retain unresolved pronunciation."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
state=read(OUT/'current-whole-audio-asr-execution-v1.json')
assert state['exitCode']==0 and state['completed']==state['total']==38
local=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/current-whole-audio-v1'
bundle=read(local/'asr.json');assert bundle['complete'] and len(bundle['results'])==38
notes={
 '01':'Whole overview and both independent ending paragraphs cover height, camera, conversions and axis/boundary promise. 구면접표 is an ASR alternative to 구면좌표; human pronunciation remains pending.',
 '02':'Whole covers all seven paragraphs. Its extra tail repeats word timestamps40.00–49.98 after49.98 rather than advancing. Independent full last two paragraphs contain each sentence once and complete 그래서 두 위치를 따로 생각해야 하죠. Record the chunk-merge anomaly; do not infer actual repeated audio or regenerate PCM.',
 '03':'Whole retains component, cylindrical-surface and half-plane claims; independent full last two paragraphs match. Whole initial 먼저 is omitted by recognition and 세 값 appears 색값. Independently recheck the first two complete paragraphs before sealing this boundary.',
 '04':'Numeric5,0,3 and sqrt34≈5.83 are intact. Independent inverse/boundary context retains both complete paragraphs. 하이폿/하이포스 remains a pronunciation/recognizer alternative.',
 '05':'Horizontal/world-plane height versus terrain clearance claims are intact in whole and independent context. 세계 is recognized 색의 in both: unresolved human pronunciation; independently recheck this complete context.',
 '06':'Both angular references, sin/cos, latitude90−phi and altitude difference are intact. Whole 기준9 versus independent 기준구 is a recognition alternative; retain human review.',
 '07':'Whole retains heading/pitch sign, +pitch down and roll distinction. Spoken 지 축 is represented G축; independently recheck the full axis/sign paragraphs. Coordinate-term alternatives remain human pending.',
 '08':'Whole preserves all seven direction/attitude/projection paragraphs; independent last two paragraphs match. 세계의 위쪽 is recognized3개의 위쪽 in the middle: independently recheck that complete paragraph with its following context.',
 '09':'Every signed formula/reference direction survives. Whole 세계 좌표 is recognized3개 좌표, also in independent ending. Recheck complete unit/reference context; no inferred numeric error.',
 '10':'Inverse order, minus-height atan2, origin/pole and canonical-policy distinction are complete in whole and independent texts. Function-name and 조사 alternatives are human pending.',
 '11':'Whole seven paragraphs and independent relative-origin/inverse ending are complete. 세계 좌표→3개 좌표 and 역변환→역변한 are alternatives requiring human review; recheck the complete world-to-relative context.',
 '12':'Negative-distance and180-degree alias rules and90/45 versus−90/135 example are intact in both full contexts. No omitted/repeated claim found in these texts.',
 '13':'Canonical ranges, pole, direction-coordinate singularity versus full-attitude gimbal lock, and tolerance policy are intact in both full contexts.',
 '14':'Whole and independent preserve canonical representation versus smooth following and unverified engine claim. 제한→제안 alternative remains human pending.',
 '15':'Camera input0,1,0/r5/h60/p−30 and output3.75,3.5,2.165 are intact; independent full ending retains opposite subtraction and separate control rules. 간단한→단단한/책의→체계 recognition alternatives remain pending.',
 '16':'Whole seven paragraphs and independent last two contexts retain opposite subtraction, moving centre, obstruction and speed policy. 빼기→배기/수학→수확 alternatives remain human pending.',
 '17':'All five substantive paragraphs survive in whole text. Whole silence tail hallucinates 자막 제공...광고; independently decoded last two complete paragraphs end exactly at 중요합니다 without that addition. This is not evidence of actual an extra spoken sentence.',
 '18':'Whole and independent preserve separate position/attitude/viewpoint, useful coordinate scope and limits. Coordinate-name recognizer alternatives remain pending.',
 '19':'All three reference numeric directions and complete conclusion survive in whole and independent context. 세→새, 각도에→각도의 and coordinate terms are recognition alternatives; pending human listening.'}
rows=[]
for row in bundle['results']:
    source=local/(row['label']+'.json')
    assert sha(ROOT/row['windowPath'])==row['windowSha256']
    rows.append({**row,'directlyCompared':True,'fullTextReview':notes[row['scene']],
       'recognitionJson':source.relative_to(ROOT).as_posix(),'recognitionJsonSha256':sha(source)})
dest=OUT/'current-whole-aac-direct-review-v1.json'
record={'reviewedAt':datetime.now(timezone.utc).isoformat(),
 'sessionId':15271,'actualOuterExitCode':0,'exitObservedChunk':'a76f21',
 'aacSha256':state['aacSha256'],'wavSha256':state['wavSha256'],
 'all19WholeAnd19IndependentFullExpectedAndActualTextsDirectlyRead':True,'rows':rows,
 'adaptiveCompleteContextsPending':['03 first two','05 final two','07 axis/sign','08 world-up middle','09 units','11 world-to-relative'],
 'currentWholeMixedAsrApproved':False,'humanListeningApproved':False,'publicRightsApproved':False,
 'audioRegenerated':False,'wholeVideoApproved':False,'allFinalPixelsApproved':False}
if dest.exists():
    previous=read(dest)
    assert previous['exitObservedChunk']=='a76f21' and previous['rows']==rows and not previous['currentWholeMixedAsrApproved']
else:
    dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qfile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qfile)
assert not any(j['sessionId']==15271 for j in q['execution']['completedJobs'])
q['execution']['completedJobs'].append({'sessionId':15271,'pid':state['pid'],'createTime':state['createTime'],
 'state':(OUT/'current-whole-audio-asr-execution-v1.json').relative_to(ROOT).as_posix(),
 'actualOuterExitCode':0,'exitObservedChunk':'a76f21','all38FullTextsDirectlyRead':True,'currentAudioGateApproved':False})
render=read(OUT/'six-moving-pilots-execution-v4.json')
q['execution'].update(stage='polar-six-repaired-moving-pilots-running-adaptive-audio-preparation',
 heavyJob={'sessionId':20169,'pid':render['pid'],'createTime':render['createTime'],
 'state':(OUT/'six-moving-pilots-execution-v4.json').relative_to(ROOT).as_posix(),
 'cpuThreads':2,'gpuJobs':0,'runningExpected':render.get('exitCode') is None,
 'next':'Actual render exit and all six moving-captioned sample boards; then adaptive complete audio contexts and final whole original-AAC assembly.'},
 next='Do not rerun38 completed ASR contexts. Preserve unresolved human alternatives and old pilots. Review repaired six moving renders before whole54115-frame original-AAC final pair.')
q['updatedAt']=datetime.now(timezone.utc).isoformat();qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'fullTextsDirectlyRead':38,'currentAudioApproved':False,'activeRenderSession':20169}))
