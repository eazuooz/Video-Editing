"""Build D21's native-speed edit from measured voice timing, never estimates.

Run only after source-scene-timings.json exists. --help reads no project inputs;
--dry-run validates and reports capacity without writing an edit or MC modules.
--capacity-audit --body-seconds N gives a read-only source upper-bound report
without inventing paragraph timing or creating an exact edit.
The default banks are deliberately narrower than source-selection's upper
research ranges. A root-reviewed source may replace its defaults by recording
editBankRanges: [{id, localIn, localOut, roles, purpose, reviewEvidence}].
Those ranges must stay inside that source's selected recommendedRanges. This
does not certify continuous playback: the generated cuts still need moving QA.

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
HERE = PROJECT / "production/reference-preserving-v2"
LOCAL = PROJECT / "production/local/reference-preserving-v2"
VOICE = ROOT / "shared/output/narration/player-customization/reference-preserving-v2"
MC = ROOT / "motion-canvas/src/projects/player-customization/revision-v2"
TIMING = VOICE / "source-scene-timings.json"
FPS, INTRO, OUTRO = 60, 120, 600
MIN_CUT = FPS
SLUG, REVISION = "player-customization", "reference-preserving-v2"
MC_VIDEO = "shared/output/motion-canvas/customization-production-v2.mp4"
KINDS = {"01": "overview", "02": "effects", "03": "tradeoffs", "04": "find",
         "05": "auto", "06": "test", "07": "appearance", "08": "conclusion"}
COUNTS = [3, 5, 5, 5, 4, 5, 4, 4]
MAIN_KEYS = {"jets2-shop", "acvi-assembly", "botw-menu", "mh-menu",
             "terratech-build", "acnh-appearance"}
ROLES = {"overview-greeting", "overview-shop", "appearance-overview", "preview-shop", "choice-shop", "effects", "tradeoff-menu", "tradeoff-choice",
         "find-category", "find-equipment", "test-context", "test-build", "test-shop",
         "test-loop", "appearance", "recap-choice", "recap-mechanics", "recap-appearance"}
ATOMIC_BANKS = {"jets-blackfist-event", "acvi-booster-numbers", "acvi-equip-confirm", "botw-category-equip",
                "mh-part-icons", "mh-preview", "terra-wheel-drill", "terra-drive-edit"}
# These complete before/action/result blocks cannot be replaced by a prefix.
EVENT_GUARDS = {
    "jets-blackfist-event": (140, 148, "Blackfist purchase/equip140–146 with visible test-pattern result retained"),
    "acvi-booster-numbers": (154.8, 161.5, "Simple155s view changes to detailed156s comparison; correct menu numbers"),
    "acvi-equip-confirm": (234.6, 240.8, "Old/preview state, then EQ confirmation237–239s and retained result"),
    "botw-category-equip": (203.5, 211.5, "Menu/world/menu/equipped-world sequence; annotations must follow each state"),
    "mh-part-icons": (6, 18, "Body-part changes, linked details and set preview"),
    "mh-preview": (30, 38, "Whole-set context followed by selected-part preview/details"),
    "terra-wheel-drill": (62.5, 71.8, "Held wheel, solid wheel65.5, solid drill71.5"),
    "terra-drive-edit": (161.5, 176.5, "Movement162–166.5, reopen167, preview171.5, retained solid edit175.5"),
}
COPYRIGHT = {
    "jets2-shop": "Game © Rake in Grass",
    "acvi-assembly": "Game © FromSoftware / Bandai Namco Entertainment",
    "botw-menu": "Game © Nintendo",
    "mh-menu": "Game © CAPCOM CO., LTD. ALL RIGHTS RESERVED.",
    "terratech-build": "Game © Payload Studios",
    "acnh-appearance": "Game © Nintendo",
}
MC_CREDITS = {
    "overview": "Põe Pra 2 · LongplayArchive / SpectreBull",
    "effects": "Põe Pra 2 Co-op Gaming · Rake in Grass",
    "tradeoffs": "Kevin A. Wright · FromSoftware / Bandai Namco",
    "find": "World of Longplays / longplays.org / Spazbo4 · DuckTinGaming",
    "auto": "설명용 그림·UI: 얌얌코딩",
    "test": "AnoxLongs No-Commentary Gameplay · Põe Pra 2",
    "appearance": "LongplayArchive / SpectreBull · Nintendo",
    "conclusion": "Põe Pra 2 · Kevin A. Wright · LongplayArchive / SpectreBull",
}


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
    # Corrected native review:4/12/44/100–115.5 are PROFILE, not weapon SHOP.
    #Only122–196 is the inspected SHOP upper range;120 is still PROFILE.
    #Root additionally read every two-second SHOP sample in122–196.
    #Profile edits must never
    #illustrate a changed weapon, firing effect or equipment/test adjacency.
    defaults = [
        ("jets-profile-intro", "jets2-shop", 4, 12, ["overview-greeting", "appearance-overview", "recap-choice", "recap-appearance"], "PROFILE appearance choice only; not weapon selection/test"),
        ("jets-profile-12-20", "jets2-shop", 12, 28, ["recap-choice", "recap-appearance"], "Root-viewed PROFILE body/nose/wing changes, meaningful appearance examples"),
        ("jets-profile-44", "jets2-shop", 40, 48, ["appearance-overview", "recap-choice", "recap-appearance"], "PROFILE generic appearance preview; no firing-effect inference"),
        ("jets-profile-100", "jets2-shop", 96, 104, ["recap-choice", "recap-appearance"], "PROFILE appearance changes; local100–115.5 is not weapon SHOP"),
        ("jets-shop-122-136", "jets2-shop", 122, 136, ["overview-shop", "effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"], "SHOP equipment sale/change, then candidate tooltips/list; active test animation"),
        ("jets-shop-136-152", "jets2-shop", 136, 152, ["effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"], "SHOP Blackfist purchase/equip/two firing patterns, then slots/exchange"),
        ("jets-shop-152-168", "jets2-shop", 152, 168, ["effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"], "SHOP slot/exchange, Clint purchase, slot/list; active preview"),
        ("jets-shop-168-184", "jets2-shop", 168, 184, ["effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"], "SHOP candidates, missile list and equipment change; active preview"),
        ("jets-shop-184-196", "jets2-shop", 184, 196, ["effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"], "SHOP candidates/missile list/equipment change, not idle footage"),
        ("acvi-booster-numbers", "acvi-assembly", 154.8, 161.5, ["tradeoff-menu"], "BST-G2/P04: Boost Speed306→320 / QB EN Consumption480→560"),
        ("acvi-equip-confirm", "acvi-assembly", 234.6, 240.8, ["tradeoff-menu"], "After detailed comparison, preserve the full preview→EQ237–239→retained result"),
        ("botw-category-equip", "botw-menu", 203.5, 211.5, ["find-category"], "Armor category, shirt/trousers selection and actual worn result"),
        ("mh-part-icons", "mh-menu", 6, 18, ["find-equipment"], "Body-part icons, selected part details and whole-set preview"),
        ("mh-preview", "mh-menu", 30, 38, ["find-equipment"], "Kirin set/part preview and connected details; no sorting execution"),
        ("terra-build-context", "terratech-build", 44, 62.5, ["overview-greeting", "test-context", "recap-mechanics"], "Vehicle block construction in the same campaign world"),
        ("terra-wheel-drill", "terratech-build", 62.5, 71.8, ["test-build"], "Wheel selection and solid attachment, followed by drill attachment"),
        #71.8–100 is not automatically spent merely because the upper bank ends
        #at100. Root can add an actually inspected meaningful continuous range.
        ("terra-pre-drive-context", "terratech-build", 150, 161.5, ["test-context", "recap-mechanics"], "Edited vehicle preparation/adjustment; held previews are not already equipped"),
        ("terra-drive-edit", "terratech-build", 161.5, 176.5, ["test-loop"], "Actual world translation, inventory reopen, renewed edit and retained solid result"),
        ("acnh-appearance", "acnh-appearance", 139, 179.5, ["appearance"], "Initial hair/face editing; final confirmation is claimed only when177–179.5 is included"),
    ]
    raw = defaultdict(list)
    for bid, key, lo, hi, roles, purpose in defaults:
        raw[key].append(dict(id=bid, localIn=lo, localOut=hi, roles=roles,
                             purpose=purpose, reviewEvidence="Root source handoff and source-selection linked audits"))
    banks = []
    for key, source in sources.items():
        rows = source.get("editBankRanges", raw.get(key, []))
        if key not in MAIN_KEYS:
            require(rows and source["game"].casefold().startswith("armored core vi") and
                    all(set(x.get("roles", [])) <= {"overview-greeting"} for x in rows),
                    "Only a separately recorded ACVI introductory assembly addition is supported; no extra-game filler.")
        for r in rows:
            lo, hi = float(r["localIn"]), float(r["localOut"])
            roles = set(r["roles"])
            require(0 <= lo < hi and roles and roles <= ROLES, f"Invalid source bank: {r}")
            require(any(lo >= float(a["localIn"]) - 1e-7 and hi <= float(a["localOut"]) + 1e-7
                        for a in source["recommendedRanges"]),
                    f"Bank {r['id']} exceeds root-selected source intervals.")
            require(bool(r.get("purpose")) and bool(r.get("reviewEvidence")),
                    f"Bank {r['id']} needs its concept role and inspection provenance.")
            start, end = math.ceil(lo * FPS - 1e-6), math.floor(hi * FPS + 1e-6)
            if key == "jets2-shop" and roles & {"overview-shop", "effects", "preview-shop", "choice-shop", "test-shop", "recap-mechanics"}:
                require(lo >= 122 and hi <= 196,
                        f"{r['id']}: PROFILE cannot be used as direct weapon SHOP/test evidence.")
            if key == "jets2-shop" and roles & {"appearance-overview", "recap-choice", "recap-appearance"}:
                require(hi <= 116,
                        f"{r['id']}: the appearance/PROFILE role must have separately inspected PROFILE states, not a weapon SHOP assumption.")
            if key == "jets2-shop" and "effects" in roles and lo <= 140 and hi >= 148 and r["id"] != "jets-blackfist-event":
                # Split any root-reviewed containing bank so the Blackfist
                #purchase→equip→test event cannot disappear in prefix slicing.
                if start < 140*FPS:
                    banks.append(Bank(r["id"]+"-before-event", key, start, 140*FPS,
                                      frozenset(roles), r["purpose"], r["reviewEvidence"]))
                banks.append(Bank("jets-blackfist-event", key, 140*FPS, 148*FPS,
                                  frozenset({"effects"}), EVENT_GUARDS["jets-blackfist-event"][2], r["reviewEvidence"], True))
                if end > 148*FPS:
                    banks.append(Bank(r["id"]+"-after-event", key, 148*FPS, end,
                                      frozenset(roles), r["purpose"], r["reviewEvidence"]))
                continue
            if r["id"] in EVENT_GUARDS:
                event_lo, event_hi, _ = EVENT_GUARDS[r["id"]]
                require(lo <= event_lo + 1e-7 and hi >= event_hi - 1e-7,
                        f"{r['id']}: bank clips a required before/action/result event.")
            banks.append(Bank(r["id"], key, start, end, frozenset(roles), r["purpose"], r["reviewEvidence"],
                              r.get("atomic", False) or r["id"] in ATOMIC_BANKS))
    require(len({b.id for b in banks}) == len(banks), "Source bank IDs must be unique.")
    for key in sources:
        spans = sorted((b.lo, b.hi, b.id) for b in banks if b.source == key)
        for a, b in zip(spans, spans[1:]):
            require(a[1] <= b[0], f"Overlapping source banks would repeat frames: {key}: {a}, {b}")
    return banks


def measured_timing(script: dict, english: dict, spoken: dict):
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
        if "paragraphs" in row:
            require(len(row["paragraphs"]) == len(ko["lines"]), "Timing paragraph count mismatch.")
            for item, kl, el, sl in zip(row["paragraphs"], ko["lines"], en["lines"], sp["lines"]):
                for field, expected in (("text", kl), ("english", el), ("spokenText", sl)):
                    if field in item:
                        require(item[field] == expected, f"Timing describes stale {field}: scene{row['id']}")
    require(abs(float(rows[0]["sourceOrigin"])) < 1e-6, "Measured body must start at source origin0.")
    for a, b in zip(rows, rows[1:]):
        require(float(b["sourceOrigin"]) >= float(a["sourceOrigin"]) + float(a["duration"]) - 1 / 24000,
                "Voice scenes overlap; builder must not conceal speech.")
    body = math.ceil((float(rows[-1]["sourceOrigin"]) + float(rows[-1]["duration"])) * FPS - 1e-7)
    return timing, rows, body


def make_slots(rows, body):
    slots = []
    for i, r in enumerate(rows):
        sid, origin = r["id"], float(r["sourceOrigin"])
        start = round(origin * FPS)
        end = round(float(rows[i + 1]["sourceOrigin"]) * FPS) if i + 1 < len(rows) else body
        paragraph = [round((origin + float(x)) * FPS) for x in r["paragraphStarts"]]
        paragraph[0] = start  # Include measured leading silence, without inserting any.
        def put(a, b, role, minimum, purpose, tail=0, maximum=None, required=()):
            lo = start if a == 0 else paragraph[a]
            hi = end if b is None else paragraph[b]
            require(hi > lo, f"Nonpositive semantic slot {sid}:{a}-{b}.")
            slots.append(Slot(f"{sid}-p{a + 1}-{b if b is not None else len(paragraph)}", sid,
                              lo, hi, role, round(minimum * FPS), purpose, round(tail * FPS),
                              None if maximum is None else round(maximum * FPS), tuple(required)))
        if sid == "01":
            put(0, 1, "overview-greeting", 3, "Choosing equipment is itself play; introductory independent menu/build action")
            put(1, 2, "appearance-overview", 0, "Brief appearance-preview context, then retain the authored three-part overview", tail=4, maximum=4)
            put(2, None, "overview-shop", 3, "Introduce the equipment/test-space shop that follows")
        elif sid == "02":
            put(0, 3, "effects", 16, "Actual SHOP weapon selection and firing preview; distinguish both ships",
                required=("jets-blackfist-event",))
            put(3, 4, "preview-shop", 0, "Preview definition over the actual choice→visible firing result; moving game evidence, not a diagram")
            put(4, None, "choice-shop", 0, "General reasons-to-choose question over active SHOP choices; no measured dominance or all-better weapon assertion")
        elif sid == "03":
            put(0, 1, None, 0, "Introduce the booster using the actual booster still; no unrelated part statistics")
            put(1, 2, "tradeoff-menu", 12.9,
                "Full detailed comparison156s, then full EQ237–239 confirmation; never prefix-slice either event",
                required=("acvi-booster-numbers", "acvi-equip-confirm"))
            put(2, 4, None, 0, "Independent fictional A/B arithmetic and one-opportunity counterexample; protect both complete worked explanations")
            put(4, None, "tradeoff-choice", 0, "Actual ACVI part-category selection and changing mech preview illustrate clear tradeoffs followed by finding a desired combination; no damage/performance measurement claim")
        elif sid == "04":
            put(0, 1, "find-category", 8, "BOTW menu/world/menu/equipped-world; no resistance/sort claim",
                required=("botw-category-equip",))
            put(1, 3, "find-equipment", 20, "Complete Iceborne body-part changes and linked character/detail preview; no sorting execution",
                required=("mh-part-icons", "mh-preview"))
            put(3, None, None, 0, "Authored sorting list, then the need for a suggested starting set")
        elif sid == "05":
            put(0, None, None, 0, "Authored criterion→candidate→equip→manual revision; no real-game auto-equip assertion")
        elif sid == "06":
            put(0, 1, "test-context", 4, "Actual same-world building context before the trial question")
            put(1, 2, "test-build", 9.3, "Complete held wheel→solid wheel→solid drill event",
                required=("terra-wheel-drill",))
            put(2, 3, "test-shop", 6, "Recall actual Jets2 equipment/test adjacency")
            put(3, None, "test-loop", 15, "Complete same-world movement→return→retained edit; authored loop/appearance bridge follows", tail=3,
                required=("terra-drive-edit",))
        elif sid == "07":
            put(0, None, "appearance", 30, "Actual initial hair/face editing and immediate preview, then anchored explanation of performance/appearance", tail=4)
        else:
            put(0, 1, "recap-choice", 0, "PROFILE choice-process recall only; no weapon-performance inference")
            put(1, 2, "recap-mechanics", 3, "Fresh actual SHOP/build/test details for the mechanics recap, not PROFILE")
            put(2, None, "recap-appearance", 0, "Actual unique PROFILE body/nose/wing changes illustrate aesthetic fun and what/how to choose; no firing or strength claim")
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
    # PROFILE can demonstrate actual aesthetic changes in the conclusion,
    #but cannot acquire first-three-paragraph weapon-demonstration slots.
    caps = {"appearance-overview": 4 * FPS}
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
                protectedExplanationPassages=["03-1 booster introduction still", "03-3/4 fictional math and limits",
                                              "04-4/5 illustrative sorting and starting-set bridge", "05 all automatic-equipment explanation"],
                profileRestrictions="Only appearance overview or meaningful choice/aesthetic recap including actual body/nose/wing changes; never weapon selection/effect/test evidence.",
                action="Acquire/inspect additional concept-matched footage if short. Never take time from required math/auto/sorting explanations, loop, slow playback, pad idle or count upper research ranges as valid action.",
                exactCutPlanCreated=False)


def allocate(banks, slots, target):
    allocated = defaultdict(int)
    bank_left = [b.capacity for b in banks]
    slot_left = [s.actual_capacity for s in slots]
    by_id = {b.id: i for i, b in enumerate(banks)}
    # Reserve complete named events first. In particular, "12.9seconds of an
    #ACVI pool" is not allowed to turn into a prefix that loses EQ at237–239.
    for si, slot in enumerate(slots):
        for bank_id in slot.required_banks:
            require(bank_id in by_id, f"Required event bank missing: {bank_id}; retain/review its complete event, not a generic replacement.")
            bi = by_id[bank_id]; bank = banks[bi]
            require(bank.atomic and slot.role in bank.roles and bank_left[bi] == bank.capacity,
                    f"Required atomic event {bank_id} has a wrong role or was already spent.")
            require(bank.capacity <= slot_left[si],
                    f"Measured slot {slot.id} cannot hold the full {bank_id} event ({bank.capacity/FPS:.3f}s); review placement, never trim away its result.")
            allocated[bi, si] = bank.capacity
            bank_left[bi] = 0; slot_left[si] -= bank.capacity
    for si, slot in enumerate(slots):
        have = sum(allocated[bi, si] for bi in range(len(banks)))
        need = max(0, slot.minimum-have)
        require(need <= slot_left[si], f"Measured slot {slot.id} is too short for its necessary native demonstration.")
        for bi, bank in enumerate(banks):
            if bank.atomic or slot.role not in bank.roles or not need:
                continue
            n = min(need, bank_left[bi])
            # Initial optional pieces are not allowed to become flash fragments.
            if n and n < MIN_CUT and allocated[bi, si] == 0:
                continue
            allocated[bi, si] += n; bank_left[bi] -= n; slot_left[si] -= n; need -= n
        require(need == 0, f"Missing concept-matched capacity for {slot.id}: {need/FPS:.3f}s. No filler selected.")
    floors = dict(allocated)
    seeded = sum(allocated.values())
    require(seeded <= target, f"Necessary native demonstrations{seeded/FPS:.3f}s exceed60% target{target/FPS:.3f}s; review allocation.")
    # Optional flow is in whole-second pieces. Exact residual frames may extend
    #an existing valid cut, but cannot create a new one-frame/half-second insert.
    graph = Flow(len(banks) + len(slots) + 2)
    source, sink = len(graph.g) - 2, len(graph.g) - 1
    edges = {}
    for bi, bank in enumerate(banks):
        graph.edge(source, bi, bank_left[bi] // MIN_CUT)
        for si, slot in enumerate(slots):
            if not bank.atomic and slot.role and slot.role in bank.roles:
                cap = min(bank_left[bi], slot_left[si]) // MIN_CUT
                edges[bi, si] = (graph.edge(bi, len(banks)+si, cap), cap)
    for si, slot in enumerate(slots):
        graph.edge(len(banks)+si, sink, slot_left[si] // MIN_CUT)
    graph.run(source, sink, (target-seeded) // MIN_CUT)
    for (bi, si), (edge, initial) in edges.items():
        n = (initial-edge[2]) * MIN_CUT
        allocated[bi, si] += n; bank_left[bi] -= n; slot_left[si] -= n
    left = target-sum(allocated.values())
    for (bi, si), count in sorted(list(allocated.items()), key=lambda x: (x[0][1], x[0][0])):
        if count < MIN_CUT or banks[bi].atomic or not left:
            continue
        n = min(left, bank_left[bi], slot_left[si])
        allocated[bi, si] += n; bank_left[bi] -= n; slot_left[si] -= n; left -= n
    if left:
        report = dict(targetActualSeconds=target/FPS,
                      availableConceptMatchedSeconds=(target-left)/FPS, shortfallSeconds=left/FPS,
                      unusedBanks=[dict(id=b.id, source=b.source, seconds=bank_left[bi]/FPS,
                                        roles=sorted(b.roles)) for bi, b in enumerate(banks) if bank_left[bi]],
                      slots=[dict(id=s.id, role=s.role, spanSeconds=s.capacity/FPS,
                                  actualSeconds=sum(allocated[bi, si] for bi in range(len(banks)))/FPS,
                                  reservedExplanationTailSeconds=s.explanation_tail/FPS) for si, s in enumerate(slots)],
                      action="Inspect additional relevant ranges or review precise placements. Required explanations and complete events are protected; no idle/loop/slowdown/subsecond patch.")
        raise PlanError("Insufficient meaningful actual footage for exact60:40:\n"+json.dumps(report, ensure_ascii=False, indent=2))

    def safe_extension_room(bi, si):
        if banks[bi].atomic or allocated[bi, si] < MIN_CUT:
            return 0
        total = sum(allocated[j, si] for j in range(len(banks)))
        gap = slots[si].capacity-total
        # Leave a readable at-least-one-second MC state rather than creating
        #a tiny explanation blink while moving fractional rounding frames.
        return max(0, min(bank_left[bi], slot_left[si], gap-MIN_CUT))

    for si, slot in enumerate(slots):
        count = sum(allocated[bi, si] for bi in range(len(banks)))
        gap = slot.capacity-count
        if not count or gap == 0 or gap >= MIN_CUT:
            continue
        # A short tail is harmless if it joins the next continuing MC state.
        if si+1 < len(slots) and slots[si+1].scene == slot.scene and not sum(allocated[bi, si+1] for bi in range(len(banks))):
            continue
        if si+1 < len(slots) and slots[si+1].scene == slot.scene:
            following = slots[si+1]
            following_gap = following.capacity-sum(allocated[bi, si+1] for bi in range(len(banks)))
            if following_gap and gap+following_gap >= MIN_CUT:
                # Keep an atomic event whole. The next paragraph's already
                #allocated explanation may precede its native footage, merging
                #with this short tail into one readable continuing MC shot.
                #No voice, footage count or paragraph-role boundary is moved.
                continue
        move = MIN_CUT-gap
        donor = next((bi for bi in range(len(banks)) if not banks[bi].atomic and
                      allocated[bi, si]-floors.get((bi, si), 0) >= move and allocated[bi, si]-move >= MIN_CUT), None)
        recipient = next(((bi, sj) for sj in range(len(slots)) if sj != si
                          for bi in range(len(banks)) if safe_extension_room(bi, sj) >= move), None)
        require(donor is not None and recipient is not None,
                f"{slot.id} would create a {gap/FPS:.3f}s MC blink. No plan written; review this exact boundary without cutting a mandatory event.")
        allocated[donor, si] -= move; bank_left[donor] += move; slot_left[si] += move
        bi, sj = recipient
        allocated[bi, sj] += move; bank_left[bi] -= move; slot_left[sj] -= move
    # The final question should finish on the continuing PROFILE change,
    #not flash a one-second explanation before membership. Spend the remaining
    #one second of the already inspected final PROFILE bank, offset by one
    #second of the earlier choice recall. This changes only visual allocation:
    #all narration/caption/scene boundaries and the exact60:40 stay unchanged.
    final_si = len(slots)-1
    final = slots[final_si]
    final_gap = final.capacity-sum(allocated[bi, final_si] for bi in range(len(banks)))
    if final.scene == "08" and final.role == "recap-appearance" and final_gap == MIN_CUT:
        recipient = next((bi for bi, bank in enumerate(banks)
                          if bank.id == "jets-profile-recap-100" and final.role in bank.roles
                          and allocated[bi, final_si] >= MIN_CUT and bank_left[bi] >= final_gap), None)
        donor = next(((bi, si) for si, slot in enumerate(slots)
                      if slot.scene == "08" and slot.role == "recap-choice"
                      for bi, bank in enumerate(banks)
                      if bank.id == "jets-profile-choice" and not bank.atomic
                      and allocated[bi, si]-final_gap >= MIN_CUT
                      and allocated[bi, si]-floors.get((bi, si), 0) >= final_gap), None)
        require(recipient is not None and donor is not None,
                "Final one-second explanation would interrupt the closing question; the source-bound recall transfer is unavailable. Review the visual placement, not voice timing.")
        donor_bi, donor_si = donor
        allocated[donor_bi, donor_si] -= final_gap
        bank_left[donor_bi] += final_gap; slot_left[donor_si] += final_gap
        allocated[recipient, final_si] += final_gap
        bank_left[recipient] -= final_gap; slot_left[final_si] -= final_gap
    require(sum(allocated.values()) == target, "Fragment repair changed the exact ratio.")
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
        # Same-source detail→application must retain its native chronology.
        #ACVI156 detailed comparison therefore precedes EQ237–239.
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
            copyright_credit = s.get("copyrightCredit", COPYRIGHT.get(cut["source"], COPYRIGHT["acvi-assembly"]))
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
            cut["sourceEventsIncluded"] = [meaning for bid, (a, b, meaning) in EVENT_GUARDS.items()
                                           if bid == cut["sourceBankId"] and lo <= a+1e-7 and hi >= b-1e-7]
            if cut["source"] == "jets2-shop":
                cut["sourceContentMode"] = "PROFILE: aesthetic changes" if hi <= 116 else "SHOP: equipment and active trial"
                cut["notEstablished"] = "No weapon-effect inference from PROFILE; no measured dominance, damage or universal optimum asserted."
            if cut["source"] == "botw-menu":
                cut["sourceStateSamples"] = [dict(localSeconds=x, state=state) for x, state in
                    [(203.5, "Armor menu"), (204, "Armor menu"), (205, "World"),
                     (205.5, "Armor menu"), (206.8, "Armor menu"), (207, "Equipped world")]
                    if lo <= x < hi]
                cut["annotationStateRule"] = "Menu targets must hide across world205 and207; samples are not exact transition frames. Root must use its actual native transition timings, not interpolate a menu rectangle through the world."
            if cut["sourceBankId"] == "acvi-booster-numbers":
                cut["sourceStateSamples"] = [dict(localSeconds=155, state="Simple stats"),
                                             dict(localSeconds=156, state="Detailed comparison")]
                cut["annotationStateRule"] = "QB EN Consumption mark starts only after detailed view appears; do not assume the simple view shows that row."
            if cut["source"] == "acnh-appearance":
                require(lo <= 148.7 and hi >= 168.5,
                        "Appearance allocation lost the actual hair/face before/action/result.")
                cut["sourceEventsIncluded"] += ["Hair/eye preview changes148.7–168.5"]
                if lo <= 177 and hi >= 179.5:
                    cut["sourceEventsIncluded"].append("Final appearance confirmation177–179.5")
        else:
            row = rowmap[cut["scene"]]
            local_start = (cut["startFrame"]-INTRO)/FPS - float(row["sourceOrigin"])
            cues = [float(x)-local_start for x in row["paragraphStarts"]]
            cut.update(cues=cues, narrationSceneLocalStart=local_start,
                       renderedSource=MC_VIDEO, renderedStartFrame=mc_cursor,
                       mcStartFrame=mc_cursor, mcEndFrame=mc_cursor+cut["frames"],
                       renderStatus="pending root render", credit=MC_CREDITS[cut["visual"]])
            mc_cursor += cut["frames"]
            name = "production-" + cut["id"]
            payload = dict(duration=(cut["frames"]-.75)/FPS, cues=cues, credit=MC_CREDITS[cut["visual"]])
            modules[name] = ("import {makeScene2D} from '@motion-canvas/2d';\n"
                             "import {lesson} from './visuals';\n"
                             "export default makeScene2D(function*(view){yield* lesson(view,"
                             + json.dumps(cut["visual"]) + "," + json.dumps(payload, ensure_ascii=False) + ");});\n")
    require(merged and merged[0]["startFrame"] == INTRO and merged[-1]["endFrame"] == INTRO+body,
            "The edit must cover the measured body, excluding the original2s/10s branding/member clips.")
    for a, b in zip(merged, merged[1:]):
        require(a["endFrame"] == b["startFrame"], f"Body gap/overlap: {a['id']}, {b['id']}")
    for sha in {s["media"]["sha256"] for s in sources.values()}:
        spans = sorted((c["sourceStart"], c["sourceStart"]+c["frames"]/FPS, c["id"])
                       for c in merged if c.get("sourceSha256") == sha)
        for a, b in zip(spans, spans[1:]):
            require(a[1] <= b[0]+1e-7, f"Repeated source frames: {a}, {b}")
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
    require(MAIN_KEYS <= sources.keys(), "A primary teaching source is missing; do not replace it with unrelated footage.")
    if args.capacity_audit:
        print(json.dumps(capacity_report(banks_from_sources(sources), args.body_seconds), ensure_ascii=False, indent=2))
        return
    ko_path = PROJECT / "script/reference-preserving-v2/narration.ko.json"
    en_path = PROJECT / "script/reference-preserving-v2/narration.en.json"
    sp_path = PROJECT / "script/reference-preserving-v2/narration.spoken-ko.json"
    script, english, spoken = read(ko_path), read(en_path), read(sp_path)
    timing, rows, body = measured_timing(script, english, spoken)
    inputs = []
    for p in [TIMING, ko_path, en_path, sp_path, selected_path, HERE/"script-audit.json"]:
        inputs.append(dict(path=rel(p), sha256=digest(p)))
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
        media = scoped(source["media"]["path"], PROJECT)
        require(media.exists() and digest(media) == source["media"]["sha256"], f"Source bytes no longer match selection: {key}")
    banks = banks_from_sources(sources)
    slots = make_slots(rows, body)
    target = round(body * .6)
    allocation = allocate(banks, slots, target)
    cuts, modules, mc_frames, warnings = make_cuts(banks, slots, allocation, rows, sources, body)
    actual = sum(c["frames"] for c in cuts if c["kind"] == "independent-gameplay")
    require(actual == target and abs(actual-body*.6) <= 1, "Actual/explanation body ratio escaped one-frame tolerance.")
    games = {c["game"] for c in cuts if c["kind"] == "independent-gameplay"}
    nintendo = {c["game"] for c in cuts if c.get("nintendoGame")}
    require(len(games) == 6 and len(nintendo) == 2, "Current six meaningful main examples must retain the selected two Nintendo roles; no count padding.")
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
                expectedGameplayShare=.6, ratioToleranceFrames=1,
                outputDir=rel(LOCAL/"edit"), outputStem="player-customization-v2",
                captionAliases=read(PROJECT/"script/reference-preserving-v2/caption-aliases.json"),
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
                                  wholeEventRequired=b.atomic) for b in banks],
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
                negativeParagraphCuesPreserved=True, narrationPcmPreserved=True, sourceIntervalsUnique=True,
                noLoops=True, noSlowdown=True, noSourceFrameHolds=True,
                gameExampleCoverage=dict(mainGames=sorted(games), nintendoGames=sorted(nintendo),
                                         fraction=len(nintendo)/len(games), countBasis="Distinct meaningfully taught game, once each; separate from time ratio"),
                annotationsReview="pending root native-coordinate marks and moving QA", humanWholeListening="pending",
                renderStatus="pending", shortCutReviewWarnings=warnings, youtubeUploadAuthorized=False,
                automaticNextVideo=False, baselineReplacementOrDeletionAuthorized=False)
    annotation = HERE / "source-annotations.json"
    if annotation.exists():
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
