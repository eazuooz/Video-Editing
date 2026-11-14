"""A factual local revision table. Encoding is separate from internal/user review."""
import html
import psutil
from pathlib import Path
from datetime import datetime,timezone
from inventory import HERE,ROOT,read,save

START="<!-- MATH-TEACHING-SYNC-20261115-START -->"
END="<!-- MATH-TEACHING-SYNC-20261115-END -->"


def review_index(row,item):
    """A playable local master with direct navigation to the revised passages."""
    from workings import WORKINGS
    folder=ROOT/"output"/(item["slug"]+"-teaching-sync-v2")
    moments=[]
    for scene in item['scenes']:
        recipe=WORKINGS.get(item['id'],{}).get(scene['scene'])
        if recipe:moments.append((scene['start'],recipe['purpose']))
    gameplan=read(HERE/'game-additions.json')['additions']
    for g in gameplan:
        if g['episode']==item['id']:moments.append((g['start'],g['label']))
    buttons=[]
    for t,label in sorted(moments):
        stamp=f'{int(t)//60:02}:{int(t)%60:02}'
        buttons.append(f'<li><button data-time="{t:.4f}">{stamp} · {html.escape(label)}</button></li>')
    credit='<p><a href="supplemental-credits.txt">추가 게임 녹화 출처 · 설명문 반영용</a></p>' if (folder/'supplemental-credits.txt').exists() else ''
    slug=item['slug']
    text=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{row['id']} {html.escape(row['title'])} · 수정 검수본</title><style>
