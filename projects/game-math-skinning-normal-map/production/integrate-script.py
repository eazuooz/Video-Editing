"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads(r'''{"episode":"M22","slug":"game-math-skinning-normal-map","edits":[{"index":0,"mode":"replace","ko":"슈퍼 마리오 오디세이에서 마리오가 뛰어올라 착지할 때, 몸 전체가 움직이는 동안 팔과 다리의 자세도 함께 바뀝니다. 컴퓨터는 한 캐릭터의 여러 부분을 어떻게 함께 움직일까요? 오늘은 관절을 따라 큰 형태를 바꾸는 스키닝부터, 표면의 작은 요철을 빛으로 표현하는 노멀 맵까지 이어서 살펴보겠습니다. 먼저 캐릭터를 통째로 움직이는 것과 관절을 굽히는 것의 차이부터 보죠.","en":"In Super Mario Odyssey, Mario jumps and lands: his whole body moves while his arms and legs change pose. How can a computer coordinate these different parts of one character? We will follow skinning, which changes the large shape, then normal mapping, which uses surface directions to shade fine detail. First, let us distinguish moving the whole character from bending its joints.","reason":"Replace the unresolved introductory example with observed Mario710–730 at native speed; preserve large shape→fine shading and coordinate-transform thesis. Do not identify Nintendo's internal skinning method.","screen":"After2sbranding, nativeMario710–730with readable joint arcs. Observe whole motion and limb pose, then match-cut to our shared articulated-model stage while the overview continues. No static hold or gameplay stretch."},{"index":2,"mode":"prepend","ko":"라이더스 리퍼블릭에서 자전거가 점프할 때, 프레임은 모양을 유지하지만 타는 사람의 팔과 무릎은 접혔다 펴집니다. 이 차이를 직접 만들어 보려고, 관절마다 작은 좌표계를 붙여 보겠습니다.","en":"When a bicycle jumps in Riders Republic, its frame retains its shape while the rider bends and extends arms and knees. To build this distinction ourselves, we will attach a small coordinate frame to each joint.","reason":"Observed rigid bicycle versus articulated rider motivates virtual bone coordinates; clothing is not evidence of smooth skinning.","screen":"NativeRiders734–758: frame contour versus brief elbow/knee arcs. Continue speech over source then our same jointed model; introduce labelled local-axis bone gizmos only in our implementation."},{"index":15,"mode":"prepend","ko":"둠 쓰리의 금속 벽을 손전등으로 비추면, 작은 홈이 밝아졌다 어두워지며 드러납니다. 이런 표면 디테일을 표현하는 한 가지 방법을, 이제 우리가 만든 같은 면에서 직접 비교해 보겠습니다.","en":"As a flashlight sweeps over a metal wall in Doom 3, small grooves emerge through changes in brightness. We will now compare one way to create this kind of surface detail on a fixed surface in our own implementation.","reason":"Observed small surface light response motivates normal mapping without asserting that each visible groove is mapped rather than geometric.","screen":"NativeDoom3original111–128open contour on lit plate/grooves. Then fixed same geometry in our Unity stage: grayscaleheight→slopeN versusRGBnormal→N, unchanged silhouette and wireframe."}],"screenOverrides":{"35":"Close on the same independently authored articulated model used throughout: bone transform and surface TBN axes update with its bend. Actual game examples were observational motivation, not measured internal skeletons. No unverified gameplay return, added BGM, loop or hold."},"bindings":[{"index":0,"candidate":"M22-G01-mario-articulation","speechPrefix":"슈퍼 마리오 오디세이에서 마리오가 뛰어올라 착지할 때","role":"Actual-game thesis abstract: whole-body movement versus limb configuration","after":"Our articulated model begins with rigid whole-body transform, then part hierarchy. The remaining abstract may overlap this transition."},{"index":2,"candidate":"M22-G02-rider-joints","speechPrefix":"라이더스 리퍼블릭에서 자전거가 점프할 때","role":"Rigid frame versus articulated rider, then coordinate-frame bones","after":"Our model alone shows actual implementation bone axes and vertex weights."},{"index":15,"candidate":"M22-G03-doom3-surface-response","speechPrefix":"둠 쓰리의 금속 벽을 손전등으로 비추면","role":"Fine surface brightness motivates height/normal representation","after":"Isolate height/normal map changes on our unchanged mesh; actual Doom footage is not a toggle comparison."}],"aliases":{"슈퍼 마리오 오디세이":"슈퍼 마리오 오디세이","둠 쓰리":"둠 3","유브이":"UV","알지비":"RGB","티비엔 기저":"TBN 기저"},"corrections":[{"index":19,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":25,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":27,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":28,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":31,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":32,"koFrom":"바이탄젠트","koTo":"비탄젠트","reason":"Consistent Korean rendering of bitangent across M22/M23; display canonical English bitangent beside first definition."},{"index":24,"koFrom":"그래서 플러스 일 또는 마이너스 일의 손잡이 부호를 함께 저장합니다.","koTo":"그래서 좌표계의 좌우 방향을 구분하는 부호, 핸디드니스를 함께 저장합니다. 값은 플러스 일 또는 마이너스 일이에요.","enFrom":"so store a handedness sign of +1 or -1.","enTo":"so store a handedness sign that distinguishes the frame's orientation: +1 or -1.","reason":"Define handedness in plain words beside canonical term; retain sign and cross-product algorithm."},{"index":32,"koFrom":"내적 부호를 보고 손잡이를 저장합니다.","koTo":"내적 부호를 보고 앞서 정의한 핸디드니스 부호를 저장합니다.","reason":"Use established handedness term rather than an unexplained literal handle translation."}],"reviewNotes":["All36KO and all36EN source-faithful teaching beats read; keep every source paragraph mapping and calculation.","Original source images3 now visually inspected as recorded in research/figure-audit.json; old draft metadata about unviewed images is superseded, not rewritten.","New gameplay text says only what root's time-indexed source observations support; no assertion of Nintendo/Ubisoft skinning algorithm or per-groove Doom geometry."]}''')
PROJECT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

