"""Record A03's bounded read-only-source follow-up. No media operations."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = HERE.parents[1]
PLAN = PROJECT / "planning/production-plan.json"
SURVEY = ROOT / "production/batches/animation-18-20261031/research/A03/independent-survey"
DATE = "2026-11-04"


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def artifact(p):
    return {"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}


def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    plan = read(PLAN)
    if plan.get("sourceReadinessFollowup"):
        raise RuntimeError("Follow-up already registered. Do not replay this updater over later work.")
    for f in plan["scriptInputs"]:
        assert artifact(ROOT / f["path"])["sha256"] == f["sha256"]
    timing_path = PROJECT / "planning/source-timing-audit.json"
    timing = read(timing_path)
    link = timing["sources"]["link-grid-15-29"]
    mh = timing["sources"]["greatsword-training-312-326"]
    for row in (link, mh):
        assert artifact(ROOT / row["file"])["sha256"] == row["sha256"]
    link["presentationGap"] = {"precedingDecodedFrame": 836, "nextDecodedFrame": 837,
        "ptsBefore": 13.979497, "ptsAfter": 14.029663, "deltaSeconds": .050166,
        "note": "Outside proposed useful intervals. Preserve recorded timing; do not interpolate, speed-repair or choose the tail as cadence evidence."}
    for row in (link, mh):
        row["declaredFrameCountIsNotDecodedCount"] = True
        row["countRule"] = "Use actual decoded sequence and PTS. Stream nb_frames is not a validated usable-frame count for this section file. Cause of the mismatch is not asserted."
    write(timing_path, timing)
    primary = [
        {"id": "nintendo-current", "url": "https://www.nintendo.co.jp/networkservice_guideline/en/index.html", "checkedOnKst": DATE,
         "documentVersion": "2024-09-02", "readScope": "Full current page and FAQ",
         "finding": "Creative/editorial game commentary and specified platform monetization are covered conditionally; individual consumers only. Official Nintendo promotional material is included. Third-party rights remain separate.",
         "application": "Supports a conditional Nintendo-game-content basis, not another recorder's blanket permission or a guarantee for our final edit."},
        {"id": "capcom-support-current-link", "url": "https://www.capcom-support.com/hc/en-us/articles/5606982299292-Capcom-Video-Policy", "checkedOnKst": DATE,
         "documentVersion": "Support article says Updated July22,2026 09:31", "readScope": "Full short official support article and its outbound policy link",
         "finding": "The current support article directs creators to the Capcom Video Policy. Its link resolves to https://www.capcomusa.com/video-policy/.",
         "application": "New current official endorsement for the accessible US policy. The policy text itself still dates March15,2021; do not relabel it a2026 revision or the unread Japanese2025 policy."},
        {"id": "capcom-us-policy", "url": "https://www.capcomusa.com/video-policy/", "checkedOnKst": DATE,
         "documentVersion": "2021-03-15", "readScope": "Full page and FAQ, reached directly and through the2026 official support link",
         "finding": "Educational commentary tied to game action and specified ad/platform monetization are contemplated. Third-party footage/music and unlicensed events remain separate; the policy reserves rights and is not a blanket derivative-work licence.",
         "application": "Available official game-content guidance, subject to actual use and regional/account context. Does not clear Arekkz's authored guide or music."},
        {"id": "capcom-sg-policy", "url": "https://www.capcom.sg/video-policy/", "checkedOnKst": DATE,
         "documentVersion": "2021-01-06", "readScope": "Full official Singapore page",
         "finding": "Public regional policy also permits creative game commentary and specified ad monetization subject to conditions and separate third-party rights.",
         "application": "Corroborating official regional text, not proof that this version supersedes the Japanese2025 update or governs every uploader."},
        {"id": "capcom-japan-faq", "url": "https://www.capcom.co.jp/support/faq/others_website_037152.html", "checkedOnKst": DATE,
         "documentVersion": "FAQ states guideline update2025-12-01", "readScope": "Full relevant Q&A",
         "finding": "Individuals are directed to the linked guidelines; corporate/affiliated creators are treated separately. The linked current Japanese policy still returns403.",
         "application": "Preserve the unresolved regional/applicant scope; do not assume the uploader is a corporate entity or that a creator-specific grant exists."},
    ]
    recorder_search = {
        "existingDescriptionsRead": [artifact(SURVEY / n) for n in ["link-grid-15-29.info.json", "greatsword-training-312-326.info.json", "link-official.info.json", "greatsword-official.info.json", "link-grounded.info.json"]],
        "result": "No explicit Creative Commons licence or blanket reuse permission found in the saved video descriptions. The two preferred candidates have a null metadata licence field; null is not proof of prohibition or permission.",
        "publicSearch": ["Arekkz Gaming footage usage permission", "Arekkz use my footage", "Arekkz Gaming reuse", "国立大のモンダ 転載"],
        "creatorAboutPages": {"https://www.youtube.com/@ArekkzGaming/about": "Fetch throttled; no permission inferred", "https://www.youtube.com/@国立大のモンダ/about": "Fetch throttled; no permission inferred"},
        "unrelatedSearchResultsUsedAsPermission": False, "creatorContactSent": False,
        "conclusion": "Recorder-specific permission remains unestablished. Editorial use must be recorded honestly, separately from publisher guidance; no approval is fabricated.",
    }
    intervals = [
        {"id": "link-first-string", "sourceId": "zIu71IFHHYA", "file": link["file"],
         "decodedBoundaryProposal": link["candidateIntervals"]["0-2.073515"],
         "absoluteSourceRangeApprox": [15, 17.090236], "absoluteOffsetVerified": False,
         "before": "At sampled local0,.5,.702319,.752485,.802651 Link is upright facing Mario on the grid.",
         "action": "At .852816/.902982 the sword rises; .953148–1.304307 shows successive slashes, with early swings falling short;1.354473/1.404638 shows contact and changed training HUD.",
         "result": "At1.605301–1.956461 Mario is launched while Link remains extended; by2.006626/2.056792 Link is back near standby.",
         "correctedEarlierSummary": "The0–.802651 interval is the before state, not the complete before/action/result. The visible sequence is a multi-part weak-attack string, not one continuous single-hit window.",
         "supportedScenes": ["01 baseline/phase illustration, if labelled as a string", "02 visible windup only", "03 visible contact and launch", "06 phase recap"],
         "notSupported": ["A single attack with exactly one active interval", "Button acceptance or input delay", "Current8F/3.6%/12%/280% values", "Exact Hit Stop or cancel frames"],
         "openingDecision": "Do not lock the generic single-swing opening to this multi-hit example without an explicitly compatible visual beat. Frozen KO is unchanged; source fit remains pending.",
         "visualEvidence": [artifact(SURVEY / "link-grid-15-29-contact.jpg"), artifact(SURVEY / "link-grid-15-29-phase-detail.jpg"), artifact(SURVEY / "link-grid-15-29-phase-frame-index.json")],
         "beginnerUi": [{"target": "left red1P Link", "plainLabel": "검을 휘두르는 캐릭터", "need": "Identify whose movement to watch; do not assume viewers recognize Link."},
             {"target": "right CP Mario", "plainLabel": "공격을 받는 상대", "need": "CP is the training opponent, not an animation bone or timing marker."},
             {"target": "native white grid", "plainLabel": "연습장 격자", "need": "It is the game's Training stage; do not call it our animation editor."},
             {"target": "upper-right training counters", "plainLabel": "맞았는지 확인하는 표시", "need": "If retained as evidence, explain only that the display changes after contact; do not teach unverified current balance numbers."}],
         "overlayPlan": "Avoid adopting the creator's bottom frame/damage/KO explanation. Proposed top gameplay region ends roughly near sourcey810; exact crop and floor/HUD clearance require original decoded-frame layout QA. Preserve aspect, captions and any required credit. No crop is executed or locked."},
        {"id": "link-second-string", "sourceId": "zIu71IFHHYA", "file": link["file"],
         "decodedBoundaryProposal": link["candidateIntervals"]["5.0-7.01"], "absoluteSourceRangeApprox": [20.016566, 22.023192], "absoluteOffsetVerified": False,
         "before": "Sample5.0 shows the same two characters facing each other after repositioning.",
         "action": "Sample5.5 raises the blade;6.0 shows a sweep in contact, and6.5 has the final extended strike and launch.",
         "result": "At7.0 Link has recovered upright while Mario remains displaced.",
         "supportedScenes": ["03 independent contact confirmation"],
         "notSupported": ["Different game example", "Extra evidence for a claimed single active window", "Exact controller timing"],
         "reuseRule": "This is another recorded attempt of the same string, not a new primary game. Use only for a distinct narrated observation, never to fill ratio or replay identical proof.",
         "visualEvidence": [artifact(SURVEY / "link-grid-15-29-contact.jpg")],
         "beginnerUi": "Same identities and Training-grid explanation as link-first-string."},
        {"id": "mhw-follow-through", "sourceId": "mhC1eHMnZzY", "file": mh["file"],
         "decodedBoundaryProposal": mh["candidateIntervals"]["5.5-8.5"], "absoluteSourceRangeApprox": [317.5055, 320.5085], "absoluteOffsetVerified": False,
         "before": "At local5.5/6.0 the hunter faces a distant practice target; the sword and full body are visible in the same three-quarter view.",
         "action": "At6.5 the blade is raised;7.0 shows the overhead swing brought low;7.5/8.0 maintains a low finish before rebalancing.",
         "result": "At8.5 the hunter is visibly returning toward a ready pose.",
         "supportedScenes": ["04 visible weapon/body follow-through", "06 concrete shoulder/blade art-direction comparison"],
         "notSupported": ["A confirmed hit on the distant target", "Hit Stop", "A measured recovery or cancel permission", "The creator's button tutorial as our explanation"],
         "narrationFit": "This is a dry swing. A phrase saying that this hunter just hit the target must not accompany it. The frozen '맞힌 다음에도' passage can stay over our actual hit-event scene; real-game confirmation must target visible motion only.",
         "visualEvidence": [artifact(SURVEY / "greatsword-training-312-326-contact.jpg")],
         "beginnerUi": [{"target": "hunter and large blade", "plainLabel": "큰 검을 휘두른 뒤의 몸", "need": "Identify sword tip and torso; no franchise knowledge needed."},
             {"target": "distant practice target", "plainLabel": "동작 확인 · 빈 공간에 휘두름", "need": "Do not suggest the distant dummy was struck."},
             {"target": "Overhead Slash and button prompts", "plainLabel": "기술·조작 안내", "need": "These are source-game/guide UI, not measured input events. Avoid relying on the creator's instructional label."}],
         "overlayPlan": "Trace sword tip and shoulder with small labels and the same camera; leave actual game UI unobscured. Exact label/caption layout remains unverified at1080p/375px."},
        {"id": "mhw-sideview-alternative", "sourceId": "mhC1eHMnZzY", "file": mh["file"],
         "decodedBoundaryProposal": mh["candidateIntervals"]["0.5-2.6"], "absoluteSourceRangeApprox": [312.5005, 314.6026], "absoluteOffsetVerified": False,
         "before": "At .5s the sword is already raised; the earlier beginning is a four-panel guide transition.",
         "action": "1.0/1.5s shows a low sword/torso finish.", "result": "2.5s the hunter raises the weapon toward a ready posture.",
         "supportedScenes": ["04 side view of visible follow-through only"],
         "notSupported": ["Full start-to-finish single attack", "Confirmed hit", "Exact input or control return"],
         "priority": "Secondary to the clearer5.5–8.5s block; do not include the opening guide montage.",
         "visualEvidence": [artifact(SURVEY / "greatsword-training-312-326-contact.jpg")],
         "beginnerUi": "Same hunter/sword explanation; explicitly a motion demonstration without a visible hit target."},
    ]
    review = {
        "episode": "A03", "revision": "grid-v1", "checkedOnKst": DATE,
        "scope": "Existing candidate files/metadata/contact sheets only plus public primary-policy/creator searches. No new media download, TTS, Unity edit, render, platform change, Git or shared worklist mutation.",
        "timingAudit": artifact(timing_path),
        "normalSpeedAssessment": {
            "zIu71IFHHYA": {"filePresentationCadenceAudited": True, "decodedFrames": 838, "medianIntervalSeconds": .016722,
                "normalGameSpeedConfirmed": False, "continuousPlaybackViewedThisPass": False,
                "sampledFinding": "No slow-speed indicator was visible in the inspected contact sheets. Native PTS is close to60fps, but that does not prove game simulation or upstream editor speed.",
                "tailAnomaly": "One .050166s PTS interval at13.979497→14.029663; proposed useful blocks exclude it.", "retimingApplied": False},
            "mhC1eHMnZzY": {"filePresentationCadenceAudited": True, "decodedFrames": 839, "cadence": "60000/1001", "normalGameSpeedConfirmed": False,
                "continuousPlaybackViewedThisPass": False, "sampledFinding": "Three separate camera blocks are visible. No slow-speed label observed, but sampled images/CFR metadata do not certify normal simulation speed.", "retimingApplied": False},
            "VlKkv5HSYVA": {"decision": "rejected-for-native-playback", "evidence": artifact(SURVEY / "link-grounded-contact.jpg"),
                "finding": "Training speed1/2 is visible through the excerpt; final shown frame switches to2/3. Do not accelerate it and claim native gameplay."},
        },
        "reviewedVisuals": [artifact(SURVEY / n) for n in ["link-grid-15-29-contact.jpg", "link-grid-15-29-phase-detail.jpg", "greatsword-training-312-326-contact.jpg", "link-official-contact.jpg", "greatsword-official-contact.jpg", "link-grounded-contact.jpg"]],
        "visualReviewLimit": "Every panel of these existing contact sheets was inspected. Main candidates are sampled at2fps and Link first-string detail every third decoded frame. This is not continuous motion/audio or all-frame inspection.",
        "candidateIntervals": intervals,
        "supplementarySources": [
            {"sourceId": "kfeUdBi67G4", "file": "link-official.mp4", "status": "official-promotional-candidate-not-selected",
             "observed": "9.5–11.5s shows a spin slash and return, but the excerpt starts mid-attack; earlier parts show bow/bomb demonstrations. It is not the requested grid environment.",
             "rightsAdvantage": "Published by the official Smash channel and Nintendo guidelines explicitly include official promotional material; avoids an unrelated recorder's authorship layer.",
             "limits": "Montage cuts, actual speed, audio and full single-action start remain unverified. Do not treat an official upload as complete scene clearance."},
            {"sourceId": "t2h3Uxj7nNg", "file": "greatsword-official.mp4", "status": "official-promotional-candidate-not-selected",
             "observed": "10–15s attacks a large monster, which often occludes the sword/body. Burned-in explanatory subtitles and later montage are present.",
             "rightsAdvantage": "Official Monster Hunter channel reduces unrelated-recorder uncertainty; publisher policy still applies.",
             "limits": "The existing file is29.97fps at1080p; no60fps capture claim. Voice/music, montage timing, and obscured follow-through prevent using it as exact frame-mechanism proof."},
        ],
        "primaryRightsEvidence": primary, "recorderPermissionResearch": recorder_search,
        "accessLimits": [
            {"url": "https://www.capcom-games.com/ja-jp/video-policy/", "result": "403 from the official FAQ link; no bypass attempted"},
            {"url": "https://www.capcom-games.com/en/fan-content-guidelines/", "result": "403 from official US footer link; no bypass attempted"},
            {"url": "https://www.capcom-europe.com/video-policy/", "result": "Not accessible in web tool; no bypass attempted"},
        ],
        "sourceAudio": {"listenedThisPass": False, "adopted": False, "policy": "Keep original audio intact. Do not copy tutorial narration or assume music is cleared; choose only after actual clip audio review."},
        "clipRightsStatus": "publisher-guidance-reconfirmed-with-current-official-support-link; recorder-specific-or-final-editorial-basis-pending",
        "productionSelectedSources": [], "newDownloads": 0, "newMediaOutputs": 0,
        "reducedUnknowns": ["Both primary files' exact decoded presentation timestamps and frame counts", "Current official Capcom support route to accessible policy", "Correct before/action/result attribution for Link's multi-hit string", "Dry-swing versus actual-hit distinction for MHW", "Beginner UI pointers and explicit unsupported commercial timing claims"],
        "remaining": ["Continuous original-speed visual playback and actual source audio review", "Final recorder-specific permission or honest bounded editorial assessment with applicable publisher context", "Exact single-swing opening footage compatible with frozen narration", "Enough useful distinct motion for the body contract without loops/padding", "Final per-cut frame/layout/annotation QA", "Own Unity runtime and voice/timing stages"],
    }
    review_path = PROJECT / "planning/source-readiness-review.json"
    write(review_path, review)
    plan["sourceReadinessFollowup"] = {"record": artifact(review_path), "timingAudit": artifact(timing_path),
        "checkedOnKst": DATE, "status": "presentation-timestamps-and-policy-route-verified-final-selection-open"}
    plan["primaryRightsEvidence"] = primary
    plan["candidateCutBindings"] = intervals
    plan["sourceSelectionNotes"]["commercialFrameMeasurements"] = "Native local file PTS is audited. It is not input latency, game active frames, hit stop or cancel timing. No retiming is performed."
    plan["sourceSelectionNotes"]["openingSourceFit"] = "First Link recording is a multi-part string; MHW preferred block is a dry swing. Neither is yet locked as exact proof of the generic single-swing-and-contact opening. Preserve frozen narration while selecting compatible proof."
    for scene in plan["scenes"]:
        sid = scene["id"]
        scene["independentSourceEvidence"] = [x["id"] for x in intervals if any(s.startswith(sid + " ") for s in x["supportedScenes"])]
        scene["independentSourceEvidenceStatus"] = "candidate-observations-and-PTS-only-not-production-clearance"
        if sid == "05":
            scene["independentSourceEvidenceLimits"] = "No existing candidate proves exact commercial cancel permission. All48/36-frame claims remain on our actual implementation, not a borrowed game clip."
    for blocker in plan["blockers"]:
        if blocker["id"] == "native-footage-lock":
            blocker["status"] = "partially-resolved"
            blocker["completedEvidence"] = "Exact decoded PTS, usable frame count and bounded candidate intervals for both preferred files; no speed repair. Slowed IzAw source confirmed rejected."
            blocker["needed"] = "Continuous native-speed visual/audio review, single-swing opening fit and sufficient distinct useful action; metadata cadence is not proof of game speed."
        if blocker["id"] == "source-rights-audio":
            blocker["status"] = "partially-resolved"
            blocker["completedEvidence"] = "Nintendo current policy reread. Capcom official support article updated2026-07-22 points to accessible US policy; official Singapore page also read."
            blocker["needed"] = "Final clip-specific recorder/editorial basis, original-audio review and applicable uploader/regional context. Japan2025 policy remains unread403; do not label older US/SG text as that revision."
    plan["nextAction"] = "Parent reviews the source-readiness record, then completes compatible actual-motion selection and clip audio/rights assessment before allocating Unity/TTS/media slots. No final source is auto-selected by this follow-up."
    write(PLAN, plan)
    checkpoint_path = HERE / "checkpoint.json"
    checkpoint = read(checkpoint_path)
    checkpoint["sourceFollowup"] = plan["sourceReadinessFollowup"]
    checkpoint["blockers"] = plan["blockers"]
    checkpoint["nextAction"] = plan["nextAction"]
    checkpoint["completed"] += review["reducedUnknowns"]
    write(checkpoint_path, checkpoint)
    ledger_path = PROJECT / "production/review-ledger.json"
    ledger = read(ledger_path)
    ledger["entries"].append({"kind": "bounded-source-readiness-followup", "checkedOnKst": DATE,
        "record": artifact(review_path), "timing": artifact(timing_path),
        "existingMediaReadOnly": True, "newDownloads": False, "render": False, "tts": False,
        "continuousMotionReview": False, "actualAudioListening": False, "humanReview": False,
        "finalRightsClearance": False, "sourceScriptsChanged": False})
    write(ledger_path, ledger)
    for f in plan["scriptInputs"]:
        assert artifact(ROOT / f["path"])["sha256"] == f["sha256"]
    print(json.dumps({"episode": "A03", "review": artifact(review_path), "decodedPrimaryFrames": [838, 839], "scriptsUnchanged": True, "ttsReady": False, "productionSelectedSources": []}, ensure_ascii=False))


if __name__ == "__main__":
    main()
