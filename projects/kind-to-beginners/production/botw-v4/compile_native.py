"""Deploy/freeze only BOTW v4 sources and use the existing no-focus refresh probe.
Default is read-only readiness. --execute requires the root's resource slot.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys,time,uuid
from freeze_sources import H,R,U,C,read,digest,ensure_idle

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');a=ap.parse_args()
 source=H/'unity-source';paths=[p for p in source.rglob('*') if p.is_file() and p.suffix in ('.cs','.json') and p.name!='DesignBotwBuildVersion.cs']
 assert paths and all(p.resolve().is_relative_to(source.resolve()) for p in paths)
 changes=[p for p in paths if not (C/p.relative_to(source)).exists() or digest(p)!=digest(C/p.relative_to(source))]
 if not a.execute:
  print(json.dumps({'writesPerformed':False,'changes':[p.relative_to(source).as_posix() for p in changes]}));return
 ensure_idle()
 library=U/'Library';assert not list(library.glob('*.request')) and not list(library.glob('*.request.json')),'Preserve pending bridge'
 asset=library/'YamyamAssetLibrary';state=read(asset/'state.json');assert state['phase'] in ('complete','failed')
 auth=read(H/'authorization.json');assert auth['revision']=='botw-v4' and auth['localProductionAuthorized'] and auth['noUiOrFocus']
 for p in changes:
  dst=C/p.relative_to(source);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
 subprocess.run([sys.executable,str(H/'freeze_sources.py')],check=True)
 frozen=read(H/'botw-code-fingerprint.json');expected=frozen['fingerprints']['D29BotwStage']
 nonce='d29-botw-v4-compile-'+uuid.uuid4().hex
 with (asset/'request.json').open('x',encoding='utf-8') as f:json.dump({'command':'probe','nonce':nonce},f)
 print('COMPILE REQUESTED '+nonce,flush=True);start=time.monotonic();ack=library/'DesignBotwV4.compiled.json'
 while time.monotonic()-start<240:
  if ack.exists():
   try:result=read(ack)
   except json.JSONDecodeError:result={}
   rows=result.get('stages',[])
   if any(x.get('stageClass')=='D29BotwStage' and x.get('fingerprint')==expected and x.get('typeAvailable') for x in rows):
    s=read(asset/'state.json')
    if s.get('nonce')==nonce and s.get('phase')=='complete':
     shutil.copy2(ack,H/'native-compiled-ack.json');print('COMPILED '+expected,flush=True);return
  time.sleep(1)
 raise RuntimeError('No matching compiled acknowledgement: preserve editor, inspect bounded Bee compiler errors; no capture submitted.')
if __name__=='__main__':main()