ko_path = PROJECT / "script/draft-narration.ko.json"
en_path = PROJECT / "script/draft-narration.en.json"
ko, en = load(ko_path), load(en_path)
segments, english = copy.deepcopy(ko["segments"]), copy.deepcopy(en["segments"])
assert [s["id"] for s in segments] == [s["id"] for s in english]
changes = []
for edit in CONFIG["edits"]:
    i = edit["index"]
    before, before_en = segments[i]["text"], english[i]["text"]
    segments[i]["text"] = edit["ko"] + (" " + before if edit["mode"] == "prepend" else "")
    english[i]["text"] = edit["en"] + (" " + before_en if edit["mode"] == "prepend" else "")
    segments[i]["screenPlan"] = edit["screen"]
    changes.append({"sourceBeatId":segments[i]["id"], "mode":edit["mode"],
                    "beforeKo":before, "afterKo":segments[i]["text"],
                    "beforeEn":before_en, "afterEn":english[i]["text"],
                    "reason":edit["reason"]})
for fix in CONFIG["corrections"]:
    i = fix["index"]
    before, before_en = segments[i]["text"], english[i]["text"]
    if "koFrom" in fix:
        assert fix["koFrom"] in before
        segments[i]["text"] = before.replace(fix["koFrom"], fix["koTo"])
    if "enFrom" in fix:
        assert fix["enFrom"] in before_en
        english[i]["text"] = before_en.replace(fix["enFrom"], fix["enTo"])
    changes.append({"sourceBeatId":segments[i]["id"], "mode":"readthrough-correction",
                    "beforeKo":before, "afterKo":segments[i]["text"],
                    "beforeEn":before_en, "afterEn":english[i]["text"], "reason":fix["reason"]})
for index, screen in CONFIG["screenOverrides"].items():
    segments[int(index)]["screenPlan"] = screen

def display(text):
    for a, b in CONFIG["aliases"].items():
        text = text.replace(a, b)
    return text

common = {
    "schemaVersion":1, "slug":CONFIG["slug"], "episodeId":CONFIG["episode"],
    "status":"integrated-draft-text-readthrough-complete-runtime-binding-pending",
    "isFinalNarration":False, "chapterOrderPreserved":True,
    "actualDurationSeconds":None,
    "sourceDraftSha256":sha(ko_path), "englishDraftSha256":sha(en_path),
    "speechAndVisualOverlap":True, "defaultHoldSeconds":0
}
scenes, scenes_en = [], []
for i, (s,e) in enumerate(zip(segments, english)):
    scenes.append({"id":f"{i:03d}", "sourceBeatId":s["id"], "title":s["title"],
                   "section":s["section"], "lines":[s["text"]], "displayLines":[display(s["text"])]})
    scenes_en.append({"id":f"{i:03d}", "sourceBeatId":s["id"], "title":e["title"],
                      "section":s["section"], "lines":[e["text"]]})
ko_final = PROJECT / "script/narration.ko.json"
en_final = PROJECT / "script/narration.en.json"
save(ko_final, dict(common, language="Korean", scenes=scenes))
save(en_final, dict(common, language="English", scenes=scenes_en))

