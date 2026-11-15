"""Original source-order teaching diagrams. Pure CPU, no import-time rendering.

Authored relationships and exact diagram geometry are distinguished from game
telemetry. Times are local model times, never guessed speech/caption anchors.
"""
from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
FONT='C:/Windows/Fonts/NotoSansKR-VF.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf'
C=dict(ink='#f5f5f5',muted='#839398',relation='#73c7c2',changed='#f39a4b',problem='#ef8585',title='#e8cf83',panel='#122124')
def font(size=40,bold=False):
    f=ImageFont.truetype(BOLD if bold else FONT,size)
    if not bold and hasattr(f,'set_variation_by_name'):f.set_variation_by_name('Medium')
    return f
def arrow(d,a,b,color,width=7):
    d.line((*a,*b),fill=color,width=width);dx=b[0]-a[0];dy=b[1]-a[1];length=max(.001,math.hypot(dx,dy));x,y=dx/length,dy/length
    d.polygon([b,(b[0]-24*x+12*y,b[1]-24*y-12*x),(b[0]-24*x-12*y,b[1]-24*y+12*x)],fill=color)
def lines(d,text,xy,size=40,color='ink',anchor='mm'):
    f=font(size);chunks=text.split('\n');height=size*1.4
    for n,t in enumerate(chunks):
        assert f.getlength(t)<=950,'Shorten diagram label, not the spoken lesson: '+t
        d.text((xy[0],xy[1]+(n-(len(chunks)-1)/2)*height),t,font=f,fill=C.get(color,color),anchor=anchor)
def base(title,term):
    im=Image.new('RGB',(984,984),'black');d=ImageDraw.Draw(im);lines(d,title,(492,64),46,'title');lines(d,term,(492,137),30,'relation');return im,d
def dot(d,p,color='relation',radius=12):d.ellipse((p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius),fill=C[color])
def rect_hit(a,b,rect):
    # Slab test on this diagram's actual finite ray segment.
    lo,hi=0.,1.
    for start,delta,minimum,maximum in [(a[0],b[0]-a[0],rect[0],rect[2]),(a[1],b[1]-a[1],rect[1],rect[3])]:
        if abs(delta)<1e-10:
            if not minimum<=start<=maximum:return None
        else:
            u,v=(minimum-start)/delta,(maximum-start)/delta;lo=max(lo,min(u,v));hi=min(hi,max(u,v))
            if lo>hi:return None
    return (a[0]+(b[0]-a[0])*lo,a[1]+(b[1]-a[1])*lo)
def spider_rays(seconds):
    im,d=base('검사 선 사이의 작은 구조물','Raycast (레이캐스트) · 해설용 도식');origin=(150,800);pillar=(480,230,510,300);d.rectangle(pillar,fill=C['changed']);results=[]
    for degrees in [-80,-65,-50,-35,-20,-5]:
        a=math.radians(degrees);length=min(850,600/max(.0001,-math.sin(a)),770/max(.0001,math.cos(a)));end=(origin[0]+length*math.cos(a),origin[1]+length*math.sin(a));hit=rect_hit(origin,end,pillar);results.append(dict(degrees=degrees,hit=hit,end=end));arrow(d,origin,hit or end,C['relation'],5)
    assert not any(x['hit'] for x in results)
    dot(d,origin,'title',22);lines(d,'검사 시작점',(190,870),34,'title');arrow(d,(675,280),(526,270),C['changed']);lines(d,'검사 선 사이에 남는 구조물',(638,374),31,'changed');lines(d,'선을 늘려도\n후보를 다루는 방식은 필요합니다.',(492,938),36)
    return im,dict(kind='authored finite-ray gap example',origin=origin,structure=pillar,rays=results,originalGameRayCount=False)
def spider_volume(seconds):
    im,d=base('건물 면에서 후보를 고릅니다','Markup Volume (표시용 영역) · 해설용 도식');building=(420,240,840,720);reference=(300,340);candidate=(420,340);d.rectangle(building,fill=C['panel'],outline=C['relation'],width=7)
    for x in range(450,830,70):d.line((x,260,x,700),fill='#254044',width=2)
    dot(d,reference,'title',18);dot(d,candidate,'relation',18);arrow(d,reference,candidate,C['title']);arrow(d,(180,740),(180,500),C['changed']);lines(d,'원하는 진행 방향',(200,808),31,'changed');lines(d,'기준점',(279,281),34,'title');lines(d,'면 위의 후보',(570,340),34,'relation');lines(d,'단순한 영역 → 실제 지형 확인',(492,917),37)
    assert candidate[0]==building[0] and building[1]<=candidate[1]<=building[3]
    return im,dict(kind='authored box-face candidate illustration',building=building,reference=reference,candidate=candidate,houdiniOrOriginalGameDataExecuted=False)
