"""Record directly read source concepts and relevant content; no media adoption."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
NOW = datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(path):
    p = ROOT / path
    return {"path": path, "sha256": sha(p), "bytes": p.stat().st_size}


def save(name, data):
    p = PROOF / name
    if p.exists():
        raise RuntimeError(f"Preserve existing record: {p}")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


report_path = ROOT / "production/batches/sakurai-planning-game-design/preflight/limited-color-world.json"
report = json.loads(report_path.read_text(encoding="utf-8-sig"))
assert report["inputsDigest"] == "64ffbe164be35b2aab8b5dc6659580b6b5c2d026c4f47eb3ea7caea14723c482"
for row in report["inputFiles"]:
    actual = hashlib.sha256((ROOT / row["path"]).read_bytes().decode("utf-8").encode("utf-8")).hexdigest()
    assert actual == row["sha256"], row["path"]

source_observations = [
    (29, "Color alone excludes some players; Meteos tiles also have distinct internal artwork."),
    (39, "Planet-specific artwork varies, so one uniform color scheme cannot be assumed across all worlds."),
    (54, "The visible teaching text says a filter was used to check the game. This observation does not establish a specific software tool name."),
    (69, "Visible label: Color Blindness - Protanopia-type. The table shows a preview example, not every person's perception."),
    (79, "Visible label: Deuteranopia-type. Some colors in the example look similar; shape/pattern information remains visible."),
    (84, "Visible English text calls for significant differences in brightness. This resolves the concept of lightness separation, without approving exact JA automatic wording."),
    (89, "Dark Meteos may blend into the background; light boundaries and lighter tiles remain distinct in the pictured world."),
    (94, "Visible English text identifies some designs as needing follow-up work; it does not assert every block has been fixed."),
    (114, "Power-ups and interactable objects can be difficult to tell apart; the concern extends beyond puzzle tiles."),
    (139, "Smash Ultimate lava-stage color/grayscale comparison illustrates checking foreground/background art hierarchy."),
    (149, "Smash Ultimate arena color/grayscale comparison asks which visual aspects stand out, rather than prescribing monochrome for every final game."),
    (159, "Visible teaching text proposes flipping artwork to find inconsistencies. This is an artwork inspection example, not gameplay footage adoption."),
]
source_record = {
    "schemaVersion": 2, "slug": "limited-color-world", "recordedAt": NOW,
    "sourceId": "obnjR8KJ9nk", "officialChannel": "Masahiro Sakurai on Creating Games",
    "transcript": evidence("production/batches/sakurai-planning-game-design/proof-limited-color-world/source-obnjR8KJ9nk-ja-auto-v1.txt"),
    "fullExportedAutomaticJaDirectlyRead": True,
    "observations": [{"browserSeekSeconds": seconds, "directObservation": note,
                      "screenshot": evidence(f"production/batches/sakurai-planning-game-design/proof-limited-color-world/source-{seconds}-v1.png")}
                     for seconds, note in source_observations],
    "sourceConceptResearchApproved": True,
    "approvalScope": "Independent teaching about hue-independent identifying information, brightness/shape/pattern support, dark-background separation and grayscale art inspection, established by the full research transcript plus directly viewed teaching examples.",
    "exactAuthorJaWordingApproved": False, "fullContinuousPlaybackReviewed": False,
    "sourceAudioListenedInFull": False, "browserSecondsAreNativePts": False,
    "allInterveningSourceFramesReviewed": False, "lectureMediaReused": False,
    "lectureFootageAdopted": False, "transcriptAndResearchScreenshotsGitEligible": False,
    "uncertainAutomaticTermsNotRepeatedAsQuotes": ["使用部分", "えの方", "タイス色", "1型四角", "禁じし", "引き格多様性", "金whom", "絶賛グ"],
    "playback": {"muted": True, "normalSpeed": 1, "selectedSeekSamplesOnly": True},
}
source_review_path = PROOF / "source-visual-concept-direct-review-v2.json"
if source_review_path.exists():
    preserved = json.loads(source_review_path.read_text(encoding="utf-8"))
    comparable_preserved = dict(preserved)
    comparable_current = dict(source_record)
    comparable_preserved.pop("recordedAt")
    comparable_current.pop("recordedAt")
    assert comparable_preserved == comparable_current
else:
    save("source-visual-concept-direct-review-v2.json", source_record)

comparison = {
    "picking-sides": "Spectator identity, motivation, risk and result. Its single color/shape identity section is supporting evidence; it does not examine perception previews, value separation or color-independent essential game information as the central question.",
    "responsive-game-feedback": "Input received, refusal reason, confirmation, pending and completion. Color plus words supports state feedback; the current and historical full KOEN scripts do not cover the new video's color-perception inspection and background/art hierarchy question.",
    "small-window-game-design": "Aspect ratio, FOV, angular target size, screen occupancy and occlusion. Visibility is shared vocabulary, while the viewer problem and comparisons differ.",
    "let-them-play": "Time to first playable action, onboarding, opening promises and immediate learning. It does not teach perception previews or hue-independent signals.",
    "player-customization": "Select, compare, test and express identity through appearance. Color selection and preview are player choice, rather than preserving essential information when colors are difficult to distinguish.",
    "character-parameters": "Common ability baseline, unique fire/water/smoke rules, conditions, targets and balance. Readable ability effects support understanding character choices; color-perception/art inspection is not its lesson.",
    "game-lighting-history-01": "Stored/recomputed light and visibility from DOOM palettes to lightmaps, shadows, forward/deferred and SSAO. Sector brightness/palette calculations differ from information-design checks for indistinguishable hues.",
    "game-lighting-history-02": "Stored indirect light, AA, linear/sRGB data, material/reflection/refraction and volumes. Its linear-light numerical encoding lesson is not the same as perceptual legibility or redundancy of game cues.",
    "game-lighting-history-03": "Scene representations, BVH, ray samples, temporal reuse, DDGI/ReSTIR, geometry and light caches. No duplicate color-accessibility claim sequence.",
    "game-lighting-history-04": "Virtual shadow pages, reconstruction, visibility buffers, path tracing, exposure, tone mapping and frame inspection. Final pixel calculation and postprocessing are distinct from preserving readable essential signals across color perceptions.",
    "game-math-rendering-light": "Surface visibility, BRDF/BSDF, radiometric units and rendering-equation calculations. Color representation/brightness is mathematical input/output, rather than gameplay communication under reduced color differentiation.",
}
reviewed = []
for slug, reason in comparison.items():
    base = f"projects/{slug}"
    paths = [f"{base}/project.json", f"{base}/planning/outline.md",
             f"{base}/script/narration.ko.json", f"{base}/script/narration.en.json"]
    if slug == "responsive-game-feedback":
        paths += [f"{base}/production/final-v2/script.ko.json", f"{base}/production/final-v2/script.en.json"]
    if slug == "player-customization":
        # Current scripts were both read in full; legacy files are inventory inputs, not this approval's direct-body scope.
        manifest = json.loads((ROOT / paths[0]).read_text(encoding="utf-8-sig"))
        paths = paths[:2] + [manifest["paths"]["script"], manifest["paths"]["scriptEnglish"]]
    reviewed.append({"slug": slug, "fullCurrentKoEnAndOutlineDirectlyRead": True,
                     "fullManifestDirectlyRead": True, "files": [evidence(p) for p in dict.fromkeys(paths)],
                     "comparison": reason})

studio = [
    ("picking-sides", "xtUVcAHtQzg", "공개"),
    ("responsive-game-feedback", "BYk6cLsO9Mc", "공개"),
    ("small-window-game-design", "84xPzR2ww88", "공개"),
    ("let-them-play", "IHKv1p_aSJ4", "공개"),
    ("player-customization", "lf765yYhPdM", "예약됨"),
    ("character-parameters", "nic5Sp6dylQ", "예약됨"),
    ("game-math-rendering-light", "-19ngvEqhao", "예약됨"),
]
studio_rows = []
for slug, video_id, status in studio:
    path = f"production/batches/sakurai-planning-game-design/proof-limited-color-world/studio-{slug}-current-v2.ax.txt"
    ax = (ROOT / path).read_text(encoding="utf-8")
    assert video_id in ax and "고화질 완료" in ax and "표준 화질 완료" in ax and status in ax
    assert "text entry area" in ax and "시청자에게 동영상에 대해 설명해 주세요" in ax
    studio_rows.append({"slug": slug, "actualVideoId": video_id, "url": f"https://studio.youtube.com/video/{video_id}/edit",
                        "actualCurrentStatusObserved": status, "completeTitleAndDescriptionDirectlyRead": True,
                        "sdHdObserved": True, "ax": evidence(path), "metadataModified": False})

save("content-studio-direct-review-v2.json", {
    "schemaVersion": 2, "slug": "limited-color-world", "recordedAt": NOW,
    "sourceConceptReview": "production/batches/sakurai-planning-game-design/proof-limited-color-world/source-visual-concept-direct-review-v2.json",
    "candidateViewerQuestion": "When colors are difficult to distinguish, can the player still identify the object, its role and what needs attention using brightness, boundaries, shape or pattern?",
    "independentPlannedClaimScope": ["Do not place essential meaning in hue alone", "Use meaningful form/pattern/brightness cues", "Keep dark objects separate from their background", "Inspect attention hierarchy in grayscale and color-perception previews; validate with actual players"],
    "fullInventoryTitleAndChapterReview": {"projectCount": 54, "inputCount": 381, "digest": report["inputsDigest"],
        "allKoEnTitlesAndChapterTitlesDirectlyRead": True, "all381FileBodiesDirectlyRead": False,
        "recheckedAllInputHashes": True, "changedSinceInitial54": []},
    "relevantFullBodyReviews": reviewed, "currentStudioReviews": studio_rows,
    "currentFutureInventory": evidence("production/batches/sakurai-planning-game-design/proof-limited-color-world/current-scheduled-inventory-v2.ax.txt"),
    "lightingSeriesUploadIdsInCurrentInventory": [None, None, None, None],
    "lightingSeriesNote": "These four current manifests have no actual upload ID. Their full existing KOEN scripts, chapter plans and manifests were compared. No unobserved upload or full-channel absence is asserted.",
    "contentDecision": "distinct", "decisionNotBasedOnTitlesOrIdsOrEmptyExactMatches": True,
    "distinctCheckPerformedByThisRecorder": False, "footageBeforeDependentNarrationStillRequired": True,
    "newProjectScriptTtsMcOrFootageAdoption": False, "foreignFileOrPublishingChanges": 0,
    "researchProcessManipulation": 0, "newGitImages": 0,
})
print(json.dumps({"sourceConceptReview": "source-visual-concept-direct-review-v2.json", "fullRelatedReviews": len(reviewed),
                  "currentStudioReviews": len(studio_rows), "digest": report["inputsDigest"],
                  "distinctCheckStillRequired": True, "productionStarted": False}, ensure_ascii=False))
