"""Four-fps finite-frame sequence QA supplement; never realtime-playback evidence."""
from pathlib import Path
import hashlib, json, math, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'; H=Path(__file__).parent
O=P/'production/local/revision-v5/preflight-final/temporal'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
    outputs=read(P/'production/local/revision-v5/gizmos/outputs.json')
    static=read(H/'gizmo-review.json'); plan=read(H/'gizmo-plan.json')
    timeline=read(P/plan['timeline']); annotation=read(P/plan['sourceAnnotation'])
    O.mkdir(parents=True,exist_ok=True)
    rows=[]; font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
    for repl in outputs['replacements']:
        name=repl['id']; entry=repl['files']['captioned']; clip=R/entry['file']
        assert sha(clip)==entry['sha256']; count=repl['frames']
        frames=sorted(set(range(0,count,15))|{count-1})
        folder=O/name; folder.mkdir(exist_ok=True)
        inputs=dict(captionedSha256=entry['sha256'],totalFrames=count,sampleFrames=frames,extractorSha256=sha(Path(__file__)))
        receipt=folder/'extraction.json'; reused=[]
        if not (receipt.exists() and read(receipt)['inputs']==inputs and all((folder/f'f-{n:04}.jpg').exists() for n in frames)):
            need=[]
            for n in frames:
                same=next((s for s in static['samples'] if s['id']==name and s['localFrame']==n),None)
                source=(R/same['native']) if same else None
                if same and source.exists() and sha(source)==same['nativeSha256']:
                    shutil.copyfile(source,folder/f'f-{n:04}.jpg'); reused.append(n)
                else: need.append(n)
            if need:
                select='+'.join('eq(n\\,%d)'%n for n in need)
                subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(clip),'-an','-vf','select='+select,'-fps_mode','vfr','-frames:v',str(len(need)),'-q:v','2',str(folder/'extract-%03d.jpg')],check=True)
                for i,n in enumerate(need): (folder/f'extract-{i+1:03}.jpg').replace(folder/f'f-{n:04}.jpg')
            save(receipt,dict(inputs=inputs,exactStaticSampleFramesReused=reused,newFramesExtracted=len(need)))
        er=read(receipt)
        w=next(w for w in plan['windows'] if w['id']==name)
        tracker=next(w for w in annotation['windows'] if w['id']==name)
        cut=next(c for c in timeline['cuts'] if c['scene']==tracker['scene'] and c['sourceId']==tracker['sourceId'] and c['sourceStart']<=w['start'] and c['sourceEnd']>=w['end'])
        samples=[]; boards=[]
        for n in frames:
            f=folder/f'f-{n:04}.jpg'; im=Image.open(f); assert im.size==(1920,1080)
            samples.append(dict(localFrame=n,localSeconds=n/60,sourceSeconds=w['start']+n/60,globalFrame=repl['globalStartFrame']+n,file=f.relative_to(R).as_posix(),sha256=sha(f)))
        for start in range(0,len(samples),16):
            chunk=samples[start:start+16]; board=Image.new('RGB',(1920,298*math.ceil(len(chunk)/4)),'#131313'); d=ImageDraw.Draw(board)
            for j,s in enumerate(chunk):
                x=j%4*480; y=j//4*298
                im=Image.open(R/s['file']).convert('RGB').resize((480,270),Image.Resampling.LANCZOS)
                board.paste(im,(x,y));d.text((x+4,y+272),f'{name} f{s["localFrame"]} {s["localSeconds"]:.3f}s',font=font,fill='white')
            f=folder/f'board-{start//16+1:02}.jpg';board.save(f,quality=96)
            boards.append(dict(file=f.relative_to(R).as_posix(),sha256=sha(f),firstLocalFrame=chunk[0]['localFrame'],lastLocalFrame=chunk[-1]['localFrame'],samples=len(chunk)))
        assert sha(clip)==entry['sha256']
        rows.append(dict(id=name,captionedFile=entry['file'],captionedSha256=entry['sha256'],totalFrames=count,rate='4 fps plus final frame',coverageSeconds=count/60,samples=samples,boards=boards,extraction=er,sourceCut=dict(id=cut['id'],sourceId=cut['sourceId'],windowIn=w['start'],windowOutExclusive=w['end'],originalCutIn=cut['sourceStart'],originalCutOut=cut['sourceEnd'],containedInOneOriginalCut=True),review='pending direct temporal-frame-sequence review; not realtime playback'))
    report=dict(revision=plan['revision'],method='Direct inspection of 4fps ordered frame sheets including exact first/last encoded frame; supplementary temporal sampling, not realtime playback and not exhaustive 60fps inspection.',rendererSha256=sha(H/'gizmo-render.py'),planSha256=sha(H/'gizmo-plan.json'),outputsSha256=sha(P/'production/local/revision-v5/gizmos/outputs.json'),clips=rows,totalSamples=sum(len(x['samples']) for x in rows),totalBoards=sum(len(x['boards']) for x in rows),review='pending',productionMediaChanged=False)
    save(H/'gizmo-review-sequence.json',report)
    print(json.dumps(dict(samples=report['totalSamples'],boards=report['totalBoards'],report=str(H/'gizmo-review-sequence.json')),ensure_ascii=False))

if __name__=='__main__':main()
