"""Keep camera diagram labels clear of the original source credits."""
from pathlib import Path
from datetime import datetime, timezone
import json, importlib.util
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/remaining-annotations-v2'
spec=importlib.util.spec_from_file_location('remaining_annotation_v1',Path(__file__).with_name('prepare-polar-remaining-annotations-v1.py'))
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
sha,rel,label,line,arrow,COLORS=previous.sha,previous.rel,previous.label,previous.line,previous.arrow,previous.COLORS

def relative_diagram(d,x,y,opposite=True,formula=False):
    cx=max(210,x-510);cy=max(280,min(330,y-110))
    previous.camera(d,cx,cy)
    tx=x-140
    arrow(d,(tx,y-24),(cx+82,cy-24),COLORS['radius'])
    label(d,(cx-80,cy-94),'대상 → 카메라',COLORS['radius'],27)
    if opposite:
        arrow(d,(cx+82,cy+30),(tx,y+30),COLORS['horizontal'])
        label(d,(cx-80,cy+86),'카메라 → 대상',COLORS['horizontal'],27)
    label(d,(cx-85,cy+155),'상대 관계 · 설명용',size=25)
    if formula:
        label(d,(70,705),'배치 = 카메라 − 중심    시선 = 중심 − 카메라',size=29)

previous.relative_diagram=relative_diagram
annotate=previous.annotate

def main():
    evidence=json.loads((OUT/'remaining-editorial-annotation-preparation-v1.json').read_text(encoding='utf-8'))
    results=[]
    for old in evidence['jobs']:
        sid=old['scene'];folder=LOCAL/sid;folder.mkdir(parents=True,exist_ok=True)
        planfile=ROOT/old['plan'];assert sha(planfile)==old['planSha256']
        plan=json.loads(planfile.read_text(encoding='utf-8'))
        plan.update(createdAt=datetime.now(timezone.utc).isoformat(),previousPlan=rel(planfile),previousPlanSha256=sha(planfile),
          repair='Camera relationship labels stay above y520, clear of source credits628/654. Opposite arrows point beside the rider attention region.',
          preservedSourceCreditRect=[30,628,850,682],sampledLayoutApproved=False,movingTrackApproved=False,allFinalPixelsApproved=False)
        dest=OUT/f'scene{sid}-editorial-annotations-v2.json';assert not dest.exists()
        dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if sid=='08':source_rows=json.loads((OUT/'selected-scene08-execution-v1.json').read_text(encoding='utf-8'))['samples']
        else:
            jobs=json.loads((OUT/'action-clarity-execution-v3.json').read_text(encoding='utf-8'))['jobs']
            source_rows=next(j for j in jobs if str(j['scene'])==sid)['records']
        rows=[]
        for row in source_rows:
            assert sha(ROOT/row['path'])==row['sha256']
            with Image.open(ROOT/row['path']) as im:res=annotate(im,row['frame'],plan)
            p=folder/f"annotation-f{row['frame']:04d}.png";res.save(p)
            rows.append({'frame':row['frame'],'path':rel(p),'sha256':sha(p)})
        boards=[]
        for n in range(0,len(rows),6):
            board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
            for j,row in enumerate(rows[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/row['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                d.text((x+8,y+7),f"scene{sid} repaired overlay f{row['frame']}",fill='white')
            p=folder/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
        results.append({'scene':sid,'plan':rel(dest),'planSha256':sha(dest),'samples':rows,'boards':boards,'preparedOnly':True})
    proof={'preparedAt':datetime.now(timezone.utc).isoformat(),'previousLayoutHeld':'v1 camera labels observed touching original source credits on scene11/16 samples; preserve v1 without using it for final rendering.',
      'jobs':results,'allMovingPixelsApproved':False,'wholeVideoApproved':False}
    p=OUT/'remaining-editorial-annotation-preparation-v2.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scenes':6,'samples':sum(len(j['samples']) for j in results),'boards':sum(len(j['boards']) for j in results),'movingApproval':False}),flush=True)

if __name__=='__main__':main()
