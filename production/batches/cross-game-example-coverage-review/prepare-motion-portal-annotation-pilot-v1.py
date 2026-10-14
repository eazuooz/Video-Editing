"""Four manual screen observations; static clearance checks are not moving approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/portal-annotation-static-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not OUT.exists();OUT.mkdir()
e=read(R/'native-preflight-execution-v1.json');w=next(x for x in e['windows'] if x['name']=='portal-aim')
# Screen-space locations manually read in four original 1280x720 samples.
# The red target is a visible point on the upper cube face, not its physical centroid.
coords=[(1109,[625,350],[370,425]),(1139,[635,385],[850,320]),
        (1169,[635,375],[985,225]),(1199,[635,377],[1030,235])]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',28)
captionfont=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44)
rows=[]
for frame,cube,wall in coords:
    x=next(x for x in w['samples'] if x['nativeFrame']==frame)
    assert sha(ROOT/x['path'])==x['sha256']
    with Image.open(ROOT/x['path']) as original:scaled=original.resize((1920,1080))
    im=Image.new('RGB',(1920,1080));im.paste(scaled.crop((0,120,1920,1080)),(0,0))
    im.paste(scaled.crop((0,960,1920,1080)).filter(ImageFilter.GaussianBlur(18)),(0,960))
    d=ImageDraw.Draw(im)
    def mapxy(p):return [round(p[0]*1.5),round(p[1]*1.5-120)]
    c=mapxy(cube);b=mapxy(wall)
    d.rounded_rectangle((1120,100,1660,157),radius=0,fill='white',outline='#c73131',width=3)
    d.text((1140,108),'조작 대상: 큐브',font=font,fill='#a31818')
    d.line([(1130,157),(1080,205),tuple(c)],fill='#df3434',width=5)
    d.line([(c[0]-22,c[1]-12),(c[0]-22,c[1]+12)],fill='#df3434',width=5)
    d.line([(c[0]-22,c[1]-12),(c[0]+22,c[1]-12)],fill='#df3434',width=5)
    d.rectangle((80,175,580,232),fill='white',outline='#087ca6',width=3)
    d.text((100,183),'방의 단서: 벽',font=font,fill='#066685')
    d.line([(580,232),(610,270),tuple(b)],fill='#1bb3d0',width=5)
    d.ellipse((b[0]-11,b[1]-11,b[0]+11,b[1]+11),outline='#1bb3d0',width=4)
    d.rectangle((1280,30,1870,73),fill='#ffffff')
    d.text((1290,34),'Portal 2 — Valve',font=small,fill='black')
    d.rectangle((134,918,1814,1046),fill='#174735')
    d.rectangle((120,906,1800,1034),fill='white',outline='black',width=2)
    text='큐브는 화면 가운데를 따라가고, 방의 단서는 위치가 바뀝니다.'
    box=d.textbbox((0,0),text,font=captionfont)
    d.text(((1920-(box[2]-box[0]))/2,942),text,font=captionfont,fill='black')
    out=OUT/f'frame-{frame}.png';im.save(out)
    rows.append(dict(nativeFrame=frame,pts=x['pts'],timeBase=x['timeBase'],sourceSample=x['path'],sourceSampleSha256=x['sha256'],
      cubeUpperVisiblePoint=cube,wallVisiblePoint=wall,coordinateSystem='native 1280x720 observed screen pixels',
      reframedCubePoint=c,reframedWallPoint=b,staticPath=str(out.relative_to(ROOT)),staticSha256=sha(out),
      endpointIsExclusive=frame==1199))
v=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),sourceKey='portal2',
 sourcePath='shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',
 sourceSha256='0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb',
 sourceFirstFrame=1109,sourceEndExclusiveFrame=1199,nativePtsStep=1001,nativeTimeBase='1/30000',
 observations=rows,redRole='Visible upper cube face: task object',blueRole='Visible room wall: orientation clue',
 framing=dict(scale=1.5,shiftY=-120,bottomSameFrameBlurPixels=120,captionCenter=[960,970]),
 interpolation='Prepared linear interpolation in native PTS; must be compared with encoded moving pixels before adoption.',
 physicalCentroidClaim=False,engineWorldAxisClaim=False,comfortOutcomeClaim=False,
 directStaticClearanceReview=False,movingAnnotationApproved=False,narrationTimed=False,finalCueApproval=False,
 sourceAudioAdopted=False,gitImagesAdded=0)
(R/'portal-annotation-observation-plan-v1.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Four manually observed screen anchors/static clearance candidates prepared; no moving/final approval.')
