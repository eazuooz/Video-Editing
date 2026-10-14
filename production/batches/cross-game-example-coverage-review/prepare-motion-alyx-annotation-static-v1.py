"""Six already-reviewed source pixels, with conservative observed screen anchors."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/alyx-annotation-static-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'alyx-annotation-observation-plan-v1.json')
assert not OUT.exists();OUT.mkdir()
anchors={3039:('destinationFeet',[840,650]),3051:('destinationFeet',[820,550]),3063:('destinationFeet',[780,520]),
    3069:('arrivalWall',[568,303]),3075:('arrivalWall',[531,375]),3081:('arrivalWall',[508,405])}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36);cf=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',28)
rows=[]
for row in plan['samples']:
    src=ROOT/row['path'];assert sha(src)==row['sha256']
    scaled=Image.open(src).convert('RGB').resize((1920,1080));im=Image.new('RGB',(1920,1080));im.paste(scaled.crop((0,120,1920,1080)),(0,0))
    im.paste(scaled.crop((0,960,1920,1080)).filter(ImageFilter.GaussianBlur(18)),(0,960))
    role,p=anchors[row['nativeFrame']];point=[round(p[0]*1.5),round(p[1]*1.5-120)];d=ImageDraw.Draw(im)
    if role=='destinationFeet':
        d.rectangle((80,110,660,175),fill='white',outline='#c73131',width=3);d.text((100,121),'이동 전: 노란 목적지',font=font,fill='#a31818')
        d.line([(660,175),(710,230),tuple(point)],fill='#df3434',width=5);d.ellipse((point[0]-42,point[1]-30,point[0]+42,point[1]+30),outline='#df3434',width=5)
    else:
        d.rectangle((1150,110,1780,175),fill='white',outline='#087ca6',width=3);d.text((1170,121),'도착 후: 문 옆의 벽',font=font,fill='#066685')
        d.line([(1160,175),(1090,230),tuple(point)],fill='#1bb3d0',width=5)
        d.line([(point[0]-18,point[1]+18),(point[0]-18,point[1]-18),(point[0]+18,point[1]-18)],fill='#1bb3d0',width=5)
    d.rectangle((1280,30,1870,73),fill='white');d.text((1290,34),'Half-Life: Alyx — Valve',font=small,fill='black')
    d.rectangle((134,918,1814,1046),fill='#174735');d.rectangle((120,906,1800,1034),fill='white',outline='black',width=2)
    t='목적지를 고른 뒤, 문과 벽을 보고 도착한 방향을 다시 읽습니다.';box=d.textbbox((0,0),t,font=cf);assert box[2]-box[0]<1660
    d.text(((1920-(box[2]-box[0]))/2,942),t,font=cf,fill='black')
    dest=OUT/f"frame-{row['nativeFrame']}.png";im.save(dest)
    rows.append({**row,'role':role,'observedSampleScreenPoint':p,'native1920ScreenPoint':[x*1.5 for x in p],
        'reframedScreenPoint':point,'staticPath':dest.relative_to(ROOT).as_posix(),'staticSha256':sha(dest)})
out={**plan,'preparedAt':datetime.now(timezone.utc).isoformat(),'priorPlanSha256':sha(R/'alyx-annotation-observation-plan-v1.json'),
    'samples':rows,'coordinatesPrepared':True,'coordinateSystem':'Observed1280x720 sample -> native1920x1080 = *1.5; reframed y subtract120',
    'destinationMarkerVisibleNativeRange':[3039,3063],'rangeEndExclusive':True,
    'unknownTransitionBracketAnnotationHidden':[3063,3069],
    'arrivalWallMarkerVisibleNativeRange':[3069,3082],'arrivalRangeEndExclusive':True,
    'interpolation':'Only within separate same-viewpoint reviewed ranges; hide outside and throughout unknown jump bracket. Screen observation only.',
    'allStaticPixelsDirectlyReviewed':False,'sourceAudioAdopted':False}
(R/'alyx-annotation-observation-plan-v2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Six static source mocks prepared; no media/TTS/extraction/final approval.')
