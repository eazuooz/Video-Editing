"""Recompose changed candidate stills from the preserved native extraction.

Pixels remain local. Reuse current native samples; no source decode/extraction.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
resource=read(ROOT/args.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
input_path=PROOF/'word-cue-input-trials-v1.json';source_path=BASE/'word-action-source-candidate-v2.json'
caption_path=BASE/'word-caption-candidate-v3/captions.json'
old=read(input_path);source=read(source_path);caption=read(caption_path)
assert source['captionCandidateSha256']==sha(caption_path)
cuts={c['id']:c for p in source['pieces'] for c in p['selectedSourceCuts']}
affected=set(source['targetedCropIds'])|{'10-part2-cut01'}
samples=[s for s in old['samples'] if s['cutId'] in affected]
out=ROOT/'shared/output/familiar-game-rules/research/targeted-input-recheck-v3'
dest=PROOF/'targeted-input-recheck-v3.json'
assert not out.exists() and not dest.exists()
(out/'captioned').mkdir(parents=True);(out/'boards').mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
tiles=[]
for sample in samples:
    native=ROOT/sample['nativePath'];assert sha(native)==sample['nativeSha256']
    cut=cuts[sample['cutId']];crop=cut['sourceCrop'];x,y,w,h=crop
    t=sample['outputFrame']/60
    matches=[r for r in caption['ko'] if r['startSeconds']<=t<r['endSeconds']]
    assert len(matches)<=1
    cue=matches[0] if matches else None
    with Image.open(native) as raw:
        im=raw.crop((x,y,x+w,y+h)).resize((1920,1080),Image.Resampling.LANCZOS).convert('RGB')
    box=None
    if cue:
        width=round(font.getlength(cue['ko'])+44);left=960-width/2;top=928
        draw=ImageDraw.Draw(im)
        draw.rectangle((left+14,top+14,left+width+14,top+98),fill='#073c32')
        draw.rectangle((left,top,left+width,top+84),fill='white',outline='#161b18',width=3)
        draw.text((960,top+11),cue['ko'],font=font,fill='#080b09',anchor='mt')
        box=[left,top,width,84]
    p=out/'captioned'/f'{len(tiles)+1:04}.jpg';im.save(p,quality=95)
    tiles.append(dict(index=len(tiles)+1,originalSampleIndex=sample['index'],outputFrame=sample['outputFrame'],
       sourceVideoId=sample['sourceVideoId'],sourceFrame=sample['sourceFrame'],cutId=cut['id'],sourceCrop=crop,
       nativePath=sample['nativePath'],nativeSha256=sample['nativeSha256'],captionIndex=cue['index'] if cue else None,
       literalKo=cue['ko'] if cue else None,captionBox=box,path=rel(p),sha256=sha(p),directlyRead=False))
boards=[]
for first in range(0,len(tiles),6):
    board=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(board);group=tiles[first:first+6]
    for i,tile in enumerate(group):
        x,y=i%2*960,i//2*570
        draw.text((x+6,y+1),f'{tile["index"]} {tile["cutId"]} {tile["sourceVideoId"]}@{tile["sourceFrame"]} cue{tile["captionIndex"]}',font=label,fill='black')
        with Image.open(ROOT/tile['path']) as im:board.paste(im.resize((960,540)),(x,y+30))
    p=out/'boards'/f'{len(boards)+1:02}.jpg';board.save(p,quality=95)
    boards.append(dict(index=len(boards)+1,path=rel(p),sha256=sha(p),tileIndices=[r['index'] for r in group],directlyRead=False))
data=dict(schemaVersion=1,slug='familiar-game-rules',createdAt=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),
    commandLine=[os.sys.executable,*os.sys.argv],cpuThreads=1,gpuJobs=0,resourceObservation=resource,
    inputEvidence=rel(input_path),inputEvidenceSha256=sha(input_path),sourceCandidate=rel(source_path),sourceCandidateSha256=sha(source_path),
    captionCandidate=rel(caption_path),captionCandidateSha256=sha(caption_path),affectedCutIds=sorted(affected),tiles=tiles,boards=boards,
    sampleCount=len(tiles),boardCount=len(boards),newSourceExtraction=0,newGitImages=0,imagesGitPolicy='local-only',
    allDirectlyRead=False,allSourceMotionReviewed=False,allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,
    scope='All preserved v1 samples of changed8cuts recomposed with exact current candidate cue text; additional new split edge pixels and complete moving source remain separate pending checks.')
dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=len(tiles),boards=len(boards),newSourceExtraction=0,finalApproved=False)))
