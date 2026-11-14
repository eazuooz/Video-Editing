"""Read-only decoded-picture audit; never changes a production master or engine."""
import hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3];BATCH=HERE.parent
WORK=Path('C:/Users/1/Videos/YamyamProduction/animation-footage-audit-20261115')
DELIVERY=Path('C:/Users/1/Videos/YamyamCoding/animation-overview-v7')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for x in iter(lambda:f.read(8*1024*1024),b''):h.update(x)
    return h.hexdigest()
def run(args):
    p=subprocess.run([str(s) for s in args],capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace')[-2000:])
    return p.stdout
def frame(path,t,size=(640,360)):
    raw=run(['ffmpeg','-nostdin','-v','error','-ss',t,'-threads',2,'-i',path,'-an','-frames:v',1,
        '-vf',f'scale={size[0]}:{size[1]}:flags=lanczos','-f','rawvideo','-pix_fmt','rgb24','-'])
    return Image.frombytes('RGB',size,raw)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/NotoSansKR-VF.ttf',n)
def text(d,p,s,n=27):d.text(p,s,font=font(n),fill='#f3f5ef')

# Audition windows are local-file timestamps, not YouTube full-recording timestamps.
CASES=[
 ('A03','great',18,23,125),('A04','hades-training',39,41.9,110),
 ('A05','hifi-beat',4,9,100),('A06','mhw-hammer',3.4,8.25,120),
 ('A07','luigi-run',8,12,140),('A08','ringfit-warrior1',15,20,130),
 ('A09','cup-goopy',20.5,25,200),('A10','juri-hit-b',29,32.5,102),
 ('A11','deadcells-motion',11,15,108),('A12','acnh-catch-expression',11.25,14.25,90),
 ('A13','sf2-deejay',28.5,30.5,106),('A14','hzd-aim-move',8.5,12.5,98),
 ('A15','alyx-grip',19,26,85),('A16','mhw-longsword',14.5,18.5,92),
 ('A17','arms-helix',9,14,80),('A18','luigi-lobby',29,34.5,84)]
def source_catalog():
    a=read(BATCH/'contrast-v5/footage/game-coverage-team-a.json')
    catalog={r['key']:dict(r) for r in a['sources']}
    b=read(BATCH/'contrast-v5/footage/team-b/game-coverage.json')
    catalog.update({k:dict(v,sourceUrl=v['url']) for k,v in b['sources'].items()})
    great=ROOT/'projects/animation-breaking-down-attack-animations/production/local/grid-v1/sources'
    catalog['great']=dict(file=str(great/'great.mp4'),game='Monster Hunter Wilds',sourceUrl=read(great/'great.metadata.json')['webpage_url'])
    return catalog

def main():
    catalog=source_catalog();plan=read(BATCH/'overview-v7/plan.json');evidence=[]
    WORK.mkdir(parents=True,exist_ok=True)
    for ep,key,start,end,current in CASES:
        folder=WORK/ep;folder.mkdir(exist_ok=True)
        source=catalog[key];path=Path(source['file']);assert path.is_file(),path
        video=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',path]))['streams'][0]
        assert video['width']>=1920 and video['height']>=1080,(key,video['width'],video['height'])
        source_hash=sha(path)
        if source.get('sha256'):assert source['sha256']==source_hash,(key,'changed source')
        receipt=read(DELIVERY/ep/'delivery.json');master=next(f for f in receipt['files'] if f['kind']=='captioned.mp4')
        assert sha(master['path'])==master['sha256'],(ep,'changed master')
        canvas=Image.new('RGB',(1920,850),'#080c0a');d=ImageDraw.Draw(canvas)
        text(d,(22,8),ep+' · '+source['game']+' · 실제 영상 후보',35)
        times=[round(start+(end-start)*i/5,4) for i in range(6)]
        for i,t in enumerate(times):
            x=(i%3)*640;y=70+(i//3)*390
            pic=frame(path,t);canvas.paste(pic,(x,y));text(d,(x+15,y+358),f'local {t:.3f}s',24)
        canvas.save(folder/'source-sequence.jpg',quality=94)
        pic=frame(master['path'],current,(960,540));pic.save(folder/'current-demo.jpg',quality=94)
        n=next(r for r in plan['episodes'] if r['id']==ep)
        evidence.append(dict(id=ep,title=n['title'],sourceKey=key,sourcePath=str(path),sourceUrl=source['sourceUrl'],
            sourceSha256=source_hash,sourceWidth=video['width'],sourceHeight=video['height'],containerFps=video['avg_frame_rate'],
            localWindow=[start,end],decodedSamples=times,sampleSheet=str(folder/'source-sequence.jpg'),
            sampleSheetSha256=sha(folder/'source-sequence.jpg'),currentMaster=master,
            currentDemoTime=current,currentDemoSample=str(folder/'current-demo.jpg'),
            viewingScope='Six ordered decoded source frames plus current-master sample; existing source observations reused. Not uninterrupted playback or human whole-video review.',
            rightsStatus='Previously recorded source/publisher evidence retained; this is technical/editorial feasibility, not a fresh public-use clearance.'))
        print(ep+' decoded candidate '+key+' '+video['avg_frame_rate'],flush=True)
    for g in range(4):
        c=Image.new('RGB',(1920,1160),'#080c0a');d=ImageDraw.Draw(c)
        for i,r in enumerate(evidence[g*4:g*4+4]):
            x=(i%2)*960;y=(i//2)*580
            text(d,(x+10,y+1),r['id']+' current '+str(r['currentDemoTime'])+'s',25)
            c.paste(Image.open(r['currentDemoSample']),(x,y+40))
        c.save(WORK/f'current-contact-{g+1}.jpg',quality=94)
    save(HERE/'evidence.json',dict(scope=[r['id'] for r in evidence],request='Audit feasibility only; no master, TTS, engine or platform changes.',episodes=evidence,
          samplingOnly=True,productionStarted=False,platformChanged=False,humanWholeVideoReviewed=False))
    print('Read-only picture audit complete;16 decoded source windows /16 current pictures.')
if __name__=='__main__':main()
