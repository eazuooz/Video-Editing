"""Verify the actual sources, chapter bindings and preview factories before long captures."""
from pathlib import Path
import hashlib,json,subprocess
from edition import ROOT,BATCH,read,save,sha

def input_check():
    files={};results=[];occurrences={}
    for row in read(BATCH/"batch.json")["items"][2:]:
        p=ROOT/"projects"/row["slug"];edition=read(p/"planning/part2-delivery-edition.json")
        plan=read(p/"planning/production-plan.json");bind=read(p/"planning/scene-bindings.json")
        bilingual=read(p/"planning/bilingual-caption-map.json");picture=read(p/"planning/part2-picture-plan.json")
        scripts=[read(p/("script/narration."+lang+".json")) for lang in ("ko","en")]
        assert all(plan[k] for k in ("sourceFinal","narrationFinal","sceneBindingsFinal"))
        assert sha(p/"planning/scene-bindings.json")==picture["sourceBindingsSha256"]==plan["sceneBindingsSha256"]
        for lang,doc in zip(("ko","en"),scripts):
            key=lang+"Sha256";assert bilingual[key]==sha(p/("script/narration."+lang+".json"))
            assert [s["id"] for s in doc["scenes"]]==[s["id"] for s in bind["scenes"]]
        assert set(edition["changedScenes"])==set(picture["teachingFigures"])
        assert all(s["speech"]==t["lines"][0] for s,t in zip(bind["scenes"],scripts[0]["scenes"]))
        clips=[];audit=read(p/"planning/footage-audit.json");sources={s["id"]:s for s in audit["sources"]}
        for s in bind["scenes"]:
            g=s.get("actualGamePart")
            if not g:continue
            source=sources[g["sourceId"]];path=ROOT/source["file"]
            if path not in files:
                h=hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda:stream.read(8*1024*1024),b""):h.update(block)
                dec=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",path]))
                stream=next(v for v in dec["streams"] if v["codec_type"]=="video")
                files[path]=(h.hexdigest(),stream["width"],stream["height"],float(dec["format"]["duration"]))
            h,w,height,seconds=files[path]
            assert h==source["sha256"]==g["sourceSha256"] and min(w,height)>=1080
            assert 0<=g["sourceIn"]<g["sourceOut"]<=seconds+.05 and g["playbackRate"]==1 and not g["freezePadding"] and not g["loop"]
            assert source["recordingPermission"] and (source.get("publisherRights") or source.get("rights"))
            assert source["classification"] in {"independent-gameplay","independent-gameplay-and-menu-operation"}
            clip=dict(scene=s["id"],game=g["game"],role=g["role"],sourceId=g["sourceId"],
                      sourceSha256=h,size=[w,height],start=g["sourceIn"],end=g["sourceOut"])
            clips.append(clip);key=(clip["sourceId"],clip["start"],clip["end"])
            occurrences.setdefault(key,[]).append([row["id"],s["id"]])
        assert len({c["game"] for c in clips})>=3 and clips[0]["scene"]=="000"
        results.append(dict(episode=row["id"],title=row["title"],scenes=len(bind["scenes"]),changed=len(edition["changedScenes"]),clips=clips))
    evidence=dict(episodes=results,sourceFiles=len(files),actualGameCuts=sum(len(x["clips"]) for x in results),
                  recurringExamples=[dict(recording=k[0],window=k[1:],roles=v) for k,v in occurrences.items() if len(v)>1],
                  verifiedScope="Source and layout inputs, not the final rendered videos.")
    save(BATCH/"part2/input-review.json",evidence)
    print(len(results),"lessons;",evidence["sourceFiles"],"FHD source files;",evidence["actualGameCuts"],"game windows")
if __name__=="__main__":input_check()
