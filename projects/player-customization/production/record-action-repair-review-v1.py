"""Record the actually read seventeen local candidate boards; approve no media."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
s=read(BASE/'action-repair-candidate-execution-v1.json')
assert s['exitCode']==0 and len(s['boards'])==17 and len(s['samples'])==98
for x in [*s['boards'],*s['samples']]:assert sha(ROOT/x['path'])==x['sha256'],x['path']
notes=[
 {'window':1,'decision':'reject-whole-window','observation':'18.4–19.15 stationary radial burst then dissolve;19.4–19.9 track largely empty,20.15 airborne,20.4–20.65 landing,20.9–21.48 standing. Does not supply continuous locomotion for cue34; MachRush label is insufficient.'},
 {'window':2,'decision':'candidate-only','observation':'150.35/150.5 caster-centered ring while moving around column; nearby humanoid/doorway visible. Ten native frames are a candidate extension before Dante cut; final encoded boundary review required.'},
 {'window':3,'decision':'candidate-only','observation':'64.6167/64.8667/64.9833 close caster with orbiting Aquablades, fits surrounding-range phrase. Twenty-three-frame prepend candidate; preserve existing endpoint66.5 and total paragraph frames.'},
 {'window':4,'decision':'candidate-only-partial','observation':'66.5–67 overhead caster and nearby foes;67.25–69.0 rotating slashes intersect close foe torso with caster offscreen;69.25–69.4833 caster running but target offscreen. Whole window cannot automatically prove both positions continuously; use a reviewed contiguous sequence with context and inspect encoded caption.'},
 {'window':5,'decision':'reject-for-rotating-nearby-repair','observation':'54–56.75 gray Merulina ride with marketing health-number overlay;57–58.75 Merulina ride shooting distant foes;59–60.75 target closeup,60.983 transition to Aquablades. This is not the caster-centered rotating range described by04p2/12p1.'},
 {'window':6,'decision':'reject-for-nearby-target-phrase','observation':'515–516.75 tunnel movement;517–522.75 WAVE INCOMING and green Mote Collector objective without nearby foe;523.25–523.983 brief combat beyond barrier with slashes. Do not treat green objective as nearby enemy or allocate absent foe to cue173.'}
]
r=dict(schemaVersion=1,slug='player-customization',reviewedAt=now,execution='projects/player-customization/production/action-repair-candidate-execution-v1.json',all17BoardsDirectlyRead=True,all98NativeSamplesDirectlyRead=True,hashVerifiedFiles=115,hashMismatches=0,boards=s['boards'],samples=s['samples'],notes=notes,sourceAllocationApproved=False,allFinalPixels=False,imagesLocalOnly=True,newGitImages=0)
p=BASE/'action-repair-candidate-direct-review-v1.json';assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(boards=17,samples=98,approved=False)))
