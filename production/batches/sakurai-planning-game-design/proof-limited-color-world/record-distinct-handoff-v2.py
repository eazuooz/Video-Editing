"""Advance only the limited-color-world preflight after an actual check."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
now = datetime.now(timezone.utc).isoformat()
queue_path = ROOT / "production/batches/sakurai-planning-game-design/queue.json"
queue_bytes = queue_path.read_bytes()
queue = json.loads(queue_bytes.decode("utf-8-sig"))
items = queue.get("videos", queue.get("items"))
assert items is not None
item = next(x for x in items if x["slug"] == "limited-color-world")
assert item["status"] == "in-progress"
assert not any(item["checkpoints"].values()) and item["videoId"] is None
other_items = [x for x in items if x["slug"] != "limited-color-world"]
before_others = json.dumps(other_items, ensure_ascii=False, sort_keys=True)

check = subprocess.run(["node", "scripts/review-video-duplicates.cjs", "limited-color-world", "--check"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
assert check.returncode == 0, check.stdout + check.stderr
report_path = ROOT / "production/batches/sakurai-planning-game-design/preflight/limited-color-world.json"
report = json.loads(report_path.read_text(encoding="utf-8-sig"))
assert report["verdict"] == "distinct"
assert report["inputsDigest"] == "64ffbe164be35b2aab8b5dc6659580b6b5c2d026c4f47eb3ea7caea14723c482"
review_path = PROOF / "content-studio-direct-review-v2.json"
review = json.loads(review_path.read_text(encoding="utf-8"))
assert len(review["relevantFullBodyReviews"]) == 11 and len(review["currentStudioReviews"]) == 7
source_path = PROOF / "source-visual-concept-direct-review-v2.json"
source = json.loads(source_path.read_text(encoding="utf-8"))
assert source["sourceConceptResearchApproved"] and not source["lectureFootageAdopted"]

handoff = json.loads((PROOF / "preflight-handoff-v1.json").read_text(encoding="utf-8"))
handoff["schemaVersion"] = 2
handoff["recordedAt"] = now
handoff["status"] = "current-distinct-official-source-candidate-review-pending"
handoff["source"]["sourceConceptResearchApproved"] = True
handoff["source"]["visualConceptReview"] = str(source_path.relative_to(ROOT)).replace("\\", "/")
handoff["source"]["visualConceptReviewSha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
handoff["source"]["unresolved"] = "Exact JA automatic wording and whole continuous playback remain unapproved; independent concepts are established by the full research transcript and twelve directly read teaching examples. No source lecture media is adopted."
handoff["duplicate"].update({"allRelevantFullKoEnClaimsRead": True,
    "currentStudioCompared": True, "distinctApproved": True, "currentDistinctCheckPassed": True,
    "contentStudioDirectReview": str(review_path.relative_to(ROOT)).replace("\\", "/"),
    "contentStudioReviewSha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
    "check": {"exitCode": check.returncode, "stdout": check.stdout, "stderr": check.stderr,
              "recordedAt": now}})
handoff["duplicate"]["likelyOverlapReviewNext"] = []
handoff["nextAction"] = "Secure sufficient concept-matched official or condition-compliant existing-game action footage, inspect normal-speed action, native PTS/in-out and caption/UI space, record candidate selection/rights/recent-use, then write independent KOEN overview and narration."
out = PROOF / "preflight-handoff-v2.json"
assert not out.exists()
out.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
item.update({"stage": handoff["status"], "preflightHandoff": str(out.relative_to(ROOT)).replace("\\", "/"),
             "sourceConceptResearchApproved": True, "duplicateReviewApproved": True,
             "duplicateReview": "production/batches/sakurai-planning-game-design/preflight/limited-color-world.json",
             "duplicateInventoryDigest": report["inputsDigest"], "currentJob": None})
queue["updatedAt"] = now
assert json.dumps([x for x in items if x["slug"] != "limited-color-world"], ensure_ascii=False, sort_keys=True) == before_others
assert queue_path.read_bytes() == queue_bytes, "Concurrent queue change; preserve it and reconcile explicitly"
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"handoff": str(out.relative_to(ROOT)).replace("\\", "/"), "distinctCheckExit": check.returncode,
                  "stage": item["stage"], "allProductionCheckpointsFalse": not any(item["checkpoints"].values()),
                  "actualId": item["videoId"], "foreignItemsPreserved": True}, ensure_ascii=False))
