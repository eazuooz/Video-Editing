"""Deliver one reviewed episode with an isolated index and owned queue fields only."""
from pathlib import Path
import argparse,copy,hashlib,json,os,subprocess
parser=argparse.ArgumentParser();parser.add_argument('episode',choices=['foundations','calculations']);parser.add_argument('--commit',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3';slug=f'game-math-quaternion-{args.episode}-v3'
W=ROOT/'shared/output/quaternion-git-delivery-v3';W.mkdir(exist_ok=True)
env=dict(os.environ,GIT_INDEX_FILE=str(W/f'{args.episode}.index'))
def git(*a,data=None,isolated=True):
 result=subprocess.run(['git',*a],cwd=ROOT,env=env if isolated else os.environ,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if result.returncode:raise RuntimeError(result.stderr.decode('utf8',errors='replace'))
 return result.stdout
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=git('rev-parse','HEAD',isolated=False).decode().strip();branch=git('symbolic-ref','HEAD',isolated=False).decode().strip()
index=Path(git('rev-parse','--git-path','index',isolated=False).decode().strip())
if not index.is_absolute():index=ROOT/index
before=sha(index);git('read-tree',base)
p=ROOT/'projects'/slug;review=read(p/'production/current-pixel-review.json');qa=read(p/'production/qa.json')
assert review['directMovingPixelsPassed'] and review['wholeNativePlayback']['ended']
assert review['captionReview']['allCuePixelsDirectlyReviewed'] and len(review['distinctGames'])>=4
assert qa['ratioErrorFrames']==0 if 'ratioErrorFrames' in qa else review['bodyRatio']['roundingErrorFrames']==0
files=[]
allowed={'.py','.cjs','.json','.md','.txt','.srt','.ass','.ts','.tsx'}
def add_tree(folder):
 for f in folder.rglob('*'):
  if f.is_file() and f.suffix in allowed and not {'__pycache__','delivery-history'}.intersection(f.parts):files.append(f.relative_to(ROOT).as_posix())
add_tree(p);add_tree(ROOT/'projects/game-math-quaternion-cross-game-additions-v3');add_tree(Q)
for f in B.iterdir():
 if f.is_file() and 'quaternion' in f.name and 'v3' in f.name and f.suffix in allowed:files.append(f.relative_to(ROOT).as_posix())
files.append('manim/projects/game-math-part2-teaching-revision/quaternion_four_game_v3.py')
assert not any(Path(f).suffix in {'.mp4','.wav','.png','.jpg','.webp'} for f in files)
files=sorted(set(files));git('add','--pathspec-from-file=-','--pathspec-file-nul',data=('\0'.join(files)+'\0').encode())
qpath=B.relative_to(ROOT).as_posix()+'/queue.json';queue=json.loads(git('show',base+':'+qpath,isolated=False));working=read(B/'queue.json')
owned=next(i for i in working['items'] if i['slug']=='game-math-quaternion-operations')
target=next(i for i in queue['items'] if i['slug']==owned['slug'])
for key in ['status','fourGameRevision']:target[key]=copy.deepcopy(owned[key])
for key in ['lastProgressAt','currentQuaternionReview']:
 if key in working['execution']:queue['execution'][key]=copy.deepcopy(working['execution'][key])
blob=git('hash-object','-w','--stdin',data=(json.dumps(queue,ensure_ascii=False,indent=2)+'\n').encode()).decode().strip()
git('update-index','--add','--cacheinfo','100644,'+blob+','+qpath);files.append(qpath)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
subprocess.run(['node','scripts/build-rebuild-manifests.cjs',slug,'--check'],cwd=ROOT,env=env,check=True)
tree=git('write-tree').decode().strip();summary=git('diff','--cached','--stat',base).decode('utf8')
record=dict(base=base,tree=tree,episode=args.episode,slug=slug,paths=files,
 currentCaptionedSha256=review['videos']['videoBurnedCaptions']['sha256'],
 realIndexBeforeSha256=before,realIndexPreserved=True,unrelatedQueueAndLedgerExcluded=True,
 automaticOrHumanRightsApprovalNotInferred=True,committed=False,summary=summary)
if args.commit:
 assert git('rev-parse','HEAD',isolated=False).decode().strip()==base
 commit=git('commit-tree',tree,'-p',base,data=f'Deliver reviewed four-game quaternion {args.episode} lecture\n'.encode()).decode().strip()
 git('update-ref',branch,commit,base);record.update(committed=True,commit=commit)
 git('push','origin',branch);remote=git('ls-remote','origin',branch).decode().split()[0];assert remote==commit
 record.update(pushed=True,remoteSha=remote)
record['realIndexAfterSha256']=sha(index);assert record['realIndexAfterSha256']==before
(W/f'{args.episode}-delivery.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(summary);print(json.dumps({k:record.get(k) for k in ['slug','committed','commit','pushed','remoteSha','realIndexPreserved']}))
