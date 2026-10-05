"""Record direct targeted evidence and independent new commentary; preserve current13."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
EDIT = BASE / 'measured-edit-v2'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

execution = read(EDIT/'caption-and-tail-local-v3/execution.json')
assert execution['exitCode']==0 and len(execution['images'])==174 and len(execution['sheets'])==29
for x in execution['images']+execution['sheets']:
    assert sha(ROOT/x['path'])==x['sha256']
    x.update(directlyRead=True,finalApproved=False,gitStorage='local-only')
review = {
    'schemaVersion':1,'reviewedAt':now,'scope':'All174 targeted caption/crop/device/tail sample images and29 contact boards directly read. Sample evidence only; final whole motion, cues, joins and final mix remain unapproved.',
    'execution':str((EDIT/'caption-and-tail-local-v3/execution.json').relative_to(ROOT)).replace('\\','/'),
    'executionSha256':sha(EDIT/'caption-and-tail-local-v3/execution.json'),
    'actualClosedWorker':{'pid':18136,'sessionId':48544,'exitCode':0,'alive':False},
    'images':execution['images'],'boards':execution['sheets'],
    'findings':[
        {'subject':'cue139','observation':'Old285.176–301.416667 bridge no longer shows the next paragraph. At301.416667 ASS centisecond rounding shows the first caption one output frame later; source text and PCM are unchanged. Independent new-join/final timing still pending.','resolution':'Candidate bridge correction directly observed; do not claim every corrected/final cue approved.'},
        {'subject':'06p3/08p2/08p3 boundaries','observation':'Corrected target samples show wall preview under06p3, overhead objects under08p2, and resource-counter footage under08p3. No next-paragraph caption over inspected silence.','resolution':'Retain exact PCM clamps and verify final mix/frames later.'},
        {'subject':'08p3 resource28','crop':[0,252,1472,828],'observation':'Quarter-second motion samples and every affected cue anchor keep the left counter above the fixed caption and exclude the presenter. Read11000→9824→9800→10874→11000→10277→10200; intermediate interpolation values are not fixed cost rules. Sell prompt is distinct from actual removal/installation; blue ReadyUp ghost is not a fighting enemy.','resolution':'Adopt lower crop as candidate; all final caption motion remains pending.'},
        {'subject':'13p1 source49','crop':[192,270,1056,594],'observation':'Quarter-second motion/affected cue anchors enlarge distant approach and purple attacks. Far targets remain above the fixed caption; part of near body is covered. Aroundlocal105–240 aim is held while the distant route is visible; that observation is not automatic quota approval.','resolution':'Candidate zoom adopted; preserve target visibility and inspect final literal cues. Keep only relevant meaningful observation.'},
        {'subject':'02 rail10','observation':'Dark foreground still obscures the centre at local30/60fps=0.5s; local60 is clear. Earlier0.35s estimate rejected.','resolution':'Review exact native boundary between output30–60 and trim the obstructed lead; do not use the estimate as final.'},
        {'subject':'02 tails12/13','observation':'12 ends on stairs with no visible enemy;13 starts/ends behind a large pillar.13local60/120/180 show enemies beside wall devices and direct attacks.','resolution':'Trim unrelated staircase/pillar camera motion at exact native boundaries; guide the retained wall-side attack.'},
        {'subject':'06 selected previews','observation':'22 starts tilted green preview then selected HUD readsSpike Trap and blocked indication;15 remainsSpike/Invalid Location until near local220–230 when a tilted/spring preview appears.26 shows Not enough money and changes preview.','resolution':'Do not assign one HUD name to all previews or claim successful placement from a preview. The current general orientation wording remains separate from item attribution.'},
        {'subject':'06 retained tail','observation':'21 shows close direct shots beside floor/wall effects, then a distant aim.24 shows green barricade preview shifting and blocked locations;25 shows a tilted floor preview changing orientation followed by Spring/Invalid Location.','resolution':'New independent commentary guides direct combat then explicitly separate preparation; final word-to-shot alignment pending.'},
        {'subject':'13 retained tail','observation':'57 begins with an upward Minecart camera glimpse; combat is visible later.58 shows a close purple attack;59 shows fire beyond floor devices.','resolution':'Remove unrelated upward glance unless an exact visible action supports it. Describe separate close/far excerpts without continuous-play causality.'},
        {'subject':'12 conclusion tail','observation':'46 shows a blue preparation preview switching floor forms, with ReadyUp;40 shows a separate high viewpoint firing along the enemy route and floor effects throughout7.5s.','resolution':'Guide preparation separately, relocate unique40 before original concluding paragraphs, and end on the preserved conclusion. Do not claim a preparation guarantees victory.'}
    ],
    'allTargetSamplesDirectlyRead':True,'allFinalPixelsReviewed':False,'allFinalTimingApproved':False,
    'newJoinAsrApproved':False,'newGitImages':0,'captionPositionChanged':False,'currentPcmChanged':False
}
save(EDIT/'caption-and-tail-direct-review-v3.json',review)

entries = [
    ('02-g1','02',4,'벽 장치 옆으로 적이 다가오면, 플레이어는 그쪽으로 몸을 돌려 직접 공격합니다.','When enemies approach beside the wall devices, the player turns toward them and attacks directly.',[12,13],'Trim staircase/pillar ends; retained wall-side approach and direct attack.'),
    ('06-g1','06',4,'가까운 적을 겨누며 물러나는 모습과, 길 위 장치의 효과를 함께 보세요.','Watch the player aim at nearby enemies and move back, alongside effects from devices on the route.',[20,21],'Direct combat; no claimed damage or winning placement.'),
    ('06-g2','06',4,'뒤의 준비 장면에서는 초록색 미리보기를 돌리고 자리를 바꿉니다. 금지 표시가 뜬 순간은 설치가 끝난 모습과 구별합니다.','In the following preparation excerpts, the green preview is rotated and moved. Distinguish a blocked-placement indication from a completed installation.',[24,25],'Separate preparation footage, shifting/rotating preview and blocked indication.'),
    ('13-g1','13',1,'적이 장치 너머로 다가오자, 겨누는 방향도 그 움직임을 따라 바뀝니다.','As enemies approach beyond the devices, the direction of aim changes with their movement.',[50],'Within this retained excerpt only; no relation to a different source time or sequel feature.'),
    ('13-g2','13',2,'먼 길을 겨누는 컷과 가까운 적을 상대하는 컷은 별도 구간입니다. 거리마다 어디를 보고 공격하는지 살펴보세요.','The shots of aiming down the distant route and confronting nearby enemies are separate intervals. Notice where the player looks and attacks at each distance.',[52,56,57],'Remove the unrelated upward camera lead of57; do not imply one continuous encounter.'),
    ('13-g3','13',2,'가까운 적을 향한 보라색 공격 뒤에는, 장치 너머로 발사하는 다른 장면이 이어집니다.','After a purple attack on a nearby enemy, another excerpt shows shots beyond the devices.',[58,59],'Editorial order of separate intervals; not attack-result causality.'),
    ('12-g1','12',2,'여기서는 장치를 고르고 미리보기의 방향을 바꿉니다.','Here, the player selects a device and changes the preview orientation.',[45,46],'ReadyUp preparation; preview not an enemy or guaranteed installed result.'),
    ('12-g2','12',2,'별도 전투에서는 높은 자리에서 적이 오는 길을 겨눕니다. 준비와 전투의 판단을 나누어 보세요.','A separate combat excerpt shows aiming down the enemy route from a high position. Distinguish the decisions during preparation from those during combat.',[40],'Move this unique combat before original12p3/4 conclusion, never repeat the interval.')
]
guides=[]
for id,sid,p,ko,en,bank_ids,connection in entries:
    guides.append({'id':id,'parentScene':sid,'afterOriginalParagraph':p,'ko':ko,'en':en,'text':ko,
                   'path':f'shared/output/narration/making-game-sequels/guided-observation-v3/{id}.wav',
                   'classification':'actual-existing-game','bankCutIds':bank_ids,'visibleActionAndConnection':connection,
                   'sourceEvidence':str((EDIT/'caption-and-tail-direct-review-v3.json').relative_to(ROOT)).replace('\\','/'),
                   'measuredSeconds':None,'finalWordActionAlignment':False})
index = read(BASE/'narration-expanded13-index.json')
protected_paths = [ROOT/x['path'] for x in index['measurements']]
protected_paths += [ROOT/'projects/making-game-sequels/script/narration.ko.json',ROOT/'projects/making-game-sequels/script/narration.en.json',ROOT/'projects/making-game-sequels/planning/outline.md',ROOT/'projects/making-game-sequels/project.json',BASE/'narration-expanded13-index.json',ROOT/'shared/voice-reference/reference-15-35s.wav',ROOT/'shared/voice-reference/reference-15-35s.ko.txt']
request = {'schemaVersion':1,'reviewedAt':now,'guides':guides,'pairedWholeTextReview':True,'overviewPromiseReview':True,
           'allPriorScenePcmPreserved':True,'device':'cpu','cpuThreads':2,'gpuJobs':0,
           'protectedInputs':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in protected_paths],
           'baselineScenes':13,'baselineParagraphs':52,'baselinePcmSeconds':509.624,
           'currentCanonicalScriptsUnchangedUntilMeasuredAdoption':True,'originalSixExplanationMinimumSeconds':219.68,
           'originalSixCurrentExplanationSeconds':222.446,'overviewSeconds':24.14,
           'sameApprovedModelAndReference':True,'NimbusUnchanged':True,'finalTimingApproved':False,
           'newGuidesTechnicalAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending',
           'newGitImages':0,'sourceAudioStreams':0,'selfCreatedGames':0,'loops':0,'slowdown':0}
assert len(guides)==8
save(BASE/'guided-observation-tts-request-v3.json',request)
save(ROOT/'projects/making-game-sequels/planning/guided-observation-v3.json',request)
queue = read(PROOF.parent/'queue.json');item=next(x for x in queue['items'] if x['slug']=='making-game-sequels')
item.setdefault('executionHistory',[]).append(item.get('execution',{}))
item.update(stage='current13-targeted-review-complete-new-guidance-pre-TTS',updatedAt=now,
            guidedObservation={'request':'projects/making-game-sequels/production/guided-observation-tts-request-v3.json','guides':8,'measured':False,'technicalAsrApproved':False},
            nextAction='Measure only8 independent new observation guides using approved Qwen/reference on CPU; preserve all current13 PCM. Then align words/native cuts, trim rail/pillar/upward camera ends, keep the conclusion last, and review exact60:40/mix/captions/joins/final pixels before rendering/private delivery.')
item['execution'].update(observedAt=now,status='targeted-worker-closed-new-guidance-pre-TTS',phase=item['stage'],pid=None,sessionId=None,alive=False,activeTasks=[],cpuProductionJobs=0,primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,commandLine=None)
queue.update(updatedAt=now,lastProgressAt=now);save(PROOF.parent/'queue.json',queue)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','guidedObservation','nextAction','execution']:d[k]=item[k]
    d['targetedCaptionAndTailReview']=str((EDIT/'caption-and-tail-direct-review-v3.json').relative_to(ROOT)).replace('\\','/')
    save(p,d)
print(json.dumps({'directlyReadImages':174,'boards':29,'newGuideParagraphs':8,'basePcmPreserved':509.624,'finalApproved':False,'newGitImages':0}))
