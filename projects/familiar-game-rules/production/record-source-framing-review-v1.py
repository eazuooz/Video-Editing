"""Record actual direct reads of all30 stress boards, without granting final approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

dest=PROOF/'source-framing-direct-review-v1.json'
assert not dest.exists(), 'Preserve existing direct review'
execution=read(PROOF/'source-framing-execution-v1.json')
assert execution['boardCount']==30 and execution['sampleCount']==180
assert len(execution['children'])==9 and all(x['exitCode']==0 for x in execution['children'])
assert execution['status']=='source-framing-stress-extracted-awaiting-direct-review'
notes=[
 '01/02: first-person centre targets clear; lower gun/leg edges enter the maximum mask. Exact kick/action cues still need final inspection.',
 '03/04: alley/blue-hall kick and catwalk target are above the mask; separate trailer edits are retained as separate shots.',
 '05/06: ceiling aim and crossbow/bathroom targets remain above the mask in these samples.',
 '07/08: bathroom/pizza and disco/living-room aim targets are above the mask.',
 '09/10: furniture kick and room target are central; final literal cues must still show the kick contact.',
 '12/13: air player above mask, but action13 last30.483 factory-floor lower body overlaps maximum two-line box.',
 '14/15: platform ascent clear; action15 first33.5/middle34.23 lower body/feet behind box while upper target stays visible.',
 '16/17: action16 ground body close to top of box; action17 middle42.23 lower body behind box, later airborne body clear.',
 '18/19: airborne player/eye action above box; low debris is covered and cannot be used as an action claim.',
 '20/21: action20 first24.5/middle25.73 player body largely behind box; ceiling target visible. Crusher passage core above box.',
 '22/23: action22 first32.5 ground lower body hidden; later air/grenade targets clear. action23 middle low enemy partly masked.',
 '24/25: action24 first58 player lower body hidden; later elevated body clear. action25 platform body clear, low enemy legs masked.',
 '26/27: barrel/upper aim and zipline body above box; lowest target edges still require literal-cue checks.',
 '28/29: spin above box; inverted player clear but lower opposing targets/aim-line ends partly masked.',
 '30/31: vertical swing middle38.43/last39.98 lower body overlaps; glass-jump body above box.',
 '32/33: train boss/player feet partly masked in first32 sample; upper/air player and two-level core visible.',
 '35/36: player generally central, lower-floor opponents partly masked, especially35first/middle and36last.',
 '37/38: two-level player clear; lower-floor target bodies repeatedly behind mask. Those targets cannot be approved by these samples.',
 '39/additional01: shaft body upper/central, lowest targets at103.083/106.183 near box; first-person corridor/pink-door targets central.',
 'additional02/03: brain-hall/pink-bath and escalator upper aim/kick central and above mask.',
 'additional04/05: pink shotgun hall/dark stairs and doorway/green bathroom target centres visible.',
 'additional06/07: close bathroom/purple upper aim and classroom upward kick/minigun target centres visible.',
 'additional09/10: downward escalator door kick and flaming crossbow/upward kick core above box; actual contact cues need full motion.',
 'additional11/13: purple hall/roof kick and lobby/checkered hall target centres visible.',
 'additional16/17: additional16first18.5185 ground player mostly masked and20.0333 lower body masked; wire/roof umbrella and17 rooftop opponents clear.',
 'additional22/25: rail8 and market9.9667 ground bodies/targets partly masked;22last11.9667 descending player at right edge must remain in frame.25 swamp/containers upper combat clear.',
 'Hype01/02: train interior body and elevated crate targets above mask; native tilt black world region is not a PPT border.',
 'Hype03/04: opposite-direction airborne guns and varied-height crate targets visible; explosions briefly obscure action but no invented result is claimed.',
 'Hype05/06: upper body/downward guns visible; low carriage targets/feet may touch mask. Inspect every actual cue and intervening frame before approving.',
 'Hype07/08: spin/roof and descent/shooting remain above mask; lowest opponent feet partly covered, upper target directions visible. No claim about input bindings.'
]
assert len(notes)==30
boards=[]
for b,note in zip(execution['boards'],notes):
    assert sha(ROOT/b['path'])==b['sha256']
    for x in b['tiles']:
        assert sha(ROOT/x['path'])==x['sha256'] and sha(ROOT/x['nativePath'])==x['nativeSha256']
    boards.append({**b,'directlyRead':True,'observation':note,'allFinalPixelsApproved':False})
conflicts=['action-13','action-15','action-16','action-17','action-20','action-22','action-23','action-24','action-25','action-26','action-29','action-30','action-32','action-35','action-36','action-37','action-38','action-39','additional-16','additional-22','hype-05','hype-06','hype-07','hype-08']
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),execution=rel(PROOF/'source-framing-execution-v1.json'),executionSha256=sha(PROOF/'source-framing-execution-v1.json'),
 actualWorker=dict(pid=45500,sessionId=27650,exitCode=0,actualExitObserved=True,alive=False,commandLine=execution['commandLine']),
 boards=boards,all30BoardsDirectlyRead=True,all180SourceSamplesDirectlyRead=True,scope='Source first/middle/last stress-mask samples; not actual encoded final cues or complete motion',
 stressMask=execution['stressMask'],conflictOrLiteralCueCheckClipIds=conflicts,
 remedy='Keep caption centre960,970. Use shorter literal cues, recompose source/crop or reassign source intervals; directly inspect all actual cue/cut pixels and motion. Never clear final gate from this maximum-mask sample review.',
 fullScreenFramingApproved=False,allFinalCaptionPixelsReviewed=False,captionAnchorChanged=False,finalTimingApproved=False,newGitImages=0)
save(dest,review)
qpath=PROOF.parent/'queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='all-source-framing-samples-read-additive-guidance-pre-TTS',updatedAt=now(),sourceFramingReview=rel(dest),
 nextAction='Write independent matching KOEN observation guides and separate MC entrypoints from reviewed actual actions, preserving all11 original PCM and147.2s white. Then measure only new guides; resolve flagged source/literal-cue overlaps before final approval.')
item['sourceFramingExecution'].update(sessionId=27650,status='closed-all30stress-boards-directly-read-final-framing-pending',exitCode=0,actualExitObserved=True,alive=False)
q['updatedAt']=now();save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','sourceFramingReview','sourceFramingExecution','nextAction']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(boards=30,samples=180,allDirectlyRead=True,framingApproved=False,sessionId=27650,newGitImages=0)))
