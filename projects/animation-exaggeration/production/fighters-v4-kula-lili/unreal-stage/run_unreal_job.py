"""Launch only this revision's isolated worker; never control user processes."""
from pathlib import Path
import json,subprocess,sys,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[4];L=H.parents[1]/'local/fighters-v4-kula-lili'
EXE=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
def main():
    script=H/sys.argv[1];assert script.parent==H and script.is_file()
    control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
    auth=json.loads((H.parent/'authorization.json').read_text(encoding='utf-8'))
    assert control['scopedProductionAuthorizations']['animation-exaggeration-fighters-v4-kula-lili']['fullProductionAuthorized'] and auth['localProductionAuthorized']
    label=script.stem;out=L/'unreal';out.mkdir(parents=True,exist_ok=True)
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    # CREATE_NO_WINDOW keeps this commandlet separate from the user's desktop.
    args=[str(EXE),str(L/'unreal-worker/A02Worker.uproject'),'-run=pythonscript','-script='+str(script),
        '-unattended','-nullrhi','-nosplash','-nosound','-NoLiveCoding','-abslog='+str(out/(label+'.log'))]
    with (out/(label+'.stdout.log')).open('w',encoding='utf-8') as log:
        p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    job={'pid':p.pid,'script':script.relative_to(R).as_posix(),'startedAt':now,'nullRhi':True,
        'sourceEditorTouched':False,'controlSha256':hashlib.sha256((R/'shared/publishing/video-production-control.json').read_bytes()).hexdigest()}
    (out/(label+'.job.json')).write_text(json.dumps(job,indent=2)+'\n',encoding='utf-8');print(json.dumps(job))
    if '--wait' in sys.argv:
        code=p.wait();print('Commandlet exit',code,flush=True)
        if code:raise SystemExit(code)
if __name__=='__main__':main()
