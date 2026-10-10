"""Seal directly read scripts/boards; retain historical renders and other owners."""
exec((__import__('pathlib').Path(__file__).with_name('prepare-polar-source-review-v1.py')).read_text(encoding='utf-8').split('OUT.mkdir')[0])
ko=json.loads((BASE/'script/narration.ko.json').read_text(encoding='utf-8-sig'))
en=json.loads((BASE/'script/narration.en.json').read_text(encoding='utf-8-sig'))
timeline=json.loads((BASE/'production/timeline.json').read_text(encoding='utf-8-sig'))
snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8-sig'))
assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
v1=json.loads((OUT/'source-pilot-extraction-v1.json').read_text(encoding='utf-8-sig'))
v2=json.loads((OUT/'source-pilot-extraction-v2.json').read_text(encoding='utf-8-sig'))
v3=json.loads((OUT/'action-clarity-execution-v3.json').read_text(encoding='utf-8-sig'));assert v3['exitCode']==0
v4=json.loads((OUT/'unused-native-execution-v4.json').read_text(encoding='utf-8-sig'));assert v4['exitCode']==0
samples=v1['records']+v2['records']+[r for j in v3['jobs'] for r in j['records']]
boards=list(LOCAL.glob('pilot-source-board-*.png'))+list(LOCAL.glob('later-source-board-*.png'))+[ROOT/r['path'] for j in v3['jobs'] for r in j['boards']]
assert len(samples)==132 and len(boards)==26
for r in samples+v4['records']:assert sha(ROOT/r['path'])==r['sha256']
issues={
 '02':'First12s: ground riding gives weak height example. Converted f2086 shows a crash/respawn state. Second cut under the landing-before/after cue instead shows ground riding. Re-select these, retain all seven narration paragraphs.',
 '05':'Visible ramp approach, air and landing at samples4/8s; later wooden ramp and rock gap. Clearer height example, but do not infer world height from screen y or terrain clearance.',
 '08':'Air rotations distinguish travel from bike attitude; native movement and world-up versus screen tilt need labelled tracked highlights. Team-unlock overlay near32s can distract; inspect/remove where appropriate.',
 '11':'Sunset riding supports target/viewpoint distinction. Wooden obstacle occludes part of the first interval. Daylight cut is a separate action; do not claim one continuous run or exact camera coordinates.',
 '14':'Steep ramps, backflip, landing and turning visible. Separate camera-control policy from canonicalization; no exact pole/gimbal-lock state can be proven from this footage.',
 '16':'Target ahead of following viewpoint, repeated jumps, daylight second cut. Draw opposite placement/look vectors as explicitly illustrative relationships, never measured hidden camera positions.',
 '18':'Rider position, bank/air rotation and trailing viewpoint are distinguishable. Keep final separate test-direction explanation; annotate movement and attitude separately.'}
record={'reviewedAt':datetime.now(timezone.utc).isoformat(),'baselineId':'ZLOewk8JHXA','fullKoEnScriptScenesRead':19,'completeCurrentUnmixedReadbacksRead':19,'unmixedAsrIsFinalMixedApproval':False,'opening':{'paragraphs':4,'voiceSeconds':25.2,'slotFrames':1549,'passesQuestionOutcomeOrderedExamplesAndFirstConnection':True,'retainApprovedPcm':True,'chapter00_02To01_24IsNot82SecondsOfOverview':True},'sourceComparison':{'samplesDirectlyRead':132,'boardsDirectlyRead':26,'samplingOnly':True,'allContinuousPixelsApproved':False,'issues':issues,'boards':[{'path':rel(p),'sha256':sha(p),'directlyRead':True} for p in boards]},'unusedCandidateComparison':{'evidence':rel(OUT/'unused-native-execution-v4.json'),'samplesDirectlyRead':71,'boardsDirectlyRead':12,'absoluteNativePtsVerified':True,'observations':['318–322 ground riding;323 onward results/menu/loading, exclude those.','375–383 riding into ramp;384–385 air,386–387 crash/respawn, exclude crash.','388–398 reapproach and ramp;399 air. Later adjacent outcome not yet reviewed.','583–594 sunset ramp, air/rotation, landing and forward travel;595 onward result/menu/loading. Treat boundaries as sampled candidates, not exact adopted in/out.','600–609 menus/start prompt, exclude.610–612 short ground riding setup.'],'footageAdopted':False},'originalFilesUnchanged':True,'newNarrationGenerated':False,'newOverlayMotionApproved':False,'finalMixedAsrApproved':False,'finalQaApproved':False,'replacementVideoId':None,'humanListeningApproved':False,'publicRightsApproved':False}
write(OUT/'whole-content-and-source-direct-review-v1.json',record)
chain=[
 ('01','2D addresses lack height','Introduce cylinder, sphere and camera; state scope and boundary checks'),
 ('02','Observe track position/air height/following view','Separate target and view point before formulas; improve mismatched landing footage'),
 ('03','Need a third component','Build horizontal polar address plus z height; distinguish horizontal from total distance'),
 ('04','How to calculate the address','Reuse part1 trig and apply5,0,3; recover horizontal radius/angle'),
 ('05','Do formulas describe visible jumps','Relate horizontal projection to height and distinguish terrain clearance from world height'),
 ('06','Want total distance with two direction angles','Construct sphere from z-up mathematical convention; explain zenith, latitude and altitude'),
 ('07','How do game direction names correspond','Explicit switch to x-right/y-up/z-forward and positive-pitch-down; separate roll'),
 ('08','Can a direction explain every bike rotation','Observe attitude, travel and camera projection as separate quantities'),
 ('09','Need a usable game-convention conversion','Split into horizontal/vertical components, then heading; checkforward/right signs'),
 ('10','Recover distance and angles from coordinates','Usehypot/atan2; treatorigin/pole without claiming camera policy'),
 ('11','How to connect relative camera geometry','Observe target/viewpoint; subtract target position before inverse conversion'),
 ('12','Why different angle values can describe one point','Show aliases and verify via Cartesian coordinates'),
 ('13','Need one stored representative','Choose canonical ranges; distinguish pole singularity, attitude gimbal lock and camera policy'),
 ('14','Do storage conventions make motion smooth','Observe ramps; motivate separate smoothing and pitch policies without inferring engine internals'),
 ('15','Construct camera placement explicitly','Useonecenter(0,1,0) example; reverse subtraction for look vector'),
 ('16','What opposite vectors mean in action','Track the rider and distinguish placement/look relationships, update center and check occlusion'),
 ('17','What survives implementation','AddCartesian vectors; handle arcsine input/rounding/axis units'),
 ('18','What these coordinates can and cannot control','Separate position, attitude, collisions and camera behavior'),
 ('19','How to validate the learned convention','Checkthree radius2 directions, origin/pole policy; return to viewer question')]
