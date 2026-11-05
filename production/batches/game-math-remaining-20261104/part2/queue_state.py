"""Select one ready local step from the eleven remaining lectures; never touch Studio."""
import argparse, json, subprocess, sys
from pathlib import Path
import psutil
from edition import BATCH,ROOT,read,save,sha

PROJECTS={x["id"]:x for x in read(BATCH/"batch.json")["items"][2:]}
STATE=BATCH/"local/part2-20261106"
QPY=ROOT/"qwen3-tts/.venv/Scripts/python.exe"
def live(record):
    try:return abs(psutil.Process(record["pid"]).create_time()-record["createTime"])<.15
    except (KeyError,psutil.NoSuchProcess,psutil.AccessDenied):return False
def snap(path):
    return read(path) if path.is_file() else {}
def instruction(name,tool,args,model=False):
    return {"step":name,"exe":str(QPY if model else sys.executable),
            "args":["-u","-X","utf8",str(BATCH/tool),*map(str,args)]}
def select(row):
    p=ROOT/"projects"/row["slug"]; s=p/"production/unity-staging"; local=p/"production/local"
    doc=p/"planning/part2-delivery-edition.json";slug=p.name
    if not doc.exists():return "편별 수정 작업 중",None
    edition=read(doc); rev=edition["audioRevision"];audio=local/rev
    output=local/"render-v2";queue=output/"queue.json";qa=output/"final-qa/report.json"
    if row.get("localReviewReady") and (output/"content-review.json").is_file():return "사용자 일괄 검수 대기",None
    if not (audio/"narration.wav").is_file():
        w=snap(audio/"finite-worker.json")
        if live(w):return "음성 생성 또는 GPU 순서 대기",None
        return "음성",instruction("voice","finish-selected-voice.py",["--project",slug,"--manifest",edition["manifest"],"--wait-hours","48"])
    if not (audio/"review/source-full-asr.timestamps.json").is_file():
        if live(snap(audio/"finite-word-review.json")):return "녹음된 음성의 발화 시점 확인 중",None
        return "발화 시점",instruction("source-words","part2/source_words.py",["--project",slug,"--revision",rev],True)
    aligned=local/rev.replace("audio-","edit-")/"word-aligned-timeline.json"
    if not aligned.exists() or read(aligned).get("bindingsSha256")!=sha(p/"planning/scene-bindings.json"):
        return "자막 정렬",instruction("align","align-module-speech.py",["--project",slug,"--audio-revision",rev])
    correction=snap(p/"production/part2-review/targeted-recording.json")
    if correction.get("sourceRevision")==rev:
        assert correction["episode"]==row["id"] and correction["approvedScope"]=="local grouped course production"
        return "실제 녹음에서 확인한 문장 교정",instruction("retake","part2/edition.py",[row["id"],correction["targetRevision"],"--retakes"])
    flags=read(aligned)["flags"]
    if flags:return "확인할 대사·자막 시점 "+str(len(flags))+"건",None
    if not (p/"planning/part2-picture-plan.json").is_file():return "기호·화면 대조 중",None
    picture=read(p/"planning/part2-picture-plan.json")
    pq=s/picture["preflightQueue"];qs=read(pq)
    if snap(pq.parent/"progress.json").get("status")!="images-ready-for-internal-visual-QA":
        if live(snap(pq.parent/"progress.json")):return "Unity 시험 장면 제작 중",None
        return "Unity 시험 장면",instruction("preview","run-module-preflight.py",["--queue",pq,"--run","--wait-hours","48"])
    if not queue.is_file():
        return "본편 장면 준비",instruction("prepare","prepare-module-render.py",["--project",slug,"--audio-revision",rev,
            "--revision",output.name,"--sandbox",Path(qs["sandbox"]).name])
    if not (output/"composite/preflight.json").is_file():
        return "편집 사전 점검",instruction("compose-check","compose-module.py",["--queue",queue])
    if snap(output/"progress.json").get("status")!="body-captures-complete-compositing-and-QA-pending":
        if live(snap(output/"progress.json")):return "본편 Unity 렌더 중",None
        return "본편 Unity 렌더",instruction("capture","run-module-render.py",["--queue",queue,"--render","--wait-hours","48"])
    if snap(output/"composite/progress.json").get("status")!="encoded-internal-QA-pending":
        if live(snap(output/"composite/worker.json")):return "두 마스터 인코딩 중",None
        return "마스터 인코딩",instruction("encode","compose-module.py",["--queue",queue,"--render","--wait-hours","48"])
    if not qa.is_file():return "영상·자막 검사",instruction("media-qa","verify-module-media.py",["--queue",queue,"--output",ROOT/"output"/(slug+"-"+output.name)])
    if not (output/"final-mix-review/report.json").is_file():
        if live(snap(output/"final-mix-review/worker.json")):return "최종 음성 대조 중",None
        return "최종 음성 대조",instruction("mix-qa","review-final-mix.py",["--queue",queue,"--device","cuda","--wait-hours","48"],True)
    if not (output/"part2-delivery-evidence.json").exists():
        return "재생·게임 장면 점검",instruction("playback-qa","part2/check_delivery.py",[row["id"]],True)
    return "4파일 생성 · 화면과 음성 직접 검수 대기",None

def cycle():
    auth=read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]
    assert auth["productionAllowedNow"] and auth["advanceWithinExactBatch"] and not auth["upload"]
    assert list(PROJECTS)==[f"M{i}" for i in range(23,34)]
    statuses={};options=[]
    for ep,row in PROJECTS.items():
        assert row["slug"] in auth["projectSlugs"]
        try:
            state,cmd=select(row)
        except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
            # A partial file from one renderer must not stall ten other lectures.
            statuses[ep]="자료 확인 필요 · "+type(exc).__name__
            save(STATE/(ep+"-selection-error.json"), {"episode":ep,"type":type(exc).__name__,"detail":str(exc)})
            continue
        statuses[ep]=state
        if cmd:
            lane=snap(STATE/"lanes"/(ep+".json"))
            if lane.get("active") and live(lane):continue
            fail=STATE/(ep+"-"+cmd["step"]+"-error.json")
            if fail.is_file():statuses[ep]="점검 필요 · "+cmd["step"];continue
            options.append(dict(episode=ep,**cmd))
    # Prefer finishing a render whose speech is ready to admitting a new voice.
    order=["playback-qa","media-qa","mix-qa","encode","capture","compose-check","prepare","preview","retake","align","source-words","voice"]
    options.sort(key=lambda row:order.index(row["step"]))
    return dict(statuses=statuses,action=options[0] if options else None,
                candidateBatchDone=all(s.startswith(("4파일 생성","사용자 일괄")) for s in statuses.values()))
if __name__=="__main__":
    # PowerShell's native pipeline may use the host code page on Windows.
    result=cycle()
    if all((ROOT/"projects"/r["slug"]/"planning/part2-picture-plan.json").exists() for r in PROJECTS.values()):
        old=snap(STATE/"progress.json")
        if result["statuses"]!=old.get("statuses"):
            subprocess.run([sys.executable,"-X","utf8",str(Path(__file__).with_name("status.py"))],
                           check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
    print(json.dumps(result,ensure_ascii=True))
