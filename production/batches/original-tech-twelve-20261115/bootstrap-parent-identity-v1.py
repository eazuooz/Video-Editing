"""Qualify only an exact own Dvenv->Cbase shim with an acquired worker marker.

The legacy classifier source, foreign process decisions, GPU thresholds and
lease checks are unchanged. This is the same restricted identity distinction
used by the reviewed old adapter, applied to a new explicit exact argv.
"""
from pathlib import Path
import hashlib,math,os
LAUNCHER=Path('D:/Github/VideoEditing/qwen3-tts/.venv/Scripts/python.exe')
BODY=Path('C:/Anaconda3/envs/pytorch-gpu/python.exe')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def matches(info,own,parent,script,slug):
    try:
        fields=('pid','ppid','create_time','name','exe','cmdline')
        if any(any(k not in x or x[k]is None for k in fields)for x in[info,own,parent]):return False
        if any(type(x[k])is not int or x[k]<=0 for x in[info,own,parent]for k in['pid','ppid']):return False
        if any(type(x['create_time'])not in[int,float]or not math.isfinite(x['create_time'])or x['create_time']<=0 for x in[info,own,parent]):return False
        if own['ppid']!=parent['pid']or info['pid']!=parent['pid']or info['ppid']!=parent['ppid']or own['pid']==parent['pid']:return False
        a,b=own['cmdline'],parent['cmdline']
        if not isinstance(a,list)or not isinstance(b,list)or len(a)!=10 or len(b)!=10 or not all(isinstance(x,str)for x in a+b):return False
        if a[1:]!=b[1:]or info['cmdline']!=b or a[1:4]!=['-u','-X','utf8']or a[5:]!=['--project',slug,'--execute','--wait-minutes','15']:return False
        if Path(a[4]).resolve()!=Path(script).resolve():return False
        return (Path(b[0]).resolve()==Path(parent['exe']).resolve()==Path(info['exe']).resolve()==LAUNCHER.resolve()
            and Path(a[0]).resolve()==Path(own['exe']).resolve()==BODY.resolve()
            and own['name'].lower()==parent['name'].lower()==info['name'].lower()=='python.exe'
            and abs(info['create_time']-parent['create_time'])<.001 and 0<=own['create_time']-parent['create_time']<30)
    except(KeyError,TypeError,ValueError,OSError):return False
def install(native,script,project,base,protocol,owner):
    resource=native.guard;original=resource.process_reason;script=Path(script).resolve();marker=Path(base)/'worker.json';code=sha(script);launcher=sha(LAUNCHER);body=sha(BODY)
    def scoped(info,own_pid,qualified=frozenset()):
        if os.name=='nt'and own_pid==os.getpid()and info.get('pid')==os.getppid():
            try:
                fields=['pid','ppid','create_time','name','exe','cmdline'];own=resource.psutil.Process(os.getpid()).as_dict(fields);parent=resource.psutil.Process(own['ppid']).as_dict(fields);record=native.read(marker)
                valid=(record.get('protocol')==protocol and record.get('owner')==owner and record.get('project')==project
                    and record.get('stage')=='targeted-source'and isinstance(record.get('token'),str)and bool(record['token'])
                    and record.get('pid')==own['pid']and type(record.get('createTime'))in[int,float]and abs(record['createTime']-own['create_time'])<.001
                    and record.get('argv')==own['cmdline']and record.get('commandSHA256')==native.digest(own['cmdline'])
                    and record.get('child')is None and record.get('adapterSHA256')==code and sha(script)==code
                    and record.get('launcherSHA256')==launcher and sha(LAUNCHER)==launcher and record.get('bodySHA256')==body and sha(BODY)==body)
                if valid and matches(info,own,parent,script,project)and native.read(marker)==record:return None
            except(resource.psutil.NoSuchProcess,resource.psutil.AccessDenied,OSError,ValueError,KeyError,TypeError):pass
        return original(info,own_pid,qualified)
    resource.process_reason=scoped
    return dict(adapterSHA256=code,launcherSHA256=launcher,bodySHA256=body)
