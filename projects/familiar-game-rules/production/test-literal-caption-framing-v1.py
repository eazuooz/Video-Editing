"""Six targeted one-line/crop comparisons from existing native pixels; no final approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert read(BASE/'guide-joins-asr-execution-v1.json')['actualExitObserved']
source=read(PROOF/'source-framing-execution-v1.json')
out=ROOT/'shared/output/familiar-game-rules/research/literal-framing-candidates-v1';assert not out.exists();(out/'boards').mkdir(parents=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
tests=[('additional-16','시장에서 총을 쏘는 컷과'),('additional-22','기찻길과 시장,'),
    ('action-13','이동하고 뛰며,'),('action-23','이동, 점프, 도구 사용,'),
    ('action-35','여러 층을 내려가며'),('hype-05','총은 아래를 향합니다.')]
tiles=[]
for id,text in tests:
    clip=next(x for x in source['clips'] if x['id']==id)
    width=round(font.getlength(text)+44);height=84
    for mode in ['native-full-frame','bottom150-candidate']:
        crop=[0,0,1920,1080] if mode=='native-full-frame' else [320,360,1280,720]
        for sample in clip['samples']:
            path=ROOT/sample['nativePath'];assert sha(path)==sample['nativeSha256']
            with Image.open(path) as im:
                assert im.size==(1920,1080)
                x,y,w,h=crop;im=im.crop((x,y,x+w,y+h)).resize((1920,1080),Image.Resampling.LANCZOS).convert('RGB')
            draw=ImageDraw.Draw(im);left=960-width/2;top=970-height/2
            draw.rectangle((left+14,top+14,left+width+14,top+height+14),fill='#073c32')
            draw.rectangle((left,top,left+width,top+height),fill='white',outline='#161b18',width=3)
            draw.text((960,top+11),text,font=font,fill='#080b09',anchor='mt')
            target=out/f'{id}-{mode}-{sample["tag"]}.jpg';im.save(target,quality=95)
            tiles.append(dict(id=id,mode=mode,text=text,sourceCrop=crop,sourceFrame=sample['sourceFrame'],tag=sample['tag'],
                sourcePixelPath=sample['nativePath'],sourcePixelSha256=sample['nativeSha256'],path=rel(target),sha256=sha(target),
                captionBox=[left,top,width,height],directlyRead=False))
boards=[]
for start in range(0,len(tiles),6):
    im=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(im)
    for i,t in enumerate(tiles[start:start+6]):
        x=i%2*960;y=i//2*570;draw.text((x+8,y+3),f'{t["id"]} {t["tag"]} {t["mode"]}',font=label,fill='black')
        with Image.open(ROOT/t['path']) as tile:im.paste(tile.resize((960,540)),(x,y+30))
    p=out/'boards'/f'{start//6+1:02d}.jpg';im.save(p,quality=95)
    boards.append(dict(path=rel(p),sha256=sha(p),tiles=tiles[start:start+6],directlyRead=False))
evidence=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),pid=os.getpid(),commandLine=[os.sys.executable,*os.sys.argv],
    cpuThreads=1,gpuJobs=0,resourceObservation=r,sourceNativeRepeated=False,newSourceExtraction=0,
    imageCount=len(tiles),boardCount=len(boards),boards=boards,captionCenter=[960,970],captionStyle='boxed-white-forest-v1',fontPx=48,
    scope='Only targeted literal text and static crop comparison candidates; no timeline cue assignment, complete motion or encoded final pixels.',
    allDirectlyRead=False,fullScreenFramingApproved=False,allFinalCaptionPixelsReviewed=False,finalTimingApproved=False,
    newGitImages=0,imagesGitPolicy='local-only')
dest=PROOF/'literal-caption-framing-candidates-v1.json';assert not dest.exists();dest.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(images=len(tiles),boards=len(boards),sourceExtractionRepeated=False,allFinalApproval=False)))