body{{background:#080808;color:#fff;font:18px/1.65 system-ui;max-width:1200px;margin:auto;padding:24px}}h1,h2{{color:#e8cf83}}video{{width:100%}}a,button{{color:#73c7c2}}button{{font:inherit;border:0;border-bottom:1px solid #444;background:transparent;text-align:left;padding:9px;cursor:pointer}}ul{{padding-left:22px}}small{{color:#bbb}}
</style><h1>{row['id']} · {html.escape(row['title'])}</h1><p>1920×1080 · 60fps · 자체 검사 완료 / 사용자 검수 대기</p>
<video id="master" controls playsinline preload="metadata" src="{slug}.captioned.mp4"></video>
<p><a href="{slug}.captioned.mp4">자막 영상 MP4</a> · <a href="{slug}.clean.mp4">Clean MP4</a> · <a href="{slug}.ko.srt">한국어 SRT</a> · <a href="{slug}.en.srt">영어 SRT</a></p>
<p>기존 내레이션·학습 순서를 유지하고, 대사에 맞춘 수식 전개·입력값 설명과 게임 비교 화면을 보충했습니다.</p>
<h2>수정한 부분 바로 보기</h2><ul>{''.join(buttons)}</ul>{credit}
<small>전체 시청·청취와 사용자 승인은 아직 기록되지 않았습니다. 단계 검사 근거는 통합 검수표에서 별도로 관리합니다.</small>
<p><a href="../game-math-teaching-sync-20261115/index.html">13편 통합 검수표</a></p><script>
document.querySelectorAll('[data-time]').forEach(b=>b.addEventListener('click',()=>{{const v=document.getElementById('master');v.currentTime=Number(b.dataset.time);v.play();v.scrollIntoView({{behavior:'smooth',block:'center'}});}}));
</script></html>'''
    (folder/'index.html').write_text(text,encoding='utf8')


def update():
    from workings import WORKINGS
    plan=read(HERE/"plan.json");inventory=read(HERE/"inventory.json")["episodes"]
    titles={x["id"]:x["title"] for x in read(HERE.parent/"batch.json")["items"]}
    corrections=read(HERE/"pending-encoded-corrections.json") if (HERE/"pending-encoded-corrections.json").exists() else {}
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
        if item["id"] in corrections.get("episodes",{}) and corrections["episodes"][item["id"]].get("status")!="resolved":
            ready=False
        state="사용자 검수 대기" if ready else {"rendering-clean":"Clean 렌더 중","rendering-captioned":"자막본 렌더 중","encoded-QA-pending":"인코딩 완료 · 내부 검수 중"}.get(worker.get("status"),"화면·계산 보충 작성 완료 / 렌더 대기")
        rows.append(dict(id=item["id"],title=titles[item["id"]],slug=item["slug"],status=state,
            encoded=bool(encoded),technicalQa=tech.get("status") if tech else "pending",
            visualQa=visual.get("status") if visual else "pending",humanReviewed=False,
            audioQa="unchanged-bitstream" if tech and tech.get("unchangedAudioBitstream") else mix.get("status") if mix else "pending",
            finalReviewReady=ready,output=(ROOT/"output"/(item["slug"]+"-teaching-sync-v2")).as_posix() if encoded else None))
    data=dict(updatedAt=datetime.now(timezone.utc).isoformat(),scope="M21–M33 only",rows=rows,
        readyCount=sum(x["finalReviewReady"] for x in rows),upload=False,automation=False)
    save(HERE/"progress.json",data)
    # Update only this explicitly selected revision, preserving platform states
    # and unrelated projects in the shared checkpoint.
    plan['status']='local-user-review-pending' if data['readyCount']==13 else 'serialized-render-and-QA'
    for episode in plan['episodes']:
        row=next(r for r in rows if r['id']==episode['id'])
        episode.update(status=row['status'],review=dict(technical=row['technicalQa'],
            currentEncodedPictures=row['visualQa'],human='pending'),output=row['output'])
        episode['calculationScenes']=list(WORKINGS.get(episode['id'],{}))
        episode['calculationSceneCount']=len(episode['calculationScenes'])
    save(HERE/'plan.json',plan)
    checkpoint_path=HERE.parent/'checkpoint.json'
    checkpoint=read(checkpoint_path)
    leaf=checkpoint['teachingSyncRevision20261115']
    lease_path=ROOT/'shared/output/GPU_HANDOFF.json'
    lease=read(lease_path) if lease_path.exists() else {}
    active=lease if lease.get('pid') and psutil.pid_exists(lease['pid']) and any(
        str(lease.get('owner','')).startswith(item['slug']) for item in inventory) else None
    current=next((item['id'] for item in inventory if active and active.get('owner','').startswith(item['slug'])),None)
    leaf.update(status=plan['status'],completed=[r['id'] for r in rows if r['finalReviewReady']],
        completedTechnical=[r['id'] for r in rows if r['technicalQa']=='pass'],
        localReadyCount=data['readyCount'],humanReviewed=False,
        calculationSceneCount=sum(len(v) for v in WORKINGS.values()),
        currentEpisode=current,currentStage=active.get('owner') if active else 'local-picture-review',
        runningCostlyJobs=[active] if active else [],
        pendingPictureCorrections=[eid for eid,c in corrections.get('episodes',{}).items() if c.get('status')!='resolved'],
        nextAction='Finish remaining actual encoded picture review and guarded jobs; deliver all thirteen locally. No platform mutations.')
    save(checkpoint_path,checkpoint)
    control_path=ROOT/'shared/publishing/video-production-control.json'
    control=read(control_path)
    current_leaf=control['explicitMathRemainingBatch20261104']['teachingSyncRevision20261115']
    current_leaf.update(status=plan['status'],currentEpisode=current,
        localReadyCount=data['readyCount'],calculationSceneCount=sum(len(v) for v in WORKINGS.values()),
        humanReviewed=False,progress=(HERE/'progress.json').relative_to(ROOT).as_posix())
    save(control_path,control)
    batch_path=HERE.parent/'batch.json';batch=read(batch_path)
    batch['teachingSyncRevision20261115'].update(status=plan['status'],
        localReadyCount=data['readyCount'],humanReviewed=False,
        progress=(HERE/'progress.json').relative_to(ROOT).as_posix())
    save(batch_path,batch)
    for row,item in zip(rows,inventory):
        if row['finalReviewReady']:review_index(row,item)
        ledger_path=ROOT/'projects'/item['slug']/'production/review-ledger.json'
        ledger=read(ledger_path)
        folder=ROOT/'projects'/item['slug']/'production/local/teaching-sync-v2'
        ledger['teachingSyncRevision20261115']=dict(status=row['status'],
            finalReviewReady=row['finalReviewReady'],humanReviewed=False,
            actualHumanViewing=False,actualHumanListening=False,
            output=row['output'],evidence={name:str((folder/name).relative_to(ROOT)).replace('\\','/')
                for name in ('encoded.json','technical-qa.json','visual-review.json','mix-review.json') if (folder/name).exists()},
            scope='Additive lesson visuals and matched gameplay; original order and voice retained. Local review only.')
        save(ledger_path,ledger)
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
        body.append(f'<tr><td>{r["id"]}<br>{html.escape(r["title"])}</td><td>{html.escape(r["status"])}</td><td>{r["technicalQa"]}</td><td>{r["visualQa"]}</td><td>검수 전</td><td>{link}</td></tr>')
    (out/"index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임수학 13편 수정 검수표</title><style>body{max-width:1200px;padding:24px;margin:auto;background:#080808;color:#fff;font:18px/1.7 system-ui}h1{color:#e8cf83}a{color:#73c7c2}table{border-collapse:collapse;width:100%}td,th{padding:12px;text-align:left;border-bottom:1px solid #444}</style><h1>M21–M33 계산·게임 예시 보충 검수표</h1><p>기존 완성본은 보존합니다. 새 영상은 내부 검수 완료 후 사용자 검수 대기로 표시합니다. 업로드·공개·예약은 진행하지 않습니다.</p><table><tr><th>편</th><th>현재 작업</th><th>파일 검사</th><th>화면 검수</th><th>사용자 검수</th><th>새 영상</th></tr>'+''.join(body)+'</table>',encoding="utf8")
    return data


if __name__=="__main__":
    for row in update()["rows"]:print(row["id"],row["status"])
