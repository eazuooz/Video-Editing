"""Deliver one reviewed lines episode; preserve the shared index byte-for-byte."""
from pathlib import Path
import os,json,subprocess,hashlib,argparse,shutil,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OUT=ROOT/'shared/output/game-math-part2-teaching-revision/git-delivery/lines-first';OUT.mkdir(parents=True,exist_ok=True)
GIT=shutil.which('git');NODE=shutil.which('node');assert GIT and NODE
parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--commit-and-push',action='store_true');args=parser.parse_args();assert args.prepare!=args.commit_and_push
def run(cmd,env=None):
 try:return subprocess.check_output(cmd,cwd=ROOT,env=env,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError as e:print(e.output.decode('utf8',errors='replace'),flush=True);raise
def git(*args,env=None):return run([GIT,*args],env)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SLUG='game-math-lines-circles-v2';TEXT={'.json','.md','.py','.cjs','.ts','.tsx','.meta','.srt','.ass','.txt','.html','.css'}
pathlist=OUT/'explicit-paths.json';preparation=OUT/'preparation.json'
if args.prepare:
 head=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').decode().strip()=='main'
 index=OUT/'lines-first.index'
 if index.exists():index.unlink()
 env=os.environ.copy();env['GIT_INDEX_FILE']=str(index);git('read-tree',head,env=env);paths=set()
 def add_tree(prefix):
  for p in prefix.rglob('*'):
   if p.is_file() and p.suffix in TEXT and '__pycache__' not in p.parts:paths.add(p.relative_to(ROOT).as_posix())
 receipt=read(ROOT/f'projects/{SLUG}/publishing/youtube-upload.json');assert receipt['privateUploadComplete'] and receipt['fullPublishingSettingsComplete']
 add_tree(ROOT/'projects'/SLUG);add_tree(ROOT/'motion-canvas/src/projects'/SLUG)
 images=[f'projects/{SLUG}/publishing/thumbnail-v2.png',f'projects/{SLUG}/publishing/private-caption-proof.png'];paths.update(images)
 for suffix in ['bounds-teaching-additions-v2','narration-retakes-v3','opening-retake-v4','numeric-retakes-v5','unit-retake-v6']:add_tree(ROOT/'projects'/('game-math-lines-'+suffix))
 for p in B.iterdir():
  if p.is_file() and p.suffix in TEXT and ('lines' in p.name or p.name in ['README.md','queue.json','interpolation-git-delivery.json','complete-revision-source-records.py']):paths.add(p.relative_to(ROOT).as_posix())
 for prefix in [B/'lines-tracks',B/'baselines/game-math-lines-bounds']:add_tree(prefix)
 paths.add('manim/projects/game-math-part2-teaching-revision/lines_additions.py')
 # Reviewed documentation repair to completed interpolation renders; no media changes.
 for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
  paths.update([f'projects/{slug}/project.json',f'projects/{slug}/production/footage-cuts.json'])
 registry=read(ROOT/'shared/git-essential-images.json')
 for p in images:
  row=next(e for e in registry['entries'] if e['path']==p);assert row['sha256']==sha(ROOT/p) and row['purpose'] in ['delivery-thumbnail','minimal-publishing-proof']
 def headtext(p):return git('show',head+':'+p).decode('utf8')
 shared={};r=json.loads(headtext('shared/git-essential-images.json'));r['entries']=[x for x in r['entries'] if x['path'] not in images]+[x for x in registry['entries'] if x['path'] in images];shared['shared/git-essential-images.json']=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 base=headtext('.gitignore')
 for p in images:
  if '!/'+p not in base.splitlines():base=base.rstrip()+'\n!/'+p+'\n'
 shared['.gitignore']=base;base=json.loads(headtext('motion-canvas/projects.json'))
 for value in read(ROOT/'motion-canvas/projects.json'):
  if '/'+SLUG+'/' in value and value not in base:base.append(value)
 shared['motion-canvas/projects.json']=json.dumps(base,ensure_ascii=False,indent=2)+'\n'
 assert not any(Path(p).suffix.lower() in {'.wav','.mp4','.mp3','.m4a','.zip','.pt','.jpg','.jpeg'} for p in paths)
 for p in sorted(paths):git('add','--',p,env=env)
 for p,content in shared.items():
  blob=OUT/('shared-'+p.replace('/','--'));blob.write_text(content,encoding='utf8');digest=git('hash-object','-w',str(blob)).decode().strip();git('update-index','--add','--cacheinfo','100644',digest,p,env=env)
 staged=git('diff','--cached','--name-only',env=env).decode().splitlines();assert set(staged)<=paths|set(shared)
 write(pathlist,{'explicitPaths':sorted(paths),'sharedBlobPaths':sorted(shared),'essentialImages':images,'stagedPaths':staged})
 (OUT/'staged.diff').write_bytes(git('diff','--cached','--stat',env=env)+git('diff','--cached','--',*shared.keys(),env=env))
 normal=Path(git('rev-parse','--git-path','index').decode().strip());normal=normal if normal.is_absolute() else ROOT/normal
 write(preparation,{'baseHead':head,'isolatedIndex':str(index),'normalIndex':str(normal),'normalIndexSha256':sha(normal),'pathsSha256':sha(pathlist),'stagedCount':len(staged),'review':'pending explicit staged path/shared-diff review'})
 print(json.dumps({'stagedCount':len(staged),'essentialImages':len(images),'review':str(OUT/'staged.diff')}))
else:
 prep=read(preparation);assert prep['review']=='directly-reviewed-explicit-paths-and-shared-diff';assert git('rev-parse','HEAD').decode().strip()==prep['baseHead']
 assert sha(pathlist)==prep['pathsSha256'];env=os.environ.copy();env['GIT_INDEX_FILE']=prep['isolatedIndex']
 print(run([NODE,'scripts/media-policy.cjs'],env).decode(),end='');print(run([NODE,'scripts/build-rebuild-manifests.cjs',SLUG,'--check']).decode(),end='')
 assert git('rev-parse','HEAD').decode().strip()==prep['baseHead']
 git('commit','-m','Deliver coherent lines and circles lecture with reviewed private upload',env=env)
 commit=git('rev-parse','HEAD').decode().strip();assert sha(Path(prep['normalIndex']))==prep['normalIndexSha256']
 push=git('push','origin','HEAD:main').decode();remote=git('ls-remote','origin','refs/heads/main').decode().split()[0];assert remote==commit
 record={'commit':commit,'remoteSha':remote,'pushOutput':push,'normalIndexBytesUnchanged':True,'normalIndexWrittenByTask':False,'explicitPaths':str(pathlist.relative_to(ROOT)),'sharedFilesStagedAsTaskOnlyBlobs':True,'videoAudioArchivesCommitted':False,'privateVideoIds':['cOcuxWKHN5g'],'deliveredAt':datetime.datetime.now().astimezone().isoformat(),'scheduleReplacementComplete':False,'fullBatchCompleted':False};write(B/'lines-first-git-delivery.json',record)
 q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-lines-bounds');item['revision'].update(firstEpisodeGitDelivered=True,firstEpisodeGitCommit=commit,firstEpisodeRemoteVerifiedSha=remote);write(B/'queue.json',q)
 print(json.dumps(record,ensure_ascii=False))
