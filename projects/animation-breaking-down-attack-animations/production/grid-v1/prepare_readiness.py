"""Build only A03's isolated, non-executing readiness scaffold.

No media, Unity, TTS, platform, shared worklist or Git operations. Inputs are
frozen batch scripts; copied pipeline helpers retain an empty execution grant.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = HERE.parents[3]
SLUG = PROJECT.name
DATE = "2026-11-04"
BATCH = "animation-18-20261031"
SCRIPT = PROJECT / "script/grid-v1"
PLANNING = PROJECT / "planning"
INPUT = ROOT / f"production/batches/{BATCH}/scripts/A03"
RESEARCH = ROOT / f"production/batches/{BATCH}/research/A03"
EXPECTED = {
    "narration.ko.json": "62ccc70748c3a9a33c7172a8cbb3435f524820e9d87da41a277d1fe4d0d13678",
    "narration.en.json": "09fcdbf531bea70491f3ccc64fb027ec719bbe841b8dc2e7c0201859879fa3c1",
    "caption-units.json": "dd36d59a21e03e9dc6817f2b5e36a29612fbbd4e5c550d90151d0199f6375487",
}


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return Path(p).relative_to(ROOT).as_posix()


def artifact(p):
    return {"path": rel(p), "sha256": sha(p), "bytes": Path(p).stat().st_size}


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized(s):
    return re.sub(r"\s+", "", s)


def unity_asset(key, product_id, name, url, teaching_role):
    asset_root = ROOT / "unity/VideoEditing"
    lib = read(ROOT / "shared/assets/unity-asset-library.json")
    product = next(x for x in lib["products"] if x["id"] == product_id)
    path = asset_root / product["actualAssetPath"] / "Generated/Prefabs" / name
    meta = path.with_suffix(path.suffix + ".meta")
    guid = re.search(r"^guid:\s*(\w+)", meta.read_text(encoding="utf-8-sig"), re.M).group(1)
    return {
        "key": key, "productId": product_id,
        "assetPath": path.relative_to(asset_root).as_posix(), "guid": guid,
        "file": artifact(path), "meta": artifact(meta),
        "sourceUrl": url, "license": "CC0-1.0", "creditRequired": False,
        "licenseEvidence": {"checkedOnKst": DATE, "kind": "publisher-product-page",
            "url": url, "finding": "Publisher states CC0; personal and commercial use allowed and attribution not required."},
        "sourceRedistribution": False, "adoption": "planned-existing-owned-library-reuse",
        "teachingRole": teaching_role, "actualFileAndGuidChecked": True,
        "runtimeReviewedForA03": False, "materialsAndGripReviewedForA03": False,
        "knownLimits": ["Static/import evidence does not prove this revision's animation, grip, occlusion or runtime materials.",
            "Shared vendor originals remain unchanged; use scene instances or own prefab variants."],
    }


def main():
    assert SLUG == "animation-breaking-down-attack-animations"
    if (HERE / "checkpoint.json").exists():
        raise RuntimeError("A03 readiness already exists. Review changed inputs and edit the existing plan selectively; do not overwrite later work by replaying this initializer.")
    control = read(ROOT / "shared/publishing/video-production-control.json")
    auth = control["finiteBatchAuthorizations"][BATCH]
    assert auth["productionAuthorized"] and "A03" in auth["episodeIds"]
    for name, expected in EXPECTED.items():
        assert sha(INPUT / name) == expected, name
        destination = SCRIPT / name
        if destination.exists():
            assert sha(destination) == expected, f"Refuse changed destination: {destination}"
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((INPUT / name).read_bytes())
    ko, en, units = (read(SCRIPT / n) for n in EXPECTED)
    assert [s["id"] for s in ko["scenes"]] == [s["id"] for s in en["scenes"]] == [f"{i:02}" for i in range(1, 7)]
    paragraph_count = clause_count = 0
    paired = {}
    for k, e in zip(ko["scenes"], en["scenes"]):
        assert len(k["lines"]) == len(e["lines"])
        for i, (kl, el) in enumerate(zip(k["lines"], e["lines"])):
            us = units["byScene"][k["id"]][str(i)]
            assert normalized(" ".join(u["ko"] for u in us)) == normalized(kl)
            assert normalized(" ".join(u["en"] for u in us)) == normalized(el)
            paired[f'{k["id"]}-p{i + 1:02}'] = {
                "semanticPairingReviewed": True,
                "basis": "All six scenes and sixteen independent KO/EN paragraphs read in source order. The prior 115-clause pairing was reread and exact normalized reconstruction rechecked. This is text review, not speech or encoded-frame QA.",
                "captionUnits": us,
            }
            paragraph_count += 1
            clause_count += len(us)
    assert (paragraph_count, clause_count) == (16, 115)
    spoken = copy.deepcopy(ko)
    spoken.update(slug=SLUG, pronunciationOnly=True, pronunciationAliases={},
                  status="unchanged-spoken-draft-awaiting-source-and-runtime-lock")
    write(SCRIPT / "narration.spoken-ko.json", spoken)
    (SCRIPT / "narration.spoken-ko.txt").write_text(
        "\n\n".join(line for s in spoken["scenes"] for line in s["lines"]) + "\n", encoding="utf-8")
    write(SCRIPT / "caption-aliases.json", {})
    script_inputs = [artifact(SCRIPT / n) for n in ("narration.ko.json", "narration.en.json", "narration.spoken-ko.json")]
    write(HERE / "caption-units.json", {
        "slug": SLUG, "revision": "grid-v1", "status": "authored-paired-clauses-text-verified",
        "timingLocked": False, "reviewedSource": artifact(SCRIPT / "caption-units.json"),
        "scriptInputs": script_inputs, "paragraphs": paired,
    })

    old_helpers = ROOT / "projects/animation-exaggeration/production/grid-v1"
    pipeline_provenance = []
    for name in ("storage_paths.py", "audio_pipeline.py", "caption_pipeline.py"):
        source = old_helpers / name
        text = source.read_text(encoding="utf-8-sig").replace("A02", "A03").replace("animation-exaggeration", SLUG)
        text = text.replace("reference-preserving-v2", "grid-v1")
        ast.parse(text, filename=name)
        (HERE / name).write_text(text, encoding="utf-8")
        pipeline_provenance.append({"source": artifact(source), "copy": artifact(HERE / name),
            "changes": ["Episode authorization A02 to A03 where present", "Episode slug where present", "Documentation revision examples to grid-v1"],
            "compileAstPassed": True})
    write(HERE / "authorization.json", {
        "episode": "A03", "slug": SLUG, "revision": "grid-v1", "batch": BATCH,
        "localProductionAuthorized": True, "platformMutation": False, "noUiOrFocus": True,
    })
    write(HERE / "execution-grant.json", {
        "episode": "A03", "revision": "grid-v1", "batch": BATCH, "stages": [],
        "status": "awaiting-parent-slot-and-source-runtime-lock",
        "reason": "This child is authorized for metadata and pipeline readiness only. No media stage has been granted.",
    })
    write(HERE / "pipeline-provenance.json", {
        "episode": "A03", "slug": SLUG, "checkedOnKst": DATE, "copies": pipeline_provenance,
        "executionStagesGranted": [], "jobsStarted": False, "importHasNoMainExecution": True,
        "voiceRegistrationCopied": False, "voiceRegistrationReason": "A02's registration is tied to completed voice evidence; no A03 recording or UI completion exists.",
    })

    readiness = read(INPUT / "production-readiness.json")
    sources = read(RESEARCH / "footage-candidates.json")
    character_url = "https://rg-poly.itch.io/cartoon-city-massive-pack-characters"
    assets = [
        unity_asset("hero", "011", "Character_2_2_1_57b5b7b010ec.prefab", character_url,
                    "Same articulated attacker across all six grid explanations."),
        unity_asset("target", "011", "Character_1_1_1_f0ff54f64441.prefab", character_url,
                    "Readable counterpart for custom hit detection and paired hit stop."),
        unity_asset("sword", "080", "Sword_1_A_0b109e96ef50.prefab",
                    "https://rg-poly.itch.io/medieval-weapons-small-low-poly-pack",
                    "Recognizable blade, guard and grip; visible tip for preparation, strike and follow-through pointers."),
    ]
    native_contract = {
        "status": "implementation-specification-only-not-created-or-runtime-tested",
        "engine": "Unity", "project": "unity/VideoEditing", "editorVersion": "6000.6.0f1",
        "renderPipeline": "Universal Render Pipeline 17.6.0", "capture": {"width": 1920, "height": 1080, "fps": 60},
        "rendererReason": "One rig, own attack, actual state transition and timing explain the four source-ordered elements in a consistent grid environment.",
        "existingStage": "unity/VideoEditing/Assets/VideoScenes/animation-series-v1",
        "createdSceneFiles": [], "sharedAssetPaths": [a["assetPath"] for a in assets],
        "visualGrammar": {
            "environment": "Existing animation-series dark grid, fixed side/three-quarter framing with floor and clear silhouettes; preserve black brand background and warm-yellow headings.",
            "pictureLabel": "직접 구현 · Unity", "cameraRule": "Same camera and character scale in A/B comparisons. A different angle needs an explicit teaching reason.",
            "gridIsIllustration": True, "commercialCharacterMattingUsed": False,
            "captionSafeArea": {"anchorPx": [960, 970], "fontPx": 48, "maxLines": 2, "fixed": True},
            "terms": "English canonical term + Korean/plain meaning at first use, then collapse to persistent term chip.",
            "annotations": "Point to the actual shoulder, sword tip, hit region or phase boundary; reveal with narration, clear at cuts and hide when occluded.",
            "analysisHold": "Label a pose freeze as analysis. Do not let a static character silently pad narration or classify it as actual gameplay.",
        },
        "animationDesign": {
            "kind": "new-authored-sword-attack-on-existing-generic-rig",
            "sourceVendorClipReusedAsAttack": False,
            "prohibitedShortcut": "Do not stretch A02's 22-frame FightM_Punch_A clip to 48 frames and describe it as the designed sword attack.",
            "clock": "Integer simulation boundaries k=0..48 at 60 Hz; 48 intervals produce 0.8 seconds. Stored rendered samples 0..47 precede the ending boundary48.",
            "phasesEndExclusive": {"leadIn": [0, 12], "attack": [12, 18], "followThrough": [18, 48], "activeHitRegion": [12, 16]},
            "designedContactFrame": 14, "contactStatus": "Proposed; actual geometry overlap and event trace must agree before use.",
            "keyPoses": [
                {"boundary": 0, "pose": "Ground standby with weapon clearly readable; accepted input immediately starts the arm/body response."},
                {"boundary": 4, "pose": "Readable windup silhouette; visible shoulder turn and raised blade, feet still planted."},
                {"boundary": 11, "pose": "Preparation maximum; weapon poised before the attack plane."},
                {"boundary": 14, "pose": "Contact composition: readable blade direction, turned torso, balanced feet; custom target overlaps active swept region."},
                {"boundary": 18, "pose": "Sword continues through the strike; torso and arm follow the force."},
                {"boundary": 28, "pose": "Extended finish; body begins restoring balance without appearing fully idle."},
                {"boundary": 36, "pose": "Ready to branch into a permitted next action; no-input trajectory still continues."},
                {"boundary": 48, "pose": "Return to initial standby with no positional jump."},
            ],
            "requiredPoseChecks": ["Bind to actual generic-rig bones after inspecting hierarchy", "Stable sword-hand grip", "No foot skating through main attack", "No clipping through torso/target", "Distinguishable prep/contact/follow-through at375px", "Continuous no-input return and accepted-run blend"],
        },
        "actualStateImplementationRequired": {
            "input": "One deterministic accepted input event at boundary0 drives comparisons; buffer only the explicit requested next action.",
            "hitDetection": "Custom sword swept region against target collider enabled only inside own active interval. Hit event originates from actual overlap and is logged once, rather than a decorative collision label.",
            "hitStop": "For scene03 only, proposed six output ticks freeze both actor and target on the actual contact event. Record renderClock and simulationClock separately. Duration is our setting, never a commercial value.",
            "cancelComparison": "Scene05 disables hit stop so .8/.6/.2-second arithmetic uses the unpaused60-Hz simulation. Same clip, rig and queued-run event; only transition permission threshold36 versus48 differs.",
            "noInput": "Both policies finish their full48-frame visual clip when no next action is requested.",
            "nextAction": "Queued run transitions at boundary36 in the early-permission variant and boundary48 in the wait-to-idle variant. Record first accepted transition time.",
            "actionMask": "Running, jumping and attacking are separate eligible action types. Show the configured rule; do not imply all transitions are always enabled.",
            "numberProvenance": "All displayed48,36,60,.8,.6,.2 values are our configured/measured implementation only. Reconcile event log before publishing labels.",
            "requiredEventFields": ["sceneId", "variant", "outputFrame", "simulationFrame", "inputAccepted", "actionRequested", "hitRegionActive", "collisionConfirmed", "hitStopRemaining", "currentState", "transitionAccepted"],
        },
    }
    native_by_scene = {
        "01": {"test": "Four elements on one grid", "before": "Ground standby and a distinct airborne standby pose", "action": "One sword attack through preparation, attack and follow-through", "result": "Three moving stages plus standby form four elements", "variables": "Ground/air starting pose; phase labels follow same motion", "gameplay": ["zIu71IFHHYA"], "speechVisual": ["01-p01: independently recorded observed preparation/contact/return opens after branding", "01-p02: ground and airborne standby side by side, then four-element timeline; no exact commercial hitbox labels"]},
        "02": {"test": "Readable response after input", "before": "Identical standby and accepted input tick", "action": "Clear early windup versus barely changing early pose; same attack contact timing", "result": "Body silhouette makes the accepted input and coming attack readable", "variables": "Only early-pose amplitude/readability", "gameplay": ["zIu71IFHHYA"], "speechVisual": ["02-p01: reveal arm/torso movement from standby", "02-p02: aligned A/B, same actual input pulse and time cursor", "02-p03: show attacker and opponent sight lines without claiming measured commercial reaction delay"]},
        "03": {"test": "Active interval, contact and hit stop", "before": "Weapon visibly moving before own hit region is active", "action": "Enable own active region, register overlap, freeze both bodies on hit", "result": "The contact pose remains readable and shows force direction", "variables": "Active flag and own hit-stop setting, tested separately", "gameplay": ["zIu71IFHHYA"], "speechVisual": ["03-p01: separate movement timeline from enabled hit interval", "03-p02: impact pose pointers and separate simulation/render clocks; commercial example illustrates visible contact only"]},
        "04": {"test": "Visible follow-through versus control restriction", "before": "Same strike and same remaining locked interval", "action": "Early near-idle visual versus arm extension, torso continuation and rebalancing", "result": "Meaningful follow-through communicates the otherwise unresponsive interval", "variables": "Only post-strike pose curve, not lock time", "gameplay": ["mhC1eHMnZzY"], "speechVisual": ["04-p01: sword tip/shoulder contour follows visible continuation", "04-p02: same-clock A/B; next-action indicator stays locked equally", "04-p03: separate labelled Follow-through/Recovery lanes with potentially different endpoints"]},
        "05": {"test": "Animation end versus next-action permission", "before": "Same authored48-frame attack, no hit stop", "action": "Queue identical run; permit transition at36 versus48; separately show no-input continuation", "result": "Same .8-second clip with .6-second early action permission produces .2-second difference", "variables": "Permission threshold only; action mask shown separately", "gameplay": [], "speechVisual": ["05-p01: two transition policies plus no-input lane", "05-p02: substitute48/60=.8 and36/60=.6 beside actual logged timeline, subtract .2; do not read numbers over unrelated play", "05-p03: explicitly configured run/jump/attack eligibility beside same rig"]},
        "06": {"test": "Four shared briefing anchors and concrete direction", "before": "Same full attack and partially empty brief", "action": "Populate standby pose, attack pose, active-start frame and next-action time, then point to shoulder angle/blade height/held finish", "result": "Timing and intended impression describe one coherent movement", "variables": "One art-direction detail per comparison; retain own event timings", "gameplay": ["zIu71IFHHYA", "mhC1eHMnZzY"], "speechVisual": ["06-p01: four fields fill in spoken order; prep and follow-through connect the anchors", "06-p02: draw concrete shoulder/weapon pointers beside same frame", "06-p03: full motion on persistent grid; close on thesis without a new chapter or spoken coaching ad"]},
    }
    scenes = []
    for ks, mapping in zip(ko["scenes"], readiness["referenceToScriptScreen"]):
        sid = ks["id"]
        scenes.append({
            "id": sid, "title": ks["title"], "paragraphIds": [f"{sid}-p{i+1:02}" for i in range(len(ks["lines"]))],
            "referenceMapping": mapping, "renderer": "Unity + Motion Canvas labels/compositing",
            "classification": "self-authored-explanation", "implementationStatus": "planned-only",
            "plannedUnityScene": f"unity/VideoEditing/Assets/VideoScenes/{SLUG}/grid-v1/A03_{sid}.unity",
            "unitySceneExists": False, "nativeDesign": native_by_scene[sid],
            "sourceTiming": "Unbound; use actual future paragraph/word alignment, not estimated reading speed",
            "holdDefaultSeconds": 0, "audioVisualTimingVerified": False,
        })
    blockers = [
        {"id": "native-footage-lock", "status": "open", "needed": "Audit exact decoded PTS, source cut boundaries and continuous normal-speed playback. Reject the slowed IzAw candidate. Secure enough distinct useful native demonstrations for the teaching beats without loops or padding."},
        {"id": "source-rights-audio", "status": "open", "needed": "Clip-specific editorial/rights and original-audio review; recorder permission is not established. Capcom current video-policy fetch again returned403 on2026-11-04. Nintendo game policy does not independently grant recorder footage rights."},
        {"id": "scene-runtime", "status": "open", "needed": "Build six editable Unity scenes using actual generic rig and owned sword. Implement and inspect the48-frame attack, hit event, meaningful follow-through, no-input path and36/48 transition event log. Check actual rendered pose/material/grip/occlusion at1080p and375px."},
        {"id": "screen-contract", "status": "open", "needed": "Measure native gameplay/explanation against default60:40 excluding branding2s/member10s after useful cut/timing lock. No ratio exception is inherited from A02; do not fill with repeated or idle clips."},
        {"id": "voice-slot", "status": "not-started", "needed": "Root allocates sequential costly-job slot only after source/runtime lock. Then generate approved own-voice ElevenLabs sampleB, register actual settings and source hashes, align unchanged PCM, and derive timing."},
    ]
    plan = {
        "schemaVersion": 1, "episode": "A03", "slug": SLUG, "revision": "grid-v1", "title": ko["title"],
        "status": "source-ordered-design-and-isolated-pipeline-ready-footage-runtime-lock-pending", "updatedOnKst": DATE,
        "authority": {"batch": BATCH, "control": artifact(ROOT / "shared/publishing/video-production-control.json"), "scope": "Bounded A03 readiness requested by root; no media jobs, Unity mutations, shared worklist, Git or platform changes."},
        "sourceReference": {"episode": "G03", "title": "Breaking Down Attack Animations [Animation]", "url": "https://www.youtube.com/watch?v=LewXWM7HDd8", "classification": "research-reference-only", "productionUseAllowed": False},
        "sourceEvidence": {"sourceMap": artifact(RESEARCH / "source-map.json"), "fullResearchTranscript": artifact(RESEARCH / "transcript.research.txt"), "priorReadiness": artifact(INPUT / "production-readiness.json"), "candidateSurvey": artifact(RESEARCH / "footage-candidates.json")},
        "sourceReviewLimits": readiness["referenceReview"], "scriptInputs": script_inputs,
        "preservedHashes": EXPECTED, "sourceOrder": [s["id"] for s in scenes], "scenes": scenes,
        "canonicalTerms": readiness["canonicalTerms"], "historicalScopeCorrection": readiness["historicalScopeCorrection"],
        "chapterBoundaryLinks": readiness["chapterBoundaryLinks"], "assetRecords": assets,
        "sharedAssetPaths": native_contract["sharedAssetPaths"], "nativeImplementationContract": native_contract,
        "independentFootageCandidates": sources["candidates"], "productionSelectedSources": [],
        "sourceSelectionNotes": {
            "referenceMediaExcluded": True,
            "nativeSpeedRequired": True, "minimumDecodedSource": [1920, 1080], "sourceAspectPreserved": True,
            "commercialMattingDecision": "Prefer the actual Smash Training grid and independently authored Unity grid. Do not matte opaque gameplay characters onto a false tool background; no new capture source is represented as an animation-tool output.",
            "previousEpisode": {"episode": "A02", "actualPlannedProductionGames": ["Tekken 8", "Virtua Fighter 5 R.E.V.O.", "Kirby's Adventure"], "comparison": "Prospective A03 keeps a distinct platform fighter and adds an action RPG. The original Link role is useful for the visible phase demonstration; Monster Hunter supports a heavy follow-through across genre."},
            "nintendoExampleCount": {"provisionalNumerator": 1, "provisionalDenominator": 2, "target": "approximately one third, nearest feasible whole example with at least one", "rounding": "round(2/3)=1; do not invent a third example to force an exact ratio", "ownershipEvidence": "https://www.smashbros.com/en_US/fighter/03.html", "finalized": False},
            "gameplayClaims": "Only observed body/weapon action and opponent result. Commercial input delay, active hitboxes, cancel timing, hit-stop duration and current frame data are not inferred.",
            "sameGameGuideWarning": "The Monster Hunter source is a guide. Only independently recorded game movement may be considered after exact selection and rights/audio review; the creator's explanation, overlays and narration are not our lesson content.",
            "captionClearance": "Old creator numerical overlays are not current measurements; choose bounded presentation retaining game aspect and useful UI while avoiding adoption of those figures. Verify on decoded frames before lock.",
        },
        "screenTimeContract": {"bodyActualGameplay": .60, "bodyExplanation": .40, "excludedBrandingSeconds": 2, "excludedMemberEndSeconds": 10, "measured": False, "exceptionGranted": False},
        "headingFreeReadthrough": {"ko": "All current six scenes retained and read in source order", "en": "All current six scenes read; no unsupported commercial timing or Melee universal claim added", "pairedClauses": 115, "paragraphs": 16, "reconstructionExactIgnoringWhitespace": True, "spokenTextUnchanged": True, "audioListening": False, "audioVisualPacingVerified": False},
        "audio": {"voice": "user's own ElevenLabs voice, approved sampleB", "voiceId": "jIRSnF8OWAsWEChVwCuK", "generated": False, "settings": "Resolve exact accepted sampleB settings from existing verified record before generation; do not guess model/stability/speed", "backgroundMusic": "Use verified existing original BGM with license/source record and narration ducking; no missing-music final", "sourceAudioAdopted": False, "noGreetingAdded": True, "spokenCoachingCTA": False},
        "currentPrimaryFetch": [{"url": "https://www.capcom-games.com/en/video-policy/", "checkedOnKst": DATE, "result": "403 Forbidden; no policy clearance inferred"}],
        "blockers": blockers,
        "nextAction": "Lock exact native independent footage and audio/rights basis while designing own Unity scenes; parent allocates next costly stage only after blockers relevant to TTS are resolved.",
    }
    write(PLANNING / "production-plan.json", plan)
    write(PROJECT / "project.json", {
        "schemaVersion": 1, "slug": SLUG, "series": "animation", "seriesOrder": 3,
        "episode": "A03", "revision": "grid-v1", "title": ko["title"], "status": plan["status"],
        "batch": BATCH, "sourceReference": plan["sourceReference"], "sourceClassification": "research-reference-only",
        "planning": rel(PLANNING / "production-plan.json"), "checkpoint": rel(HERE / "checkpoint.json"),
        "voice": plan["audio"],
        "delivery": {"status": "not-rendered", "directory": f"projects/{SLUG}/production/local/grid-v1/delivery/output/{SLUG}", "files": [], "masterSha256": None},
        "review": {"humanFinalReviewCompleted": False, "audioListeningCompleted": False, "visualReviewCompleted": False},
        "youtube": {"uploadAuthorized": False, "uploaded": False, "publicOrScheduled": False},
    })
    write(HERE / "checkpoint.json", {
        "episode": "A03", "slug": SLUG, "updatedOnKst": DATE, "status": plan["status"],
        "plan": rel(PLANNING / "production-plan.json"), "scriptInputs": script_inputs,
        "completed": ["Correct batch slug/title verified", "Frozen KO/EN/caption inputs copied byte-for-byte", "Six source-ordered native scene designs and exact clock distinction documented", "Owned rig/sword paths, GUIDs, hashes and current publisher CC0 terms verified", "Isolated audio/caption helpers copied with empty stage grant"],
        "notDone": ["Final independent cut/speed/audio/rights selection", "Unity scene or animation creation/runtime checks", "TTS/ASR/render/mix", "Encoded1080p/mobile playback and complete listening", "Human final review", "Git/shared-worklist/platform mutation"],
        "readiness": {"scriptStructure": True, "isolatedPipelineScaffold": True, "ttsReady": False, "timingLocked": False, "unityReady": False, "finalProductionReady": False},
        "blockers": blockers, "nextAction": plan["nextAction"], "executionStagesGranted": [],
    })
    write(PROJECT / "production/review-ledger.json", {
        "episode": "A03", "revision": "grid-v1", "updatedOnKst": DATE,
        "entries": [{"kind": "static-readiness", "sourceHashes": script_inputs, "sourceOrder": True,
            "completeKoEnTextRead": True, "pairedClauseReconstructionVerified": True,
            "paragraphs": 16, "pairedClauses": 115, "compileAstPassed": True,
            "captionPixelVerification": False, "audioGenerated": False, "audioListening": False,
            "nativeAnimationRuntimeReview": False, "humanReview": False,
            "limit": "Design and metadata only. Prior sampled source visuals remain bounded to their recorded review; no continuous playback or new rights claim is inferred."}],
        "currentFinalMaster": None, "humanFinalApproval": None,
    })
    (PLANNING / "outline.md").write_text(
        "# " + ko["title"] + "\n\n"
        "A03의 원본 설명 순서와 6개 씬·16개 문단을 보존한 제작 준비본입니다. 아직 음성 생성·씬 제작·렌더링은 하지 않았습니다.\n\n"
        "| 순서 | 설명 흐름 | 화면에서 보여줄 것 |\n|---|---|---|\n"
        + "\n".join(f'| {s["id"]} | {s["title"]} | {s["referenceMapping"]["retainedTeaching"]} |' for s in scenes)
        + "\n\n기존 캐릭터 011과 검 에셋 080을 재사용합니다. 제작자 페이지에서 CC0를 확인했고, 이번 씬의 재질·관절·검 손잡이·실행 동작은 아직 검수하지 않았습니다.\n\n"
        "48프레임 전체 동작과 36프레임 다음 조작 허용을 같은 자체 제작 동작으로 비교합니다. 히트 스톱 설명에는 별도 시계를 쓰고, 0.8초·0.6초 계산 장면에는 히트 스톱을 적용하지 않습니다. 상용 게임의 판정·캔슬 시간을 추정값으로 표시하지 않습니다.\n\n"
        "남은 확인: 독립 게임 영상의 정확한 구간·정상 속도·원본 소리·이용 근거, Unity 실제 동작과 상태 기록, 화면 비중, 음성과 최종 영상 검수. 입력 대본·단락·순서와 자막은 해시로 고정되어 있습니다.\n",
        encoding="utf-8")
    print(json.dumps({"slug": SLUG, "title": ko["title"], "paragraphs": paragraph_count,
        "pairedClauses": clause_count, "plan": rel(PLANNING / "production-plan.json"),
        "jobsStarted": False, "ttsReady": False, "frozenHashesPreserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
