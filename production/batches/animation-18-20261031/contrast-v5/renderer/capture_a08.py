"""Isolated offscreen UE capture, only with the existing global GPU lease guard."""
from sources import *
import shutil,os
from datetime import datetime,timezone
sys.path.insert(0,str(B))
from gpu_slot import idle_slot
LOCAL=B/'local/contrast-v5/a08-cumulative';W=LOCAL/'unreal-worker'
def run(args,label):
    exe=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
    with (LOCAL/(label+'.log')).open('wb')as f:
        subprocess.run([str(exe),str(W/'A08ContrastV5.uproject'),*map(str,args),'-unattended','-nosound','-nosplash','-NoLiveCoding',
                        '-abslog='+str(LOCAL/(label+'.engine.log'))],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def main():
    ctrl=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ctrl['renderAuthorized']and'A08'in ctrl['episodes']
    job=read(LOCAL/'study-job.json');assert job['episode']=='A08ContrastV5'
    W.mkdir(parents=True,exist_ok=True);(W/'Content').mkdir(exist_ok=True);(W/'Config').mkdir(exist_ok=True)
    template=project('A01')/'production/local/unreal-kit-v2/unreal-worker'
    shutil.copyfile(template/'A01Worker.uproject',W/'A08ContrastV5.uproject');shutil.copyfile(template/'Config/DefaultEngine.ini',W/'Config/DefaultEngine.ini')
    for f in (R/'GameAnimationSample/Content').iterdir():
        if not f.is_dir()or f.name=='YamyamAnimationSeries':continue
        dst=W/'Content'/f.name
        if not dst.exists():
            q=lambda p:"'"+str(p).replace("'","''")+"'"
            subprocess.run(['powershell','-NoProfile','-Command','New-Item -ItemType Junction -Path '+q(dst)+' -Target '+q(f)+' | Out-Null'],check=True)
        assert dst.resolve()==f.resolve()
    (W/'build-job.json').write_text(json.dumps(job),'utf8')
    builder=B/'native/build_level.py'
    signature=hashlib.sha256(b''.join((LOCAL/'poses'/(key+'.json')).read_bytes()for key in job['keys'])+builder.read_bytes()).hexdigest()
    receipt=LOCAL/'capture-receipt.json';old=read(receipt)if receipt.exists()else{}
    if old.get('signature')==signature and all(len(list((LOCAL/'frames'/k).glob('*.png')))==180 for k in job['keys']):print('Reused matching actual captures');return
    # Never wait with a hidden job monopolizing the user's GPU. A denied slot is
    # a normal return and other CPU work can continue before a later retry.
    with idle_slot('A08-contrast-v5-cumulative-actual-capture',wait=False) as owned:
        if not owned:print('GPU_SLOT_NOT_AVAILABLE; no process launched',flush=True);return
        print('Acquired existing GPU lease; isolated A08 build',flush=True)
        run(['-run=pythonscript','-script='+str(builder),'-nullrhi'],'build')
        for key in job['keys']:
            if old.get('definitionHashes',{}).get(key)==sha(LOCAL/'poses'/(key+'.json'))and len(list((LOCAL/'frames'/key).glob('*.png')))==180:
                print('Reused unchanged capture',key,flush=True);continue
            meta=read(LOCAL/(key+'-build.json'));print('Capturing',key,flush=True)
            run([meta['level'],'-game','-LevelSequence='+meta['sequence'],'-MoviePipelineConfig='+meta['config'],'-RenderOffscreen',
                 '-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080'],'capture-'+key)
            files=list((LOCAL/'frames'/key).glob('*.png'));assert len(files)==180,(key,len(files))
        data={'signature':signature,'keys':job['keys'],'framesPerStudy':180,'resolution':[1920,1080],'fps':60,'engine':'UE 5.8',
              'definitionHashes':{k:sha(LOCAL/'poses'/(k+'.json'))for k in job['keys']},
              'assetNamespace':'/Game/YamyamAnimationSeries/A08ContrastV5','vendorAssetsModified':False,'createdAt':datetime.now(timezone.utc).isoformat(),
              'actualFrameSamples':{k:[{'frame':n,'sha256':sha(LOCAL/'frames'/k/f'{n:06d}.png')}for n in (0,48,88,179)]for k in job['keys']}}
        receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8');print('Actual UE captures complete',flush=True)
if __name__=='__main__':main()
