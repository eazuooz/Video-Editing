"""Verify and preserve the existing combined scripts, without rewriting their bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'measured-current17-plan-v2.json');audit=[]
for lang in ['ko','en']:
 oldpath=OLD/f'script/narration.{lang}.json';addpath=R/f'script/additions.{lang}.json';path=R/f'script/narration.{lang}.json'
 old=read(oldpath);add=read(addpath);current=read(path);before=sha(path)
 byid={s['id']:s for s in old['scenes']+add['scenes']}
 assert len(old['scenes'])==14 and len(add['scenes'])==3 and len(byid)==17
 expected=[byid[s['id']] for s in plan['scenes']]
 assert current['scenes']==expected and sum(len(s['lines']) for s in expected)==81
 assert sha(path)==before
 audit.append(dict(language=lang,path=path.relative_to(ROOT).as_posix(),sha256=before,originalSource=oldpath.relative_to(ROOT).as_posix(),originalSha256=sha(oldpath),additionsSource=addpath.relative_to(ROOT).as_posix(),additionsSha256=sha(addpath),original14ScenesAnd66ParagraphsExact=True,new3ScenesAnd15ParagraphsExact=True,sceneOrder=[s['id'] for s in expected],paragraphCount=81,currentFileRewritten=False))
out=R/'combined-script-preservation-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(verifiedAt=datetime.now(timezone.utc).isoformat(),scripts=audit,existingCombinedScriptsReused=True,mainManifestPromoted=False,allFinalPixelApproval=False,newTts=0,preparationGuardHistory=dict(actualExitCode=1,actualChunk='af06fe',reason='Target scripts already existed; immutable-create guard stopped before any write.',newScriptFilesWritten=0)),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(existingCombinedKoEnVerified=True,scenes=17,paragraphs=81,originalTextsExact=True,filesRewritten=0,mainPromoted=False)))
