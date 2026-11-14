"""A factual local revision table. Encoding is separate from internal/user review."""
import html
from pathlib import Path
from datetime import datetime,timezone
from inventory import HERE,ROOT,read,save

START="<!-- MATH-TEACHING-SYNC-20261115-START -->"
END="<!-- MATH-TEACHING-SYNC-20261115-END -->"


def update():
    plan=read(HERE/"plan.json");inventory=read(HERE/"inventory.json")["episodes"]
    rows=[]
    for item in inventory:
        folder=ROOT/"projects"/item["slug"] / "production/local/teaching-sync-v2"
        worker=read(folder/"worker.json") if (folder/"worker.json").exists() else {}
        encoded=read(folder/"encoded.json") if (folder/"encoded.json").exists() else None
        tech=read(folder/"technical-qa.json") if (folder/"technical-qa.json").exists() else None
        visual=read(folder/"visual-review.json") if (folder/"visual-review.json").exists() else None
        mix=read(folder/"mix-review.json") if (folder/"mix-review.json").exists() else None
        audio_ok=bool(tech and (tech.get("unchangedAudioBitstream") or (mix and mix.get("status") in ("pass","reused"))))
        ready=bool(encoded and tech and tech.get("status")=="pass" and visual and visual.get("status")=="pass" and audio_ok)
        state="사용자 검수 대기" if ready else {"rendering-clean":"Clean 렌더 중","rendering-captioned":"자막본 렌더 중","encoded-QA-pending":"인코딩 완료 · 내부 검수 중"}.get(worker.get("status"),"화면·계산 보충 작성 완료 / 렌더 대기")
        rows.append(dict(id=item["id"],slug=item["slug"],status=state,
            encoded=bool(encoded),technicalQa=tech.get("status") if tech else "pending",
            visualQa=visual.get("status") if visual else "pending",humanReviewed=False,
            audioQa="unchanged-bitstream" if tech and tech.get("unchangedAudioBitstream") else mix.get("status") if mix else "pending",
            finalReviewReady=ready,output=(ROOT/"output"/(item["slug"]+"-teaching-sync-v2")).as_posix() if encoded else None))
    data=dict(updatedAt=datetime.now(timezone.utc).isoformat(),scope="M21–M33 only",rows=rows,
        readyCount=sum(x["finalReviewReady"] for x in rows),upload=False,automation=False)
    save(HERE/"progress.json",data)
    worklist_path=ROOT/"shared/publishing/video-worklist.json"
    worklist=read(worklist_path)
    worklist["mathRemainingTeachingSync20261115"]=dict(plan=(HERE/"plan.json").relative_to(ROOT).as_posix(),
        reviewHub="output/game-math-teaching-sync-20261115/index.html",readyCount=data["readyCount"],
        encodedCount=sum(r["encoded"] for r in rows),humanReviewedCount=0,scope=[r["id"] for r in rows])
    byid={r["id"]:r for r in rows}
    for item in worklist["rows"]:
        if item["id"] in byid:
            item["teachingSync20261115"]=byid[item["id"]]
    save(worklist_path,worklist)
    doc=ROOT/"docs/VIDEO_WORKLIST.md";text=doc.read_text(encoding="utf-8-sig")
    block=START+"\n\n## M21–M33 계산·게임 예시 보충 수정 (2026-11-15)\n\n기존 완성본·게시 이력은 보존하고, 새 수정본은 아래 상태로 구분한다. 사용자 검수 전 업로드하지 않는다.\n\n| 편 | 새 수정본 진행 | 파일 검사 | 화면 검수 | 사용자 검수 |\n|---|---|---|---|---|\n"
    block+="\n".join(f'| {r["id"]} | {r["status"]} | {r["technicalQa"]} | {r["visualQa"]} | 검수 전 |' for r in rows)+"\n\n"+END
    if START in text:text=text[:text.index(START)]+block+text[text.index(END)+len(END):]
    else:text=text.rstrip()+"\n\n"+block+"\n"
    doc.write_text(text,encoding="utf8")
    out=ROOT/"output/game-math-teaching-sync-20261115";out.mkdir(exist_ok=True)
    body=[]
    for r in rows:
        link=f'<a href="../{r["slug"]}-teaching-sync-v2/index.html">영상 폴더</a>' if r["encoded"] else "제작 중"
        body.append(f'<tr><td>{r["id"]}</td><td>{html.escape(r["status"])}</td><td>{r["technicalQa"]}</td><td>{r["visualQa"]}</td><td>검수 전</td><td>{link}</td></tr>')
    (out/"index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임수학 13편 수정 검수표</title><style>body{max-width:1200px;padding:24px;margin:auto;background:#080808;color:#fff;font:18px/1.7 system-ui}h1{color:#e8cf83}a{color:#73c7c2}table{border-collapse:collapse;width:100%}td,th{padding:12px;text-align:left;border-bottom:1px solid #444}</style><h1>M21–M33 계산·게임 예시 보충 검수표</h1><p>기존 완성본은 보존합니다. 새 영상은 내부 검수 완료 후 사용자 검수 대기로 표시합니다. 업로드·공개·예약은 진행하지 않습니다.</p><table><tr><th>편</th><th>현재 작업</th><th>파일 검사</th><th>화면 검수</th><th>사용자 검수</th><th>새 영상</th></tr>'+''.join(body)+'</table>',encoding="utf8")
    return data


if __name__=="__main__":
    for row in update()["rows"]:print(row["id"],row["status"])
