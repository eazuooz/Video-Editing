"""Inspect new Alyx transition PTS and reframe existing samples; CPU2, local-only."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import bisect, hashlib, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT = ROOT / 'shared/output/cross-game-example-coverage/motion/source-clearance-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.writing')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
def sheets(rows, folder, name):
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
    result = []
    for first in range(0, len(rows), 6):
        group = rows[first:first+6]
        im = Image.new('RGB', (1920, 780), '#f5f5f5'); draw = ImageDraw.Draw(im)
        for j, row in enumerate(group):
            x = j % 3 * 640; y = j // 3 * 390
            with Image.open(ROOT / row['path']) as source: im.paste(source.resize((640, 360)), (x,y))
            draw.text((x+4,y+363), f"{name} f{row['nativeFrame']} PTS{row['pts']}", font=font, fill='black')
        p = folder / f'sheet-{first//6+1:02d}.png'; im.save(p)
        result.append(dict(path=rel(p), sha256=sha(p), sampleCount=len(group)))
    return result
def main():
    target = R / 'source-clearance-execution-v1.json'
    assert not target.exists(), 'Preserve completed work; inspect it instead.'
    pre = json.loads((R/'source-preflight-v1.json').read_text('utf-8'))
    native = json.loads((R/'native-preflight-execution-v1.json').read_text('utf-8'))
    assert native['exitCode'] == 0 and native['totalSamples'] == 122
    assert all(sha(ROOT/x['path']) == x['sha256'] for x in pre['protectedBaseline'])
    me = psutil.Process()
    resource = dict(recordedAt=now(), pid=me.pid, createTime=me.create_time(), command=me.cmdline(), cwd=me.cwd(),
                    pythonProcesses=[dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline()) for p in psutil.process_iter() if p.name().lower().startswith('python')],
                    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout.strip(),
                    cpuThreads=2, gpuWorker=False, researchManipulation=False)
    save(R/'source-clearance-resource-v1.json',resource)
    state=dict(status='running', startedAt=now(), pid=me.pid, createTime=me.create_time(), cpuThreads=2, gpuWorker=False,
               reusedSamples=0, newTransitionSamples=0, allSamplesDirectlyRead=False, finalCueApproval=False, exitCode=None)
    save(target,state); OUT.mkdir(parents=True,exist_ok=True)
    source=next(x for x in pre['sources'] if x['key']=='alyx')
    ptfile=ROOT/'shared/output/cross-game-example-coverage/motion/native-preflight-v1/alyx-native-pts.json'
    pts=json.loads(ptfile.read_text('utf-8'))['pts']; tb=Fraction(source['video']['time_base'])
    # Fine samples are new; the completed one-second candidate extraction is reused.
    indices=list(dict.fromkeys(bisect.bisect_left(pts,Fraction(490+i,10)/tb) for i in range(51)))
    folder=OUT/'alyx-transition'; folder.mkdir(exist_ok=True)
    select='+'.join('eq(n\\,%d)'%n for n in indices)
    cmd=[FF,'-v','error','-threads','2','-i',str(ROOT/source['path']),'-vf',f'select={select},scale=1280:-2','-filter_threads','2','-fps_mode','vfr','-frames:v',str(len(indices)),'-threads','2',str(folder/'sample-%03d.png')]
    result=subprocess.run(cmd,capture_output=True,text=True); (folder/'ffmpeg.log').write_text(result.stderr,'utf-8'); assert result.returncode==0,result.stderr
    fine=[]
    for i,n in enumerate(indices,1):
        p=folder/f'sample-{i:03d}.png'
        fine.append(dict(path=rel(p),sha256=sha(p),nativeFrame=n,pts=pts[n],timeBase=str(tb),seconds=float(pts[n]*tb)))
    state['transition']=dict(samples=fine,sheets=sheets(fine,folder,'alyx-transition'),ffmpegExit=result.returncode)
    state['newTransitionSamples']=len(fine); save(target,state)
    # This is a maximum-size caption-clearance test, without timed annotations.
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',46)
    framed=[]
    for window in native['windows']:
        if window['name']=='alyx-locomotion': continue
        subset=window['samples'] if window['name']!='alyx-hand' else window['samples'][:7]
        dest=OUT/window['name'];dest.mkdir(exist_ok=True)
        rows=[]
        for i,row in enumerate(subset,1):
            original=ROOT/row['path'];assert sha(original)==row['sha256']
            with Image.open(original) as src:
                src=src.convert('RGB').resize((1920,1080))
                frame=Image.new('RGB',(1920,1080),'black')
                frame.paste(src.crop((0,120,1920,1080)),(0,0))
                frame.paste(src.crop((0,840,1920,1080)).resize((1920,120)).filter(ImageFilter.GaussianBlur(18)),(0,960))
            d=ImageDraw.Draw(frame);box=(120,906,1800,1034)
            d.rectangle((128,914,1808,1042),fill='#194b35');d.rectangle(box,fill='white',outline='black',width=2)
            d.text((960,970),'고정 자막 최대 폭 검수 · 실제 동작과 목표를 함께 읽습니다.',font=font,anchor='mm',fill='black')
            d.rectangle((15,15,525,55),fill='#111111')
            d.text((25,20),'Portal 2 — Valve' if window['sourceKey']=='portal2' else 'Half-Life: Alyx — Valve',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26),fill='white')
            p=dest/f'sample-{i:03d}.png';frame.save(p)
            rows.append(dict(path=rel(p),sha256=sha(p),nativeFrame=row['nativeFrame'],pts=row['pts'],timeBase=row['timeBase'],sourceSample=row['path']))
        framed.append(dict(window=window['name'],samples=rows,sheets=sheets(rows,dest,window['name'])))
    state.update(status='complete-awaiting-direct-review',finishedAt=now(),exitCode=0,reframed=framed,reusedSamples=sum(len(x['samples']) for x in framed),
                 framing=dict(shiftYPixels=-120,topCropPixels=120,bottomSameFrameBlurPixels=120,captionCenter=[960,970],captionBox=[120,906,1800,1034],timedAnnotations=False),
                 protectedBaselineUnchanged=all(sha(ROOT/x['path'])==x['sha256'] for x in pre['protectedBaseline']),
                 localOnly=True,gitImagesAdded=0)
    save(target,state);print(json.dumps({k:state[k] for k in ['status','exitCode','newTransitionSamples','reusedSamples','protectedBaselineUnchanged']}),flush=True)
if __name__=='__main__':main()
