"""Specific observed movements, never arbitrary background gameplay."""
from pathlib import Path
from inventory import ROOT,HERE,read,save,sha


def build():
    inventory={e["id"]:e for e in read(HERE/"inventory.json")["episodes"]}
    additions=[]
    def add(eid,sid,source,inpoint,duration,label,observation,meaning,marks):
        ep=inventory[eid];scene=next(s for s in ep["scenes"] if s["scene"]==sid)
        assert duration<scene["end"]-scene["start"]-.2
        additions.append(dict(episode=eid,scene=sid,start=scene["start"]+.1,duration=duration,
            source=source,sourceIn=inpoint,sourceOut=inpoint+duration,label=label,
            beforeActionResult=observation,teachingRole=meaning,
            viewport=[70,325,850,478],marks=marks,
            audio="Native synchronized recording, normal production ducking; no added BGM",
            playbackRate=1,loop=False,freezePadding=False,
            sourceMotionReview="One-second contact sheet inspected across the whole selected interval; encoded playback QA pending",
            illustrationNotice="Right: authored teaching model, not measured game coordinates or hidden implementation",
            status="source-selected-final-playback-pending"))
    mario=read(ROOT/"projects/game-math-velocity-derivatives/planning/footage-audit.json")
    mario=next(x for x in mario["sources"] if x["id"]=="_wH_-1saHnw")
    add("M24","004",mario,712,10,"Super Mario Odyssey (슈퍼 마리오 오디세이)",
        dict(before="Mario runs toward blocks",action="Jumps onto and away from the blocks; camera follows",result="Character changes position while retaining recognizable articulated shape"),
        "Particle model: choose a point on the visible character to track without replacing the game's actual body with a robot",
        dict(kind="tracked-hollow-circle",label="추적하는 위치",radius=28,
             keys=[[0,.515,.645],[1,.477,.32],[2,.49,.65],[3,.553,.473],[4,.467,.491],[5,.487,.586],[6,.493,.651],[7,.5,.627],[8,.483,.544],[9,.467,.544]],
             hideAfter=9.6))
    kart=read(HERE/"sources/mario-kart-provenance.json")
    add("M25","002",kart,7,16,"Mario Kart 8 Deluxe (마리오카트 8 디럭스)",
        dict(before="Luigi's kart waits on grid during 3–2–1",action="GO, kart pulls away and follows road",result="Position keeps changing after departure; direction also changes as the course bends"),
        "Concrete start-from-rest example before formal acceleration units. No numerical acceleration or engine model is inferred from the capture.",
        dict(kind="tracked-hollow-circle",label="출발하는 카트",radius=63,
             keys=[[0,.51,.67],[5,.51,.67],[6,.50,.67],[7,.50,.70],[8,.52,.64],[9,.51,.66],[10,.51,.66],[11,.49,.65],[12,.51,.67],[13,.50,.65],[14,.52,.70],[15,.52,.70]],
             hideAfter=15.8))
    besiege=read(ROOT/"projects/game-math-circular-motion/planning/footage-audit.json")
    besiege=next(x for x in besiege["sources"] if x["id"]=="T3ncWUwKUns")
    add("M26","001",besiege,338,8,"Besiege (비시지)",
        dict(before="Intact windmill turns behind vehicle",action="Rotor tips rotate around attached hub as camera approaches",result="The hub stays attached while points on the blade trace arcs"),
        "Introduce a rotating object's point and centre. Later scene017 revisits this same meaningful subject to compare hub/tip linear speeds; no repeated duration padding.",
        dict(kind="tracked-hollow-circle",label="회전하는 날개",radius=47,
             keys=[[0,.55,.155],[1,.55,.155],[2,.55,.155],[3,.55,.155],[4,.55,.155],[5,.49,.16],[6,.49,.16],[7,.49,.16]],
             hideAfter=7.8))
    for item in additions:
        item["audioMode"]="add-original-only-over-formerly-silent-explanation"
        f=ROOT/item["source"]["file"]
        assert f.is_file() and sha(f)==item["source"]["sha256"]
        dims=item["source"].get("decodedSize") or item["source"].get("decodedDimensions")
        item["sourceSizeEvidence"]=dims
    # Keep the meaningful original game windows and bring the native principle
    # picture beside them. These are not extra borrowed examples or new claims.
    paired={"M22":["002"],"M23":["009","028"],"M24":["015","032"],
        "M25":["018"],"M26":["011","017"],"M27":["012"],
        "M28":["001","016"],"M29":["014","018"],"M30":["003"],
        "M31":["027"],"M32":["017","022"],"M33":["008","017"]}
    for eid,sids in paired.items():
        ep=inventory[eid];project=ROOT/"projects"/ep["slug"]
        queue=read(project/"production/local"/ep["baselineRevision"]/"queue.json")
        sources={s["id"]:s for s in read(project/"planning/footage-audit.json")["sources"]}
        jobs={read(Path(j))["sceneId"]:read(Path(j)) for j in queue["jobs"]}
        for sid in sids:
            scene=next(s for s in ep["scenes"] if s["scene"]==sid)
            cut=next(c for c in queue["cuts"] if c["scene"]==sid and c["kind"]=="actual-gameplay")
            source=sources[cut["sourceId"]]
            native=Path(jobs[sid]["output"])/"unity.mp4"
            assert native.is_file(),native
            part=scene["originalGame"]
            additions.append(dict(episode=eid,scene=sid,start=2+cut["globalStartFrame"]/60,
                duration=cut["frames"]/60,source=source,sourceIn=cut["sourceIn"],sourceOut=cut["sourceOut"],
                label=part.get("game",source.get("game",cut["sourceId"])),
                viewport=[70,325,850,478],marks=None,playbackRate=1,loop=False,freezePadding=False,
                beforeActionResult=part.get("observed"),teachingRole=part.get("role",part.get("teachingRole")),
                audioMode="baseline-original-game-audio-unchanged",nativeSource=str(native),
                preservedAnnotatedPicture=ep["baselineOutputs"]["clean"],
                preservedPictureIn=2+cut["globalStartFrame"]/60,
                preservedPictureCrop=[192,48,1536,864],
                nativeIn=(2+cut["globalStartFrame"]/60)-scene["start"],
                nativeCrop=[995,178,887,738] if int(eid[1:])<=26 else [40,178,940,738],
                nativeViewport=[995,178,887,738],
                basis="Previously inspected concept-matched game window and its same-scene frame-exact Unity capture; newly paired layout requires encoded QA",
                status="paired-layout-prepared-review-pending"))
            if (eid,sid) in {("M31","027"),("M33","008")}:
                # These two approved figures replace the raw native placeholder.
                # Preserve the corrected p/v and continuity constructions rather
                # than reviving the older Bézier-control labels from the capture.
                paired_picture=additions[-1]
                paired_picture["nativeSource"]=ep["baselineOutputs"]["clean"]
                paired_picture["nativeIn"]=scene["start"]+cut["frames"]/60
                paired_picture["nativeInputKind"]="current postprocessed explanation; introduce the same principle beside its existing game preface"
                assert paired_picture["nativeIn"]+paired_picture["duration"]<=scene["end"]
    save(HERE/"game-additions.json",dict(additions=additions,
        otherGameExamples="Retain the concept-specific independently recorded before/action/result windows and their existing source/rights/FHD evidence; see inventory.originalGame for every episode.",
        finalVisualReview=False,gameInternalMeasurementsFabricated=False))
    return additions


if __name__=="__main__":
    for item in build():print(item["episode"],item["scene"],item["sourceIn"],item["sourceOut"],item["label"])
