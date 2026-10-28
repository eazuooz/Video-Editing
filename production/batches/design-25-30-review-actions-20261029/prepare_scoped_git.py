"""Prepare exact-path inventory and reviewed thumbnail exceptions. No Git mutation.

Default only records proposals. Root may pass --apply-thumbnails after reviewing the
four entries; that changes only the exact image registry entries and ignore lines.
Generated originals, QA images, media and delivery junctions are never candidates.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

R=Path(__file__).resolve().parents[3]
H=Path(__file__).resolve().parent
SLUGS=['computer-controlled-players','in-game-cutscenes','start-with-climax','respect-player-time']
REVISIONS=['limited-color-world','kind-to-beginners']
TEXT_EXT={'.py','.cs','.json','.txt','.md','.cjs','.js','.ts','.tsx','.css','.html','.srt','.ass','.unity','.meta','.mat','.asset','.shader','.hlsl'}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def walk_owned(folder):
    if not folder.is_dir():return
    for base,dirs,files in os.walk(folder,followlinks=False):
        dirs[:]=[d for d in dirs if d.casefold() not in {'local','__pycache__','node_modules','preflight','render','delivery','native-compile-source-repairs','attempt','before'} and not (Path(base)/d).is_symlink()]
        for name in files:
            if name.casefold() == 'preflight.meta':continue
            p=Path(base)/name
            if p.suffix in TEXT_EXT and p.stat().st_size<5_000_000:yield p
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply-thumbnails',action='store_true');a=ap.parse_args()
    proposed=[]
    for slug in SLUGS:
        folder=R/'projects'/slug/'publishing/upload-20261029';review=read(folder/'thumbnail-review.json');f=review['final'];p=R/f['path']
        assert review['status']=='pass' and f['dimensions']==[1280,720]
        assert all(review['inspection'][k] for k in ['generatedFullViewed','final1280Viewed','mobile375Viewed','koreanMainCopyExact','brandExact'])
        assert digest(p)==f['sha256'] and p.stat().st_size==f['bytes']
        assert p==folder/'thumbnail.png'
        proposed.append({'path':f['path'],'purpose':'delivery-thumbnail',
          'reason':'One final original Yamyam calico illustration for the user-approved Unity revision upload. Black/red Korean copy, yellow brand strip and white ground; native1280 and375px visually inspected. Generated original and QA previews stay local.',
          'sha256':f['sha256'],'reviewedAt':review['preparedAt'],'project':slug})
    registry=R/'shared/git-essential-images.json';ignore=R/'.gitignore'
    reg=read(registry);before={str(p.relative_to(R)):digest(p) for p in (registry,ignore)}
    assert all(e['purpose'] in reg['allowedPurposes'] for e in proposed)
    existing={e['path']:e for e in reg['entries']}
    for e in proposed:
        if e['path'] in existing:assert existing[e['path']]['sha256']==e['sha256'],'Existing essential entry differs; preserve and review explicitly'
    if a.apply_thumbnails:
        for e in proposed:
            if e['path'] not in existing:reg['entries'].append(e)
        old=ignore.read_text(encoding='utf-8');lines=old.splitlines();new=[ '!'+e['path'] for e in proposed if '!'+e['path'] not in lines and '!/'+e['path'] not in lines]
        assert before=={str(p.relative_to(R)):digest(p) for p in (registry,ignore)},'Shared files changed during preparation'
        save(registry,reg)
        if new:ignore.write_text(old.rstrip()+'\n\n# Four reviewed delivery thumbnails, design review actions 2026-10-29.\n'+'\n'.join(new)+'\n',encoding='utf-8')
    # A dry inventory run must not overwrite an earlier real registration with a
    # misleading applied=false. Observe the files again and separate state/action.
    actual_registry={e['path']:e for e in read(registry)['entries']}
    actual_ignore=ignore.read_text(encoding='utf-8').splitlines()
    registered=all(e['path'] in actual_registry and actual_registry[e['path']]['sha256']==e['sha256'] and
        ('!'+e['path'] in actual_ignore or '!/'+e['path'] in actual_ignore) for e in proposed)
    proposal={'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'applied':registered,
      'registrationObserved':registered,'applyRequestedThisRun':a.apply_thumbnails,
      'entries':proposed,'exactIgnoreExceptions':['!'+e['path'] for e in proposed],
      'registryAndIgnoreBefore':before,'gitMutation':False,'mediaFilesExcluded':True}
    save(H/'essential-thumbnails-proposal.json',proposal)
    roots=[H,R/'unity/VideoEditing/Assets/VideoScenes/design-25-29-clarity-v3']
    for s in SLUGS:roots += [R/'projects'/s/'production/upload-20261029',R/'projects'/s/'publishing/upload-20261029']
    for s in REVISIONS:roots += [R/'projects'/s/'production/clarity-v3',R/'projects'/s/'script/clarity-v3',R/'unity/VideoEditing/Assets/VideoScenes'/s/'clarity-v3']
    paths={p for root in roots for p in walk_owned(root)}
    paths.update(R/e['path'] for e in proposed)
    paths.update(R/p for p in ['shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md','shared/publishing/video-production-control.json'])
    paths.update(R/p for p in ['output/game-design-25-29-clarity-v3-20261029/index.html',
        'unity/VideoEditing/Assets/VideoScenes/design-25-29-clarity-v3.meta'])
    for s in REVISIONS:
        paths.add(R/'unity/VideoEditing/Assets/VideoScenes'/s/'clarity-v3.meta')
        paths.update(R/'projects'/s/p for p in ['project.json','rebuild.json','production/delivery-output.json',
            'production/checkpoint.json','production/review-ledger.json'])
    if registered:paths.update([registry,ignore])
    # Inventory is advisory. Parent must review current diffs and each stage author's
    # readiness before selectively committing; unfinished source is not auto-staged.
    own_records=[]
    for p in sorted(paths):
        rel=p.relative_to(R).as_posix()
        if p.name in ['scoped-commit-inventory.json','scoped-commit-paths.txt','scoped-commit-paths.json']:continue
        if p.exists():own_records.append({'path':rel,'sha256':digest(p),'bytes':p.stat().st_size})
    read_env=os.environ.copy();read_env['GIT_OPTIONAL_LOCKS']='0'
    status=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all','--',*[str(root.relative_to(R)).replace('\\','/') for root in roots], 'shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md','shared/publishing/video-production-control.json','.gitignore','shared/git-essential-images.json'],cwd=R,env=read_env,text=True,encoding='utf-8')
    # Read-only status is retained as evidence, not used to broaden allowed paths.
    save(H/'scoped-commit-inventory.json',{'preparedAt':proposal['preparedAt'],'advisoryOnly':True,'gitMutation':False,
      'parentReviewRequired':'Review ownership/readiness/current diff; commit only exact selected files with separate-index preservation.',
      'pendingGeneratedUnityMetas':any(x['path'].startswith('unity/') and Path(x['path']).suffix!='.meta' and not (R/(x['path']+'.meta')).is_file() for x in own_records),'records':own_records,'scopedGitStatus':status.splitlines(),
      'excluded':['all delivery/source video/audio','all preflight/QA PNGs','thumbnail-original.png','thumbnail-mobile-375.png','local junction trees','superseded diagnostic source backups (preserved locally)','unrelated task paths']})
    (H/'scoped-commit-paths.txt').write_text('\n'.join(x['path'] for x in own_records)+'\n',encoding='utf-8')
    save(H/'scoped-commit-paths.json',[x['path'] for x in own_records])
    print(json.dumps({'status':'registered-thumbnail-exceptions-verified' if registered else 'proposal-only','applyRequestedThisRun':a.apply_thumbnails,'entries':len(proposed),'inventoryPaths':len(own_records),'gitMutation':False}))
if __name__=='__main__':main()
