"""Original sand teaching diagrams, supplementary to actual four-second shots."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,random
from PIL import Image
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('ot12_diagrams_v2',HERE/'tech-diagrams-v2.py');v2=importlib.util.module_from_spec(s);s.loader.exec_module(v2)
base,lines,arrow,dot,C=v2.base,v2.lines,v2.arrow,v2.dot,v2.C
def sand_mips(seconds):
    im,d=base('작은 무늬에서도 방향 차이를 남깁니다','Normal Distribution (방향 분포) · 해설용 도식')
    angles=[-55,40,-25,55,-40,15,50,-30,30]
    for col,(title,values)in enumerate([('가까운 무늬',angles),('평균으로 약해진 차이',[5]*9),('결을 남기는 분포',angles[::-1])]):
        cx=165+col*327;d.rectangle((cx-145,280,cx+145,725),fill=C['panel']);lines(d,title,(cx,330),29,'title')
        for i,a in enumerate(values):
            x=cx+(i%3-1)*85;y=460+(i//3)*90;r=math.radians(a);arrow(d,(x,y),(x+45*math.sin(r),y-45*math.cos(r)),C['relation'],4)
    lines(d,'멀리서 쓰는 작은 텍스처 단계도 따로 다듬습니다.',(492,840),33,'relation');lines(d,'화살표와 분포는 설명용 예시 · 원래 텍스처 값 아님',(492,938),28,'muted')
    return im,dict(kind='authored direction-distribution illustration',originalNormalMapData=False,directionAngles=angles)
def sand_glints(seconds):
    im,d=base('반짝임을 정하는 관계를 고릅니다','Light / View / Surface · 해설용 도식');centers=[(260,650),(724,650)]
    for i,(x,y)in enumerate(centers):
        d.line((x-160,y+35,x+160,y+35),fill=C['title'],width=8);arrow(d,(x,y),(x,y-210),C['relation']);arrow(d,(x,y),(x+145,y-135),C['changed']);lines(d,'표면',(x-90,y+94),31,'title');lines(d,'시선',(x+116,y-177),31,'changed')
        if i==0:lines(d,'중간 방향',(x-65,y-235),26,'relation');arrow(d,(x,y),(x-145,y-135),C['ink']);d.line((x-70,y-150,x+70,y-150),fill=C['muted'],width=4);lines(d,'빛',(x-120,y-180),31);lines(d,'빛·시선의 중간 방향',(x,310),30,'title')
        else:lines(d,'표면 방향',(x-55,y-235),26,'relation');lines(d,'표면·시선의 관계',(x,310),30,'title')
    lines(d,'저니는 시선에 따라 드러나는 작은 빛을 조절',(492,837),33,'relation');lines(d,'발표의 표현 방법 · 정확한 물리 법칙의 증명 아님',(492,938),29,'muted')
    return im,dict(kind='authored explanatory relationship diagram',physicalOpticsProof=False,originalJourneyShaderExecuted=False)
def sand_mask(seconds):
    im,d=base('비스듬한 가장자리는 따로 다룹니다','Mask (적용 영역 조절) · 해설용 도식');rng=random.Random(7123);pts=[(rng.uniform(100,880),rng.uniform(390,680))for i in range(95)]
    polygon=[(60,700),(220,360),(700,440),(930,700)];d.polygon(polygon,fill='#765134');mask=Image.new('L',(984,984));v2.v1.ImageDraw.Draw(mask).polygon(polygon,fill=255);pts=[(x,y)for x,y in pts if mask.getpixel((round(x),round(y)))]
    for x,y in pts:
        masked=(x<300 and y<560)
        if masked:d.ellipse((x-18,y-4,x+18,y+4),outline=C['problem'],width=3)
        else:d.ellipse((x-3,y-3,x+3,y+3),fill=C['title'])
    d.line((170,420,300,330,450,365),fill=C['relation'],width=6);arrow(d,(580,260),(310,440),C['relation']);lines(d,'길게 번지는 구간에서 적용을 줄임',(492,820),35,'relation');lines(d,'도식의 점·경계는 설명용 · 원래 게임의 마스크 값 아님',(492,938),28,'muted')
    return im,dict(kind='authored grazing-region illustration',illustrativePoints=len(pts),originalMaskMeasured=False)
def sand_layers(seconds):
    im,d=base('세 가지 크기의 빛이 함께 작동합니다','Layered Sand (모래의 빛 표현) · 해설용 도식')
    for i,(title,detail)in enumerate([('거친 결','작은 단계에서도 방향 차이'),('작은 반짝임','시선 관계와 적용 영역'),('넓은 반사광','사구의 큰 형태')]):
        y=305+i*200;d.rectangle((150,y-63,834,y+75),fill=C['panel'],outline=C['relation'],width=3);lines(d,title,(492,y-20),40,'title');lines(d,detail,(492,y+40),31,'relation')
        if i<2:arrow(d,(492,y+90),(492,y+125),C['relation'])
    lines(d,'입자 수뿐 아니라, 빛을 나누는 방법이 중요합니다.',(492,936),32)
    return im,dict(kind='authored summary of published sand shading components',exactPhysicalGrainCount=False)
DIAGRAMS=dict(v2.DIAGRAMS,**{'sand-mips':sand_mips,'sand-glints':sand_glints,'sand-mask':sand_mask,'sand-layers':sand_layers})
def render(key,seconds):
    im,e=DIAGRAMS[key](seconds);return im,dict(**e,diagramKey=key,localModelSeconds=seconds,notSpeechTimestamp=True,finalFilm=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=Path,required=True);a=p.parse_args();a.samples.mkdir(parents=True,exist_ok=False);rows=[]
    for key in ['sand-mips','sand-glints','sand-mask','sand-layers']:
        im,e=render(key,3.5);path=a.samples/(key+'.png');im.save(path);im.resize((375,375),Image.Resampling.LANCZOS).save(a.samples/(key+'-375.png'));rows.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),evidence=e))
    (a.samples/'samples.json').write_text(json.dumps(dict(sourceOnlyExamples=True,frames=rows,finalFilm=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(a.samples)
if __name__=='__main__':main()
