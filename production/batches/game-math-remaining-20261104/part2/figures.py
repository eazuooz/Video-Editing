"""Bind the edited explanation to the original analytic scene, in measured-speech order."""
from pathlib import Path
import argparse,re
from edition import BATCH,ROOT,read,save,sha,passages
from preview import build

# Formula inputs are bound to each native teaching rig: the graph or game object's state,
# not a second independently animated value. Only the teaching text changes here.
def bind(episode):
    item=next(x for x in read(BATCH/"batch.json")["items"] if x["id"]==episode)
    p=ROOT/"projects"/item["slug"];planfile=p/"planning/production-plan.json"
    plan=read(planfile);bindingfile=p/"planning/scene-bindings.json";binding=read(bindingfile)
    wording=passages(Path(__file__).parent/(episode.lower()+".txt"))
    changes={}; diagrams={}
    if episode=="M23":
        terms={
         "021":("Segment–Plane Intersection","선분과 평면의 교차","경계에서 만나는 점 P"),
         "037":("Specular Strength","정반사 세기","같은 구에서 정반사 세기만 바꿉니다"),
         "053":("Viewport Aspect Ratio","뷰포트 종횡비","창의 폭과 높이를 비교합니다"),
         "054":("Vertical Field of View","수직 시야각","위아래 경계 사이 펼쳐진 각"),
         "055":("Depth Range","깊이 범위","가까운 면과 먼 면의 깊이를 표시합니다"),
         "056":("Perspective Divide","원근 나눗셈","같은 점을 가까운 면에서 먼 면으로 옮깁니다"),
         "057":("Display Aspect Ratio","표시 종횡비","가로가 넓어지는 동안 위아래 경계가 모입니다"),
         "062":("Normal Encoding","법선 인코딩","표면 방향을 색 채널에 기록합니다"),
         "063":("Normal Data","법선 데이터","화살표와 RGB 표본을 같은 값에서 구합니다"),
         "065":("Tangent Handedness","접선 공간의 좌우성","거울 부호만 바꾸면 B가 뒤집힙니다"),
         "066":("Tangent-to-Model Transform","접선 공간에서 모델 공간으로","면이 돌 때 함께 도는 세 축을 봅니다")}
        for sid,(en,ko,goal) in terms.items():
            binding["scenes"][int(sid)]["shot"].update(englishTerm=en,koreanTerm=ko,meaning=goal)
            changes[sid]=dict(purpose=goal,figure="Unity / PipelineMeaningGuides")
        samples=["021","037","053","055","062","065"]
    else:
        for line in (Path(__file__).parent/"figures.txt").read_text("utf8").splitlines():
            head,formula,purpose,target=line.split(" | ")
            ep,sid=head.split()
            if ep==episode:diagrams[sid]=(formula,purpose,target)
        assert diagrams.keys()==wording.keys(),(episode,diagrams.keys()^wording.keys())
        for sid,(formula,purpose,target) in diagrams.items():
            row=binding["scenes"][int(sid)];shot=row["shot"];steps=shot["steps"]
            pairs=wording[sid];anchors=[]
            for j,step in enumerate(steps):
                ix=min(len(pairs)-1,int(j*len(pairs)/len(steps)))
                ko=pairs[ix][0]; phrase=ko.split(". ")[0].rstrip(".?!")
                if not anchors or anchors[-1]["phrase"]!=phrase:
                    anchors.append(dict(phrase=phrase,character=row["speech"].index(phrase),position=j/len(steps)))
                step.update(anchor=phrase,formula=purpose if j==0 and len(steps)>1 else formula,
                            meaning=purpose if len(steps)==1 else target)
                if "model" in step:
                    step["model"]["meaning"]=purpose
                    if "screenIntent" in step["model"]:step["model"]["screenIntent"]=target
            if "motion" in shot:
                shot["motion"]["meaning"]=purpose;shot["guideCaption"]=target
                for step in steps:
                    if step.get("useMotionOverride"):step["motionOverride"]["meaning"]=purpose
            row["speechPhaseAnchors"]=anchors
            changes[sid]=dict(purpose=purpose,formula=formula,figure=target,rig=shot.get("diagramMode") or "existing native teaching stage")
        ids=list(diagrams);samples=sorted({ids[0],ids[len(ids)//2],ids[-1]})
    save(bindingfile,binding)
    plan["sceneBindingsSha256"]=sha(bindingfile)
    for sid,edit in changes.items():plan["learningSteps"][int(sid)]["screenIntent"]=edit["figure"]
    save(planfile,plan)
    display=p/"planning/caption-reading-adjustments.json"
    adjustments=read(display) if display.exists() else {"groups":[]}
    current={ (row["id"],group["koStart"]):group["en"] for row in read(p/"planning/bilingual-caption-map.json")["scenes"]
              for group in row["groups"] }
    adjustments["groups"]=[g for g in adjustments.get("groups",[])
                           if current.get((g["scene"],g["koStart"]))==g["source"]]
    spellings={
        "델타 엑스":"Δx","델타 티":"Δt","델타 브이":"Δv","디 엑스 디 티":"dx/dt",
        "디 와이 디 엑스":"dy/dx","디 디 티":"d/dt","티비엔 기저":"TBN 기저",
        "유브이 좌표":"UV 좌표","여덟 비트":"8비트","오메가 영":"ω₀",
        "런게 쿠타":"Runge–Kutta","오픈지엘":"OpenGL","다이렉트쓰리디":"Direct3D",
        "씨 영 연속":"C⁰ 연속","씨 일 연속":"C¹ 연속","씨 이 연속":"C² 연속",
        "지 영 연속":"G⁰ 연속","지 일 연속":"G¹ 연속","지 이 연속":"G² 연속",
        "피에스아이":"psi","킬로헤르츠":"kHz","슈퍼 마리오 메이커 투":"슈퍼 마리오 메이커 2"}
    adjustments.setdefault("koPrintedForms",{}).update(spellings)
    save(display,adjustments)
    # The M23 diagnostics have already run on the new compiled guides; the
    # revised term chip is bound to the final speech shots, not a new GPU job.
    build(episode,samples)
    stage=p/"production/unity-staging"
    q=stage/"local-preflight-part2-v1/queue.json"
    file=p/"planning/part2-picture-plan.json"
    save(file,dict(episode=episode,preflightQueue=q.relative_to(stage).as_posix(),fingerprint=read(q)["fingerprint"],
                   sourceBlocks=len(binding["scenes"]),teachingFigures=changes,
                   actualGameScenes=[row["id"] for row in binding["scenes"] if row.get("actualGamePart")],
                   actualInternalMasterReview=False,sourceBindingsSha256=sha(bindingfile)))
    print(episode,len(changes),"symbol scenes;",len(samples),"moving preview shots")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");bind(ap.parse_args().episode)
