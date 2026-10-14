"""Retain all14 original script scenes and insert the3 directly reviewed additions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'measured-current17-plan-v2.json')
review=read(R/'current17-mixed-complete-direct-review-v2.json')
assert review['currentMixedContentReviewPassed']
audit=[]
for lang in ['ko','en']:
 oldpath=OLD/f'script/narration.{lang}.json';addpath=R/f'script/additions.{lang}.json'
 old=read(oldpath);add=read(addpath);byid={s['id']:s for s in old['scenes']+add['scenes']}
 assert len(old['scenes'])==14 and len(add['scenes'])==3 and len(byid)==17
 scenes=[byid[s['id']] for s in plan['scenes']]
 assert len(scenes)==17 and sum(len(s['lines']) for s in scenes)==81
 assert [s for s in scenes if s['id'] in {v['id'] for v in old['scenes']}]==old['scenes']
 assert [s for s in scenes if s['id'] in {v['id'] for v in add['scenes']}]==add['scenes']
 path=R/f'script/narration.{lang}.json';assert not path.exists()
 data=dict(title=old['title'],status='current17-combined-script-prepared-before-final-pixel-adoption',scenes=scenes)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
 audit.append(dict(language=lang,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),originalSource=oldpath.relative_to(ROOT).as_posix(),originalSha256=sha(oldpath),additionsSource=addpath.relative_to(ROOT).as_posix(),additionsSha256=sha(addpath),original14ScenesAnd66ParagraphsExact=True,new3ScenesAnd15ParagraphsExact=True,sceneOrder=[s['id'] for s in scenes],paragraphCount=81))
out=R/'combined-script-preservation-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),scripts=audit,mainManifestPromoted=False,allFinalPixelApproval=False,newTts=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedCombinedKoEn=True,scenes=17,paragraphs=81,originalTextsExact=True,mainPromoted=False)))