def spider_scores(seconds):
    im,d=base('좋은 연결점을 고르는 조건','Attachment (부착점) · 해설용 도식');rows=[('방향','가려는 쪽을 돕는가?'),('거리','줄이 어울리는 길이인가?'),('기울기','너무 깊이 떨어지지 않는가?')]
    for i,(title,description) in enumerate(rows):
        y=300+i*170;d.rectangle((70,y-55,915,y+70),fill=C['panel']);dot(d,(110,y+8),'relation',12);lines(d,title,(180,y+8),35,'title');lines(d,description,(590,y+8),34)
    arrow(d,(490,760),(490,825),C['relation']);lines(d,'조건을 비교해 후보 선택',(492,886),40,'relation')
    return im,dict(kind='documented criteria explained without invented numeric weights',criteria=[x[0]for x in rows],originalGameScoresMeasured=False)
def history_nodes(frame,count=8):
    assert 0<=frame<720
    states=[]
    for n in range(frame+1):
        root=(492+125*math.sin(n/60*1.1),780);current=[root]
        for k in range(1,count):
            old_parent=states[-1][k-1] if states else (492,780-(k-1)*65)
            current.append((old_parent[0]+8*math.sin(n/60*1.8-k*.25),old_parent[1]-65))
        states.append(current)
    return states
def returnal_delay(seconds):
    frame=min(719,max(1,round(seconds*60)));states=history_nodes(frame);now,previous=states[-1],states[-2];im,d=base('자식은 부모의 지난 정보를 읽습니다','Node Particle (노드 입자) · 해설용 도식')
    # Two data columns make a one-frame dependency readable without magnifying
    # the tiny actual motion delta or presenting it as slow game playback.
    for x,title in [(260,'이전 프레임'),(724,'현재 프레임')]:
        d.rectangle((x-170,260,x+170,830),fill=C['panel']);lines(d,title,(x,305),36,'title')
        for k,y in enumerate([735,575,415]):
            dot(d,(x,y),'changed'if k==0 else'relation',22);lines(d,'부모'if k==0 else'자식 '+str(k),(x,y+57),31,'changed'if k==0 else'ink')
    arrow(d,(296,735),(685,575),C['relation'],7);arrow(d,(296,575),(685,415),C['relation'],7)
    lines(d,'읽기',(500,640),32,'relation');lines(d,'화살표는 정보의 전달 · 공간 이동 경로가 아닙니다.',(492,912),30,'muted')
    for k in range(1,8):assert abs(now[k][1]-(previous[k-1][1]-65))<1e-8
    return im,dict(kind='authored previous-frame parent dependency',fps=60,frame=frame,currentNodes=now,previousNodes=previous,rule='child[k,t] reads parent[k-1,t-1]; authored offsets',layout='two data columns, not spatial trajectories',originalReturnalGpuOrAi=False)
def returnal_surface(seconds):
    im,d=base('점의 이동과 표면 만들기는 다릅니다','Curve & Tube (곡선과 원통형 표면) · 해설용 도식');points=history_nodes(min(719,max(0,round(seconds*60))))[-1]
    left=[(x-235,y)for x,y in points];right=[(x+235,y)for x,y in points]
    for a,b in zip(left,left[1:]):d.line((*a,*b),fill=C['relation'],width=8)
    for p in left:dot(d,p,'title',11)
    for width,color in [(72,'#27464a'),(56,'#477a7b'),(31,C['relation'])]:
        d.line(right,fill=color,width=width,joint='curve')
        for p in [right[0],right[-1]]:d.ellipse((p[0]-width/2,p[1]-width/2,p[0]+width/2,p[1]+width/2),fill=color)
    for p in right:d.ellipse((p[0]-35,p[1]-10,p[0]+35,p[1]+10),outline='#a2ded9',width=2)
    lines(d,'움직이는 점',(255,845),34,'title');lines(d,'둘레에 만든 표면',(725,845),34,'relation');lines(d,'단면과 빛의 방향도 함께 다듬습니다.',(492,930),34)
    return im,dict(kind='own2D projected tube explanation',nodePositions=points,originalShaderOrGeometry=False)
