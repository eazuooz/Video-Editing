"""Repair fixed-caption/UI spacing and reveal components during the first jump.

Keep original source frames, manually reviewed target keys and narration.
The source's irrelevant top HUD is cropped; its score/speed and CC move up.
Component/camera glyphs are explicitly illustrative, not recovered 3D data.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, importlib.util
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/scene02-annotations-v3'
spec=importlib.util.spec_from_file_location('polar_base',Path(__file__).with_name('prepare-polar-scene02-annotations-v2.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha,rel,label,line,arrow,COLORS=base.sha,base.rel,base.label,base.line,base.arrow,base.COLORS

def reframe(im):
    assert im.size==(1920,1080)
    result=Image.new('RGB',im.size)
    result.paste(im.crop((0,180,1920,1080)),(0,0))
    result.paste(im.crop((0,900,1920,1080)).filter(ImageFilter.GaussianBlur(24)),(0,900))
    return result

def glyph(d,x,y,title):
    x=max(120,x);y=max(290,min(440,y))
    a=(x,y+100);b=(x+200,y+100);c=(x+200,y-70)
    arrow(d,a,b,COLORS['horizontal']);arrow(d,b,c,COLORS['height']);line(d,a,c,COLORS['radius'])
    label(d,(x-10,y+140),'수평 방향',COLORS['horizontal'],27)
    label(d,(x+220,y-5),title,COLORS['height'],27)
    label(d,(x-10,y-125),'성분 구분 · 설명용',size=26)

def annotate(im,frame,plan):
    im=reframe(im)
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);t=frame/60
    x,y=base.point_at(frame,plan['observationKeyframes640'],plan['cuts']);y-=180
    if t<22.72 or t>=34.78:
        for sx in [-1,1]:
            for sy in [-1,1]:
                a=(x+sx*90,y+sy*120)
                line(d,a,(a[0]-sx*28,a[1]),COLORS['focus'],4)
                line(d,a,(a[0],a[1]-sy*28),COLORS['focus'],4)
        label(d,(x+135,max(150,y-125)),'관찰 대상',COLORS['focus'],27)
    if t<3.35:
        label(d,(70,100),'먼저 점프와 착지를 보세요',size=35)
    elif t<7.98:
        label(d,(70,100),'바닥 이동과 높이를 나누어 보세요',size=34)
        glyph(d,x-420,y+45,'높이 성분')
    elif t<15:
        label(d,(70,100),'바닥 방향만으로는 높이를 표현할 수 없습니다',size=32)
        glyph(d,x-420,y+45,'높이 성분')
    elif t<22.72:
        label(d,(70,100),'대상의 위치와 카메라의 시점은 다릅니다',size=32)
        cx,cy=x-440,y+30
        d.rounded_rectangle((cx-36,cy-25,cx+36,cy+25),radius=7,outline=COLORS['radius'],width=6)
        d.polygon([(cx+36,cy-18),(cx+62,cy-32),(cx+62,cy+32),(cx+36,cy+18)],outline=COLORS['radius'])
        arrow(d,(cx+78,cy),(x-110,y),COLORS['radius'])
        label(d,(cx-125,cy+66),'카메라 관계도',COLORS['radius'],27)
    elif t<29.08:
        label(d,(70,100),'같은 위치를 표현하는 두 가지 도구',size=34)
        label(d,(70,175),'원통: 바닥 방향 + 높이',COLORS['height'],30)
        label(d,(70,230),'구면: 거리 + 두 방향각',COLORS['radius'],30)
    elif t<34.78:
        label(d,(70,100),'거리 · 높이 · 시점을 구분해 보세요',size=34)
    elif t<42.5:
        label(d,(70,100),'점프와 착지 전후를 비교해 보세요',size=34)
        glyph(d,x-430,y+30,'높이')
    else:
        label(d,(70,100),'화면 중앙에 있어도 세계에서는 움직입니다',size=32)
        # Original source image-center region shifted by the exact crop.
        d.rectangle((900,190,1020,590),outline=(96,156,236,150),width=3)
        label(d,(70,175),'게임 화면 중앙 기준',COLORS['radius'],27)
    for c in plan['cuts'][1:]:
        if c['sceneStartFrame']<=frame<c['sceneStartFrame']+120:
            label(d,(1320,100),'다른 주행 구간',size=28)
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    LOCAL.mkdir(parents=True,exist_ok=True)
    selected=json.loads((OUT/'selected-scene02-execution-v1.json').read_text(encoding='utf-8'))
    previous=OUT/'scene02-editorial-annotations-v2.json'
    plan=json.loads(previous.read_text(encoding='utf-8'))
    assert selected['exitCode']==0 and plan['frames']==3403
    plan.update(createdAt=datetime.now(timezone.utc).isoformat(),
        previousPlan=rel(previous),previousPlanSha256=sha(previous),
        sourceReframe={'cropTopPixels':180,'activeRect':[0,0,1920,900],
            'bottomBand':'180px blurred original same frame; no invented scene pixels',
            'targetImageTransform':'x unchanged, y minus 180',
            'scoreAndSpeedPreservedAboveCaption':True,
            'topHudIntentionallyExcluded':'Unrelated objective/player-name UI',
            'originalCreditNewY':[628,654]},
        stagesSeconds=[0,3.35,7.98,15,22.72,29.08,34.78,42.5,3403/60],
        fixedNarrationCaptionPosition=[960,970],
        sampledLayoutApproved=False,movingTrackApproved=False,
        finalCaptionPixelsApproved=False,allVideoApproved=False)
    p=OUT/'scene02-editorial-annotations-v3.json';assert not p.exists()
    p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    records=[]
    for r in selected['samples']:
        assert sha(ROOT/r['path'])==r['sha256']
        with Image.open(ROOT/r['path']) as im:res=annotate(im,r['frame'],plan)
        target=LOCAL/f"annotation-f{r['frame']:04d}.png";res.save(target)
        records.append({'frame':r['frame'],'path':rel(target),'sha256':sha(target)})
    boards=[]
    for n in range(0,len(records),6):
        board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
        for j,r in enumerate(records[n:n+6]):
            x=j%3*640;y=j//3*390
            with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
            d.text((x+8,y+7),f"reframed editorial f{r['frame']}",fill='white')
        b=LOCAL/f'board-{n//6+1:02d}.png';board.save(b);boards.append({'path':rel(b),'sha256':sha(b)})
    proof=OUT/'scene02-editorial-annotation-preparation-v3.json';assert not proof.exists()
    proof.write_text(json.dumps({'plan':rel(p),'planSha256':sha(p),'samples':records,'boards':boards,
        'preparedOnly':True,'currentMovingPixelReviewApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preparedSamples':len(records),'boards':len(boards),'movingApproval':False}),flush=True)
if __name__=='__main__':main()
