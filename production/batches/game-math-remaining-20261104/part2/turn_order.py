"""Let a live earlier lecture acquire the next shared render slot."""
import psutil
from .edition import ROOT,read

def earlier_waiting_picture(slug,control):
    ids=control.get("groupReview20261106",{}).get("remaining",[])
    earlier=read(ROOT/control["batchPlan"])["items"]
    for ep in earlier:
        if ep["slug"]==slug:return None
        if ep["id"] not in ids:continue
        project=ROOT/"projects"/ep["slug"];plan=project/"planning/part2-picture-plan.json"
        if not plan.exists():continue
        picture=read(plan);local=project/"production/local"/picture.get("renderRevision","render-v2")
        queue=project/"production/unity-staging"/picture["preflightQueue"]
        candidates=[queue.parent/"progress.json",local/"progress.json"]
        if (local/"progress.json").exists() and read(local/"progress.json").get("status")=="body-captures-complete-compositing-and-QA-pending":
            candidates.append(local/"composite/worker.json")
        for path in candidates:
            if not path.exists():continue
            state=read(path)
            if state.get("status")!="waiting":continue
            try:
                proc=psutil.Process(state["pid"])
                if abs(proc.create_time()-state["createTime"])<.15:return ep["slug"]
            except (KeyError,psutil.NoSuchProcess,psutil.AccessDenied):continue
    return None
