"""Test caption and diagram anchors against the recorded words of the preserved takes."""
from pathlib import Path
import argparse, importlib.util, sys
from edition import BATCH,ROOT,read,save

def inspect(episode,early=False):
    item=next(x for x in read(BATCH/"batch.json")["items"] if x["id"]==episode)
    project=ROOT/"projects"/item["slug"];doc=read(project/"planning/part2-delivery-edition.json")
    sys.argv=[str(BATCH/"align-module-speech.py"),"--project",project.name,"--audio-revision",doc["audioRevision"]]
    spec=importlib.util.spec_from_file_location("word_alignment",BATCH/"align-module-speech.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    scenes={r["id"]:r for r in read(project/"planning/scene-bindings.json")["scenes"]}
    results=[]
    entries=[]
    if early:
        for f in sorted((project/"production/local"/doc["audioRevision"]/"review/early-pcm").glob("*.json")):
            s=read(f);entries.append((f.stem.split("-")[0],s["sourceText"],s["recognized"]["chunks"],s["recognized"]["text"]))
    else:
        for take in doc["copiedTakes"]:
            sid=take["scene"]
            options=[Path(take["file"]).parents[1], *sorted((project/"production/local").glob("audio-v*"),reverse=True)]
            original=next((p for p in options if (p/"review/paragraphs"/(sid+"-01.json")).is_file()
                           and (p/"chunks"/Path(take["file"]).name).is_file()
                           and mod.sha(p/"chunks"/Path(take["file"]).name)==take["sha256"]),None)
            if not original:continue
            s=read(original/"review/paragraphs"/(sid+"-01.json"));entries.append((sid,s["entry"]["text"],s["chunks"],s["text"]))
    for sid,speech,chunks,transcript in entries:
        assert speech==scenes[sid]["speech"]
        words,_=mod.same_audio_overlap([w for w in chunks if None not in w["timestamp"]])
        expected,actual,mapping,owners,_=mod.map_chars(speech,words)
        problems=[];cursor=0
        cues=[]
        for clause in mod.chunks(speech):
            pos=speech.index(clause,cursor);cues.append((clause,pos));cursor=pos+len(clause)
        cues += [(v["phrase"],v["character"]) for v in scenes[sid]["speechPhaseAnchors"]]
        for phrase,pos in cues:
            try:mod.phrase_time(speech,phrase,mapping,owners,pos)
            except ValueError:problems.append(phrase)
        coverage=round(len(mapping)/max(1,len(expected)),3)
        result=dict(scene=sid,coverage=coverage,unresolved=problems)
        if coverage<.93 or problems:result.update(expected=speech,recognized=transcript)
        results.append(result)
    category="early" if early else "existing"
    save(BATCH/"local/part2-20261106"/(episode+"-"+category+"-word-check.json"),results)
    print(episode,len(results),"recorded paragraphs;",[(r["scene"],r["coverage"],r["unresolved"]) for r in results if r["unresolved"] or r["coverage"]<.93])
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");ap.add_argument("--early",action="store_true");a=ap.parse_args()
    inspect(a.episode,a.early)
