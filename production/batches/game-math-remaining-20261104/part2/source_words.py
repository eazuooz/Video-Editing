from pathlib import Path
import argparse,subprocess,sys
from edition import ROOT,BATCH,read

ap=argparse.ArgumentParser();ap.add_argument("--project",required=True);ap.add_argument("--revision",required=True)
a=ap.parse_args();p=ROOT/"projects"/a.project; local=p/"production/local"; edition=read(p/"planning/part2-delivery-edition.json")
assert a.project in read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]["projectSlugs"] and a.revision==edition["audioRevision"]
target=local/a.revision
if not (target/"review/reused-pcm-evidence.json").is_file():
    previous=sorted([f for f in local.glob("audio-v*") if f!=target and (f/"review/source-full-asr.timestamps.json").is_file()],
                    key=lambda f:int(f.name.split("v")[-1]),reverse=True)
    if previous and edition["copiedTakes"]:
        subprocess.run([sys.executable,"-X","utf8",str(BATCH/"reuse-unchanged-word-evidence.py"),
                        "--project",a.project,"--source",previous[0].name,"--target",a.revision],check=True,cwd=ROOT)
subprocess.run([sys.executable,"-X","utf8",str(BATCH/"finish-word-review.py"),"--project",a.project,
                "--audio-revision",a.revision,"--group-device","cuda","--wait-hours","48"],check=True,cwd=ROOT)
