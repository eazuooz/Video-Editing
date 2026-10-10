"""CPU-only, sequential local review media helpers; verification is not pixel approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, psutil
ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'projects/game-lighting-history-03/production'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
def stamp(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    temp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)
def owned_media():
    jobs = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        if (p.info['name'] or '').lower() != 'ffmpeg.exe': continue
        if 'game-lighting-history' in ' '.join(p.info['cmdline'] or []): jobs.append(p.info)
    return jobs
def resources():
    assert not owned_media(), 'Owned series media worker active; preserve it.'
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                          '--format=csv,noheader'], capture_output=True, text=True, check=True)
    return dict(observedAt=stamp(), nvidiaSmi=gpu.stdout.strip(), ownGpuJobs=0,
                cpuThreads=2, foreignProcessesPreserved=True)
def worker():
    p = psutil.Process()
    return dict(pid=p.pid, createTime=p.create_time(), commandLine=p.cmdline(), cwd=str(ROOT))
def run(cmd, label, state, state_path, out):
    assert not owned_media(), 'Another owned series media job is running.'
    log = out / (label + '.log')
    with log.open('wb') as f:
        p = subprocess.Popen(list(map(str, cmd)), cwd=ROOT, stdout=f, stderr=subprocess.STDOUT,
                             creationflags=subprocess.CREATE_NO_WINDOW)
        state['active'] = dict(pid=p.pid, createTime=psutil.Process(p.pid).create_time(),
                               commandLine=list(map(str, cmd)), cwd=str(ROOT), log=rel(log),
                               startedAt=stamp(), cpuThreads=2, gpuJobs=0)
        save(state_path, state)
        code = p.wait()
    record = dict(state['active'], exitCode=code, completedAt=stamp())
    state['lastCommand'] = record
    state['active'] = None
    state.setdefault('commands', []).append(record)
    save(state_path, state)
    if code: raise RuntimeError(f'{label} exit {code}; preserve output and inspect {log}')
    return record
def verify_video(output, frames, state, state_path, out, label):
    probe_cmd = [str(FP), '-v', 'error', '-threads', '2', '-count_frames', '-show_entries',
                 'stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames,duration',
                 '-of', 'json', str(output)]
    probe = json.loads(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout)
    v = probe['streams'][0]
    assert len(probe['streams']) == 1 and v['codec_type'] == 'video'
    assert (v['width'], v['height'], v['r_frame_rate'], v['time_base'], int(v['nb_read_frames'])) == (1920, 1080, '60/1', '1/90000', frames), probe
    packet_cmd = [str(FP), '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts', '-of', 'json', str(output)]
    pts = sorted(x['pts'] for x in json.loads(subprocess.run(packet_cmd, capture_output=True, text=True, check=True).stdout)['packets'])
    assert pts == list(range(0, frames * 1500, 1500)), 'Presentation timestamps differ from exact frame plan'
    decode = run([FF, '-v', 'error', '-threads', '2', '-i', output, '-f', 'null', 'NUL'],
                 label + '-decode', state, state_path, out)
    return dict(verifiedAt=stamp(), output=rel(output), outputSha256=sha(output),
                observedFrames=frames, probe=probe, probeCommand=probe_cmd, packetCommand=packet_cmd,
                allPresentationPtsContinuous=True, wholeDecode=decode, allPixelsReviewed=False,
                finalUseApproved=False, localOnly=True)