write(OUT/'causal-flow-and-primary-reference-review-v1.json',{'reviewedAt':datetime.now(timezone.utc).isoformat(),'koSha256':sha(BASE/'script/narration.ko.json'),'enSha256':sha(BASE/'script/narration.en.json'),'chapterChain':[{'scene':i,'incomingQuestion':q,'reasonAndResult':r} for i,q,r in chain],'primaryReference':{'url':'https://gamemath.com/book/polarspace.html','observedSections':['7.3 cylinders and spheres','heading/pitch game convention','aliases/canonical ranges','polar/Cartesian conversions','vector conversion'],'sequenceCompared':True,'difference':'Independent game observation cuts and robust atan2 inverse examples connect the source concepts to a following viewpoint. Mathematical scenes explicitly declare z-up; game-convention scenes switch to y-up. No claim that all engines share the book convention.','notionFreshFullRead':False,'correspondingSakuraiMathReferenceExists':False,'sakuraiFlowComparison':'General problem→observable example→explanation→result progression only; no invented corresponding math video or copied narration.'},'originalSceneOrderPreserved':True,'usefulOriginalPcmPreserved':True,'newPrerequisiteNarrationDecision':'Part2 explicitly reuses Part1 sin/cos, hypot/atan2 knowledge. Existingoverview and causal links retained; annotateaction to make existingspoken relationships visible. Do notclaim new finalcontinuousflow approval fromscriptaudit.','numericalChecks':{'sqrt34':34**.5,'orbitOffset':[3.75,2.5,2.1650635094610964],'orbitCamera':[3.75,3.5,2.1650635094610964]},'scriptCausalAuditPassed':True,'finalContinuousAudiovisualFlowPassed':False})
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=json.loads(qpath.read_text(encoding='utf-8-sig'))
q['execution']['completedJobs']=[{'sessionId':98658,'pid':72584,'state':rel(OUT/'action-clarity-execution-v3.json'),'actualOuterExitCode':0,'exitObservedChunk':'d4b476'},{'sessionId':64995,'pid':39132,'state':rel(OUT/'unused-native-execution-v4.json'),'actualOuterExitCode':0,'exitObservedChunk':'8efa86'}]
q['execution']['heavyJob']={'sessionId':27299,'pid':71804,'createTime':1791616074.6573913,'state':rel(OUT/'unused-native-execution-v5.json'),'cpuThreads':2,'gpuJobs':0,'runningExpected':True,'next':'read52newnativecandidate samples; choose exact clearer action without loops; editable narration-timed tracked overlays'}
q['execution']['stage']='polar-source-selection-and-tracked-overlay-planning'
item=next(i for i in q['items'] if i['slug']=='game-math-polar-3d');item['review'].update(causalFlowPassed=True,referenceFlowCompared=True,firstTimeGameplayCompared=True)
item['causalAuditEvidence']=rel(OUT/'causal-flow-and-primary-reference-review-v1.json');item['sourceAuditEvidence']=rel(OUT/'whole-content-and-source-direct-review-v1.json');item['reviewScopeNote']='Script/primary-reference and sampled candidate comparison only. Final moving overlays, currentmixedASR, allfinalpixels/QA/settings/Git/schedule remain false.'
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'scriptScenes':19,'currentActionSamples':132,'unusedNativeSamples':71,'baselineUnchanged':True,'overlaysFinalApproval':False,'queuedCurrentWorker':27299}),flush=True)
