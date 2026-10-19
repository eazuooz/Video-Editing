"""Extract exactly eight current inspected stills, never an old candidate.

Run --dry-run (no probe/extract/write), then --prepare explicitly.
visual-asset-selection.json: slug/revision/sourceSelectionSha256/
titleSelectionSha256/assets[{id,source,localSeconds,purpose,actuallyInspected,
reviewEvidence}]. IDs accept optional .png. Actual extraction preserves aspect
without crop/stretch in1920x1080, caches only assets-current and copies exactly
eight current PNGs to the renderer directory. No other media stage runs here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
LOCAL=PROJECT/'production/local/reference-preserving-v3'
OUT=LOCAL/'assets-current'
DEST=ROOT/'output/player-customization/preproduction-assets-v3'
SELECTION=HERE/'source-selection.json'
TITLES=HERE/'title-selection.json'
SPEC=HERE/'visual-asset-selection.json'
GAMES={'Splatoon Raiders','Animal Crossing: New Horizons','The Legend of Zelda: Breath of the Wild'}
IDS={'raiders-equipment','raiders-test','raiders-choice','botw-inventory','botw-test','acnh-before','acnh-after','acnh-categories'}
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF=os.environ.get('FFMPEG',str(BIN/'ffmpeg.exe'))
PROBE=os.environ.get('FFPROBE',str(BIN/'ffprobe.exe'))

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p): return p.resolve().relative_to(ROOT.resolve()).as_posix()
def scoped(v):
    p=Path(v);p=(p if p.is_absolute() else ROOT/p).resolve()
    p.relative_to(ROOT.resolve());return p
def receipt(p): return dict(path=rel(p),sha256=sha(p),bytes=p.stat().st_size)
def require(ok,message):
    if not ok: raise ValueError(message)

def guard():
    ap=HERE/'authorization.json';cp=ROOT/'shared/publishing/video-production-control.json'
    a,c=read(ap),read(cp)
    require((a.get('slug'),a.get('revision'))==('player-customization',HERE.name),'Wrong revision authorization')
    require(a.get('fullProductionAuthorized') is True and a.get('automaticNextVideo') is False
            and set(a.get('selectedGameTitles',[]))==GAMES,'Expected exact current one-video scope')
    return dict(authorization=receipt(ap),control=receipt(cp),observedGlobalSelection=c.get('selectedVideo'),foreignChanges=False)

def validate():
    auth=guard();sel,titles,spec=read(SELECTION),read(TITLES),read(SPEC)
    require((spec.get('slug'),spec.get('revision'))==('player-customization',HERE.name),'Wrong still spec revision')
    require(spec.get('sourceSelectionSha256')==sha(SELECTION) and spec.get('titleSelectionSha256')==sha(TITLES),'Stale source/title selection hash')
    require(set(titles.get('selectedTitles',[]))==GAMES,'Exact title selection changed')
    require((sel.get('slug'),sel.get('revision'))==('player-customization',HERE.name)
            and sel.get('referenceOnlyMediaExcluded') is True,'Independent current source selection required')
    sources={s['key']:s for s in sel['sources']};require(len(sources)==len(sel['sources']),'Duplicate source key')
    rows=[];files={}
    for item in spec['assets']:
        name=item['id'][:-4] if item['id'].endswith('.png') else item['id']
        require(name in IDS and item.get('actuallyInspected') is True,'Exact inspected still ID required')
        require(item.get('purpose') and item.get('reviewEvidence'),f'{name}: purpose/evidence missing')
        s=sources[item['source']]
        expected=('Splatoon Raiders' if name.startswith('raiders-') else
                  'The Legend of Zelda: Breath of the Wild' if name.startswith('botw-') else 'Animal Crossing: New Horizons')
        require(s.get('game')==expected and s.get('sourceRole')=='independent-gameplay'
                and s.get('referenceLesson') is False,f'{name}: wrong/non-independent game source')
        n=s['nativeSource'];w,h=n['decodedDimensions']
        require(n.get('minimum1080Passed') is True and n.get('noTaskUpscale') is True and w>=1920 and h>=1080,f'{name}: nativeFHD proof missing')
        at=float(item['localSeconds']);require(math.isfinite(at) and at>=0,'Invalid LOCAL time')
        require(any(float(r['localIn'])<=at<float(r['localOut']) for r in s['recommendedRanges']),f'{name}: outside selected inspected ranges')
        media=scoped(s['media']['path'])
        if rel(media) not in files: files[rel(media)]=receipt(media)
        require(files[rel(media)]['sha256']==s['media']['sha256'],f'{name}: source bytes changed')
        rows.append(dict(id=name,source=item['source'],localSeconds=at,purpose=item['purpose'],
                         actuallyInspected=True,reviewEvidence=item['reviewEvidence'],selectedSource=s))
    require(len(rows)==8 and {r['id'] for r in rows}==IDS,'Exactly eight unique current assets required')
    inputs=[receipt(SELECTION),receipt(TITLES),receipt(SPEC),receipt(Path(__file__)),*files.values()]
    signature=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    return dict(authorization=auth,inputs=inputs,signature=signature,rows=rows)

def inspect_header(s):
    proc=subprocess.run([PROBE,'-v','error','-select_streams','v:0','-show_entries',
        'stream=width,height,sample_aspect_ratio:format=duration','-of','json',str(scoped(s['media']['path']))],check=True,capture_output=True,text=True)
    data=json.loads(proc.stdout);v=data['streams'][0];dims=[int(v['width']),int(v['height'])]
    require(dims==s['nativeSource']['decodedDimensions'] and dims[0]>=1920 and dims[1]>=1080,'Actual source header differs from nativeFHD receipt')
    require(v.get('sample_aspect_ratio','1:1') in ('1:1','0:1','N/A'),'Non-square source needs explicit display-aspect conversion')
    return float(data['format']['duration'])

def prepare(state):
    from PIL import Image
    durations={}
    for r in state['rows']:
        s=r['selectedSource'];key=s['media']['sha256']
        if key not in durations: durations[key]=inspect_header(s)
        require(r['localSeconds']<durations[key],'Still exceeds actual source duration')
    OUT.mkdir(parents=True,exist_ok=True);records=[]
    for r in state['rows']:
        require(guard()['authorization']['sha256']==state['authorization']['authorization']['sha256'],'Authorization changed')
        s,name=r['selectedSource'],r['id'];target=OUT/(name+'.png');cache=OUT/(name+'.json')
        extraction=dict(sourceSha256=s['media']['sha256'],localSeconds=r['localSeconds'],accurateInputSeek=True,
            crop='none',aspect='contain; square pixels; black letterbox as needed',sourceDimensions=s['nativeSource']['decodedDimensions'],outputDimensions=[1920,1080])
        if cache.exists():
            old=read(cache)
            # Selection/rights text may be rebound after validation without
            #decoding an identical source frame again. Pixel inputs must match.
            require(old.get('extraction')==extraction
                    and target.exists() and sha(target)==old.get('sha256'),'Incompatible assets-current cache; preserve/version it before a changed extraction')
        else:
            require(not target.exists(),'Unreceipted current image exists; no silent overwrite')
            temp=OUT/('.'+name+'-'+uuid.uuid4().hex+'.png')
            subprocess.run([FF,'-nostdin','-n','-v','error','-threads','2','-ss',str(r['localSeconds']),
                '-i',str(scoped(s['media']['path'])),'-frames:v','1','-vf',
                'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1',
                '-threads','2',str(temp)],check=True)
            with Image.open(temp) as image: require(image.size==(1920,1080),'Extracted still dimensions changed')
            temp.replace(target)
        record=dict(id=name,image=rel(target),sha256=sha(target),inputSignature=state['signature'],
            sourceKey=r['source'],sourceFile=s['media']['path'],sourceUrl=s['sourceUrl'],
            uploader=s.get('uploaderCredit') or s['uploader'],game=s['game'],extraction=extraction,
            purpose=r['purpose'],reviewEvidence=r['reviewEvidence'],sourceFrameActuallyInspected=True,
            sourceRole='independent-gameplay',referenceLessonUsed=False,classification='explanation-still',
            layoutReview='pending actual1080/mobile with current final captions')
        cache.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(record)
    for item in state['inputs']: require(sha(scoped(item['path']))==item['sha256'],'Input changed; no renderer copy performed')
    DEST.mkdir(parents=True,exist_ok=True)
    for r in records:
        target=DEST/(r['id']+'.png')
        if not target.exists() or sha(target)!=r['sha256']:
            temp=target.with_name('.'+target.name+'-'+uuid.uuid4().hex+'.tmp');shutil.copy2(scoped(r['image']),temp)
            require(sha(temp)==r['sha256'],'Renderer copy changed bytes');temp.replace(target)
        r['rendererImage']=rel(target)
    result=dict(slug='player-customization',revision=HERE.name,assets=records,inputs=state['inputs'],
                authorization=state['authorization'],sourceSpecificPixelReview='pending',imagesRemainExplanation=True)
    path=HERE/'visual-assets.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return dict(status='prepared-eight-current-independent-stills',files=8,receipt=receipt(path),pixelReview='pending')

def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run',action='store_true',help='Validate pinned inspected specs; no probe/extract/write')
    mode.add_argument('--prepare',action='store_true',help='Probe headers, extract eight stills and copy current renderer assets')
    args=parser.parse_args()
    try:
        state=validate()
        result=(dict(status='dry-run; no probe/extract/write',inputSignature=state['signature'],
                    assets=[{k:v for k,v in r.items() if k!='selectedSource'} for r in state['rows']])
                if args.dry_run else prepare(state))
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as exc: parser.exit(2,f'Current still preparation stopped: {exc}\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
