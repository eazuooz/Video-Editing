"""Deliver explicit current-video paths using an isolated actual-HEAD Git index."""
from pathlib import Path
import sys, os, json, hashlib, subprocess, re, time
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'projects/familiar-game-rules/production'))
from final_cpu_common import read, write, now
SLUG='familiar-game-rules'
BATCH='production/batches/sakurai-planning-game-design/'
PROOF=BATCH+'proof-familiar-game-rules/'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(args, env=None, data=None):
    p=subprocess.run(args,cwd=ROOT,env=env,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout.decode('utf-8','replace')+p.stderr.decode('utf-8','replace'))
    return p.stdout
def git(args,env=None,data=None):return run(['git',*args],env,data)
def js(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def head_json(parent,p):return json.loads(git(['show',parent+':'+p]))
def captured(parent,p):
    if p=='.gitignore':
        b=git(['show',parent+':'+p]).decode('utf-8');lines=b.splitlines()
        for entry in read(ROOT/'shared/git-essential-images.json')['entries']:
            if entry.get('project')==SLUG and '!'+entry['path'] not in lines:lines.append('!'+entry['path'])
        return ('\n'.join(lines)+'\n').encode('utf-8')
    if p=='shared/git-essential-images.json':
        j=head_json(parent,p);entries=[e for e in read(ROOT/p)['entries'] if e.get('project')==SLUG]
        assert len(entries)==5
        j['entries']=[e for e in j['entries'] if e.get('project')!=SLUG]+entries
        return js(j)
    if p=='motion-canvas/projects.json':
        j=head_json(parent,p)
        for s in ['./src/projects/familiar-game-rules/project.ts','./src/projects/familiar-game-rules/timed-white-reel-project-v1.ts']:
            if s not in j:j.append(s)
        return js(j)
    if p=='projects/rebuild-index.json':
        j=head_json(parent,p);own=dict(slug=SLUG,manifest='projects/familiar-game-rules/rebuild.json')
        j['projects']=[v for v in j['projects'] if v['slug']!=SLUG]+[own]
        j['projects'].sort(key=lambda v:v['slug']);return js(j)
    if p==BATCH+'queue.json':
        j=head_json(parent,p);w=read(ROOT/p)
        j['items']=[next(v for v in w['items'] if v['slug']==SLUG) if v['slug']==SLUG else v for v in j['items']]
        for k in ['status','updatedAt','lastProgressAt','currentSlug','stopAfterCurrent','automation','progress']:
            j[k]=w[k]
        j['publishingFollowups']=[v for v in j.get('publishingFollowups',[]) if v.get('videoId')!='NLEHMC0XMtg']+[v for v in w.get('publishingFollowups',[]) if v.get('videoId')=='NLEHMC0XMtg']
        return js(j)
    if p in [BATCH+'README.md','docs/VIDEO_ADDITIVE_REVISION.md']:
        base=git(['show',parent+':'+p]);work=(ROOT/p).read_bytes()
        # These files have only the current append; refuse foreign document edits.
        base_text=base.decode('utf-8-sig').replace('\r\n','\n').rstrip()
        work_text=work.decode('utf-8-sig').replace('\r\n','\n')
        assert work_text.startswith(base_text),'Shared document contains another edit: '+p
        suffix=work_text[len(base_text):]
        assert '## 2026-10-07 familiar-game-rules' in suffix
        return base.rstrip(b'\r\n')+suffix.encode('utf-8')
    return (ROOT/p).read_bytes()

def deliver(paths_file,label):
    selected=read(ROOT/paths_file);assert len(selected)==len(set(selected))
    checkfile=PROOF+label+'-prechecks.json';verifyfile=PROOF+label+'-git-verification.json'
    assert checkfile in selected and verifyfile not in selected
    allowed=['projects/familiar-game-rules/','motion-canvas/src/projects/familiar-game-rules/',PROOF]
    exact={'.gitignore','shared/git-essential-images.json','motion-canvas/projects.json','projects/rebuild-index.json',BATCH+'queue.json',BATCH+'README.md','docs/VIDEO_ADDITIVE_REVISION.md',BATCH+'preflight/familiar-game-rules.json'}
    assert all(not p.startswith('/') and '..' not in Path(p).parts and ('\n' not in p) and (p in exact or any(p.startswith(a) for a in allowed)) for p in selected)
    receipt=read(ROOT/'projects/familiar-game-rules/publishing/youtube-upload.json')
    assert receipt['privateSaved'] and receipt['availableSettingsVerified'] and not receipt['scheduled']
    assert receipt['videoId']=='NLEHMC0XMtg' and not receipt['fullSettingsVerified'] and not receipt['thumbnailSaved']
    assert read(ROOT/'projects/familiar-game-rules/production/final-v1/QA.json')['technicalReviewApproved']
    assert 'status = "PAUSED"' in Path('C:/Users/eazuo/.codex/automations/24/automation.toml').read_text(encoding='utf-8')
    parent=git(['rev-parse','HEAD']).decode().strip()
    assert git(['branch','--show-current']).decode().strip()=='main'
    staged=git(['diff','--cached','--name-only','-z']).decode().split('\0');staged=[p for p in staged if p]
    assert not set(staged)&set(selected),'Selected path already staged by another task'
    def foreign_index():
        entries=git(['ls-files','--stage','-z']).split(b'\0')
        return sha(b'\0'.join(e for e in entries if e and e.split(b'\t',1)[1].decode() not in selected))
    foreign_before=foreign_index()
    index=(ROOT/'.git'/('familiar-delivery-'+str(time.time_ns())+'.index')).resolve()
    assert index.parent== (ROOT/'.git').resolve()
    env={**os.environ,'GIT_INDEX_FILE':str(index)}
    snapshots=[];commands=[]
    images={e['path']:e for e in read(ROOT/'shared/git-essential-images.json')['entries'] if e.get('project')==SLUG}
    def snapshot(p):
        b=captured(parent,p)
        if p.endswith(('.json','.meta')):json.loads(b.decode('utf-8-sig'))
        assert not re.search(r'\.(mp4|webm|mov|mkv|wav|m4a|mp3|aac|flac|ogg|zip|7z|rar|info\.json)$',p,re.I)
        assert 'research-local' not in p and not p.endswith('.raw-original')
        if re.search(r'\.(png|jpe?g|webp|gif|bmp|tiff?)$',p,re.I):
            assert p in images and images[p]['sha256']==sha(b),'Unreviewed image'
            r=subprocess.run(['git','check-ignore','--no-index',p],cwd=ROOT,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==1,'Exact image ignore exception required'
        blob=git(['hash-object','-w','--path='+p,'--stdin'],env,b).decode().strip()
        snapshots.append(dict(path=p,blob=blob,capturedSha256=sha(b),capturedAt=now(),workingCopyPreserved=True))
        return ('100644 '+blob+'\t'+p+'\n').encode('utf-8')
    def check(args):
        p=subprocess.run([NODE,*args],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        output=(p.stdout+p.stderr).decode('utf-8','replace')
        commands.append(dict(commandLine=[NODE,*args],exitCode=p.returncode,output=output))
        assert p.returncode==0,output
    def whitespace():
        # Raw UI captures and measured subtitle files retain exact original bytes.
        args=['diff','--cached','--check',parent,'--','.',
              ':(exclude,glob)**/*.ax.txt',':(exclude,glob)**/*.srt']
        git(args,env)
        commands.append(dict(commandLine=['git',*args],exitCode=0,
                             scope='Authored code/JSON/Markdown; original AX captures and measured SRT bytes preserved.'))
    try:
        git(['read-tree',parent],env)
        rows=[snapshot(p) for p in selected if p!=checkfile]
        git(['update-index','--index-info'],env,b''.join(rows))
        check(['scripts/media-policy.cjs'])
        check(['scripts/review-video-duplicates.cjs',SLUG,'--check'])
        check(['scripts/build-rebuild-manifests.cjs',SLUG,'--check'])
        check(['motion-canvas/node_modules/typescript/bin/tsc','--noEmit','-p',PROOF+'tsconfig-current-review.json'])
        whitespace()
        changed=git(['diff','--cached','--name-only','-z',parent],env).decode().split('\0');changed=[p for p in changed if p]
        image_paths=[p for p in changed if p in images]
        write(ROOT/checkfile,dict(schemaVersion=1,checkedAt=now(),parent=parent,commands=commands,
              explicitPaths=selected,snapshots=snapshots,temporaryIndexFromActualHead=True,
              foreignStagedBefore=staged,foreignIndexBefore=foreign_before,
              newEssentialImages=image_paths,newQaSourceImages=0,mediaAdded=0,whitespacePassed=True,
              whitespaceScope='Authored code/JSON/Markdown. Raw AX and SRT retained byte-for-byte; their captured trailing whitespace is not an authored-code failure.',
              npm='Unavailable; exact Node hooks used.',globalWorkingTreePassed=False,
              globalLimitation='Earlier global TypeScript failed in unrelated unfinished/older projects. Only current-video TypeScript and rebuild checks are approved.',
              renderQaFourFilesPrivateSaved=True,availableSettingsVerified=True,fullSettingsVerified=False,
              thumbnailPending=True,humanReviewsPending=True,automation24='PAUSED',nextQueuedStarted=False))
        git(['update-index','--index-info'],env,snapshot(checkfile))
        whitespace()
        assert not git(['diff','--cached','--diff-filter=D','--name-only',parent],env).strip()
        changed=[p for p in git(['diff','--cached','--name-only','-z',parent],env).decode().split('\0') if p]
        assert changed and set(changed)<=set(selected)
        for s in snapshots:
            if s['path']!=checkfile:assert sha(captured(parent,s['path']))==s['capturedSha256'],'Working input changed'
        tree=git(['write-tree'],env).decode().strip()
        assert git(['rev-parse','HEAD']).decode().strip()==parent,'Concurrent HEAD changed; do not overwrite'
        message=('Deliver reviewed familiar controls video privately with fixed captions; pause production\n' if label=='final-private-delivery' else 'Record verified current private delivery and requested production pause\n')
        commit=git(['commit-tree',tree,'-p',parent],env,message.encode()).decode().strip()
        actual=[p for p in git(['diff-tree','--no-commit-id','--name-only','-r','-z',commit]).decode().split('\0') if p]
        assert sorted(actual)==sorted(changed)
        for s in snapshots:
            if s['path'] in changed:assert git(['rev-parse',commit+':'+s['path']]).decode().strip()==s['blob']
        assert foreign_index()==foreign_before
        git(['update-ref','HEAD',commit,parent])
        # Sync only our selected paths; all other index entries remain identical.
        for start in range(0,len(changed),35):git(['restore','--staged','--source='+commit,'--',*changed[start:start+35]])
        foreign_after=foreign_index();assert foreign_after==foreign_before
        push=subprocess.run(['git','push','origin','main'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        local=git(['rev-parse','HEAD']).decode().strip();remote=git(['ls-remote','origin','refs/heads/main']).decode().split()[0]
        write(ROOT/verifyfile,dict(schemaVersion=1,verifiedAt=now(),label=label,productionCommit=commit,parent=parent,
              commitPaths=actual,snapshots=[s for s in snapshots if s['path'] in changed],pushExitCode=push.returncode,
              pushOutput=(push.stdout+push.stderr).decode('utf-8','replace'),normalPush=True,forcePush=False,
              localSha=local,remoteSha=remote,remoteMatches=local==remote,
              foreignIndexBefore=foreign_before,foreignIndexAfter=foreign_after,foreignIndexEntriesUnchanged=True,
              otherUsersFilesIncluded=False,newRasterCommitted=len(image_paths),newQaSourceImages=0,mediaCommitted=False,
              videoId='NLEHMC0XMtg',privateSaved=True,availableSettingsVerified=True,fullSettingsVerified=False,
              thumbnailPending=True,humanReviewsPending=True,automation24='PAUSED',nextQueuedStarted=False))
        assert push.returncode==0 and local==remote,'Actual normal-push outcome saved; remote match incomplete'
        print(json.dumps(dict(commit=commit,parent=parent,paths=len(actual),newEssentialImages=len(image_paths),media=0,
                         pushExitCode=push.returncode,localSha=local,remoteSha=remote,foreignIndexEntriesUnchanged=True)))
    finally:
        if index.exists():index.unlink()

if __name__=='__main__':deliver(sys.argv[1],sys.argv[2])
