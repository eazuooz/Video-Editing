"""Close the finite local course and check the thirteen actual player destinations."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from edition import BATCH, ROOT, read, sha
from status import refresh, store

def inspect(row, ffprobe):
    ep=row["id"]
    assert row["localReviewReady"], ep
    project=ROOT/"projects"/row["slug"]
    files={key:Path(row["outputs"][key]) for key in ("clean","captioned","ko","en","index")}
    assert all(file.is_relative_to(ROOT/"output") and file.is_file() for file in files.values())
    master=files["captioned"]
    revision=master.parent.name.removeprefix(project.name+"-")
    review=read(project/"production/local"/revision/"content-review.json")
    digest=sha(master)
    assert review["localFinalReviewReady"] and review["masterSha256"]==digest,ep
    if ep not in ("M21","M22"):
        delivery=read(project/"production/part2-review/final-delivery.json")
        assert delivery["localFinalReviewReady"] and not delivery["humanReview"]
        assert delivery["masterSha256"]==digest and len(delivery["playerTests"])==2
    tracks={}
    for key in ("clean","captioned"):
        streams=json.loads(subprocess.check_output([str(ffprobe),"-v","error","-show_streams","-of","json",str(files[key])]))["streams"]
        picture=next(s for s in streams if s["codec_type"]=="video")
        assert any(s["codec_type"]=="audio" for s in streams)
        assert (picture["width"],picture["height"],picture["r_frame_rate"])==(1920,1080,"60/1"),(ep,key)
        tracks[key]=int(picture["nb_frames"])
        # Clean concatenations have millisecond rounding at cut boundaries. Check
        # adjacent actual presentation times rather than interpreting that rounding as a different frame rate.
        if picture["avg_frame_rate"]!="60/1":
            timestamps=subprocess.check_output([str(ffprobe),"-v","error","-select_streams","v",
                "-show_entries","packet=pts_time","-of","csv=p=0",str(files[key])])
            times=sorted(float(t) for t in timestamps.splitlines() if t.strip())
            assert len(times)==tracks[key] and all(abs(b-a-1/60)<.0011 for a,b in zip(times,times[1:])),(ep,key)
    assert tracks["clean"]==tracks["captioned"]
    url="http://127.0.0.1:9347/output/"+master.parent.name+"/"
    with urlopen(url+"index.html",timeout=15) as page:
        page_text=page.read().decode("utf8")
        assert page.status==200 and master.name in page_text
    for key in ("clean","captioned","ko","en"):
        with urlopen(Request(urljoin(url,files[key].name),headers={"Range":"bytes=0-63"}),timeout=15) as response:
            assert response.status==206 and len(response.read())==64,(ep,key)
    return dict(id=ep,title=row["title"],url=url+"index.html",frames=tracks["captioned"],
                seconds=tracks["captioned"]/60,masterSha256=digest,humanReview=row["humanReviewed"])

def complete():
    refresh()
    items=read(BATCH/"batch.json")["items"]
    assert [r["id"] for r in items]==[f"M{i}" for i in range(21,34)]
    source_queue=read(ROOT/"projects"/items[2]["slug"]/"production/local/render-v3/queue.json")
    ffprobe=Path(read(Path(source_queue["jobs"][0]))["ffmpeg"]).with_name("ffprobe.exe")
    packages=[inspect(row,ffprobe) for row in items]
    hub="http://127.0.0.1:9347/output/game-math-remaining-20261104/index.html"
    with urlopen(hub,timeout=15) as page:
        listing=page.read().decode("utf8")
        assert all(p["url"].split("/output/")[1] in listing for p in packages)
    now=datetime.now(timezone.utc).isoformat()
    results=dict(status="local-course-ready",checkedAt=now,reviewHub=hub,packages=packages,
                 outputFiles=4*len(packages),totalFrames=sum(p["frames"] for p in packages),
                 awaitingHumanReview=[p["id"] for p in packages if not p["humanReview"]])
    checkpoint=BATCH/"checkpoint.json";state=read(checkpoint)
    state.update(updatedAt=now,status="local-group-review-ready",currentEpisode=None,localReviewReady=True,
                 currentWorkingEpisodes=[],runningCostlyJobs=[],currentWork="M21–M33 grouped local review package verified",
                 nextAction="The user reviews the course locally.",groupDelivery=results)
    store(checkpoint,state)
    control=ROOT/"shared/publishing/video-production-control.json";rules=read(control)
    group=rules["explicitMathRemainingBatch20261104"]["groupReview20261106"]
    group.update(status="local-group-review-ready",checkedAt=now,verifiedOutputCount=52)
    store(control,rules)
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=="__main__":
    complete()