footage_path = PROJECT / "planning/footage-audit.json"
footage = load(footage_path)
sources = {s["id"]:s for s in footage["sources"]}
candidates = {c["id"]:c for c in footage["candidateSegments"]}
bindings = []
for selected in CONFIG["bindings"]:
    c = candidates[selected["candidate"]]
    src = sources[c["sourceId"]]
    audio = copy.deepcopy(src.get("audio", {}))
    offset = audio.get("fullOriginalAudioOffsetForLocalVideo", 0)
    bindings.append({
        "beat":segments[selected["index"]]["id"], "sceneId":f'{selected["index"]:03d}',
        "candidate":c["id"], "sourceId":c["sourceId"], "game":src["game"],
        "sourceIn":c["sourceIn"], "sourceOut":c["sourceOut"],
        "sourceFile":src["file"], "sourceSha256":src["sha256"],
        "recordingUrl":src["recordingUrl"], "decodedSize":src["decodedSize"],
        "nativeFps":src["nativeFps"], "playbackRate":1, "hold":0,
        "loop":False, "freezePadding":False,
        "role":selected["role"], "observed":c["observed"],
        "claimLimits":c["claimLimits"], "annotationPlan":c["annotationPlan"],
        "reviewEvidence":c["reviewEvidence"],
        "nativeDecodeEvidence":c.get("nativeDecodeEvidence"),
        "speechTarget":{"prefixKo":selected["speechPrefix"],
                        "timing":"Phrase placement to follow actual PCM; speak target, action and result while visible."},
        "handoffToExplanation":selected["after"],
        "audio":audio, "fullOriginalAudioIn":c["sourceIn"]+offset,
        "fullOriginalAudioOut":c["sourceOut"]+offset,
        "status":"observed-source-bound-to-text; native playback, audio, annotation and exact timing QA pending"
    })
plan_path = PROJECT / "planning/production-plan.json"
plan = load(plan_path)
plan.update({
    "sourceFinal":True, "narrationFinal":False, "sceneBindingsFinal":False,
    "stage":"full-draft-gameplay-integration",
    "learningSteps":[{"id":s["id"],"section":s["section"],
                     "sourceParagraphs":s["sourceParagraphs"],
                     "retainedExplanation":s["text"],"screenIntent":s["screenPlan"]}
                    for s in segments],
    "teachingBeats":[{"id":s["id"],"speech":s["text"],"visual":s["screenPlan"],"hold":0,
                     "timing":"pending actual PCM and realized motion; no automatic observation silence"}
                    for s in segments],
    "nativeGameCueBindings":bindings,
    "gameMix":{"adoptedGames":len(set(b["game"] for b in bindings)),
               "nintendoGames":1,"nintendoGame":"Super Mario Odyssey",
               "selectionReason":"Three distinct concept-matched games; one Nintendo game among three. Each shows an observed action/result, without assigning hidden engine internals."},
    "boundaryLinks":[{"from":segments[i-1]["id"],"to":segments[i]["id"],
                      "carriedResult":re.split(r"(?<=[.!?])\s+", segments[i-1]["text"])[-1],
                      "nextOpening":re.split(r"(?<=[.!?])\s+", segments[i]["text"])[0],
                      "sourceBoundary":segments[i].get("boundaryFromPrevious"),
                      "actualGameBridge":next((b["role"] for b in bindings if b["beat"]==segments[i]["id"]),None)}
                     for i in range(1,len(segments))]
})
save(plan_path, plan)
readthrough = {
    "status":"full bilingual draft and all integration changes read; final integrated readthrough requires explicit review record",
    "source": "planning/source-audit.json",
    "beats":len(segments),"sourceOrderPreserved":True,
    "sourceParagraphMappingPreserved":True,
    "notes":CONFIG["reviewNotes"],
    "audioListeningCompleted":False, "realizedTimingReviewed":False,
    "koSha256":sha(ko_final),"enSha256":sha(en_final)
}
save(PROJECT/"planning/script-integration.json", {
    "updatedAt":datetime.now(timezone.utc).isoformat(),
    "episode":CONFIG["episode"], "sourceAudit":"planning/source-audit.json",
    "sourceAuditSha256":sha(PROJECT/"planning/source-audit.json"),
    "footageAudit":"planning/footage-audit.json","footageAuditSha256":sha(footage_path),
    "changes":changes,"readThrough":readthrough,
    "sourceFinal":True,"narrationFinal":False,"sceneBindingsFinal":False,
    "ttsStarted":False,
    "remaining":["Explicit review of integrated full KO/EN output",
                 "Unity runtime and all source-beat scene bindings",
                 "Actual voice duration, phrase-to-motion synchronization and native gameplay listening",
                 "Final moving annotations and caption composite at1080p and375px"]
})
for language, rows in [("ko",scenes),("en",scenes_en)]:
    (PROJECT/f"script/integrated-readthrough.{language}.txt").write_text(
        "\n\n".join(" ".join(s["lines"]) for s in rows)+"\n",encoding="utf-8")
print(CONFIG["episode"], "integrated", len(segments), "beats;", len(bindings),
      "verified-source roles; final narration and scene-binding gates remain false.")
