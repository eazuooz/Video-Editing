"""Run a scoped Unreal commandlet or a single offscreen audition capture."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, subprocess, sys, uuid
from setup_worker import setup, R, B, L, W, H, EXE

def command(args, name):
    with (L/(name+'.log')).open('wb') as log:
        subprocess.run([EXE,W/'RealClipsWorker.uproject',*args,'-unattended','-nosound',
                        '-nosplash','-NoLiveCoding','-abslog='+str(L/(name+'-engine.log'))],
                       stdout=log,stderr=log,check=True,creationflags=subprocess.CREATE_NO_WINDOW)

def render(key):
    batch=json.loads((B/'batch.json').read_text('utf-8'))
    assert batch['renderAuthorized'] and key.replace('-','').isalnum()
    json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
    lease=R/'shared/output/GPU_HANDOFF.json'
    token=uuid.uuid4().hex
    available=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True)
    assert int(available.strip())>4500,'Insufficient GPU memory for offscreen capture'
    with lease.open('x',encoding='utf-8') as f:
        json.dump(dict(owner='animation-real-clips-v2',id=token,pid=os.getpid(),createdAt=datetime.now(timezone.utc).isoformat()),f)
    try:
        meta=json.loads((L/(key+'-audition.json')).read_text('utf-8'))
        command([meta['level'],'-game','-LevelSequence='+meta['sequence'],'-MoviePipelineConfig='+meta['config'],
                 '-RenderOffscreen','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming',
                 '-resx=1920','-resy=1080'],'render-'+key)
        folder=L/'audition-frames'/key
        frames=sorted(folder.glob('*.png'));assert len(frames)==meta['frames'],(key,len(frames),meta['frames'])
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-start_number',str(int(frames[0].stem)),
                        '-i',str(folder/'%06d.png'),'-c:v','h264_nvenc','-preset','p4','-cq','18',
                        '-pix_fmt','yuv420p',str(L/(key+'.mp4'))],check=True)
    finally:
        if lease.is_file() and json.loads(lease.read_text('utf-8')).get('id')==token:
            lease.unlink()

def render_queue():
    batch=json.loads((B/'batch.json').read_text('utf-8'));assert batch['renderAuthorized']
    json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
    meta=json.loads((L/'study-queue.json').read_text('utf-8'))
    lease=R/'shared/output/GPU_HANDOFF.json';token=uuid.uuid4().hex
    available=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True)
    assert int(available.strip())>4500
    with lease.open('x',encoding='utf-8') as f:json.dump(dict(owner='animation-real-clips-v2',id=token,pid=os.getpid(),createdAt=datetime.now(timezone.utc).isoformat()),f)
    try:
        command([meta['jobs'][0]['level'],'-game','-MoviePipelineConfig='+meta['queue'],
                 '-RenderOffscreen','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080'],'render-studies')
        for row in meta['jobs']:
            directory=L/'study-frames'/row['key'];frames=sorted(directory.glob('*.png'))
            assert len(frames)==row['frames'],(row['key'],len(frames),row['frames'])
            subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-start_number',str(int(frames[0].stem)),
                            '-i',str(directory/'%06d.png'),'-c:v','h264_nvenc','-preset','p4','-cq','18',
                            '-pix_fmt','yuv420p',str(L/(row['key']+'.mp4'))],check=True)
        print('Verified native studies:',len(meta['jobs']),flush=True)
    finally:
        if lease.is_file() and json.loads(lease.read_text('utf-8')).get('id')==token:lease.unlink()

if __name__=='__main__':
    setup()
    if sys.argv[1]=='script':command(['-run=pythonscript','-script='+str(H/sys.argv[2]),'-nullrhi'],Path(sys.argv[2]).stem)
    elif sys.argv[1]=='audition':
        command(['-run=pythonscript','-script='+str(H/'build_preview.py'),'-nullrhi'],'build-audition')
        render(json.loads((L/'audition-request.json').read_text('utf-8'))['id'])
    elif sys.argv[1]=='queue':render_queue()
    else:raise ValueError(sys.argv[1])
