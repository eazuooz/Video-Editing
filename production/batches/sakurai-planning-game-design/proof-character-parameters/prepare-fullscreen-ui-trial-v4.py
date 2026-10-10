"""Small full-screen composition trial from preserved native PNGs, no extraction."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[4]; PROOF=Path(__file__).resolve().parent
QA=ROOT/'shared/output/character-parameters/preflight/fullscreen-ui-v4'
STATE=PROOF/'fullscreen-ui-trial-v4.json'
assert not QA.exists() and not STATE.exists(), 'Read existing trial; do not repeat.'
resource=json.loads((ROOT/'shared/output/character-parameters/preflight/resource-before-fullscreen-v4.json').read_text(encoding='utf-8-sig'))
assert (datetime.now().astimezone()-datetime.fromisoformat(resource['observedAt'])).total_seconds()<600
s=json.loads((PROOF/'native-framing-execution-v3.json').read_text(encoding='utf-8-sig'))
review=json.loads((PROOF/'native-trial-direct-review-v3.json').read_text(encoding='utf-8-sig'))
assert review['sampleContentDirectReviewComplete'] and review['totalSamplePixelsDirectlyRead']==897
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
TEXT='캐릭터마다 규칙이 다릅니다.'
def caption(im):
    d=ImageDraw.Draw(im); b=d.textbbox((0,0),TEXT,font=font)
    bw=b[2]-b[0]+44; bh=84; x=(1920-bw)//2; y=970-bh//2
    assert x>485 and x+bw+14<1460
    d.rectangle((x+14,y+14,x+bw+14,y+bh+14),fill='#073c32')
    d.rectangle((x,y,x+bw,y+bh),fill='white',outline='#161b18',width=3)
    d.text((x+22,y+11-b[1]),TEXT,font=font,fill='#080b09'); return im
def compose(im,key):
    im=im.convert('RGB')
    if key=='gBbKFYZYvbc':
        assert im.size==(1280,720)
        out=im.resize((1920,1080),Image.Resampling.NEAREST)
        # Original visible action0:657 is preserved at full width and original aspect.
        # Only the broadcast HUD band is rearranged to two bottom corners.
        bg=im.crop((0,602,1280,657)).filter(ImageFilter.GaussianBlur(12)).resize((1920,95),Image.Resampling.BILINEAR)
        out.paste(bg,(0,985))
        p1=im.crop((16,657,315,720)).resize((449,95),Image.Resampling.NEAREST)
        p2=im.crop((335,657,631,720)).resize((444,95),Image.Resampling.NEAREST)
        credit=im.crop((639,657,1280,720)).resize((462,45),Image.Resampling.LANCZOS)
        out.paste(p1,(24,985)); out.paste(p2,(1476,985)); out.paste(credit,(729,1035))
    else:
        assert im.size==(1920,1080)
        out=im.copy()
        # Keep all original game action, stats, skills and health in place.
        # Copy the actual same-frame inventory+coins to the unused upper-right region.
        inventory=im.crop((406,921,1520,1065)).resize((668,86),Image.Resampling.NEAREST)
        bg=im.crop((406,870,1520,920)).filter(ImageFilter.GaussianBlur(12)).resize((1114,144),Image.Resampling.BILINEAR)
        out.paste(bg,(406,921)); out.paste(inventory,(1205,370))
    return caption(out)
selection={
 'gBbKFYZYvbc':[357,570,1515,1530,1800,3597,4410,6120,6270,7605,7650,9780,10065],
 'a8nwpiCqyTQ':[1710,1752,1902,1950,2034,2139,2205,2265,2424,2502,2556,4533,4605]
}
QA.mkdir(parents=True)
out={'schemaVersion':1,'slug':'character-parameters','createdAt':datetime.now(timezone.utc).isoformat(),
 'status':'prepared-awaiting-direct-review','cpuThreads':1,'gpuJobs':0,'newNativeExtractionCount':0,
 'resourceProof':'shared/output/character-parameters/preflight/resource-before-fullscreen-v4.json',
 'framing':{'match':'Full-width source action, unchanged aspect/aerial extent; same-frame colored HUD panels split into bottom corners. Original commentator credit below caption. Blur only replaces original HUD band.',
 'dungeons':'Original1920x1080 action/stats/skills/hearts unchanged. Same-frame inventory/coin UI copied at0.6scale to1205,370; its old button region gets same-frame blurred floor.',
 'caption':'Fixed960,970 single-line18-or-fewer-Korean-character cues planned; final cues not yet authored.'},
 'samples':[],'boards':[],'fullscreenCompositionApproved':False,'allFinalCueUiApproved':False,
 'sourceAdoptionApproved':False,'externalResearchChanges':0,'rasterGitAdditions':0}
for key,frames in selection.items():
    src=next(x for x in s['sources'] if x['sourceKey']==key)
    for f in frames:
        t=next(x for x in src['samples'] if x['nativeFrame']==f)
        p=ROOT/t['path'];assert sha(p)==t['sha256']
        q=QA/f'{key}-f{f}.png';compose(Image.open(p),key).save(q)
        out['samples'].append({**t,'sourceKey':key,'trialPath':str(q.relative_to(ROOT)).replace('\\','/'),'trialSha256':sha(q)})
for off in range(0,len(out['samples']),6):
    board=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(board)
    for n,t in enumerate(out['samples'][off:off+6]):
        x=n%3*640;y=n//3*408
        board.paste(Image.open(ROOT/t['trialPath']).resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
        d.text((x+6,y+3),f"{t['sourceKey']} f{t['nativeFrame']}",font=small,fill='white')
        d.text((x+6,y+384),f"PTS{t['pts']} t{t['timeSeconds']:.6f} fullscreen-v4",font=small,fill=(180,230,230))
    p=QA/f'board-{off//6+1:03d}.jpg';board.save(p,quality=93)
    out['boards'].append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'sampleRange':[off,min(off+6,len(out['samples']))]})
STATE.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'samples':len(out['samples']),'boards':len(out['boards']),'adoption':False}))
