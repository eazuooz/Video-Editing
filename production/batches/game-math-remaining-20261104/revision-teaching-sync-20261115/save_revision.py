"""Commit only this finite revision and its own leaves in shared ledgers."""
import argparse
import copy
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile

from inventory import ROOT,HERE


def git(*args,data=None,env=None):
    return subprocess.check_output(["git","-c","core.safecrlf=false",*args],cwd=ROOT,input=data,env=env)


def payload(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf8")


def project(path,base,current):
    a=json.loads(base.decode("utf-8-sig"));b=json.loads(current.decode("utf-8-sig"))
    if path.endswith("video-production-control.json"):
        a["explicitMathRemainingBatch20261104"]["teachingSyncRevision20261115"]=copy.deepcopy(b["explicitMathRemainingBatch20261104"]["teachingSyncRevision20261115"])
    else:a["teachingSyncRevision20261115"]=copy.deepcopy(b["teachingSyncRevision20261115"])
    return payload(a)


def main(message,push):
    helper=runpy.run_path(str(ROOT/"projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py"))
    publish=helper["publish_index_and_ref"]
    head=git("rev-parse","HEAD").decode().strip();ref=git("symbolic-ref","HEAD").decode().strip()
    index=Path(git("rev-parse","--path-format=absolute","--git-path","index").decode().strip());original=index.read_bytes()
    direct=[p for p in HERE.iterdir() if p.suffix in (".py",".json",".md") or p.name==".gitignore"]
    direct.append(HERE/"sources/mario-kart-provenance.json")
    direct.append(HERE.parent/"revision-teaching-sync-20261114/audit-m24-m26.json")
    shared=["shared/publishing/video-production-control.json",str((HERE.parent/"batch.json").relative_to(ROOT)).replace("\\","/"),str((HERE.parent/"checkpoint.json").relative_to(ROOT)).replace("\\","/")]
    with tempfile.TemporaryDirectory() as temp:
        commit_env=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/"commit.index"))
        reconcile=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/"reconcile.index"))
        git("read-tree",head,env=commit_env);Path(reconcile["GIT_INDEX_FILE"]).write_bytes(original)
        buffers={e["GIT_INDEX_FILE"]:bytearray() for e in (commit_env,reconcile)}
        def stage(path,data,env):
            data=data.replace(b"\r\n",b"\n")
            oid=git("hash-object","-w","--stdin",data=data).decode().strip()
            buffers[env["GIT_INDEX_FILE"]].extend(f"100644 {oid}\t{path}\0".encode("utf8"))
        for p in direct:
            data=p.read_bytes();relative=p.relative_to(ROOT).as_posix()
            if p.suffix==".json":json.loads(data.decode("utf-8-sig"))
            if p.suffix==".py":compile(data,str(p),"exec")
            for env in (commit_env,reconcile):stage(relative,data,env)
        for path in shared:
            current=(ROOT/path).read_bytes()
            stage(path,project(path,git("show",head+":"+path),current),commit_env)
            stage(path,project(path,git("show",":"+path),current),reconcile)
        for env in (commit_env,reconcile):git("update-index","-z","--index-info",env=env,data=bytes(buffers[env["GIT_INDEX_FILE"]]))
        git("diff","--cached","--check",env=commit_env)
        subprocess.run(["node","scripts/media-policy.cjs"],cwd=ROOT,env=commit_env,check=True)
        changed=git("diff","--cached","--name-only",head,env=commit_env).decode().splitlines()
        if not changed:print("No scoped changes");return
        tree=git("write-tree",env=commit_env).decode().strip()
        commit=git("commit-tree",tree,"-p",head,data=(message+"\n").encode("utf8")).decode().strip()
        publish(index,Path(reconcile["GIT_INDEX_FILE"]).read_bytes(),original,ref,head,commit)
        print(commit,len(changed),"scoped files; unrelated index entries preserved")
    if push:subprocess.run(["git","push","origin",ref],cwd=ROOT,check=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--message",required=True);ap.add_argument("--push",action="store_true")
    args=ap.parse_args();main(args.message,args.push)
