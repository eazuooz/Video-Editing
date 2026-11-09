"""Isolated visual-only corrections on the original relations-v4 clock."""
from pathlib import Path
import hashlib,json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont

H=Path(__file__).resolve().parents[1]; R=H.parents[3]
O=H/'local/visual-corrections/A01'; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(H/'renderer'))
import compose
from sources import input_receipt
FPS=60; BG='#080c0e'; WHITE='#f5f4ed'; YELLOW='#f2d787'; TEAL='#81cfc5'; RED='#f18b81'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def rel(p):
    try:return Path(p).resolve().relative_to(R.resolve()).as_posix()
    except ValueError:return Path(p).resolve().as_posix()
def text(d,xy,t,size=42,color=WHITE):d.text(xy,t,font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size),fill=color)
def base(title,game):
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    text(d,(60,35),title,60,YELLOW);text(d,(60,114),game,34,WHITE)
    text(d,(1460,120),'실제 프레임 분석',32,WHITE)
    return im
def outlined(d,box,color):
    d.rectangle(box,outline=BG,width=13);d.rectangle(box,outline=color,width=7)
def still(name):
    if name in ('walk','pose'):
        return compose.frame('A01',name,57,mode='compare',legend=False)
    if name=='goose':
        p=H/'local/game-plates/A01/A01-gp-023476-023618-analysis.mp4'
        f=O/'goose-current-analysis.png'
        if not f.exists():subprocess.run(['ffmpeg','-v','error','-threads','1','-ss','1','-i',str(p),'-frames:v','1','-threads','1','-y',str(f)],check=True)
        return Image.open(f).convert('RGB')
    if name=='oatchi':
        im=base('두 몸이 맞닿는 위치를 함께 보기','Pikmin 4');src=Image.open(O/'pikmin-oatchi.png').convert('RGB')
        im.paste(src.resize((1000,563)),(55,225));im.paste(src.crop((820,430,1120,730)).resize((600,600)),(1190,205))
        d=ImageDraw.Draw(im);outlined(d,(1210,275,1610,475),TEAL);outlined(d,(1260,470,1660,750),YELLOW)
        text(d,(1070,180),'맞닿는 부분 확대',36,TEAL)
        text(d,(62,818),'탑승자의 위치',42,TEAL);text(d,(1020,818),'오치의 등과 몸',42,YELLOW)
    elif name=='weapon':
        im=base('몸과 무기가 차지하는 공간','Sifu');src=Image.open(O/'sifu-weapons-a.png').convert('RGB')
        im.paste(src.resize((1184,666)),(48,186));im.paste(src.crop((350,270,900,820)).resize((590,590)),(1270,215))
        d=ImageDraw.Draw(im);outlined(d,(1280,295,1590,420),TEAL)
        text(d,(1280,175),'손과 봉의 방향',36,TEAL)
        text(d,(84,810),'팔 끝에서 끝나지 않는 동작',40,YELLOW)
    else:
        im=base('상대의 행동과 몸의 방향','Sifu');src=Image.open(O/'sifu-check-21.0.png').convert('RGB')
        im.paste(src.resize((1184,666)),(48,186));im.paste(src.crop((700,350,1200,850)).resize((590,590)),(1270,215))
        d=ImageDraw.Draw(im);text(d,(1270,175),'몸과 상대를 함께 관찰',34,TEAL)
        text(d,(84,810),'공격 방향 · 몸을 옮길 방향',40,YELLOW)
    return im
