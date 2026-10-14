"""Bounded, reversible music comparison for the selected video's planning package."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys
import psutil

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROJECT = ROOT / 'projects/hierarchical-game-outlines'
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def run(args):
    cp = subprocess.run([FF, '-hide_banner', '-nostdin', '-threads', '2', *args], capture_output=True, text=True, encoding='utf8', errors='replace')
    with (OUT / 'sample.log').open('a', encoding='utf8') as f:
        f.write(cp.stderr + '\n')
    if cp.returncode: raise RuntimeError(cp.stderr[-2000:])
    return cp.stderr

assert not (OUT / 'lofi-comparison.mp4').exists(), 'Reuse existing sample; no overwrite.'
me = psutil.Process()
me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state = dict(startedAt=now(), pid=me.pid, createTime=me.create_time(), command=me.cmdline(), cwd=me.cwd(), cpuThreads=2, gpuJobs=0, status='running', exitCode=None)
state['resource'] = dict(cpu=psutil.cpu_percent(interval=1), availableMemoryBytes=psutil.virtual_memory().available,
    gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout)
assert state['resource']['cpu'] < 85 and state['resource']['availableMemoryBytes'] > 8_000_000_000
save('sample-state.json',state)
baseline = PROJECT / 'production/visual-depth-v1/hierarchical-game-outlines.captioned.review.mp4'
voice = PROJECT / 'production/final-v1/narration-timed-body.wav'
music = OUT / 'Late-Night-Radio.mp3'
duration = 46.68333333333333
# Existing first complete paragraph (9.233333 s), then the whole parent/question explanation (37.45 s).
# Captioned pixels stay unchanged. This specifically previews the audio change, not new tracked annotations.
windows = [(2,9.233333333333333),(40.21666666666667,37.45)]
try:
    for i,(start,length) in enumerate(windows):
        run(['-loglevel','error','-ss',str(start),'-i',str(baseline),'-t',str(length),'-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-c:a','aac','-b:a','192k','-ar','48000',str(OUT/f'baseline-{i}.mp4')])
    (OUT/'concat.txt').write_text("file 'baseline-0.mp4'\nfile 'baseline-1.mp4'\n",encoding='utf8')
    run(['-loglevel','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-c','copy','-movflags','+faststart',str(OUT/'original-comparison.mp4')])
    filters = f"[0:a]asplit=2[a][b];[a]atrim=start=0:end=9.233333333333333,asetpts=PTS-STARTPTS[a0];[b]atrim=start=38.21666666666667:end=75.66666666666667,asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1,loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,asplit=2[n][side];[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,loudnorm=I=-31:TP=-3:LRA=7,aresample=48000,afade=t=in:d=0.45,afade=t=out:st={duration-.45}:d=0.45[m];[m][side]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[duck];[n][duck]amix=inputs=2:duration=first:normalize=0[out]"
    (OUT/'mix-filter.txt').write_text(filters,encoding='utf8')
    run(['-loglevel','error','-i',str(voice),'-i',str(music),'-filter_complex_threads','2','-filter_complex_script',str(OUT/'mix-filter.txt'),'-map','[out]','-c:a','pcm_s16le','-ar','48000','-ac','2',str(OUT/'sample-mix.wav')])
    run(['-loglevel','error','-i',str(OUT/'original-comparison.mp4'),'-i',str(OUT/'sample-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(duration),'-movflags','+faststart',str(OUT/'lofi-comparison.mp4')])
    for name in ['original-comparison.mp4','lofi-comparison.mp4']:
        run(['-loglevel','error','-i',str(OUT/name),'-f','null','-'])
    loud = run(['-i',str(OUT/'lofi-comparison.mp4'),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'])
    measured = json.loads(loud[loud.rfind('{'):loud.rfind('}')+1])
    assert float(measured['input_tp']) <= -1.5, measured
    state.update(status='complete',exitCode=0,finishedAt=now(),seconds=duration,windows=windows,loudness=measured,
        outputs={n:sha(OUT/n) for n in ['original-comparison.mp4','lofi-comparison.mp4','sample-mix.wav']},
        finalVideo=False,sourceSfxRestored=False,newAnnotationPixelApproval=False,humanListening=False,
        note='Audio comparison with preserved approved captioned visuals; original commentary/music omitted. No claim of recovered game sound.')
    save('sample-state.json',state)
    print(json.dumps({k:state[k] for k in ['status','seconds','loudness','outputs']},ensure_ascii=False))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=str(e),finishedAt=now());save('sample-state.json',state);raise
