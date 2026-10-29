"""Prepare, then explicitly extract bounded CPU-only final-V2 mark QA.

Default invocation is metadata-only. --extract requires the completed master
SHA supplied by the coordinator and never replaces earlier evidence.
"""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
LOCAL=HERE.parent/'local/botw-v4'
OUT=LOCAL/'qa/final-v2'
PLAN_SHA='d7c261e7d10e23cf4865df8e2688515883a4dd5d3cbbe0cf04791b431b2216dd'
V1_PLAN_SHA='e9a7007a2ad328db51eb33b97b1b7c801867a03cc6bf2b07adf4dee8f3fe4e87'
V1_MASTER_SHA='6827aac1839481c847c5a2c34e4e90bb07a54cfce6f065da73a26656e97a4f93'
TARGETS={'04-05':[.29,.31,1.70,1.76,2.45,3.5],
         '07-01':[.05,.75,1.4,2.7,2.81,3.5]}

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def rel(path):return path.relative_to(ROOT).as_posix()
def exclusive_json(path,data):
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    with path.open('x',encoding='utf-8')as f:f.write(text)

def specification():
    pp=HERE/'edit-plan.json'
    assert sha(pp)==PLAN_SHA,'Unexpected V2 edit plan.'
    p=read(pp);cuts={c['id']:c for c in p['cuts']}
    cp=LOCAL/'edit/captions.json';captions=read(cp)['cues']
    points={}
    def add(frame,reason):
        assert 0<=frame<p['totalFrames']
        points.setdefault(frame,[]).append(reason)
    for cut_id,times in TARGETS.items():
        cut=cuts[cut_id];start=cut['startFrame'];end=cut['endFrame']
        for t in times:add(start+round(t*60),{'kind':'mark-state','requestedLocalSeconds':t,'targetCut':cut_id})
        # Both actual source joins, last two frames and first two frames.
        for boundary,name in [(start,'start'),(end,'end')]:
            for delta in [-2,-1,0,1]:add(boundary+delta,{'kind':'join','boundary':name,'offsetFrames':delta,'targetCut':cut_id})
        # Adjacent clause changes as well as clauses inside these short cuts.
        for cue in captions:
            for key in ['start','end']:
                frame=round(cue[key]*60)
                if start-30<=frame<=end+30:
                    for delta in [-1,1]:add(frame+delta,{'kind':'caption-boundary','cue':cue['cue'],'edge':key,'offsetFrames':delta,'targetCut':cut_id})
    rows=[]
    for frame,reasons in sorted(points.items()):
        cut=next(c for c in p['cuts'] if c['startFrame']<=frame<c['endFrame'])
        local=(frame-cut['startFrame'])/60
        rows.append({'frame':frame,'ptsSeconds':frame/60,'cut':cut['id'],'kind':cut['kind'],
            'localSeconds':local,'sourceSeconds':cut.get('sourceStart',0)+local if cut['kind']=='independent-gameplay'else None,
            'reasons':reasons,'captionCues':[c['cue']for c in captions if c['start']<=frame/60<c['end']],
            'image':rel(OUT/f'f{frame:06d}-{cut["id"]}.jpg')})
    assert len(rows)<90,'Unexpected extraction scope expansion.'
    return {'schemaVersion':1,'status':'prepared-no-extraction','editPlanSha256':PLAN_SHA,
        'captionUnitsSha256':sha(cp),'movie':rel(LOCAL/'edit/kind-to-beginners-captioned.mp4'),
        'scope':'Two corrected marks, each neighboring join ±2 frames and adjacent caption boundaries.',
        'requestedCutLocalStates':TARGETS,'frames':rows}

