"""Create only this distinct, source-reviewed project and preserve the shared registry."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
registry=ROOT/'motion-canvas/projects.json'
before=read(registry)
bank=BASE/'source-action-bank-v4.json'
assert read(bank)['sourceSamplesAndFramingApproved']
assert not (ROOT/'projects/presenting-game-scores').exists()
subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
environment=os.environ.copy();environment['PATH']=str(NODE.parent)+os.pathsep+environment['PATH']
cmd=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','scripts/new-video-project.ps1',
     '-Slug','presenting-game-scores','-TitleKo','점수는 무엇을 말해 줄까? 이름·단위·비교 기준으로 읽는 게임 성과',
     '-TitleEn','What Does a Score Tell Us? Names, Units, and Comparisons']
subprocess.run(cmd,cwd=ROOT,env=environment,check=True)
after=read(registry)
assert all(x in after for x in before)
entry='./src/projects/presenting-game-scores/project.ts'
assert after.count(entry)==1
assert [x for x in after if x!=entry]==before, 'Inspect concurrent new registry entries; preserve them.'
save(BASE/'project-creation-verification-v1.json',dict(schemaVersion=1,slug='presenting-game-scores',
  recordedAt=datetime.now(timezone.utc).isoformat(),duplicateCheckExit=0,sourceBankSha256=sha(bank),
  command=cmd,registryEntriesBefore=len(before),registryEntriesAfter=len(after),
  originalRegistryEntriesAndOrderPreserved=True,registrySha256=sha(registry),
  placeholderAudio='0.1s template WAV is not TTS, approved narration, or final media',
  projectCreated=True,scriptApproved=False,ttsStarted=False,finalMediaApproved=False,
  foreignProjectsModified=False,gitStagingChanges=0))
