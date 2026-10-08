"""Prepare explicit, disjoint native action cuts. This is not a pixel/ratio approval."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import json, hashlib, os, bisect, subprocess, time

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

# Each tuple is source key, local native start seconds, exact output frames,
# and the visible action corresponding to this particular paragraph.
# Durations are trimmed at normal speed. Nothing is looped or slowed down.
cuts={
 ('02',1):[('gauss','21.5',150,'Forward departure/path'),('gauss','87.5',237,'Dash, blue effect and target reaction; stop before yellow notice')],
 ('02',2):[('gauss','50',210,'Circular ground effect and nearby enemies'),('gauss129','287.5',185,'Caster ground spread and target relation')],
 ('09',1):[('gauss129','403.1',186,'Approach and fire at visible Thumper'),('gauss','26.2',216,'Moved position and enemy fall'),('gauss','82',150,'Dash and airborne enemy reaction'),('gauss129','342.2',103,'Near enemy and forward action')],
 ('09',2):[('gauss','39.5',420,'Cast, forward attack and jump'),('gauss','62.5',150,'Blue ground area'),('gauss129','284.5',98,'Ground origin at caster, before obscured transition')],
 ('09',3):[('dante','502',337,'Forward effect from near wall toward visible targets'),('dante','78',259,'Caster, direction and target; first part of the same native shot')],
 ('09',4):[('yareli155','145.1',315,'Moving ring and character/near-target relationship'),('dante','55.4',96,'Caster effect toward observed space'),('dante','95',286,'Forward projectile and target relation; stop before rejected boundary')],
 ('10',1):[('dante','41',468,'Arm/caster origin and circular effect'),('dante','49',233,'Caster action and near origin')],
 ('10',2):[('dante','100',540,'Forward effect and multiple target positions'),('dante','88',120,'Forward direction, caster and target')],
 ('10',3):[('dante','30',240,'Actual blue round effect near the caster'),('dante','92',120,'Blue round effect, not a world orb'),('dante','142',120,'Actual caster round effect'),('dante','151.8',122,'Actual round effect; before later separate interval')],
 ('10',4):[('dante','68',300,'Action origin then spatial target relation'),('dante','88+120/60',96,'Remaining forward action'),('dante','112',214,'Caster, affected space and targets')],
 ('03',1):[('jade','140',373,'Ground light, overhead target marks and reactions')],
 ('03',2):[('jade','48',190,'Ground origin and target relation'),('jade','172.2',168,'Aerial caster/target connection')],
 ('11',1):[('jade','51+10/60',116,'Remaining ground circle before HUD boundary'),('jade','72',228,'Arm motion, ground and target positions'),('jade','140+373/60',95,'Unused marked-target ground continuation')],
 ('11',2):[('jade','175',658,'Jade above the targets aiming downward; no below-to-above substitution')],
 ('04',1):[('gauss129','12',120,'Short actual forward path, relevant to this explicit movement clause'),('yareli','65',90,'Near-caster rotating area'),('yareli','69.5',80,'Near-target intersecting area')],
 ('04',2):[('yareli','61',180,'Moving ring and target'),('yareli','69.5+80/60',118,'Unused continuation of moving ring'),('yareli','48',117,'Rotating effect and nearby position')],
 ('12',1):[('jadeYareli','524',723,'Developer-controlled Yareli moving ring; this is Yareli, not Jade')],
 ('12',2):[('jadeYareli','524+723/60',207,'Unused passing/turning continuation'),('jadeYareli','546',108,'Moving caster and ring near target'),('yareli155','130',364,'Ring centred on moving caster with near targets; before rank-up')],
 ('12',3):[('dante','118',300,'Caster motion culminating in actual round effect'),('dante','154.2',126,'Actual round effect at caster'),('dante','170',270,'Actual round effect and target relationship; no triangle/world-orb substitution')],
 ('12',4):[('yareli','75.5',120,'Nearby target and mounted movement'),('yareli155','151.1',168,'Unused near-target continuation'),('yareli155','157.5',204,'Origin, bubbles and nearby target'),('yareli155','177.25',118,'Near caster/target interaction')],
 ('13',1):[('dante','217.6',162,'Door, target and forward effect'),('dante','223',193,'Door-side target and direction; no claim about world orbs'),('dante','241.2',168,'Doorway and visible forward targets'),('dante','434.5',156,'Gate and forward target relationship')],
 ('13',2):[('dante','427',354,'Elevated angle to visible targets; stop before ceiling'),('dante','485.1',288,'Balcony and target angle'),('dante','289',71,'Wide action/target angle')],
 ('13',3):[('gauss129','297.3',177,'Ground target group'),('yareli','23',240,'Movement and near enemy fall'),('dante','266',248,'Beam and separated target direction')],
 ('13',4):[('gauss129','396.05',291,'Visible Thumper aim/fire; position example, not a power ranking'),('gauss129','423',198,'Unused aim/fire at Thumper'),('dante','456.2',210,'Targets and changed observation angle')],
 ('14',1):[('dante','260',78,'Forward target action'),('dante','145',224,'Near caster effect and target relation'),('dante','157.7',198,'Forward and near space'),('dante','134',210,'Arm/caster-space action')],
 ('14',2):[('dante','57.7',336,'Arm/cast origin and ensuing effect'),('dante','68+300/60',221,'Unused origin/forward action continuation'),('dante','413.5',210,'Action from lifted/elevated position toward targets')],
 ('14',3):[('dante','418.5',240,'First named forward target/caster-space example'),('dante','510.2',96,'Forward target in a separate shot'),('yareli155','239.5',258,'Target above this caster; generic angle caveat, never Jade-downward claim'),('gauss129','345.4',126,'Near enemy and action; generic comparison caveat')],
 ('14',4):[('gauss129','156.1',258,'Unused firearm action and visible target'),('yareli','79.1',234,'Different visible task/target action'),('yareli155','183.3',187,'Nearby target reaction and task space')],
 ('06',1):[('jade','154.5',61,'Distance decreases while approaching fallen teammate'),('jade','160.5',393,'Revive progress and teammate moving again')],
 ('15',1):[('jade','154.5+61/60',270,'Continuous unused approach toward visibly fallen teammate; recovery/task relation follows in the existing projected white explanation')],
 ('15',2):[('dante','516.2',456,'Forward attack and target on stairs'),('dante','469',150,'Forward/near-target action'),('dante','276.6',78,'Forward origin and visible target'),('dante','422.5',84,'Unused forward target continuation')],
 ('15',3):[('yareli155','114',135,'Forward bubbles and reachable target'),('yareli155','118.75',159,'Unused bubble/target space'),('yareli155','127.75',135,'Near-target reachable space'),('yareli155','209.25',123,'Door and target direction'),('yareli155','220.5',66,'Actual visible target before pillar'),('yareli155','229.5',155,'Bubble and elevated target; positions, not support completion')],
 ('15',4):[('yareli155','187.2',102,'Visible target/result in nearby space'),('yareli155','223.75',123,'Action and near target'),('yareli155','278.1',216,'Unused gun action and target result, stop before splash'),('gauss129','312.65',123,'Forward firearm and target'),('yareli155','275.1',69,'Visible firearm target, stop before empty transition'),('gauss129','380.1',68,'Near foe and observed result')],
 ('16',1):[('gauss','71.5',330,'Unused movement, cast and target action; path clause'),('gauss129','153.1',180,'Forward firearm/target action'),('dante','351.6',96,'Action origin, nearby effect and target; generic action comparison, not the named blue-circle claim'),('dante','85',86,'Origin and forward target action')],
 ('16',2):[('yareli155','142.1',78,'Near caster/target effect before the high-position clause'),('jade','175+658/60',288,'Unused Jade above targets aiming downward'),('gauss129','276.7',240,'Unused approach/fire and target position; general spatial comparison tail'),('dante','78+310/60',85,'Unused forward target angle; general comparison tail')],
}

def seconds(expr):
    return sum((Fraction(x) for x in str(expr).split('+')),Fraction())

roles=read(ROOT/'projects/player-customization/planning/current16-paragraph-roles-v2.json')
timing=read(BASE/'current16-voice-timing-candidate-v1.json')
for i in roles['inputs']:assert sha(ROOT/i['path'])==i['sha256']
r=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','player-customization','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
sources={}
for s in read(BASE/'source-bank-exact-pts-review-execution-v3.json')['sources']:
    if s['key']=='ui':continue
    sources[s['key']]=dict(s,ptsPath=f"shared/output/player-customization/research/source-bank-exact-pts-v3/{s['key']}-native-frame-pts.json",sourceVideoId={'gauss':'gb9JKmJ5-6g','jade':'ovxaYxLbUNE','yareli':'nkhFideK6VU','dante':'vy_vtGx8vq8'}[s['key']],originalOffsetSeconds={'gauss':0,'jade':1280,'yareli':0,'dante':2530}[s['key']])
for key,stem,folder,offset in [('gauss129','gauss129','gauss-devstream129-native-v1',2244),('yareli155','yareli155','yareli-devstream155-native-v1',2721)]:
    j=read(BASE/f'{stem}-exact-crop-execution-v1.json')
    assert j['exitCode']==0 and j['allCropSamplesDirectlyRead']
    c=j['crop'];sources[key]=dict(key=key,path=j['sourcePath'],sha256=j['sourceSha256'],cropCandidate=[c[k] for k in ['x','y','w','h']],sourceVideoId=j['sourceVideoId'],originalOffsetSeconds=offset,ptsPath=f'shared/output/player-customization/research/{folder}/native-frame-pts.json')
sources['jadeYareli']=dict(sources['jade'],key='jadeYareli',cropCandidate=[658,132,1108,624],cropChangePendingDirectPixels=True,reason='Remove development-build top strip while preserving source action; changed crop requires direct selected-pixel approval.')
pts={k:read(ROOT/s['ptsPath'])['frames'] for k,s in sources.items()}
ts={k:[Fraction(p['best_effort_timestamp_time']) for p in v] for k,v in pts.items()}
white={s['id']:s for s in read(BASE/'current-reviewed-original-white-inputs-v2.json')['scenes']}
guide=read(ROOT/'motion-canvas/src/projects/player-customization/observation-guide-timing-measured-v1.json')
guide_rows=guide.get('scenes',guide.get('rows'))
if isinstance(guide_rows,dict):guide_rows=list(guide_rows.values())
if guide_rows is None:raise AssertionError('Read guide timing structure before using it')
alloc=[];used={};issues=[]
scene_rows={s['id']:s for s in timing['rows']}
for p in roles['paragraphs']:
    key=(p['scene'][:2],p['paragraph']);local=p['sceneLocalStartFrame'];actual=[s for s in p['spans'] if s['role']=='actual-game-candidate']
    if actual:
        spec=cuts[key];required=sum(s['frames'] for s in actual)
        assert sum(c[2] for c in spec)==required,(key,required,sum(c[2] for c in spec))
        for source,expr,n,action in spec:
            sec=seconds(expr);start=bisect.bisect_left(ts[source],sec-Fraction(1,10**5));end=start+n
            assert end<=len(pts[source])
            physical=sources[source]['path']
            for a,b,other in used.setdefault(physical,[]):assert end<=a or start>=b,('Repeated native source frames',key,other,source,start,end,a,b)
            used[physical].append((start,end,key))
            ticks=[int(t['best_effort_timestamp']) for t in pts[source][start:end]]
            diffs={b-a for a,b in zip(ticks,ticks[1:])}
            if len(diffs)>1:issues.append(dict(kind='native-pts-gap',paragraph=key,source=source,startFrame=start,diffs=sorted(diffs)))
            if n<60:issues.append(dict(kind='short-action-cut-needs-editorial-replacement-or-specific-transition-evidence',paragraph=key,source=source,frames=n))
            alloc.append(dict(scene=p['scene'],paragraph=p['paragraph'],role='actual-game-candidate',sceneLocalStartFrame=local,sceneLocalEndFrame=local+n,frames=n,outputStartFrame=scene_rows[p['scene']]['startFrame']+local,sourceKey=source,sourcePath=physical,sourceSha256=sources[source]['sha256'],sourceInFrame=start,sourceOutFrame=end,firstNativePts=ticks[0],lastNativePts=ticks[-1],firstNativeSeconds=float(ts[source][start]),originalSourceInSeconds=float(ts[source][start])+sources[source]['originalOffsetSeconds'],cropCandidate=sources[source]['cropCandidate'],visibleAction=action,sourceActionCorrespondenceCandidate=True,sourceActionAligned=False,continuousSelectedPixelsReviewed=False,fixedCaptionPixelsReviewed=False,loop=False,slowdown=False,sourceAudioUsed=False))
            local+=n
    for span in p['spans']:
        if span['role']!='explanation':continue
        if p['scene'] in white:s=white[p['scene']];source_in=s['sourceInFrame']+span['startFrame'];path=s['path'];h=s['sha256']
        else:
            s=next(x for x in guide_rows if x.get('id',x.get('scene'))==p['scene'])
            source_in=s.get('sourceInFrame',s.get('startFrame',s.get('offsetFrames')))+span['startFrame']
            path='shared/output/player-customization/observation-guides-white-v1/player-customization-observation-guides-v1.exact.mp4';h='6bac5ccfd526a4581e3d1b3bc7985ce5deaa5fe4b041d19161069d0eba67702e'
        alloc.append(dict(scene=p['scene'],paragraph=p['paragraph'],role='explanation',sceneLocalStartFrame=span['startFrame'],sceneLocalEndFrame=span['endFrame'],frames=span['frames'],outputStartFrame=scene_rows[p['scene']]['startFrame']+span['startFrame'],sourcePath=path,sourceSha256=h,sourceInFrame=source_in,sourceOutFrame=source_in+span['frames'],originalAnimatedSourcePixelsReviewed=True,finalPixelsReviewed=False))
alloc.sort(key=lambda s:s['outputStartFrame'])
cursor=120
for a in alloc:assert a['outputStartFrame']==cursor,(cursor,a);cursor+=a['frames']
assert cursor==120+roles['bodyFrames']
assert sum(s['frames'] for s in alloc if s['role']=='explanation')==14128
assert sum(s['frames'] for s in alloc if s['role']=='actual-game-candidate')==21193
gap=read(BASE/'jade-support-gap-direct-review-v1.json')
assert gap['sourceSha256']==sources['jade']['sha256'] and gap['approachGapCandidateRelated']
out=ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v3.json'
assert not out.exists(),'Preserve prior candidate; make an explicitly reviewed next version.'
e=dict(schemaVersion=3,slug='player-customization',preparedAt=now(),status='explicit-disjoint-native-allocation-candidate-continuous-pixels-pending',priorCandidate='projects/player-customization/planning/integer-action-allocation-candidate-v2.json',revisionReason='Replace the isolated half-second Jade approach edge and separate result fragment with a single normal-speed 4.5-second unused approach. New gap samples and bounded playback remain candidate evidence; selected encoded pixels still require direct review.',jadeGapReview='projects/player-customization/production/jade-support-gap-direct-review-v1.json',inputs=roles['inputs'],currentDuplicateCheck=dict(exitCode=r.returncode,output=r.stdout+r.stderr),sources=list(sources.values()),paragraphs=roles['paragraphs'],cuts=alloc,cutCount=len(alloc),issues=issues,allNativeSourceFramesUnique=True,allCurrentPcmSamplesPreserved=True,wholePcmSamples=timing['wholePcmSamples'],bodyFrames=35321,actualFramesCandidate=21193,explanationFramesCandidate=14128,finalFramesCandidate=36041,bodyRatioErrorFrames=.4,sourceAllocationApproved=False,finalTimingApproved=False,bodyRatioApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,uploaded=False,newGitImages=0,newMedia=0,next='Build one CPU-only selected native preview and inspect the continuous action/crop and all fixed-caption cue/cut pixels before adopting final timing. Do not render a final pair from this candidate.')
save(out,e)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage=e['status'],currentIntegerAllocationCandidate=out.relative_to(ROOT).as_posix(),currentDistinctCheckPassed=True,nextAction=e['next']);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization');i.update(stage=e['status'],currentIntegerAllocationCandidate=out.relative_to(ROOT).as_posix(),nextAction=e['next']);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(status=e['status'],cuts=len(alloc),actionCuts=sum(s['role']=='actual-game-candidate' for s in alloc),issues=issues,allNativeSourceFramesUnique=True),ensure_ascii=False,indent=2))
