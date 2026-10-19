"""Build D21's native-speed edit from measured voice timing, never estimates.

Run only after source-scene-timings.json exists. --help reads no project inputs;
--dry-run validates and reports capacity without writing an edit or MC modules.
--capacity-audit --body-seconds N gives a read-only source upper-bound report
without inventing paragraph timing or creating an exact edit.
Only the current selection's explicit editBankRanges are available; no old
game or fallback bank is inherited. Banks have id/localIn/localOut/roles/
purpose/reviewEvidence. Complete events use atomic=true and eventGuard
{localIn, localOut, meaning}; requiredSlot names the semantic slot in which
the whole event must appear. Ranges must stay inside recommendedRanges. This
does not certify continuous playback: the generated cuts still need moving QA.

Current semantic-placement.json binds the reviewed02 exchange to the actual
ASR/script hashes and preserves every bank's used prefix and unrelated slot.
--defer-annotations keeps prior annotation files intact, applies no old marks
to changed cuts, and leaves explicit native-coordinate remapping pending.

No media, audio, ASR, render, browser, Git or other-project job runs here.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/player-customization"
HERE = PROJECT / "production/reference-preserving-v3"
LOCAL = PROJECT / "production/local/reference-preserving-v3"
VOICE = ROOT / "shared/output/narration/player-customization/reference-preserving-v3"
MC = ROOT / "motion-canvas/src/projects/player-customization/revision-v3"
TIMING = VOICE / "source-scene-timings.json"
FPS, INTRO, OUTRO = 60, 120, 600
MIN_CUT = FPS
SLUG, REVISION = "player-customization", "reference-preserving-v3"
MC_VIDEO = "shared/output/motion-canvas/customization-production-v3.mp4"
KINDS = {"01": "overview", "02": "effects", "03": "tradeoffs", "04": "find",
         "05": "auto", "06": "test", "07": "appearance", "08": "conclusion"}
COUNTS = [3, 5, 5, 5, 4, 5, 4, 4]
ROLES = {"overview-greeting", "overview-shop", "overview-visible-results", "appearance-overview", "preview-shop", "choice-shop", "effects", "tradeoff-menu", "tradeoff-choice",
         "find-category", "find-equipment", "test-context", "test-build", "test-shop",
         "test-loop", "appearance", "recap-choice", "recap-mechanics", "recap-appearance"}
EXPECTED_GAMES = {"Splatoon Raiders", "The Legend of Zelda: Breath of the Wild",
                  "Animal Crossing: New Horizons"}
PROTECTED_ATOMIC_SLOTS = {"02-p1-3", "03-p1-2", "04-p1-2", "04-p3-3",
                          "06-p1-2", "06-p3-5", "07-p1-4"}


class PlanError(RuntimeError):
    """No edit is written when evidence, timing or semantic capacity is invalid."""


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def scoped(value: str | Path, owner: Path = ROOT) -> Path:
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    if not p.is_relative_to(owner.resolve()):
        raise PlanError(f"Path escapes its D21/input scope: {p}")
    return p


def require(condition: bool, message: str):
    if not condition:
        raise PlanError(message)


def guard():
    auth = read(HERE / "authorization.json")
    control_path = ROOT / "shared/publishing/video-production-control.json"
    control = read(control_path)
    require(auth.get("slug") == SLUG and auth.get("revision") == REVISION,
            "Expected the explicit selected-D21 revision authorization.")
    require(auth.get("fullProductionAuthorized") is True,
            "D21 full production is not authorized in its current record.")
    require(auth.get("automaticNextVideo") is False,
            "This builder is selected D21 only; no automatic next-video work.")
    require(auth.get("driveFinalReviewAuthorized") is True,
            "Current revision must retain its Drive final-review boundary.")
    require(set(auth.get("selectedGameSeries", [])) ==
            {"Splatoon", "Animal Crossing", "The Legend of Zelda"},
            "Expected the user's explicit three-series revision scope.")
    require(set(auth.get("selectedGameTitles", [])) == EXPECTED_GAMES,
            "Current title authorization must match Raiders, BOTW and ACNH exactly.")
    override = auth.get("nintendoCountOverride", {})
    require(override.get("generalOneThirdPolicyUnchanged") is True
            and "3of3" in override.get("target", ""),
            "Nintendo3/3 needs this revision's explicit override, not a changed general rule.")
    # A separate explicit D21 authorization is intentional. The global control
    # still belongs to M04 and must neither be overwritten nor repurposed.
    selected = control.get("selectedVideo")
    require(selected == SLUG or "Preserve" in auth.get("foreignWork", ""),
            "Foreign global selection lacks the recorded preserve-other-work scope.")
    return {"authorization": rel(HERE / "authorization.json"),
            "authorizationSha256": digest(HERE / "authorization.json"),
            "control": rel(control_path), "controlSha256": digest(control_path),
            "globalSelectedVideoPreserved": selected,
            "noControlOrForeignFilesWritten": True}


@dataclass(frozen=True)
class Bank:
    id: str
    source: str
    lo: int
    hi: int
    roles: frozenset[str]
    purpose: str
    evidence: str
    atomic: bool = False
    required_slot: str | None = None
    event: tuple[float, float, str] | None = None

    @property
    def capacity(self):
        return self.hi - self.lo


@dataclass(frozen=True)
class Slot:
    id: str
    scene: str
    lo: int
    hi: int
    role: str | None
    minimum: int
    purpose: str
    explanation_tail: int = 0
    maximum_actual: int | None = None
    required_banks: tuple[str, ...] = ()

    @property
    def capacity(self):
        return self.hi - self.lo

    @property
    def actual_capacity(self):
        cap = max(0, self.capacity - self.explanation_tail) if self.role else 0
        return min(cap, self.maximum_actual) if self.maximum_actual is not None else cap


def banks_from_sources(sources: dict) -> list[Bank]:
    """Read only explicit reviewed banks, without inheriting any v2 fallback."""
    banks = []
    for key, source in sources.items():
        rows = source.get("editBankRanges")
        require(isinstance(rows, list) and rows,
                f"{key}: explicit current editBankRanges are required; no default bank.")
        for row in rows:
            lo, hi = float(row["localIn"]), float(row["localOut"])
            roles = set(row["roles"])
            require(math.isfinite(lo) and math.isfinite(hi) and 0 <= lo < hi
                    and roles and roles <= ROLES, f"Invalid source bank: {row}")
            require(any(lo >= float(span["localIn"]) - 1e-7
                        and hi <= float(span["localOut"]) + 1e-7
                        for span in source["recommendedRanges"]),
                    f"Bank {row['id']} exceeds selected reviewed intervals.")
            require(bool(row.get("purpose")) and bool(row.get("reviewEvidence")),
                    f"Bank {row['id']} needs purpose and inspection provenance.")
            atomic = row.get("atomic", False)
            require(isinstance(atomic, bool), f"{row['id']}: atomic must be boolean.")
            required_slot = row.get("requiredSlot")
            event = row.get("eventGuard")
            if atomic:
                require(isinstance(event, dict),
                        f"{row['id']}: atomic event needs its actual before/action/result guard.")
                begin, finish = float(event["localIn"]), float(event["localOut"])
                require(math.isfinite(begin) and math.isfinite(finish)
                        and lo <= begin < finish <= hi and bool(event.get("meaning")),
                        f"{row['id']}: whole event must stay inside the bank.")
                event = (begin, finish, event["meaning"])
                require(required_slot is not None,
                        f"{row['id']}: declare requiredSlot for the mandatory complete event.")
            else:
                require(event is None and required_slot is None,
                        f"{row['id']}: eventGuard/requiredSlot require atomic=true.")
            if required_slot is not None:
                require(isinstance(required_slot, str) and required_slot,
                        f"{row['id']}: requiredSlot must identify one current semantic slot.")
            start, end = math.ceil(lo * FPS - 1e-6), math.floor(hi * FPS + 1e-6)
            require(end - start >= MIN_CUT, f"{row['id']}: subsecond bank is not usable.")
            if event:
                require(start/FPS <= event[0]+1e-7 and end/FPS >= event[1]-1e-7,
                        f"{row['id']}: frame quantization would clip the actual event.")
            allowed = {
                "Splatoon Raiders": {"overview-greeting", "overview-shop", "effects", "preview-shop",
                               "choice-shop", "tradeoff-menu", "tradeoff-choice", "test-shop",
                               "test-loop", "recap-choice", "recap-mechanics"},
                "The Legend of Zelda: Breath of the Wild": {"overview-visible-results", "find-category", "test-build",
                               "test-loop", "recap-choice", "recap-mechanics"},
                "Animal Crossing: New Horizons": {"find-equipment", "appearance", "recap-appearance"},
            }[source["game"]]
            require(roles <= allowed,
                    f"{row['id']}: role would change the selected game's verified example function.")
            banks.append(Bank(row["id"], key, start, end, frozenset(roles),
                              row["purpose"], row["reviewEvidence"], atomic,
                              required_slot, event))
    require(len({bank.id for bank in banks}) == len(banks), "Source bank IDs must be unique.")
    require_unique_ranges([
        dict(source=sources[bank.source], lo=bank.lo/FPS, hi=bank.hi/FPS, id=bank.id)
        for bank in banks])
    acnh = [bank for bank in banks
            if sources[bank.source]["game"] == "Animal Crossing: New Horizons"]
    require(acnh and sum(bank.capacity for bank in acnh) <= round(33.5*FPS),
            "ACNH useful unique bank is at most33.5s; introductory dialog is not a category action.")
    for bank in acnh:
        require(146*FPS <= bank.lo < bank.hi <= round(179.5*FPS),
                "ACNH useful action banks must stay inside LOCAL146–179.5s.")
        require(bank.roles <= {"find-equipment", "appearance"},
                "Reserve ACNH for category demonstration and main appearance; recap uses authored stills.")
    return banks


def source_identity(source):
    """Return navigation origin, never infer exact PTS from a requested cut."""
    origin = source.get("sourceTimeOriginSeconds")
    if origin is not None:
        origin = float(origin)
        uncertainty = float(source.get("sourceOriginUncertaintySeconds", 0))
        require(math.isfinite(origin) and origin >= 0 and math.isfinite(uncertainty)
                and uncertainty >= 0, "Invalid original-source navigation origin.")
        return source["sourceUrl"], origin
    return "sha256:" + source["media"]["sha256"], 0.0


def require_unique_ranges(ranges):
    for index, left in enumerate(ranges):
        for right in ranges[index+1:]:
            a, b = left["source"], right["source"]
            if a["media"]["sha256"] == b["media"]["sha256"]:
                safe = left["hi"] <= right["lo"]+1e-7 or right["hi"] <= left["lo"]+1e-7
                basis = "same-file exact LOCAL time"
            elif a["sourceUrl"] == b["sourceUrl"]:
                require(a.get("sourceTimeOriginSeconds") is not None
                        and b.get("sourceTimeOriginSeconds") is not None,
                        "Different windows of one recording need navigation origins and uncertainty.")
                _, ao = source_identity(a)
                _, bo = source_identity(b)
                au = float(a.get("sourceOriginUncertaintySeconds", 0))
                bu = float(b.get("sourceOriginUncertaintySeconds", 0))
                safe = (ao+left["hi"]+au <= bo+right["lo"]-bu+1e-7
                        or bo+right["hi"]+bu <= ao+left["lo"]-au+1e-7)
                basis = "different windows, conservative origin uncertainty"
            else:
                continue
            require(safe, f"Possible repeated original frames ({basis}): {left['id']}, {right['id']}; inspect before selecting.")


def validate_selected_sources(selected, sources):
    require(isinstance(selected.get("sources"), list) and sources
            and len(sources) == len(selected["sources"]), "Source keys must be unique.")
    require({source["game"] for source in sources.values()} == EXPECTED_GAMES,
            "Expected exactly Splatoon Raiders, BOTW and ACNH; source-window count is unrestricted.")
    for key, source in sources.items():
        require(source.get("nintendoGame") is True
                and source.get("sourceRole") == "independent-gameplay"
                and source.get("referenceLesson") is False,
                f"{key}: current independent Nintendo gameplay classification is required.")
        native = source["nativeSource"]
        width, height = native["decodedDimensions"]
        require(native.get("minimum1080Passed") is True and width >= 1920 and height >= 1080
                and native.get("noTaskUpscale") is True,
                f"{key}: genuine downloaded/decoded FHD evidence is missing.")
        require(source.get("rights") and source.get("audio"),
                f"{key}: separate recorder/publisher rights and audio decision must be retained.")
        source_identity(source)
    # Validate source-window mapping even before a measured edit exists.
    by_url = defaultdict(list)
    for source in sources.values():
        by_url[source["sourceUrl"]].append(source)
    for windows in by_url.values():
        if len({window["media"]["sha256"] for window in windows}) > 1:
            require(all(window.get("sourceTimeOriginSeconds") is not None for window in windows),
                    "One recording's multiple files need explicit navigation origins; requested starts are not exact PTS.")


def mc_credit(scene, sources):
    wanted = {
        "01": {"Splatoon Raiders"}, "02": {"Splatoon Raiders"}, "03": {"Splatoon Raiders"},
        "04": {"The Legend of Zelda: Breath of the Wild", "Animal Crossing: New Horizons"},
        "05": set(), "06": {"Splatoon Raiders", "The Legend of Zelda: Breath of the Wild"},
        "07": {"Animal Crossing: New Horizons"}, "08": EXPECTED_GAMES,
    }[scene]
    if not wanted:
        return "설명용 그림·UI: 얌얌코딩"
    credits = list(dict.fromkeys(source.get("uploaderCredit") or source["uploader"]
                                for source in sources.values() if source["game"] in wanted))
    return " · ".join(credits) + " · Nintendo / 설명: 얌얌코딩"


def measured_timing(script: dict, english: dict, spoken: dict):
    for language, document in (("ko", script), ("en", english), ("spoken-ko", spoken)):
        require(str(document.get("status", "")).startswith("locked"),
                f"Current {language} narration must be locked after source/text review.")
    require(TIMING.exists(), f"Measured timing is missing: {TIMING}. Do not estimate voice duration.")
    timing = read(TIMING)
    rows = timing["scenes"]
    require([r["id"] for r in rows] == list(KINDS), "Timing must contain only current D21 scenes01–08 in order.")
    require([len(s["lines"]) for s in script["scenes"]] == COUNTS, "Current script shape changed; review semantic slots.")
    for row, ko, en, sp in zip(rows, script["scenes"], english["scenes"], spoken["scenes"]):
        d, origin = float(row["duration"]), float(row["sourceOrigin"])
        starts = row["paragraphStarts"]
        require(math.isfinite(d) and math.isfinite(origin) and d > 0 and origin >= 0, "Invalid measured voice extent.")
        require(len(starts) == len(ko["lines"]) and all(math.isfinite(x) and 0 <= x < d for x in starts)
                and all(a < b for a, b in zip(starts, starts[1:])),
                f"Invalid measured paragraph starts: {row['id']}")
        # The full current captions/aliases, not an ending heuristic, bind timing.
        require(len(row.get("paragraphs", [])) == len(ko["lines"]),
                "Measured timing must bind all current bilingual/display/spoken paragraphs.")
        for item, kl, el, sl in zip(row["paragraphs"], ko["lines"], en["lines"], sp["lines"]):
            for field, expected in (("text", kl), ("english", el), ("spokenText", sl)):
                require(item.get(field) == expected,
                        f"Timing describes stale/missing {field}: scene{row['id']}")
    require(abs(float(rows[0]["sourceOrigin"])) < 1e-6, "Measured body must start at source origin0.")
    for a, b in zip(rows, rows[1:]):
        require(float(b["sourceOrigin"]) >= float(a["sourceOrigin"]) + float(a["duration"]) - 1 / 24000,
                "Voice scenes overlap; builder must not conceal speech.")
    body = math.ceil((float(rows[-1]["sourceOrigin"]) + float(rows[-1]["duration"])) * FPS - 1e-7)
    return timing, rows, body


def make_slots(rows, body, banks):
    slots = []
    for index, row in enumerate(rows):
        sid, origin = row["id"], float(row["sourceOrigin"])
        start = round(origin * FPS)
        end = (round(float(rows[index+1]["sourceOrigin"]) * FPS)
               if index+1 < len(rows) else body)
        paragraph = [round((origin+float(value))*FPS) for value in row["paragraphStarts"]]
        paragraph[0] = start
        def put(a, b, role, minimum, purpose, tail=0, maximum=None):
            lo = start if a == 0 else paragraph[a]
            hi = end if b is None else paragraph[b]
            require(hi > lo, f"Nonpositive semantic slot {sid}:{a}-{b}.")
            slot_id = f"{sid}-p{a+1}-{b if b is not None else len(paragraph)}"
            required = tuple(bank.id for bank in banks if bank.required_slot == slot_id)
            minimum_frames = (sum(bank.capacity for bank in banks if bank.required_slot == slot_id)
                              if minimum is None else round(minimum*FPS))
            slots.append(Slot(slot_id, sid, lo, hi, role, minimum_frames,
                              purpose, round(tail*FPS),
                              None if maximum is None else round(maximum*FPS), required))
        if sid == "01":
            put(0, 1, "overview-greeting", 3,
                "Verified Raiders customization choice introduces choosing as play; source context must match")
            put(1, 2, "overview-visible-results", 0,
                "Observed weapon use previews the promised visible-result step; retain the authored three-step overview beside the same unchanged narration",
                tail=2.5, maximum=9)
            put(2, None, "overview-shop", 2,
                "Verified Raiders choice connects directly to its inspected visible result")
        elif sid == "02":
            put(0, 3, "effects", None,
                "Actual independently verified Raiders choice followed by its visible use/result; shop/trial features are not inherited from Splatoon3")
            put(3, 4, "preview-shop", 0,
                "Verified visible choice/result clarifies preview; no unobserved hover/equip behavior")
            put(4, None, "choice-shop", 0,
                "Active choice/trial connects visible difference to reasons for choosing")
        elif sid == "03":
            put(0, 2, "tradeoff-menu", None,
                "Actual independently verified Raiders choice/result differences; weapon-specific claims remain source-bound, not inherited from Splatoon3")
            put(2, 4, None, 0,
                "Fully fictional A100/2=50 versus B40/.5=80 and one-shot90 counterexample; explanation only")
            put(4, None, "tradeoff-choice", 0,
                "Actual choice recalls distinct uses, then introduces the burden of finding equipment")
        elif sid == "04":
            put(0, 2, "find-category", None,
                "BOTW equipment categories and icons; actual sorting requires direct observation")
            put(2, 3, "find-equipment", 5.5,
                "ACNH skin→hair category and changed preview; introductory dialog is excluded", maximum=5.5)
            put(3, None, None, 0,
                "Authored illustrative sorting and starting-combination bridge; no actual game sort/auto assertion")
        elif sid == "05":
            put(0, None, None, 0,
                "Fully authored criterion→candidate→equipment→manual revision; no real-game automatic equipment")
        elif sid == "06":
            put(0, 2, "test-build", None,
                "BOTW equipment choice/equip followed by nearby actual use; exact event duration derives from inspected current banks")
            put(2, None, "test-shop", None,
                "Verified Raiders choice/use result; no inherited lobby, equip-confirmation or closed-loop assertion", tail=3)
        elif sid == "07":
            put(0, None, "appearance", 28,
                "ACNH hair→eyes→nose/cheeks→confirmed initial appearance; taste differs from strength", tail=4, maximum=28)
        else:
            put(0, 1, "recap-choice", 0,
                "Fresh actual selection details recall the choice process, not reused source frames")
            put(1, 2, "recap-mechanics", 3,
                "Fresh actual weapon/category/trial evidence recalls the taught mechanics")
            put(2, None, None, 0,
                "Authored ACNH still-based appearance recall and final question; no repeated footage", maximum=0)
    by_id = {slot.id: slot for slot in slots}
    for bank in banks:
        if bank.required_slot:
            require(bank.required_slot in by_id,
                    f"{bank.id}: unknown requiredSlot {bank.required_slot}")
            require(by_id[bank.required_slot].role in bank.roles,
                    f"{bank.id}: required event cannot serve that slot's teaching role.")
    for slot_id in PROTECTED_ATOMIC_SLOTS:
        require(slot_id in by_id and by_id[slot_id].required_banks,
                f"{slot_id}: provide an explicitly inspected mandatory atomic event; generic capacity is insufficient.")
    return slots


class Flow:
    def __init__(self, count):
        self.g = [[] for _ in range(count)]

    def edge(self, u, v, capacity):
        a, b = [v, len(self.g[v]), capacity], [u, len(self.g[u]), 0]
        self.g[u].append(a); self.g[v].append(b)
        return a

    def run(self, source, sink, limit):
        total = 0
        while total < limit:
            level = [-1] * len(self.g); level[source] = 0; q = deque([source])
            while q:
                u = q.popleft()
                for v, _, cap in self.g[u]:
                    if cap and level[v] < 0:
                        level[v] = level[u] + 1; q.append(v)
            if level[sink] < 0:
                break
            cursor = [0] * len(self.g)
            def send(u, amount):
                if u == sink:
                    return amount
                while cursor[u] < len(self.g[u]):
                    edge = self.g[u][cursor[u]]; v, rev, cap = edge
                    if cap and level[v] == level[u] + 1:
                        pushed = send(v, min(amount, cap))
                        if pushed:
                            edge[2] -= pushed; self.g[v][rev][2] += pushed
                            return pushed
                    cursor[u] += 1
                return 0
            while total < limit:
                n = send(source, limit - total)
                if not n:
                    break
                total += n
        return total


def capacity_report(banks, body_seconds):
    """Best-case upper bound only; no fabricated scene or paragraph positions."""
    body = math.ceil(body_seconds * FPS - 1e-7)
    target = round(body * .6)
    roles = sorted({r for bank in banks for r in bank.roles})
    graph = Flow(len(banks) + len(roles) + 2)
    source, sink = len(graph.g) - 2, len(graph.g) - 1
    raw = sum(b.capacity for b in banks)
    for bi, bank in enumerate(banks):
        graph.edge(source, bi, bank.capacity)
        for role in bank.roles:
            graph.edge(bi, len(banks) + roles.index(role), bank.capacity)
    # This is an upper bound, not permission to spend appearance footage
    # outside its measured category/main-appearance/recap slots.
    caps = {"appearance": 28*FPS, "find-equipment": round(5.5*FPS),
            "recap-appearance": 0}
    for ri, role in enumerate(roles):
        graph.edge(len(banks) + ri, sink, caps.get(role, raw))
    upper = graph.run(source, sink, raw)
    by_source = defaultdict(int)
    for bank in banks:
        by_source[bank.source] += bank.capacity
    return dict(mode="source-capacity-upper-bound-only; not an exact edit",
                suppliedMeasuredBodySeconds=body_seconds, frameRoundedBodySeconds=body/FPS,
                targetActualSeconds=target/FPS, targetExplanationSeconds=(body-target)/FPS,
                rawUniqueBankSeconds=raw/FPS, bestCaseRoleCompatibleUpperSeconds=upper/FPS,
                minimumAdditionalMeaningfulSourceSeconds=max(0, target-upper)/FPS,
                feasibleEvenBeforeParagraphConstraints=upper >= target,
                actualParagraphCapacity="Unknown until ASR split; may be LOWER than this upper bound.",
                sourceBankSeconds={key: count/FPS for key, count in by_source.items()},
                fullAtomicEventSeconds=sum(b.capacity for b in banks if b.atomic)/FPS,
                protectedExplanationPassages=["01-2 ordered overview", "03-3/4 fictional math and limits",
                                              "04-4/5 illustrative sorting and starting-set bridge", "05 all automatic-equipment explanation"],
                appearanceRestrictions="ACNH useful unique33.5s: category146–151.5 and main appearance151.5–179.5; recap is authored stills, not repeated footage.",
                action="Acquire/inspect additional concept-matched footage if short. Never take time from required math/auto/sorting explanations, loop, slow playback, pad idle or count upper research ranges as valid action.",
                exactCutPlanCreated=False)


def load_semantic_placement(banks, sources, timing, target, inputs):
    """Load reviewed ASR-bound placement facts, never guess timing constraints."""
    path = HERE / "semantic-placement.json"
    data = read(path)
    require((data.get("slug"), data.get("revision")) == (SLUG, REVISION)
            and data.get("status") == "reviewed-source-asr-bound-frame-preserving-semantic-pins",
            "Expected current reviewed D21 semantic-placement record.")
    expected = {
        "scriptKo": PROJECT / "script/reference-preserving-v3/narration.ko.json",
        "scriptEn": PROJECT / "script/reference-preserving-v3/narration.en.json",
        "scriptSpokenKo": PROJECT / "script/reference-preserving-v3/narration.spoken-ko.json",
        "sourceSelection": HERE / "source-selection.json",
        "measuredTiming": TIMING,
        "wholeSourceAsr": VOICE / "whole-source-asr.json",
        "scene02Words": VOICE / "asr/02.json",
    }
    require(set(data.get("bindings", {})) == set(expected), "Missing/foreign semantic-placement input.")
    for key, current in expected.items():
        entry = data["bindings"][key]
        require(scoped(entry["path"]) == current.resolve() and digest(current) == entry["sha256"],
                f"Semantic placement is stale for {key}; review changed speech/source facts before constraining its cuts.")
        if rel(current) not in {item["path"] for item in inputs}:
            inputs.append(dict(path=rel(current), sha256=entry["sha256"]))
    whole = read(expected["wholeSourceAsr"])
    scene_words = read(expected["scene02Words"])
    require(data.get("sourcePcmSha256") == timing.get("sourceSha256") == whole.get("audio_sha256")
            and whole.get("completeAudioSubmitted") is True and whole.get("noExpectedPrompt") is True,
            "Semantic placement must bind the actual whole-source ASR/PCM, never a supplied expected transcript.")
    derived = scene_words.get("derivedFrom", {})
    require(derived.get("path") == rel(expected["wholeSourceAsr"])
            and derived.get("sha256") == data["bindings"]["wholeSourceAsr"]["sha256"],
            "Scene02 words no longer derive from the bound complete source ASR.")
    require(data.get("fps") == FPS and data.get("exactTargetActualFrames") == target
            and data.get("preserveEveryBankUsedFrameTotal") is True,
            "Semantic placement cannot change source frame totals, fps or the exact target.")
    totals = data.get("bankTotals", [])
    by_id = {row["bankId"]: row for row in totals}
    require(len(totals) == len(by_id) == len(banks) and set(by_id) == {b.id for b in banks},
            "Every current bank, including unused banks, needs its original used-frame total.")
    for bank in banks:
        row = by_id[bank.id]
        require(isinstance(row["usedFrames"], int) and 0 <= row["usedFrames"] <= bank.capacity
                and row["source"] == bank.source
                and row["sourceSha256"] == sources[bank.source]["media"]["sha256"]
                and abs(float(row["bankLocalIn"])-bank.lo/FPS) < 1e-7
                and abs(float(row["bankLocalOut"])-bank.hi/FPS) < 1e-7
                and abs(float(row["selectedPrefixOut"])-(bank.lo+row["usedFrames"])/FPS) < 1e-7,
                f"Original source-prefix evidence differs for {bank.id}.")
    require(sum(row["usedFrames"] for row in totals) == target,
            "Preserved bank totals disagree with the exact actual target.")
    inputs.append(dict(path=rel(path), sha256=digest(path)))
    # The live baseline plan is provenance, not a mutable required input. The
    # explicit original bank prefixes above survive rebuilding that plan.
    data["_receipt"] = dict(path=rel(path), sha256=digest(path))
    return data


def allocate(banks, slots, target, placement):
    """Solve exact integer frames; never repair a quota with a flash fragment.

    Each compatible bank/slot pair has integer frames and a use binary. Whole
    inspected events are fixed to their declared slot. Optional blocks are zero
    or >=2 seconds, and every slot's remaining explanation is zero or >=2.5 seconds.
    First minimize used source blocks, then briefly improve explanation-bearing
    slots at that fixed optimum. This is a bank/slot-block objective, not a claim about the
    final merged movie's globally minimal edit count or semantic approval.
    """
    try:
        import numpy as np
        from scipy import __version__ as scipy_version
        from scipy.optimize import Bounds, LinearConstraint, milp
    except ImportError as exc:
        raise PlanError("Integer-frame allocation requires the existing Qwen environment's SciPy; run qwen3-tts/.venv/Scripts/python.exe. No dependency is installed here.") from exc

    optional_min, explanation_min = 2 * FPS, round(2.5 * FPS)
    require(isinstance(target, int) and target >= 0, "Actual target must be integer frames.")
    bank_by_id = {b.id: bi for bi, b in enumerate(banks)}
    slot_by_id = {s.id: si for si, s in enumerate(slots)}
    require(len(bank_by_id) == len(banks) and len(slot_by_id) == len(slots),
            "Allocation IDs must be unique.")
    required = {}
    for si, slot in enumerate(slots):
        require(0 <= slot.minimum <= slot.actual_capacity <= slot.capacity,
                f"Necessary event/minimum exceeds measured slot {slot.id}; no useful explanation may be trimmed.")
        for bank_id in slot.required_banks:
            require(bank_id in bank_by_id and bank_id not in required,
                    f"Missing/repeated mandatory event: {bank_id}")
            bi = bank_by_id[bank_id]; bank = banks[bi]
            require(bank.atomic and bank.required_slot == slot.id and slot.role in bank.roles,
                    f"Mandatory event {bank_id} has an incompatible slot/role.")
            required[bank_id] = si
    for bank in banks:
        require(not bank.atomic or bank.id in required,
                f"Atomic event {bank.id} must be declared in its actual required slot.")

    # Atomic pairs are forced whole; optional pairs exist only for the current
    # authored semantic role and have enough capacity for a readable2s block.
    pairs = []
    for bi, bank in enumerate(banks):
        for si, slot in enumerate(slots):
            if bank.atomic:
                if required[bank.id] == si:
                    pairs.append((bi, si, bank.capacity, bank.capacity, True))
            elif slot.role in bank.roles:
                upper = min(bank.capacity, slot.actual_capacity)
                if upper >= optional_min:
                    pairs.append((bi, si, optional_min, upper, False))
    require(pairs or target == 0, "No compatible whole events/readable optional source blocks.")
    pair_count = len(pairs)
    variable_count = 2 * pair_count + len(slots)
    lower = np.zeros(variable_count)
    upper = np.ones(variable_count)
    for ei, (_, _, minimum, maximum, fixed) in enumerate(pairs):
        upper[ei] = maximum
        if fixed:
            lower[ei] = maximum
            lower[pair_count + ei] = 1
    constraint_rows, lower_rows, upper_rows = [], [], []

    def constrain(coefficients, lo=-math.inf, hi=math.inf):
        row = np.zeros(variable_count)
        for index, value in coefficients.items():
            row[index] = value
        constraint_rows.append(row); lower_rows.append(lo); upper_rows.append(hi)

    for ei, (_, _, minimum, maximum, _) in enumerate(pairs):
        # minimum*y <= x <= maximum*y
        constrain({ei: 1, pair_count + ei: -minimum}, lo=0)
        constrain({ei: 1, pair_count + ei: -maximum}, hi=0)
    for bi, bank in enumerate(banks):
        constrain({ei: 1 for ei, pair in enumerate(pairs) if pair[0] == bi}, hi=bank.capacity)
    preserved_totals = {row["bankId"]: row["usedFrames"] for row in placement["bankTotals"]}
    for bi, bank in enumerate(banks):
        count = preserved_totals[bank.id]
        constrain({ei: 1 for ei, pair in enumerate(pairs) if pair[0] == bi}, lo=count, hi=count)
    pair_indices = {(bi, si): ei for ei, (bi, si, _, _, _) in enumerate(pairs)}
    changed_slots = set(placement.get("changedSlotIds", []))
    unchanged_slots = set(placement.get("unchangedSlotIds", []))
    require(placement.get("preserveUnchangedSlotAllocations") is True
            and changed_slots == {"02-p1-3", "02-p4-4"}
            and unchanged_slots == set(slot_by_id)-changed_slots,
            "The current reviewed exchange may change only the two02 semantic slots.")
    baseline_pairs = {}
    for row in placement.get("baselineBankSlotFrames", []):
        key = row["bankId"], row["slotId"]
        require(key not in baseline_pairs and key[0] in bank_by_id and key[1] in slot_by_id
                and isinstance(row["frames"], int) and row["frames"] > 0,
                "Invalid original bank/slot allocation evidence.")
        baseline_pairs[key] = row["frames"]
    for bank in banks:
        require(sum(count for (bank_id, _), count in baseline_pairs.items() if bank_id == bank.id)
                == preserved_totals[bank.id], "Original pair totals do not match the preserved bank prefix.")
    for ei, (bi, si, _, _, _) in enumerate(pairs):
        if slots[si].id in unchanged_slots:
            count = baseline_pairs.get((banks[bi].id, slots[si].id), 0)
            constrain({ei: 1}, lo=count, hi=count)
    seen_pins = set()
    for pin in placement.get("fixedBankSlotFrames", []):
        require(pin["bankId"] in bank_by_id and pin["slotId"] in slot_by_id,
                "Semantic pin refers to a missing bank/slot.")
        pair = bank_by_id[pin["bankId"]], slot_by_id[pin["slotId"]]
        require(pair in pair_indices and pair not in seen_pins,
                "Semantic pin is duplicated or incompatible with its current teaching role.")
        seen_pins.add(pair)
        ei = pair_indices[pair]
        _, _, minimum, maximum, _ = pairs[ei]
        count = pin["frames"]
        require(isinstance(count, int) and (count == 0 or minimum <= count <= maximum),
                "Semantic pin violates a whole-event or readable-cut boundary.")
        constrain({ei: 1}, lo=count, hi=count)
    for si, slot in enumerate(slots):
        source = {ei: 1 for ei, pair in enumerate(pairs) if pair[1] == si}
        constrain(source, lo=slot.minimum, hi=slot.actual_capacity)
        # z identifies a nonzero MC remainder. Existing reserved tails and
        #maximumActualFrames are already protected by actual_capacity above.
        z = 2 * pair_count + si
        constrain({**source, z: slot.capacity}, lo=slot.capacity)
        constrain({**source, z: explanation_min}, hi=slot.capacity)
    constrain({ei: 1 for ei in range(pair_count)}, lo=target, hi=target)
    bounds = Bounds(lower, upper)
    integrality = np.ones(variable_count, dtype=int)
    objective = np.zeros(variable_count)
    objective[pair_count:2 * pair_count] = 1
    def solve(cost, phase, *, time_limit=20.0, accept_limited_incumbent=False):
        result = milp(cost, integrality=integrality, bounds=bounds,
            constraints=LinearConstraint(np.asarray(constraint_rows),
                                         np.asarray(lower_rows), np.asarray(upper_rows)),
            options=dict(presolve=True, time_limit=time_limit, mip_rel_gap=0.0))
        if result.status != 0 or result.x is None:
            if accept_limited_incumbent and result.status == 1:
                if result.x is None:
                    return None, result
                # Only an independently checked feasible incumbent is useful.
                # The primary optimum and all readability constraints stay fixed.
            else:
                report = dict(phase=phase, status=int(result.status), message=result.message,
                    targetActualSeconds=target/FPS, optionalMinimumSeconds=optional_min/FPS,
                    minimumExplanationRemainderSeconds=explanation_min/FPS,
                    mandatorySeconds=sum(b.capacity for b in banks if b.atomic)/FPS,
                    sourceBankSeconds=sum(b.capacity for b in banks)/FPS,
                    slots=[dict(id=s.id, spanFrames=s.capacity, minimumActualFrames=s.minimum,
                                maximumActualFrames=s.actual_capacity) for s in slots],
                    action="Review only actual source/slot compatibility or the exact measured boundary; do not trim useful explanation/events, loop, slow playback or add flash patches.")
                raise PlanError("No proven optimal readable integer-frame allocation:\n"
                                + json.dumps(report, ensure_ascii=False, indent=2))
        rounded = np.rint(result.x).astype(int)
        require(np.max(np.abs(result.x-rounded), initial=0) < 1e-5,
                "Solver returned noninteger source frames/binaries.")
        values = np.asarray(constraint_rows) @ rounded
        require(np.all(values >= np.asarray(lower_rows)-1e-7)
                and np.all(values <= np.asarray(upper_rows)+1e-7)
                and np.all(rounded >= lower-1e-7) and np.all(rounded <= upper+1e-7),
                "Rounded solver result violates an original frame constraint.")
        return rounded, result

    first, first_result = solve(objective, "minimum-used-source-bank-slot-blocks")
    minimum_blocks = int(sum(first[pair_count:2 * pair_count]))
    constrain({pair_count+ei: 1 for ei in range(pair_count)},
              lo=minimum_blocks, hi=minimum_blocks)
    objective[:] = 0
    objective[2 * pair_count:] = 1
    candidate, second_result = solve(objective, "prefer-fewer-explanation-remainders-at-fixed-source-block-optimum",
                                    time_limit=4.0, accept_limited_incumbent=True)
    answer = first
    if candidate is not None and sum(candidate[2*pair_count:]) <= sum(first[2*pair_count:]):
        answer = candidate
    allocated = defaultdict(int)
    for ei, (bi, si, minimum, maximum, fixed) in enumerate(pairs):
        frames = int(answer[ei])
        if frames:
            require(minimum <= frames <= maximum and (not fixed or frames == banks[bi].capacity),
                    "A selected source block violates its whole-event/minimum-cut condition.")
            allocated[bi, si] = frames
    require(sum(allocated.values()) == target, "Integer allocation changed the exact60:40 target.")
    slot_summaries = []
    for si, slot in enumerate(slots):
        actual = sum(allocated[bi, si] for bi in range(len(banks)))
        remainder = slot.capacity-actual
        require(slot.minimum <= actual <= slot.actual_capacity
                and (remainder == 0 or remainder >= explanation_min),
                f"Unreadable explanation remainder or violated slot: {slot.id}")
        slot_summaries.append(dict(id=slot.id, actualFrames=actual, explanationFrames=remainder,
                                   blocks=sum(allocated[bi, si] > 0 for bi in range(len(banks)))))
    for bi, bank in enumerate(banks):
        count = sum(allocated[bi, si] for si in range(len(slots)))
        require(count <= bank.capacity, f"Source bank capacity exceeded: {bank.id}")
        require(count == preserved_totals[bank.id], f"Original used source frames changed: {bank.id}")
        if bank.atomic:
            require(count == bank.capacity and allocated[bi, required[bank.id]] == count,
                    f"Mandatory event {bank.id} was trimmed, moved or fragmented.")
    allocate.last_report = dict(method="scipy.optimize.milp", scipyVersion=scipy_version,
        exactIntegerFrameTarget=target, minimumOptionalSourceBlockFrames=optional_min,
        minimumNonzeroExplanationRemainderFrames=explanation_min,
        optimizedUsedBankSlotBlocks=minimum_blocks,
        selectedExplanationBearingSlots=int(sum(answer[2 * pair_count:])),
        objectiveOrder=["proven minimum used source bank/slot pairs", "bounded preference for fewer explanation-bearing slots at that fixed optimum"],
        objectiveLimit="Final adjacent cuts can merge; this objective is not proof of globally minimal merged movie cuts or semantic approval.",
        firstSolveStatus=int(first_result.status), secondSolveStatus=int(second_result.status),
        secondaryOptimumProven=second_result.status == 0,
        secondaryMessage=second_result.message,
        selectedSolution="secondary feasible result" if answer is candidate else "primary proven optimum retained",
        semanticPlacement=placement["_receipt"],
        originalUsedFramesPreservedForEveryBank=True,
        unchangedSlotAllocationsPreserved=True,
        semanticBankSlotPins=placement["fixedBankSlotFrames"],
        unchangedConstraints="Current bank ranges, roles, atomic required slots, voice timing, reserved explanation tails, maximum actual frames and exact60:40 target.",
        slots=slot_summaries)
    return allocated



def make_cuts(banks, slots, allocation, rows, sources, body):
    per_slot = defaultdict(list)
    # Reassign each bank's allocated frames in final timeline order so distinct
    #cuts never reuse a source frame. Required event banks have restricted roles.
    for bi, bank in enumerate(banks):
        cursor = bank.lo
        assigned = sum(allocation[bi, si] for si in range(len(slots)))
        require(not bank.atomic or assigned in (0, bank.capacity),
                f"{bank.id}: a mandatory event was prefix-sliced instead of retained whole.")
        for si, slot in enumerate(slots):
            count = allocation[bi, si]
            if count:
                per_slot[si].append((bank, cursor, count))
                cursor += count
        require(cursor <= bank.hi, f"Source capacity overflow: {bank.id}")
    # A short remainder after a complete mandatory event can continue into
    #the following paragraph's existing explanation. Move that explanation
    #to the paragraph head, rather than showing a subsecond MC flash or
    #trimming the required native action/result. The native block stays wholly
    #inside its own narration slot, and total actual/explanation is unchanged.
    explanation_heads = defaultdict(int)
    for si, slot in enumerate(slots[:-1]):
        actual = sum(allocation[bi, si] for bi in range(len(banks)))
        tail = slot.capacity-actual-explanation_heads[si]
        following = slots[si+1]
        if actual and tail > 0 and following.scene == slot.scene:
            next_gap = following.capacity-sum(allocation[bi, si+1] for bi in range(len(banks)))
            if next_gap and (tail < MIN_CUT or next_gap < MIN_CUT) and tail+next_gap >= MIN_CUT:
                explanation_heads[si+1] = next_gap
    cuts = []
    for si, slot in enumerate(slots):
        cursor = INTRO + slot.lo
        if explanation_heads[si]:
            count = explanation_heads[si]
            cuts.append(dict(scene=slot.scene, startFrame=cursor, endFrame=cursor+count,
                             frames=count, kind="explanation", visual=KINDS[slot.scene],
                             semanticSlot=slot.id, renderer="Motion Canvas",
                             placementReason="Continue the previous complete-event explanation tail using this paragraph's already allocated explanation; no new frames or source hold",
                             implementationKind="independently authored illustration and inspected gameplay stills"))
            cursor += count
        # Same-source detail→application retains native chronology. The
        # selection order also defines cross-window before→action→result order.
        source_order = {key: i for i, key in enumerate(sources)}
        per_slot[si].sort(key=lambda item: (source_order[item[0].source], item[1]))
        for bank, start, count in per_slot[si]:
            cuts.append(dict(scene=slot.scene, startFrame=cursor, endFrame=cursor+count,
                             frames=count, kind="independent-gameplay", source=bank.source,
                             sourceStart=start/FPS, sourceBankId=bank.id, sourceBankPurpose=bank.purpose,
                             semanticSlot=slot.id, semanticRole=slot.role, label=slot.purpose,
                             completeEventBlock=bank.atomic, marks=[], playbackSpeed=1, loop=False))
            cursor += count
        if cursor < INTRO + slot.hi:
            cuts.append(dict(scene=slot.scene, startFrame=cursor, endFrame=INTRO+slot.hi,
                             frames=INTRO+slot.hi-cursor, kind="explanation", visual=KINDS[slot.scene],
                             semanticSlot=slot.id, renderer="Motion Canvas",
                             implementationKind="independently authored illustration and inspected gameplay stills"))
    # Adjacent parts of the same continuing state do not need extra scene resets.
    merged = []
    for cut in cuts:
        previous = merged[-1] if merged else None
        compatible = previous and previous["endFrame"] == cut["startFrame"] and previous["scene"] == cut["scene"] and previous["kind"] == cut["kind"]
        if compatible and cut["kind"] == "explanation":
            previous["endFrame"] = cut["endFrame"]; previous["frames"] += cut["frames"]
            previous.setdefault("joinedSemanticSlots", [previous["semanticSlot"]])
            if cut["semanticSlot"] not in previous["joinedSemanticSlots"]:
                previous["joinedSemanticSlots"].append(cut["semanticSlot"])
            if cut.get("placementReason"):
                previous.setdefault("joinedPlacementReasons", []).append(cut["placementReason"])
        elif compatible and cut["kind"] == "independent-gameplay" and previous["source"] == cut["source"] and previous["sourceBankId"] == cut["sourceBankId"] and abs(previous["sourceStart"] + previous["frames"]/FPS - cut["sourceStart"]) < 1e-7:
            previous["endFrame"] = cut["endFrame"]; previous["frames"] += cut["frames"]
        else:
            merged.append(cut)
    rowmap = {r["id"]: r for r in rows}
    modules, mc_cursor, warnings = {}, 0, []
    for i, cut in enumerate(merged):
        cut["id"] = f"cut{i:02}"
        cut["clearAtSourceCut"] = True
        require(cut["frames"] >= MIN_CUT,
                f"{cut['id']} would be a {cut['frames']/FPS:.3f}s flash fragment. No plan written; review this boundary, do not stretch/hold source.")
        if cut["kind"] == "independent-gameplay":
            s = sources[cut["source"]]
            recorder = s.get("uploaderCredit") or s["uploader"]
            copyright_credit = s.get("copyrightCredit", "Game © Nintendo")
            cut.update(sourceFile=s["media"]["path"], sourceSha256=s["media"]["sha256"],
                       sourceUrl=s["sourceUrl"], game=s["game"], genre=s["genre"], nintendoGame=s.get("nintendoGame", False),
                       credit=dict(text=s["game"] + " · " + recorder, position=[24, 16], fontSize=23),
                       creditRoles=dict(game=s["game"], originalRecorder=recorder, rightsHolderNotice=copyright_credit),
                       copyrightCredit=copyright_credit, viewport=[0, 0, 1920, 900], aspectFit="contain",
                       sourceNativeFps=s["nativeSource"].get("fps"),
                       sourceAudioEnabled=False,
                       audioExclusionReason="Unreviewed inseparable game soundtrack is muted; original bytes retained. Approved quiet Nimbus is a separate game-design music layer.",
                       editorialUse="Necessary concept-matched critical/educational quotation with original analysis and credit; publisher/recorder conditions remain separately recorded.")
            lo, hi = cut["sourceStart"], cut["sourceStart"]+cut["frames"]/FPS
            bank = next(bank for bank in banks if bank.id == cut["sourceBankId"])
            cut["sourceEventsIncluded"] = ([bank.event[2]] if bank.event
                and lo <= bank.event[0]+1e-7 and hi >= bank.event[1]-1e-7 else [])
            if bank.atomic:
                require(cut["sourceEventsIncluded"],
                        f"{bank.id}: complete event guard is absent from the actual cut.")
            cut["sourceContentMode"] = s.get("sourceContentMode", s.get("teachingRole", ""))
            cut["notEstablished"] = s.get("notEstablished", [])
            if s.get("sourceStateSamples"):
                cut["sourceStateSamples"] = [sample for sample in s["sourceStateSamples"]
                                              if lo <= float(sample["localSeconds"]) < hi]
            if s.get("annotationStateRule"):
                cut["annotationStateRule"] = s["annotationStateRule"]
            identity, offset = source_identity(s)
            cut["originalRecordingIdentity"] = identity
            cut["originalRecordingNavigationStartSeconds"] = offset + lo
            cut["sourceTimeOriginSeconds"] = offset
            cut["sourceOriginUncertaintySeconds"] = float(s.get("sourceOriginUncertaintySeconds", 0))
            cut["originalMappingIsFrameExact"] = bool(s.get("sourceOriginFrameExact", False))
            cut["navigationOriginIsNotExactCutEvidence"] = not cut["originalMappingIsFrameExact"]

        else:
            row = rowmap[cut["scene"]]
            local_start = (cut["startFrame"]-INTRO)/FPS - float(row["sourceOrigin"])
            cues = [float(x)-local_start for x in row["paragraphStarts"]]
            cut.update(cues=cues, narrationSceneLocalStart=local_start,
                       renderedSource=MC_VIDEO, renderedStartFrame=mc_cursor,
                       mcStartFrame=mc_cursor, mcEndFrame=mc_cursor+cut["frames"],
                       renderStatus="pending root render", credit=mc_credit(cut["scene"], sources))
            mc_cursor += cut["frames"]
            name = "production-" + cut["id"]
            payload = dict(duration=(cut["frames"]-.75)/FPS, cues=cues, credit=mc_credit(cut["scene"], sources))
            modules[name] = ("import {makeScene2D} from '@motion-canvas/2d';\n"
                             "import {lesson} from './visuals';\n"
                             "export default makeScene2D(function*(view){yield* lesson(view,"
                             + json.dumps(cut["visual"]) + "," + json.dumps(payload, ensure_ascii=False) + ");});\n")
    require(merged and merged[0]["startFrame"] == INTRO and merged[-1]["endFrame"] == INTRO+body,
            "The edit must cover the measured body, excluding the original2s/10s branding/member clips.")
    for a, b in zip(merged, merged[1:]):
        require(a["endFrame"] == b["startFrame"], f"Body gap/overlap: {a['id']}, {b['id']}")
    require_unique_ranges([
        dict(source=sources[cut["source"]], lo=cut["sourceStart"],
             hi=cut["sourceStart"]+cut["frames"]/FPS, id=cut["id"])
        for cut in merged if cut["kind"] == "independent-gameplay"])
    for slot in slots:
        for bank_id in slot.required_banks:
            bank = next(b for b in banks if b.id == bank_id)
            matching = [c for c in merged if c.get("sourceBankId") == bank_id]
            require(len(matching) == 1 and abs(matching[0]["sourceStart"]-bank.lo/FPS)<1e-7
                    and matching[0]["frames"] == bank.capacity,
                    f"Required event {bank_id} is incomplete or spread into disconnected fragments.")
    return merged, modules, mc_cursor, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate measured timing/source capacity without writing any output")
    parser.add_argument("--defer-annotations", action="store_true", help="Preserve existing annotation files, apply no marks to the new plan, and leave explicit remapping pending")
    parser.add_argument("--capacity-audit", action="store_true", help="Read-only best-case source bound, without loading ASR paragraph timing")
    parser.add_argument("--body-seconds", type=float, help="Measured complete narration duration for --capacity-audit only")
    args = parser.parse_args(argv)
    if args.capacity_audit:
        require(args.body_seconds is not None and math.isfinite(args.body_seconds) and args.body_seconds > 0,
                "--capacity-audit needs a positive measured --body-seconds; no paragraph duration is estimated.")
    else:
        require(args.body_seconds is None, "--body-seconds is not an edit-timing override; use only with --capacity-audit.")
    authorization = guard()
    selected_path = HERE / "source-selection.json"
    selected = read(selected_path)
    require(selected.get("slug") == SLUG and selected.get("revision") == REVISION and selected.get("referenceOnlyMediaExcluded") is True,
            "Expected the independent, current D21 source selection.")
    sources = {s["key"]: s for s in selected["sources"]}
    validate_selected_sources(selected, sources)
    if args.capacity_audit:
        print(json.dumps(capacity_report(banks_from_sources(sources), args.body_seconds), ensure_ascii=False, indent=2))
        return
    ko_path = PROJECT / "script/reference-preserving-v3/narration.ko.json"
    en_path = PROJECT / "script/reference-preserving-v3/narration.en.json"
    sp_path = PROJECT / "script/reference-preserving-v3/narration.spoken-ko.json"
    aliases_path = PROJECT / "script/reference-preserving-v3/caption-aliases.json"
    script, english, spoken = read(ko_path), read(en_path), read(sp_path)
    timing, rows, body = measured_timing(script, english, spoken)
    inputs = []
    for p in [Path(__file__), TIMING, ko_path, en_path, sp_path, aliases_path,
              selected_path, HERE/"script-audit.json"]:
        inputs.append(dict(path=rel(p), sha256=digest(p)))
    current_pcm = VOICE / "narration-source.wav"
    require(current_pcm.exists() and digest(current_pcm) == timing.get("sourceSha256"),
            "Current measured timing is not bound to the current assembled narration PCM.")
    inputs.append(dict(path=rel(current_pcm), sha256=timing["sourceSha256"]))
    script_audit = read(HERE/"script-audit.json")
    audited_scripts = {x["path"]: x["sha256"] for x in script_audit["inputs"]}
    for p in [ko_path, en_path, sp_path]:
        require(audited_scripts.get(rel(p)) == digest(p),
                f"Current script differs from the completed semantic audit: {p}; review the changed paragraphs/joins first.")
    # Reuse the source inspection evidence; don't rerun download/decode/ASR here.
    for entry in selected.get("inputAudits", []):
        p = scoped(entry["path"], PROJECT)
        require(digest(p) == entry["sha256"], f"Source audit changed since selection: {p}")
        inputs.append(dict(path=rel(p), sha256=entry["sha256"]))
    for key, source in sources.items():
        native = source["nativeSource"]
        require(source.get("sourceRole") == "independent-gameplay" and source.get("referenceLesson") is False,
                f"Reference/non-independent media cannot enter the edit: {key}")
        require(native.get("minimum1080Passed") is True and native["decodedDimensions"][0] >= 1920 and native["decodedDimensions"][1] >= 1080,
                f"Independent FHD dimensions were not verified: {key}")
        # A selected, hash-pinned pre-existing recording may be read from a
        # sibling inventory (for example a selected retained independent raw file). This
        # builder never writes to source paths or another project's outputs.
        media = scoped(source["media"]["path"])
        require(media.exists() and digest(media) == source["media"]["sha256"], f"Source bytes no longer match selection: {key}")
        if rel(media) not in {item["path"] for item in inputs}:
            inputs.append(dict(path=rel(media), sha256=source["media"]["sha256"]))
    banks = banks_from_sources(sources)
    slots = make_slots(rows, body, banks)
    target = round(body * .6)
    placement = load_semantic_placement(banks, sources, timing, target, inputs)
    allocation = allocate(banks, slots, target, placement)
    cuts, modules, mc_frames, warnings = make_cuts(banks, slots, allocation, rows, sources, body)
    actual = sum(c["frames"] for c in cuts if c["kind"] == "independent-gameplay")
    require(actual == target and abs(actual-body*.6) <= 1, "Actual/explanation body ratio escaped one-frame tolerance.")
    games = {c["game"] for c in cuts if c["kind"] == "independent-gameplay"}
    nintendo = {c["game"] for c in cuts if c.get("nintendoGame")}
    require(games == EXPECTED_GAMES and nintendo == EXPECTED_GAMES,
            "Current revision must meaningfully demonstrate exactly three selected Nintendo games, counted once each.")
    branding = ROOT / "projects/game-reward-planning/production/local/reference-preserving-v2/edit/branding.mp4"
    membership = branding.with_name("membership.mp4")
    require(branding.exists() and membership.exists(), "Original approved2s branding/10s member clips must be restored, not fabricated.")
    plan = dict(schemaVersion=1, slug=SLUG, revision=REVISION, fps=FPS, width=1920, height=1080,
                timing="measured source-scene-timings; no estimated narration", inputTiming=rel(TIMING),
                inputTimingSourceSha256=timing.get("sourceSha256"), inputs=inputs, authorization=authorization,
                bodyFrames=body, totalFrames=body+INTRO+OUTRO, brandingFrames=INTRO, outroFrames=OUTRO,
                brandingFile=rel(branding), membershipFile=rel(membership),
                brandingSha256=digest(branding), membershipSha256=digest(membership),
                actualFrames=actual, explanationFrames=body-actual, mcFrames=mc_frames,
                allocationReview=allocate.last_report,
                expectedGameplayShare=.6, ratioToleranceFrames=1,
                outputDir=rel(LOCAL/"edit"), outputStem="player-customization-v3",
                captionAliases=read(aliases_path),
                scenes=[dict(id=r["id"], voiceStart=2+float(r["sourceOrigin"]), voiceDuration=r["duration"],
                             startFrame=INTRO+math.floor(float(r["sourceOrigin"])*FPS+1e-7),
                             endFrame=INTRO+math.ceil((float(r["sourceOrigin"])+float(r["duration"]))*FPS-1e-7),
                             visualStartFrame=INTRO+round(float(r["sourceOrigin"])*FPS),
                             visualEndFrame=INTRO+(round(float(rows[i+1]["sourceOrigin"])*FPS) if i+1<len(rows) else body),
                             paragraphStarts=r["paragraphStarts"]) for i, r in enumerate(rows)], cuts=cuts,
                sceneFrameConvention="scenes.startFrame/endFrame are floor(start)/ceil(PCM end) audio envelopes; adjacent envelopes may overlap by one frame. visualStartFrame/visualEndFrame and cuts use contiguous rounded boundaries. These are different purposes, never PCM trimming.",
                sourceBankPolicy="Narrow inspected concept-matched banks; not the full upper research intervals",
                sourceBanks=[dict(id=b.id, source=b.source, localIn=b.lo/FPS, localOut=b.hi/FPS,
                                  roles=sorted(b.roles), purpose=b.purpose, reviewEvidence=b.evidence,
                                  wholeEventRequired=b.atomic, requiredSlot=b.required_slot,
                                  eventGuard=(dict(localIn=b.event[0], localOut=b.event[1], meaning=b.event[2])
                                              if b.event else None)) for b in banks],
                semanticSlots=[dict(id=s.id, scene=s.scene, bodyStartFrame=s.lo, bodyEndFrame=s.hi,
                                    role=s.role, minimumActualFrames=s.minimum,
                                    maximumActualFrames=s.maximum_actual, requiredEventBanks=list(s.required_banks),
                                    reservedExplanationTailFrames=s.explanation_tail, purpose=s.purpose) for s in slots],
                audio=dict(targetLufs=-16, voicePeakDbfs=-2.5, musicLufs=-31, gameRmsDbfs=-33,
                           matchSceneRms=False, preserveGameAudio=False,
                           gameAudioDecision="Unreviewed inseparable OST muted, not claimed as separated SFX.",
                           music=dict(path="shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3",
                                      sha256="06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08",
                                      licenseRecord="shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md",
                                      title="Nimbus", artist="Eveningland")),
                motionCanvasFrameConvention="Each module endpoint=(requestedFrames-.75)/60; root must verify actual rendered frame span before using the concatenated output.",
                negativeParagraphCuesPreserved=True, narrationPcmPreserved=True,
                narrationPreservationMeaning="Current assembled narration PCM is not modified by editing; original unchanged ranges are evidenced separately in voice-reuse-plan.json.",
                sourceIntervalsUnique=True,
                sourceWindowUniquenessBasis="Same-file exact LOCAL intervals; different files from one URL compared conservatively with recorded navigation-origin uncertainty, never asserted exact PTS.",
                noLoops=True, noSlowdown=True, noSourceFrameHolds=True,
                gameExampleCoverage=dict(mainGames=sorted(games), nintendoGames=sorted(nintendo),
                                         fraction=len(nintendo)/len(games), countBasis="Distinct meaningfully taught game, once each; separate from time ratio",
                                         revisionOnlyOverride=read(HERE/"authorization.json")["nintendoCountOverride"],
                                         generalOneThirdPolicyUnchanged=True),
                annotationsReview="pending root native-coordinate marks and moving QA", humanWholeListening="pending",
                renderStatus="pending", shortCutReviewWarnings=warnings, youtubeUploadAuthorized=False,
                automaticNextVideo=False, baselineReplacementOrDeletionAuthorized=False)
    annotation = HERE / "source-annotations.json"
    if annotation.exists() and args.defer_annotations:
        # Exact cut geometry/timing is changing. Keep the previous native/ASS
        #evidence intact, never transfer coordinates by a coincidental cut ID.
        plan["deferredAnnotationSource"] = dict(path=rel(annotation), sha256=digest(annotation),
            action="Existing file preserved and not applied; remap the inspected native targets against these new cuts.")
        plan["annotationsReview"] = "pending explicit annotation remap; --defer-annotations applied no previous marks"
        require(all(not cut.get("marks") for cut in cuts), "Deferred plan must have no transplanted marks.")
    elif annotation.exists():
        by_id = {c["id"]: c for c in cuts}
        for item in read(annotation)["annotations"]:
            c = by_id[item["cutId"]]
            require(c["kind"] == "independent-gameplay" and
                    (c["sourceSha256"], c["sourceStart"], c["frames"], c["viewport"], c.get("sourceCrop")) ==
                    (item["sourceSha256"], item["sourceStartSeconds"], item["cutFrames"], item["viewport"], item.get("sourceCrop")),
                    f"Annotation is stale for {item['cutId']}; don't transplant old target coordinates.")
            c["marks"].append(item["mark"])
        plan["annotationSource"] = rel(annotation)
        plan["annotationsReview"] = "root-authored source-bound coordinates loaded; realized moving/caption review still pending"
    summary = dict(bodySeconds=body/FPS, totalSeconds=plan["totalFrames"]/FPS,
                   actualSeconds=actual/FPS, explanationSeconds=(body-actual)/FPS,
                   cuts=len(cuts), motionCanvasFrames=mc_frames, warnings=warnings,
                    sourceBankCapacitySeconds=sum(b.capacity for b in banks)/FPS,
                    allocation=allocate.last_report,
                    annotationsDeferred=args.defer_annotations,
                   written=not args.dry_run)
    if not args.dry_run:
        # Validate everything before the first mutation. Only the D21 plan and
        #D21 revision module directory are written; existing unrelated files stay.
        for item in inputs:
            require(digest(scoped(item["path"])) == item["sha256"], "Input changed during planning; rebuild against the new snapshot.")
        latest_authorization = guard()
        require(latest_authorization["authorizationSha256"] == authorization["authorizationSha256"],
                "D21 authorization changed during planning; no output written.")
        MC.mkdir(parents=True, exist_ok=True)
        for name, content in modules.items():
            (MC/(name+".tsx")).write_text(content, encoding="utf-8")
        project_text = "import {makeProject} from '@motion-canvas/core';\n"
        project_text += "\n".join(f"import s{i} from './{name}?scene';" for i, name in enumerate(modules))
        project_text += "\nexport default makeProject({scenes:[" + ",".join(f"s{i}" for i in range(len(modules))) + "]});\n"
        (MC/"production-project.ts").write_text(project_text, encoding="utf-8")
        (HERE/"edit-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (PlanError, FileNotFoundError, KeyError, ValueError) as exc:
        raise SystemExit(f"D21 edit plan not written: {exc}") from exc
