"""Deliver only the completed interpolation pair with an isolated Git index.

Shared raster registry/ignore/project catalog are composed from HEAD plus the
four exact reviewed rows. Never stage foreign changes or reproducible media.
"""
from pathlib import Path
import os,json,subprocess,hashlib,argparse,shutil,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OUT=ROOT/'shared/output/game-math-part2-teaching-revision/git-delivery/interpolation';OUT.mkdir(parents=True,exist_ok=True)
GIT=shutil.which('git');NODE=shutil.which('node');assert GIT and NODE
parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--commit-and-push',action='store_true');args=parser.parse_args();assert args.prepare!=args.commit_and_push
def run(cmd,env=None):
 try:return subprocess.check_output(cmd,cwd=ROOT,env=env,stderr=subprocess.STDOUT)
 except subprocess.CalledProcessError as error:
  print(error.output.decode('utf8',errors='replace'),flush=True)
  raise
def git(*args,env=None):return run([GIT,*args],env)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SLUGS=['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']
TEXT={'.json','.md','.py','.cjs','.ts','.tsx','.meta','.srt','.ass','.txt','.html','.css'}
pathlist=OUT/'explicit-paths.json';preparation=OUT/'preparation.json'
if args.prepare:
 head=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').decode().strip()=='main'
 index=OUT/'interpolation.index'
 if index.exists():index.unlink() # Exact owned temporary index.
 env=os.environ.copy();env['GIT_INDEX_FILE']=str(index);git('read-tree',head,env=env)
 paths=set()
 def add_tree(prefix):
  for p in prefix.rglob('*'):
   if p.is_file() and p.suffix in TEXT and '__pycache__' not in p.parts:paths.add(p.relative_to(ROOT).as_posix())
 for slug in SLUGS:
  receipt=read(ROOT/f'projects/{slug}/publishing/youtube-upload.json');assert receipt['privateUploadComplete'] and receipt['fullPublishingSettingsComplete']
  add_tree(ROOT/'projects'/slug);add_tree(ROOT/'motion-canvas/src/projects'/slug)
  paths.update([f'projects/{slug}/publishing/thumbnail-v2.png',f'projects/{slug}/publishing/proof/platform-caption-proof.png'])
 for slug in ['game-math-interpolation-teaching-additions-v2','game-math-interpolation-worked-checks-v3','game-math-interpolation-numeric-retakes-v4']:add_tree(ROOT/'projects'/slug)
 for p in B.iterdir():
  if p.is_file() and p.suffix in TEXT and ('interpolation' in p.name or p.name in ['README.md','queue.json','expanded-publication-plan.json','quaternion-git-delivery.json']):paths.add(p.relative_to(ROOT).as_posix())
 for prefix in [B/'interpolation-tracks',B/'baselines/game-math-rotation-interpolation']:add_tree(prefix)
 paths.add('manim/projects/game-math-part2-teaching-revision/interpolation_additions.py')
 images=[p for p in sorted(paths) if Path(p).suffix=='.png'];registry=read(ROOT/'shared/git-essential-images.json')
 assert len(images)==4
 for p in images:
  row=next(e for e in registry['entries'] if e['path']==p);assert row['sha256']==sha(ROOT/p) and row['purpose'] in ['delivery-thumbnail','minimal-publishing-proof']
 def headtext(p):return git('show',head+':'+p).decode('utf8')
 shared={};r=json.loads(headtext('shared/git-essential-images.json'));r['entries']=[x for x in r['entries'] if x['path'] not in images]+[x for x in registry['entries'] if x['path'] in images];shared['shared/git-essential-images.json']=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 base=headtext('.gitignore')
 for p in images:
  exception='!/'+p
  if exception not in base.splitlines():base=base.rstrip()+'\n'+exception+'\n'
 shared['.gitignore']=base
 base=json.loads(headtext('motion-canvas/projects.json'))
 for value in read(ROOT/'motion-canvas/projects.json'):
  if any('/'+slug+'/' in value for slug in SLUGS) and value not in base:base.append(value)
 shared['motion-canvas/projects.json']=json.dumps(base,ensure_ascii=False,indent=2)+'\n'
 assert not any(Path(p).suffix.lower() in {'.wav','.mp4','.mp3','.m4a','.zip','.pt','.jpg','.jpeg'} for p in paths)
 for p in sorted(paths):git('add','--',p,env=env)
 for p,content in shared.items():
  blob=OUT/('shared-'+p.replace('/','--'));blob.write_text(content,encoding='utf8');digest=git('hash-object','-w',str(blob)).decode().strip();git('update-index','--add','--cacheinfo','100644',digest,p,env=env)
 staged=git('diff','--cached','--name-only',env=env).decode().splitlines();assert set(staged)<=paths|set(shared)
 write(pathlist,{'explicitPaths':sorted(paths),'sharedBlobPaths':sorted(shared),'essentialImages':images,'stagedPaths':staged})
 (OUT/'staged.diff').write_bytes(git('diff','--cached','--stat',env=env)+git('diff','--cached','--',*shared.keys(),env=env))
 normal_index=Path(git('rev-parse','--git-path','index').decode().strip());normal_index=normal_index if normal_index.is_absolute() else ROOT/normal_index
 write(preparation,{'baseHead':head,'isolatedIndex':str(index),'normalIndex':str(normal_index),'normalIndexSha256':sha(normal_index),'pathsSha256':sha(pathlist),'stagedCount':len(staged),'review':'pending explicit staged path/shared-diff review','createdAt':datetime.datetime.now().astimezone().isoformat()})
 print(json.dumps({'stagedCount':len(staged),'essentialImages':len(images),'review':str(OUT/'staged.diff'),'commitCreated':False}))
