"""Repair the attitude glyph only; preserve other v2 scene layouts."""
from pathlib import Path
from datetime import datetime, timezone
import json, importlib.util
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/remaining-annotations-v3/08'
spec=importlib.util.spec_from_file_location('remaining_annotation_v2',Path(__file__).with_name('prepare-polar-remaining-annotations-v2.py'))
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
sha,rel,label,line,arrow,COLORS=previous.sha,previous.rel,previous.label,previous.line,previous.arrow,previous.COLORS

def annotate(im,frame,plan):
    if plan['scene']!='08':return previous.annotate(im,frame,plan)
    im=previous.previous.base.reframe(im)
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);t=frame/60
    x,y=previous.previous.base.base.point_at(frame,plan['observationKeyframes640'],plan['cuts']);y-=180
    previous.previous.bracket(d,x,y)
    if t<8.98:head='보는 방향과 자전거 자세를 구분하세요'
    elif t<14.9:head='진행 방향 · 차체의 기울기'
    elif t<22.62:head='헤딩 + 피치 = 한 방향, 전체 자세는 별도'
    elif t<27.88:head='화면이 기울어도 세계의 위쪽 축은 별도입니다'
    elif t<36:head='축을 확인하고 각도의 역할을 나누어 봅니다'
    elif t<45.92:head='같은 방향으로 가면서 차체는 회전할 수 있습니다'
    else:head='화면의 세로 위치 ≠ 세계 좌표의 높이'
    label(d,(70,100),head,size=32)
    if t<22.62 or 36<=t<45.92:
        gx=max(210,x-490);gy=max(275,min(330,y-120))
        arrow(d,(gx-60,gy),(gx+145,gy),COLORS['horizontal'])
        d.arc((gx-65,gy+45,gx+55,gy+165),15,315,fill=COLORS['radius'],width=6)
        label(d,(gx-110,gy-68),'방향',COLORS['horizontal'],28)
        label(d,(gx+90,gy+85),'자세 회전',COLORS['radius'],28)
        label(d,(gx-110,gy+195),'두 역할 · 설명용',size=25)
    elif t<36:
        label(d,(70,230),'위쪽 축은 세계의 약속, 화면 기울기는 투영 결과',COLORS['height'],28)
    else:
        line(d,(1750,230),(1750,735),COLORS['radius'],4)
        label(d,(1350,180),'화면 세로 기준',COLORS['radius'],27)
        label(d,(70,230),'세계 높이는 정한 위쪽 축으로 잽니다',COLORS['height'],28)
    for c in plan['cuts'][1:]:
        if c['sceneStartFrame']<=frame<c['sceneStartFrame']+120:
            label(d,(1420,175),'다른 주행 구간',size=26)
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    evidence=json.loads((OUT/'remaining-editorial-annotation-preparation-v2.json').read_text(encoding='utf-8'))
    old=next(j for j in evidence['jobs'] if j['scene']=='08')
    oldplan=ROOT/old['plan'];assert sha(oldplan)==old['planSha256']
    plan=json.loads(oldplan.read_text(encoding='utf-8'))
    plan.update(createdAt=datetime.now(timezone.utc).isoformat(),previousPlan=rel(oldplan),previousPlanSha256=sha(oldplan),
      repair='Scene08 illustrative direction/attitude glyph labels stay above y580, leaving source credit628/654px clear.',sampledLayoutApproved=False,movingTrackApproved=False)
    dest=OUT/'scene08-editorial-annotations-v3.json';assert not dest.exists()
    dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    LOCAL.mkdir(parents=True,exist_ok=True)
    records=json.loads((OUT/'selected-scene08-execution-v1.json').read_text(encoding='utf-8'))['samples'];rows=[]
    for row in records:
        assert sha(ROOT/row['path'])==row['sha256']
        with Image.open(ROOT/row['path']) as im:res=annotate(im,row['frame'],plan)
        p=LOCAL/f"annotation-f{row['frame']:04d}.png";res.save(p);rows.append({'frame':row['frame'],'path':rel(p),'sha256':sha(p)})
    boards=[]
    for n in range(0,len(rows),6):
        board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
        for j,row in enumerate(rows[n:n+6]):
            x=j%3*640;y=j//3*390
            with Image.open(ROOT/row['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
            d.text((x+8,y+7),f"scene08 credit-clear overlay f{row['frame']}",fill='white')
        p=LOCAL/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
    new={'scene':'08','plan':rel(dest),'planSha256':sha(dest),'samples':rows,'boards':boards,'preparedOnly':True}
    proof={'preparedAt':datetime.now(timezone.utc).isoformat(),
      'previous08Held':'Direction/attitude glyph in v2 touched source credits; preserve sampled history and render v3.',
      'jobs':[new if j['scene']=='08' else j for j in evidence['jobs']],
      'allMovingPixelsApproved':False,'wholeVideoApproved':False}
    p=OUT/'remaining-editorial-annotation-preparation-v3.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'targetScene':'08','samples':len(rows),'boards':len(boards),'otherFiveV2Preserved':True}),flush=True)
if __name__=='__main__':main()
