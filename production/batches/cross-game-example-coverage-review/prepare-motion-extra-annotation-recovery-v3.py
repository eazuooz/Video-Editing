"""Seal actual V2 sample review, retain Portal, repair only held PowerWash anchors."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';B=Path(__file__).parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
e=read(R/'extra-annotation-pieces-execution-v2.json')
try:
 p=psutil.Process(e['pid']);assert abs(p.create_time()-e['createTime'])>=.01
except psutil.NoSuchProcess:pass
assert e['exitCode']==0 and e['encodedSampleCount']==84 and e['boardCount']==22
checked={}
for p in e['pieces']:
 assert all(p[k]==0 for k in ['decodeExitCode','encodeExitCode','wholeDecodeExitCode','extractionExitCode'])
 for x in [p]+p['samples']+p['boards']:
  assert sha(ROOT/x['path'])==x['sha256'];checked[x['path']]=x['sha256']
e.update(actualOuterSession=79352,actualOuterExitCode=0,actualOuterCompletion='9db1a6',originalWorkerAlive=False)
(R/'extra-annotation-pieces-execution-v2.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=dict(schemaVersion=1,reviewedAt=stamp,actualSession=79352,actualCompletion='9db1a6',actualExitCode=0,
 directlyReadEncodedSamples=84,directlyReadBoards=22,sha256RecheckedFiles=checked,
 findings={'Portal':'All31 sampled frames read: red cube and initial cyan wall role points visible; markers hidden across uncertain putdown/crop/pickup. HUD and caption preview clear. Retain this rendered piece; no rerender.',
 'PowerWash':'All53 sampled frames read: HUD/caption clearance retained, but cyan hut point wanders onto fence at encoded195/210 and red tool points visibly miss at600/630/645, with additional offsets through fast aim. Entire moving annotation adoption held pending coordinate repair.'},
 portalSampledRoleApproval=True,powerwashSampledRoleApproval=False,
 allIntermediateFramesRead=False,normalPlaybackApproved=False,narrationTimed=False,finalCueApproval=False,
 worldMeasurementApproved=False,localOnly=True)
assert not (R/'extra-annotation-pieces-sampled-direct-review-v2.json').exists()
(R/'extra-annotation-pieces-sampled-direct-review-v2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(R/'extra-annotation-observation-plan-v1.json')
plan.update(schemaVersion=2,preparedAt=stamp,previous='extra-annotation-observation-plan-v1.json',
 repairEvidence='extra-annotation-pieces-sampled-direct-review-v2.json',
 pointPrecision='Manually estimated visible tool region and hut from current encoded samples; requires new encoded review. No physical centroid claim.')
pw=[r for r in plan['observations'] if r['sourceId']=='powerwash-independent-nozzle-aim']
# Coordinates directly estimated in current1920x1080 fit render; invert only its documented fit.
fix={12:[1532,458],13:[1532,392],14:[1532,500],15:[1532,460],16:[1532,384],17:[1532,450],18:[1532,516],19:[1532,576],20:[1532,636],
25:[1090,862],26:[1035,889],27:[1020,889],28:[1010,710],29:[872,680],30:[820,640],31:[820,640],32:[728,642],33:[695,644],
34:[566,646],35:[556,640],36:[578,642],37:[578,642],38:[566,642],39:[566,642],40:[640,565],41:[850,462],42:[850,485],
43:[870,360],44:[860,466],45:[850,568],46:[850,640],47:[850,602],48:[1200,527],49:[1298,582],50:[1200,634],51:[1110,640],52:[1220,580]}
def inv(pt):return [round((pt[0]-160)/1.25),round(pt[1]/1.25)]
for i,row in enumerate(pw):
 if i in fix:row['redObservedSamplePoint']=inv(fix[i])
 if 12<=i<=16:row['blueObservedSamplePoint']=inv([580,330])
 elif 17<=i<=33:row['blueObservedSamplePoint']=inv([584,370])
 elif i>=34:row['blueObservedSamplePoint']=inv([625,365])
 row['redLabel']='조작 대상: 도구'
(R/'extra-annotation-observation-plan-v2.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'render-motion-extra-annotation-pieces-v2.py').read_text('utf-8')
src=src.replace('extra-annotation-pieces-v2','extra-annotation-pieces-v3').replace('extra-annotation-pieces-execution-v2','extra-annotation-pieces-execution-v3').replace('extra-annotation-pieces-current-cim-v2','extra-annotation-pieces-current-cim-v3')
src=src.replace('render-motion-extra-annotation-pieces-v2.py','render-motion-extra-annotation-pieces-v3.py').replace("plan=read(R/'extra-annotation-observation-plan-v1.json')","plan=read(R/'extra-annotation-observation-plan-v2.json')")
src=src.replace("pieces=read(R/'narration-led-cut-allocation-proposal-v2.json')['cuts']","pieces=[p for p in read(R/'narration-led-cut-allocation-proposal-v2.json')['cuts'] if p['game']=='PowerWashSimulator']\nassert len(pieces)==1")
src=src.replace("(R/'extra-annotation-framing-plan-v2.json').write_text(json.dumps(framing,ensure_ascii=False,indent=2)+'\\n','utf-8')","# Current framing already reviewed; preserve V2 framing evidence.")
assert not (B/'render-motion-extra-annotation-pieces-v3.py').exists()
(B/'render-motion-extra-annotation-pieces-v3.py').write_text(src,'utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(active=False,status='completed-held-powerwash',sessionId=79352,exitCode=0,completion='9db1a6'),activeOwnedWorkers=0,
 extraAnnotationSampledReview='extra-annotation-pieces-sampled-direct-review-v2.json',next='Retain Portal V2. Run only prepared PowerWash V3 after fresh resources, then read all53 new encoded samples14boards and normal1x playback. No final ratio/mix/private/schedule approval.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samplesRead=84,boardsRead=22,shaChecks=len(checked),portalRetained=True,powerwashHeld=True,v3PreparedOnly=True)))