else:
 prep=read(preparation);assert prep['review']=='directly-reviewed-explicit-paths-and-shared-diff';assert git('rev-parse','HEAD').decode().strip()==prep['baseHead'],'Concurrent HEAD advanced; prepare anew.'
 assert sha(pathlist)==prep['pathsSha256'];env=os.environ.copy();env['GIT_INDEX_FILE']=prep['isolatedIndex']
 print(run([NODE,'scripts/media-policy.cjs'],env).decode(),end='')
 for slug in SLUGS:print(run([NODE,'scripts/build-rebuild-manifests.cjs',slug,'--check']).decode(),end='')
 assert git('rev-parse','HEAD').decode().strip()==prep['baseHead'],'Concurrent HEAD advanced during checks; prepare anew without changing the shared index.'
 git('commit','-m','Deliver coherent interpolation lectures with tracked gameplay and bilingual private uploads',env=env)
 commit=git('rev-parse','HEAD').decode().strip();normal_unchanged=sha(Path(prep['normalIndex']))==prep['normalIndexSha256'];assert normal_unchanged,'Normal shared index changed concurrently; inspect before reporting.'
 push=git('push','origin','HEAD:main').decode();remote=git('ls-remote','origin','refs/heads/main').decode().split()[0];assert remote==commit
 record={'commit':commit,'remoteSha':remote,'pushOutput':push,'normalIndexBytesUnchanged':True,'normalIndexWrittenByTask':False,'explicitPaths':str(pathlist.relative_to(ROOT)),'sharedFilesStagedAsTaskOnlyBlobs':True,'videoAudioArchivesCommitted':False,'privateVideoIds':['_SzbJR4R6OI','n-k7zwaSum0'],'deliveredAt':datetime.datetime.now().astimezone().isoformat(),'scheduleReplacementComplete':False,'fullBatchCompleted':False};write(B/'interpolation-git-delivery.json',record)
 q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-rotation-interpolation');item['revision'].update(gitDelivered=True,gitCommit=commit,remoteVerifiedSha=remote);item['status']='two-reviewed-private-episodes-and-git-delivered; schedule-transition-pending';write(B/'queue.json',q)
 print(json.dumps(record,ensure_ascii=False))