def encode(output,frames,getframe):
    args=['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','-','-an','-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-y',str(output)]
    p=subprocess.Popen(args,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    for f in range(frames):p.stdin.write(getframe(f).tobytes())
    p.stdin.close();assert p.wait()==0
    v=read_probe(output);assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',frames)
def read_probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(p)]))['streams'][0]
def main():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert control['renderAuthorized'] and 'A01' in control['episodes']
    integ=read(H/'renderer/integration-caption-safe.json');ep=next(x for x in integ['episodes']if x['id']=='A01')
    timing=read(H/'baseline-sentence-timing.json');sent=next(x for x in timing['records']if x['id']=='A01')['sentences']
    ranges=[(1722,1868,'direction'),(12142,12267,'walk'),(17665,17908,'oatchi'),(18232,18237,'oatchi'),(18462,18480,'oatchi'),(18687,19276,'oatchi'),(19276,19453,'weapon'),(19627,19659,'weapon'),(19833,20433,'weapon'),(20433,20626,'direction'),(20973,21035,'pose'),(23618,23800,'goose'),(25006,25486,'goose'),(26830,28005,'stop')]
    stills={k:still(k)for k in ['oatchi','weapon','direction','walk','pose','goose']}
    for k,im in stills.items():im.save(O/(k+'-design.png'))
    rows=[]
    for a,b,kind in ranges:
        name=f'A01-correction-{a:06d}-{b:06d}-{kind}';p=O/(name+'.mp4');count=b-a
        if kind=='stop':
            # One observed stop sequence, then its genuinely different step poses.
            # Slow analysis is labelled by the shared compositor, not native gameplay.
            cached={}
            def getframe(f):
                if f<540:key=('compare',min(119,int(f*120/540)))
                else:key=('stages',100)
                if key not in cached:cached[key]=compose.frame('A01','stop',key[1],mode=key[0],legend=False)
                return cached[key]
            evidence=input_receipt('A01','stop');sourcekey='A01-stop';sourcefile=None;sourceat=None
        elif kind in ('walk','pose'):
            im=stills[kind];getframe=lambda f,im=im:im
            evidence=input_receipt('A01',kind);sourcekey='A01-'+kind;sourcefile=None;sourceat=None
        elif kind=='goose':
            im=stills[kind];getframe=lambda f,im=im:im
            sourcekey='goose-basket-start';sourcefile=H/'footage/local/goose-basket-start.mp4';sourceat=9.966666666666665
            prior=H/'local/game-plates/A01/A01-gp-023476-023618-analysis.mp4'
            evidence={'source':rel(sourcefile),'sha256':sha(sourcefile),'observedFrameTimes':[8.45,9.966666666666665,11.483333333333333],'alreadyVerifiedAnalysisPlate':rel(prior),'analysisPlateSha256':sha(prior),'observation':'Current independently recorded goose beak and basket contact. No 2017 development/reference screenshot.'}
        else:
            im=stills[kind];getframe=lambda f,im=im:im
            sourcekey={'oatchi':'pikmin-oatchi','weapon':'sifu-weapons-a','direction':'sifu-female'}[kind]
            sourcefile=H/'footage/local'/f'{sourcekey}.mp4';sourceat={'oatchi':14.65,'weapon':1.5,'direction':21.0}[kind]
            evidence={'source':rel(sourcefile),'sha256':sha(sourcefile),'decodedStillAtSeconds':sourceat,'stillSha256':sha(O/({'oatchi':'pikmin-oatchi.png','weapon':'sifu-weapons-a.png','direction':'sifu-check-21.0.png'}[kind])),'observation':'Visible external body/prop/contact relationship only. No inference of hidden joint data, successful evasion, boarding, or measured timing.'}
        if not p.exists():encode(p,count,getframe)
        else:assert int(read_probe(p)['nb_frames'])==count
        ids=[s['id']for s in sent if max(a,s['startSeconds']*60)<min(b,s['endSeconds']*60)]
        underlying=[r['id']for r in ep['rows']if max(a,r['relationFrameStart'])<min(b,r['relationFrameEnd'])]
        row={'id':name,'kind':'authored-explanation','startFrame':a,'endFrame':b,'newFrames':count,'picture':rel(p),'pictureSha256':sha(p),'sourceStartFrame':0,'sourceVerified':True,'expectedUnderlyingExplanationIds':underlying,'narrationEvidence':{'path':rel(H/'baseline-sentence-timing.json'),'sha256':sha(H/'baseline-sentence-timing.json'),'sentenceIds':ids},'reason':'Replace leftover unrelated commercial screenshot with the approved observed example or existing same-topic UE illustration.'if kind!='stop'else'Replace incorrect upright/crouched walk comparison under stop-foot narration with actual left/right stop study.','mediaSegments':[{'kind':'authored-explanation'if kind in ('stop','walk','pose')else'still-analysis','offsetFrame':0,'frames':count,'sourceKey':sourcekey,'sourceLocalIn':sourceat,'sourceLocalOut':sourceat,'sourceSha256':evidence.get('sha256'),'nativeFrames':0}],'visualEvidence':evidence,'captionSafeBottomY':892,'newAudio':False,'newTts':False}
        rows.append(row);print('DONE',name,flush=True)
    result={'schemaVersion':1,'episode':'A01','clock':'relations-v4','readyForAssembly':True,'pictureEdits':rows,'sourceCode':rel(Path(__file__)),'sourceCodeSha256':sha(__file__),'preservesExistingNativeGamePlates':True,'nativeGameplayFramesAdded':0,'retainsUsefulNarrationAndOrder':True,'humanFullWatch':False,'modelVisualReview':'Design/encoded patch review recorded separately; final rebuilt master review still required.'}
    (H/'visual-corrections/A01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
if __name__=='__main__':main()
