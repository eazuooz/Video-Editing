"""Prepare a single measured-scene repair; preserve every v3 input byte."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;MC=ROOT/'motion-canvas/src/projects/character-parameters'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
engine=MC/'spatial-character-explanation-measured-v3.tsx';new=MC/'spatial-character-explanation-measured-v4.tsx';assert not new.exists()
old="tag(['이동','점프','공격'][i],x,-160,170);"
text=engine.read_text('utf-8');assert text.count(old)==1
new.write_text(text.replace(old,"tag(['이동','점프','공격'][i],x,-160,300);"),'utf-8')
directory=MC/'scenes-measured-v4';directory.mkdir()
wrapper=directory/'02-common-baseline.tsx';wrapper.write_text((MC/'scenes-measured-v3/02-common-baseline.tsx').read_text('utf-8').replace('spatial-character-explanation-measured-v3','spatial-character-explanation-measured-v4'),'utf-8')
entry=MC/'black-label-repair-v4.ts';entry.write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './scenes-measured-v4/02-common-baseline?scene';\nexport default makeProject({name:'character-parameters-black-label-repair-v4',scenes:[scene]});\n",'utf-8')
live=MC/'black-structural-preflight-v1.ts';backup=BASE/'live-measured-entry-before-label-repair-v4.ts';assert not backup.exists();backup.write_bytes(live.read_bytes());live.write_text("export {default} from './black-label-repair-v4';\n",'utf-8')
watch=BASE/'watch-measured-black-export-v3.py';target=BASE/'watch-label-repair-export-v4.py';assert not target.exists()
w=watch.read_text('utf-8').replace('measured-black-export-execution-v3.json','label-repair-export-execution-v4.json').replace('character-parameters-black-measured-v3.mp4','character-parameters-black-label-repair-v4.mp4').replace('measured-mc-preparation-v3.json','label-repair-preparation-v4.json').replace("schemaVersion=3","schemaVersion=4")
target.write_text(w,'utf-8')
proof=dict(schemaVersion=4,preparedAt=datetime.now(timezone.utc).isoformat(),scope='Only scene02 common-baseline moving-label layout; all timing/paragraph/caption/voice/game inputs preserved.',originalEngine=rel(engine),originalEngineSha256=sha(engine),engine=rel(new),engineSha256=sha(new),wrapper=rel(wrapper),wrapperSha256=sha(wrapper),entry=rel(entry),entrySha256=sha(entry),liveEntryBefore=rel(backup),liveEntryBeforeSha256=sha(backup),frames=370,expectedInclusiveRawFrames=371,originalPosition=[-160,170],repairedPosition=[-160,300],sourceDirectReview='projects/character-parameters/production/selected-input-direct-review-v3.json',finalTimingApproved=False,allFinalPixels=False,rerenderOtherScenes=False,mediaGitAdditions=0)
(BASE/'label-repair-preparation-v4.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(proof,ensure_ascii=False))
