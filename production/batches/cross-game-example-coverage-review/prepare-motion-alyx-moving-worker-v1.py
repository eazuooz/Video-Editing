"""Reuse the reviewed encoding contract for a new bounded Alyx pilot."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
src=B/'render-motion-portal-annotation-pilot-v2.py';dst=B/'render-motion-alyx-annotation-pilot-v1.py';assert not dst.exists()
code=src.read_text('utf-8-sig').replace('silent3s','silent0.7167s').replace('portal-annotation-pilot-v2','alyx-annotation-pilot-v1').replace('portal-annotation-observation-plan-v2','alyx-annotation-observation-plan-v3').replace('portal-annotation-pilot-execution-v2','alyx-annotation-pilot-execution-v1').replace('portal-cube-camera.captioned-pilot','alyx-arrival.captioned-pilot')
code=code.replace("for x in plan['observations']:","plan['sourceFirstFrame']=3039;plan['sourceEndExclusiveFrame']=3082\nfor x in plan['samples']:")
code=code.replace("sha(ROOT/x['sourceSample'])==x['sourceSampleSha256']","sha(ROOT/x['path'])==x['sha256']")
a=code.index('def anchor(frame,key):');b=code.index('output=OUT/',a)
code=code[:a]+'''def anchor(frame,role):
    rows=[r for r in plan['samples'] if r['role']==role];a,b=rows[-2:]
    for left,right in zip(rows,rows[1:]):
        if left['nativeFrame']<=frame<=right['nativeFrame']:a,b=left,right;break
    u=max(0,min(1,(frame-a['nativeFrame'])/(b['nativeFrame']-a['nativeFrame'])))
    return [round(a['reframedScreenPoint'][i]+u*(b['reframedScreenPoint'][i]-a['reframedScreenPoint'][i])) for i in [0,1]]
'''+code[b:]
code=code.replace("'-frames:v','180'","'-frames:v','43'").replace('range(180)','range(43)').replace("=='180'","=='43'").replace('frames=180,seconds=3','frames=43,seconds=43/60')
code=code.replace('crop((0,120,1920,1080))','crop((0,180,1920,1080))').replace('crop((0,960,1920,1080))','crop((0,900,1920,1080))').replace('(0,960))','(0,900))')
start=code.index("            d=ImageDraw.Draw(im);native=");end=code.index('            d.rectangle((134,918',start)
code=code[:start]+'''            d=ImageDraw.Draw(im);native=plan['sourceFirstFrame']+round(frame/60*60000/1001)
            if 3039<=native<3063:
                point=anchor(native,'destinationFeet')
                d.rectangle((80,110,660,175),fill='white',outline='#c73131',width=3);d.text((100,121),'이동 전: 노란 목적지',font=font,fill='#a31818')
                d.line([(660,175),(710,230),tuple(point)],fill='#df3434',width=5)
                d.ellipse((point[0]-115,point[1]-55,point[0]+115,point[1]+55),outline='#df3434',width=5)
            elif 3069<=native<3082:
                point=anchor(native,'arrivalWall')
                d.rectangle((1150,110,1780,175),fill='white',outline='#087ca6',width=3);d.text((1170,121),'도착 후: 문 옆의 벽',font=font,fill='#066685')
                d.line([(1160,175),(1090,230),tuple(point)],fill='#1bb3d0',width=5)
                d.line([(point[0]-18,point[1]+18),(point[0]-18,point[1]-18),(point[0]+18,point[1]-18)],fill='#1bb3d0',width=5)
            d.rectangle((1280,30,1870,73),fill='white');d.text((1290,34),'Half-Life: Alyx — Valve',font=small,fill='black')
'''+code[end:]
code=code.replace('큐브는 화면 가운데를 따라가고, 방의 단서는 위치가 바뀝니다.','목적지를 고른 뒤, 문과 벽을 보고 도착한 방향을 다시 읽습니다.')
code=code.replace('frames=[0,1,15,30,45,60,75,90,105,120,150,179]','frames=[0,1,6,12,18,23,24,29,30,36,42]').replace('f/60*30000/1001','round(f/60*60000/1001)').replace('len(rows)==12','len(rows)==11').replace('180f3s pilot/12samples','43f0.7167s pilot/11samples')
compile(code,str(dst),'exec');dst.write_text(code,'utf-8')
print('SingleCPU2/GPU0 43-frame pilot prepared; hides uncertain native3063..3069 bracket. No rendering yet.')
