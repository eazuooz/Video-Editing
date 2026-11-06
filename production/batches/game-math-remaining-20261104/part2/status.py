"""Update only the selected course rows using files actually produced on this machine."""
from pathlib import Path
from datetime import datetime,timezone
import argparse, json, os, re
from html import escape
from edition import ROOT,BATCH,read,render_revision
from queue_state import PROJECTS,select,snap

def atomic(path,payload):
    tmp=path.with_name(path.name+"."+str(os.getpid())+".tmp")
    tmp.write_text(payload,"utf8");os.replace(tmp,path)
def store(path,data):
    atomic(path,json.dumps(data,ensure_ascii=False,indent=2)+"\n")
def refresh():
    now=datetime.now(timezone.utc).isoformat()
    wp=ROOT/"shared/publishing/video-worklist.json"
    w=read(wp);rows={r["id"]:r for r in w["rows"]}
    bp=BATCH/"batch.json";b=read(bp)
    hub=ROOT/"output/game-math-remaining-20261104";hub.mkdir(exist_ok=True)
    html=[];md=[]
    for item in b["items"]:
        ep=item["id"];p=ROOT/"projects"/item["slug"];row=rows[ep]
        master=None; files=item.get("outputs",{})
        if ep in PROJECTS:
            try:state,_=select(item)
            except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
                state="자료 확인 필요 · "+type(exc).__name__
            doc=read(p/"planning/part2-delivery-edition.json")
            audio=p/"production/local"/doc["audioRevision"]
            wavecount=len(list((audio/"chunks").glob("*-scene.wav")))
            revision=render_revision(p)
            q=p/"production/local"/revision;rc=snap(q/"progress.json")
            picture=read(p/"planning/part2-picture-plan.json")
            preview=p/"production/unity-staging"/picture["preflightQueue"]
            prog=snap(preview.parent/"progress.json")
            qa=snap(q/"final-qa/report.json");content=snap(q/"content-review.json")
            dest=ROOT/"output"/(p.name+"-"+revision)
            files={suffix:str(dest/(p.name+"."+suffix+ext)) for suffix,ext in
                   [("clean",".mp4"),("captioned",".mp4"),("ko",".srt"),("en",".srt")]}
            allfiles=all(Path(v).is_file() for v in files.values()) and (dest/"index.html").is_file()
            ready=bool(allfiles and content.get("localFinalReviewReady") and qa.get("files",{}).get("captioned",{}).get("sha256")==content.get("masterSha256"))
            if allfiles: files["index"]=str(dest/"index.html")
            else: files={}
            state="로컬 일괄 검수 대기" if ready else {"음성":"녹음 대기","음성 생성 또는 GPU 순서 대기":"녹음 진행" if snap(audio/"finite-worker.json").get("status")=="synthesizing" else "녹음 장치 대기"}.get(state,state)
            stage=f"{state} · 음성 {wavecount}/{doc['sceneCount']}문단"
            correction=snap(p/"production/part2-review/final-picture-correction.json")
            if not ready and correction.get("renderRevision")==revision:
                stage="첫 출력 검수 후 화면 보완 · "+stage
            selected_games=[(s["id"],s["actualGamePart"]) for s in read(p/"planning/scene-bindings.json")["scenes"] if s.get("actualGamePart")]
            inserts=sum((p/"production/local/part2-game-inserts"/(sid+("-"+g["insertVersion"] if g.get("insertVersion") else ""))/"receipt.json").is_file() for sid,g in selected_games)
            if inserts:
                total=len(read(p/"planning/part2-picture-plan.json")["actualGameScenes"])
                stage+=f" · 게임 장면 {inserts}/{total}개 편집"
            if prog and not rc:stage+=f" · Unity 시험 장면 {len(prog.get('completed',[]))}개"
            prefix=snap(p/"production/local/preserved-prefix-v1/progress.json") if ep=="M23" else {}
            if prefix.get("completed") and not rc:stage+=f" · 본편 앞부분 {len(prefix['completed'])}장면 캡처"
            if rc:stage+=f" · 본편 장면 {len(rc.get('completed',[]))}개 렌더"
            item.update(status="local-review-ready" if ready else "active-production",localReviewReady=ready,
                        outputCandidatesAvailable=allfiles,outputs=files,humanReviewed=False)
            item["evidence"]["edition"]=(p/"planning/part2-delivery-edition.json").relative_to(ROOT).as_posix()
            item["evidence"]["picture"]=(p/"planning/part2-picture-plan.json").relative_to(ROOT).as_posix()
            row.update(productionStatus=stage,productionComplete=ready,localMasterAvailable=allfiles,
                       reviewStatus="사용자 일괄 검수 대기" if ready else "내부 제작 중",
                       notes=f"파트 2 일괄 검수 · 수식·그림 수정 {len(doc['changedScenes'])}문단 · "+stage)
            cp=p/"production/checkpoint.json";data=read(cp)
            data.update(stage=stage,updatedAt=now,localReviewReady=ready,outputsReady=allfiles,
                        groupReview={"edition":doc["audioRevision"],"narrationChunks":wavecount,
                                     "reusedTakes":len(doc["copiedTakes"]),"sceneCount":doc["sceneCount"],
                                     "gameInserts":inserts,
                                     "preservedPrefixScenes":len(prefix.get("completed",[])),
                                     "previewScenes":len(prog.get("completed",[])),"renderScenes":len(rc.get("completed",[])),
                                     "state":state,"localReviewIndex":files.get("index")})
            store(cp,data)
        if (ep not in PROJECTS or item["localReviewReady"]) and files.get("index") and Path(files["index"]).is_file():
            master="../"+Path(files["index"]).relative_to(ROOT/"output").as_posix()
        link=f'<a href="{escape(master)}">영상 보기</a>' if master else "제작 중"
        html.append(f'<tr><td>{ep}</td><th scope="row">{escape(item["title"])}</th><td>{escape(row["productionStatus"])}</td><td>{escape(row["reviewStatus"])}</td><td>{link}</td></tr>')
        md.append(f'| {ep} | {item["title"]} | {row["productionStatus"]} | {row["reviewStatus"]} | '+('확인 완료' if item["humanReviewed"] else ('검수 대기' if item["localReviewReady"] else '완성본 대기'))+' |')
    b["updatedAt"]=now;store(bp,b)
    latest=read(wp)
    for current in latest["rows"]:
        if current["id"] in PROJECTS:
            revised=rows[current["id"]]
            for key in ("productionStatus","productionComplete","localMasterAvailable","reviewStatus","notes"):
                current[key]=revised[key]
    store(wp,latest)
    atomic(BATCH/"progress.md","# 게임수학 파트 2 제작·검수표\n\nM23~M33의 사용자 검수는 한꺼번에 진행한다. M21과 M22는 기존 검수본으로 연결한다.\n\n| 편 | 강의 | 제작 단계 | 검수 | 사용자 확인 |\n|---|---|---|---|---|\n"+"\n".join(md)+"\n")
    workdoc=ROOT/"docs/VIDEO_WORKLIST.md";text=workdoc.read_text("utf-8-sig")
    for ep in PROJECTS:
        row=rows[ep];line=f'| {ep} | {row["title"]} | {row["productionStatus"]} | {row["reviewStatus"]} | {row["platformStatus"]} |'
        text=re.sub(r"^\| "+ep+r" \|.*$",lambda _:line,text,flags=re.M)
        text=re.sub(r"^\| "+ep+r" [^|]+ \|.*$",lambda _:"| "+ep+" "+row["title"]+" | "+row["notes"]+" |",text,flags=re.M)
    atomic(workdoc,text)
    top='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임수학 파트 2 검수</title>
<style>:root{color-scheme:dark}body{max-width:1080px;margin:auto;background:#111512;color:#f1f1eb;padding:clamp(12px,3vw,32px);font:16px/1.55 system-ui}h1{color:#e9ce83}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #47514b;text-align:left;padding:9px}a{color:#8ed6c7}section{overflow:auto}time{color:#bbb}</style><h1>게임수학 파트 2 검수</h1><p>영상이 준비되면 각 강의에서 자막판·무자막판과 한영 자막을 열 수 있습니다. <a href="gameplay.html">게임 예시 검토</a></p>'''
    atomic(hub/"index.html",top+f'<time>{escape(now)}</time><section><table><thead><tr><th>편</th><th>강의</th><th>제작</th><th>검수</th><th>파일</th></tr></thead><tbody>'+''.join(html)+'</tbody></table></section></html>')
    print("Updated selected local course table")
if __name__=="__main__":refresh()
