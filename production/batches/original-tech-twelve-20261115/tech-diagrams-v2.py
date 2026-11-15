"""Additional original diagrams for the exact documented processing steps."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
from PIL import Image
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('ot12_original_diagrams_v1',HERE/'tech-diagrams-v1.py');v1=importlib.util.module_from_spec(s);s.loader.exec_module(v1)
base,lines,arrow,dot,C=v1.base,v1.lines,v1.arrow,v1.dot,v1.C
def temporal_reproject(seconds):
    im,d=base('같은 점의 지난 위치를 찾습니다','Reprojection (재투영) · 해설용 도식')
    for x,label in [(260,'지난 화면'),(724,'현재 화면')]:
        d.rectangle((x-170,270,x+170,740),fill=C['panel'],outline=C['muted'],width=3);lines(d,label,(x,315),36,'title')
        for a in range(-120,150,60):d.line((x+a,370,x+a,700),fill='#254044',width=2)
        for a in range(370,720,60):d.line((x-130,a,x+130,a),fill='#254044',width=2)
    before=(200,520);now=(780,580);dot(d,before,'title',23);dot(d,now,'relation',23);arrow(d,(750,570),(230,525),C['relation'],7);lines(d,'깊이·움직임 정보로 대응 찾기',(492,815),37,'relation');lines(d,'화살표는 좌표 대응 · 원래 게임의 이동량 측정 아님',(492,930),29,'muted')
    return im,dict(kind='authored current-to-history coordinate correspondence',current=now,previous=before,originalGameVelocityMeasured=False)
def temporal_clip(seconds):
    im,d=base('지난 색을 현재 주변 범위로 제한합니다','Neighborhood Clipping (주변 색 범위 제한) · 해설용 도식')
    colors=['#416467','#527579','#42686b','#597f81','#618a8b','#4f7277','#466c70','#719596','#5e8689']
    for i,color in enumerate(colors):
        x=150+i%3*90;y=300+i//3*90;d.rectangle((x,y,x+82,y+82),fill=color)
    lines(d,'현재 주변 픽셀',(280,650),34,'relation');d.rectangle((530,320,820,425),fill='#db6861');lines(d,'어울리지 않는 지난 색',(690,480),29,'problem');arrow(d,(670,520),(670,650),C['relation']);d.rectangle((530,690,820,795),fill='#719596');lines(d,'현재 범위 안으로',(690,855),32,'relation');lines(d,'도식의 색은 예시 · 정확한 구현은 별도 실제 AA 비교',(492,937),28,'muted')
    values=[int(c[1:3],16)for c in colors];return im,dict(kind='authored one-channel range example',currentRedRange=[min(values),max(values)],pastRed=219,limitedRed=min(max(219,min(values)),max(values)),notCompleteOriginal3DColorClippingImplementation=True)
def temporal_history_blur(seconds):
    im,d=base('재사용할 기록과 보완 흐림을 구별합니다','History / Motion Blur · 해설용 도식')
    boxes=[((250,285),'현재 화면'),((250,490),'과거 정보 다듬기'),((250,700),'섞은 기록 저장'),((735,700),'보완 모션 블러')]
    for (x,y),text in boxes:
        d.rectangle((x-180,y-60,x+180,y+60),fill=C['panel'],outline=C['relation'],width=4);lines(d,text,(x,y),32,'title')
    arrow(d,(250,355),(250,420),C['relation']);arrow(d,(250,560),(250,630),C['relation']);arrow(d,(445,700),(535,700),C['changed']);d.line((60,700,35,700,35,490,60,490),fill=C['relation'],width=6);lines(d,'다음 장에 재사용',(250,828),32,'relation');lines(d,'출력 화면 보완',(735,828),32,'changed');lines(d,'보완 흐림을 과거 기록에 계속 쌓지 않습니다.',(492,936),33)
    return im,dict(kind='authored history/output branch explanation',historyIncludesAccumulatedMotionBlur=False,originalShaderBranchObservedInPrimarySource=True,diagramNotGpuExecution=True)
def control_surface_hole(seconds):
    im,d=base('표면의 흔적과 구멍은 다릅니다','Decal / Geometry · 해설용 도식')
    for x in [260,724]:d.rectangle((x-175,300,x+175,750),fill='#8c7253',outline=C['title'],width=4)
    d.ellipse((190,430,330,570),fill='#252323');d.ellipse((654,430,794,570),fill='black');d.line((724,432,724,568),fill=C['relation'],width=5)
    lines(d,'표면에 그린 자국',(260,815),33,'title');lines(d,'안쪽이 보이는 구멍',(724,815),33,'relation');lines(d,'비슷한 화면이라도 만드는 작업은 구별합니다.',(492,936),32)
    return im,dict(kind='authored surface-mark versus open-geometry explanation',originalControlDestructionMeasured=False)
DIAGRAMS=dict(v1.DIAGRAMS,**{'temporal-reproject':temporal_reproject,'temporal-clip':temporal_clip,'temporal-history-blur':temporal_history_blur,'control-surface-hole':control_surface_hole})
def render(key,seconds):
    im,e=DIAGRAMS[key](seconds);return im,dict(**e,diagramKey=key,localModelSeconds=seconds,notSpeechTimestamp=True,finalFilm=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=Path,required=True);a=p.parse_args();a.samples.mkdir(parents=True,exist_ok=False);rows=[]
    for key in ['temporal-reproject','temporal-clip','temporal-history-blur','control-surface-hole']:
        im,e=render(key,3.5);path=a.samples/(key+'.png');im.save(path);im.resize((375,375),Image.Resampling.LANCZOS).save(a.samples/(key+'-375.png'));rows.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),evidence=e))
    (a.samples/'samples.json').write_text(json.dumps(dict(sourceOnlyExamples=True,frames=rows,finalFilm=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(a.samples)
if __name__=='__main__':main()
