"""Consolidate the inspected M22 files for local review without changing Studio."""
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from difflib import SequenceMatcher
from re import sub

from prepare import P, R, read, save, sha
from record import mark


def handoff():
    work = P / "production/local/render-v2"
    folder = R / "output" / (P.name + "-render-v2")
    docs = P / "production/meaning-guides"
    qa = read(work / "final-qa/report.json")
    mix = read(work / "final-mix-review/report.json")
    motion = read(work / "final-qa/game-motion.json")
    level = read(work / "final-qa/voice-preservation.json")
    cap_hash = qa["files"]["captioned"]["sha256"]
    assert all(x["masterSha256"] == cap_hash for x in (mix, motion, level))
    assert len(mix["paragraphs"]) == 36 and all(row["fullDecodeExitCode"] == 0 for row in qa["files"].values())
    assert qa["truePeakWithinLimit"] and qa["originalPcmUnchanged"] and len(qa["samples"]) == 108
    assert not qa["koSubtitles"]["issues"] and not qa["enSubtitles"]["issues"]
    assert {p.name for p in folder.glob("*.srt")} == {P.name + ".ko.srt", P.name + ".en.srt"}
    links = "http://127.0.0.1:9347/output/" + folder.name + "/"
    with urlopen(Request(links + P.name + ".captioned.mp4", headers={"Range": "bytes=0-63"}), timeout=6) as response:
        assert response.status == 206 and len(response.read()) == 64
    recordings = []
    for entry in mix["paragraphs"]:
        sid = entry["entry"]["scene_id"]
        original = read(P / ("production/local/audio-v4/review/paragraphs/" + sid + "-01.json"))
        norm = lambda s: sub(r"[^가-힣a-z0-9]", "", s.lower())
        delta = SequenceMatcher(None,norm(original["text"]),norm(entry["text"]),autojunk=False).ratio()
        recordings.append(dict(scene=sid,finalToScript=round(entry["coverage"],4),
                               finalToSourceRecognition=round(delta,4)))
    evidence = {
        "at": datetime.now(timezone.utc).isoformat(), "localReviewUrl": links + "index.html",
        "localFolder": str(folder), "masterSha256": cap_hash, "durationSeconds": qa["expectedFrames"] / 60,
        "files": {name: {"path": row["path"], "sha256": row["sha256"]}
                  for name,row in {**qa["files"], "ko": qa["koSubtitles"], "en": qa["enSubtitles"]}.items()},
        "picture": {"sampledFramesInspected": 108, "chapters": 36, "mobileWidth": 375, "gameFrames": motion["cuts"],
                    "checks": ["Elbow pose and the two candidate sleeve positions beside the blended vertex",
                               "Bind/current button positions with separate leaders",
                               "Moving T/B/N and decoded shader normal on the same surface",
                               "Corresponding model and UV triangles; full heading visible",
                               "Source cuts clear overlays, fixed captions below diagrams"]},
        "audio": {"finalLoudness": qa["actualMixLoudness"], "sourcePCMUnchanged": True,
                  "voicedWindows":sum(row["voicedWindows"] for row in level["scenes"]),
                  "suspectVideoSeconds":[t for row in level["scenes"] for t in row["inspectAtVideoSeconds"]],
                  "contentCheck":"At 00:20.8 in Mario gameplay the short low projection (-3.98 dB / 100 ms) overlaps game sound. The surrounding spoken clause is preserved in the encoded recognition. Flag for listening during user review.",
                  "pronunciationSpotChecks":["Tangent Frame (019): the final recognizer abbreviates 비탄젠트 as Bt. The source recognizer recovers 비탄젠트. Both authored captions and the object's B label were checked.",
                                             "Normal Decoding (020): ASR sometimes parses 8비트 색에는 as 8비트 3개는. Check the printed 8비트 색에는 and the spoken phrase together."],
                  "fullMixAsr": recordings, "continuousHumanListening": False},
        "nativePlayback": {"rangeStatus":206,"source":links+P.name+".captioned.mp4",
                           "actualPlayerLog": str(work/"final-qa/native-player-test.log")},
        "userReviewed": False, "publicUploadAuthorized": False}
    save(docs/"review-evidence.json", evidence)
    save(work/"content-review.json",dict(status="local-review-ready",annotationRevision="meaning-guides-v2",
         localFinalReviewReady=True,humanReview=False,masterSha256=cap_hash,
         evidence=str(docs/"review-evidence.json")))
    stage = "14분 21초 · 1080p60 · 자막판·무자막판·한영 SRT 검수 대기"
    mark(stage, review=True)
    for name in ("checkpoint","review-ledger"):
        path=P/("production/"+name+".json")
        doc=read(path)
        doc.update(localReviewReady=True,reviewUrl=evidence["localReviewUrl"],outputFiles=evidence["files"],
                   masterSha256=cap_hash,finalReviewEvidence=(docs/"review-evidence.json").relative_to(R).as_posix())
        if name=="review-ledger":
            doc["humanReview"]={"status":"로컬 검수 대기","fullListening":False}
        save(path,doc)
    batchfile=R/"production/batches/game-math-remaining-20261104/batch.json"
    batch=read(batchfile)
    row=next(i for i in batch["items"] if i["id"]=="M22")
    output_paths={key: item["path"] for key, item in evidence["files"].items()}
    output_paths["index"]=str(folder/"index.html")
    row.update(status="local-review-ready",localReviewReady=True,humanReviewed=False,
               outputCandidatesAvailable=True,outputFiles=output_paths,outputs=output_paths)
    row["evidence"]["finalVisualAndAudioEvidence"]=(docs/"review-evidence.json").relative_to(R).as_posix()
    m21=P.with_name("game-math-shading-lights")
    approved=read(m21/"publishing/youtube-upload-v7.json")
    m21files=read(m21/"production/teaching-v7/review-evidence.json")["files"]
    assert approved["userReview"]["approved"] and approved["video"]["sha256"]==m21files["captioned"]["sha256"]
    m21paths={k:x["path"] for k,x in m21files.items()}
    m21paths["index"]=str(Path(m21paths["captioned"]).parent/"index.html")
    prior=next(i for i in batch["items"] if i["id"]=="M21")
    prior.update(status="local-review-approved",localReviewReady=True,humanReviewed=True,
                 outputCandidatesAvailable=True,outputFiles=m21paths,outputs=m21paths)
    cp=m21/"production/local/render-v7/content-review.json"
    content=read(cp)
    content.update(status="user-reviewed-for-private-upload",localFinalReviewReady=True,humanReview=True,
                   platformReceipt=str(m21/"publishing/youtube-upload-v7.json"))
    save(cp,content)
    batch["updatedAt"]=evidence["at"]
    save(batchfile,batch)
    wp=R/"shared/publishing/video-worklist.json"
    worklist=read(wp)
    row=next(i for i in worklist["rows"] if i["id"]=="M22")
    row["notes"]="마리오·라이더스 리퍼블릭·둠 3 원속도 예시, 물체 위 수식 기호. " + evidence["localReviewUrl"]
    row["evidence"]=list(dict.fromkeys([*row["evidence"],(docs/"review-evidence.json").relative_to(R).as_posix()]))
    save(wp,worklist)
    print(evidence["localReviewUrl"])


if __name__=="__main__":
    handoff()
