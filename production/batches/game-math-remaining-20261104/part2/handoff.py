"""Package an internally inspected M23–M33 master for the user's single course review."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
from edition import ROOT,BATCH,read,save,sha,render_revision
from status import refresh

def finish(episode):
    row=next(r for r in read(BATCH/"batch.json")["items"][2:] if r["id"]==episode)
    p=ROOT/"projects"/row["slug"];work=p/"production/local"/render_revision(p)
    qa=read(work/"final-qa/report.json");d=read(work/"part2-delivery-evidence.json")
    notes=read(p/"production/part2-review/final-inspection.json")
    h=qa["files"]["captioned"]["sha256"];assert h==d["masterSha256"]==notes["masterSha256"]
    assert notes["inspectedScenes"]==len(read(p/"planning/scene-bindings.json")["scenes"])
    assert notes["mobileContactSheets"]==len(list((work/"final-qa").glob("contact-*.png")))==(3*notes["inspectedScenes"]+11)//12
    assert not notes["unresolvedProductionDefects"] and notes["actualGameCutsChecked"]==len(d["actualGameCuts"])
    assert notes["formulaFindings"] and notes["speechFindings"] and notes["captionFindings"]
    assert d["fullTranscriptReviewedByMachine"]==notes["inspectedScenes"]
    assert all(c["nativeSpeed"] and c["movingIntervals"]>0 for c in d["actualGameCuts"])
    paths={k:v["path"] for k,v in d["files"].items()}
    paths.update({k:v["path"] for k,v in d["subtitles"].items()})
    for key,path in paths.items():
        ref=d["files"].get(key) or d["subtitles"][key];assert sha(Path(path))==ref["sha256"]
    proof=dict(episode=episode,createdAt=datetime.now(timezone.utc).isoformat(),localFinalReviewReady=True,
        humanReview=False,masterSha256=h,files=paths,localReviewUrl=d["localReviewUrl"],frames=d["frames"],
        durationSeconds=d["duration"],actualGameCuts=d["actualGameCuts"],playerTests=d["playerTests"],
        speechFindings=notes["speechFindings"],formulaFindings=notes["formulaFindings"],
        approvalScope="Internal local delivery; grouped user review pending.")
    save(p/"production/part2-review/final-delivery.json",proof)
    save(work/"content-review.json",dict(status="local-review-ready",localFinalReviewReady=True,
        humanReview=False,masterSha256=h,evidence=str(p/"production/part2-review/final-delivery.json")))
    ledger=p/"production/review-ledger.json";record=read(ledger) if ledger.exists() else {}
    record["part2Delivery"]=proof;record["localReviewReady"]=True;record["humanReview"]={"status":"awaiting grouped user review"}
    save(ledger,record);refresh();print(d["localReviewUrl"])
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");finish(ap.parse_args().episode)
