"""Repair misleading attention brackets, retain narrated maths over actual play.

The six pilots showed that the broad rider bracket was not a reliable object
tracker. Remove it; clearly labelled models explain components, subtraction
and separate position/attitude/viewpoint roles. No engine reconstruction.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, importlib.util, math
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/remaining-annotations-v4'
spec=importlib.util.spec_from_file_location('remaining_v3',Path(__file__).with_name('prepare-polar-remaining-annotations-v3.py'))
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
v2=previous.previous;v1=v2.previous;base=v1.base
sha,rel,label,line,arrow,COLORS=v1.sha,v1.rel,v1.label,v1.line,v1.arrow,v1.COLORS

def relative_diagram(d,x,y,opposite=True,formula=False):
    # Fixed side diagram. Camera/target symbols are deliberately separated
    # from the rider pixels: neither is a recovered world/image position.
    cx,cy=280,330;tx,ty=660,420
    v1.camera(d,cx,cy)
    d.ellipse((tx-9,ty-9,tx+9,ty+9),fill=COLORS['focus'])
    label(d,(tx-58,ty+34),'중심(대상)',COLORS['focus'],27)
    arrow(d,(tx-18,ty-24),(cx+82,cy-24),COLORS['radius'])
    label(d,(195,238),'대상 → 카메라',COLORS['radius'],27)
    if opposite:
        arrow(d,(cx+82,cy+32),(tx-18,ty+32),COLORS['horizontal'])
        label(d,(195,490),'카메라 → 대상',COLORS['horizontal'],27)
    label(d,(195,552),'상대 벡터 관계도 · 설명용',size=25)
    if formula:label(d,(70,705),'배치 = 카메라 − 중심    시선 = 중심 − 카메라',size=29)

def summary_shapes(im,frame,plan):
    result=base.reframe(im);layer=Image.new('RGBA',result.size);d=ImageDraw.Draw(layer);t=frame/60
    if t<9.44:head='위치 · 자세 · 카메라 시점을 나누어 보세요'
    elif t<19.1:head='좌표 계산에 충돌 · 회전 · 추적 규칙을 더합니다'
    elif t<24.44:head='거리와 방향의 관계에 극좌표를 적용합니다'
    else:head='공식이 유용한 범위와 설명하지 않는 부분을 구분합니다'
    label(d,(70,100),head,size=31)
    # Three distinct types of quantity, with no inferred game values.
    arrow(d,(110,300),(245,300),COLORS['focus'])
    arrow(d,(110,300),(110,205),COLORS['focus'])
    d.ellipse((173,242,191,260),fill=COLORS['focus'])
    label(d,(285,240),'위치: 어디에 있는가',COLORS['focus'],30)
    line(d,(285,295),(420,295),COLORS['focus'],4)
    d.arc((120,350,220,450),25,315,fill=COLORS['horizontal'],width=6)
    arrow(d,(170,400),(210,350),COLORS['horizontal'])
    label(d,(285,370),'자세: 어떻게 기울었는가',COLORS['horizontal'],30)
    v1.camera(d,150,525)
    line(d,(215,505),(260,480),COLORS['radius'],4)
    line(d,(215,545),(260,570),COLORS['radius'],4)
    line(d,(260,480),(260,570),COLORS['radius'],4)
    label(d,(285,505),'시점: 어디에서 보는가',COLORS['radius'],30)
    label(d,(70,595),'역할 구분 · 설명용 모형',size=26)
    if t>=9.44:label(d,(70,705),'서로 연결되지만 같은 값은 아닙니다',size=29)
    return Image.alpha_composite(result.convert('RGBA'),layer).convert('RGB')

# Module-local overrides do not edit any historical file or render.
v1.bracket=lambda *args:None
v1.relative_diagram=relative_diagram
def annotate(im,frame,plan):
    if plan['scene']=='18':return summary_shapes(im,frame,plan)
    return previous.annotate(im,frame,plan)

def main():
    proofpath=OUT/'remaining-editorial-annotation-preparation-v4.json';assert not proofpath.exists()
    evidence=json.loads((OUT/'remaining-editorial-annotation-preparation-v3.json').read_text(encoding='utf-8'))
    repaired=json.loads((OUT/'selected-scene08-execution-v2.json').read_text(encoding='utf-8'))
    assert repaired['status']=='completed' and repaired['exitCode']==0 and repaired['frames']==3743
    jobs=[]
    for old in evidence['jobs']:
        sid=old['scene'];prior=ROOT/old['plan'];assert sha(prior)==old['planSha256']
        plan=json.loads(prior.read_text(encoding='utf-8'))
        plan.update(createdAt=datetime.now(timezone.utc).isoformat(),previousPlan=rel(prior),previousPlanSha256=sha(prior),
          repair='Remove inaccurate whole-rider attention brackets. Keep the spoken component/vector relationships as explicit explanatory shapes over game footage.',
          target='Actual rider/action is watched directly. Labelled mathematical models are explanatory, not an object tracker or inferred engine/world coordinates.',
          inaccurateWholeObjectBracketRemoved=True,sampledLayoutApproved=False,movingTrackApproved=False,allFinalPixelsApproved=False)
        if sid=='08':
            plan.update(source=repaired['sourceCandidate'],sourceSha256=repaired['sourceCandidateSha256'],
              cuts=[{'sceneStartFrame':c['sceneStartFrame'],'frames':c['frames']} for c in repaired['cuts']],
              sourceRepairEvidence='projects/game-math-polar-3d/revision-teaching-clarity-v1/scene08-selected-source-direct-review-v2.json')
            rows=repaired['samples'];oldkeys={k[0]:k[1:] for k in plan['observationKeyframes640']}
            keys=[]
            for r in rows:
                f=r['frame'];oldf=r.get('previousSceneFrame',f)
                xy=oldkeys.get(oldf,[318,230])
                # Glyphs are explanatory and clamped to the left upper side;
                # these keys never claim to track the complete body/head.
                keys.append([f,*xy])
            plan['observationKeyframes640']=keys
        else:
            oldstate=json.loads((OUT/'action-clarity-execution-v3.json').read_text(encoding='utf-8'))
            rows=next(j for j in oldstate['jobs'] if str(j['scene'])==sid)['records']
        assert sha(ROOT/plan['source'])==plan['sourceSha256']
        dest=OUT/f'scene{sid}-editorial-annotations-v4.json';assert not dest.exists()
        dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        folder=LOCAL/sid;folder.mkdir(parents=True,exist_ok=False);images=[]
        for row in rows:
            assert sha(ROOT/row['path'])==row['sha256']
            with Image.open(ROOT/row['path']) as im:res=annotate(im,row['frame'],plan)
            p=folder/f"annotation-f{row['frame']:04d}.png";res.save(p)
            images.append({'frame':row['frame'],'path':rel(p),'sha256':sha(p)})
        boards=[]
        for n in range(0,len(images),6):
            board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
            for j,row in enumerate(images[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/row['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                d.text((x+8,y+7),f"scene{sid} v4 f{row['frame']}",fill='white')
            p=folder/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
        jobs.append({'scene':sid,'plan':rel(dest),'planSha256':sha(dest),'samples':images,'boards':boards,'preparedOnly':True})
    proofpath.write_text(json.dumps({'preparedAt':datetime.now(timezone.utc).isoformat(),'jobs':jobs,
      'narrationChanged':False,'allMovingPixelsApproved':False,'wholeVideoApproved':False,
      'historyPreserved':True,'newImageGitAdded':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scenes':6,'samples':sum(len(j['samples']) for j in jobs),'boards':sum(len(j['boards']) for j in jobs),'movingApproval':False}),flush=True)
if __name__=='__main__':main()
