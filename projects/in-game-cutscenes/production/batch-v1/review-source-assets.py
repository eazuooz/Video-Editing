"""Bounded independent-source still extraction only; no rendered-video job."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4]
P=R/'projects/in-game-cutscenes'
L=P/'production/local/batch-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def still(src,t,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():return
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(src),'-frames:v','1','-update','1','-y',str(dest)],check=True)
for stem,times in [('hades2-first-run',list(range(118,146))),('hades2-crossroads',list(range(38,59)))]:
    src=L/'sources'/f'{stem}.mp4';out=L/'sources'/f'{stem}-review/fine';records=[]
    for i,t in enumerate(times,1):
        dst=out/f'native-{i:03}.png';still(src,t,dst);records.append({'file':rel(dst),'sourceSecond':t,'sha256':sha(dst)})
    for page in range((len(records)+8)//9):
        board=Image.new('RGB',(1920,1152),'#111111');draw=ImageDraw.Draw(board)
        for cell,row in enumerate(records[page*9:page*9+9]):
            im=Image.open(R/row['file']);im.thumbnail((640,360));x=(cell%3)*640;y=(cell//3)*384
            board.paste(im,(x,y));draw.text((x+8,y+361),f"native {row['sourceSecond']}s",fill='white')
        board.save(out/f'contact-{page+1:02}.jpg',quality=93)
    write(out/'index.json',{'source':rel(src),'sourceSha256':sha(src),'frames':records,'scope':'Decoded source stills only; full playback/listening not claimed.'})
S=R/'projects/start-with-climax';SL=S/'production/local/batch-v1';assets=SL/'visual-assets';records=[]
gal=SL/'sources/galaxy2-opening-OWl-ikWpNMU.mkv'
for name,t in [('spin-before',114.0),('spin-after',115.6)]:
    dst=assets/f'{name}.png';still(gal,t,dst);records.append({'id':name,'file':rel(dst),'sha256':sha(dst),'sourceFile':rel(gal),'sourceSha256':sha(gal),'sourceSecond':t,'nativeDimensions':list(Image.open(dst).size),'purpose':'Before/after Spin crystal destruction; no mandatory path-opening claim.'})
fine=SL/'sources/ace-announce-review/fine-first-case'
for name,i,t in [('ace-badge',6,57.991),('ace-statue',7,58.992)]:
    dst=fine/f'{i:03}.png';records.append({'id':name,'file':rel(dst),'sha256':sha(dst),'sourceFile':rel(SL/'sources/ace-trilogy-official-announce.mp4'),'sourceSecond':t,'purpose':'Evidence-selection object changes; official edited UI excerpts, not a continuous play attempt.'})
write(S/'production/batch-v1/asset-records.json',{'revision':'batch-v1','status':'native-source-illustrations-extracted-pixel-read-pending','assets':records,'captionProtectedRect':[150,892,1784,1060],'imageUrlBase':'/@fs/D:/Github/VideoEditing/'})
extra=SL/'sources/galaxy2-first-stage-OWl-ikWpNMU.mkv'
probe=json.loads((SL/'sources/first-stage-review/probe.json').read_text(encoding='utf-8'))
write(S/'sources/galaxy2-extra-source-review.json',{'file':rel(extra),'sha256':sha(extra),'sourceUrl':'https://www.youtube.com/watch?v=OWl-ikWpNMU','recorder':'LongplayArchive','classification':'independent-gameplay','requestedOriginalRange':[300,390],'nativeDimensions':[2560,1404],'decodedProbe':rel(SL/'sources/first-stage-review/probe.json'),'decodedDuration':probe['format']['duration'],'visualReview':'All32 three-second bins local0–96 directly read by /root/d22_reference. No subjective audio listening or uninterrupted-play assertion.','actualWindows':[{'in':9,'out':19,'before':'Mario at lower route','action':'Jumps up yellow platforms','result':'Reaches upper blue checkpoint area'},{'in':33,'out':51,'before':'Base of yellow platforms','action':'Successive upward jumps','result':'Reaches Launch Star at top'},{'in':78,'out':95,'before':'Landing on green route','action':'Spin crystal, jump across moving blocks','result':'Continues along route'}],'excluded':[[0,8,'Initial samples appear repeated after bounded stream-copy seek; no exact original-to-local offset asserted.'],[54,75,'Automatic launch/flight; not represented as continuous manual platform control.']],'rights':'Same Nintendo commentary policy and LongplayArchive transformed-credited-snippet permission in source-audit.json; no new game count.','sourceAudio':'Original synchronized audio preserved; actual listening remains pending.'})
print('Bounded native source frames and own D28 provenance records saved.')
