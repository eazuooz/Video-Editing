"""Only cached count-up frames are reframed; no source extraction repeated."""
import json, hashlib, os
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[4];PR=Path(__file__).parent
SRC=ROOT/'shared/output/presenting-game-scores/balatro-caption-native-v3'
OUT=ROOT/'shared/output/presenting-game-scores/balatro-countup-framing-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    s=json.loads((SRC/'execution.json').read_text());assert s['exitCode']==0
    for r in s['images']+s['boards']:assert sha(r['path'])==r['sha256']
    save(PR/'balatro-native-pre-clearance-direct-review-v3.json',dict(reviewedAt=now(),execution=str(SRC/'execution.json'),executionSha256=sha(SRC/'execution.json'),
        allFiveBoardsDirectlyRead=True,samples=25,allHashesMatched=True,
        findings=['One-line fixed caption keeps the selected upper five cards and +10/Mult notifications readable at f1710-1800.',
            'Discard f1680-1700 from adoption: tarot transformation precedes the scored-hand observation.',
            'Native f1840 has enlarged/rotated176 glyph overlapping the fixed one-line caption top. Do not approve the original count-up framing.',
            'Count-up shot begins before observed f1810; select no earlier than f1810, without inferring the exact original montage cut.',
            'The original official closeup already truncates Round score at the top; this scene demonstrates chip/mult animations only, not the final round total or a full continuous run.'],
        sourceIntervalsApproved=False,footageAdopted=False,allFinalPixelsReviewed=False,rasterGitAdditions=0))
    assert not OUT.exists();OUT.mkdir(parents=True)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
    entries=[];left,top,right,bottom=s['captionBox']
    for r in s['images']:
        if r['frame']<1810:continue
        assert sha(r['rawPath'])==r['rawSha256']
        raw=Image.open(r['rawPath']).convert('RGB');im=raw.filter(ImageFilter.GaussianBlur(24));im.paste(raw.crop((0,48,1920,1080)),(0,0))
        d=ImageDraw.Draw(im);d.rectangle((left+14,top+14,right+14,bottom+14),fill='#073c32');d.rectangle((left,top,right,bottom),fill='white',outline='#161b18',width=3)
        d.text((960,970),s['placeholderText'],font=font,fill='#080b09',anchor='mm')
        p=OUT/f"overlay-{r['frame']:06}.jpg";im.save(p,quality=94);entries.append(dict(r,path=str(p),sha256=sha(p)))
    boards=[]
    for start in range(0,len(entries),6):
        im=Image.new('RGB',(1920,1683),'#151515');d=ImageDraw.Draw(im);rows=entries[start:start+6]
        for j,r in enumerate(rows):
            sample=Image.open(r['path']);sample.thumbnail((948,533));x=j%2*960+6;y=j//2*561+28;im.paste(sample,(x,y));d.text((x,y-26),f"countup shift48 f{r['frame']} PTS{r['pts']}",font=label,fill='white')
        p=OUT/f'board-{start//6+1:03}.jpg';im.save(p,quality=94);boards.append(dict(path=str(p),sha256=sha(p),entries=rows))
    save(OUT/'execution.json',dict(startedAt=now(),pid=os.getpid(),exitCode=0,stage='cached-countup-clearance-ready-direct-review-pending',
        sourceExtractionRepeated=False,foregroundCrop=[0,48,1920,1080],foregroundScale=1,bottomFill='same source frame Gaussian blur radius24, bottom48px only',
        fixedCaptionCenter=[960,970],captionMaxLines=1,images=entries,boards=boards,sampleCount=len(entries),boardCount=len(boards),
        sourceIntervalsApproved=False,allFinalPixelsReviewed=False,rastersGit=False))
    print(json.dumps(dict(exit=0,samples=len(entries),boards=len(boards))))
if __name__=='__main__':main()
