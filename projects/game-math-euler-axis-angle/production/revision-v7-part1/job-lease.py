"""Finite selected-Part1 expensive-job lease; never steals another owner.

Use after the explicit root handoff. Existing editors/research are preserved.
This is a finite local coordinator, not a scheduler or automatic next task.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse, importlib.util, json, os, subprocess, sys, time, uuid
import psutil

H=Path(__file__).resolve().parent;R=H.parents[3]
O=R/'projects/game-math-euler-axis-angle/production/local/revision-v7-part1'
LEASE=R/'shared/output/GPU_HANDOFF.json'
CPU_LEASE=O/'jobs/CPU_HANDOFF.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def gpu_state():
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,used,util=map(int,raw.split(','));return dict(freeMiB=free,usedMiB=used,utilization=util)
def authorization():
    sp=importlib.util.spec_from_file_location('v7_finite_job_authority',H/'timing.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m.authorized()
@contextmanager
def finite(purpose,require_gpu=False,minimum_free_mib=2048):
    auth=authorization()
    # Software decoding, alignment, mixing and Cairo rendering do not acquire
    # another task's GPU. Serialize our own CPU work independently, at a small
    # thread budget, while preserving the shared GPU owner's finite lease.
    lease=LEASE if require_gpu else CPU_LEASE
    if lease.exists():raise RuntimeError('The current resource owner is preserved; wait for its finite handoff.')
    before=gpu_state()
    if require_gpu:
        assert before['freeMiB']>=minimum_free_mib,'Insufficient free graphics memory; no foreign job was changed'
        apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
        assert not any('python'in row.lower()for row in apps.splitlines()),'A GPU model process remains; await its completed-job handoff'
    else:
        assert psutil.virtual_memory().available>=2*1024**3,'Less than2GiB system RAM available for bounded CPU preparation'
    token=uuid.uuid4().hex;me=psutil.Process()
    record=dict(schemaVersion=1,token=token,project='game-math-euler-axis-angle',part=1,purpose=purpose,
        coordinator=dict(pid=me.pid,createTime=me.create_time()),state='render_running',gpuBefore=before,
        startedAt=time.time(),requireGpu=require_gpu,approvedScriptSha256=auth['approvedScriptSha256'],
        resource='shared-gpu'if require_gpu else'part1-cpu-only',
        cpuThreadBudget=None if require_gpu else 2,foreignGpuLeasePresent=LEASE.exists(),
        foreignJobsChanged=False,automaticNextVideo=False)
    lease.parent.mkdir(parents=True,exist_ok=True)
    with lease.open('x',encoding='utf8')as stream:json.dump(record,stream,indent=2)
    try:
        yield record
        record['state']='complete'
    except BaseException:
        record['state']='failed';raise
    finally:
        record['completedAt']=time.time()
        try:record['gpuAfter']=gpu_state()
        except Exception as error:record['gpuReadbackError']=str(error)
        folder=O/'jobs';folder.mkdir(parents=True,exist_ok=True)
        (folder/(token+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        child=record.get('child');live=False
        if child:
            try:live=psutil.Process(child['pid']).create_time()==child['createTime']
            except psutil.NoSuchProcess:pass
        if lease.exists()and read(lease).get('token')==token:
            if live:
                record['state']='owned-child-still-running; explicit completion handoff required'
                lease.write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
            else:lease.unlink()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--purpose',required=True);ap.add_argument('--gpu',action='store_true');ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    command=a.command[1:]if a.command[:1]==['--']else a.command;assert command,'A finite explicit command is required'
    with finite(a.purpose,a.gpu)as record:
        env=dict(os.environ)
        if not a.gpu:
            env.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
        process=subprocess.Popen(command,cwd=R,env=env,
            creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        record['child']=dict(pid=process.pid,createTime=psutil.Process(process.pid).create_time())
        try:code=process.wait()
        except BaseException:
            # Only the exact child created by this coordinator may be stopped.
            try:
                own=psutil.Process(process.pid)
                if own.create_time()==record['child']['createTime']:
                    children=own.children(recursive=True)
                    for child in children:
                        try:child.terminate()
                        except psutil.NoSuchProcess:pass
                    own.terminate();process.wait(timeout=30)
            except psutil.NoSuchProcess:pass
            raise
        record['exitCode']=code
        if code:raise RuntimeError('Selected finite command failed with exit code '+str(code))
if __name__=='__main__':main()
