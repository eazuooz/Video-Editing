"""Prepare an additive, bilingual lecture edit using verified existing takes only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re, shutil, time

BATCH=Path(__file__).resolve().parents[1]
ROOT=BATCH.parents[2]
def read(path):
    for attempt in range(8):
        try:return json.loads(path.read_text(encoding="utf-8-sig"))
        except (PermissionError,json.JSONDecodeError):
            if attempt==7:raise
            time.sleep(.1)
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(path):
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b""):digest.update(block)
    return digest.hexdigest()
def render_revision(project):
    picture=project/"planning/part2-picture-plan.json"
    revision=read(picture).get("renderRevision","render-v2") if picture.is_file() else "render-v2"
    if not re.fullmatch(r"render-v[2-9]\d*|render-v1\d+",revision):raise ValueError(revision)
    return revision
def passages(source):
    rows={}
    for line in source.read_text("utf8").splitlines():
        if not line.strip(): continue
        if line.startswith("# "):
            current=line[2:].strip()
            assert re.fullmatch(r"\d{3}",current) and current not in rows
            rows[current]=[]
        else:
            ko,en=line.split(" | ")
            assert ko.strip() and en.strip()
            rows[current].append((ko.strip(),en.strip()))
    assert rows and all(rows.values())
    return rows
def groups(rows):
    result=[];ki=ei=0
    for ko,en in rows:
        nk=len(re.split(r"(?<=[.!?])\s+",ko));ne=len(re.split(r"(?<=[.!?])\s+",en))
        result.append(dict(koStart=ki,koCount=nk,enStart=ei,enCount=ne,ko=ko,en=en))
        ki+=nk;ei+=ne
    return result
def prepare(episode,revision,retakes=None):
    control=read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]
    item=next(r for r in read(BATCH/"batch.json")["items"] if r["id"]==episode)
    assert control["productionAllowedNow"] and item["slug"] in control["projectSlugs"] and 23<=int(episode[1:])<=33
    p=ROOT/"projects"/item["slug"]
    src=Path(__file__).parent/(episode.lower()+".txt")
    edit_digest=sha(src)
    extras={}
    if retakes:
        extra_path=Path(__file__).parent/(episode.lower()+"-retakes.txt")
        extras=passages(extra_path)
        edit_digest=hashlib.sha256(src.read_bytes()+b"\0"+extra_path.read_bytes()).hexdigest()
    report=p/"planning/part2-delivery-edition.json"
    if report.exists():
        prev=read(report)
        if prev["audioRevision"]==revision:
            assert prev["editSha256"]==edit_digest,"An edited script requires a new audio revision"
            return
        assert int(revision.split("v")[-1])>int(prev["audioRevision"].split("v")[-1])
    rows=passages(src);rows.update(extras);prod=p/"production"; target=prod/"local"/revision
    if retakes:
        previous_audio=prod/"local"/prev["audioRevision"]
        assert (previous_audio/"narration.wav").is_file() and (previous_audio/"review/source-full-asr.timestamps.json").is_file()
        assert read(previous_audio/"finite-worker.json")["status"]=="voice-generated-review-pending"
    assert re.fullmatch(r"audio-v\d+",revision) and int(revision.split("v")[-1])>=2 and not target.exists()
    ko=read(p/"script/narration.ko.json");en=read(p/"script/narration.en.json")
    bindings=read(p/"planning/scene-bindings.json");mapping=read(p/"planning/bilingual-caption-map.json")
    plan=read(p/"planning/production-plan.json"); integ=read(p/"planning/script-integration.json")
    ids=[x["id"] for x in ko["scenes"]]
    assert set(rows)<=set(ids) and all([x["id"] for x in doc["scenes"]]==ids for doc in [en,bindings,mapping])
    assert sha(p/"script/narration.ko.json")==mapping["koSha256"] and sha(p/"script/narration.en.json")==mapping["enSha256"]
    previous={row["id"]:row["lines"][0] for row in ko["scenes"]}
    for sid,pairs in rows.items():
        index=ids.index(sid);scene=bindings["scenes"][index];before=scene["speech"]
        assert before==previous[sid]
        clauses=[line[0] for line in pairs];spoken=" ".join(clauses)
        ko["scenes"][index].update(lines=[spoken],displayLines=[spoken.replace("여덟 비트","8비트").replace("유브이","UV")])
        en["scenes"][index]["lines"]=[" ".join(line[1] for line in pairs)]
        anchors=[]
        for j,line in enumerate(clauses):
            phrase=line.split(". ")[0].rstrip(".?!")
            assert spoken.count(phrase)==1
            anchors.append(dict(phrase=phrase,character=spoken.index(phrase),position=j/len(clauses)))
        scene.update(speech=spoken,speechPhaseAnchors=anchors)
        if episode=="M23" and sid=="020" and sid in extras:
            # Each state shown by this rig is a distinct inside/outside case.
            cases=clauses[2:6];assert len(cases)==4
            scene["speechPhaseAnchors"]=[dict(phrase=text.rstrip("."),character=spoken.index(text),position=j/4) for j,text in enumerate(cases)]
        game=scene.get("actualGamePart")
        if game and game.get("speechTarget",{}).get("prefixKo") and game["speechTarget"]["prefixKo"] not in spoken:
            game["speechTarget"]["prefixKo"]=clauses[0].split(". ")[0].rstrip(".?!")
            for source in plan.get("nativeGameCueBindings",[]):
                if source["sceneId"]==sid:source["speechTarget"]=dict(game["speechTarget"])
        mapping["scenes"][index]["groups"]=groups(pairs)
        plan["learningSteps"][index].update(retainedExplanation=spoken,screenIntent=clauses[0]+" "+clauses[-1])
    for lang,doc in [("ko",ko),("en",en)]:
        dest=p/f"script/narration.{lang}.json";save(dest,doc)
        (p/f"script/integrated-readthrough.{lang}.txt").write_text("\n\n".join(s["lines"][0] for s in doc["scenes"])+"\n","utf8")
        mapping[lang+"Sha256"]=sha(dest);plan["scriptReadthrough"][lang+"Sha256"]=sha(dest);integ["readThrough"][lang+"Sha256"]=sha(dest)
    bindings["sourceNarrationSha256"]=mapping["koSha256"];save(p/"planning/scene-bindings.json",bindings)
    save(p/"planning/bilingual-caption-map.json",mapping);plan["sceneBindingsSha256"]=sha(p/"planning/scene-bindings.json")
    plan["part2MeaningRevision"]=dict(rules=["meaning-before-values-v1","surface-symbol-guides-v1"],revisedScenes=list(rows),sourceOrderPreserved=True)
    save(p/"planning/production-plan.json",plan);save(p/"planning/script-integration.json",integ)
    prior=sorted((prod/"local").glob("audio-v*"),key=lambda a:int(a.name.split("v")[-1]),reverse=True)
    reuse={}
    changed={s["id"] for s in ko["scenes"] if s["lines"][0]!=previous[s["id"]]}|set(extras)
    for folder in prior:
        derived=folder/"narration.lines.ko.json"
        if not derived.exists():continue
        texts={s["id"]:s["lines"][0] for s in read(derived)["scenes"]}
        for f in (folder/"chunks").glob("*-scene.wav"):
            sid=f.name.split("-")[0]
            if sid in changed or sid in reuse or f.stat().st_size<45 or previous.get(sid)!=texts.get(sid+"-01"):continue
            reuse[sid]=f
    (target/"chunks").mkdir(parents=True)
    reused=[]
    for sid,f in sorted(reuse.items()):
        out=target/"chunks"/f.name;shutil.copy2(f,out);assert sha(out)==sha(f)
        reused.append(dict(scene=sid,file=str(f),sha256=sha(out)))
    manifest=read(prod/"tts-manifest.json");manifest["tts"]["outputDir"]=target.relative_to(ROOT).as_posix()
    newmanifest=prod/f"tts-manifest-{revision}.json";save(newmanifest,manifest)
    save(target/"retake-plan.json",dict(sourceAudioPreserved=True,revisedScenes=list(rows),copied=reused))
    save(report,dict(episode=episode,at=datetime.now(timezone.utc).isoformat(),audioRevision=revision,
         editSha256=edit_digest,changedScenes=list(rows),targetedRetakes=list(extras),sceneCount=len(ids),copiedTakes=reused,
         manifest=newmanifest.relative_to(ROOT).as_posix(),finalReviewReady=False,humanReviewed=False))
    print(episode,len(rows),"revised passages;",len(reused),"preserved takes",newmanifest)
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");ap.add_argument("revision")
    ap.add_argument("--retakes",action="store_true")
    a=ap.parse_args();prepare(a.episode,a.revision,a.retakes)
    if a.retakes:
        from figures import bind
        bind(a.episode)
