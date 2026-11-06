"""Render reviewed mathematical spelling on the original subtitle clock."""
import json

def apply(project,revision,rows,source_srt,destination):
    plan=project/"planning/printed-symbol-cues.json"
    if not plan.exists():return 0
    data=json.loads(plan.read_text("utf-8-sig"))
    if data["renderRevision"]!=revision:return 0
    changes={(r["scene"],r["original"]):r["caption"] for r in data["edits"]}
    assert len(changes)==len(data["edits"])
    blocks=source_srt.read_text("utf-8-sig").strip().split("\n\n")
    assert len(blocks)==len(rows)
    applied=set()
    for i,row in enumerate(rows):
        header,time,text=blocks[i].split("\n",2)
        assert int(header)==i+1 and text==row["text"]
        key=(row["scene"],text)
        if key not in changes:continue
        assert key not in applied and changes[key].strip()
        row["text"]=changes[key];blocks[i]="\n".join([header,time,row["text"]]);applied.add(key)
    assert applied==set(changes),set(changes)-applied
    destination.write_text("\n\n".join(blocks)+"\n",encoding="utf8")
    return len(applied)
