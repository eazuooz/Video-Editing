"""Every current cue, cue/cut intersection, exact caption edge and paragraph onset."""
from final_cpu_common import *
import argparse, math, traceback
from PIL import Image, ImageDraw, ImageFont
parser=argparse.ArgumentParser();parser.add_argument('--plan-only',action='store_true');parser.add_argument('--resource');a=parser.parse_args()
plan=read(FINAL/'plan.json');cap=read(ROOT/plan['captionCandidate']);visual=read(FINAL/'visual-build.json')
assert sha(ROOT/plan['captionCandidate'])==plan['captionCandidateSha256']
assert visual['planSha256']==sha(FINAL/'plan.json')
def centis(s):
    h,m,z=s.split(':');return int(h)*360000+int(m)*6000+round(float(z)*100)
rows=[]
for line in (FINAL/'captions.ko.ass').read_text(encoding='utf-8-sig').splitlines():
    if line.startswith('Dialogue: 2,'):
        fields=line.split(',',9);start,end=centis(fields[1]),centis(fields[2]);rows.append(dict(index=len(rows)+1,startCentisecond=start,endCentisecond=end,firstFrame=math.ceil(start*.6-1e-8),endFrameExclusive=math.ceil(end*.6-1e-8),text=fields[9]))
assert len(rows)==253 and len(cap['paragraphs'])==70
points={}
def add(frame,anchor,cue=None):
    frame=int(frame)
    if 0<=frame<plan['finalFrames']:
        r=points.setdefault(frame,dict(frame=frame,anchors=[],cues=[]))
        if anchor not in r['anchors']:r['anchors'].append(anchor)
        if cue and cue not in r['cues']:r['cues'].append(cue)
for cue in rows:
    start,end=cue['firstFrame'],cue['endFrameExclusive']
    assert end>start
    for f,tag in [(start-1,'before'),(start,'first'),((start+end-1)//2,'middle'),(end-1,'last'),(end,'after')]:add(f,f'cue-{cue["index"]}-{tag}',cue['index'])
for seg in visual['segments']:
    start,end=seg['startFrame'],seg['startFrame']+seg['frames']
    for f,tag in [(start-1,'before'),(start,'first'),(start+1,'first+1'),((start+end-1)//2,'middle'),(end-2,'last-1'),(end-1,'last'),(end,'after')]:add(f,tag+':'+seg['id'])
    for cue in rows:
        lo,hi=max(start,cue['firstFrame']),min(end,cue['endFrameExclusive'])
        if hi>lo:add((lo+hi-1)//2,'cue/segment:'+seg['id'],cue['index'])
for para in cap['paragraphs']:
    f=round(para['startSeconds']*60)
    for off in [-1,0,1]:add(f+off,f'paragraph-onset:{para["scene"]}p{para["paragraph"]}')
for f in [0,60,119,120,5871,5876,5877,5995,5996,5997,6006,6051,22969,22970,22971,23270,23569]:add(f,'targeted-branding/guide13/member')
for f,row in points.items():
    seg=next(s for s in visual['segments'] if s['startFrame']<=f<s['startFrame']+s['frames'])
    row.update(segment=seg['id'],classification=seg['classification'],scene=seg.get('sceneId'),localFrame=f-seg['startFrame'],visibleCueIds=[c['index'] for c in rows if c['firstFrame']<=f<c['endFrameExclusive']])
assert {c for r in points.values() for c in r['cues']}==set(range(1,254))
request=dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),captionAssSha256=sha(FINAL/'captions.ko.ass'),sampledFrames=len(points),cueCount=253,nativeCutCount=85,whiteCount=8,all70ParagraphOnsetsCovered=True,assCentisecondTimesDirectlyParsed=True,points=[points[f] for f in sorted(points)],koRows=rows,allImagesLocalOnly=True,newGitImages=0,allEncodedPixelsDirectlyReviewed=False)
if a.plan_only:
    write(FINAL/'encoded-caption-qa-request.json',request);print(json.dumps(dict(frames=len(points),cues=253,imagesCreated=0,approved=False)));raise SystemExit(0)
pair=read(FINAL/'review-pair-build.json');assert pair['planSha256']==request['planSha256'] and pair['captionAssSha256']==request['captionAssSha256'] and pair['identicalAacPayload']
source=next(r for r in pair['records'] if '.captioned.' in r['path']);assert sha(ROOT/source['path'])==source['sha256']
dest=FINAL/'encoded-caption-qa-local-v1';assert not dest.exists() and a.resource
w=Worker('encoded-caption-qa',a.resource,'Directly read all actual final cue/cut/UI/PCM/branding/member boards before approval, collection and private delivery. Then Git and pause24, no next queued.');dest.mkdir();write(FINAL/'encoded-caption-qa-request.json',request)
w.state.update(source=source['path'],sourceSha256=source['sha256'],request=rel(FINAL/'encoded-caption-qa-request.json'),images=[],sheets=[],allFinalPixelsApproved=False,qaApproved=False,newGitImages=0,finalMixAsrApproved=True)
try:
    w.checkpoint();expression='+'.join(f'eq(n\\,{f})' for f in sorted(points))
    assert not w.ff(['-v','error','-i',ROOT/source['path'],'-an','-vf',f"select='{expression}'",'-fps_mode','passthrough','-frames:v',len(points),dest/'frame-%04d.png'],'CPU-exact-encoded-pixel-extraction').strip()
    files=sorted(dest.glob('frame-*.png'));assert len(files)==len(points)
    for path,f in zip(files,sorted(points)):w.state['images'].append(dict(points[f],path=rel(path),sha256=sha(path),directlyRead=False))
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
    for offset in range(0,len(files),6):
        subset=w.state['images'][offset:offset+6];board=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(board)
        for slot,row in enumerate(subset):
            x,y=slot%2*960,slot//2*580
            with Image.open(ROOT/row['path']) as im:
                assert im.size==(1920,1080);board.paste(im.resize((960,540)),(x,y+40))
            draw.text((x+5,y+4),f'{offset+slot+1:04d} n{row["frame"]} {row["segment"][:30]} cue{row["visibleCueIds"]}',font=font,fill='black')
        path=dest/f'final-sheet-{offset//6+1:03d}.jpg';board.save(path,quality=94)
        w.state['sheets'].append(dict(path=rel(path),sha256=sha(path),imageIndices=list(range(offset+1,offset+len(subset)+1)),directlyRead=False))
        if offset%60==0:w.checkpoint()
    w.close('closed-encoded-pixels-awaiting-direct-review');print(json.dumps(dict(images=len(files),sheets=len(w.state['sheets']),newGitImages=0,approved=False)))
except BaseException:w.close('closed-encoded-pixel-extraction-failed',1,traceback.format_exc());raise
