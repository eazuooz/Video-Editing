"""Prepare editable, narrated observation overlays for six retained game slots.

The image-space brackets identify an attention region. Separate labelled
diagrams explain coordinate relationships without inventing engine data.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, importlib.util, math
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/remaining-annotations-v1'
spec=importlib.util.spec_from_file_location('polar_annotation_base',Path(__file__).with_name('prepare-polar-scene02-annotations-v3.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha,rel,label,line,arrow,COLORS=base.sha,base.rel,base.label,base.line,base.arrow,base.COLORS

DATA={
 '05':{'frames':2558,'startFrame':10137,'stages':[0,6.14,14.36,21.62,32.04],
 'cutFrames':[0],'sampleFrames':[0,240,480,720,960,1200,1440,1680,1920,2160,2400,2557],
 'points':[(330,210),(315,212),(298,226),(318,230),(309,223),(315,235),(309,225),(304,221),(308,232),(317,235),(320,191),(317,231)],
 'claim':'Coordinate-plane projection and world height differ from clearance above sloped terrain.'},
 '08':{'frames':3743,'startFrame':19263,'stages':[0,8.98,14.9,22.62,27.88,36,45.92],
 'cutFrames':[0,1560,2070,2423],
 'claim':'Viewing direction, bicycle attitude and image tilt are separate. No engine heading/pitch or world-up measurement is inferred.'},
 '11':{'frames':3429,'startFrame':28330,'stages':[0,9.22,14.9,24.086667,30,35.52,43.28],
 'cutFrames':[0,2131],'sampleFrames':[0,240,480,720,960,1200,1440,1680,1920,2130,2131,2132,2160,2400,2640,2880,3120,3360,3428],
 'points':[(320,217),(319,219),(318,207),(313,218),(328,236),(321,237),(318,228),(318,227),(331,239),(325,237),(321,230),(321,230),(318,232),(316,239),(321,230),(319,221),(301,233),(321,239),(317,240)],
 'claim':'Target, camera placement and look direction are separate relationships; the diagram is not a reconstruction of exact camera coordinates.'},
 '14':{'frames':2443,'startFrame':36915,'stages':[0,7.26,14.46,23.02,28.44],
 'cutFrames':[0],'sampleFrames':[0,240,480,720,960,1200,1440,1680,1920,2160,2400,2442],
 'points':[(318,210),(314,226),(319,227),(292,235),(330,225),(334,239),(319,221),(320,226),(297,234),(291,239),(292,239),(319,243)],
 'claim':'Canonical polar representation and smooth following/pitch policy are different tasks; this footage does not prove a pole or this game\'s implementation.'},
 '16':{'frames':3848,'startFrame':42025,'stages':[0,9.1,16.82,25.94,34.34,41.12,50.2],
 'cutFrames':[0,2468],'sampleFrames':[0,240,480,720,960,1200,1440,1680,1920,2160,2400,2467,2468,2469,2640,2880,3120,3360,3600,3840,3847],
 'points':[(321,217),(316,225),(318,236),(341,220),(299,222),(321,231),(320,213),(318,224),(323,225),(340,225),(320,222),(310,220),(319,222),(319,222),(318,235),(318,236),(305,244),(347,251),(315,225),(348,218),(327,224)],
 'claim':'Opposite subtraction order reverses the relative vector. Desired placement, tracking speed and obstruction rules must be treated separately.'},
 '18':{'frames':1934,'startFrame':48871,'stages':[0,9.44,19.1,24.44],
 'cutFrames':[0],'sampleFrames':[0,240,480,720,960,1200,1440,1680,1920,1933],
 'points':[(323,214),(331,216),(322,237),(325,232),(322,234),(319,218),(320,222),(333,237),(318,225),(318,221)],
 'claim':'Position, attitude and viewpoint need distinct rules; polar coordinates are useful for distance/direction rather than all game behaviour.'}
}

def bracket(d,x,y):
    # Broad whole-rider attention region, not a precision helmet tracker.
    for sx in [-1,1]:
        for sy in [-1,1]:
            a=(x+sx*105,y+sy*132)
            line(d,a,(a[0]-sx*28,a[1]),COLORS['focus'],4)
            line(d,a,(a[0],a[1]-sy*28),COLORS['focus'],4)
    label(d,(min(1650,x+150),max(210,y-142)),'관찰 대상',COLORS['focus'],26)

def camera(d,x,y):
    d.rounded_rectangle((x-36,y-25,x+36,y+25),radius=7,outline=COLORS['radius'],width=6)
    d.polygon([(x+36,y-18),(x+62,y-32),(x+62,y+32),(x+36,y+18)],outline=COLORS['radius'])

def relative_diagram(d,x,y,opposite=True,formula=False):
    # Side-of-action explanatory icon; never claimed as the image location
    # of the unseen recording camera.
    cx=max(210,x-510);cy=max(320,min(530,y))
    camera(d,cx,cy)
    tx=x-140
    arrow(d,(tx,cy-24),(cx+82,cy-24),COLORS['radius'])
    label(d,(cx-80,cy-94),'대상 → 카메라',COLORS['radius'],27)
    if opposite:
        arrow(d,(cx+82,cy+30),(tx,cy+30),COLORS['horizontal'])
        label(d,(cx-80,cy+86),'카메라 → 대상',COLORS['horizontal'],27)
    label(d,(cx-85,cy+155),'상대 관계 · 설명용',size=25)
    if formula:
        label(d,(70,705),'배치 = 카메라 − 중심    시선 = 중심 − 카메라',size=29)

def annotate(im,frame,plan):
    im=base.reframe(im)
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);t=frame/60
    x,y=base.base.point_at(frame,plan['observationKeyframes640'],plan['cuts']);y-=180
    scene=plan['scene']
    bracket(d,x,y)
    if scene=='05':
        if t<6.14:head='경사로에서 앞으로 가는 이동과 점프를 보세요'
        elif t<14.36:head='바닥으로 내려 본 위치 + 높이'
        elif t<21.62:head='수평 거리와 높이는 따로 변할 수 있습니다'
        elif t<32.04:head='세계의 높이 ≠ 경사진 지면까지의 거리'
        else:head='높이를 잴 기준 평면부터 정합니다'
        label(d,(70,100),head,size=33)
        if t>=6.14:
            base.glyph(d,x-490,y+15,'높이 성분')
            label(d,(70,710),'정한 좌표 평면으로 투영한 설명입니다',size=28)
    elif scene=='08':
        if t<8.98:head='보는 방향과 자전거 자세를 구분하세요'
        elif t<14.9:head='진행 방향 · 차체의 기울기'
        elif t<22.62:head='헤딩 + 피치 = 한 방향, 전체 자세는 별도'
        elif t<27.88:head='화면이 기울어도 세계의 위쪽 축은 별도입니다'
        elif t<36:head='축을 확인하고 각도의 역할을 나누어 봅니다'
        elif t<45.92:head='같은 방향으로 가면서 차체는 회전할 수 있습니다'
        else:head='화면의 세로 위치 ≠ 세계 좌표의 높이'
        label(d,(70,100),head,size=32)
        if t<22.62 or 36<=t<45.92:
            gx=max(210,x-490);gy=max(320,min(500,y))
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
    elif scene=='11':
        if t<9.22:head='카메라의 높이와 떨어진 거리가 구도를 바꿉니다'
        elif t<14.9:head='이 화면만으로 정확한 카메라 좌표는 알 수 없습니다'
        elif t<24.086667:head='대상 위치 · 상대 배치 · 바라보는 방향'
        elif t<30:head='상대 벡터 = 카메라 위치 − 대상 위치'
        elif t<35.52:head='같은 점의 여러 표현 → 대표 표현을 정리합니다'
        elif t<43.28:head='화면 중심은 비슷해도 세계에서는 이동합니다'
        else:head='대상 위치를 빼고, 수평 길이와 높이로 나눕니다'
        label(d,(70,100),head,size=31)
        if t<35.52:relative_diagram(d,x,y,t>=14.9)
        elif t<43.28:
            d.rectangle((900,190,1020,590),outline=(96,156,236,150),width=3)
            label(d,(70,215),'게임 화면 중앙 기준',COLORS['radius'],27)
        else:
            base.glyph(d,x-490,y,'상대 높이')
            label(d,(70,710),'정확한 엔진 좌표를 복원한 그림은 아닙니다',size=27)
    elif scene=='14':
        if t<7.26:head='배치 계산만으로 따라가는 방식이 정해지지는 않습니다'
        elif t<14.46:head='추적 속도 · 허용할 위아래 각도는 설계 선택'
        elif t<23.02:head='극점 근처의 헤딩 변화와 실제 큰 이동은 다릅니다'
        elif t<28.44:head='대표 표현 정리와 부드러운 화면은 별도입니다'
        else:head='우리가 카메라를 만들 때 검토할 지점입니다'
        label(d,(70,100),head,size=31)
        if t<14.46:
            relative_diagram(d,x,y,False)
            label(d,(70,710),'방향 계산 뒤에 추적 정책을 더합니다',size=29)
        else:
            label(d,(70,235),'숫자 규칙: 대표 표현 정리',COLORS['horizontal'],30)
            label(d,(70,305),'화면 규칙: 제한 + 부드러운 추적',COLORS['radius'],30)
            label(d,(70,385),'현재 주행은 극점 실험이나 내부 구현 증거가 아닙니다',size=27)
    elif scene=='16':
        if t<9.1:head='대상과 카메라 사이의 관계를 떠올려 보세요'
        elif t<16.82:head='대상에서 카메라로 · 카메라에서 대상으로'
        elif t<25.94:head='같은 두 점도 뺄셈 순서에 따라 반대 방향'
        elif t<34.34:head='대상 이동 → 중심 갱신 → 원하는 배치 → 추적'
        elif t<41.12:head='구면좌표는 배치를 위한 도구입니다'
        elif t<50.2:head='중심이 이동해도 상대 관계는 유지할 수 있습니다'
        else:head='원하는 배치 뒤에 가림과 추적 속도를 확인합니다'
        label(d,(70,100),head,size=31)
        relative_diagram(d,x,y,t>=9.1,16.82<=t<25.94)
        if 25.94<=t<34.34:
            label(d,(70,735),'중심 갱신 → 배치 계산 → 실제 이동',size=28)
        elif t>=50.2:
            label(d,(70,735),'대상이 가려지는가?  얼마나 빨리 따라가는가?',size=27)
    elif scene=='18':
        if t<9.44:head='위치 · 자세 · 카메라 시점을 나누어 보세요'
        elif t<19.1:head='좌표 계산에 충돌 · 회전 · 추적 규칙을 더합니다'
        elif t<24.44:head='거리와 방향의 관계에 극좌표를 적용합니다'
        else:head='공식이 유용한 범위와 설명하지 않는 부분을 구분합니다'
        label(d,(70,100),head,size=31)
        label(d,(70,235),'위치: 어디에 있는가',COLORS['focus'],30)
        label(d,(70,305),'자세: 어떻게 기울었는가',COLORS['horizontal'],30)
        label(d,(70,375),'시점: 어디에서 보는가',COLORS['radius'],30)
        if t>=9.44:label(d,(70,465),'서로 연결되지만 같은 값은 아닙니다',size=29)
    for c in plan['cuts'][1:]:
        if c['sceneStartFrame']<=frame<c['sceneStartFrame']+120:
            label(d,(1420,175),'다른 주행 구간',size=26)
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    assert not (OUT/'remaining-editorial-annotation-preparation-v1.json').exists()
    selected=json.loads((OUT/'selected-scene08-execution-v1.json').read_text(encoding='utf-8'))
    assert selected['exitCode']==0 and len(selected['samples'])==69 and len(selected['boards'])==12
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in selected['samples']+selected['boards'])
    old=json.loads((OUT/'action-clarity-execution-v3.json').read_text(encoding='utf-8'))
    coords08=[(317,216),(317,223),(318,229),(317,228),(316,228),(318,229),
      (317,235),(315,230),(318,231),(323,217),(318,225),(346,266),
      (316,234),(316,235),(334,234),(320,220),(320,199),(319,226),
      (322,235),(318,230),(353,229),(336,233),(317,223),(333,250),
      (324,268),(330,230),(329,231),(308,231),(320,230),(311,231),
      (296,235),(350,232),(317,234),(316,231),(310,230),(318,229),
      (311,216),(315,231),(321,231),(318,238),(310,230),(297,232),
      (359,230),(314,230),(320,230),(311,230),(311,226),(310,212),
      (316,225),(310,242),(330,230),(319,230),(311,235),(317,235),
      (330,235),(337,228),(312,236),(294,235),(310,232),(316,228),
      (318,230),(330,230),(326,231),(319,230),(317,211),(320,230),
      (327,230),(319,231),(319,193)]
    assert len(coords08)==69
    all_results=[]
    for sid,data in DATA.items():
        folder=LOCAL/sid;folder.mkdir(parents=True,exist_ok=True)
        if sid=='08':
            records=selected['samples'];keys=[[r['frame'],*xy] for r,xy in zip(records,coords08)]
            source=ROOT/selected['sourceCandidate'];source_sha=selected['sourceCandidateSha256']
        else:
            job=next(j for j in old['jobs'] if str(j['scene'])==sid)
            records=job['records'];keys=[[f,*xy] for f,xy in zip(data['sampleFrames'],data['points'])]
            assert [r['frame'] for r in records]==data['sampleFrames']
            source=ROOT/f'shared/output/game-math-polar-3d/clips/{sid}.mp4';source_sha=job['sourceSha256']
        assert sha(source)==source_sha
        cuts=[{'sceneStartFrame':a,'frames':b-a} for a,b in zip(data['cutFrames'],data['cutFrames'][1:]+[data['frames']])]
        plan={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'scene':sid,
          'source':rel(source),'sourceSha256':source_sha,'frames':data['frames'],'globalStartFrame':data['startFrame'],
          'cuts':cuts,'observationKeyframes640':keys,'stagesSeconds':data['stages']+[data['frames']/60],
          'semanticColors':COLORS,'claim':data['claim'],'target':'Broad whole-rider observation region in image pixels. Diagrams beside it are explanatory, not recovered engine/world coordinates.',
          'sourceReframe':{'cropTopPixels':180,'activeRect':[0,0,1920,900],'bottomBand':'180px blurred original same frame','targetImageTransform':'x unchanged; y minus180','creditNewY':[628,654]},
          'fixedNarrationCaptionPosition':[960,970],'narrationChanged':False,
          'sampledLayoutApproved':False,'movingTrackApproved':False,'allFinalPixelsApproved':False}
        p=OUT/f'scene{sid}-editorial-annotations-v1.json';assert not p.exists()
        p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        images=[]
        for r in records:
            assert sha(ROOT/r['path'])==r['sha256']
            with Image.open(ROOT/r['path']) as im:res=annotate(im,r['frame'],plan)
            dest=folder/f"annotation-f{r['frame']:04d}.png";res.save(dest)
            images.append({'frame':r['frame'],'path':rel(dest),'sha256':sha(dest)})
        boards=[]
        for n in range(0,len(images),6):
            board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
            for j,r in enumerate(images[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                d.text((x+8,y+7),f"scene{sid} overlay f{r['frame']}",fill='white')
            dest=folder/f'board-{n//6+1:02d}.png';board.save(dest);boards.append({'path':rel(dest),'sha256':sha(dest)})
        all_results.append({'scene':sid,'plan':rel(p),'planSha256':sha(p),'samples':images,'boards':boards,'preparedOnly':True})
    selection={'reviewedAt':datetime.now(timezone.utc).isoformat(),'actualOuterExitCode':0,'sessionId':20597,'exitObservedChunk':'fa31e0',
      'all69SelectedSamplesDirectlyRead':selected['samples'],'all12SelectedBoardsDirectlyRead':selected['boards'],
      'sourceCandidateSha256':selected['sourceCandidateSha256'],'nativePtsVerified':all(c['allNativePtsVerified'] for c in selected['cuts']),
      'observations':['Original first26s retains ramps, visible rotations, landings and turns.','Fresh26–34.5s and34.5–40.383333s show normal turns and following view without the unrelated team unlock; later crash/recovery is excluded.','Final original30–52s has ramp,air,turns and final approach, never a claimed uninterrupted race across the four source intervals.'],
      'sampledFootageClarityApproved':True,'allContinuousFramesApproved':False,'currentFinalCuePixelsApproved':False,'publicRightsApproved':False}
    p=OUT/'scene08-selected-source-direct-review-v1.json';assert not p.exists();p.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p=OUT/'remaining-editorial-annotation-preparation-v1.json';p.write_text(json.dumps({'preparedAt':datetime.now(timezone.utc).isoformat(),'jobs':all_results,'allMovingPixelsApproved':False,'wholeVideoApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preparedScenes':6,'samples':sum(len(j['samples']) for j in all_results),'boards':sum(len(j['boards']) for j in all_results),'allMovingApproved':False}),flush=True)

if __name__=='__main__':main()
