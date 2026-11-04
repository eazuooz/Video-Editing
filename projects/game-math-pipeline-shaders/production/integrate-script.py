"""Integrate observed gameplay into the full source-faithful narration.
This changes no audio and does not close runtime, scene-binding or final-review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re

CONFIG = json.loads(r'''{"episode":"M23","slug":"game-math-pipeline-shaders","edits":[{"index":0,"mode":"replace","ko":"타운스케이퍼에서 건물을 더하고 화면을 돌리면, 지붕의 위치와 서로 가리는 모양이 계속 달라집니다. 컴퓨터는 이 삼차원 변화를 어떻게 한 장의 화면으로 만들까요? 정점이 화면에 놓이는 길을 따라가며, 앞뒤를 가르는 깊이와 표면의 색을 만드는 셰이더를 연결해 보겠습니다. 먼저 건물과 카메라의 정보가 화면까지 전달되는 전체 흐름부터 보죠.","en":"In Townscaper, adding buildings and turning the view changes where roofs appear and how they overlap. How does a computer turn these three-dimensional changes into one image? We will follow vertices toward the screen, connect depth to visibility, and use shaders to calculate surface color. First, let us trace the route from the buildings and camera to the resulting picture.","reason":"Actual Townscaper100–124 construction/view changes supply the thesis abstract; no inference about its proprietary pipeline order, shader language or timing.","screen":"After2sbranding, nativeTownscaper100–124with one changed roof contour. Continue overview into our fixed scene pipeline diagram; no fabricated wireframe or buffer overlay on the actual game."},{"index":9,"mode":"prepend","ko":"포털에서 큐브를 들어 옮기면, 가까운 큐브가 뒤쪽 발판과 벽의 일부를 가립니다. 같은 화면 자리에 여러 표면이 겹칠 때, 어느 표면을 남겨야 할지 결정해야 하는 거죠.","en":"In Portal, carrying a cube makes it cover parts of the platforms and walls behind it. When several surfaces project onto the same place in the image, the renderer needs a way to decide which surface remains visible.","reason":"Observed Portal2007 local445–461 occlusion motivates the depth buffer, not an exposed measured game depth value or early-Z implementation.","screen":"NativePortal445–461local: near cube contour and farther platform edge, no numerical depth overlay. Then our depth test0.7→0.3→0.8 under an explicitly declared conventional comparison."},{"index":28,"mode":"prepend","ko":"같은 포털에서도 유리 너머의 방은 보이지만, 그 둘레의 불투명한 틀 뒤는 가려집니다. 앞뒤만 정하는 데서 한 걸음 더 나아가, 어떤 표면의 색을 얼마나 보여 줄지도 정해야 합니다.","en":"In the same game, the room remains visible through a glass pane while its opaque frame blocks the view. Beyond resolving what is in front, we also need to determine how each surface contributes to the visible color.","reason":"Observed localPortal194–214 glass/frame contrast motivates material output. Blend equation is a separate labelled teaching implementation; no actual alpha value or portal-as-transparency claim.","screen":"NativePortal194–214local: outline pane and opaque border separately, retain real button context. Then our alpha test versus straight-alpha blend0.25red+0.75blue, with depth-state label."},{"index":29,"mode":"replace","ko":"슈퍼 마리오 오디세이에서는 물속으로 들어간 몸이 수면 너머로 보이다가, 뛰어나오면서 모습이 달라집니다. 방금 본 유리나 물처럼 표면에 따라 달라지는 색을, 지금까지 따라온 파이프라인에서 계산하는 겁니다. 이제 그 길에서 우리가 작성하는 두 계산, 정점 셰이더와 픽셀 셰이더를 코드로 연결해 보죠. 에이치엘에스엘은 이를 작성하는 언어입니다. 예제는 단순한 셰이더에서 출발해 조명, 노멀 매핑, 스키닝을 차례로 더합니다. 오래된 셰이더 모델의 표기와 현재 표기는 구분하되, 데이터가 어느 단계로 흐르는지에 집중하겠습니다.","en":"In Super Mario Odyssey, Mario remains partly visible through the water, then changes appearance as he jumps out. The pipeline we have followed calculates the visible color of surfaces such as this water and the glass we just saw. We will now implement its programmable stages in HLSL: the vertex and pixel shaders. We begin with an unlit texture, then add lighting, normal mapping, and skinning. We will distinguish legacy shader-model notation from modern syntax while following the same data flow.","reason":"Native13-second Mario730–743 crossing shows observable material-dependent appearance, not a measured water alpha, refractive index, or proof that a simple texture shader reproduces the game's water. Merge the new bridge with the original chapter opening to remove duplicate promises to start coding; retain every shader-stage and lesson-order claim.","screen":"NativeMario730–743at1x: water boundary and visible submerged region, clear annotation on exit; then our unlit-texture shader baseline. Never extend the13-second example or use following frog cinematic."}],"screenOverrides":{"67":"Close on the same independent explanation-stage object and pipeline used beside the opening. Trace location→orientation→color across vertex/raster/pixel/output stages. No unverified additional gameplay return or duplicate static padding."},"bindings":[{"index":0,"candidate":"M23-G01-building-to-picture","speechPrefix":"타운스케이퍼에서 건물을 더하고 화면을 돌리면","role":"Actual-game thesis abstract:3Dconstruction/viewpoint to changing2Dimage","after":"Our fixed scene shows conceptual pipeline; actual internal Townscaper buffers remain unknown."},{"index":9,"candidate":"M23-G02-opaque-depth","speechPrefix":"포털에서 큐브를 들어 옮기면","role":"Occlusion before numeric depth test","after":"Move to our0.7/0.3/0.8depth calculation; never draw those numbers as measured Portal values."},{"index":28,"candidate":"M23-G03-glass-versus-frame","speechPrefix":"같은 포털에서도 유리 너머의 방은 보이지만","role":"Visible glass versus opaque frame before alpha concepts","after":"Our cutout/blend test distinguishes mechanisms using explicit chosen values."},{"index":29,"candidate":"M23-G04-water-and-character","speechPrefix":"슈퍼 마리오 오디세이에서는 물속으로 들어간 몸이","role":"Cross-genre material example bridges pipeline overview to programmable shader stages","after":"Begin our deliberately simpler unlit material; add light, normals and skinning in original teaching order."}],"aliases":{"타운스케이퍼":"Townscaper","에이치엘에스엘":"HLSL","에스브이 포지션":"SV_Position","에스브이 타깃":"SV_Target","유브이":"UV","알지비":"RGB"},"corrections":[{"index":53,"koFrom":"일 점 일이오","koTo":"일 점 일오오","reason":"Full read-through found Korean transcription1.125 instead of the computed vertical scale2sqrt(3)/3≈1.154700538. Correct spoken digits to1.155; existing EN and equation were correct."},{"index":54,"koFrom":"일 점 일이오","koTo":"일 점 일오오","reason":"Full read-through found Korean transcription1.125 instead of the computed vertical scale2sqrt(3)/3≈1.154700538. Correct spoken digits to1.155; existing EN and equation were correct."},{"index":62,"enFrom":"Encode each normal component with 255 times one half of the component plus one, then round to the nearest integer.","enTo":"Add one to each normal component, halve that result, multiply by 255, then round to the nearest integer.","reason":"Unambiguous English operation order for255*(n+1)/2; no change in numerical results."}],"reviewNotes":["All68KO and all68EN beats read, including all exercises10.13 and correctedshader equations.","Source source-audit records full paragraph/figure read; preserve ordered10.10→10.11→10.12→10.13 flow.","Portal is2007game, notPortal2; original full audio starts450s later than local cropped video timeline.","Gamewater/glass are observation, not proof of exact shader/blendimplementation; numerical values belong to our independently authored stage.","Narration overlaps motion and diagrams; durations remain unknown until approved voice generation and synchronized visual review."]}''')
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