def inheritance():
    proof=read(HERE/'final-visual-corrections.json')
    old=LOCAL/'edit/review-v1-preserved/edit-plan.json'
    assert sha(old)==V1_PLAN_SHA
    p=read(HERE/'edit-plan.json');q=read(old)
    assert len(p['cuts'])==len(q['cuts'])==53
    changed=[]
    for c,b in zip(p['cuts'],q['cuts']):
        assert c['id']==b['id']
        if c!=b:
            assert c['id']in TARGETS
            assert {k:v for k,v in c.items()if k!='marks'}=={k:v for k,v in b.items()if k!='marks'}
            changed.append(c['id'])
    assert set(changed)==set(TARGETS)
    unchanged=[]
    assert len(proof['unchangedCutMedia'])==51
    for r in proof['unchangedCutMedia']:
        pth=LOCAL/'edit'/(r['cut']+'.mp4');actual=sha(pth);assert actual==r['sha256'],r['cut']
        unchanged.append({'cut':r['cut'],'path':rel(pth),'sha256':actual})
    inputs=[]
    for name,expected in proof['unchangedInputs'].items():
        pth=(LOCAL/'edit'/name)if(LOCAL/'edit'/name).exists()else(HERE/name)
        actual=sha(pth);assert actual==expected,name
        inputs.append({'path':rel(pth),'sha256':actual})
    return {'previousMasterSha256':V1_MASTER_SHA,'previousPlanSha256':V1_PLAN_SHA,
        'currentPlanSha256':PLAN_SHA,'changedCutIds':changed,'unchangedCutCount':51,
        'unchangedCutMedia':unchanged,'unchangedInputs':inputs,
        'evidence':rel(HERE/'final-visual-corrections.json'),'evidenceSha256':sha(HERE/'final-visual-corrections.json'),
        'priorGameplayReview':rel(HERE/'gameplay-final-pixel-review.json'),'priorGameplayReviewSha256':sha(HERE/'gameplay-final-pixel-review.json'),
        'inference':'Reuses reviewed V1 source/cut states only for byte-identical 51 cuts with identical ASS/audio/timeline. Does not claim fresh continuous viewing of all V2 frames.'}

def extract(spec,expected):
    from audio_pipeline import tool
    assert len(expected)==64 and expected!=V1_MASTER_SHA,'Completed V2 master SHA is required.'
    movie=ROOT/spec['movie'];stat=movie.stat();assert sha(movie)==expected,'Incomplete or unexpected master.'
    evidence=inheritance()
    rows=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    for row in spec['frames']:
        f=ROOT/row['image'];assert not f.exists(),f
        subprocess.run([tool('ffmpeg'),'-v','error','-threads','2','-ss',format(row['ptsSeconds'],'.9f'),
            '-i',str(movie),'-frames:v','1','-q:v','2','-threads','2','-filter_threads','1','-n',str(f)],check=True)
        with Image.open(f)as im:assert im.size==(1920,1080)
        rows.append({**row,'sha256':sha(f),'viewed':False})
    assert (movie.stat().st_size,movie.stat().st_mtime_ns)==(stat.st_size,stat.st_mtime_ns),'Master changed during extraction.'
    pages=[]
    for n in range(0,len(rows),12):
        board=Image.new('RGB',(1125,247*4),(18,18,18));draw=ImageDraw.Draw(board)
        for i,r in enumerate(rows[n:n+12]):
            x=i%3*375;y=i//3*247
            with Image.open(ROOT/r['image'])as im:board.paste(im.resize((375,211),Image.Resampling.LANCZOS),(x,y+36))
            draw.text((x+3,y+2),f"{r['cut']} f{r['frame']} local{r['localSeconds']:.3f}",font=font,fill='white')
            draw.text((x+3,y+19),f"t{r['ptsSeconds']:.3f} captions{r['captionCues']}",font=font,fill='#cccccc')
        f=OUT/f'gameplay-delta-375-{n//12+1:02d}.jpg';assert not f.exists();board.save(f,quality=94)
        pages.append({'path':rel(f),'sha256':sha(f),'frames':[r['frame']for r in rows[n:n+12]],'viewed':False})
    exclusive_json(OUT/'index.json',{'status':'extracted-not-yet-viewed','extractedAt':datetime.now().astimezone().isoformat(),
        'movie':spec['movie'],'masterSha256':expected,'editPlanSha256':PLAN_SHA,'frames':rows,'mobilePages':pages,'inheritance':evidence})
    print(json.dumps({'frames':len(rows),'mobilePages':len(pages),'index':rel(OUT/'index.json'),'masterSha256':expected}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--extract',action='store_true');ap.add_argument('--expected-master-sha256');args=ap.parse_args()
    spec=specification();OUT.mkdir(parents=True,exist_ok=True)
    prepared=OUT/'extraction-plan.json'
    if prepared.exists():assert read(prepared)==spec,'Changed prepared extraction plan.'
    else:exclusive_json(prepared,spec)
    if args.extract:
        assert args.expected_master_sha256,'Must supply completed master hash from coordinator.'
        extract(spec,args.expected_master_sha256)
    else:print(json.dumps({'status':'prepared-only-no-ffmpeg','frames':len(spec['frames']),'path':rel(prepared),'sha256':sha(prepared)}))

if __name__=='__main__':main()
