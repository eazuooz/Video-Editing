"""Collect source-matched Unity preview frames and existing concept-matched game cuts."""
from edition import ROOT,BATCH,read,save
from pathlib import Path
from PIL import Image,ImageDraw

def inspect():
    work=BATCH/"local/part2-20261106/source-contact";work.mkdir(parents=True,exist_ok=True)
    cards=[];inventory=[]
    for row in read(BATCH/"batch.json")["items"][2:]:
        project=ROOT/"projects"/row["slug"]
        stage=project/"production/unity-staging"
        candidates=[p for p in stage.glob("local-preflight-v*/queue.json")
                    if (p.parent/"progress.json").exists() and read(p.parent/"progress.json")["status"]=="images-ready-for-internal-visual-QA"]
        q=max(candidates,key=lambda p:int(p.parent.name.split("v")[-1]))
        jobs=read(q)["jobs"];selected=[jobs[i] for i in sorted({0,len(jobs)//2,len(jobs)-1})]
        audit=read(project/"planning/footage-audit.json")
        frames=[]
        for jp in selected:
            job=read(Path(jp));receipt=read(Path(job["output"])/"structural-check.json")
            frame=Path(receipt["frames"][len(receipt["frames"])//2]["path"])
            cards.append((row["id"],frame));frames.append(str(frame))
        inventory.append(dict(episode=row["id"],slug=row["slug"],runtimeQueue=str(q),sampleFrames=frames,
                             actualGames=[s.get("game",s.get("title")) for s in audit["sources"]]))
    for index,start in enumerate(range(0,len(cards),12)):
        group=cards[start:start+12];im=Image.new("RGB",(1200,((len(group)+2)//3)*250),"#141414")
        draw=ImageDraw.Draw(im)
        for j,(ep,p) in enumerate(group):
            x=j%3*400;y=j//3*250
            with Image.open(p) as src: im.paste(src.convert("RGB").resize((400,225),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+9,y+229),ep+" / "+p.parent.name,fill="white")
        im.save(work/f"source-{index}.jpg",quality=94)
    save(work/"inventory.json",inventory)
if __name__=="__main__":inspect()