def ratchet_pipeline(seconds):
    im,d=base('읽은 자료도 바로 쓸 수는 없습니다','Decompression (압축 해제) · 해설용 도식');stages=[('저장 장치','압축된 자료'),('읽기','메모리로 이동'),('압축 해제','쓸 수 있는 자료')];active=0 if seconds<1.4 else 1 if seconds<2.5 else 2
    for i,(name,detail)in enumerate(stages):
        y=285+i*215;d.rectangle((160,y-65,824,y+80),fill=C['panel'],outline=C['relation'] if i==active else '#395357',width=6 if i==active else 2);lines(d,name,(492,y-18),43,'title' if i==active else'ink');lines(d,detail,(492,y+45),31,'relation')
        if i<2:arrow(d,(492,y+95),(492,y+135),C['relation'])
    lines(d,'표시 시간은 해설용 예시 · 실제 PC 측정 아님',(492,932),29,'muted')
    return im,dict(kind='authored storage pipeline',localTime=seconds,stage=active,illustrativeStageDurations=[1.4,1.1],originalBenchmark=False)
def control_hierarchy(seconds):
    im,d=base('조각과 연결을 미리 준비합니다','Fracture Hierarchy (파괴 계층) · 해설용 도식');d.rectangle((330,230,654,355),fill=C['panel'],outline=C['title'],width=5);lines(d,'큰 물체',(492,291),42,'title');children=[(230,515),(492,515),(754,515)]
    for i,p in enumerate(children):
        arrow(d,(492,370),(p[0],p[1]-75),C['relation']);d.rectangle((p[0]-100,p[1]-62,p[0]+100,p[1]+62),fill=C['panel'],outline=C['relation'],width=4);lines(d,'큰 조각',(p[0],p[1]),33)
        for j in range(3):
            q=(p[0]+(j-1)*60,760);arrow(d,(p[0],p[1]+75),q,C['muted'],4);dot(d,q,'changed',12)
    lines(d,'더 작은 파편·입자',(492,830),35,'changed');lines(d,'재질에 맞는 조각과 결합 강도를 준비',(492,934),35)
    return im,dict(kind='authored preparation hierarchy',levels=['whole object','fragments','small fragments and particles'],notAllParticlesPhysicsBodies=True,originalHoudiniOrPhysxExecuted=False)
def botw_rules(seconds):
    im,d=base('움직임과 상태 변화를 나눕니다','Chemistry Engine (화학 엔진) · 해설용 도식');rows=[('불 원소','나무 물질','불붙은 상태','relation'),('물 원소','불 원소','불 상태 변화','relation'),('물질','물질','이 규칙의 직접 상태 변화 없음','muted')]
    for i,(a,b,result,color) in enumerate(rows):
        y=300+i*220;lines(d,a,(190,y),33,'changed'if i<2 else'muted');arrow(d,(290,y),(400,y),C[color],6);lines(d,b,(540,y),33,'title');lines(d,result,(492,y+80),32,color)
    lines(d,'물리적인 충돌까지 없다는 뜻은 아닙니다.',(492,944),32)
    return im,dict(kind='authored diagram of published3 chemistry rules',sourceRules=[1,2,3],physicalCollisionNotDenied=True,realChemistrySimulation=False)
DIAGRAMS={'spider-rays':spider_rays,'spider-volume':spider_volume,'spider-criteria':spider_scores,'returnal-delay':returnal_delay,'returnal-surface':returnal_surface,'ratchet-read-decompress':ratchet_pipeline,'control-hierarchy':control_hierarchy,'botw-rules':botw_rules}
def render(key,seconds):
    im,evidence=DIAGRAMS[key](seconds);return im,dict(**evidence,diagramKey=key,localModelSeconds=seconds,notSpeechTimestamp=True,finalFilm=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=Path,required=True);a=p.parse_args();a.samples.mkdir(parents=True,exist_ok=False);rows=[]
    for key in DIAGRAMS:
        im,e=render(key,3.5);target=a.samples/(key+'.png');im.save(target);im.resize((375,375),Image.Resampling.LANCZOS).save(a.samples/(key+'-375.png'));rows.append(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),evidence=e))
    (a.samples/'samples.json').write_text(json.dumps(dict(designSamplesOnly=True,finalFilm=False,records=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(a.samples)
if __name__=='__main__':main()
