"""Persist the independent, manually read source/script audit for BOTW v4."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
P = ROOT / "projects/kind-to-beginners"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(source, start, end, observation):
    return {"sourceId": source, "localSeconds": [start, end], "observation": observation}


def main():
    ko_path = P / "script/botw-v4/narration.ko.json"
    en_path = P / "script/botw-v4/narration.en.json"
    spoken_path = P / "script/botw-v4/narration.spoken-ko.txt"
    ko = json.loads(ko_path.read_text(encoding="utf-8-sig"))
    en = json.loads(en_path.read_text(encoding="utf-8-sig"))
    # This is a manual audit record, not an automatic semantic validator.
    # If the reviewed opening has changed, stop for a fresh direct read.
    assert ko["scenes"][0]["lines"][0].startswith("추위에 대비한 음식을 먹자 보호 효과와 남은 시간이 표시됩니다.")
    assert en["scenes"][0]["lines"][0].startswith("Eating food that protects against the cold displays its protective effect and remaining time.")
    assert [len(s["lines"]) for s in ko["scenes"]] == [2,3,3,3,3,3,3,3]
    assert [len(s["lines"]) for s in en["scenes"]] == [2,3,3,3,3,3,3,3]
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    source_map = {s["id"]: s for s in sources["sources"]}
    rows = [
      ("01", [
        ("Actual-game abstract: prepared food, active protection, then warning/exploration, agency thesis and ordered overview.", [evidence("botw-cold-food",4,40,"Menu gauge, food selection/Eat, effect timer, warning AFTER eating, snowy movement.")], "Opening was corrected during audit to food→effect→later warning and directly re-read in both languages. Preserve this actual source chronology in the edit; do not imply the warning caused the already-completed eating action."),
        ("Kindness protects attempts and discovery; observer and beginner can have different goals.", [], "Independent design interpretation, not measured recorder intent. Carries the first outcome into scene02.")]),
      ("02", [
        ("Explicitly imagined friend/observer scenario; BOTW is Link's single-player world exploration; pickup and climbing are early actions.", [evidence("botw-opening",32,64,"Playable world movement and mushroom acquisition."),evidence("botw-cold-expiry",0,11,"Climbing snowy ruins.")], "The narration says imagine; never identify the independent recorder as a beginner or friend."),
        ("Expert route efficiency and beginner discovery are different possible goals.", [evidence("botw-opening",50,83,"Pickup and continued self-directed travel."),evidence("botw-exploration",0,24,"Movement through ruins.")], "Inference/example about possible goals, not a measured emotion or proof that this recorder was instructed."),
        ("Agree what the newcomer wants before supplying the full solution.", [], "Preserves the source's unknown-opponent-intent lesson via user-authorized solo observer substitution; no claim BOTW has multiplayer competition.")]),
      ("03", [
        ("Full-strength competition is appropriate when both want a serious contest.", [], "Must be rendered as an explicitly general competitive-game principle, separated from BOTW gameplay. No BOTW race/fighting labels."),
        ("A casual first BOTW attempt can use one small pickup as its goal.", [evidence("botw-opening",50,64,"Approach mushroom, Take prompt, first Hylian Shroom result.")], "One visible action and result suffice; no invented scoring or success rate."),
        ("Pickup input produces an acquisition result and invites the next self-directed action.", [evidence("botw-opening",50,64,"Native normal-speed pickup and item panel.")], "Show the prompt, action, and actual result; a later Korok dialog must not be substituted for mushroom pickup feedback.")]),
      ("04", [
        ("Defines onboarding plainly: reducing unfamiliar controls/rules before first enjoyment.", [], "Definition plus authored illustration; do not present a new BOTW automated assist feature."),
        ("Applies to competitive and single-player games; action, visible result, then added step.", [], "Matches the reference's explicit competitive/solo first-contact principle."),
        ("Great Plateau cold warning, menu thermometer, hearts, and conditional cold-health consequence.", [evidence("botw-cold-food",4,9,"Thermometer actually visible in inventory; field Pro HUD hides it."),evidence("botw-cold-food",13.8,18,"Low-temperature warning appears while protected.")], "Cold damage is a verified game rule, not observed health loss in these clips. Use menu frame for gauge callout and labelled illustration for unprotected loss; never fabricate gameplay HUD or damage rate.")]),
      ("05", [
        ("Cold Resistance increases cold tolerance; eat qualifying food, then see active protection and remaining time while exploring.", [evidence("botw-cold-food",9,13.8,"Spicy Sauteed Peppers selection, Eat, ingestion, Cold Resistance05:00."),evidence("botw-cold-food",18,40,"Snow traversal with decreasing timer.")], "The icon is an hourglass followed by05:00, not1:05:00. No mod claim. The narration does not prescribe a numerical duration or claim all food protects."),
        ("Warm Doublet provides protection while worn; distinguish timed food from clothing.", [evidence("botw-warm-doublet",6,12,"Warm Doublet item panel explicitly shows Cold Resistance."),evidence("botw-warm-doublet",23.8,27.4,"Actual Armor menu, Equip at25.2, model changes25.8, field26.4."),evidence("botw-cold-expiry",18,39.8,"Food timer goes00:03 to absent; doublet stays equipped and three hearts remain while walking in snow.")], "The fast Equip menu is about2.2s: retain1x and explain beside it rather than slowing it. Earlier dressed traversal still has a food buff and alone cannot isolate clothing protection. Do not imply one garment protects every possible cold region; selected Great Plateau context bounds the claim."),
        ("Explain signals and available responses, then return preparation and route choices.", [evidence("botw-free-exploration",0,31,"Glide, land, run/jump; visible self-controlled exploration.")], "Agency is the design interpretation; no fabricated player thoughts or optimized route measurement.")]),
      ("06", [
        ("Unpacking takes possessions out of boxes and places them in a new home.", [evidence("unpacking-launch",33,42,"Cursor places kitchen possessions.")], "Retained original source inspection; official publisher trailer game-screen passages only, not claimed raw new capture."),
        ("No required button-hold, simultaneous buttons, or time limit; objects can be moved again.", [evidence("unpacking-launch",64,73,"Visible item relocation and cleared bed.")], "No-hold/no-multi-button/no-timer facts come from the developer's accessibility page; the trailer does not itself prove physical button state or a settings toggle."),
        ("Light controls retain placement choice; dictating every location leads to overguidance.", [evidence("unpacking-launch",33,42,"Actual objects remain where placed.")], "Does not claim all placements satisfy the puzzle; optional Allow items anywhere is not asserted.")]),
      ("07", [
        ("Constant instructions reduce opportunities for personal choice.", [], "Source's overguidance point; corresponding illustration must keep orders visible while the line describes following orders."),
        ("A Short Hike walking/climbing/gliding supports choosing a visible destination.", [evidence("hike-walk",0,18.9,"Developer walking B-roll."),evidence("hike-climbing",0,17.1,"Developer climbing B-roll."),evidence("hike-glide",0,29.1,"Developer gliding B-roll.")], "Retain independently reviewed official press sources; route marks are editorial choices, not game detection or measured attention."),
        ("Announcing all destinations can remove discovery; step back after needed help.", [], "Instruction release belongs here, not prematurely in the prior paragraph; preserves original source order.")]),
      ("08", [
        ("Initial interest is hard to obtain; protect it from confusion or endless orders.", [], "Retains source conclusion and returns to the same thesis."),
        ("Shared goal, lighter first controls, then returned choices.", [], "Restates the demonstrated sequence; not an empirical guarantee that every newcomer continues."),
        ("Games are for enjoyment and self-chosen further play.", [], "KO/EN meanings aligned; no creator attribution, borrowed personal experience, or spoken promotional CTA.")])
    ]
    scenes = []
    for sid, paragraphs in rows:
        ks = next(s for s in ko["scenes"] if s["id"] == sid)
        es = next(s for s in en["scenes"] if s["id"] == sid)
        result = []
        for i, (claim, observations, constraint) in enumerate(paragraphs):
            result.append({"paragraphId": f"{sid}-p{i+1:02d}", "koText": ks["lines"][i], "enText": es["lines"][i], "claimReview": claim, "evidence": observations, "result": "text-and-source-feasibility-pass", "realizationConstraint": constraint})
        scenes.append({"id": sid, "paragraphs": result})
    inputs = [ko_path,en_path,spoken_path,HERE/"production-plan.json",HERE/"sources.json",HERE/"audio-source-review.json",P/"production/local/batch-v1/research/R7rd4-ua2AI.en.json3"]
    record = {
      "schemaVersion":1,"slug":"kind-to-beginners","revision":"botw-v4",
      "reviewer":"independent-source-and-text-audit-agent","reviewedAt":datetime.now(timezone.utc).isoformat(),
      "status":"text-facts-and-source-feasibility-pass-with-realization-constraints",
      "scope":{"completeKoJsonRead":True,"completeEnJsonRead":True,"completeKoSpokenTextRead":True,"englishSpokenFileExists":False,"englishReviewedFrom":"narration.en.json","sceneCount":8,"paragraphCount":23,"completeReferenceCaptionTextRead":True,"directSourcePixelReview":"Eight BOTW sources: sampled contact sheets plus dense native menu/effect transitions reviewed in this task; exact observations and proof hashes in sources.json.","referenceVisualEvidence":"Existing complete1fps review retained from production plan; not represented as a fresh whole reference rewatch.","newDownload":False,"newRender":False,"actualAudioListeningPerformed":False,"humanWholeReview":"pending"},
      "inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in inputs],
      "primaryFactSources":[
        {"url":"https://www.piggyback.com/online-guide/the-legend-of-zelda/en/","kind":"official licensed BOTW guide","reviewedSections":["On-screen Display: Temperature","Weather & Elements: Low Temperatures","Great Plateau warm doublet/cold route"],"confirmed":"The gauge describes ambient temperature. Unprotected cold can reduce hearts. Food gives timed cold resistance; suitable equipped clothing provides protection. Stronger cold may require a higher level."},
        {"url":"https://www.unpackinggame.com/","kind":"developer primary site; indexed Accessibility section retrieved","confirmed":"Required actions do not need button holds or simultaneous buttons. No timer or penalty for missteps. Item placement can be revised.","fetchLimit":"Direct page open timed out; primary-domain indexed text was returned and matched retained source facts."},
        {"url":"https://www.nintendo.com/kr/zelda/totk/guide/index.html","kind":"official Korean localization corroboration only","confirmed":"Uses the Korean effect name 추위 가드.","limit":"TOTK page is not evidence of BOTW footage or exact BOTW Korean UI. BOTW English Cold Resistance and Warm Doublet were directly read in the selected video; Korean 방한복 remains root-selected glossary spelling without a new Korean-menu capture."}
      ],
      "teachingBackbone":{"referenceUrl":"https://www.youtube.com/watch?v=R7rd4-ua2AI","researchOnly":True,"fullCaptionDirectRead":True,"claimOrderPreserved":True,"mapping":[{"range":"0:04–1:43","scenes":["01","02"],"meaning":"Unknown other-person intent; expertise can remove newcomer participation.","adaptation":"Explicit imagined observer/solo beginner scenario under the user-selected BOTW replacement."},{"range":"1:44–1:55","scenes":["03"],"meaning":"Serious competition is respectful when mutually wanted; remains generic competition."},{"range":"1:56–2:15","scenes":["04","05","06"],"meaning":"Gently lower first-contact barriers in competitive and solo play."},{"range":"2:16–2:32","scenes":["07"],"meaning":"Too much instruction removes freedom and interest."},{"range":"2:35–2:46","scenes":["08"],"meaning":"Protect fragile initial interest and self-directed enjoyment."}],"omittedNoninstructionalDetails":["Reference creator's50-win personal history, named combo, specific arcade couple biography, decision to stop random matches, closing self-deprecating joke."],"omissionReason":"Personal history is not reattributed to our narrator; underlying mismatch and agency lessons remain. No reference footage enters production."},
      "textChecks":{"koEnMeaningAligned":True,"chapterLinksConcrete":True,"noCreatorOrSourceFramingInNarration":True,"noBorrowedBiographyAsOurs":True,"noObservedColdDamageClaim":True,"noInventedTemperatureDamageRateOrDuration":True,"noBotwMultiplayerClaim":True,"noSpokenAdvertisingCta":True},
      "scenes":scenes,
      "reportedPlanCorrections":[{"field":"sourceToScriptMap[0].added","issue":"Stale race goal/steering success wording.","action":"Asked content owner to replace with current observer goal/pickup action."},{"field":"sourceToScriptMap[1].added","issue":"Stale input→corner wording.","action":"Asked content owner to replace with pickup→acquisition→next action."},{"field":"previousCompletedEpisodeComparison.newGenres","issue":"Stale kart racing entry.","action":"Update to BOTW open-world action adventure without claiming BOTW and A Short Hike are wholly different genres."},{"field":"chapterLinks 04→05, glossary and pendingEvidence","issue":"Shivering/Normal HUD and pending exact-footage status exceed or lag current observations.","action":"Menu gauge and warning verified; actual cold-health-loss absent; retain labelled principle illustration distinction and current source IDs/times."}],
      "remainingRealizationChecks":["Keep food→effect→later warning chronology honest in actual abstract.","03 general competitive principle must not appear to describe BOTW multiplayer.","04 actual thermometer callout belongs to menu only; loss belongs to labelled principle illustration.","05 preserve normal-speed Equip, correctly show worn model and timed-food expiry; avoid claiming earlier simultaneous food+clothes shot isolates clothing.","Measure speech/caption/target alignment and actual60:40 after timing, without duplicate/idle padding.","Review actual final audio, native motion, captions1080/375, and final source-audio mix separately."],
      "sourceSchemaNormalization":{"changedSource":"unpacking-launch","other11EntriesUnchanged":True,"freshProbe":"1920x1080 h26430fps; AAC44100Hz stereo;118.096689s","retainedAudioDecision":True,"originalMediaUnchanged":True,"all12SourcesRequiredSchemaValidated":True},
      "termReviewResolution":"Root accepted the directly observed canonical English first display with the current Korean explanation labels. No additional source hunt or separate approval is needed.",
      "ttsFactReadiness":{"sourceFactsSufficient":True,"bothLanguagesDirectlyRead":True,"openingChronologyCorrected":True,"newSourceHuntNeeded":False,"meaning":"This evidence supports the root/content owner setting TTS-ready within the existing authorized workflow; final voice and video still require their ordinary actual-output QA."},
      "doesNotAssert":["Final edit has passed pixel or whole audio review","Human has watched or listened","Actual recorded cold damage","Switch-hardware recording","Platform upload completion"]
    }
    out = HERE / "source-script-review.json"
    with out.open("x",encoding="utf-8") as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(json.dumps({"path":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"paragraphsReviewed":23,"status":record["status"]}))


if __name__ == "__main__":
    main()
