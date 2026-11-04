from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parent
ROOT=P.parents[4]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,o): (P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
core=read(P/'selected-footage.json')
extra=read(P/'additional-fighters-inventory.json')
script_path=ROOT/'projects/animation-assigning/script/grid-v1/narration.ko.json'
script=read(script_path)
# Human-inspected before/after candidate pairs. Impact flashes are deliberately
# excluded; not every scene-detector hit is a native edit.
cut_times={
 'vf':[10.5,11.8,14.45,18.116667,33.016667,40.766667,44.766667,49.166667,49.866667,50.183333,51.883333,56.866667],
 'inkling':[1.818483,4.487817,6.339667,6.673333,8.742067,9.876533,11.144467,13.546867,14.597917,15.432083],
 'samus':[1.818483,3.520183,4.904900,6.006,8.341667,12.629283,16.149467],
 'mario':[1.818483,3.853850,6.006,7.691017,10.527183,13.263250,13.763750,16.833483],
 'piranha':[1.818483,6.623283,12.012,14.447767,17.834483,22.2222],
 'goose-retail':[11.034,13.4,15.867,18.267,20.4,23.367,25.133,30.6,32.167,33.933,36.567,38.867,40.634,43.267,46.5,53.667],
 'goose-prealpha':[25.366667,29.066667,69.866667,79.4,90.933333,97.566667,102.933333,114.8,132.033333,138.1,158.466667,161,163.5,164.1,170.6,188.866667,193.766667],
 'donkey-kong':[1.818483,4.738067,6.790117,8.875533,12.095417,13.296617,14.864850],
 'kirby':[1.818483,4.387717,6.139467,8.324983,10.627283,13.830483,14.3143],
 'luigi':[1.818483,4.771433,5.45545,6.923583,8.1081,10.994317,12.429083,15.5155,17.450767],
 'wii-fit':[1.818483,3.720383,5.739067,6.239567,6.873533,9.4094,12.328983,15.9159],
 'mii':[1.818483,3.269933,5.005,6.139467,9.042367,13.16315,14.76475,16.633283],
 'krool':[1.818483,5.121783,8.141467,10.977633,14.531183,15.6156,16.76675,17.8178,19.16915,21.237883]
}
cut_info={'schemaVersion':1,'reviewMethod':'Candidate boundaries from FFmpeg scene .20, then chronological 2/4fps contacts plus every cut-pairs sheet at -/+0.1 seconds. Impact flashes excluded. This is not a claim that every possible edit has been found.',
 'timesSeconds':cut_times,'precision':{'detectedTimes':'source PTS, nearest selected detector frame; final annotation reset may conservatively use +/- one frame','manualBrackets':{'goose-prealpha':[{'time':138.1,'uncertaintySeconds':0.1},{'time':161,'uncertaintySeconds':0.25},{'time':163.5,'uncertaintySeconds':0.25}]},'sameStageEdits':'Some same-stage jump edits can evade scene threshold; final selected-cut playback still required.'},
 'criticalCorrection':{'samus':'3.520183–4.904900 is the first upward throw. At 4.904900 a different grab shot starts; never describe 3.75–5.8 as one continuous throw.'},
 'annotationPolicy':'Reset at native edits and abrupt camera changes. For manually bracketed cuts, hide before uncertainty interval and resume only after re-anchoring.'}
save('native-cuts-reviewed.json',cut_info)
def split(k,a,b):
 ts=[a]+[t for t in cut_times[k] if a<t<b]+[b]
 return [{'start':round(x,6),'end':round(y,6),'seconds':round(y-x,6),'resetAnnotationsAtStart':True} for x,y in zip(ts,ts[1:])]
def win(k,a,b,role,before,action,result,paras,notes=''):
 return {'sourceKey':k,'start':a,'end':b,'seconds':round(b-a,3),'role':role,'before':before,'action':action,'result':result,'paragraphCandidates':paras,'nativeShots':split(k,a,b),'notes':notes}
rows=[
 win('donkey-kong',2,4.65,'weight-and-ready-pose','Arrival crouch','Raises body and winds arm through a broad pose','Fists/face settle toward ready stance',['01.2','04.1','07.1']),
 win('donkey-kong',6.85,8.8,'arm-body-follow-through','Mario close to grounded DK','DK rises through broad arm motion','Mario launched; DK returns to ground',['02.1','04.1','06.1']),
 win('donkey-kong',9,12.0,'wind-up-response','Peach and DK face each other','DK winds punch; Peach responds','They separate into next stance',['02.3','07.1']),
 win('donkey-kong',12.1,13.1,'two-body-carry','Peach close to DK','Peach goes over DK shoulder','DK carries her out of shared position',['04.2'],'Alternative following Samus, not a replacement for the named Samus sentence.'),
 win('kirby',2,4.3,'character-greeting','Kirby arrives from star','Raises arms and waves/bounces','Expressive standing pose',['04.4']),
 win('kirby',8.4,10.5,'hammer-wind-up-release','Kirby raises hammer near Dedede','Body turns through hammer strike','Dedede launches; Kirby follows through',['04.3','07.1']),
 win('kirby',10.7,13.7,'nonhuman-transform-and-return','Kirby airborne over Link','Changes into heavy object, drops, returns and inhales','Body shape and prop/head features change',['06.1'],'Optional alternative; avoid introducing new transformation lecture.'),
 win('luigi',2.5,4.7,'expressive-recovery-shrug','Luigi enters from door','Tumbles/turns then opens arms','Characterful shrug-like pose',['01.2','04.4']),
 win('luigi',4.85,8.0,'attack-chain-and-recovery','Luigi and Diddy close','Punches then air/ground attack in separately edited shots','Diddy recoils; Luigi returns to stance',['02.1','06.1']),
 win('luigi',8.2,10.9,'head-first-body-extension','Luigi stands and charges','Launches head first','Body meets wall with limbs extended',['04.1','07.1'],'Do not infer invincibility/hitbox or describe as real-world physics.'),
 win('luigi',12.5,15.4,'small-leg-motion-consequence','Mario hangs below Luigi at ledge','Luigi looks down and makes small downward foot motion','Mario falls; Luigi resets',['04.4','07.1'],'Not a numeric hitbox measurement.'),
 win('luigi',17.5,19.9,'landing-to-personality-pose','Luigi tumbles after upward attack','Body/feet recover; small hand/body gesture','Returns toward characterful ready pose',['01.2','06.1','07.1']),
 win('wii-fit',2,3.65,'precise-arm-shoulder-pose','Trainer upright','Moves shoulder/arm into stretch','Clear arm-at-shoulder-height pose',['03.1','04.4']),
 win('wii-fit',3.8,6.8,'whole-body-attack-poses','Trainer close to Little Mac','Leg/arm extensions and deep forward bend in separate native shots','Opponent rises/recoils while trainer recovers',['04.1','06.1'],'Not a verified grab/throw; earlier candidate search hypothesis rejected.'),
 win('wii-fit',7,9.3,'idle-versus-full-body-action','Trainer upright','Hula-hoop rising action then another standing pose','Arms/body return toward upright',['02.1','04.4']),
 win('wii-fit',9.5,12.2,'prop-head-contact-and-body-bend','Ball above female trainer','Heads the ball, then cut to male trainer side bend','Ball leaves head; extended body pose visible',['03.1','04.1'],'Contains same-stage internal edit around gender/body change; final split refinement needed before annotation. Do not animate one continuous tracker through it.'),
 win('wii-fit',12.5,15.5,'foot-torso-opposition','Male trainer near Villager','Moves through deep bend and leg/arm extension','Villager launched; trainer re-centers',['04.1','06.1']),
 win('wii-fit',16.1,18.7,'stance-breath-turn','Female trainer faces Meta Knight','Raises knee/arms, settles, turns into next action','Another extended stance appears',['02.3','07.1']),
 win('mii',2,3.2,'different-weapons-different-ready-poses','Three Mii fighters together','Sword, cannon and bare-hand ready gestures','Different arm and body arrangements',['02.1','04.4']),
 win('mii',3.35,6.0,'punch-foot-torso-connection','Brawler faces opponent','Punch and rising attack in edited shots','Follows through and lands',['04.1','06.1']),
 win('mii',6.2,9.0,'sword-path-body-path','Swordfighter and Ike close','Down/side/upward sword motion with body turns','Opponent reacts; weapon follows recovery',['04.3','07.1']),
 win('mii',9.1,13.1,'arm-cannon-aim-recoil','Gunner faces Zero Suit Samus','Aims/fires and recovers across same-stage angles','Opponent launches while cannon/body reset',['02.1','04.3']),
 win('mii',13.2,14.7,'weapon-contact-recovery','Swordfighter close to Ice Climbers','Sword sweeps through shared space','Opponent launches; body follows sword',['04.3','06.1']),
 win('mii',14.8,16.6,'leg-body-follow-through','Brawler faces opponent','Turns through rising kick/flip','Opponent launched; Mii lands',['06.1','07.1']),
 win('krool',2,5.05,'body-shape-personality','K. Rool stands on ship','Belly/arm/head gestures and broad open-mouth lean','Settles into expressive ready stance',['01.2','04.4']),
 win('krool',5.2,8.05,'prop-and-body-position','K. Rool holds blunderbuss','Cannonball fire and inhale/launch action','Opponent/cannonball leaves barrel while body recovers',['04.3'],'No real gun mechanism or exact named-input claim needed.'),
 win('krool',8.2,10.9,'belly-attack-and-recovery','K. Rool leans forward near Link','Extends belly/body then rises using propeller','Returns to upright elevated pose',['06.1','07.1']),
 win('krool',11.1,14.4,'detached-prop-path','Crown on head facing Diddy','Throws crown and changes body position','Crown travels independently and returns',['04.3'],'Only visible body/prop relation; no claim about internal rig/attachment implementation.')
]
sources={}
for k,s in extra.items():
 sources[k]={**s,'game':'Super Smash Bros. Ultimate','genre':'platform fighting','sourceClassification':'independent-gameplay-promotional-capture','sourceOfficialIndex':'https://www.smashbros.com/assets_v2/data/fighter_movie_en.json','rights':core['sources']['samus']['rights'],'visualReview':'Pages extra-{key}-01/02 reviewed chronologically at 2fps; native cut-pairs sheets reviewed at +/-0.1 sec. Full continuous decode passed. Not realtime human playback/audio review.','audio':{'sourceTrackPreserved':True,'musicIdentity':None,'audioListened':False,'finalMixDecision':'Parent pending; Nintendo policy does not identify or separately clear soundtrack recording.'},'windows':[r for r in rows if r['sourceKey']==k]}
save('additional-selected-footage.json',{'schemaVersion':1,'status':'reviewed-candidate-pool-not-final-timeline','sources':sources,'additionalCandidateSeconds':round(sum(r['seconds'] for r in rows),3),'selectionAdvice':'Prefer the smallest useful fighter subset. Do not use every fighter or insert name/exposition solely to consume footage. All variants remain one primary game. Treat montage shots as separate observations; use continuous VF/grid demo for longer analysis.','unresolved':'Some same-background edits are only bracketed by 2fps visual inspection. Final used intervals need source-cut/overlay check.','excluded':'Titles, brand/end cards, Kirby Pokemon absorption, DK Pikachu segment, Luigi Ryu segment, K. Rool final-smash movie are not adopted.'})

def ref(k,a,b,claim,anchor,priority='primary'):
 return {'sourceKey':k,'sourceStart':a,'sourceEnd':b,'seconds':round(b-a,3),'anchor':anchor,'supports':claim,'priority':priority,'nativeShots':split(k,a,b),'useAtSourceSpeed':True}
mapping={
'01.1':[
 ref('vf',24,28,'Kick duck and counter: opening exact thesis proof','높은 발차기를 피하려고 몸을 낮추고'),
 ref('vf',18.32,24,'Direction/feet/distance across attacks and reaction','몸의 방향, 발의 위치, 상대와의 거리가 함께 들어 있습니다.'),
 ref('vf',28,32.9,'Recovery connects to next attack while overview sets process','완성된 움직임을 함께 고쳐 가는 과정')],
'01.2':[
 ref('wii-fit',2,3.65,'A recognizable instantaneous arm/shoulder pose','캐릭터의 한 순간 자세를 포즈라고 합니다.'),
 ref('krool',2,5.05,'Body posture conveys different personality','어떤 느낌으로 보여야 하는지도'),
 ref('luigi',2.5,4.7,'Expressive recovery has a recognizable character feeling','어떤 느낌으로 보여야 하는지도','alternate')],
'02.1':[
 ref('mii',2,3.2,'Ready pose differs with required action/weapon','동작 목록이 필요합니다.'),
 ref('luigi',4.85,8,'Several attack actions, each one separate row','가만히 서 있기, 걷기, 공격하기처럼'),
 ref('mii',9.1,13.1,'Body/arm aim and recovery, no invisible hit-window claim','어느 쪽으로 몸과 손을 움직이는지')],
'02.2':[],
'02.3':[
 ref('donkey-kong',9,12,'Opponent response around wind-up','상대가 보고 대응할 여유'),
 ref('goose-prealpha',171,174.5,'Action settles toward idle','반면 대기나 걷기는'),
 ref('goose-prealpha',7.5,11.5,'Continuous shore walking, naturally repeated steps','반복 재생, 루프가 필요합니다.'),
 ref('goose-prealpha',164.5,170.55,'Natural repeated prop-transfer activity, not video loop','한 번 실행할 동작인지','alternate')],
'03.1':[
 ref('wii-fit',9.5,12.2,'Arm/torso shapes compared, separate female/male native shot','어깨 높이, 팔꿈치 방향, 허리를 기울이는 정도','alternate')],
'03.2':[],
'04.1':[
 ref('donkey-kong',2,4.65,'Broad arm pose and stance','주먹을 뻗는 자세라면'),
 ref('mii',3.35,6,'Feet/torso support the arm attack','어느 발에 체중을 싣고, 몸통을 어느 쪽으로 돌리며'),
 ref('wii-fit',3.8,6.8,'Whole-body poses into recovery, no fabricated skeleton','다음 자세로 어떻게 돌아오는지'),
 ref('wii-fit',12.5,15.5,'Ready/action/recovery across whole-body extension','앞뒤 동작을 비교하면')],
'04.2':[
 ref('samus',3.520183,4.9049,'Exact named Samus holds/lifts/upward throw, first shot only','사무스가 상대를 붙잡아 들어 올리고 위로 던지는 모습을 보세요.'),
 ref('samus',4.9049,5.95,'Second distinct grab/throw view for contact condition; reset overlay','잡는 쪽의 손과 잡히는 쪽의 몸이 함께 움직여야 합니다.'),
 ref('donkey-kong',12.1,13.1,'Optional same-game carry/contact variant','상대를 포함한 모습','alternate')],
'04.3':[
 ref('inkling',2,4.4,'Named Inkling and ink weapon/body orientation','같은 게임의 잉클링은 잉크를 사용하는 캐릭터입니다.'),
 ref('inkling',4.487817,6.2,'Aim and body reaction','몸이 향하는 쪽과 무기가 지나가는 쪽'),
 ref('inkling',11.35,12.15,'Ink weapon overhead-down/forward path','공격 방향과 무기의 궤적'),
 ref('mii',6.2,9,'Weapon extends beyond body/arm motion','무기의 크기와 지나갈 공간','alternate'),
 ref('krool',11.1,14.4,'Detached prop trajectory versus body','공격 방향과 무기의 궤적','alternate')],
'04.4':[
 ref('vf',40,44.7,'High/low body placement and opponent avoidance','회피는 무엇을 피하고 어느 쪽으로 몸을 빼는지'),
 ref('inkling',9.9,11.14,'Lineup body-language differences','대기 자세는 가만히 있어도 어떤 성격이 드러나는지'),
 ref('mario',2,3.8,'Greeting cap/hand/body gesture','인사나 기뻐하는 몸짓'),
 ref('kirby',2,4.3,'Greeting wave/bounce','인사나 기뻐하는 몸짓','alternate'),
 ref('mario',16.85,18.15,'Thumbs-up expression','그 움직임을 알아보게 만드는 조건'),
 ref('luigi',12.5,15.4,'Small leg gesture has clear visible consequence','동작의 종류가 바뀌면','alternate')],
'05.1':[],
'05.2':[
 ref('goose-retail',3.5,11,'Goose moves and gardener reacts; game introduction','언타이틀드 구스 게임은 거위를 움직여'),
 ref('goose-prealpha',44,48,'Beak lowers, grips radio handle, lifts and carries','목을 낮춰 부리로 집고'),
 ref('goose-prealpha',11.5,19.5,'Bench sandwich grasp→turn/carry→release, one continuous action','목과 몸의 위치를 바꾸며 운반합니다.'),
 ref('goose-prealpha',39,43.8,'Beak grips sack; body pulls it','부리를 어디로 옮기고 언제 물건을 붙잡는지'),
 ref('goose-prealpha',117,120.9,'Beak-held cap maintains object relation during path turn','그 몸이 할 일을 정확히 보여 주는 데','alternate')],
'06.1':[
 ref('vf',34,40,'Reaction/fall/get-up/next movement','그 자세로 들어가고 빠져나오는 과정'),
 ref('luigi',17.5,19.9,'Landing/recovery/expressive stance','몸의 중심을 옮기고, 발을 디디고'),
 ref('mii',13.2,14.7,'Weapon follow-through into body recovery','다음 동작으로 연결하는 판단'),
 ref('mii',14.8,16.6,'Air-to-ground action connection','실제 움직임을 만드는 과정')],
'06.2':[],
'07.1':[
 ref('vf',44.8,46,'Readable finished action at source speed','실제 속도로 움직일 때 행동이 잘 읽히는지'),
 ref('luigi',8.2,10.9,'Head-first action remains characterful through wall-contact result','캐릭터다운 인상이 남는지'),
 ref('wii-fit',16.1,18.7,'Visible pose-to-action reading','조작과 맞물렸을 때 기분 좋은지'),
 ref('goose-prealpha',79.5,89.9,'Wing/idle/key grab/opponent response natural sequence','움직이는 결과는 그 목표를 다시 점검하게 합니다.','alternate')],
'07.2':[]}
guides={
'01.1':'Keep VF opening at source speed. Overview can remain on visible fighting recovery; do not repeat same four seconds to fill the whole paragraph.',
'01.2':'Both contrasting walks need our Unity pair. Actual characters only support pose/personality, not the exact upright/head-down walking comparison.',
'02.1':'Our list can be drawn over actual examples; numeric duration/active frames are not known for these sources.',
'02.2':'Entire numeric 60fps / 12frame / .2sec example must be our Unity implementation or diagram. Never label source game actual hitboxes.',
'02.3':'Use real response/steps where clearly visible; use Unity same-cycle start/end to explicitly prove seamless loop. Recorded repeated pickup is activity repetition, not direct proof of an internal animation clip loop.',
'03.1':'Unity pose variations are exact evidence for shoulder/elbow/waist alternatives. Optional Wii Fit is contextual comparison, not actual studio instruction material.',
'03.2':'Unity-only capture-to-silhouette-to-document demonstration is explicitly narrated. No unrelated actual game filling.',
'04.1':'Our reference pose should be a separately labeled educational pose. Do not pretend it is the original developer brief; freeze/screenshot halves count as explanation, not actual seconds.',
'04.2':'Samus precise named action only lasts ~1.38sec. Use native-speed action once then our two-body contact demo for longer explanation. A labeled static annotated Samus still is explanation. Do not pad via slow motion/repeat.',
'04.3':'Inkling total useful named span ~5sec; use our weapon path for geometric detail. Alternate fighter inserts only after Inkling wording is finished, without unannounced substitute.',
'04.4':'Prefer 3 clearly different animation roles over an every-character montage. VF avoidance, Inkling ready pose, Mario greeting suffice; others are alternatives.',
'05.1':'Narration explicitly says our same-gesture two-character demonstration. Use own RGPoly comparison. Actual game gesture history is not established.',
'05.2':'Native Goose background retained; lower/raise neck radio sequence strongest. 2017 prealpha footage must be identified as development-public footage; do not call current release footage. Hide beak annotation during planter occlusion. Do not fill entire paragraph with unrelated gardening.',
'06.1':'Actual completed movement shows entrance/recovery. This demonstrates observable animation; it cannot prove the historical animator decision process.',
'06.2':'Our intentionally varied rig/shoulder/prop intersection illustration only. Do not imply actual commercial source contains deformation bugs.',
'07.1':'Evaluate visible source-native actions; unknown control feel cannot be inferred from prerecorded video. Our controllable testbed supplies that part. Revision/drop discussion should remain on our labeled review board.',
'07.2':'Our document/change sharing scene closes the workflow. No actual studio-document or developer attribution invented.'}
out=[]
for scene in script['scenes']:
 for i,line in enumerate(scene['lines'],1):
  pid=f"{scene['id']}.{i}";rs=mapping[pid]
  for r in rs:assert r['anchor'] in line,(pid,r['anchor'])
  out.append({'paragraphId':pid,'narration':line,'referenceSections':scene['referenceSections'],'candidates':rs,'teachingAndClassification':guides[pid],'primarySourceSeconds':round(sum(r['seconds'] for r in rs if r['priority']=='primary'),3),'timelineStatus':'await actual ASR paragraph boundaries; source duration is not narration duration'})
save('paragraph-footage-map.json',{'schemaVersion':1,'episode':'A01','scriptPath':str(script_path).replace('\\','/'),'scriptSha256':hashlib.sha256(script_path.read_bytes()).hexdigest(),'bodyVoiceSecondsFromParent':402.756,'status':'source-matched-editorial-candidates-not-locked-timeline','paragraphs':out,'constraint':'This mapping prioritizes exact visible claims, retains original sequence, and does NOT force all 187.6 core seconds plus all extra seconds into narration. Whole-source footage totals cannot establish a truthful 60% body ratio.','ratioRisk':'Named Samus/Inkling actions are short and five paragraphs explicitly require authored diagrams/workflow. Final ratio must be computed from the timeline; do not fill these paragraphs with unrelated gameplay.'})
save('core-windows-native-shots.json',{'schemaVersion':1,'sources':{k:[{**w,'nativeShots':split(k,w['start'],w['end'])} for w in s['windows']] for k,s in core['sources'].items()},'criticalCorrections':cut_info['criticalCorrection'],'originalCoreFilePreserved':True})
print('extra seconds',sum(r['seconds'] for r in rows),'paragraphs',len(out),'primary mapped seconds',sum(x['primarySourceSeconds'] for x in out))
