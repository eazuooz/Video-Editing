"""Record only explicitly viewed input boards; never grant encoded-pixel approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
SOURCE=PROOF/'word-cue-input-trials-v1.json'
DEST=PROOF/'word-cue-input-direct-progress-v1.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True);p.add_argument('--notes',required=True);p.add_argument('--issues',default='[]');p.add_argument('--issues-file',type=Path);a=p.parse_args()
issues=read(a.issues_file) if a.issues_file else json.loads(a.issues)
assert isinstance(issues,list)
e=read(SOURCE);d=read(DEST) if DEST.exists() else dict(schemaVersion=1,slug='familiar-game-rules',evidence=SOURCE.relative_to(ROOT).as_posix(),evidenceSha256=sha(SOURCE),groups=[],boards=[],allInputBoardsDirectlyRead=False,allFinalCaptionPixelsReviewed=False,allSourceMotionReviewed=False,finalTimelineAdopted=False,imagesGitPolicy='local-only',newGitImages=0,humanListeningPronunciation='pending')
assert d['evidenceSha256']==sha(SOURCE)
indices=set(b['index'] for b in d['boards']);chosen=[b for b in e['boards'] if a.first<=b['index']<=a.last]
assert len(chosen)==a.last-a.first+1 and not any(b['index'] in indices for b in chosen)
now=datetime.now(timezone.utc).isoformat()
for b in chosen:
 assert sha(ROOT/b['path'])==b['sha256']
 d['boards'].append(dict(index=b['index'],path=b['path'],sha256=b['sha256'],sampleIndices=b['sampleIndices'],directlyRead=True,reviewedAt=now))
d['groups'].append(dict(first=a.first,last=a.last,reviewedAt=now,notes=a.notes,issues=issues))
d['boards'].sort(key=lambda b:b['index']);d['directlyReadBoards']=len(d['boards']);d['directlyReadSamples']=len(set(n for b in d['boards'] for n in b['sampleIndices']));d['allInputBoardsDirectlyRead']=len(d['boards'])==e['boardCount'];d['updatedAt']=now
d['scope']='Directly viewed source-input/PIL-caption trial boards only; full moving cuts, white scenes, final mix and encoded pixels remain separate gates.'
t=DEST.with_name(DEST.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,DEST)
print(json.dumps({k:d[k] for k in ['directlyReadBoards','directlyReadSamples','allInputBoardsDirectlyRead','allFinalCaptionPixelsReviewed']},ensure_ascii=False))
