"""Save just the course edition. Preserve unrelated staged changes and shared-table rows."""
import argparse, json, os, re, runpy, subprocess, tempfile
from pathlib import Path
from edition import ROOT,BATCH,read

def project(path,base,working,episodes):
    if path.endswith(".json"):
        result=json.loads(base.decode("utf-8-sig")); current=json.loads(working.decode("utf-8-sig"))
        if path.endswith("video-production-control.json"):
            result["explicitMathRemainingBatch20261104"]["groupReview20261106"]=current["explicitMathRemainingBatch20261104"]["groupReview20261106"]
        else:
            key="rows" if "rows" in result else "items"
            updates={r["id"]:r for r in current[key] if r["id"] in episodes}
            result[key]=[updates.get(r["id"],r) for r in result[key]]
        return (json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    result=base.decode("utf-8-sig")
    for line in working.decode("utf-8-sig").splitlines():
        match=re.match(r"^\| (M\d+)( \|| [^|]+ \|)",line)
        if match and match[1] in episodes:
            lead=r" \|" if match[2]==" |" else r" [^|]+ \|"
            result=re.sub(r"^\| "+match[1]+lead+r".*$",lambda _:line,result,flags=re.M)
    return result.encode("utf8")

def commit(message,push):
    helper=runpy.run_path(str(BATCH/"save-progress.py"));git=helper["git"]
    publish=runpy.run_path(str(ROOT/"projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py"))["publish_index_and_ref"]
    rows=read(BATCH/"batch.json")["items"][2:];episodes={r["id"] for r in rows}
    direct=list(x for x in Path(__file__).parent.iterdir() if x.suffix in {".py",".txt",".ps1"})
    direct+=[BATCH/f for f in ["align-module-speech.py","compose-module.py","finish-selected-voice.py","freeze-reviewed-module-narration.py","prepare-module-render.py","render-voice.py","update-preproduction.py","progress.md"]]
    for r in rows:
        p=ROOT/"projects"/r["slug"]
        direct.extend(p/x for x in ["project.json","planning/part2-delivery-edition.json","planning/part2-picture-plan.json","planning/scene-bindings.json","planning/bilingual-caption-map.json","planning/production-plan.json","planning/script-integration.json","planning/caption-reading-adjustments.json","script/narration.ko.json","script/narration.en.json","script/integrated-readthrough.ko.txt","script/integrated-readthrough.en.txt","production/checkpoint.json"])
        direct.extend((p/"production").glob("tts-manifest-audio-v*.json"))
        direct.extend((p/"production/part2-review").glob("*.json"))
    for slug in ["game-math-pipeline-shaders","game-math-velocity-derivatives","game-math-acceleration-integration","game-math-circular-motion"]:
        s=ROOT/"projects"/slug/"production/unity-staging"
        direct.extend(s/x for x in ["PipelineMeaningGuides.cs","PipelineTeachingStage.cs","MotionLessonStage.cs","verify-source.py","compile-check.json","sandbox-preparation.json"] if (s/x).is_file())
    shared=["shared/publishing/video-production-control.json","shared/publishing/video-worklist.json","docs/VIDEO_WORKLIST.md",(BATCH/"batch.json").relative_to(ROOT).as_posix()]
    head=git("rev-parse","HEAD").decode().strip();ref=git("symbolic-ref","HEAD").decode().strip()
    real=Path(git("rev-parse","--path-format=absolute","--git-path","index").decode().strip());original=real.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        assign=lambda name:dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/name))
        isolated,reconcile=assign("commit.index"),assign("reconcile.index")
        git("read-tree",head,env=isolated);Path(reconcile["GIT_INDEX_FILE"]).write_bytes(original)
        buffers={e["GIT_INDEX_FILE"]:bytearray() for e in (isolated,reconcile)}
        def stage(path,payload,env):
            oid=git("hash-object","-w","--stdin",data=payload.replace(b"\r\n",b"\n")).decode().strip()
            buffers[env["GIT_INDEX_FILE"]].extend(f"100644 {oid}\t{path}\0".encode("utf8"))
        for file in sorted(set(direct)):
            data=file.read_bytes();path=file.relative_to(ROOT).as_posix()
            if file.suffix==".json":json.loads(data.decode("utf-8-sig"))
            if file.suffix==".py":compile(data,str(file),"exec")
            for dst in (isolated,reconcile):stage(path,data,dst)
        for path in shared:
            data=(ROOT/path).read_bytes()
            stage(path,project(path,git("show",head+":"+path),data,episodes),isolated)
            stage(path,project(path,git("show",":"+path),data,episodes),reconcile)
        for dst in (isolated,reconcile):git("update-index","-z","--index-info",env=dst,data=bytes(buffers[dst["GIT_INDEX_FILE"]]))
        files=git("diff","--cached","--name-only",head,env=isolated).decode().splitlines()
        if not files:print("No changed course records");return
        git("diff","--cached","--check",env=isolated)
        subprocess.run(["node","scripts/media-policy.cjs"],cwd=ROOT,env=isolated,check=True)
        tree=git("write-tree",env=isolated).decode().strip()
        new=git("commit-tree",tree,"-p",head,data=(message+"\n").encode("utf8")).decode().strip()
        publish(real,Path(reconcile["GIT_INDEX_FILE"]).read_bytes(),original,ref,head,new)
        print(new,len(files),"course files")
    if push:subprocess.run(["git","push","origin",ref],cwd=ROOT,check=True)
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--message",required=True);ap.add_argument("--push",action="store_true");a=ap.parse_args();commit(a.message,a.push)
